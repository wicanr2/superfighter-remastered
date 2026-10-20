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

// 原圖與 typed 資產通過不代表原生人物、姓名及完整動作已驗收。
func TestBulletCandidateMatchesNormalOriginalSources(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadCharacters(filepath.Join(root, "hd-characters-bullet-candidate-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	base, err := LoadCharacters(filepath.Join(root, "hd-characters-sarkov-victory-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(assets.Manifest.Poses) != 517 || len(assets.Manifest.Atlases) != 25 ||
		!reflect.DeepEqual(assets.Manifest.Poses[:len(base.Manifest.Poses)], base.Manifest.Poses) ||
		!reflect.DeepEqual(assets.Manifest.Atlases[:len(base.Manifest.Atlases)], base.Manifest.Atlases) {
		t.Fatal("existing assets changed or candidate incomplete")
	}
	unique := map[string]bool{}
	for slot := 0; slot < 72; slot++ {
		art := assets.poses[[3]int{2, slot, 0}]
		if art == nil {
			t.Fatal("missing original normal slot", slot)
		}
		unique[art.Pose.SourceSHA256] = true
	}
	if len(unique) != 58 {
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
	data, err := os.ReadFile(filepath.Join(root, "hd-frame-bullet-v1", "receipt.json"))
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
		if !frame.Background || len(frame.Actors) != 2 || frame.Actors[0].Character != 2 || frame.Actors[1].Character != 4 {
			t.Fatal("normal selection or rooftop mismatch")
		}
		actor := frame.Actors[0]
		pose := assets.poses[[3]int{2, actor.Slot, 0}].Pose
		if !actor.Matches || pose.SourceOffset != actor.Offset || actor.Size != [2]int{pose.Width, pose.Height} {
			t.Fatal("normal runtime source differs", actor.Slot)
		}
		seen[actor.Slot] = true
	}
	if len(seen) != 15 {
		t.Fatal("normal source coverage changed", seen)
	}
}

func TestBulletHUDUsesNormalCapturedName(t *testing.T) {
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
		data, err := os.ReadFile(filepath.Join(root, "native-bullet-v1", "hd-paused.png"+suffix))
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
	if frame.HUD == nil || frame.HUD.State.Characters != [2]uint16{2, 4} {
		t.Fatal("wrong normal character selection")
	}
	frame.HUD.Bitmap = read(".hud.bitmap")
	frame.HUD.Underlay.Indices = read(".hud-under.idx")
	frame.HUD.Underlay.Coverage = read(".hud-under.mask")
	for ordinal := range frame.Layers {
		frame.Layers[ordinal].Indices = read(fmt.Sprintf(".layer-%02d.idx", ordinal))
		frame.Layers[ordinal].Coverage = read(fmt.Sprintf(".layer-%02d.mask", ordinal))
	}
	var palette [256][3]uint8
	if err := json.Unmarshal(read(".palette.json"), &palette); err != nil {
		t.Fatal(err)
	}
	selected, reason := a.Select(frame.HUD, read(".idx"), palette, frame.Layers)
	if selected == nil {
		t.Fatal(reason)
	}
	if selected.Labels != [2]string{"BULLET", "FRANK"} || selected.Layout.Names[0].Dx() != 62 || selected.Layout.Names[0].Dy() != 11 {
		t.Fatal("captured original name or bounds changed", selected.Labels, selected.Layout.Names)
	}
	wrong := *frame.HUD
	wrong.State.Characters[0] = 11
	if got, reason := a.Select(&wrong, read(".idx"), palette, frame.Layers); got != nil || reason != "介面欄位未對應，保留原貌" {
		t.Fatal("unknown character was accepted", reason)
	}
}
