// Normal-input original victory probe. No memory, winner, position or RNG injection.
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
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

type victoryState struct {
	Round      uint16    `json:"round_index"`
	Winner     uint16    `json:"winner_word"`
	Mode       uint16    `json:"mode"`
	Characters [2]uint16 `json:"characters"`
	Health     [2]uint16 `json:"health"`
	Flags      [2]uint8  `json:"flags_3eb7_3eb8"`
	Rows       uint8     `json:"crtc_rows"`
	Timer      uint16    `json:"timer"`
}
type draw struct {
	Slot        int    `json:"slot"`
	X           int    `json:"x"`
	Y           int    `json:"y"`
	Width       int    `json:"width"`
	Height      int    `json:"height"`
	SourceSI    uint16 `json:"source_si"`
	SourceDS    uint16 `json:"source_ds"`
	Caller      uint16 `json:"caller_ip"`
	Palette     uint8  `json:"palette"`
	Steps       uint64 `json:"steps"`
	EndSteps    uint64 `json:"end_steps"`
	SourceSHA   string `json:"source_sha256"`
	Writes      int    `json:"writes"`
	EqualWrites int    `json:"equal_writes"`
	Source      []byte `json:"-"`
	Before      []byte `json:"-"`
	Mask        []byte `json:"-"`
	Expected    []byte `json:"-"`
	SP          uint16 `json:"-"`
}

