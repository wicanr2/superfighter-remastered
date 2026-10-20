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

func TestPhoenixVictoryCandidatePreservesBulletAndOriginalSources(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadCharacters(filepath.Join(root, "hd-characters-phoenix-victory-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	base, err := LoadCharacters(filepath.Join(root, "hd-characters-bullet-victory-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(assets.Manifest.Poses) != 1093 || len(assets.Manifest.Atlases) != 60 || len(assets.Manifest.Sources) != 15 ||
		!reflect.DeepEqual(assets.Manifest.Poses[:len(base.Manifest.Poses)], base.Manifest.Poses) ||
		!reflect.DeepEqual(assets.Manifest.Atlases[:len(base.Manifest.Atlases)], base.Manifest.Atlases) ||
		!reflect.DeepEqual(assets.Manifest.Sources[:len(base.Manifest.Sources)], base.Manifest.Sources) {
		t.Fatal("existing assets changed or candidate incomplete")
	}
	unique := map[string]bool{}
	for slot := 0; slot < 72; slot++ {
		art := assets.poses[[3]int{3, slot, 2}]
		if art == nil || art.Pose.SourceBank != "victory" {
			t.Fatal("missing original victory source", slot)
		}
		unique[art.Pose.SourceSHA256] = true
	}
	if len(unique) != 3 {
		t.Fatal("victory source coverage changed", len(unique))
	}
}

func TestPhoenixVictoryNameUsesNormalOriginalDraws(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	read := func(suffix string) []byte {
		t.Helper()
		b, err := os.ReadFile(filepath.Join(root, "phoenix-victory-core-diagnostic-v1", "victory-frame"+suffix))
		if err != nil {
			t.Fatal(err)
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
	if f.Victory == nil || f.Victory.State.Characters != [2]uint16{3, 4} || f.Victory.State.Winner != 3 {
		t.Fatal("wrong normal victory fixture")
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
	assets, err := LoadVictories(original)
	if err != nil {
		t.Fatal(err)
	}
	selected, why := assets.Select(f.Victory, f.Layers, palette, f.Counter)
	if selected == nil {
		t.Fatal(why)
	}
	if len(selected.Runs) != 2 || selected.Runs[0].Label != "PHO HUANG" || selected.Runs[1].Label != "WIN" ||
		selected.Runs[0].Bounds != image.Rect(94, 54, 187, 65) || selected.Runs[1].Bounds != image.Rect(196, 54, 227, 65) {
		t.Fatal("normal victory text changed", selected.Runs)
	}
	f.Victory.Draws[0].SourceSI++
	if selected, _ := assets.Select(f.Victory, f.Layers, palette, f.Counter); selected != nil {
		t.Fatal("wrong original source accepted")
	}
}
