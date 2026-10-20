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

func TestLanVictoryPackPreservesSourcesAndReusesIdenticalArt(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	a, err := LoadCharacters(filepath.Join(root, "hd-characters-lan-victory-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	b, err := os.ReadFile(filepath.Join(root, "hd-characters-spider-low-guard-v1", "manifest.json"))
	if err != nil {
		t.Fatal(err)
	}
	var base CharacterManifest
	if err := json.Unmarshal(b, &base); err != nil {
		t.Fatal(err)
	}
	if len(a.Manifest.Poses) != 1483 || len(a.Manifest.Atlases) != 66 || len(a.Manifest.Sources) != 21 ||
		!reflect.DeepEqual(a.Manifest.Poses[:len(base.Poses)], base.Poses) ||
		!reflect.DeepEqual(a.Manifest.Atlases[:len(base.Atlases)], base.Atlases) ||
		!reflect.DeepEqual(a.Manifest.Sources[:len(base.Sources)], base.Sources) {
		t.Fatal("existing sources changed or new WIN registration incomplete")
	}
	unique := map[string]bool{}
	for slot := 0; slot < 72; slot++ {
		art := a.poses[[3]int{6, slot, 2}]
		if art == nil || art.Pose.SourceBank != "victory" {
			t.Fatal("missing WIN slot", slot)
		}
		unique[art.Pose.SourceSHA256] = true
		if slot < 2 {
			normal := a.poses[[3]int{6, slot, 0}]
			if normal == nil || art.Pose.SourceSHA256 != normal.Pose.SourceSHA256 || art.Pose.Atlas != normal.Pose.Atlas || art.Bounds != normal.Bounds {
				t.Fatal("identical original bytes must reuse accepted normal art", slot)
			}
		}
	}
	if len(unique) != 6 {
		t.Fatal("wrong unique source count", len(unique))
	}
	if a.poses[[3]int{8, 0, 2}] != nil {
		t.Fatal("unmapped Spider WIN registered")
	}
}

func TestLanVictoryNameMatchesNormalSourceAndRejectsTampering(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	a, err := LoadVictories(original)
	if err != nil {
		t.Fatal(err)
	}
	read := func(suffix string) []byte {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(root, "hd-first-pass-v1", "lan-diagnostic-v2", "victory-frame"+suffix))
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
	if f.Victory == nil || f.Victory.State.Winner != 6 || f.Victory.State.Characters != [2]uint16{6, 4} {
		t.Fatal("wrong normal source")
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
	selected, why := a.Select(f.Victory, f.Layers, palette, f.Counter)
	if selected == nil {
		t.Fatal(why)
	}
	if len(selected.Runs) != 2 || selected.Runs[0].Label != "LAN" || selected.Runs[0].Bounds != image.Rect(125, 54, 156, 65) || selected.Runs[1].Label != "WIN" || selected.Runs[1].Bounds != image.Rect(165, 54, 196, 65) {
		t.Fatal("wrong original name or bounds", selected.Runs)
	}
	f.Victory.Draws[0].SourceSI++
	if selected, _ := a.Select(f.Victory, f.Layers, palette, f.Counter); selected != nil {
		t.Fatal("tampered source accepted")
	}
}
