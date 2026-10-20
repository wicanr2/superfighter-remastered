package hd

import (
	"encoding/json"
	"fmt"
	"image"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestFirstPassVictorySourcesPreserveExistingPack(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadCharacters(filepath.Join(root, "hd-characters-first-pass-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	data, err := os.ReadFile(filepath.Join(root, "hd-characters-onimaru-victory-v1", "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	var base CharacterManifest
	if err := json.Unmarshal(data, &base); err != nil {
		t.Fatal(err)
	}
	if len(assets.Manifest.Poses) != 1381 || len(assets.Manifest.Atlases) != 64 || len(assets.Manifest.Sources) != 19 ||
		!reflect.DeepEqual(assets.Manifest.Poses[:len(base.Poses)], base.Poses) ||
		!reflect.DeepEqual(assets.Manifest.Atlases[:len(base.Atlases)], base.Atlases) ||
		!reflect.DeepEqual(assets.Manifest.Sources[:len(base.Sources)], base.Sources) {
		t.Fatal("existing pack changed or new sources incomplete")
	}
	for character, want := range map[int]int{7: 8, 9: 3, 10: 4} {
		unique := map[string]bool{}
		for slot := 0; slot < 72; slot++ {
			art := assets.poses[[3]int{character, slot, 2}]
			if art == nil || art.Pose.SourceBank != "victory" {
				t.Fatal("missing victory source", character, slot)
			}
			unique[art.Pose.SourceSHA256] = true
		}
		if len(unique) != want {
			t.Fatal("source alias coverage differs", character, len(unique))
		}
	}
	for _, character := range []int{6, 8} {
		if assets.poses[[3]int{character, 0, 2}] != nil {
			t.Fatal("unapproved candidate was registered", character)
		}
	}
}

func TestFirstPassVictoryNamesMatchNormalCapturedDraws(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadVictories(original)
	if err != nil {
		t.Fatal(err)
	}
	for _, tc := range []struct {
		slug, label                     string
		character, left, width, winLeft int
	}{
		{"kim", "KING TAI CHI", 7, 86, 109, 204},
		{"clown", "JOKER", 9, 114, 52, 175},
		{"joe", "INDIAN JOE", 10, 92, 96, 197},
	} {
		t.Run(tc.slug, func(t *testing.T) {
			read := func(suffix string) []byte {
				t.Helper()
				b, e := os.ReadFile(filepath.Join(root, "hd-first-pass-v1", tc.slug+"-diagnostic", "victory-frame"+suffix))
				if e != nil {
					t.Fatal(e)
				}
				return b
			}
			var f struct {
				Victory *renderdata.VictorySnapshot `json:"victory"`
				Layers  []renderdata.Layer          `json:"layers"`
				Counter uint16                      `json:"counter"`
			}
			if err := json.Unmarshal(read(".frame.json"), &f); err != nil {
				t.Fatal(err)
			}
			if f.Victory == nil || f.Victory.State.Characters != [2]uint16{uint16(tc.character), 4} || f.Victory.State.Winner != uint16(tc.character) {
				t.Fatal("wrong normal fixture")
			}
			f.Victory.Underlay.Indices = read(".victory-under.idx")
			f.Victory.Underlay.Coverage = read(".victory-under.mask")
			for i := range f.Victory.Draws {
				f.Victory.Draws[i].Source = read(fmt.Sprintf(".victory-%02d.source", i))
			}
			for i := range f.Layers {
				f.Layers[i].Indices = read(fmt.Sprintf(".layer-%02d.idx", i))
				f.Layers[i].Coverage = read(fmt.Sprintf(".layer-%02d.mask", i))
			}
			var palette [256][3]uint8
			if err := json.Unmarshal(read(".palette.json"), &palette); err != nil {
				t.Fatal(err)
			}
			selected, why := assets.Select(f.Victory, f.Layers, palette, f.Counter)
			if selected == nil {
				t.Fatal(why)
			}
			if len(selected.Runs) != 2 || selected.Runs[0].Label != tc.label || selected.Runs[1].Label != "WIN" ||
				selected.Runs[0].Bounds != image.Rect(tc.left, 54, tc.left+tc.width, 65) || selected.Runs[1].Bounds != image.Rect(tc.winLeft, 54, tc.winLeft+31, 65) {
				t.Fatal("original name or bounds differs", selected.Runs)
			}
			f.Victory.Draws[0].SourceSI++
			if selected, _ := assets.Select(f.Victory, f.Layers, palette, f.Counter); selected != nil {
				t.Fatal("tampered source accepted")
			}
		})
	}
}
