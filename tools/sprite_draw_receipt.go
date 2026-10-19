// Disposable read-only sprite draw contract probe. No game-state writes.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wicanr2/dosgolem/oracle"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

type Draw struct {
	Player           int              `json:"player"`
	Character        int              `json:"character"`
	Slot             int              `json:"slot"`
	X                int              `json:"x"`
	Y                int              `json:"y"`
	Width            int              `json:"width"`
	Height           int              `json:"height"`
	Flags            uint8            `json:"flags"`
	Palette          uint8            `json:"palette"`
	TopClip          int              `json:"top_clip"`
	LeftClip         int              `json:"left_clip"`
	RightClip        int              `json:"right_clip"`
	DI               uint16           `json:"di"`
	ES               uint16           `json:"es"`
	Counter          uint16           `json:"counter"`
	Steps            uint64           `json:"steps"`
	ReturnIP         uint16           `json:"return_ip"`
	Routine          string           `json:"routine"`
	SourcePointer    string           `json:"source_pointer"`
	SourceOffset     int              `json:"source_file_offset"`
	SourceMatches    bool             `json:"source_matches"`
	Matched          bool             `json:"matched"`
	Differences      int              `json:"differences"`
	DifferenceSample []map[string]int `json:"difference_sample,omitempty"`
	Fixture          string           `json:"fixture,omitempty"`
	raw, before      []byte
	buffer           uint16
}

type Layer struct {
	Kind         string `json:"kind"`
	Draw         *Draw  `json:"draw,omitempty"`
	Writes       int    `json:"writes"`
	SameWrites   int    `json:"same_value_writes"`
	Pixels, Mask []byte `json:"-"`
}

// Predict from the entry-register contract, independently of the running CPU.
// All offsets keep their original 16-bit meaning, including mirror origins.
func predict(d *Draw) []byte {
	out := append([]byte(nil), d.before...)
	stride := (d.Width + 1) / 2
	rows := d.Height - d.TopClip
	left, right := (d.LeftClip+1)/2, (d.RightClip+1)/2
	pairs := stride - left - right
	if rows <= 0 || pairs <= 0 || pairs >= 128 {
		return out
	}
	flipX, flipY := d.Flags&0x40 != 0, d.Flags&0x80 != 0
	di := int(d.DI)
	if flipX {
		di += d.Width - d.LeftClip - d.RightClip
	}
	if flipY {
		di += rows * 320
	}
	di &= 65535
	for row := 0; row < rows; row++ {
		sourceRow, sourcePair := row+d.TopClip, left
		if flipY {
			sourceRow = row
		}
		if flipX {
			sourcePair = right
		}
		line := int(d.ES)*16 + di + row*320 - int(d.buffer)*16
		if flipY {
			line = int(d.ES)*16 + di - row*320 - int(d.buffer)*16
		}
		for pair := 0; pair < pairs; pair++ {
			packed := d.raw[2+sourceRow*stride+sourcePair+pair]
			for n := 0; n < 2; n++ {
				v := packed >> 4
				if n == 1 {
					v = packed & 15
				}
				position := line + pair*2 + n
				if flipX {
					position = line - pair*2 - n
				}
				if v != 0 && position >= 0 && position < len(out) {
					out[position] = v | d.Palette
				}
			}
		}
	}
	return out
}

