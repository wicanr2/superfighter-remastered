package hd

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"testing"
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
