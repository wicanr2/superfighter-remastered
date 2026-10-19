// Disposable normal-input HUD probe; no game-state or random-number injection.
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
func writeJSON(path string, value any) {
	b, e := json.MarshalIndent(value, "", "  ")
	must(e)
	must(os.WriteFile(path, append(b, '\n'), 0644))
}

type hudState struct {
	Counter     uint16    `json:"counter"`
	Rows        uint8     `json:"crtc_rows"`
	Health      [2]uint16 `json:"display_health"`
	Pending     [2]uint16 `json:"pending_damage"`
	Timer       uint16    `json:"timer"`
	Wins        [2]uint16 `json:"wins"`
	DisplayWins [2]uint16 `json:"display_wins"`
	Round       uint16    `json:"round_index"`
	RoundState  uint16    `json:"round_state"`
	Characters  [2]uint16 `json:"characters"`
	X           [2]int    `json:"x"`
}

func main() {
	root := flag.String("root", "/orig", "read-only original files")
	out := flag.String("out", "", "new output directory")
	combat := flag.Bool("combat", false, "alternate ordinary attacks and approach using observed positions")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	hashes := map[string]string{}
	for _, name := range []string{"SF.EXE", "SF.COM", "NOKEY.EXE", "NAME.XBB", "BOARD.XBB", "BOARD.COL", "0-9.XBB", "SFMAN01.DAT", "SFMAN05.DAT"} {
		b, e := os.ReadFile(filepath.Join(*root, name))
		must(e)
		hashes[name] = digest(b)
	}
	if hashes["SF.EXE"] != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("wrong input")
	}
	o, e := oracle.LoadProgram(filepath.Join(*root, "NOKEY.EXE"), *root, " /y")
	must(e)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	o.Enqueue("SF.COM", "")
	var displayWins [2]uint16
	var setupEvents []map[string]any
	o.OnCall(oracle.Far(0x1b9, 0x34e6), func(o *oracle.Oracle) {
		data := o.DSReg()
		displayWins = [2]uint16{o.Word(oracle.Far(data, 0x131e)), o.Word(oracle.Far(data, 0x1320))}
		setupEvents = append(setupEvents, map[string]any{"steps": o.Steps(), "runtime_ds": data, "display_wins": displayWins})
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
	if o.Word(oracle.Far(0, 0x24)) != 0x524c || o.Word(oracle.Far(0, 0x26)) != 0x1b9 {
		panic("wrong battle IRQ")
	}
	isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
	if !bytes.Equal(isr[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		panic("wrong ISR")
	}
	ds := binary.LittleEndian.Uint16(isr[6:8])
	word := func(off uint16) uint16 { return o.Word(oracle.Far(ds, off)) }
	state := func() hudState {
		return hudState{Counter: word(0x1a), Rows: o.Byte(oracle.Far(ds, 0x1334)),
			Health: [2]uint16{word(0x169c), word(0x169e)}, Pending: [2]uint16{word(0x16a0), word(0x16a2)},
			Timer: word(0x2f26), Wins: [2]uint16{word(0x131e), word(0x1320)}, DisplayWins: displayWins, Round: word(0x1318), RoundState: word(0x131a),
			Characters: [2]uint16{word(0x12ac), word(0x12ae)}, X: [2]int{int(int16(word(0x16d6))), int(int16(word(0x16d8)))}}
	}
	var before, bitmap, mask []byte
	var cancel func()
	var base uint32
	var atEntry hudState
	var records []map[string]any
	fixtures := map[string]bool{}
	phase := "idle"
	o.OnCall(oracle.Far(0x1b9, 0x3faa), func(*oracle.Oracle) {
		if cancel != nil {
			panic("nested HUD")
		}
		base = uint32(word(0xe)) * 16
		before = o.Bytes(oracle.Far(word(0xe), 0), 64000)
		bitmap = o.Bytes(oracle.Far(word(0xc)+0x1000, 0x8000), 320*32)
		mask = make([]byte, 64000)
		atEntry = state()
		var e error
		cancel, e = o.ObserveWrites(base, base+63999, func(w oracle.MemoryWrite) { mask[w.Address-base] = 1 })
		must(e)
	})
	o.OnCall(oracle.Far(0x1b9, 0x3feb), func(*oracle.Oracle) {
		if cancel == nil {
			return
		}
		cancel()
		cancel = nil
		after := o.Bytes(oracle.Far(word(0xe), 0), 64000)
		predicted, predictedMask := append([]byte(nil), before...), make([]byte, 64000)
		for i, v := range bitmap {
			at := int(atEntry.Rows)*320 + i
			if v != 0 && at < 64000 {
				predicted[at] = v | 0xa0
				predictedMask[at] = 1
			}
		}
		diff, maskDiff, coverage := 0, 0, 0
		for i := range after {
			if after[i] != predicted[i] {
				diff++
			}
			if mask[i] != predictedMask[i] {
				maskDiff++
			}
			coverage += int(mask[i])
		}
		key := fmt.Sprintf("%d-%d-%t-%t-%d-%d-%d-%d", atEntry.Health[0]/16, atEntry.Health[1]/16, atEntry.Pending[0] > 0, atEntry.Pending[1] > 0, atEntry.Timer/10, atEntry.Wins[0], atEntry.Wins[1], atEntry.Round)
		record := map[string]any{"phase": phase, "steps": o.Steps(), "state": atEntry, "pixel_differences": diff, "mask_differences": maskDiff, "coverage": coverage, "hud_bitmap_sha256": digest(bitmap)}
		if !fixtures[key] && len(fixtures) < 80 {
			fixtures[key] = true
			stem := fmt.Sprintf("hud-%04d", len(records))
			record["fixture"] = stem
			for suffix, b := range map[string][]byte{".bitmap": bitmap, ".before.idx": before, ".after.idx": after, ".mask": mask} {
				must(os.WriteFile(filepath.Join(*out, stem+suffix), b, 0644))
			}
			writeJSON(filepath.Join(*out, stem+".palette.json"), o.Palette())
		}
		records = append(records, record)
	})
	var phases []map[string]any
	var transitionWaits []map[string]any
	stop := "frame budget exhausted normally"
	advance := func() bool {
		if e := o.Run(1); e != nil {
			stop = e.Error()
			return false
		}
		if e := o.RunUntil(oracle.At(oracle.Far(0x1b9, 0x3e9d)), oracle.Budget(8_000_000)); e != nil {
			stop = e.Error()
			if len(o.Unimplemented()) == 0 && (word(0x131a) != 0 || word(0x1318) != 0) {
				transitionWaits = append(transitionWaits, map[string]any{"steps": o.Steps(), "ip": o.IP(), "state": state(), "reason": stop})
				// 正常回合初始化與首次進場使用相同的 75M 上限，保留等待前後狀態。
				if e = o.RunUntil(oracle.At(oracle.Far(0x1b9, 0x3e9d)), oracle.Budget(75_000_000)); e == nil {
					stop = "frame budget exhausted normally"
					return true
				}
				stop = e.Error()
			}
			return false
		}
		return true
	}
	input := func(name string, keys []uint8, frames int, approach bool) bool {
		phase = name
		for _, k := range o.HeldKeys() {
			o.KeyUp(k)
		}
		for _, k := range keys {
			o.KeyDown(k)
		}
		start := len(records)
		for i := 0; i < frames; i++ {
			if !advance() {
				return false
			}
			s := state()
			distance := s.X[1] - s.X[0]
			if distance < 0 {
				distance = -distance
			}
			if approach && distance <= 44 {
				break
			}
		}
		phases = append(phases, map[string]any{"name": name, "keys": keys, "hud_draws": len(records) - start, "state": state()})
		fmt.Println(name, len(records)-start, state())
		return true
	}
	if *combat {
		for cycle := 0; cycle < 12; cycle++ {
			s := state()
			direction := uint8(0x20)
			if s.X[0] > s.X[1] {
				direction = 0x1e
			}
			if !input(fmt.Sprintf("approach-%d", cycle), []uint8{direction}, 180, true) {
				break
			}
			punch := uint8(0xf)
			if cycle%2 == 0 {
				punch = 0x1c
			}
			if !input(fmt.Sprintf("punch-%d", cycle), []uint8{punch}, 40, false) {
				break
			}
			if !input(fmt.Sprintf("release-%d", cycle), nil, 30, false) {
				break
			}
			if state().Round != 0 || state().Wins != [2]uint16{} {
				input("round-transition", nil, 160, false)
				break
			}
		}
	} else if input("idle", nil, 16, false) && input("p1-approach", []uint8{0x20}, 180, true) && input("p1-punch", []uint8{0xf}, 260, false) && input("release", nil, 100, false) && input("p1-approach-again", []uint8{0x20}, 180, true) {
		input("p2-punch", []uint8{0x1c}, 260, false)
	}
	if cancel != nil {
		cancel()
	}
	script, e := os.ReadFile("/project/tools/hud_draw_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "hud_draw_receipt.go"), script, 0644))
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "normal two-player HUD bitmap and field experiment; not HD rendering", "address_space": "runtime 01B9:IP, DS-relative offsets; source-file offsets separate", "inputs": hashes, "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(manifest), "records": records, "phases": phases, "hud_setup_events": setupEvents, "transition_waits": transitionWaits, "final_state": state(), "stop": stop, "unimplemented": o.Unimplemented(), "state_control": "normal menu and keyboard only; no memory or RNG injection"})
	fmt.Println("HUD draws", len(records), "fixtures", len(fixtures), "stop", stop)
}
