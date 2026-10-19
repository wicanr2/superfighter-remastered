// Compare normal public-core input with effect observation off/on. No game-state writes.
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
	out := flag.String("out", "", "new output directory")
	hud := flag.Bool("hud", false, "also compare read-only HUD observation")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	base, e := gamecore.New("/orig", filepath.Join(*out, "baseline"))
	must(e)
	defer base.Close()
	observed, e := gamecore.New("/orig", filepath.Join(*out, "observed"))
	must(e)
	defer observed.Close()
	observed.EnableEffects()
	if *hud {
		observed.EnableHUD()
	}
	cores := []*gamecore.Core{base, observed}
	checks := 0
	hudSnapshots := 0
	compare := func() {
		a, b := base.Status(), observed.Status()
		if !reflect.DeepEqual(a, b) {
			panic(fmt.Sprintf("input state changed: %+v %+v", a, b))
		}
		x, y := base.Presentation(), observed.Presentation()
		if x.Serial != y.Serial || x.Steps != y.Steps || x.Counter != y.Counter || x.Actors != y.Actors || x.CameraX != y.CameraX || x.Scene != y.Scene || x.Palette != y.Palette || x.BackgroundSHA256 != y.BackgroundSHA256 || !bytes.Equal(x.Pixels, y.Pixels) {
			panic("complete original presentation changed")
		}
		checks++
		if y.HUD != nil && y.HUD.Complete {
			hudSnapshots++
		}
	}
	step := func(n uint64) {
		for _, c := range cores {
			must(c.Step(n))
		}
		compare()
	}
	for _, c := range cores {
		c.Pause(false)
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
	if !base.Status().Battle || base.Status().Fighters != [2]int{0, 4} {
		panic("not normal versus battle")
	}
	var phases []map[string]any
	runFrames := func(name string, n uint64) {
		end := base.Status().Frames + n
		seen := map[int]bool{}
		for base.Status().Frames < end {
			step(250_000)
			seen[base.Status().Paths[0]] = true
		}
		phases = append(phases, map[string]any{"name": name, "frames": n, "p1_seen_paths": seen, "last": base.Status()})
		fmt.Println(name, base.Status().Paths)
	}
	for _, c := range cores {
		must(c.Quick(0, 1))
	}
	runFrames("fresh-p1-R1", 65)
	for _, keys := range [][]uint8{{0x50}, {0x4f}, {0x4b, 0x1c}} {
		for _, c := range cores {
			must(c.SetInput([]gamecore.Source{{Player: 1, Name: "keyboard", Keys: keys}}))
		}
		runFrames(fmt.Sprintf("p2-keys-%x", keys), 2)
	}
	for _, c := range cores {
		must(c.SetInput(nil))
	}
	runFrames("p2-release", 65)
	for _, c := range cores {
		must(c.Quick(0, 1))
	}
	runFrames("p1-R1-after-p2", 40)
	script, e := os.ReadFile("/project/tools/effect_core_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "effect_core_receipt.go"), script, 0644))
	if *hud && hudSnapshots == 0 {
		panic("HUD observation did not capture any complete snapshot")
	}
	receipt := map[string]any{"kind": "normal public core input compatibility with effect/HUD observation off/on", "hud_enabled": *hud, "complete_hud_snapshots": hudSnapshots, "compared_step_boundaries": checks, "phases": phases, "result": "all observed input state, complete original pixels, palette, actors, counters and execution steps identical", "script_sha256": fmt.Sprintf("%x", sha256.Sum256(script)), "limits": "controlled two-player input observation; not GUI, gamepad hardware or cross-execution RND parity"}
	b, e := json.MarshalIndent(receipt, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "receipt.json"), append(b, '\n'), 0644))
	fmt.Println("compared", checks)
}
