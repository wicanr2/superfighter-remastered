package hd

import (
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestSecondaryMainOriginalColoursGeometryAndRejection(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local secondary main originals not supplied")
	}
	a, e := LoadCharacters(filepath.Join(root, "hd-characters-remaining-effects-v1"), original)
	if e != nil {
		t.Fatal(e)
	}
	if len(a.Manifest.Poses) != 1516 || len(a.Manifest.Atlases) != 74 {
		t.Fatal("asset identity changed")
	}
	dir := filepath.Join(root, "secondary-main-oracle-v2")
	read := func(name string) []byte {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(dir, name))
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	var receipt struct {
		Frames []struct {
			Fixture string `json:"fixture"`
		} `json:"frames"`
	}
	if e := json.Unmarshal(read("receipt.json"), &receipt); e != nil {
		t.Fatal(e)
	}
	seen := map[[2]int]bool{}
	targets := 0
	for _, capture := range receipt.Frames {
		if capture.Fixture == "" {
			continue
		}
		var meta []struct {
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
		stem := capture.Fixture
		if e := json.Unmarshal(read(stem+".layers.json"), &meta); e != nil {
			t.Fatal(e)
		}
		if e := json.Unmarshal(read(stem+".palette.json"), &palette); e != nil {
			t.Fatal(e)
		}
		layers := make([]renderdata.Layer, len(meta))
		for i, m := range meta {
			layers[i] = renderdata.Layer{Background: m.Kind == "background", Indices: read(fmt.Sprintf("%s.layer-%02d.idx", stem, i)), Coverage: read(fmt.Sprintf("%s.layer-%02d.mask", stem, i))}
			if m.Kind != "body" && m.Kind != "effect" {
				continue
			}
			d := m.Draw
			if len(d.Sources) == 0 {
				t.Fatal("missing original source")
			}
			s := d.Sources[0]
			for _, alias := range d.Sources {
				if alias.Player != s.Player || alias.Character != s.Character {
					t.Fatal("ambiguous source owner")
				}
			}
			layers[i].Sprite = &renderdata.Sprite{Effect: m.Kind == "effect", Player: s.Player, Character: s.Character, Slot: s.Slot, X: d.DI % 320, Y: d.DI / 320, Width: d.Width, Height: d.Height, Flags: d.Flags, PaletteBase: d.Palette, TopClip: d.Top, LeftClip: d.Left, RightClip: d.Right, SourceSHA256: d.SHA}
		}
		if !renderdata.Match(layers, read(stem+".idx")) {
			t.Fatal("original layers do not match")
		}
		poses, why := a.Select(layers, palette)
		if poses == nil {
			t.Fatal("normal frame rejected", stem, why)
		}
		n := 0
		for ordinal, l := range layers {
			s := l.Sprite
			if s == nil {
				continue
			}
			selected := poses[n]
			n++
			if s.Effect || s.PaletteBase != uint8(0xd0+s.Player*32) {
				continue
			}
			targets++
			seen[[2]int{s.Character, s.Slot}] = true
			base := a.poses[[3]int{s.Character, s.Slot, 0}]
			view, ok := selected.Image.(*alternateCharacterImage)
			if !ok || view.Image != base.Image || selected.Pose != base.Pose || selected.Bounds != base.Bounds {
				t.Fatal("base art or geometry changed")
			}
			wanted := uint16(0xfc80)
			if s.Character == 4 {
				wanted = 0xfc00
			}
			if view.active != wanted {
				t.Fatal("unused colour entered transfer", view.active, wanted)
			}
			for _, alpha := range []uint8{0, 64, 128, 255} {
				flat := image.NewNRGBA(image.Rect(0, 0, 16, 1))
				probe := *view
				probe.Image = flat
				for i := 1; i < 16; i++ {
					if view.active&(1<<i) == 0 {
						continue
					}
					c := view.base[i]
					flat.SetNRGBA(i, 0, color.NRGBA{R: c[0], G: c[1], B: c[2], A: alpha})
					got := color.NRGBAModel.Convert(probe.At(i, 0)).(color.NRGBA)
					if got.A != alpha {
						t.Fatal("alpha changed")
					}
					if alpha != 0 && [3]uint8{got.R, got.G, got.B} != view.alternate[i] {
						t.Fatal("source anchor not exact", i)
					}
				}
			}
			for _, change := range []func(*renderdata.Sprite){func(v *renderdata.Sprite) { v.SourceSHA256 = "invalid" }, func(v *renderdata.Sprite) { v.X++ }, func(v *renderdata.Sprite) { v.PaletteBase++ }, func(v *renderdata.Sprite) { v.LeftClip++ }, func(v *renderdata.Sprite) { v.Flags ^= 128 }} {
				bad := append([]renderdata.Layer(nil), layers...)
				v := *s
				change(&v)
				bad[ordinal].Sprite = &v
				if got, _ := a.Select(bad, palette); got != nil {
					t.Fatal("invalid secondary main accepted", stem)
				}
			}
			bad := append([]renderdata.Layer(nil), layers...)
			bad[ordinal].Coverage = append([]byte(nil), l.Coverage...)
			bad[ordinal].Coverage[0] ^= 1
			if got, _ := a.Select(bad, palette); got != nil {
				t.Fatal("wrong CPU mask accepted")
			}
			badPalette := palette
			badPalette[int(s.PaletteBase)+1][0] ^= 1
			if got, _ := a.Select(layers, badPalette); got != nil {
				t.Fatal("unknown full palette accepted")
			}
		}
	}
	if !seen[[2]int{3, 48}] || !seen[[2]int{4, 54}] || targets < 2 {
		t.Fatal("missing main sources", seen)
	}
	// 來源已用 RGB 有歧義時不能推測材質；使用真實 packed 來源驗拒絕。
	base := a.poses[[3]int{3, 48, 0}]
	sourcePalette := a.palettes[[2]int{3, 0}]
	sourcePalette[10] = sourcePalette[11]
	unsafe := &Characters{palettes: map[[2]int][16][3]uint8{{3, 0}: sourcePalette, {3, 1}: a.palettes[[2]int{3, 1}]}}
	unsafe.addSecondaryMainPose(base)
	if len(unsafe.secondaryMainPoses) != 0 {
		t.Fatal("ambiguous colours admitted")
	}
	t.Log("saved secondary-main targets", targets, "derived views", len(a.secondaryMainPoses))
}
