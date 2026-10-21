package desktop

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestCompletedSelectionStillRejectsUnknownSources(t *testing.T) {
	root := os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" {
		t.Skip("private original data required")
	}
	b, e := os.ReadFile(filepath.Join(root, "SELMAN.CPM"))
	if e != nil {
		t.Fatal(e)
	}
	w, h, base, palette, e := hd.DecodeCPM(b, 320, 200)
	if e != nil || w != 320 || h != 200 {
		t.Fatal("original selection base", e)
	}
	data, e := os.ReadFile(filepath.Join(root, "BIGFIG.XBB"))
	if e != nil {
		t.Fatal(e)
	}
	g := &Game{selectionHD: &selectionHDAssets{data: data, base: base, palette: palette}}
	makeFrame := func(player, cursor int) *gamecore.SelectionPresentation {
		f := &gamecore.SelectionPresentation{Serial: 1, Steps: 1, Selection: gamecore.Selection{Player: player, Cursor: cursor}, Palette: palette,
			Scanout: &renderdata.Scanout{Width: 320, Height: 200, PitchByte: 320, Indices: append([]byte(nil), base...)}}
		chars := [2]int{8, -1}
		chars[player] = cursor
		for side, c := range chars {
			if c < 0 {
				continue
			}
			r := data[c*8689 : (c+1)*8689]
			bank := 160 + side*32
			for i := 0; i < 32; i++ {
				for k := 0; k < 3; k++ {
					v := r[i*3+k]
					f.Palette[bank+i][k] = v*4 + v/16
				}
			}
			for y := 0; y < 89; y++ {
				for x := 0; x < 89; x++ {
					dx := 11 + x
					if side == 1 {
						dx = 302 - x
					}
					f.Scanout.Indices[(15+y)*320+dx] = r[768+y*89+x] + byte(bank)
				}
			}
		}
		return f
	}
	for _, p := range [][2]int{{0, 0}, {1, 10}} {
		if s := g.matchSelectionHD(makeFrame(p[0], p[1])); s == nil || s.Player != p[0] || s.Cursor != p[1] {
			t.Fatal("valid complete source rejected", p)
		}
	}
	cases := []struct {
		name   string
		change func(*gamecore.SelectionPresentation)
	}{
		{"cursor", func(f *gamecore.SelectionPresentation) { f.Selection.Cursor = 1 }},
		{"palette", func(f *gamecore.SelectionPresentation) { f.Palette[42][0] ^= 255 }},
		{"unknown-pixel", func(f *gamecore.SelectionPresentation) { f.Scanout.Indices[0] ^= 255 }},
		{"partial-portrait", func(f *gamecore.SelectionPresentation) { f.Scanout.Indices[20*320+20] ^= 1 }},
		{"geometry", func(f *gamecore.SelectionPresentation) { f.Scanout.StartByte = 1 }},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			f := makeFrame(0, 0)
			c.change(f)
			if g.matchSelectionHD(f) != nil {
				t.Fatal("unknown complete frame accepted")
			}
		})
	}
	g.selectionHD = nil
	if g.matchSelectionHD(makeFrame(0, 0)) != nil {
		t.Fatal("missing source accepted")
	}
}
