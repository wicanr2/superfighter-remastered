package hd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestPhoenixEffectsRealSourcesAndAtomicRejection(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original effect fixtures not supplied")
	}
	art, err := LoadCharacters(filepath.Join(root, "hd-characters-phoenix-effects-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	if len(art.Manifest.Poses) != 1485 || len(art.Manifest.Atlases) != 67 {
		t.Fatal("unexpected candidate")
	}
	for _, sample := range []struct {
		stem string
		slot int
	}{{"sample-01", 60}, {"sample-02", 58}} {
		t.Run(fmt.Sprint(sample.slot), func(t *testing.T) {
			read := func(suffix string) []byte {
				t.Helper()
				b, e := os.ReadFile(filepath.Join(root, "phoenix-effects-source-v1", "character-03", sample.stem+suffix))
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
			count := 0
			for i := range frame.Layers {
				frame.Layers[i].Indices = read(fmt.Sprintf(".layer-%02d.idx", i))
				frame.Layers[i].Coverage = read(fmt.Sprintf(".layer-%02d.mask", i))
				if s := frame.Layers[i].Sprite; s != nil {
					count++
					if s.Effect && s.Character == 3 && s.Slot == sample.slot {
						target = i
					}
				}
			}
			if target < 0 {
				t.Fatal("normal effect fixture missing")
			}
			selected, why := art.Select(frame.Layers, palette)
			if len(selected) != count {
				t.Fatal("complete effect group rejected", why)
			}
			for _, change := range []struct {
				name  string
				apply func(*renderdata.Sprite)
			}{
				{"unknown effect", func(s *renderdata.Sprite) { s.Slot = 59 }},
				{"wrong source", func(s *renderdata.Sprite) { s.SourceSHA256 = "invalid" }},
				{"wrong bank", func(s *renderdata.Sprite) { s.PaletteBase = 0xc0 }},
			} {
				layers := append([]renderdata.Layer(nil), frame.Layers...)
				sprite := *layers[target].Sprite
				change.apply(&sprite)
				layers[target].Sprite = &sprite
				if poses, _ := art.Select(layers, palette); poses != nil {
					t.Fatal("invalid effect allowed partial HD", change.name)
				}
			}
			changed := palette
			changed[0xd1][0] ^= 1
			if poses, _ := art.Select(frame.Layers, changed); poses != nil {
				t.Fatal("changed source palette allowed partial HD")
			}
		})
	}
}
