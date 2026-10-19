package hd

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"testing"
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