func main() {
	out := flag.String("out", "", "new output directory")
	root := flag.String("root", "/orig", "original data")
	withLayers := flag.Bool("layers", false, "observe every RAM write and verify complete frame replay")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	hashes := map[string]string{}
	for _, name := range []string{"NOKEY.EXE", "SF.COM", "SF.EXE", "SFMAN01.DAT", "SFMAN05.DAT"} {
		b, e := os.ReadFile(filepath.Join(*root, name))
		must(e)
		hashes[name] = digest(b)
	}
	if hashes["SF.EXE"] != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("wrong source")
	}
	sources := map[int][]byte{}
	for _, char := range []int{0, 4} {
		b, e := os.ReadFile(filepath.Join(*root, fmt.Sprintf("SFMAN%02d.DAT", char+1)))
		must(e)
		sources[char] = b
	}
	o, e := oracle.LoadProgram(filepath.Join(*root, "NOKEY.EXE"), *root, " /y")
	must(e)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	o.Enqueue("SF.COM", "")
	must(o.Run(40_000_000))
	must(o.MoveMouse(125, 181))
	o.PressButton(0)
	must(o.Run(1_000_000))
	o.ReleaseButton(0)
	must(o.Run(24_000_000))
	must(o.SendKeys("Return"))
	must(o.Run(20_000_000))
	for i := 0; i < 4; i++ {
		must(o.SendKeys("Right"))
		must(o.Run(1_000_000))
	}
	must(o.SendKeys("Return"))
	must(o.Run(75_000_000))
	if o.Word(oracle.Far(0, 0x24)) != 0x524c || o.Word(oracle.Far(0, 0x26)) != 0x1b9 {
		panic("not battle IRQ")
	}
	isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
	if !bytes.Equal(isr[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		panic("wrong ISR")
	}
	ds := binary.LittleEndian.Uint16(isr[6:8])
	var pending [2]*Draw
	var records []*Draw
	seenFixtures := map[string]bool{}
	var layers []*Layer
	var layerFrames []map[string]any
	var cancelWrites func()
	phaseName := ""
	seenPhases := map[string]bool{}
	if *withLayers {
		o.OnCall(oracle.Far(0x1b9, 0x3de4), func(o *oracle.Oracle) {
			if cancelWrites != nil {
				cancelWrites()
			}
			layers = []*Layer{{Kind: "raster", Pixels: make([]byte, 64000), Mask: make([]byte, 64000)}}
			base := uint32(o.Word(oracle.Far(ds, 0x0e))) * 16
			var e error
			cancelWrites, e = o.ObserveWrites(base, base+63999, func(event oracle.MemoryWrite) {
				if len(layers) == 0 {
					return
				}
				layer := layers[len(layers)-1]
				offset := int(event.Address - base)
				layer.Pixels[offset] = event.Value
				layer.Mask[offset] = 1
				layer.Writes++
				if event.Old == event.Value {
					layer.SameWrites++
				}
			})
			must(e)
		})
		o.OnCall(oracle.Far(0x1b9, 0x3e9d), func(o *oracle.Oracle) {
			if len(layers) == 0 {
				return
			}
			if cancelWrites != nil {
				cancelWrites()
				cancelWrites = nil
			}
			replayed := make([]byte, 64000)
			coverage := 0
			writes, same := 0, 0
			for _, v := range layers[0].Mask {
				if v != 0 {
					coverage++
				}
			}
			for _, layer := range layers {
				writes += layer.Writes
				same += layer.SameWrites
				for i, v := range layer.Mask {
					if v != 0 {
						replayed[i] = layer.Pixels[i]
					}
				}
			}
			actual := o.Indexed()
			different := 0
			for i, v := range actual {
				if v != replayed[i] {
					different++
				}
			}
			frame := map[string]any{"counter": o.Word(oracle.Far(ds, 0x1a)), "phase": phaseName, "steps": o.Steps(), "layers": len(layers), "base_coverage": coverage, "writes": writes, "same_value_writes": same, "differences": different, "matched": different == 0 && coverage == 64000, "screen_sha256": digest(actual)}
			if !seenPhases[phaseName] {
				seenPhases[phaseName] = true
				stem := fmt.Sprintf("frame-%04d", len(layerFrames))
				frame["fixture"] = stem
				must(os.WriteFile(filepath.Join(*out, stem+".idx"), actual, 0644))
				must(o.WritePNG(filepath.Join(*out, stem+".png")))
				palette, e := json.Marshal(o.Palette())
				must(e)
				must(os.WriteFile(filepath.Join(*out, stem+"-palette.json"), palette, 0644))
				for i, layer := range layers {
					name := fmt.Sprintf("%s-layer-%02d", stem, i)
					must(os.WriteFile(filepath.Join(*out, name+".idx"), layer.Pixels, 0644))
					must(os.WriteFile(filepath.Join(*out, name+".mask"), layer.Mask, 0644))
				}
				metadata, e := json.MarshalIndent(layers, "", "  ")
				must(e)
				must(os.WriteFile(filepath.Join(*out, stem+"-layers.json"), metadata, 0644))
			}
			layerFrames = append(layerFrames, frame)
			layers = nil
		})
	}
	for _, item := range []struct {
		ip   uint16
		name string
	}{{0x4665, "sub_14665"}, {0x46e8, "sub_146E8"}, {0x477e, "sub_1477E"}, {0x480a, "sub_1480A"}} {
		item := item
		o.OnCall(oracle.Far(0x1b9, item.ip), func(o *oracle.Oracle) {
			ret := o.StackWord(0)
			p := -1
			if ret >= 0x428e && ret <= 0x42a5 {
				p = 0
			}
			if ret >= 0x442f && ret <= 0x4446 {
				p = 1
			}
			if p < 0 {
				return
			}
			if pending[p] != nil {
				return
			} // IRQ return can revisit this same pre-instruction hook.
			char := int(o.Word(oracle.Far(ds, uint16(0x12ac+p*2))))
			slot := int(o.Byte(oracle.Far(ds, []uint16{0x16f2, 0x16fa}[p])))
			header := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2)
			n := 2 + ((int(header[0])+1)/2)*int(header[1])
			raw := o.Bytes(oracle.Far(o.DSReg(), o.SI()), n)
			buffer := o.Word(oracle.Far(ds, 0x0e))
			d := &Draw{Player: p, Character: char, Slot: slot, X: int(int16(o.Word(oracle.Far(ds, uint16(0x16d6+p*2))))) - int(o.Word(oracle.Far(ds, 0x1332))), Y: int(int16(o.Word(oracle.Far(ds, uint16(0x16de+p*2))))), Width: int(header[0]), Height: int(header[1]), Flags: uint8(o.CX()), Palette: uint8(o.DX() >> 8), TopClip: int(o.DX() & 255), LeftClip: int(o.BX() & 255), RightClip: int(o.BX() >> 8), DI: o.DI(), ES: o.ES(), Counter: o.Word(oracle.Far(ds, 0x1a)), Steps: o.Steps(), ReturnIP: ret, Routine: item.name, SourcePointer: fmt.Sprintf("%04X:%04X", o.DSReg(), o.SI()), raw: raw, before: o.Bytes(oracle.Far(buffer, 0), 64000), buffer: buffer}
			if data, ok := sources[char]; ok && slot < 72 {
				pointer := 0xb28 + slot*4
				d.SourceOffset = 0xc48 + int(binary.LittleEndian.Uint16(data[pointer:]))*16 + int(binary.LittleEndian.Uint16(data[pointer+2:]))
				if d.SourceOffset+n <= len(data) {
					d.SourceMatches = bytes.Equal(raw, data[d.SourceOffset:d.SourceOffset+n])
				}
			}
			pending[p] = d
			if *withLayers && len(layers) > 0 {
				layers = append(layers, &Layer{Kind: "actor", Draw: d, Pixels: make([]byte, 64000), Mask: make([]byte, 64000)})
			}
		})
	}
	for p, ip := range []uint16{0x42a5, 0x4446} {
		p := p
		o.OnCall(oracle.Far(0x1b9, ip), func(o *oracle.Oracle) {
			d := pending[p]
			if d == nil {
				return
			}
			pending[p] = nil
			if *withLayers && len(layers) > 0 {
				layers = append(layers, &Layer{Kind: "raster", Pixels: make([]byte, 64000), Mask: make([]byte, 64000)})
			}
			after := o.Bytes(oracle.Far(d.buffer, 0), 64000)
			expected := predict(d)
			for i, v := range after {
				if v != expected[i] {
					d.Differences++
					if len(d.DifferenceSample) < 8 {
						d.DifferenceSample = append(d.DifferenceSample, map[string]int{"x": i % 320, "y": i / 320, "actual": int(v), "expected": int(expected[i])})
					}
				}
			}
			d.Matched = d.Differences == 0
			class := fmt.Sprintf("%d-%02d-%02x-%t-%t-%t", d.Character, d.Slot, d.Flags&0xc0, d.TopClip > 0, d.LeftClip > 0, d.RightClip > 0)
			if !seenFixtures[class] && len(seenFixtures) < 128 {
				seenFixtures[class] = true
				d.Fixture = fmt.Sprintf("draw-%04d", len(records))
				for suffix, b := range map[string][]byte{"before.idx": d.before, "after.idx": after, "sprite.bin": d.raw} {
					must(os.WriteFile(filepath.Join(*out, d.Fixture+"-"+suffix), b, 0644))
				}
			}
			d.raw = nil
			d.before = nil
			records = append(records, d)
		})
	}
	var phases []map[string]any
	for _, phase := range []struct {
		name   string
		keys   []uint8
		frames int
	}{
		{"idle", nil, 12}, {"p1-left-edge", []uint8{0x1e}, 65}, {"p2-right-edge", []uint8{0x4d}, 65},
		{"p1-forward", []uint8{0x20}, 90}, {"p2-forward", []uint8{0x4b}, 90}, {"both-punch", []uint8{0xf, 0x1c}, 24},
		{"both-kick", []uint8{0x2a, 0x36}, 24}, {"crouch", []uint8{0x2d, 0x50}, 16}, {"jump", []uint8{0x11, 0x48}, 50},
		{"p1-back", []uint8{0x1e}, 45}, {"p2-back", []uint8{0x4d}, 45}, {"p1-jump-forward", []uint8{0x12}, 55},
		{"p2-jump-forward", []uint8{0x47}, 55}, {"p1-punch", []uint8{0xf}, 25}, {"p2-kick", []uint8{0x36}, 25}, {"release", nil, 30},
	} {
		phaseName = phase.name
		for _, k := range o.HeldKeys() {
			o.KeyUp(k)
		}
		for _, k := range phase.keys {
			o.KeyDown(k)
		}
		start := len(records)
		counter := o.Word(oracle.Far(ds, 0x1a))
		for i := 0; i < phase.frames; i++ {
			for {
				must(o.Run(1))
				must(o.RunUntil(oracle.At(oracle.Far(0x1b9, 0x5dd3)), oracle.Budget(5_000_000)))
				next := o.Word(oracle.Far(ds, 0x1a))
				if next != counter {
					counter = next
					break
				}
			}
		}
		phases = append(phases, map[string]any{"name": phase.name, "keys": phase.keys, "requested_frames": phase.frames, "draw_records": len(records) - start})
		fmt.Println(phase.name, len(records)-start)
	}
	matched, sourceMatches := 0, 0
	for _, d := range records {
		if d.Matched {
			matched++
		}
		if d.SourceMatches {
			sourceMatches++
		}
	}
	script, e := os.ReadFile("/project/tools/sprite_draw_receipt.go")
	must(e)
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	receipt := map[string]any{"kind": "normal-versus read-only original sprite draw prediction; no HD rendering", "input_sha256": hashes, "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(manifest), "address_space": "runtime 01B9:offset; DS-relative metadata; source file offsets separately labeled", "routine_entry_observation": "four blit entries, original registers; post-blit P1 01B9:42A5, P2 01B9:4446", "snapshot_control": "continuous normal title, versus, selection and keyboard inputs; no memory or RNG writes", "draws": len(records), "matched": matched, "source_matches": sourceMatches, "phases": phases, "records": records, "unimplemented": o.Unimplemented()}
	if *withLayers {
		receipt["layer_frames"] = layerFrames
		receipt["write_observation"] = "every ordinary RAM write, including same-value stores; runtime instruction start; spec 007"
	}
	b, e := json.MarshalIndent(receipt, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "receipt.json"), append(b, '\n'), 0644))
	must(os.WriteFile(filepath.Join(*out, "sprite_draw_receipt.go"), script, 0644))
	fmt.Println("draws", len(records), "matched", matched, "source matches", sourceMatches)
}
