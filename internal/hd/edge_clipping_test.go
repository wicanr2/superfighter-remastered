package hd

import (
	"encoding/json"
	"fmt"
	"image"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestMirroredEdgeClipMatchesOriginalCPULayer(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original edge fixtures not supplied")
	}
	art, err := LoadCharacters(filepath.Join(root, "hd-characters-phoenix-effects-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	for _, tc := range []struct {
		character int
		stem      string
		origin    image.Point
		clip      image.Rectangle
	}{
		{0, "sample-01", image.Pt(249, 21), image.Rect(250, 21, 320, 104)},
		{2, "sample-01", image.Pt(253, 101), image.Rect(262, 101, 320, 183)},
		{3, "sample-02", image.Pt(253, 101), image.Rect(262, 101, 320, 183)},
		{8, "sample-02", image.Pt(253, 101), image.Rect(262, 101, 320, 183)},
	} {
		t.Run(fmt.Sprint(tc.character), func(t *testing.T) {
			read := func(suffix string) []byte {
				t.Helper()
				b, e := os.ReadFile(filepath.Join(root, "hd-motion-coverage-v1", fmt.Sprintf("character-%02d", tc.character), tc.stem+suffix))
				if e != nil {
					t.Fatal(e)
				}
				return b
			}
			var frame struct {
				Layers []renderdata.Layer `json:"layers"`
			}
			var palette [256][3]uint8
			if e := json.Unmarshal(read(".frame.json"), &frame); e != nil {
				t.Fatal(e)
			}
			if e := json.Unmarshal(read(".palette.json"), &palette); e != nil {
				t.Fatal(e)
			}
			target := -1
			for i := range frame.Layers {
				frame.Layers[i].Indices = read(fmt.Sprintf(".layer-%02d.idx", i))
				frame.Layers[i].Coverage = read(fmt.Sprintf(".layer-%02d.mask", i))
				if s := frame.Layers[i].Sprite; s != nil && s.Flags&192 == 192 && s.RightClip > 0 {
					target = i
				}
			}
			if target < 0 {
				t.Fatal("real clipped C0h fixture missing")
			}
			layer := frame.Layers[target]
			s := layer.Sprite
			pose := art.poses[[3]int{s.Character, s.Slot, 0}]
			if pose == nil || !spriteGeometryMatches(s, pose.packed, layer) {
				t.Fatal("original CPU layer no longer matches")
			}
			origin, clip := s.Placement()
			if origin != tc.origin || clip != tc.clip {
				t.Fatal("source-backed placement differs", origin, clip)
			}
			if tc.character != 8 {
				if selected, why := art.Select(frame.Layers, palette); selected == nil {
					t.Fatal("known complete frame rejected", why)
				}
			}
			layer.Coverage = append([]byte(nil), layer.Coverage...)
			layer.Coverage[0] ^= 1
			if spriteGeometryMatches(s, pose.packed, layer) {
				t.Fatal("bad original mask accepted")
			}
			frame.Layers[target] = layer
			if selected, _ := art.Select(frame.Layers, palette); selected != nil {
				t.Fatal("tampered CPU layer allowed partial HD")
			}
		})
	}
}
