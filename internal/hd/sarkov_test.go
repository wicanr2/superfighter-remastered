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

// 候選資料讀取不代表角色已通過原生 HD 驗收；這裡核對正常原版 consumer。
func TestSarkovCandidateMatchesNormalOriginalSources(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original sources not supplied")
	}
	assets, err := LoadCharacters(filepath.Join(root, "hd-characters-sarkov-candidate-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	base, err := LoadCharacters(filepath.Join(root, "hd-characters-study-v8"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(assets.Manifest.Poses) != len(base.Manifest.Poses)+72 || len(assets.Manifest.Atlases) != len(base.Manifest.Atlases)+4 {
		t.Fatal("candidate is incomplete")
	}
	if !reflect.DeepEqual(assets.Manifest.Poses[:len(base.Manifest.Poses)], base.Manifest.Poses) ||
		!reflect.DeepEqual(assets.Manifest.Atlases[:len(base.Manifest.Atlases)], base.Manifest.Atlases) {
		t.Fatal("existing characters changed")
	}
	unique := map[string]bool{}
	for slot := 0; slot < 72; slot++ {
		art := assets.poses[[3]int{1, slot, 0}]
		if art == nil {
			t.Fatal("missing normal source", slot)
		}
		unique[art.Pose.SourceSHA256] = true
	}
	if len(unique) != 45 {
		t.Fatal("unexpected source alias coverage", len(unique))
	}
	var receipt struct {
		InputSHA map[string]string `json:"input_sha256"`
		Frames   []struct {
			Actors []struct {
				Character int    `json:"character"`
				Slot      int    `json:"slot"`
				Offset    int    `json:"source_file_offset"`
				Size      [2]int `json:"size"`
				Matches   bool   `json:"bytes_match_source"`
			} `json:"actors"`
		} `json:"frames"`
	}
	data, err := os.ReadFile(filepath.Join(root, "hd-frame-sarkov-v2", "receipt.json"))
	if err != nil {
		t.Fatal(err)
	}
	if err = json.Unmarshal(data, &receipt); err != nil {
		t.Fatal(err)
	}
	if receipt.InputSHA["SFMAN02.DAT"] != "e169a26f348ad6efc6563abe945698a7ccc2586134af611b5d5391e7984a30d6" || len(receipt.Frames) != 124 {
		t.Fatal("wrong normal original receipt")
	}
	seen := map[int]bool{}
	for _, frame := range receipt.Frames {
		if len(frame.Actors) != 2 || frame.Actors[0].Character != 1 || frame.Actors[1].Character != 4 {
			t.Fatal("wrong normal selection")
		}
		actor := frame.Actors[0]
		pose := assets.poses[[3]int{1, actor.Slot, 0}].Pose
		if !actor.Matches || pose.SourceOffset != actor.Offset || actor.Size != [2]int{pose.Width, pose.Height} {
			t.Fatal("candidate differs from normal runtime source", actor.Slot)
		}
		seen[actor.Slot] = true
	}
	if len(seen) != 11 {
		t.Fatal("normal source coverage changed", seen)
	}
}

func TestSarkovHUDUsesNormalCapturedName(t *testing.T) {
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
		data, err := os.ReadFile(filepath.Join(root, "native-sarkov-v2", "hd-paused.png"+suffix))
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
	if frame.HUD == nil || frame.HUD.State.Characters != [2]uint16{1, 4} {
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
	if selected.Labels != [2]string{"SARORKOV", "FRANK"} || selected.Layout.Names[0].Dx() != 88 || selected.Layout.Names[0].Dy() != 11 {
		t.Fatal("captured original name or bounds changed", selected.Labels, selected.Layout.Names)
	}
	wrong := *frame.HUD
	wrong.State.Characters[0] = 2
	if got, reason := a.Select(&wrong, read(".idx"), palette, frame.Layers); got != nil || reason != "此角色的高解析介面尚未完成" {
		t.Fatal("unknown character was accepted", reason)
	}
}
