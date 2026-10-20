// Normal paired Core replay with effect/HUD/round/victory observers off/on; display common.
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
func main() {
	out := flag.String("out", "", "new private output directory")
	sequence := flag.String("sequence", "", "normal keyboard phases")
	flag.Parse()
	if *out == "" || *sequence == "" {
		panic("out and sequence required")
	}
	must(os.Mkdir(*out, 0755))
	write := func(name string, b []byte) { must(os.WriteFile(filepath.Join(*out, name), b, 0644)) }
	script, e := os.ReadFile("tools/primary_extra_core_receipt.go")
	must(e)
	write("primary_extra_core_receipt.go", script)
	raw, e := os.ReadFile(*sequence)
	must(e)
	write("sequence.json", raw)
	var experiment struct {
		Character int
		Phases    []struct {
			Name   string
			Keys   []uint8
			Frames uint64
		}
	}
	must(json.Unmarshal(raw, &experiment))
	if experiment.Character != 5 || len(experiment.Phases) != 6 {
		panic("unexpected source sequence")
	}
	var cores [2]*gamecore.Core
	for i := range cores {
		c, e := gamecore.New("/orig", filepath.Join(*out, fmt.Sprint(i)))
		must(e)
		defer c.Close()
		c.EnableDisplay()
		if i == 1 {
			c.EnableEffects()
			c.EnableHUD()
			c.EnableShadows()
			c.EnableRounds()
			c.EnableVictory()
		}
		c.Pause(false)
		cores[i] = c
	}
	checks, extras := 0, map[uint64]bool{}
	step := func(n uint64) {
		for _, c := range cores {
			must(c.Step(n))
		}
		a, b := cores[0].Presentation(), cores[1].Presentation()
		if !reflect.DeepEqual(cores[0].Status(), cores[1].Status()) || a.Serial != b.Serial || a.Steps != b.Steps || a.Counter != b.Counter || a.Scene != b.Scene || a.CameraX != b.CameraX || a.Actors != b.Actors || a.Palette != b.Palette || a.BackgroundSHA256 != b.BackgroundSHA256 || !bytes.Equal(a.Pixels, b.Pixels) || !bytes.Equal(a.VRAMTail, b.VRAMTail) {
			panic("original state or pixels changed by observers")
		}
		for _, l := range b.Layers {
			if s := l.Sprite; s != nil && s.Effect && s.Character == 5 && s.Slot == 35 && s.PaletteBase == 0xc0 {
				extras[b.Serial] = true
			}
		}
		checks++
		if cores[0].Status().Steps > 800_000_000 {
			panic("instruction budget")
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
	for i := 0; i < 5; i++ {
		for _, c := range cores {
			must(c.MenuKey("Right"))
		}
		step(1_000_000)
	}
	for _, c := range cores {
		must(c.MenuKey("Return"))
	}
	step(20_000_000)
	for _, c := range cores {
		must(c.MenuKey("Left"))
	}
	step(1_000_000)
	for _, c := range cores {
		must(c.MenuKey("Return"))
	}
	step(75_000_000)
	for {
		f := cores[1].Presentation()
		if f.LayersComplete && f.HUD != nil && f.HUD.State.RoundState == 0 && f.RoundMessage == nil && f.Scanout != nil {
			break
		}
		step(250_000)
	}
	if cores[0].Status().Fighters != [2]int{5, 4} {
		panic("selection mismatch")
	}
	for _, p := range experiment.Phases {
		if p.Frames == 0 || p.Frames > 120 {
			panic("unbounded input")
		}
		var input []gamecore.Source
		if len(p.Keys) > 0 {
			input = []gamecore.Source{{Player: 0, Name: "keyboard", Keys: p.Keys}}
		}
		for _, c := range cores {
			must(c.SetInput(input))
		}
		end := cores[0].Status().Frames + p.Frames
		for cores[0].Status().Frames < end {
			step(250_000)
		}
		fmt.Println(p.Name, cores[0].Status().Frames)
	}
	if len(extras) != 4 {
		panic(fmt.Sprintf("expected four primary extras, got %d", len(extras)))
	}
	inputs := map[string]string{}
	for _, name := range []string{"internal/gamecore/layers.go", "workplace/dosgolem-patched-manifest.json", "workplace/orig/SF.EXE"} {
		b, e := os.ReadFile(name)
		must(e)
		inputs[name] = fmt.Sprintf("%x", sha256.Sum256(b))
	}
	receipt := map[string]any{"kind": "normal paired Core presentation observers off/on", "compared_step_boundaries": checks, "extra_serials": extras, "script_sha256": fmt.Sprintf("%x", sha256.Sum256(script)), "sequence_sha256": fmt.Sprintf("%x", sha256.Sum256(raw)), "inputs": inputs, "status": cores[0].Status(), "result": "all public original status, pixels, VRAM tail, palette, actors, counters and execution steps identical", "limits": "normal declared sequence; no forced state, wins, training or shortcut; RNG not reseeded, no random mechanism parity claim; no GPU or hardware acceptance"}
	b, e := json.MarshalIndent(receipt, "", "  ")
	must(e)
	write("receipt.json", append(b, '\n'))
	fmt.Println("compared", checks, "extra frames", len(extras))
}
