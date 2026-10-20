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

// 候選來源與正常 consumer 不代替原生或完整動畫驗收。
func TestJoeCandidateMatchesNormalOriginalSources(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadCharacters(filepath.Join(root, "hd-characters-joe-candidate-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	base, err := LoadCharacters(filepath.Join(root, "hd-characters-clown-candidate-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(assets.Manifest.Poses) != 949 || len(assets.Manifest.Atlases) != 58 || len(assets.Manifest.Sources) != 13 ||
		!reflect.DeepEqual(assets.Manifest.Poses[:len(base.Manifest.Poses)], base.Manifest.Poses) ||
		!reflect.DeepEqual(assets.Manifest.Atlases[:len(base.Manifest.Atlases)], base.Manifest.Atlases) ||
		!reflect.DeepEqual(assets.Manifest.Sources[:len(base.Manifest.Sources)], base.Manifest.Sources) {
		t.Fatal("existing assets changed or candidate incomplete")
	}
	unique := map[string]bool{}
	for slot := 0; slot < 72; slot++ {
		art := assets.poses[[3]int{10, slot, 0}]
		if art == nil {
			t.Fatal("missing original normal slot", slot)
		}
		unique[art.Pose.SourceSHA256] = true
	}
	if len(unique) != 44 {
		t.Fatal("source alias coverage changed", len(unique))
	}
	var receipt struct {
		Frames []struct {
			Phase      string `json:"phase"`
			Background bool   `json:"background_buffer_equals_source"`
			Actors     []struct {
				Path      int    `json:"path"`
				Character int    `json:"character"`
				Slot      int    `json:"slot"`
				Offset    int    `json:"source_file_offset"`
				Size      [2]int `json:"size"`
				Matches   bool   `json:"bytes_match_source"`
			} `json:"actors"`
		} `json:"frames"`
	}
	data, err := os.ReadFile(filepath.Join(root, "hd-frame-joe-v2", "receipt.json"))
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
		if !frame.Background || len(frame.Actors) != 2 || frame.Actors[0].Character != 10 || frame.Actors[1].Character != 4 {
			t.Fatal("normal selection or rooftop mismatch")
		}
		for _, actor := range frame.Actors {
			art := assets.poses[[3]int{actor.Character, actor.Slot, 0}]
			if art == nil || !actor.Matches || art.Pose.SourceOffset != actor.Offset || actor.Size != [2]int{art.Pose.Width, art.Pose.Height} {
				t.Fatal("normal runtime source differs", actor.Character, actor.Slot)
			}
		}
		seen[frame.Actors[0].Slot] = true
		if frame.Phase == "p1-punch" && (frame.Actors[0].Path != 27 || frame.Actors[0].Slot < 5 || frame.Actors[0].Slot > 7) {
			t.Fatal("ordinary punch source mismatch", frame.Actors[0])
		}
	}
	want := map[int]bool{1: true, 2: true, 3: true, 4: true, 5: true, 6: true, 7: true, 15: true, 38: true, 39: true, 40: true}
	if !reflect.DeepEqual(seen, want) {
		t.Fatal("normal source coverage changed", seen)
	}
}

func TestJoeHUDUsesNormalCapturedName(t *testing.T) {
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
		data, err := os.ReadFile(filepath.Join(root, "native-joe-v2", "hd-paused.png"+suffix))
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
	if frame.HUD == nil || frame.HUD.State.Characters != [2]uint16{10, 4} {
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
	if selected.Labels != [2]string{"INDIAN JOE", "FRANK"} || selected.Layout.Names[0].Dx() != 96 || selected.Layout.Names[0].Dy() != 11 {
		t.Fatal("captured original name or bounds changed", selected.Labels, selected.Layout.Names)
	}
	wrong := *frame.HUD
	wrong.State.Characters[0] = 8
	if got, reason := assets.Select(&wrong, read(".idx"), palette, frame.Layers); got != nil || reason != "此角色的高解析介面尚未完成" {
		t.Fatal("unknown character was accepted", reason)
	}
}
