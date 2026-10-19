// Command input_receipt is a disposable original-game input experiment.
// Run from the recorded dosgolem snapshot module; imports only its public API.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
	"path/filepath"

	"github.com/wicanr2/dosgolem/oracle"
)

type observation struct {
	Steps     uint64            `json:"steps"`
	DS        uint16            `json:"data_segment"`
	KeyValues []byte            `json:"key_values_3ef4_3ef5"`
	Words     map[string]uint16 `json:"raw_ds_words"`
	Bytes     map[string]uint8  `json:"raw_ds_bytes"`
	IRQ1      uint64            `json:"irq1_delivered"`
}

func observe(o *oracle.Oracle, ds uint16) observation {
	r := observation{Steps: o.Steps(), DS: ds, IRQ1: o.IRQ1Delivered(),
		KeyValues: o.Bytes(oracle.Far(ds, 0x3ef4), 2), Words: map[string]uint16{}, Bytes: map[string]uint8{}}
	for _, off := range []uint16{0x18, 0x1232, 0x133a, 0x133c, 0x133e, 0x1340} {
		r.Words[fmt.Sprintf("%04X", off)] = o.Word(oracle.Far(ds, off))
	}
	for _, off := range []uint16{0x159e, 0x159f, 0x15a0, 0x16ae, 0x16af, 0x16b4, 0x16b5, 0x16ea, 0x16eb, 0x3eba} {
		r.Bytes[fmt.Sprintf("%04X", off)] = o.Byte(oracle.Far(ds, off))
	}
	return r
}

