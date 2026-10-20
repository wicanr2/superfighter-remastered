package hd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestRemainingEffectsOriginalSourcesAndRejection(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local special-effect originals not supplied")
	}
	a, err := LoadCharacters(filepath.Join(root, "hd-characters-remaining-effects-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(a.Manifest.Poses) != 1516 || len(a.Manifest.Atlases) != 74 {
		t.Fatal("wrong candidate")
	}
	old, err := LoadCharacters(filepath.Join(root, "hd-characters-kim-effects-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	wanted := map[int][]int{3: {15, 39, 56}, 6: {9, 11, 12, 20, 26, 57, 58}, 9: {14, 19, 49, 57, 58, 59, 60, 61}, 10: {41, 42, 43}}
	seen, selected, refused := map[[2]int]bool{}, 0, 0
	for character, slots := range wanted {
		dir := filepath.Join(root, "remaining-special-audit-v1", fmt.Sprintf("character-%02d", character), fmt.Sprintf("character-%02d", character))
		read := func(name string) []byte {
			t.Helper()
			b, e := os.ReadFile(filepath.Join(dir, name))
			if e != nil {
				t.Fatal(e)
			}
			return b
		}
		var receipt struct {
			Samples []struct{ Stem string } `json:"samples"`
		}
		if e := json.Unmarshal(read("receipt.json"), &receipt); e != nil {
			t.Fatal(e)
		}
		for _, sample := range receipt.Samples {
			var frame struct {
				Layers []renderdata.Layer `json:"layers"`
			}
			var palette [256][3]uint8
			if e := json.Unmarshal(read(sample.Stem+".frame.json"), &frame); e != nil {
				t.Fatal(e)
			}
			if e := json.Unmarshal(read(sample.Stem+".palette.json"), &palette); e != nil {
				t.Fatal(e)
			}
			for i := range frame.Layers {
				frame.Layers[i].Indices = read(fmt.Sprintf("%s.layer-%02d.idx", sample.Stem, i))
				frame.Layers[i].Coverage = read(fmt.Sprintf("%s.layer-%02d.mask", sample.Stem, i))
			}
			poses, why := a.Select(frame.Layers, palette)
			previous, _ := old.Select(frame.Layers, palette)
			if previous != nil && poses == nil {
				t.Fatal("old frame regressed", character, sample.Stem, why)
			}
			for ordinal, l := range frame.Layers {
				s := l.Sprite
				if s == nil || !s.Effect || s.Character != character || s.PaletteBase != 0xd0 {
					continue
				}
				key := [2]int{character, s.Slot}
				found := false
				for _, slot := range slots {
					if slot == s.Slot {
						found = true
					}
				}
				if !found {
					continue
				}
				seen[key] = true
				art := a.poses[[3]int{character, s.Slot, 1}]
				if art == nil || art.Pose.SourceSHA256 != s.SourceSHA256 || art.Pose.Width != s.Width || art.Pose.Height != s.Height {
					t.Fatal("wrong packed source", key)
				}
				if poses == nil {
					if character != 3 || why != "此色盤保留原貌" {
						t.Fatal("unexpected effect refusal", key, why)
					}
					refused++
					continue
				}
				selected++
				for _, change := range []func(*renderdata.Sprite){func(v *renderdata.Sprite) { v.SourceSHA256 = "invalid" }, func(v *renderdata.Sprite) { v.PaletteBase++ }, func(v *renderdata.Sprite) { v.Player = 1 }, func(v *renderdata.Sprite) { v.TopClip = 1 }} {
					bad := append([]renderdata.Layer(nil), frame.Layers...)
					v := *s
					change(&v)
					bad[ordinal].Sprite = &v
					if got, _ := a.Select(bad, palette); got != nil {
						t.Fatal("invalid effect allowed partial HD", key)
					}
				}
				badPalette := palette
				badPalette[209][0] ^= 1
				if got, _ := a.Select(frame.Layers, badPalette); got != nil {
					t.Fatal("unknown palette accepted", key)
				}
			}
		}
	}
	for character, slots := range wanted {
		for _, slot := range slots {
			if !seen[[2]int{character, slot}] {
				t.Fatal("missing original fixture", character, slot)
			}
		}
	}
	if len(seen) != 21 || selected == 0 {
		t.Fatal("missing coverage", len(seen), selected)
	}
	t.Log("source keys", len(seen), "selected saved effects", selected, "retained Phoenix palette refusals", refused)
	dir := t.TempDir()
	if e := os.WriteFile(filepath.Join(dir, "manifest.json"), bytes.Repeat([]byte(" "), (520<<10)+1), 0600); e != nil {
		t.Fatal(e)
	}
	if got, e := LoadCharacters(dir, original); e == nil || got != nil {
		t.Fatal("oversized manifest accepted")
	}
}
