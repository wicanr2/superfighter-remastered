// Disposable 048 result lifecycle probe through the current public Core. No state writes beyond normal input.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
	"runtime"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
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

func main() {
	out := flag.String("out", "", "new output directory")
	shadows := flag.Bool("shadows", false, "also verify read-only shadow snapshot lifecycle")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	script, e := os.ReadFile("/project/tools/result_core_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "result_core_receipt.go"), script, 0644))
	c, e := gamecore.New("/orig", filepath.Join(*out, "dos"))
	must(e)
	defer c.Close()
	c.EnableEffects()
	c.EnableHUD()
	if *shadows {
		c.EnableShadows()
	}
	c.Pause(false)
	var events []map[string]any
	checkpoint := func(name string) {
		w, h, rgb := c.RGB()
		frame := c.Presentation()
		if *shadows && c.Status().Battle && (frame.Shadows == nil || !frame.Shadows.Complete) {
			panic("missing complete battle shadow snapshot")
		}
		if !c.Status().Battle && frame.Shadows != nil {
			panic("stale shadow snapshot after leaving battle")
		}
		cached := make([]byte, len(frame.Pixels)*3)
		for i, v := range frame.Pixels {
			copy(cached[i*3:i*3+3], frame.Palette[v][:])
		}
		img := image.NewRGBA(image.Rect(0, 0, w, h))
		for i := 0; i < w*h; i++ {
			copy(img.Pix[i*4:i*4+3], rgb[i*3:i*3+3])
			img.Pix[i*4+3] = 255
		}
		f, e := os.Create(filepath.Join(*out, name+".png"))
		must(e)
		must(png.Encode(f, img))
		must(f.Close())
		must(os.WriteFile(filepath.Join(*out, name+".rgb"), rgb, 0644))
        display, palette, de := c.LiveDisplay()
        must(de)
        if display == nil || !display.Valid() { panic("missing current live display") }
        must(os.WriteFile(filepath.Join(*out,name+".idx"),display.Indices,0644))
        writeJSON(filepath.Join(*out,name+".palette.json"),palette)
        writeJSON(filepath.Join(*out,name+".display.json"),display)

		event := map[string]any{"name": name, "core": c.Status(), "presentation": frame, "width": w, "height": h, "live_rgb_sha256": digest(rgb), "cached_frame_rgb_sha256": digest(cached), "cached_frame_pixels": len(frame.Pixels)}
		if frame.Steps > 0 {
			event["snapshot_age_steps"] = c.Status().Steps - frame.Steps
		}
		events = append(events, event)
		writeJSON(filepath.Join(*out, name+".json"), event)
		fmt.Println(name, c.Status(), "frame", frame.Serial, "complete shadows", frame.Shadows != nil && frame.Shadows.Complete)
	}
	step := func(n uint64) {
		must(c.Step(n))
		if c.Status().Steps > 3_000_000_000 {
			panic("bounded total instruction budget exceeded")
		}
	}
	step(40_000_000)
	must(c.Mouse(125, 181, true))
	step(1_000_000)
	must(c.Mouse(125, 181, false))
	step(24_000_000)
	must(c.MenuKey("Return"))
	step(20_000_000)
	for i := 0; i < 4; i++ {
		must(c.MenuKey("Right"))
		step(1_000_000)
	}
	must(c.MenuKey("Return"))
	step(75_000_000)
	if c.Status().Fighters != [2]int{0, 4} {
		panic("not normal Jaan/Frank battle")
	}
	checkpoint("normal-battle")
	input := func(keys []uint8) {
		if len(keys) == 0 {
			must(c.SetInput(nil))
		} else {
			must(c.SetInput([]gamecore.Source{{Player: 0, Name: "keyboard", Keys: keys}}))
		}
	}
	runFrames := func(count uint64, approach bool) {
		end := c.Status().Frames + count
		budgetEnd := c.Status().Steps + 150_000_000
		for c.Status().Battle && c.Status().Frames < end && c.Status().Steps < budgetEnd {
			step(250_000)
			f := c.Presentation()
			if f.HUD != nil && (f.HUD.State.Health[1] == 0 || f.HUD.State.RoundState != 0) {
				return
			}
			d := f.Actors[1].X - f.Actors[0].X
			if d < 0 {
				d = -d
			}
			if approach && d <= 44 {
				return
			}
		}
	}
	seenKO := map[uint16]bool{}
	for cycle := 0; cycle < 24 && c.Status().Battle; cycle++ {
		f := c.Presentation()
		if f.HUD == nil {
			panic("missing normal HUD")
		}
		s := f.HUD.State
		if s.Health[1] == 0 || s.RoundState != 0 {
			input(nil)
			if !seenKO[s.Round] {
				seenKO[s.Round] = true
				checkpoint(fmt.Sprintf("knockout-%d", s.Round))
			}
			end := c.Status().Steps + 150_000_000
			for c.Status().Battle && c.Status().Steps < end {
				step(250_000)
				next := c.Presentation()
				if next.HUD != nil && next.HUD.State.Round > s.Round && next.HUD.State.RoundState == 0 && next.HUD.State.Health == [2]uint16{124, 124} {
					checkpoint("next-round")
					break
				}
			}
			continue
		}
		direction := uint8(0x20)
		if f.Actors[0].X > f.Actors[1].X {
			direction = 0x1e
		}
		input([]uint8{direction})
		runFrames(180, true)
		input([]uint8{0xf})
		runFrames(40, false)
		input(nil)
		runFrames(30, false)
		fmt.Println("cycle", cycle, "frames", c.Status().Frames, "hud", c.Presentation().HUD.State)
	}
	input(nil)
	checkpoint("after-match-inputs")
	for i := 0; i < 60; i++ {
		step(1_000_000)
	}
	checkpoint("post-match-wait")
    if c.Status().Battle || c.Status().Training.Modified { panic("not an unmodified normal result") }
    for i:=0;i<6;i++ { step(2_000_000);checkpoint(fmt.Sprintf("result-stable-%d",i)) }
    must(c.MenuKey("Return"))
    step(24_000_000)
    checkpoint("return-to-title")

	inputs := map[string]string{}
	for _, n := range []string{"SF.EXE", "SF.COM", "NOKEY.EXE", "SHIN.FIG", "BIGFIG.XBB", "LOSEFIG.XBB", "WC.XBB", "FLAG.XBB", "FLAG.FIG", "NAME.XBB"} {
		b, e := os.ReadFile(filepath.Join("/orig", n))
		must(e)
		inputs[n] = digest(b)
	}
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "current public-core normal complete match, stable result and Return; not native GUI or HD art acceptance", "go_version": runtime.Version(), "inputs": inputs, "dosgolem_manifest_sha256": digest(manifest), "script_sha256": digest(script), "events": events, "final_core": c.Status(), "state_control": "normal menus and keyboard only; no health, winner, position or RNG writes"})
}
