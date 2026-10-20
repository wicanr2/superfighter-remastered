package hd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

// 原始 Oracle fixture 獨立於 production 分層，兩側及同角皆保存實際 CPU 寫入。
func TestPrimaryExtraOriginalSourcesAndRejection(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original primary extra fixtures not supplied")
	}
	a, err := LoadCharacters(filepath.Join(root, "hd-characters-kim-effects-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	for _, directory := range []string{"primary-extra-oracle-v2", "primary-extra-p2-oracle-v1", "primary-extra-duplicate-oracle-v1"} {
		t.Run(directory, func(t *testing.T) {
			read := func(suffix string) []byte {
				t.Helper()
				b, e := os.ReadFile(filepath.Join(root, directory, "frame-0114"+suffix))
				if e != nil {
					t.Fatal(e)
				}
				return b
			}
			var metadata []struct {
				Kind string `json:"kind"`
				Draw struct {
					DI      int                                     `json:"destination_di"`
					Width   int                                     `json:"width"`
					Height  int                                     `json:"height"`
					Flags   uint8                                   `json:"flags"`
					Palette uint8                                   `json:"palette_base"`
					Top     int                                     `json:"top_clip"`
					Left    int                                     `json:"left_clip"`
					Right   int                                     `json:"right_clip"`
					SHA     string                                  `json:"source_sha256"`
					Sources []struct{ Player, Character, Slot int } `json:"sources"`
				} `json:"draw"`
			}
			var palette [256][3]uint8
			if e := json.Unmarshal(read(".layers.json"), &metadata); e != nil {
				t.Fatal(e)
			}
			if e := json.Unmarshal(read(".palette.json"), &palette); e != nil {
				t.Fatal(e)
			}
			layers := make([]renderdata.Layer, len(metadata))
			target := -1
			for i, m := range metadata {
				layers[i] = renderdata.Layer{Background: m.Kind == "background", Indices: read(fmt.Sprintf(".layer-%02d.idx", i)), Coverage: read(fmt.Sprintf(".layer-%02d.mask", i))}
				if m.Kind != "body" && m.Kind != "effect" {
					continue
				}
				d := m.Draw
				if len(d.Sources) != 1 {
					t.Fatal("ambiguous original source")
				}
				source := d.Sources[0]
				layers[i].Sprite = &renderdata.Sprite{Effect: m.Kind == "effect", Player: source.Player, Character: source.Character, Slot: source.Slot, X: d.DI % 320, Y: d.DI / 320, Width: d.Width, Height: d.Height, Flags: d.Flags, PaletteBase: d.Palette, TopClip: d.Top, LeftClip: d.Left, RightClip: d.Right, SourceSHA256: d.SHA}
				if m.Kind == "effect" {
					target = i
				}
			}
			if target < 0 || !renderdata.Match(layers, read(".idx")) {
				t.Fatal("incomplete original frame")
			}
			selected, why := a.Select(layers, palette)
			if len(selected) != 3 {
				t.Fatal("primary extra refused", why)
			}
			if selected[2].Pose.Character != 5 || selected[2].Pose.Slot != 35 || selected[2].Pose.PaletteBank != 0 {
				t.Fatal("wrong source bank")
			}
			_, alternate := selected[2].Image.(*alternateCharacterImage)
			if alternate != (directory == "primary-extra-duplicate-oracle-v1") {
				t.Fatal("wrong palette view")
			}
			for _, change := range []struct {
				name  string
				apply func(*renderdata.Sprite)
			}{
				{"source", func(s *renderdata.Sprite) { s.SourceSHA256 = "invalid" }},
				{"slot", func(s *renderdata.Sprite) { s.Slot = 71 }},
				{"owner", func(s *renderdata.Sprite) { s.Player ^= 1 }},
				{"palette bank", func(s *renderdata.Sprite) { s.PaletteBase += 16 }},
				{"unknown palette", func(s *renderdata.Sprite) { s.PaletteBase++ }},
				{"placement", func(s *renderdata.Sprite) { s.X++ }},
				{"clipping", func(s *renderdata.Sprite) { s.LeftClip = 2 }},
				{"flip", func(s *renderdata.Sprite) { s.Flags ^= 128 }},
			} {
				bad := append([]renderdata.Layer(nil), layers...)
				s := *bad[target].Sprite
				change.apply(&s)
				bad[target].Sprite = &s
				if selected, _ := a.Select(bad, palette); selected != nil {
					t.Fatal("invalid primary extra accepted", change.name)
				}
			}
			for _, covered := range []bool{false, true} {
				bad := append([]renderdata.Layer(nil), layers...)
				if covered {
					bad[target].Coverage = append([]byte(nil), bad[target].Coverage...)
					bad[target].Coverage[0] ^= 1
				} else {
					bad[target].Indices = append([]byte(nil), bad[target].Indices...)
					for i, v := range bad[target].Coverage {
						if v != 0 {
							bad[target].Indices[i] ^= 1
							break
						}
					}
				}
				if selected, _ := a.Select(bad, palette); selected != nil {
					t.Fatal("CPU mismatch accepted")
				}
			}
			badPalette := palette
			badPalette[int(layers[target].Sprite.PaletteBase)+1][0] ^= 1
			if selected, _ := a.Select(layers, badPalette); selected != nil {
				t.Fatal("unknown palette colours accepted")
			}
		})
	}
}
