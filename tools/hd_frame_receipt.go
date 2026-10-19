// Disposable HD source probe. Only normal menu/movement input and read-only oracle API.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"

	"github.com/wicanr2/dosgolem/oracle"
)

func must(err error) {
	if err != nil {
		panic(err)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func main() {
	root := flag.String("root", "/orig", "original data")
	out := flag.String("out", "", "new output directory")
	mode := flag.String("mode", "single", "single or versus-frank")
	player0 := flag.Int("player0", 0, "normal selectable first-player character 0..7")
	flag.Parse()
	if *player0 < 0 || *player0 > 7 {
		panic("player0 must be 0..7")
	}
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output already exists")
	}
	must(os.MkdirAll(*out, 0755))
	script, e := os.ReadFile("/project/tools/hd_frame_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "hd_frame_receipt.go"), script, 0644))
	exe, e := os.ReadFile(filepath.Join(*root, "SF.EXE"))
	must(e)
	if digest(exe) != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("source mismatch")
	}
	o, e := oracle.LoadProgram(filepath.Join(*root, "NOKEY.EXE"), *root, " /y")
	must(e)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	o.Enqueue("SF.COM", "")
	must(o.Run(40_000_000))
	x := 55
	if *mode == "versus-frank" {
		x = 125
	} else if *mode != "single" {
		panic("unknown mode")
	}
	must(o.MoveMouse(x, 181))
	o.PressButton(0)
	must(o.Run(1_000_000))
	o.ReleaseButton(0)
	must(o.Run(24_000_000))
	for i := 0; i < *player0; i++ {
		must(o.SendKeys("Right"))
		must(o.Run(1_000_000))
	}
	must(o.SendKeys("Return"))
	must(o.Run(20_000_000))
	if *mode == "versus-frank" {
		// 正常選角的第二人游標沿用第一人位置，0／1 已由實跑核對。
		for i := 0; i < (4-*player0+8)%8; i++ {
			must(o.SendKeys("Right"))
			must(o.Run(1_000_000))
		}
		must(o.SendKeys("Return"))
	}
	must(o.Run(75_000_000))
	if o.Word(oracle.Far(0, 0x24)) != 0x524c || o.Word(oracle.Far(0, 0x26)) != 0x1b9 {
		panic("wrong IRQ1")
	}
	isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
	if !bytes.Equal(isr[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		panic("ISR mismatch")
	}
	ds := binary.LittleEndian.Uint16(isr[6:8])
	if int(o.Word(oracle.Far(ds, 0x12ac))) != *player0 || *mode == "versus-frank" && o.Word(oracle.Far(ds, 0x12ae)) != 4 {
		panic(fmt.Sprintf("selection mismatch: got %d/%d", o.Word(oracle.Far(ds, 0x12ac)), o.Word(oracle.Far(ds, 0x12ae))))
	}
	bgFile, e := os.Open("/project/workplace/hd-source-probe-v3/I2.XGB.png")
	must(e)
	bgImg, e := png.Decode(bgFile)
	must(e)
	must(bgFile.Close())
	bg, ok := bgImg.(*image.Paletted)
	if !ok || bg.Bounds().Dx() != 480 || bg.Bounds().Dy() != 204 {
		panic("not expected original paletted scene")
	}
	sources := map[int][]byte{}
	hashes := map[string]string{"SF.EXE": digest(exe)}
	for char := 0; char < 11; char++ {
		name := fmt.Sprintf("SFMAN%02d.DAT", char+1)
		b, e := os.ReadFile(filepath.Join(*root, name))
		must(e)
		sources[char] = b
		hashes[name] = digest(b)
	}
	var frames []map[string]any
	var lastCounter uint16
	seenCounter := false
	for _, phase := range []struct {
		name  string
		keys  []uint8
		count int
	}{{"idle", nil, 12}, {"p1-walk", []uint8{0x20}, 18}, {"release", nil, 6}, {"p1-crouch", []uint8{0x2d}, 12}, {"p1-jump", []uint8{0x11}, 30}, {"release-jump", nil, 18}, {"both-punch", []uint8{0x0f, 0x1c}, 8}, {"release-punch", nil, 20}} {
		for _, key := range o.HeldKeys() {
			o.KeyUp(key)
		}
		for _, key := range phase.keys {
			o.KeyDown(key)
		}
		for i := 0; i < phase.count; i++ {
			for {
				must(o.Run(1))
				must(o.RunUntil(oracle.At(oracle.Far(0x1b9, 0x5dd3)), oracle.Budget(5_000_000)))
				counter := o.Word(oracle.Far(ds, 0x1a))
				if !seenCounter || counter != lastCounter {
					lastCounter = counter
					seenCounter = true
					break
				}
			}
			camera := int(o.Word(oracle.Far(ds, 0x1332)))
			crtcRows := int(o.Byte(oracle.Far(ds, 0x1334)))
			// oracle.Indexed 的現行 mode 13h 契約為 A0000 線性畫面，未套 CRTC 起點。
			// 保留硬體控制值，不能把它錯當這份 API 的像素裁切。
			cropY := 0
			scene := int(o.Word(oracle.Far(ds, 0x1338)))
			idx := o.Indexed()
			ramBg := o.Bytes(oracle.Far(o.Word(oracle.Far(ds, 0x0c)), 0), 480*204)
			var actors []map[string]any
			for p := 0; p < 2; p++ {
				char := int(o.Word(oracle.Far(ds, uint16(0x12ac+p*2))))
				slot := int(o.Byte(oracle.Far(ds, []uint16{0x16f2, 0x16fa}[p])))
				x := int(int16(o.Word(oracle.Far(ds, uint16(0x16d6+p*2))))) - camera
				y := int(int16(o.Word(oracle.Far(ds, uint16(0x16de+p*2))))) - cropY
				table := uint16(0x1706 + p*0x120 + slot*4)
				seg := o.Word(oracle.Far(ds, table)) + o.Word(oracle.Far(ds, uint16(0x132a+p*2)))
				off := o.Word(oracle.Far(ds, table+2))
				header := o.Bytes(oracle.Far(seg, off), 2)
				n := 2 + ((int(header[0])+1)/2)*int(header[1])
				raw := o.Bytes(oracle.Far(seg, off), n)
				match := false
				fileOffset := -1
				if data, ok := sources[char]; ok && slot < 72 {
					ptr := 0xb28 + slot*4
					fileOffset = 0xc48 + int(binary.LittleEndian.Uint16(data[ptr:]))*16 + int(binary.LittleEndian.Uint16(data[ptr+2:]))
					if fileOffset+n <= len(data) {
						match = bytes.Equal(raw, data[fileOffset:fileOffset+n])
					}
				}
				actors = append(actors, map[string]any{"player": p, "character": char, "slot": slot, "x": x, "y": y, "path": o.Byte(oracle.Far(ds, uint16(0x16ea+p))), "attr": o.Byte(oracle.Far(ds, uint16(0x16fe+p))), "facing": o.Byte(oracle.Far(ds, uint16(0x16b4+p))), "runtime_pointer": fmt.Sprintf("%04X:%04X", seg, off), "source_file_offset": fileOffset, "size": []int{int(header[0]), int(header[1])}, "bytes_match_source": match})
			}
			matched, total := 0, 0
			var differences []map[string]int
			if camera >= 0 && camera+320 <= 480 && cropY >= 0 && cropY+200 <= 204 && len(idx) == 64000 {
				for y := 40; y < 200; y++ {
					for x := 0; x < 320; x++ {
						v := idx[y*320+x]
						if v >= 128 {
							continue
						}
						total++
						expected := bg.Pix[(y+cropY)*bg.Stride+x+camera]
						if v == expected {
							matched++
						} else if len(differences) < 8 {
							differences = append(differences, map[string]int{"x": x, "y": y, "actual": int(v), "expected": int(expected)})
						}
					}
				}
			}
			record := map[string]any{"phase": phase.name, "frame": i, "steps": o.Steps(), "counter": o.Word(oracle.Far(ds, 0x1a)), "camera_x": camera, "crop_y": cropY, "crtc_rows_not_applied_by_oracle": crtcRows, "scene": scene, "actors": actors, "background_buffer_equals_source": bytes.Equal(ramBg, bg.Pix), "background_ram_sha256": digest(ramBg), "background_visible_low_colors": total, "background_matched": matched, "difference_sample": differences}
			frames = append(frames, record)
			if i == 0 {
				stem := fmt.Sprintf("%02d-%s", len(frames), phase.name)
				must(o.WritePNG(filepath.Join(*out, stem+".png")))
				must(os.WriteFile(filepath.Join(*out, stem+".idx"), idx, 0644))
				pal, e := json.Marshal(o.Palette())
				must(e)
				must(os.WriteFile(filepath.Join(*out, stem+"-palette.json"), pal, 0644))
			}
			must(o.Run(1))
		}
		fmt.Println(phase.name, "samples", phase.count)
	}
	sourceManifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	receipt := map[string]any{"kind": "normal-path coherent-frame HD source experiment; not HD art parity", "mode": *mode, "requested_player0": *player0, "input_sha256": hashes, "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(sourceManifest), "snapshot_control": "one continuous normal path; no state injections or RNG outcome selection", "address_space": "runtime real-mode segment:offset and DS-relative offsets; source file offsets separately labeled", "capture_ip": "01B9:5DD3", "background_reference": "I2.XGB decoded paletted PNG, 480x204; comparison may differ for other stages", "frames": frames, "opened": o.Opened(), "unimplemented": o.Unimplemented()}
	data, e := json.MarshalIndent(receipt, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "receipt.json"), append(data, '\n'), 0644))
}
