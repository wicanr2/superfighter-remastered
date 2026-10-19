// Disposable normal-input shadow probe. It never writes game state.
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
func writeJSON(path string, v any) {
	b, e := json.MarshalIndent(v, "", "  ")
	must(e)
	must(os.WriteFile(path, append(b, '\n'), 0644))
}

type shadowDraw struct {
	Player               int    `json:"player"`
	X                    int    `json:"x"`
	Y                    int    `json:"y"`
	Camera               uint16 `json:"camera_x"`
	Left                 int    `json:"left_clip"`
	Right                int    `json:"right_clip"`
	Visible              int    `json:"visible_width"`
	Counter              uint16 `json:"counter"`
	SourceSHA256         string `json:"source_sha256"`
	Return               uint16 `json:"return_ip"`
	SP                   uint16 `json:"entry_sp"`
	started              bool
	base                 uint32
	destination          int
	before, mask, actual []byte
	writes, equalWrites  int
}

func main() {
	root := flag.String("root", "/orig", "read-only original files")
	out := flag.String("out", "", "new evidence directory")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output already exists")
	}
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	script, e := os.ReadFile("/project/tools/shadow_draw_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "shadow_draw_receipt.go"), script, 0644))
	inputs := map[string]string{}
	for _, name := range []string{"SF.EXE", "SF.COM", "NOKEY.EXE", "SHADOW.XLP"} {
		b, e := os.ReadFile(filepath.Join(*root, name))
		must(e)
		inputs[name] = digest(b)
	}
	if inputs["SF.EXE"] != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" || inputs["SHADOW.XLP"] != "a25f777105cc86468c91111152e8ef10dd4911d9b150e3c1a1020e21b7590bf1" {
		panic("wrong original source")
	}
	source, e := os.ReadFile(filepath.Join(*root, "SHADOW.XLP"))
	must(e)
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
		panic("battle IRQ not present")
	}
	isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
	if !bytes.Equal(isr[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		panic("unknown IRQ")
	}
	ds := binary.LittleEndian.Uint16(isr[6:8])
	word := func(off uint16) uint16 { return o.Word(oracle.Far(ds, off)) }
	var pending *shadowDraw
	var cancel func()
	var records []map[string]any
	fixtures := map[string]bool{}
	phase := "idle"
	geometryFailures, pixelFailures, maskFailures := 0, 0, 0
	o.OnCall(oracle.Far(0x1b9, 0x4167), func(*oracle.Oracle) {
		if pending != nil {
			if pending.SP == o.SP() && pending.Return == o.StackWord(0) {
				return
			}
			panic("unexpected nested shadow")
		}
		player := 1
		ret := o.StackWord(0)
		if ret == 0x4144 {
			player = 0
		} else if ret != 0x5d09 && ret != 0x5dc4 && ret != 0x5e5b {
			panic(fmt.Sprintf("unknown shadow return %04x", ret))
		}
		pending = &shadowDraw{Player: player, X: int(int16(o.AX() - word(0x1332))), Y: 178, Camera: word(0x1332), Counter: word(0x1a), Return: ret, SP: o.SP()}
	})
	o.OnCall(oracle.Far(0x1b9, 0x419c), func(*oracle.Oracle) {
		if pending == nil {
			panic("shadow header without entry")
		}
		if pending.started {
			return
		}
		p := pending
		p.started = true
		p.base = uint32(word(0xe)) * 16
		p.destination = int(uint32(o.ES())*16 + uint32(o.DI()) - p.base)
		p.Left, p.Right = int(o.BX()&255), int(o.BX()>>8)
		p.Visible = int(uint8(int(source[0]) - p.Left - p.Right))
		if int(source[0]) < p.Left {
			p.Visible = int(uint8(p.Visible - 1))
		}
		if p.Visible&128 != 0 {
			p.Visible = -1
		}
		p.before = o.Bytes(oracle.Far(word(0xe), 0), 64000)
		p.actual = append([]byte(nil), p.before...)
		p.mask = make([]byte, 64000)
		raw := o.Bytes(oracle.Far(o.DSReg(), o.SI()), len(source))
		p.SourceSHA256 = digest(raw)
		left, right := max(-p.X, 0), max(p.X+61-319, 0)
		if p.SourceSHA256 != inputs["SHADOW.XLP"] || o.DSReg() != ds || o.SI() != 0x1346 || o.ES() != word(0xe) || p.destination != 178*320+max(p.X, 0) || p.Left != left || p.Right != right {
			geometryFailures++
		}
		var e error
		cancel, e = o.ObserveWrites(p.base, p.base+63999, func(w oracle.MemoryWrite) {
			at := int(w.Address - p.base)
			p.mask[at] = 1
			p.writes++
			if p.actual[at] == w.Value {
				p.equalWrites++
			}
			p.actual[at] = w.Value
		})
		must(e)
	})
	o.OnCall(oracle.Far(0x1b9, 0x41df), func(*oracle.Oracle) {
		if pending == nil {
			return
		}
		p := pending
		if !p.started || o.SP() != p.SP {
			panic("incomplete shadow return")
		}
		cancel()
		cancel = nil
		predicted, mask := append([]byte(nil), p.before...), make([]byte, 64000)
		if p.Visible == 0 {
			panic("zero-width original loop is outside supported evidence")
		}
		if p.Visible > 0 {
			for y := 0; y < int(source[1]); y++ {
				for x := 0; x < p.Visible; x++ {
					value := source[2+y*int(source[0])+p.Left+x]
					at := p.destination + y*320 + x
					if value != 0 {
						if at < 0 || at >= 64000 {
							panic("shadow destination overflow")
						}
						predicted[at] = value | 0xa0
						mask[at] = 1
					}
				}
			}
		}
		after := o.Bytes(oracle.Far(word(0xe), 0), 64000)
		diff, mdiff := 0, 0
		for i := range after {
			if after[i] != predicted[i] {
				diff++
			}
			if mask[i] != p.mask[i] {
				mdiff++
			}
		}
		if !bytes.Equal(after, p.actual) {
			panic("observer replay differs")
		}
		if diff > 0 {
			pixelFailures++
		}
		if mdiff > 0 {
			maskFailures++
		}
		record := map[string]any{"phase": phase, "steps": o.Steps(), "draw": p, "pixel_differences": diff, "mask_differences": mdiff, "writes": p.writes, "equal_value_writes": p.equalWrites}
		key := fmt.Sprintf("%s-%d-%t-%t-%t", phase, p.Player, p.Left > 0, p.Right > 0, p.equalWrites > 0)
		if !fixtures[key] && len(fixtures) < 64 {
			fixtures[key] = true
			stem := fmt.Sprintf("shadow-%04d", len(records))
			record["fixture"] = stem
			for suffix, b := range map[string][]byte{".before.idx": p.before, ".after.idx": after, ".mask": p.mask} {
				must(os.WriteFile(filepath.Join(*out, stem+suffix), b, 0644))
			}
			writeJSON(filepath.Join(*out, stem+".palette.json"), o.Palette())
		}
		records = append(records, record)
		pending = nil
	})
	var phases []map[string]any
	for _, step := range []struct {
		name   string
		keys   []uint8
		frames int
	}{
		{"idle", nil, 12}, {"left-edge", []uint8{0x1e}, 70}, {"right-edge", []uint8{0x4d}, 70},
		{"approach", []uint8{0x20, 0x4b}, 100}, {"crossing-jump", []uint8{0x20, 0x11, 0x4b, 0x48}, 30},
		{"release", nil, 30}, {"crouch", []uint8{0x2d, 0x50}, 16}, {"opposite-walk", []uint8{0x1e, 0x4d}, 80},
	} {
		phase = step.name
		for _, k := range o.HeldKeys() {
			o.KeyUp(k)
		}
		for _, k := range step.keys {
			o.KeyDown(k)
		}
		start := len(records)
		for i := 0; i < step.frames; i++ {
			must(o.Run(1))
			must(o.RunUntil(oracle.At(oracle.Far(0x1b9, 0x3e9d)), oracle.Budget(8_000_000)))
		}
		phases = append(phases, map[string]any{"name": phase, "keys": step.keys, "shadow_draws": len(records) - start})
		fmt.Println(phase, len(records)-start)
	}
	if cancel != nil {
		cancel()
	}
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "normal original shadow draw evidence; not HD acceptance", "inputs": inputs, "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(manifest), "runtime_ds": ds, "address_space": "DOS runtime 01B9:IP and DS-relative offsets; not IDA MZ linear or file offsets", "records": records, "phases": phases, "geometry_failures": geometryFailures, "pixel_failures": pixelFailures, "mask_failures": maskFailures, "unimplemented": o.Unimplemented(), "state_control": "normal menus and held/released keyboard only; no memory, coordinate, health or RNG injection"})
	fmt.Println("draws", len(records), "fixtures", len(fixtures), "failures", geometryFailures, pixelFailures, maskFailures)
	if geometryFailures+pixelFailures+maskFailures != 0 {
		os.Exit(1)
	}
}
