package hd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestKimEffectsRealSourcesAndAtomicRejection(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original effect fixtures not supplied")
	}
	art, err := LoadCharacters(filepath.Join(root, "hd-characters-kim-effects-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(art.Manifest.Poses) != 1495 || len(art.Manifest.Atlases) != 68 {
		t.Fatal("unexpected candidate")
	}
	directory := filepath.Join(root, "special-kim-v1", "character-07")
	read := func(name string) []byte {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(directory, name))
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	var receipt struct {
		Samples []struct{ Stem string } `json:"samples"`
	}
	if err := json.Unmarshal(read("receipt.json"), &receipt); err != nil {
		t.Fatal(err)
	}
	seen := map[int]bool{}
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
		for target, layer := range frame.Layers {
			s := layer.Sprite
			if s == nil || s.Character != 7 || !s.Effect || seen[s.Slot] {
				continue
			}
			seen[s.Slot] = true
			t.Run(fmt.Sprint(s.Slot), func(t *testing.T) {
				poses, why := art.Select(frame.Layers, palette)
				if poses == nil {
					t.Fatal("complete original effect group rejected", why)
				}
				found := false
				for _, pose := range poses {
					if pose.Pose.Character == 7 && pose.Pose.PaletteBank == 1 && pose.Pose.Slot == s.Slot {
						found = true
						if pose.Pose.Atlas != "kim-effects.png" {
							t.Fatal("wrong palette-bank art")
						}
					}
				}
				if !found {
					t.Fatal("new effect not selected")
				}
				for _, change := range []struct {
					name  string
					apply func(*renderdata.Sprite)
				}{
					{"unknown effect", func(v *renderdata.Sprite) { v.Slot = 59 }},
					{"wrong source", func(v *renderdata.Sprite) { v.SourceSHA256 = "invalid" }},
					{"wrong palette bank", func(v *renderdata.Sprite) { v.PaletteBase = 0xc0 }},
				} {
					layers := append([]renderdata.Layer(nil), frame.Layers...)
					changed := *s
					change.apply(&changed)
					layers[target].Sprite = &changed
					if poses, _ := art.Select(layers, palette); poses != nil {
						t.Fatal("invalid effect allowed partial HD", change.name)
					}
				}
				changed := palette
				changed[int(s.PaletteBase)+1][0] ^= 1
				if poses, _ := art.Select(frame.Layers, changed); poses != nil {
					t.Fatal("changed source palette allowed partial HD")
				}
			})
		}
	}
	for _, slot := range []int{6, 37, 49, 50, 51, 52, 53, 54, 55, 56} {
		if !seen[slot] {
			t.Fatal("normal source fixture missing", slot)
		}
	}
}
