// Normal-input public Core comparison with round observation off/on.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"reflect"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func main() {
	out := flag.String("out", "", "new output directory")
	display := flag.Bool("display", false, "compare additive scanout observation with identical raw layers")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	script, e := os.ReadFile("/project/tools/round_core_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "round_core_receipt.go"), script, 0644))
	cores := make([]*gamecore.Core, 2)
	for i, name := range []string{"baseline", "observed"} {
		c, e := gamecore.New("/orig", filepath.Join(*out, name))
		must(e)
		defer c.Close()
		c.EnableEffects()
		c.EnableHUD()
		c.EnableShadows()
		if i == 1 || *display {
			c.EnableRounds()
		}
		if i == 1 && *display {
			c.EnableDisplay()
		}
		c.Pause(false)
		cores[i] = c
	}
	checks := 0
	seen := map[uint64]bool{}
	stages, widths := map[uint16]bool{}, map[int]bool{}
	fixtures := []string{}
	write := func(name string, b []byte) { must(os.WriteFile(filepath.Join(*out, name), b, 0644)) }
	writeJSON := func(name string, v any) {
		b, e := json.MarshalIndent(v, "", "  ")
		must(e)
		write(name, append(b, '\n'))
	}
	compare := func() {
		a, b := cores[0].Status(), cores[1].Status()
		if !reflect.DeepEqual(a, b) {
			panic("original state changed")
		}
		x, y := cores[0].Presentation(), cores[1].Presentation()
		if x.Serial != y.Serial || x.Steps != y.Steps || x.Counter != y.Counter || x.Actors != y.Actors || x.CameraX != y.CameraX || x.Scene != y.Scene || x.Palette != y.Palette || x.BackgroundSHA256 != y.BackgroundSHA256 || !bytes.Equal(x.Pixels, y.Pixels) {
			panic("original presentation changed")
		}
		_, _, ar := cores[0].RGB()
		_, _, br := cores[1].RGB()
		if !bytes.Equal(ar, br) {
			panic("live original changed")
		}
		if *display && y.Serial > 0 {
			if !y.Scanout.Matches(y.Pixels, y.VRAMTail) || x.Scanout != nil || !reflect.DeepEqual(x.Layers, y.Layers) || !reflect.DeepEqual(x.HUD, y.HUD) || !reflect.DeepEqual(x.Shadows, y.Shadows) || !reflect.DeepEqual(x.RoundMessage, y.RoundMessage) || x.RetainedBackgroundRows != y.RetainedBackgroundRows {
				panic("display observer changed source layers or invalid visible view")
			}
		}
		checks++
		if y.RetainedBackgroundRows > 0 {
			if !y.LayersComplete || y.RoundMessage == nil || !y.RoundMessage.Complete || y.HUD == nil || y.Shadows == nil {
				panic(fmt.Sprintf("incomplete round frame serial=%d layers=%t reason=%s round=%t hud=%t shadows=%t", y.Serial, y.LayersComplete, y.LayerError, y.RoundMessage != nil, y.HUD != nil, y.Shadows != nil))
			}
			if seen[y.Serial] {
				return
			}
			seen[y.Serial] = true
			stem := fmt.Sprintf("round-frame-%03d", len(fixtures))
			fixtures = append(fixtures, stem)
			stages[y.RoundMessage.Stage], widths[y.RoundMessage.Width] = true, true
			writeJSON(stem+".frame.json", y)
			writeJSON(stem+".palette.json", y.Palette)
			write(stem+".idx", y.Pixels)
			if *display {
				write(stem+".display.idx", y.Scanout.Indices)
				write(stem+".vram-tail", y.VRAMTail)
			}
			for suffix, data := range map[string][]byte{".round.source": y.RoundMessage.Source, ".round-under.idx": y.RoundMessage.Underlay.Indices, ".round-under.mask": y.RoundMessage.Underlay.Coverage, ".hud.bitmap": y.HUD.Bitmap, ".hud-under.idx": y.HUD.Underlay.Indices, ".hud-under.mask": y.HUD.Underlay.Coverage, ".shadow-under.idx": y.Shadows.Underlay.Indices, ".shadow-under.mask": y.Shadows.Underlay.Coverage} {
				write(stem+suffix, data)
			}
			for n, layer := range y.Layers {
				write(fmt.Sprintf("%s.layer-%02d.idx", stem, n), layer.Indices)
				write(fmt.Sprintf("%s.layer-%02d.mask", stem, n), layer.Coverage)
			}
		}
	}
	step := func(n uint64) {
		for _, c := range cores {
			must(c.Step(n))
		}
		compare()
	}
	step(40_000_000)
	for _, c := range cores {
		must(c.Mouse(125, 181, true))
	}
	step(1_000_000)
	for _, c := range cores {
		must(c.Mouse(125, 181, false))
	}
	step(24_000_000)
	for _, c := range cores {
		must(c.MenuKey("Return"))
	}
	step(20_000_000)
	for i := 0; i < 4; i++ {
		for _, c := range cores {
			must(c.MenuKey("Right"))
		}
		step(1_000_000)
	}
	for _, c := range cores {
		must(c.MenuKey("Return"))
	}
	for i := 0; i < 1500; i++ {
		step(50_000)
	}
	final := cores[1].Presentation()
	if len(fixtures) != 66 || len(stages) != 4 || len(widths) != 12 || final.RoundMessage != nil || final.RetainedBackgroundRows != 0 || !final.LayersComplete {
		panic(fmt.Sprintf("incomplete coverage fixtures=%d stages=%d widths=%d final=%+v", len(fixtures), len(stages), len(widths), cores[1].Status()))
	}
	writeJSON("receipt.json", map[string]any{"kind": "normal first-round public Core observation compatibility and paired fixtures", "display_observation": *display, "script_sha256": digest(script), "checks": checks, "round_fixtures": fixtures, "stages": len(stages), "widths": len(widths), "final_core": cores[1].Status(), "round_cleared_after_opening": true, "limits": "first round only; no native GUI or other round index proof"})
	fmt.Println("checks", checks, "round fixtures", len(fixtures), "cleared", final.RoundMessage == nil)
}