func saveScreen(o *oracle.Oracle, out string) error {
	w, h, rgb := o.ScreenRGB()
	img := image.NewRGBA(image.Rect(0, 0, w, h))
	for i := 0; i < w*h; i++ {
		img.SetRGBA(i%w, i/w, color.RGBA{rgb[i*3], rgb[i*3+1], rgb[i*3+2], 255})
	}
	f, err := os.Create(out)
	if err != nil {
		return err
	}
	defer f.Close()
	return png.Encode(f, img)
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
func main() {
	root := flag.String("root", "/orig", "read-only original directory")
	out := flag.String("out", "", "new receipt directory")
	mode := flag.String("mode", "single", "single or versus, normal title choice")
	recipes := flag.Bool("recipes", false, "measure Jaan recipes at original loop boundaries")
	flag.Parse()
	if *out == "" || (*mode != "single" && *mode != "versus") {
		panic("out and valid mode required")
	}
	if _, err := os.Stat(*out); !os.IsNotExist(err) {
		panic("output must not exist")
	}
	must(os.MkdirAll(*out, 0755))
	exe, err := os.ReadFile(filepath.Join(*root, "SF.EXE"))
	must(err)
	digest := sha256.Sum256(exe)
	if hex.EncodeToString(digest[:]) != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("source mismatch")
	}
	o, err := oracle.LoadProgram(filepath.Join(*root, "NOKEY.EXE"), *root, " /y")
	must(err)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	o.Enqueue("SF.COM", "")
	// Exactly ordinary title input, then normal selection confirmations.
	must(o.Run(40_000_000))
	x := 55
	if *mode == "versus" {
		x = 125
	}
	must(o.MoveMouse(x, 181))
	o.PressButton(0)
	must(o.Run(1_000_000))
	o.ReleaseButton(0)
	must(o.Run(24_000_000))
	must(o.SendKeys("Return"))
	must(o.Run(20_000_000))
	if *mode == "versus" {
		must(o.SendKeys("Return"))
	}
	must(o.Run(75_000_000))
	must(saveScreen(o, filepath.Join(*out, "normal-start.png")))
	isr := oracle.Far(o.Word(oracle.Far(0, 0x26)), o.Word(oracle.Far(0, 0x24)))
	if isr.Seg != 0x01b9 || isr.Off != 0x524c {
		panic(fmt.Sprintf("unexpected IRQ1 vector %s", isr))
	}
	// Runtime loader relocated MOV AX,DS; read it back instead of assuming DGROUP.
	code := o.Bytes(isr, 10)
	debug, _ := json.MarshalIndent(map[string]any{"irq1_vector": isr.String(), "runtime_isr_prefix": hex.EncodeToString(code), "steps": o.Steps()}, "", "  ")
	must(os.WriteFile(filepath.Join(*out, "startup-diagnostic.json"), debug, 0644))
	if !bytes.Equal(code[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		panic(fmt.Sprintf("ISR bytes mismatch: % X", code))
	}
	ds := uint16(code[6]) | uint16(code[7])<<8
	keyTable := o.Bytes(oracle.Far(ds, 0x3f16), 24)
	if !bytes.Equal(keyTable, []byte{0x1e, 0x2c, 0x2d, 0x2e, 0x20, 0x12, 0x11, 0x10, 0x4b, 0x4f, 0x50, 0x51, 0x4d, 0x49, 0x48, 0x47, 2, 6, 4, 5, 1, 9, 8, 10}) {
		panic("keyboard table bytes mismatch")
	}
	initial := observe(o, ds)
	state := o.Save()
	type result struct {
		Name             string  `json:"name"`
		Scans            []uint8 `json:"scans"`
		Before, Down, Up observation
		Error            string `json:"error,omitempty"`
	}
	var results []result
	cases := []struct {
		name  string
		scans []uint8
	}{
		{"neutral", nil}, {"p1-punch", []uint8{0x0f}}, {"p1-kick", []uint8{0x2a}}, {"p1-pk", []uint8{0x0f, 0x2a}},
		{"p2-punch", []uint8{0x1c}}, {"p2-kick", []uint8{0x36}}, {"p2-pk", []uint8{0x1c, 0x36}},
		{"both-punch", []uint8{0x0f, 0x1c}}, {"both-pk", []uint8{0x0f, 0x2a, 0x1c, 0x36}},
	}
	for i, scan := range keyTable[:16] {
		cases = append(cases, struct {
			name  string
			scans []uint8
		}{fmt.Sprintf("direction-%02d-%02X", i, scan), []uint8{scan}})
	}
	if *recipes {
		cases = nil
	}
	for _, c := range cases {
		for _, s := range o.HeldKeys() {
			o.KeyUp(s)
		}
		o.Restore(state)
		r := result{Name: c.name, Scans: c.scans, Before: observe(o, ds)}
		for _, s := range c.scans {
			o.KeyDown(s)
		}
		if err := o.Run(1_000_000); err != nil {
			r.Error = err.Error()
		}
		r.Down = observe(o, ds)
		must(saveScreen(o, filepath.Join(*out, c.name+"-down.png")))
		for _, s := range c.scans {
			o.KeyUp(s)
		}
		if err := o.Run(1_000_000); err != nil {
			r.Error += err.Error()
		}
		r.Up = observe(o, ds)
		results = append(results, r)
		fmt.Printf("%s down=% X up=% X\n", c.name, r.Down.KeyValues, r.Up.KeyValues)
	}
	var recipeResults []map[string]any
	if *recipes {
		type phase struct {
			scans  []uint8
			frames int
		}
		plans := []struct {
			name     string
			player   int
			expected uint8
			phases   []phase
		}{
			{"p1-thunder", 0, 0x24, []phase{{[]uint8{0x20}, 1}, {[]uint8{0x2e}, 1}, {[]uint8{0x2d, 0x0f}, 1}}},
			{"p2-thunder", 1, 0x24, []phase{{[]uint8{0x4b}, 1}, {[]uint8{0x4f}, 1}, {[]uint8{0x50, 0x1c}, 1}}},
			{"p1-whirlwind", 0, 0x23, []phase{{[]uint8{0x2d}, 1}, {[]uint8{0x2c}, 1}, {[]uint8{0x1e, 0x2a}, 1}}},
			{"p2-whirlwind", 1, 0x23, []phase{{[]uint8{0x50}, 1}, {[]uint8{0x51}, 1}, {[]uint8{0x4d, 0x36}, 1}}},
			{"p1-ironhead-12", 0, 0x22, []phase{{[]uint8{0x2d}, 12}, {[]uint8{0x11, 0x2a}, 1}}},
			{"p2-ironhead-12", 1, 0x22, []phase{{[]uint8{0x50}, 12}, {[]uint8{0x48, 0x36}, 1}}},
			{"p1-throw-approach", 0, 0x25, []phase{{[]uint8{0x20}, 72}, {[]uint8{0x20, 0x0f}, 1}}},
			{"p2-throw-approach", 1, 0x25, []phase{{[]uint8{0x4b}, 72}, {[]uint8{0x4b, 0x1c}, 1}}},
		}
		begin := oracle.Far(isr.Seg, 0x5d9f)
		selected := oracle.Far(isr.Seg, 0x5db5)
		for _, plan := range plans {
			for _, scan := range o.HeldKeys() {
				o.KeyUp(scan)
			}
			o.Restore(state)
			must(o.RunUntil(oracle.At(begin), oracle.Budget(5_000_000)))
			var samples []observation
			for _, phase := range plan.phases {
				for _, scan := range o.HeldKeys() {
					o.KeyUp(scan)
				}
				for _, scan := range phase.scans {
					o.KeyDown(scan)
				}
				for frame := 0; frame < phase.frames; frame++ {
					must(o.Run(1))
					must(o.RunUntil(oracle.At(selected), oracle.Budget(5_000_000)))
					samples = append(samples, observe(o, ds))
					must(o.Run(1))
					must(o.RunUntil(oracle.At(begin), oracle.Budget(5_000_000)))
				}
			}
			last := samples[len(samples)-1]
			path := last.Bytes[fmt.Sprintf("%04X", 0x16ea+plan.player)]
			for _, scan := range o.HeldKeys() {
				o.KeyUp(scan)
			}
			must(o.Run(2_000_000))
			must(saveScreen(o, filepath.Join(*out, plan.name+".png")))
			recipeResults = append(recipeResults, map[string]any{"name": plan.name, "expected_path_candidate": plan.expected, "actual_path": path, "matched": path == plan.expected, "samples": samples, "after_release": observe(o, ds)})
			fmt.Printf("recipe %s expected=%02X actual=%02X\n", plan.name, plan.expected, path)
		}
	}
	receipt := map[string]any{"kind": "normal-player-path snapshot input experiment; not full gameplay completion",
		"mode": *mode, "input_sha256": hex.EncodeToString(digest[:]), "initial": initial, "irq1_vector": isr.String(), "runtime_isr_prefix": hex.EncodeToString(code),
		"keyboard_tables": hex.EncodeToString(keyTable), "results": results, "recipes": recipeResults, "opened": o.Opened(), "unimplemented": o.Unimplemented(),
		"rng_control":    "full original-machine snapshot restored before each variant; raw RNG candidate bytes recorded, no cross-implementation RNG claim",
		"source":         "recorded dosgolem snapshot with queued-entry IF patch; public oracle API only",
		"snapshot_limit": "oracle.State does not rewind host file handles or host held-key map; held sources explicitly cleared; all initial assets already loaded"}
	data, err := json.MarshalIndent(receipt, "", "  ")
	must(err)
	must(os.WriteFile(filepath.Join(*out, "receipt.json"), append(data, '\n'), 0644))
}
