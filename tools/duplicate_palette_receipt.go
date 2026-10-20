// Normal-input duplicate-character palette probe; no production rendering or state injection.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

func main() {
	out := flag.String("out", "", "new output directory")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	writeJSON := func(name string, v any) {
		b, e := json.MarshalIndent(v, "", "  ")
		must(e)
		must(os.WriteFile(name, append(b, '\n'), 0644))
	}
	script, e := os.ReadFile("/project/tools/duplicate_palette_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "duplicate_palette_receipt.go"), script, 0644))
	col, e := os.ReadFile("/orig/MAN.COL")
	must(e)
	if len(col) != 768 || digest(col) != "7153214bf444684179b5296ad1c4dfc874385cbf6e2d5e0c215c13e711749ce5" {
		panic("palette source mismatch")
	}
	for _, v := range col {
		if v > 63 {
			panic("not six-bit palette")
		}
	}
	var cases []map[string]any
	for character := 0; character < 11; character++ {
		dir := filepath.Join(*out, fmt.Sprintf("character-%02d", character))
		must(os.Mkdir(dir, 0755))
		c, e := gamecore.New("/orig", filepath.Join(dir, "user-data"))
		must(e)
		c.EnableEffects()
		c.EnableHUD()
		c.EnableShadows()
		c.EnableRounds()
		c.EnableDisplay()
		c.Pause(false)
		step := func(n uint64) {
			must(c.Step(n))
			if c.Status().Steps > 600_000_000 {
				panic("bounded instruction budget exceeded")
			}
		}
		step(40_000_000)
		must(c.Mouse(125, 181, true))
		step(1_000_000)
		must(c.Mouse(125, 181, false))
		step(24_000_000)
		for i := 0; i < character; i++ {
			must(c.MenuKey("Right"))
			step(1_000_000)
		}
		must(c.MenuKey("Return"))
		step(20_000_000)
		must(c.MenuKey("Return"))
		step(75_000_000)
		if c.Status().Fighters != [2]int{character, character} {
			panic("normal duplicate selection mismatch")
		}
		ready := func() gamecore.Presentation {
			for {
				f := c.Presentation()
				if f.LayersComplete && f.HUD != nil && f.HUD.State.RoundState == 0 && f.RoundMessage == nil && f.Scanout != nil {
					return f
				}
				step(250_000)
			}
		}
		data, e := os.ReadFile(filepath.Join("/orig", fmt.Sprintf("SFMAN%02d.DAT", character+1)))
		must(e)
		var base, alternate [16][3]uint8
		for i := 0; i < 16; i++ {
			for k := 0; k < 3; k++ {
				v := data[0xac8+i*3+k]
				base[i][k] = v<<2 | v>>4
				v = col[character*48+i*3+k]
				alternate[i][k] = v<<2 | v>>4
			}
		}
		var samples []map[string]any
		save := func(name string, f gamecore.Presentation) {
			if !renderdata.Match(f.Layers, f.Pixels) || !f.Scanout.Matches(f.Pixels, f.VRAMTail) || c.Status().Training.Modified {
				panic("incomplete or modified frame")
			}
			var first, second [16][3]uint8
			copy(first[:], f.Palette[192:208])
			copy(second[:], f.Palette[224:240])
			sample := map[string]any{"name": name, "serial": f.Serial, "steps": f.Steps, "scene": f.Scene, "first_matches_DAT": first == base, "second_matches_MAN_COL": second == alternate, "palettes_distinct": first != second}
			writeJSON(filepath.Join(dir, name+".frame.json"), f)
			writeJSON(filepath.Join(dir, name+".palette.json"), f.Palette)
			must(os.WriteFile(filepath.Join(dir, name+".idx"), f.Pixels, 0644))
			must(os.WriteFile(filepath.Join(dir, name+".vram-tail"), f.VRAMTail, 0644))
			for i, l := range f.Layers {
				must(os.WriteFile(filepath.Join(dir, fmt.Sprintf("%s.layer-%02d.idx", name, i)), l.Indices, 0644))
				must(os.WriteFile(filepath.Join(dir, fmt.Sprintf("%s.layer-%02d.mask", name, i)), l.Coverage, 0644))
			}
			samples = append(samples, sample)
		}
		save("idle", ready())
		must(c.SetInput([]gamecore.Source{{Player: 0, Name: "keyboard", Keys: []uint8{0x20}}, {Player: 1, Name: "keyboard", Keys: []uint8{0x4b}}}))
		end := c.Status().Frames + 12
		for c.Status().Frames < end {
			step(250_000)
		}
		must(c.SetInput(nil))
		save("walk", ready())
		first, _ := json.Marshal(base)
		second, _ := json.Marshal(alternate)
		row := map[string]any{"character": character, "source_DAT_sha256": digest(data), "MAN_COL_file_offset": character * 48, "base_palette_sha256": digest(first), "alternate_palette_sha256": digest(second), "samples": samples}
		writeJSON(filepath.Join(dir, "receipt.json"), row)
		cases = append(cases, row)
		c.Close()
		runtime.GC()
		fmt.Println("sampled duplicate", character, samples)
	}
	inputs := map[string]string{}
	for _, name := range []string{"workplace/source-manifest.json", "workplace/dosgolem-patched-manifest.json", "internal/gamecore/core.go", "internal/renderdata/layers.go"} {
		b, e := os.ReadFile(filepath.Join("/project", name))
		must(e)
		inputs[name] = digest(b)
	}
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "normal duplicate-character original palette source sampling; not HD integration", "script_sha256": digest(script), "go_version": runtime.Version(), "MAN_COL_sha256": digest(col), "inputs": inputs, "cases": cases, "limits": "normal versus, eleven duplicates and idle/walk only; no state injection, forced wins, all animations or controlled RNG parity claim"})
}
