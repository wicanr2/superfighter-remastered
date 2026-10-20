// Disposable normal keyboard sequence diagnostic; no shortcut enablement or state injection.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"sort"

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

type phase struct {
	Name   string  `json:"name"`
	Keys   []uint8 `json:"keys"`
	Frames uint64  `json:"frames"`
}

func main() {
	out := flag.String("out", "", "new output directory")
	characterOnly := flag.Int("character", -1, "one character 0..10, or -1 for all eleven")
	characterDir := flag.String("hd-characters", "/project/assets/hd/characters", "character pack")
	baselineDir := flag.String("baseline", "", "optional old pack for same-frame selection comparison")
	sequencePath := flag.String("sequence", "", "explicit experiment sequence JSON")
	flag.Parse()
	if *sequencePath == "" {
		panic("sequence required")
	}
	sequence, e := os.ReadFile(*sequencePath)
	must(e)
	var experiment struct {
		Name      string  `json:"name"`
		Character int     `json:"character"`
		Phases    []phase `json:"phases"`
	}
	must(json.Unmarshal(sequence, &experiment))
	if experiment.Name == "" || experiment.Character < 0 || experiment.Character > 10 || len(experiment.Phases) == 0 || len(experiment.Phases) > 32 {
		panic("bad sequence")
	}
	var total uint64
	for _, p := range experiment.Phases {
		if p.Name == "" || p.Frames == 0 || p.Frames > 120 {
			panic("unbounded phase")
		}
		total += p.Frames
	}
	if total > 600 {
		panic("sequence frame budget")
	}
	*characterOnly = experiment.Character
	if *characterOnly < -1 || *characterOnly > 10 {
		panic("invalid character")
	}
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	must(os.WriteFile(filepath.Join(*out, "sequence.json"), sequence, 0644))
	writeJSON := func(name string, v any) {
		b, e := json.MarshalIndent(v, "", "  ")
		must(e)
		must(os.WriteFile(name, append(b, '\n'), 0644))
	}
	script, e := os.ReadFile("/project/tools/special_effects_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "special_effects_receipt.go"), script, 0644))
	manifest, e := os.ReadFile(filepath.Join(*characterDir, "manifest.json"))
	must(e)
	art, e := hd.LoadCharacters(*characterDir, "/orig")
	must(e)
	var baseline *hd.Characters
	var baselineHash string
	if *baselineDir != "" {
		baseline, e = hd.LoadCharacters(*baselineDir, "/orig")
		must(e)
		b, e := os.ReadFile(filepath.Join(*baselineDir, "manifest.json"))
		must(e)
		baselineHash = digest(b)
	}
	keys := map[string]bool{}
	key := func(s *renderdata.Sprite) string {
		bank := 0
		if s.Effect {
			bank = 1
		}
		src := s.SourceBank
		if src == "" {
			src = "normal"
		}
		return fmt.Sprintf("%d:%s:%d:%d", s.Character, src, bank, s.Slot)
	}
	for _, p := range art.Manifest.Poses {
		src := p.SourceBank
		if src == "" {
			src = "normal"
		}
		keys[fmt.Sprintf("%d:%s:%d:%d", p.Character, src, p.PaletteBank, p.Slot)] = true
	}
	phases := experiment.Phases

	var cases []map[string]any
	for character := 0; character < 11; character++ {
		if *characterOnly != -1 && character != *characterOnly {
			continue
		}
		dir := filepath.Join(*out, fmt.Sprintf("character-%02d", character))
		must(os.Mkdir(dir, 0755))
		c, e := gamecore.New("/orig", filepath.Join(dir, "user-data"))
		must(e)
		c.EnableEffects()
		c.EnableHUD()
		c.EnableShadows()
		c.EnableRounds()
		c.EnableDisplay()
		c.EnableVictory()
		c.Pause(false)
		step := func(n uint64) {
			must(c.Step(n))
			if c.Status().Steps > 1_200_000_000 {
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
		direction, count := "Right", 4-character
		if count < 0 {
			direction, count = "Left", -count
		}
		for i := 0; i < count; i++ {
			must(c.MenuKey(direction))
			step(1_000_000)
		}
		must(c.MenuKey("Return"))
		step(75_000_000)
		if c.Status().Fighters != [2]int{character, 4} {
			panic("normal selection mismatch")
		}
		for {
			f := c.Presentation()
			if f.LayersComplete && f.HUD != nil && f.HUD.State.RoundState == 0 && f.RoundMessage == nil && f.Scanout != nil {
				break
			}
			step(250_000)
		}
		var trace []map[string]any
		var samples []map[string]any
		reasons := map[string]int{}
		observed := map[string]bool{}
		missing := map[string]bool{}
		saved := map[string]bool{}
		var last uint64
		save := func(f gamecore.Presentation, reason string) {
			stem := fmt.Sprintf("sample-%02d", len(samples))
			writeJSON(filepath.Join(dir, stem+".frame.json"), f)
			writeJSON(filepath.Join(dir, stem+".palette.json"), f.Palette)
			must(os.WriteFile(filepath.Join(dir, stem+".idx"), f.Pixels, 0644))
			must(os.WriteFile(filepath.Join(dir, stem+".vram-tail"), f.VRAMTail, 0644))
			for i, l := range f.Layers {
				must(os.WriteFile(filepath.Join(dir, fmt.Sprintf("%s.layer-%02d.idx", stem, i)), l.Indices, 0644))
				must(os.WriteFile(filepath.Join(dir, fmt.Sprintf("%s.layer-%02d.mask", stem, i)), l.Coverage, 0644))
			}
			samples = append(samples, map[string]any{"stem": stem, "reason": reason, "serial": f.Serial, "steps": f.Steps})
		}
		for _, p := range phases {
			var input []gamecore.Source
			if len(p.Keys) > 0 {
				input = []gamecore.Source{{Player: 0, Name: "keyboard", Keys: p.Keys}}
			}
			must(c.SetInput(input))
			end := c.Status().Frames + p.Frames
			for c.Status().Frames < end {
				step(250_000)
				f := c.Presentation()
				if !c.Status().Battle || c.Status().Training.Modified {
					panic("normal versus path left or modified")
				}
				if f.Serial == 0 || f.Serial == last {
					continue
				}
				last = f.Serial
				if !f.LayersComplete || !renderdata.Match(f.Layers, f.Pixels) || f.Scanout == nil || !f.Scanout.Matches(f.Pixels, f.VRAMTail) {
					save(f, "incomplete original snapshot")
					writeJSON(filepath.Join(*out, "failure.json"), map[string]any{"phase": p.Name, "core": c.Status(), "frame_serial": f.Serial, "frame_steps": f.Steps, "layers_complete": f.LayersComplete, "layers_match": renderdata.Match(f.Layers, f.Pixels), "scanout_present": f.Scanout != nil, "script_sha256": digest(script), "sequence_sha256": digest(sequence)})
					panic("incomplete original snapshot")
				}
				selected, why := art.Select(f.Layers, f.Palette)
				reasons[why]++
				var sprites []*renderdata.Sprite
				var absent []string
				for _, l := range f.Layers {
					if s := l.Sprite; s != nil {
						sprites = append(sprites, s)
						k := key(s)
						observed[k] = true
						if !keys[k] {
							missing[k] = true
							absent = append(absent, k)
						}
					}
				}
				entry := map[string]any{"phase": p.Name, "serial": f.Serial, "steps": f.Steps, "selected": selected != nil, "reason": why, "sprites": sprites, "missing_keys": absent, "health": f.HUD.State.Health, "paths": c.Status().Paths}
				if baseline != nil {
					old, reason := baseline.Select(f.Layers, f.Palette)
					entry["baseline_selected"] = old != nil
					entry["baseline_reason"] = reason
				}
				trace = append(trace, entry)
				capture := !saved[why]
				for _, s := range sprites {
					if s.Character == character && !saved[key(s)] {
						capture = true
					}
				}
				if capture {
					save(f, why)
					saved[why] = true
					for _, s := range sprites {
						if s.Character == character {
							saved[key(s)] = true
						}
					}
				}
			}
			fmt.Println("sampled", character, p.Name, "frames", c.Status().Frames)
		}
		must(c.SetInput(nil))
		list := func(m map[string]bool) []string {
			v := make([]string, 0, len(m))
			for k := range m {
				v = append(v, k)
			}
			sort.Strings(v)
			return v
		}
		row := map[string]any{"character": character, "opponent": 4, "samples": samples, "trace": trace, "reasons": reasons, "observed_keys": list(observed), "missing_keys": list(missing), "training_modified": c.Status().Training.Modified, "final_steps": c.Status().Steps}
		writeJSON(filepath.Join(dir, "receipt.json"), row)
		delete(row, "trace")
		cases = append(cases, row)
		c.Close()
		runtime.GC()
		fmt.Println("finished", character, "snapshots", len(trace), "missing", list(missing), "reasons", reasons)
	}
	inputs := map[string]string{}
	for _, name := range []string{"workplace/source-manifest.json", "workplace/dosgolem-patched-manifest.json", "internal/hd/characters.go", "internal/hd/geometry.go", "internal/gamecore/core.go"} {
		b, e := os.ReadFile(filepath.Join("/project", name))
		must(e)
		inputs[name] = digest(b)
	}
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "normal keyboard special-action source sampling; not shortcut enablement, full animation or native GUI acceptance", "script_sha256": digest(script), "character_manifest_sha256": digest(manifest), "baseline_manifest_sha256": baselineHash, "requested_character": *characterOnly, "go_version": runtime.Version(), "inputs": inputs, "experiment_name": experiment.Name, "sequence_sha256": digest(sequence), "phases": phases, "cases": cases, "limits": "one declared ordinary keyboard sequence and normal versus path; attempted named action is not proof of its exact move identity; no injected state, forced wins, training, shortcut enablement, controlled RNG comparison or full animation claim"})
}
