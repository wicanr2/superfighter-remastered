package hd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestSpiderLowGuardSourcesAndFallback(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	a, err := LoadCharacters(filepath.Join(root, "hd-characters-spider-low-guard-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	b, err := LoadCharacters(filepath.Join(root, "hd-characters-first-pass-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(a.Manifest.Poses) != 1411 || len(a.Manifest.Atlases) != 65 || len(a.Manifest.Sources) != 20 ||
		!reflect.DeepEqual(a.Manifest.Poses[:1381], b.Manifest.Poses) ||
		!reflect.DeepEqual(a.Manifest.Atlases[:64], b.Manifest.Atlases) ||
		!reflect.DeepEqual(a.Manifest.Sources[:19], b.Manifest.Sources) {
		t.Fatal("base mapping changed")
	}
	unique := map[string]bool{}
	for slot := 0; slot < 72; slot++ {
		art := a.poses[[3]int{8, slot, 0}]
		want := slot == 0 || slot == 1 || slot == 41 || slot >= 45
		if (art != nil) != want {
			t.Fatal("unapproved normal source", slot)
		}
		if art != nil {
			unique[art.Pose.SourceSHA256] = true
		}
		if a.poses[[3]int{8, slot, 1}] != nil || a.poses[[3]int{8, slot, 2}] != nil {
			t.Fatal("unapproved palette or WIN", slot)
		}
	}
	if len(unique) != 3 {
		t.Fatal("wrong source aliases")
	}
	// 真實原生移動圖層另驗 Select 的整組拒絕。
	path := filepath.Join(root, "native-spider-low-guard-v1", "walk.png")
	data, err := os.ReadFile(path + ".frame.json")
	if err != nil {
		t.Fatal(err)
	}
	var frame struct {
		Layers []renderdata.Layer `json:"layers"`
	}
	if err := json.Unmarshal(data, &frame); err != nil {
		t.Fatal(err)
	}
	var palette [256][3]uint8
	data, err = os.ReadFile(path + ".palette.json")
	if err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(data, &palette); err != nil {
		t.Fatal(err)
	}
	if got, reason := a.Select(frame.Layers, palette); got != nil || reason != "此動作的 HD 素材尚未完成，保留原貌" {
		t.Fatal("unknown motion accepted", reason)
	}
}

func TestSpiderHUDUsesNormalCapturedName(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	a, err := LoadHUD(original)
	if err != nil {
		t.Fatal(err)
	}
	read := func(suffix string) []byte {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(root, "native-spider-low-guard-v1", "hd-paused.png") + suffix)
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	var frame struct {
		HUD    *renderdata.HUDSnapshot `json:"hud"`
		Layers []renderdata.Layer      `json:"layers"`
	}
	if err := json.Unmarshal(read(".frame.json"), &frame); err != nil {
		t.Fatal(err)
	}
	if frame.HUD == nil || frame.HUD.State.Characters != [2]uint16{8, 4} {
		t.Fatal("wrong selection")
	}
	frame.HUD.Bitmap = read(".hud.bitmap")
	frame.HUD.Underlay.Indices = read(".hud-under.idx")
	frame.HUD.Underlay.Coverage = read(".hud-under.mask")
	for i := range frame.Layers {
		frame.Layers[i].Indices = read(fmt.Sprintf(".layer-%02d.idx", i))
		frame.Layers[i].Coverage = read(fmt.Sprintf(".layer-%02d.mask", i))
	}
	var palette [256][3]uint8
	if err := json.Unmarshal(read(".palette.json"), &palette); err != nil {
		t.Fatal(err)
	}
	selected, reason := a.Select(frame.HUD, read(".idx"), palette, frame.Layers)
	if selected == nil {
		t.Fatal(reason)
	}
	if selected.Labels != [2]string{"WIDOW", "FRANK"} || selected.Layout.Names[0].Dx() != 57 || selected.Layout.Names[0].Dy() != 11 {
		t.Fatal("wrong name or bounds", selected)
	}
	frame.HUD.Bitmap[0] ^= 1
	if got, _ := a.Select(frame.HUD, read(".idx"), palette, frame.Layers); got != nil {
		t.Fatal("corrupt HUD accepted")
	}
}
