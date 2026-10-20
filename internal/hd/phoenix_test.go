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

// 候選的來源／consumer 核對不取代原生與完整動畫驗收。
func TestPhoenixCandidateMatchesNormalOriginalSources(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadCharacters(filepath.Join(root, "hd-characters-phoenix-candidate-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	base, err := LoadCharacters(filepath.Join(root, "hd-characters-bullet-candidate-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(assets.Manifest.Poses) != 589 || len(assets.Manifest.Atlases) != 31 || len(assets.Manifest.Sources) != 8 ||
		!reflect.DeepEqual(assets.Manifest.Poses[:len(base.Manifest.Poses)], base.Manifest.Poses) ||
		!reflect.DeepEqual(assets.Manifest.Atlases[:len(base.Manifest.Atlases)], base.Manifest.Atlases) ||
		!reflect.DeepEqual(assets.Manifest.Sources[:len(base.Manifest.Sources)], base.Manifest.Sources) {
		t.Fatal("existing assets changed or candidate incomplete")
	}
	unique := map[string]bool{}
	for slot := 0; slot < 72; slot++ {
		art := assets.poses[[3]int{3, slot, 0}]
		if art == nil {
			t.Fatal("missing original normal slot", slot)
		}
		unique[art.Pose.SourceSHA256] = true
	}
	if len(unique) != 61 {
		t.Fatal("source alias coverage changed", len(unique))
	}
	var receipt struct {
		Frames []struct {
			Background bool `json:"background_buffer_equals_source"`
			Actors     []struct {
				Character int    `json:"character"`
				Slot      int    `json:"slot"`
				Offset    int    `json:"source_file_offset"`
				Size      [2]int `json:"size"`
				Matches   bool   `json:"bytes_match_source"`
			} `json:"actors"`
		} `json:"frames"`
	}
	data, err := os.ReadFile(filepath.Join(root, "hd-frame-phoenix-v1", "receipt.json"))
	if err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(data, &receipt); err != nil {
		t.Fatal(err)
	}
	if len(receipt.Frames) != 124 {
		t.Fatal("normal consumer receipt incomplete")
	}
	seen := map[int]bool{}
	for _, frame := range receipt.Frames {
		if !frame.Background || len(frame.Actors) != 2 || frame.Actors[0].Character != 3 || frame.Actors[1].Character != 4 {
			t.Fatal("normal selection or rooftop mismatch")
		}
		actor := frame.Actors[0]
		art := assets.poses[[3]int{3, actor.Slot, 0}]
		if art == nil || !actor.Matches || art.Pose.SourceOffset != actor.Offset || actor.Size != [2]int{art.Pose.Width, art.Pose.Height} {
			t.Fatal("normal runtime source differs", actor.Slot)
		}
		seen[actor.Slot] = true
	}
	if len(seen) != 12 {
		t.Fatal("normal source coverage changed", seen)
	}
}

func TestPhoenixHUDUsesNormalCapturedName(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadHUD(original)
	if err != nil {
		t.Fatal(err)
	}
	read := func(suffix string) []byte {
		t.Helper()
		data, err := os.ReadFile(filepath.Join(root, "native-phoenix-v2", "hd-paused.png"+suffix))
		if err != nil {
			t.Fatal(err)
		}
		return data
	}
	var frame struct {
		HUD    *renderdata.HUDSnapshot `json:"hud"`
		Layers []renderdata.Layer      `json:"layers"`
	}
	if err := json.Unmarshal(read(".frame.json"), &frame); err != nil {
		t.Fatal(err)
	}
	if frame.HUD == nil || frame.HUD.State.Characters != [2]uint16{3, 4} {
		t.Fatal("wrong normal character selection")
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
	selected, reason := assets.Select(frame.HUD, read(".idx"), palette, frame.Layers)
	if selected == nil {
		t.Fatal(reason)
	}
	if selected.Labels != [2]string{"PHO HUANG", "FRANK"} || selected.Layout.Names[0].Dx() != 93 || selected.Layout.Names[0].Dy() != 11 {
		t.Fatal("captured original name or bounds changed", selected.Labels, selected.Layout.Names)
	}
	wrong := *frame.HUD
	wrong.State.Characters[0] = 11
	if got, reason := assets.Select(&wrong, read(".idx"), palette, frame.Layers); got != nil || reason != "介面欄位未對應，保留原貌" {
		t.Fatal("unknown character was accepted", reason)
	}
}
