// Disposable original round-message probe. Normal menu input; no game-state writes.
package main

import (
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
func writeJSON(path string, value any) {
	b, e := json.MarshalIndent(value, "", "  ")
	must(e)
	must(os.WriteFile(path, append(b, '\n'), 0644))
}

func main() {
	out := flag.String("out", "", "new evidence directory")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	hashes := map[string]string{}
	for _, name := range []string{"SF.EXE", "SF.COM", "NOKEY.EXE", "NAME.XBB", "0-9.XBB", "BOARD.COL"} {
		b, e := os.ReadFile(filepath.Join("/orig", name))
		must(e)
		hashes[name] = digest(b)
	}
	if hashes["SF.EXE"] != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("wrong EXE")
	}
	script, e := os.ReadFile("/project/tools/round_draw_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "round_draw_receipt.go"), script, 0644))
	o, e := oracle.LoadProgram("/orig/NOKEY.EXE", "/orig", " /y")
	must(e)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	o.Enqueue("SF.COM", "")
	var data, entrySP uint16
	var before, mask, source []byte
	var start map[string]any
	var cancel func()
	var records, frames []map[string]any
	var routineCancel func()
	var routineMask []byte
	var routineIndex int
	var routineSP uint16
	var backgrounds []map[string]any
	var bgCancel func()
	var bgBefore, bgSource, bgMask []byte
	var bgSP, bgRows, bgCamera uint16
	o.OnCall(oracle.Far(0x1b9, 0x3e09), func(o *oracle.Oracle) {
		if bgCancel != nil {
			return
		}
		data = o.DSReg()
		bgSP = o.SP()
		bgRows = uint16(o.Byte(oracle.Far(data, 0x1334)))
		bgCamera = o.Word(oracle.Far(data, 0x1332))
		seg := o.Word(oracle.Far(data, 0xe))
		bgBefore = o.Bytes(oracle.Far(seg, 0), 64000)
		bgSource = o.Bytes(oracle.Far(o.Word(oracle.Far(data, 0xc)), 0), 480*204)
		bgMask = make([]byte, 64000)
		base := uint32(seg) * 16
		bgCancel, e = o.ObserveWrites(base, base+63999, func(w oracle.MemoryWrite) { bgMask[w.Address-base] = 1 })
		must(e)
	})
	o.OnCall(oracle.Far(0x1b9, 0x3e43), func(o *oracle.Oracle) {
		if bgCancel == nil || o.SP() != bgSP {
			return
		}
		bgCancel()
		bgCancel = nil
		after := o.Bytes(oracle.Far(o.Word(oracle.Far(data, 0xe)), 0), 64000)
		predicted, predictedMask := append([]byte(nil), bgBefore...), make([]byte, 64000)
		for row := int(bgRows); row < min(200, int(bgRows)+192); row++ {
			for col := 0; col < 320; col++ {
				at := row*320 + col
				predicted[at] = bgSource[row*480+int(bgCamera)+col]
				predictedMask[at] = 1
			}
		}
		pixelDiffs, maskDiffs := 0, 0
		for i := range after {
			if after[i] != predicted[i] {
				pixelDiffs++
			}
			if bgMask[i] != predictedMask[i] {
				maskDiffs++
			}
		}
		stem := fmt.Sprintf("background-%03d", len(backgrounds))
		for suffix, b := range map[string][]byte{".before.idx": bgBefore, ".after.idx": after, ".mask": bgMask, ".source": bgSource} {
			must(os.WriteFile(filepath.Join(*out, stem+suffix), b, 0644))
		}
		backgrounds = append(backgrounds, map[string]any{"fixture": stem, "steps": o.Steps(), "rows": bgRows, "camera_x": bgCamera, "source_sha256": digest(bgSource), "pixel_differences": pixelDiffs, "mask_differences": maskDiffs})
	})
	width, column, x, y := 0, 0, 0, 0
	o.OnCall(oracle.Far(0x1b9, 0x3570), func(o *oracle.Oracle) {
		if data == 0 {
			data = o.DSReg()
		}
	})
	o.OnCall(oracle.Far(0x1b9, 0x3635), func(o *oracle.Oracle) {
		if o.StackWord(0) != 0x3599 {
			panic("unknown message caller")
		}
		if cancel != nil {
			if o.SP() != entrySP {
				panic("nested message draw")
			}
			return
		}
		entrySP = o.SP()
		word := func(off uint16) uint16 { return o.Word(oracle.Far(data, off)) }
		seg := word(0xe)
		if o.ES() != seg || o.DSReg() != seg {
			panic("unexpected destination/source segment")
		}
		before = o.Bytes(oracle.Far(seg, 0), 64000)
		source = append([]byte(nil), before[:1442]...)
		mask = make([]byte, 64000)
		width, column = int(o.CX()), int(o.SI())
		x, y = int(o.DI())%320, int(o.DI())/320
		start = map[string]any{"steps": o.Steps(), "counter": word(0x1a), "round_index": word(0x1318), "round_state": word(0x131a), "half_width": word(0x131c), "crtc_rows": o.Byte(oracle.Far(data, 0x1334)), "source_ds": o.DSReg(), "destination_es": o.ES(), "source_si": o.SI(), "destination_di": o.DI(), "width": width, "x": x, "y": y, "source_sha256": digest(source)}
		base := uint32(seg) * 16
		cancel, e = o.ObserveWrites(base, base+63999, func(w oracle.MemoryWrite) { mask[w.Address-base] = 1 })
		must(e)
	})
	o.OnCall(oracle.Far(0x1b9, 0x3666), func(o *oracle.Oracle) {
		if cancel == nil || o.SP() != entrySP {
			return
		}
		cancel()
		cancel = nil
		seg := o.Word(oracle.Far(data, 0xe))
		after := o.Bytes(oracle.Far(seg, 0), 64000)
		predicted, expectedMask := append([]byte(nil), before...), make([]byte, 64000)
		if width < 1 || width > 96 || column+width > 96 || x+width > 320 || y+15 > 200 {
			panic("invalid geometry")
		}
		for row := 0; row < 15; row++ {
			for col := 0; col < width; col++ {
				v := source[2+row*96+column+col]
				if v != 0 {
					at := (y+row)*320 + x + col
					predicted[at] = v | 0xa0
					expectedMask[at] = 1
				}
			}
		}
		diffs, maskDiffs, writes, same := 0, 0, 0, 0
		for i := range after {
			if after[i] != predicted[i] {
				diffs++
			}
			if mask[i] != expectedMask[i] {
				maskDiffs++
			}
			if mask[i] != 0 {
				writes++
				if before[i] == after[i] {
					same++
				}
			}
		}
		stem := fmt.Sprintf("round-%03d", len(records))
		for suffix, b := range map[string][]byte{".source": source, ".before.idx": before, ".after.idx": after, ".mask": mask} {
			must(os.WriteFile(filepath.Join(*out, stem+suffix), b, 0644))
		}
		start["fixture"], start["pixel_differences"], start["mask_differences"], start["writes"], start["equal_writes"] = stem, diffs, maskDiffs, writes, same
		writeJSON(filepath.Join(*out, stem+".palette.json"), o.Palette())
		records = append(records, start)
		routineIndex, routineSP = len(records)-1, entrySP+4
		routineMask = append([]byte(nil), mask...)
		base := uint32(seg) * 16
		routineCancel, e = o.ObserveWrites(base, base+63999, func(w oracle.MemoryWrite) { routineMask[w.Address-base] = 1 })
		must(e)
	})
	o.OnCall(oracle.Far(0x1b9, 0x3634), func(o *oracle.Oracle) {
		if routineCancel == nil || o.SP() != routineSP {
			return
		}
		routineCancel()
		routineCancel = nil
		record := records[routineIndex]
		stem := record["fixture"].(string)
		after := o.Bytes(oracle.Far(o.Word(oracle.Far(data, 0xe)), 0), 64000)
		must(os.WriteFile(filepath.Join(*out, stem+".routine.after.idx"), after, 0644))
		must(os.WriteFile(filepath.Join(*out, stem+".routine.mask"), routineMask, 0644))
		record["routine_complete_steps"] = o.Steps()
	})
	o.OnCall(oracle.Far(0x1b9, 0x3e9d), func(o *oracle.Oracle) {
		if data == 0 || len(records) == 0 {
			return
		}
		state := o.Word(oracle.Far(data, 0x131a))
		if state > 4 {
			return
		}
		frames = append(frames, map[string]any{"steps": o.Steps(), "round_state_after_draw": state, "last_draw": len(records) - 1, "screen_sha256": digest(o.Bytes(oracle.Far(0xa000, 0), 64000))})
	})
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
	if cancel != nil {
		cancel()
		panic("unfinished primitive")
	}
	if routineCancel != nil {
		routineCancel()
		panic("unfinished routine")
	}
	if len(records) == 0 {
		panic("no message draws")
	}
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
	if binary.LittleEndian.Uint16(isr[6:8]) != data {
		panic("data segment mismatch")
	}
	if bgCancel != nil {
		bgCancel()
		panic("unfinished background")
	}
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "normal first-round original draw replay; no HD rendering", "address_space": "runtime 01B9:IP and DS-relative offsets", "inputs": hashes, "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(manifest), "records": records, "display_frames": frames, "background_records": backgrounds, "unimplemented": o.Unimplemented(), "state_control": "normal menu only; no memory or RNG writes"})
	fmt.Println("draws", len(records), "frames", len(frames), "steps", o.Steps())
}
