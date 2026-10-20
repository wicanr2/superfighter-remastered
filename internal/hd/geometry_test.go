package hd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestCharacterGeometryMatchesOriginalCPUAndRejectsTampering(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original geometry fixtures not supplied")
	}
	a, err := LoadCharacters(filepath.Join(root, "hd-characters-lan-victory-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	for _, tc := range []struct {
		folder, stem string
		flags        uint8
		top          int
	}{
		{"native-lan-victory-v2", "transition-0.png", 192, 0},
		{"native-kim-v1", "knockout-0.png", 64, 9},
	} {
		t.Run(tc.folder, func(t *testing.T) {
			read := func(suffix string) []byte {
				t.Helper()
				b, e := os.ReadFile(filepath.Join(root, "hd-first-pass-v1", tc.folder, tc.stem+suffix))
				if e != nil {
					t.Fatal(e)
				}
				return b
			}
			var f struct {
				Layers []renderdata.Layer `json:"layers"`
			}
			if e := json.Unmarshal(read(".frame.json"), &f); e != nil {
				t.Fatal(e)
			}
			var palette [256][3]uint8
			if e := json.Unmarshal(read(".palette.json"), &palette); e != nil {
				t.Fatal(e)
			}
			target := -1
			count := 0
			for i := range f.Layers {
				f.Layers[i].Indices = read(fmt.Sprintf(".layer-%02d.idx", i))
				f.Layers[i].Coverage = read(fmt.Sprintf(".layer-%02d.mask", i))
				if s := f.Layers[i].Sprite; s != nil {
					count++
					if s.Player == 1 && s.Flags&192 == tc.flags && s.TopClip == tc.top {
						target = i
					}
				}
			}
			if target < 0 {
				t.Fatal("requested normal geometry missing")
			}
			selected, why := a.Select(f.Layers, palette)
			if len(selected) != count {
				t.Fatal("verified geometry should select complete group", why)
			}
			for _, change := range []struct {
				name  string
				apply func(*renderdata.Layer)
			}{
				{"coverage", func(l *renderdata.Layer) { l.Coverage = append([]byte(nil), l.Coverage...); l.Coverage[0] ^= 1 }},
				{"pixel", func(l *renderdata.Layer) {
					l.Indices = append([]byte(nil), l.Indices...)
					for i, v := range l.Coverage {
						if v != 0 {
							l.Indices[i] ^= 1
							return
						}
					}
				}},
				{"position", func(l *renderdata.Layer) { s := *l.Sprite; s.X += 3; l.Sprite = &s }},
				{"negative clip", func(l *renderdata.Layer) { s := *l.Sprite; s.TopClip = -1; l.Sprite = &s }},
				{"over-height clip", func(l *renderdata.Layer) { s := *l.Sprite; s.TopClip = s.Height + 1; l.Sprite = &s }},
				{"missing CPU layer", func(l *renderdata.Layer) { l.Coverage = nil }},
			} {
				mutated := append([]renderdata.Layer(nil), f.Layers...)
				change.apply(&mutated[target])
				if selected, _ := a.Select(mutated, palette); selected != nil {
					t.Fatal("bad geometry produced partial HD", change.name)
				}
			}
		})
	}
}

func TestCharacterGeometryEmptyClipRequiresEmptyCPUOutput(t *testing.T) {
	s := renderdata.Sprite{Width: 2, Height: 1, TopClip: 1, Flags: 192, PaletteBase: 192}
	layer := renderdata.Layer{Indices: make([]byte, renderdata.Pixels), Coverage: make([]byte, renderdata.Pixels)}
	if !spriteGeometryMatches(&s, []byte{2, 1, 0x12}, layer) {
		t.Fatal("legitimate fully clipped source rejected")
	}
	layer.Coverage[0] = 1
	if spriteGeometryMatches(&s, []byte{2, 1, 0x12}, layer) {
		t.Fatal("unexpected original write accepted")
	}
	layer.Coverage[0] = 0
	if spriteGeometryMatches(&s, nil, layer) {
		t.Fatal("missing original bytes accepted")
	}
	s.TopClip = -1
	if spriteGeometryMatches(&s, []byte{2, 1, 0x12}, layer) {
		t.Fatal("negative clip accepted")
	}
}
