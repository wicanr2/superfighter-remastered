// Paired normal-input Core replay. Victory observation must not change original state/RGB.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"reflect"
	"strings"

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
	characterDir := flag.String("hd-characters", "/project/workplace/hd-characters-study-v8", "character asset directory")
	attacker := flag.Int("attacker", 0, "normal attacking player: 0 or 1")
	player0 := flag.Int("player0", 0, "normal first-player character: 0..7; second player is Frank")
	poseSamples := flag.Bool("pose-samples", false, "sample WIN-bank poses from knockout through next round")
	diagnostic := flag.Bool("diagnostic", false, "single-core source diagnostics; no paired-state acceptance")
	flag.Parse()
	if *attacker < 0 || *attacker > 1 {
		panic("attacker must be 0 or 1")
	}
	if *player0 < 0 || *player0 > 7 {
		panic("player0 must be 0..7")
	}
	loser := 1 - *attacker
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
	sourceInputs := map[string]string{}
	for _, dir := range []string{"internal", "cmd"} {
		must(filepath.WalkDir(filepath.Join("/project", dir), func(path string, entry fs.DirEntry, err error) error {
			if err != nil {
				return err
			}
			if entry.IsDir() || !strings.HasSuffix(path, ".go") || strings.HasSuffix(path, "_test.go") {
				return nil
			}
			b, e := os.ReadFile(path)
			if e != nil {
				return e
			}
			sourceInputs[strings.TrimPrefix(path, "/project/")] = digest(b)
			return nil
		}))
	}
	for _, name := range []string{"go.mod", "go.sum", "go.work", "workplace/dosgolem-patched-manifest.json"} {
		b, e := os.ReadFile(filepath.Join("/project", name))
		must(e)
		sourceInputs[name] = digest(b)
	}
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
	characters, e := hd.LoadCharacters(*characterDir, "/orig")
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
	var poseCaptures []string
	var poseTrace []map[string]any
	seenPoses := map[string]bool{}
	var lastPoseSerial uint64
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
		if *poseSamples && f.Serial != 0 && f.Serial != lastPoseSerial {
			lastPoseSerial = f.Serial
			var sprites []*renderdata.Sprite
			for _, layer := range f.Layers {
				if s := layer.Sprite; s != nil && s.SourceBank == "victory" {
					sprites = append(sprites, s)
				}
			}
			if len(sprites) > 0 {
				selected, why := characters.Select(f.Layers, f.Palette)
				poseTrace = append(poseTrace, map[string]any{"steps": b.Steps, "frame_steps": f.Steps, "serial": f.Serial, "counter": f.Counter, "complete": f.LayersComplete, "sprites": sprites, "characters_selected": selected != nil, "reason": why, "victory_message": f.Victory != nil})
				for _, s := range sprites {
					key := fmt.Sprintf("%d:%d:%d:%s", s.Player, s.Character, s.Slot, s.SourceSHA256)
					if f.LayersComplete && !seenPoses[key] {
						stem := fmt.Sprintf("victory-pose-%02d", len(poseCaptures))
						save(stem, f)
						poseCaptures = append(poseCaptures, stem)
						seenPoses[key] = true
					}
				}
			}
		}
		if f.Victory != nil && !captured {
			save("victory-frame", f)
			writeJSON("victory-source-diagnostic.json", map[string]any{"actors": f.Actors, "layers": f.Layers, "state": f.Victory.State, "paired": !*diagnostic})
			if f.HUD == nil || f.Shadows == nil {
				panic("victory lacks complete HUD/shadows")
			}
			if selected, why := victories.Select(f.Victory, f.Layers, f.Palette, f.Counter); selected == nil {
				writeJSON("victory-selection-failure.json", map[string]any{"reason": why, "state": f.Victory.State})
				if !*diagnostic {
					panic(why)
				}
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
			expectedWins := [2]uint16{}
			expectedWins[*attacker] = 1
			if f.HUD.State.DisplayWins != expectedWins {
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
	for i := 0; i < *player0; i++ {
		for _, c := range cores {
			must(c.MenuKey("Right"))
		}
		step(1_000_000)
	}
	for _, c := range cores {
		must(c.MenuKey("Return"))
	}
	step(20_000_000)
	secondDirection, secondSteps := "Right", 4-*player0
	if secondSteps < 0 {
		secondDirection, secondSteps = "Left", -secondSteps
	}
	for i := 0; i < secondSteps; i++ {
		for _, c := range cores {
			must(c.MenuKey(secondDirection))
		}
		step(1_000_000)
	}
	for _, c := range cores {
		must(c.MenuKey("Return"))
	}
	step(75_000_000)
	if selected := observed.Status().Fighters; selected[0] != *player0 || selected[1] != 4 {
		panic(fmt.Sprintf("normal selection mismatch: %v", selected))
	}
	input := func(keys ...uint8) {
		for _, c := range cores {
			var source []gamecore.Source
			if len(keys) > 0 {
				source = []gamecore.Source{{Player: *attacker, Name: "keyboard", Keys: keys}}
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
			if f.HUD != nil && (f.HUD.State.Health[loser] == 0 || f.HUD.State.RoundState != 0) {
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
	for cycle := 0; cycle < 24 && !captured; cycle++ {
		f := observed.Presentation()
		if f.HUD == nil {
			panic("missing normal HUD")
		}
		if f.HUD.State.Health[loser] == 0 || f.HUD.State.RoundState != 0 {
			input()
			limit := observed.Status().Steps + 150_000_000
			for !captured && observed.Status().Steps < limit {
				budget := uint64(250_000)
				if *poseSamples {
					budget = 10_000
				}
				step(budget)
			}
			continue
		}
		dir := uint8(0x20)
		punch := uint8(0xf)
		if f.Actors[0].X > f.Actors[1].X {
			dir = 0x1e
		}
		if *attacker == 1 {
			dir, punch = 0x4b, 0x1c
			if f.Actors[1].X < f.Actors[0].X {
				dir = 0x4d
			}
		}
		input(dir)
		frames(180, true)
		input(punch)
		frames(40, false)
		input()
		frames(30, false)
		fmt.Println("cycle", cycle, "steps", observed.Status().Steps, "health", observed.Presentation().HUD.State.Health)
	}
	if !captured {
		panic("no complete victory snapshot")
	}
	input()
	limit := observed.Status().Steps + 150_000_000
	for !cleared && observed.Status().Steps < limit {
		budget := uint64(250_000)
		if *poseSamples {
			budget = 10_000
		}
		step(budget)
	}
	if !cleared {
		panic("victory metadata did not clear on normal next round")
	}
	for name, want := range sourceInputs {
		b, e := os.ReadFile(filepath.Join("/project", name))
		must(e)
		if digest(b) != want {
			panic("source changed during replay: " + name)
		}
	}
	writeJSON("receipt.json", map[string]any{"kind": "normal Core victory observation; not native GUI", "script_sha256": digest(script), "source_inputs": sourceInputs, "player0": *player0, "attacker": *attacker, "pose_captures": poseCaptures, "pose_trace": poseTrace, "checks": checks, "captures": captures, "victory_cleared": cleared, "original_state_and_rgb_unchanged": !*diagnostic, "paired": !*diagnostic, "final_core": observed.Status(), "limits": "requested normal selection first victory and next round; pose trace is sampled at 10000 instructions after knockout, not a complete native animation acceptance"})
	fmt.Println("checks", checks, "captured", captured, "cleared", cleared)
}
