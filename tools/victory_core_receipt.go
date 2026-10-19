// Paired normal-input Core replay. Victory observation must not change original state/RGB.
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
	"github.com/wicanr2/superfighter-remastered/internal/hd"
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
	diagnostic := flag.Bool("diagnostic", false, "single-core source diagnostics; no paired-state acceptance")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	write := func(n string, b []byte) { must(os.WriteFile(filepath.Join(*out, n), b, 0644)) }
	writeJSON := func(n string, v any) { b, e := json.MarshalIndent(v, "", "  "); must(e); write(n, append(b, '\n')) }
	script, e := os.ReadFile("/project/tools/victory_core_receipt.go")
	must(e)
	write("victory_core_receipt.go", script)
	cores := make([]*gamecore.Core, 2)
	for i, name := range []string{"baseline", "observed"} {
		c, e := gamecore.New("/orig", filepath.Join(*out, name))
		must(e)
		defer c.Close()
		c.EnableEffects()
		c.EnableHUD()
		c.EnableShadows()
		c.EnableRounds()
		c.EnableDisplay()
		if i == 1 {
			c.EnableVictory()
		}
		c.Pause(false)
		cores[i] = c
	}
	observed := cores[1]
	if *diagnostic {
		cores = cores[1:]
	}
	assets, e := hd.Load("/project/workplace/hd-rooftop-study")
	must(e)
	characters, e := hd.LoadCharacters("/project/workplace/hd-characters-study-v7", "/orig")
	must(e)
	hud, e := hd.LoadHUD("/orig")
	must(e)
	shadows, e := hd.LoadShadows("/orig")
	must(e)
	victories, e := hd.LoadVictories("/orig")
	must(e)
	checks := 0
	captured := false
	cleared := false
	var victoryStep uint64
	var captures []string
	save := func(stem string, f gamecore.Presentation) {
		if !f.LayersComplete || !renderdata.Match(f.Layers, f.Pixels) || !f.Scanout.Matches(f.Pixels, f.VRAMTail) {
			panic("incomplete frozen source")
		}
		writeJSON(stem+".frame.json", f)
		writeJSON(stem+".palette.json", f.Palette)
		write(stem+".idx", f.Pixels)
		write(stem+".display.idx", f.Scanout.Indices)
		write(stem+".vram-tail", f.VRAMTail)
		for n, l := range f.Layers {
			write(fmt.Sprintf("%s.layer-%02d.idx", stem, n), l.Indices)
			write(fmt.Sprintf("%s.layer-%02d.mask", stem, n), l.Coverage)
		}
		if f.HUD != nil {
			for suffix, b := range map[string][]byte{".hud.bitmap": f.HUD.Bitmap, ".hud-under.idx": f.HUD.Underlay.Indices, ".hud-under.mask": f.HUD.Underlay.Coverage} {
				write(stem+suffix, b)
			}
		}
		if f.Shadows != nil {
			write(stem+".shadow-under.idx", f.Shadows.Underlay.Indices)
			write(stem+".shadow-under.mask", f.Shadows.Underlay.Coverage)
		}
		if f.RoundMessage != nil {
			write(stem+".round.source", f.RoundMessage.Source)
			write(stem+".round-under.idx", f.RoundMessage.Underlay.Indices)
			write(stem+".round-under.mask", f.RoundMessage.Underlay.Coverage)
		}
		if f.Victory != nil {
			write(stem+".victory-under.idx", f.Victory.Underlay.Indices)
			write(stem+".victory-under.mask", f.Victory.Underlay.Coverage)
			for i, d := range f.Victory.Draws {
				write(fmt.Sprintf("%s.victory-%02d.source", stem, i), d.Source)
			}
		}
		captures = append(captures, stem)
	}
	compare := func() {
		a, b := cores[0].Status(), observed.Status()
		if !reflect.DeepEqual(a, b) {
			panic("original state changed")
		}
		aw, ah, ar := cores[0].RGB()
		bw, bh, br := observed.RGB()
		if aw != bw || ah != bh || !bytes.Equal(ar, br) {
			panic("original live RGB changed")
		}
		checks++
		f := observed.Presentation()
		if f.Victory != nil && !captured {
			save("victory-frame", f)
			writeJSON("victory-source-diagnostic.json", map[string]any{"actors": f.Actors, "layers": f.Layers, "state": f.Victory.State, "paired": !*diagnostic})
			if f.HUD == nil || f.Shadows == nil {
				panic("victory lacks complete HUD/shadows")
			}
			if selected, why := victories.Select(f.Victory, f.Layers, f.Palette, f.Counter); selected == nil {
				panic(why)
			}
			if selected, why := characters.Select(f.Layers, f.Palette); selected == nil {
				writeJSON("character-selection-failure.json", map[string]any{"reason": why, "actors": f.Actors, "layers": f.Layers})
				if !*diagnostic {
					panic(why)
				}
			}
			if selected, why := hud.Select(f.HUD, f.Pixels, f.Palette, f.Layers); selected == nil {
				panic(why)
			}
			if selected, why := shadows.Select(f.Shadows, f.Layers, f.Palette, f.Counter, f.CameraX); selected == nil {
				panic(why)
			}
			if !assets.DisplayMatch(f.Scanout, f.Pixels, f.VRAMTail, hd.Frame{Scene: f.Scene, CameraX: f.CameraX, BackgroundSHA256: f.BackgroundSHA256, Palette: f.Palette}) {
				panic("victory display background mismatch")
			}
			_, _, live := observed.RGB()
			cached := make([]byte, len(f.Pixels)*3)
			for i, v := range f.Pixels {
				copy(cached[i*3:i*3+3], f.Palette[v][:])
			}
			if !bytes.Equal(live, cached) {
				panic("victory omitted from selected original")
			}
			captured = true
			victoryStep = b.Steps
			fmt.Println("victory", f.Victory.State, "steps", b.Steps, "serial", f.Serial)
		}
		if captured && b.Steps > victoryStep && f.Victory == nil && f.HUD != nil && f.HUD.State.Round > 0 && f.HUD.State.RoundState == 0 && f.HUD.State.Health == [2]uint16{124, 124} {
			if f.HUD.State.DisplayWins != [2]uint16{1, 0} {
				panic("next-round displayed wins lost")
			}
			save("after-victory", f)
			cleared = true
		}
	}
	step := func(n uint64) {
		for _, c := range cores {
			must(c.Step(n))
		}
		compare()
		if observed.Status().Steps > 1_200_000_000 {
			panic("bounded instruction budget exceeded")
		}
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
	step(75_000_000)
	input := func(keys ...uint8) {
		for _, c := range cores {
			var source []gamecore.Source
			if len(keys) > 0 {
				source = []gamecore.Source{{Player: 0, Name: "keyboard", Keys: keys}}
			}
			must(c.SetInput(source))
		}
	}
	frames := func(count uint64, approach bool) {
		end := observed.Status().Frames + count
		limit := observed.Status().Steps + 150_000_000
		for observed.Status().Frames < end && observed.Status().Steps < limit && !captured {
			step(250_000)
			f := observed.Presentation()
			if f.HUD != nil && (f.HUD.State.Health[1] == 0 || f.HUD.State.RoundState != 0) {
				return
			}
			distance := f.Actors[1].X - f.Actors[0].X
			if distance < 0 {
				distance = -distance
			}
			if approach && distance <= 44 {
				return
			}
		}
	}
	for cycle := 0; cycle < 16 && !captured; cycle++ {
		f := observed.Presentation()
		if f.HUD == nil {
			panic("missing normal HUD")
		}
		if f.HUD.State.Health[1] == 0 || f.HUD.State.RoundState != 0 {
			input()
			limit := observed.Status().Steps + 150_000_000
			for !captured && observed.Status().Steps < limit {
				step(250_000)
			}
			continue
		}
		dir := uint8(0x20)
		if f.Actors[0].X > f.Actors[1].X {
			dir = 0x1e
		}
		input(dir)
		frames(180, true)
		input(0xf)
		frames(40, false)
		input()
		frames(30, false)
		fmt.Println("cycle", cycle, "steps", observed.Status().Steps)
	}
	if !captured {
		panic("no complete victory snapshot")
	}
	input()
	limit := observed.Status().Steps + 150_000_000
	for !cleared && observed.Status().Steps < limit {
		step(250_000)
	}
	if !cleared {
		panic("victory metadata did not clear on normal next round")
	}
	writeJSON("receipt.json", map[string]any{"kind": "paired normal Core victory observation; not native GUI", "script_sha256": digest(script), "checks": checks, "captures": captures, "victory_cleared": cleared, "original_state_and_rgb_unchanged": !*diagnostic, "paired": !*diagnostic, "final_core": observed.Status(), "limits": "first Jaan victory and next normal round; special glyphs have separate static tests"})
	fmt.Println("checks", checks, "captured", captured, "cleared", cleared)
}
