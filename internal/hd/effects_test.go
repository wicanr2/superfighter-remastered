package hd

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestOriginalEffectSourcesAndPaletteIsolation(t *testing.T) {
	pack, root, fixtures := os.Getenv("KDZZ_HD_CHARACTERS"), os.Getenv("KDZZ_ORIGINAL_ROOT"), os.Getenv("KDZZ_HD_FIXTURES")
	if pack == "" || root == "" || fixtures == "" {
		t.Skip("local effect assets not supplied")
	}
	a, e := LoadCharacters(pack, root)
	if e != nil {
		t.Fatal(e)
	}
	if !a.HasEffects() {
		t.Skip("version 1 compatibility pack has no HD effects")
	}
	read := func(path string) []byte {
		t.Helper()
		b, e := os.ReadFile(path)
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	tested, skipped := 0, 0
	for _, dir := range []string{"effect-draw-v1", "effect-draw-v2"} {
		var receipt struct{ Frames []struct{ Fixture string } }
		if e = json.Unmarshal(read(filepath.Join(fixtures, dir, "receipt.json")), &receipt); e != nil {
			t.Fatal(e)
		}
		for _, f := range receipt.Frames {
			if f.Fixture == "" {
				continue
			}
			var metadata []struct {
				Kind string
				Draw *struct {
					Width, Height int
					Flags         uint8
					Palette       uint8  `json:"palette_base"`
					DI            int    `json:"destination_di"`
					Top           int    `json:"top_clip"`
					Left          int    `json:"left_clip"`
					Right         int    `json:"right_clip"`
					SHA           string `json:"source_sha256"`
					Sources       []struct{ Player, Character, Slot int }
				}
			}
			base := filepath.Join(fixtures, dir, f.Fixture)
			if e = json.Unmarshal(read(base+".layers.json"), &metadata); e != nil {
				t.Fatal(e)
			}
			var palette [256][3]uint8
			if e = json.Unmarshal(read(base+".palette.json"), &palette); e != nil {
				t.Fatal(e)
			}
			layers := make([]renderdata.Layer, len(metadata))
			effectIndex := -1
			covered := true
			for i, l := range metadata {
				layers[i].Background = i == 0
				if l.Draw == nil {
					continue
				}
				d := l.Draw
				s := d.Sources[0]
				isEffect := l.Kind == "effect"
				bank := 0
				if isEffect {
					bank = 1
					effectIndex = i
				}
				if a.poses[[3]int{s.Character, s.Slot, bank}] == nil {
					covered = false
				}
				layers[i].Sprite = &renderdata.Sprite{Effect: isEffect, Player: s.Player, Character: s.Character, Slot: s.Slot, X: d.DI % 320, Y: d.DI / 320, Width: d.Width, Height: d.Height, Flags: d.Flags, PaletteBase: d.Palette, TopClip: d.Top, LeftClip: d.Left, RightClip: d.Right, SourceSHA256: d.SHA}
			}
			if !covered {
				skipped++
				continue
			}
			selected, reason := a.Select(layers, palette)
			if len(selected) != 3 || effectIndex < 0 {
				t.Fatalf("%s %s: %s", dir, f.Fixture, reason)
			}
			original := *layers[effectIndex].Sprite
			for _, change := range []func(*renderdata.Sprite){func(s *renderdata.Sprite) { s.PaletteBase -= 16 }, func(s *renderdata.Sprite) { s.LeftClip = 1 }, func(s *renderdata.Sprite) { s.RightClip = 1 }, func(s *renderdata.Sprite) { s.Flags = 128 }, func(s *renderdata.Sprite) { s.SourceSHA256 = "wrong" }} {
				change(layers[effectIndex].Sprite)
				if got, _ := a.Select(layers, palette); got != nil {
					t.Fatal("invalid effect produced a partial HD frame")
				}
				*layers[effectIndex].Sprite = original
			}
			badPalette := palette
			badPalette[original.PaletteBase][0] ^= 1
			if got, _ := a.Select(layers, badPalette); got != nil {
				t.Fatal("effect palette transition accepted")
			}
			tested++
		}
	}
	if tested < 8 {
		t.Fatalf("insufficient original effect fixtures: %d", tested)
	}
	t.Logf("verified original effect frames: %d; absent other-character assets: %d", tested, skipped)
	bad := t.TempDir()
	entries, e := os.ReadDir(pack)
	if e != nil {
		t.Fatal(e)
	}
	for _, entry := range entries {
		if entry.IsDir() {
			continue
		}
		name := entry.Name()
		if e = os.WriteFile(filepath.Join(bad, name), read(filepath.Join(pack, name)), 0600); e != nil {
			t.Fatal(e)
		}
	}
	m := a.Manifest
	m.Version = 1
	bytes, e := json.Marshal(m)
	if e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(filepath.Join(bad, "manifest.json"), bytes, 0600); e != nil {
		t.Fatal(e)
	}
	// Reject the incompatible version before attempting to accept any partial group.
	if got, e := LoadCharacters(bad, root); got != nil || e == nil {
		t.Fatal("version 1 accepted a version 2 effect group")
	}
	var normal CharacterManifest
	if e = json.Unmarshal(read(filepath.Join(pack, "manifest.json")), &normal); e != nil {
		t.Fatal(e)
	}
	normal.Version = 1
	normal.Sources = nil
	for _, source := range a.Manifest.Sources {
		if source.SourceBank == "" {
			normal.Sources = append(normal.Sources, source)
		}
	}
	normal.Poses = nil
	for _, pose := range a.Manifest.Poses {
		if pose.PaletteBank == 0 && pose.SourceBank == "" {
			normal.Poses = append(normal.Poses, pose)
		}
	}
	encoded, e := json.Marshal(normal)
	if e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(filepath.Join(bad, "manifest.json"), encoded, 0600); e != nil {
		t.Fatal(e)
	}
	if got, e := LoadCharacters(bad, root); e != nil || got.HasEffects() {
		t.Fatalf("legacy normal group rejected: %v", e)
	}
}