func main() {
	out := flag.String("out", "", "new output directory")
	attacker := flag.Int("attacker", -1, "0 or 1; -1 alternates attackers by normal round")
	messages := flag.Int("messages", 2, "number of completed messages, 1 or 2")
	flag.Parse()
	if *out == "" || *attacker < -1 || *attacker > 1 || *messages < 1 || *messages > 2 {
		panic("invalid arguments")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	write := func(n string, b []byte) { must(os.WriteFile(filepath.Join(*out, n), b, 0644)) }
	writeJSON := func(n string, v any) { b, e := json.MarshalIndent(v, "", "  "); must(e); write(n, append(b, '\n')) }
	script, e := os.ReadFile("/project/tools/victory_draw_receipt.go")
	must(e)
	write("victory_draw_receipt.go", script)
	inputs := map[string]string{}
	for _, n := range []string{"SF.EXE", "SF.COM", "NOKEY.EXE", "NAME.XBB"} {
		b, e := os.ReadFile(filepath.Join("/orig", n))
		must(e)
		inputs[n] = digest(b)
	}
	if inputs["SF.EXE"] != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("wrong EXE")
	}
	names, e := os.ReadFile("/orig/NAME.XBB")
	must(e)
	o, e := oracle.LoadProgram("/orig/NOKEY.EXE", "/orig", " /y")
	must(e)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	o.Enqueue("SF.COM", "")
	var ds, routineSP uint16
	word := func(off uint16) uint16 { return o.Word(oracle.Far(ds, off)) }
	state := func() victoryState {
		return victoryState{Round: word(0x1318), Winner: word(0x1322), Mode: word(0x18), Characters: [2]uint16{word(0x12ac), word(0x12ae)}, Health: [2]uint16{word(0x169c), word(0x169e)}, Flags: [2]uint8{o.Byte(oracle.Far(ds, 0x3eb7)), o.Byte(oracle.Far(ds, 0x3eb8))}, Rows: o.Byte(oracle.Far(ds, 0x1334)), Timer: word(0x2f26)}
	}
	var active bool
	var groupBefore, groupMask []byte
	var groupState victoryState
	var current *draw
	var draws []draw
	var records []map[string]any
	var routineSteps uint64
	var ticks uint64
	var counter uint16
	var lastCopy []byte
	var lastCopySteps uint64
	var refreshBefore, refreshBitmap []byte
	var refreshSP uint16
	var refreshes []map[string]any
	var setupBefore, setupMask []byte
	var setupCancel func()
	o.OnCall(oracle.Far(0x1b9, 0x33f4), func(o *oracle.Oracle) {
		if o.StackWord(0) != 0x5e77 {
			return
		}
		ds = o.DSReg()
		setupBefore = o.Bytes(oracle.Far(word(0xe), 0), 64000)
		setupMask = make([]byte, 64000)
		base := uint32(word(0xe)) * 16
		var err error
		setupCancel, err = o.ObserveWrites(base, base+63999, func(w oracle.MemoryWrite) { setupMask[w.Address-base] = 1 })
		must(err)
	})
	o.OnCall(oracle.Far(0x1b9, 0x3e9d), func(o *oracle.Oracle) { lastCopy = o.Bytes(oracle.Far(0xa000, 0), 64000); lastCopySteps = o.Steps() })
	o.OnCall(oracle.Far(0x1b9, 0x3faa), func(o *oracle.Oracle) {
		if o.StackWord(0) != 0x5e7a {
			return
		}
		ds = o.DSReg()
		refreshSP = o.SP()
		refreshBefore = o.Bytes(oracle.Far(word(0xe), 0), 64000)
		refreshBitmap = o.Bytes(oracle.Far(word(0xc)+0x1000, 0x8000), 10240)
		stem := fmt.Sprintf("hud-refresh-%02d", len(refreshes))
		write(stem+".before.idx", refreshBefore)
		write(stem+".last-copy.idx", lastCopy)
		write(stem+".bitmap", refreshBitmap)
		write(stem+".setup-before.idx", setupBefore)
		refreshes = append(refreshes, map[string]any{"fixture": stem, "entry_steps": o.Steps(), "last_copy_steps": lastCopySteps, "base_matches_last_copy": bytes.Equal(refreshBefore, lastCopy), "state": state(), "display_wins": [2]uint16{word(0x131e), word(0x1320)}})
		refreshes[len(refreshes)-1]["setup_base_matches_last_copy"] = bytes.Equal(setupBefore, lastCopy)
		refreshes[len(refreshes)-1]["hud_state"] = renderdata.HUDState{Counter: word(0x1a), Rows: int(o.Byte(oracle.Far(ds, 0x1334))), Health: [2]uint16{word(0x169c), word(0x169e)}, Pending: [2]uint16{word(0x16a0), word(0x16a2)}, Timer: word(0x2f26), Wins: [2]uint16{word(0x131e), word(0x1320)}, DisplayWins: [2]uint16{word(0x131e), word(0x1320)}, Round: word(0x1318), RoundState: word(0x131a), Characters: [2]uint16{word(0x12ac), word(0x12ae)}}
	})
	o.OnCall(oracle.Far(0x1b9, 0x3feb), func(o *oracle.Oracle) {
		if refreshBefore == nil || o.SP() != refreshSP {
			return
		}
		if setupCancel == nil {
			panic("missing setup observer")
		}
		setupCancel()
		setupCancel = nil
		after := o.Bytes(oracle.Far(word(0xe), 0), 64000)
		expected := append([]byte(nil), refreshBefore...)
		for i, v := range refreshBitmap {
			if v != 0 {
				at := int(o.Byte(oracle.Far(ds, 0x1334)))*320 + i
				if at >= 64000 {
					panic("HUD outside frame")
				}
				expected[at] = v | 0xa0
			}
		}
		if !bytes.Equal(expected, after) {
			panic("final HUD refresh differs")
		}
		record := refreshes[len(refreshes)-1]
		stem := record["fixture"].(string)
		write(stem+".after.idx", after)
		write(stem+".setup.mask", setupMask)
		record["end_steps"], record["after_sha256"] = o.Steps(), digest(after)
		writeJSON(stem+".json", record)
		refreshBefore = nil
	})
	o.OnCall(oracle.Far(0x1b9, 0x5d9f), func(o *oracle.Oracle) {
		if ds != 0 {
			v := word(0x1a)
			if counter != v {
				ticks++
				counter = v
			}
		}
	})
	o.OnCall(oracle.Far(0x1b9, 0x3963), func(o *oracle.Oracle) {
		if active {
			panic("nested victory routine")
		}
		ds = o.DSReg()
		routineSP = o.SP()
		routineSteps = o.Steps()
		groupState = state()
		groupBefore = o.Bytes(oracle.Far(0xa000, 0), 65536)
		groupMask = make([]byte, 65536)
		draws = nil
		active = true
	})
	o.OnCall(oracle.Far(0x1b9, 0x3685), func(o *oracle.Oracle) {
		if !active || o.ES() != 0xa000 {
			return
		}
		if current != nil {
			panic("nested VRAM helper")
		}
		si := o.SI()
		slot := -1
		for i := 0; i < 22; i++ {
			if binary.LittleEndian.Uint16(names[i*2:]) == si {
				slot = i
				break
			}
		}
		if slot < 0 {
			panic("unknown NAME slot")
		}
		w, h := int(names[si]), int(names[si+1])
		source := o.Bytes(oracle.Far(o.DSReg(), si), 2+w*h)
		if !bytes.Equal(source, names[int(si):int(si)+len(source)]) {
			panic("NAME source differs")
		}
		before := o.Bytes(oracle.Far(0xa000, 0), 65536)
		current = &draw{Slot: slot, X: int(o.DI()) % 320, Y: int(o.DI()) / 320, Width: w, Height: h, SourceSI: si, SourceDS: o.DSReg(), Caller: o.StackWord(0), Palette: uint8(o.BX() >> 8), Steps: o.Steps(), SourceSHA: digest(source), Source: source, Before: before, Mask: make([]byte, 65536), Expected: append([]byte(nil), before...), SP: o.SP()}
		for y := 0; y < h; y++ {
			for x := 0; x < w; x++ {
				v := source[2+y*w+x]
				if v&15 != 0 {
					at := (current.Y+y)*320 + current.X + x
					if at >= 65536 {
						panic("outside aperture")
					}
					current.Expected[at] = v | current.Palette
				}
			}
		}
	})
	// STOSB 位址先由實際 ES:DI 記錄，與從原檔預測的透明覆蓋獨立。
	o.OnCall(oracle.Far(0x1b9, 0x3696), func(o *oracle.Oracle) {
		if current == nil {
			return
		}
		at := int(o.ES())*16 + int(o.DI()) - 0xa0000
		if at < 0 || at >= 65536 {
			panic("unexpected VGA destination")
		}
		v := uint8(o.AX())
		if current.Expected[at] != v {
			panic("unexpected actual STOSB value")
		}
		current.Writes++
		if o.Byte(oracle.Far(o.ES(), o.DI())) == v {
			current.EqualWrites++
		}
		current.Mask[at] = 1
		groupMask[at] = 1
	})
	o.OnCall(oracle.Far(0x1b9, 0x36ae), func(o *oracle.Oracle) {
		if current == nil || o.SP() != current.SP {
			return
		}
		after := o.Bytes(oracle.Far(0xa000, 0), 65536)
		if !bytes.Equal(after, current.Expected) {
			panic("helper framebuffer differs")
		}
		expectedMask := make([]byte, 65536)
		for y := 0; y < current.Height; y++ {
			for x := 0; x < current.Width; x++ {
				if current.Source[2+y*current.Width+x]&15 != 0 {
					expectedMask[(current.Y+y)*320+current.X+x] = 1
				}
			}
		}
		if !bytes.Equal(current.Mask, expectedMask) {
			panic("actual STOSB coverage differs")
		}
		stem := fmt.Sprintf("victory-%02d-draw-%02d", len(records), len(draws))
		for suffix, b := range map[string][]byte{".source": current.Source, ".before.vram": current.Before, ".after.vram": after, ".mask": current.Mask} {
			write(stem+suffix, b)
		}
		current.EndSteps = o.Steps()
		writeJSON(stem+".json", current)
		draws = append(draws, *current)
		current = nil
	})
	o.OnCall(oracle.Far(0x1b9, 0x3a3f), func(o *oracle.Oracle) {
		if !active || o.SP() != routineSP {
			return
		}
		if current != nil || len(draws) == 0 {
			panic("incomplete victory")
		}
		after := o.Bytes(oracle.Far(0xa000, 0), 65536)
		expected := append([]byte(nil), groupBefore...)
		for _, d := range draws {
			for i, v := range d.Mask {
				if v != 0 {
					expected[i] = d.Expected[i]
				}
			}
		}
		if !bytes.Equal(after, expected) {
			panic("routine has unobserved framebuffer writes")
		}
		scanout, e := o.LinearScanout()
		must(e)
		stem := fmt.Sprintf("victory-%02d", len(records))
		for suffix, b := range map[string][]byte{".before.vram": groupBefore, ".after.vram": after, ".mask": groupMask, ".display.idx": scanout.Indices} {
			write(stem+suffix, b)
		}
		writeJSON(stem+".palette.json", o.Palette())
		writeJSON(stem+".scanout.json", scanout)
		record := map[string]any{"fixture": stem, "state": groupState, "start_steps": routineSteps, "end_steps": o.Steps(), "draws": draws, "display_sha256": digest(scanout.Indices), "before_sha256": digest(groupBefore), "after_sha256": digest(after), "normal_input_only": true, "base_matches_last_copy": bytes.Equal(groupBefore[:64000], lastCopy), "last_copy_steps": lastCopySteps}
		writeJSON(stem+".json", record)
		records = append(records, record)
		active = false
		fmt.Println(stem, groupState, "draws", len(draws), "steps", o.Steps())
	})
	step := func(n uint64) {
		must(o.Run(n))
		if o.Steps() > 2_500_000_000 {
			panic("instruction budget exceeded")
		}
	}
	step(40_000_000)
	must(o.MoveMouse(125, 181))
	o.PressButton(0)
	step(1_000_000)
	o.ReleaseButton(0)
	step(24_000_000)
	must(o.SendKeys("Return"))
	step(20_000_000)
	for i := 0; i < 4; i++ {
		must(o.SendKeys("Right"))
		step(1_000_000)
	}
	must(o.SendKeys("Return"))
	step(75_000_000)
	if o.Word(oracle.Far(0, 0x24)) != 0x524c || o.Word(oracle.Far(0, 0x26)) != 0x1b9 {
		panic("wrong battle IRQ")
	}
	isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
	if !bytes.Equal(isr[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		panic("wrong ISR")
	}
	ds = binary.LittleEndian.Uint16(isr[6:8])
	if state().Characters != [2]uint16{0, 4} {
		panic("not normal Jaan/Frank battle")
	}
	input := func(keys ...uint8) {
		for _, k := range o.HeldKeys() {
			o.KeyUp(k)
		}
		for _, k := range keys {
			o.KeyDown(k)
		}
	}
	frames := func(count uint64, approach bool) {
		end := ticks + count
		limit := o.Steps() + 150_000_000
		for ticks < end && o.Steps() < limit {
			step(250_000)
			if word(0x131a) != 0 || word(0x169c) == 0 || word(0x169e) == 0 {
				return
			}
			distance := int(int16(word(0x16d8))) - int(int16(word(0x16d6)))
			if distance < 0 {
				distance = -distance
			}
			if approach && distance <= 44 {
				return
			}
		}
	}
	for cycle := 0; cycle < 36 && len(records) < *messages; cycle++ {
		if word(0x131a) != 0 || word(0x169c) == 0 || word(0x169e) == 0 {
			input()
			round := word(0x1318)
			limit := o.Steps() + 150_000_000
			for o.Steps() < limit && len(records) < *messages {
				step(250_000)
				if word(0x1318) > round && word(0x131a) == 0 && word(0x169c) == 124 && word(0x169e) == 124 {
					break
				}
			}
			continue
		}
		player := *attacker
		if player < 0 {
			player = int(word(0x1318) % 2)
		}
		x0, x1 := int(int16(word(0x16d6))), int(int16(word(0x16d8)))
		direction, punch := uint8(0x20), uint8(0xf)
		if player == 0 && x0 > x1 {
			direction = 0x1e
		}
		if player == 1 {
			direction, punch = 0x4b, 0x1c
			if x1 < x0 {
				direction = 0x4d
			}
		}
		input(direction)
		frames(180, true)
		input(punch)
		frames(40, false)
		input()
		frames(30, false)
		fmt.Println("cycle", cycle, "ticks", ticks, "state", state())
	}
	input()
	if len(records) != *messages || current != nil || active {
		panic("incomplete normal victory coverage")
	}
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	writeJSON("receipt.json", map[string]any{"kind": "normal original direct-VRAM victory replay; no native HD claim", "inputs": inputs, "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(manifest), "records": records, "hud_refreshes": refreshes, "requested_messages": *messages, "final_steps": o.Steps(), "unimplemented": o.Unimplemented(), "state_control": "normal menu and keyboard only; no game-state writes", "rng_control": "bitmap replay contains no random decision; no cross-run RNG parity claim", "address_space": "runtime 01B9:IP; DS-relative game fields; VRAM physical A0000 plus byte offset"})
}
