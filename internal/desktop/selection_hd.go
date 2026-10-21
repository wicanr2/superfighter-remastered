package desktop

import (
	"bytes"
	"fmt"
	"image"
	"image/color"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/vector"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

type selectionHDAssets struct {
	loaded     bool
	data, base []byte
	palette    [256][3]uint8
	art        map[string]*ebiten.Image
	logo       *ebiten.Image
}
type selectionHDState struct {
	Player         int           `json:"player"`
	Cursor         int           `json:"cursor"`
	Portraits      [2]int        `json:"portraits"`
	OriginalSHA256 string        `json:"original_sha256"`
	Selectors      [][3]int      `json:"-"`
	Palette        [256][3]uint8 `json:"-"`
}

func loadSelectionHD(root string, art map[string]*ebiten.Image, logo image.Image) *selectionHDAssets {
	b, e := hd.ReadArt(root, "BIGFIG.XBB", "4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477", 4<<20)
	if e != nil || len(b) != 11*8689 {
		return nil
	}
	base, e := hd.ReadArt(root, "SELMAN.CPM", "9b40caeee1eff32370a6826e1362087ae1da086237731f06de905d696b6c195a", 4<<20)
	if e != nil {
		return nil
	}
	w, h, indices, palette, e := hd.DecodeCPM(base, 320, 200)
	if e != nil || w != 320 || h != 200 {
		return nil
	}
	if len(art) != 33 || logo == nil {
		return &selectionHDAssets{data: b, base: indices, palette: palette}
	}
	gray := image.NewNRGBA(logo.Bounds())
	for y := gray.Bounds().Min.Y; y < gray.Bounds().Max.Y; y++ {
		for x := gray.Bounds().Min.X; x < gray.Bounds().Max.X; x++ {
			p := color.NRGBAModel.Convert(logo.At(x, y)).(color.NRGBA)
			v := byte((299*uint32(p.R) + 587*uint32(p.G) + 114*uint32(p.B) + 500) / 1000)
			gray.SetNRGBA(x, y, color.NRGBA{v, v, v, byte(float64(p.A) * .48)})
		}
	}
	return &selectionHDAssets{loaded: true, data: b, base: indices, palette: palette, art: art, logo: ebiten.NewImageFromImageWithOptions(gray, &ebiten.NewImageFromImageOptions{Unmanaged: true})}
}

func (g *Game) selectionHDState() *selectionHDState {
	a := g.selectionHD
	if a == nil {
		return nil
	}
	selected := g.core.Status().Selection
	if selected == nil || selected.Player < 0 || selected.Player > 1 {
		return nil
	}
	display := g.core.SelectionDisplay()
	_, palette, e := g.core.LiveDisplay()
	if display == nil || e != nil || !display.Valid() || display.Width != 320 || display.Height != 200 || display.StartByte != 0 || display.PitchByte != 320 {
		return nil
	}
	s := &selectionHDState{Player: selected.Player, Cursor: selected.Cursor, Portraits: [2]int{-1, -1}, OriginalSHA256: resultDigest(display.Indices), Palette: palette}
	for i := 0; i < 160; i++ {
		if palette[i] != a.palette[i] {
			return nil
		}
	}
	expected := append([]byte(nil), a.base...)
	for side := 0; side < 2; side++ {
		bank := 160 + side*32
		for character := 0; character < 11; character++ {
			record := a.data[character*8689 : (character+1)*8689]
			match := true
			for i := 0; i < 32 && match; i++ {
				for k := 0; k < 3; k++ {
					v := record[i*3+k]
					if palette[bank+i][k] != v*4+v/16 {
						match = false
						break
					}
				}
			}
			for y := 0; y < 89 && match; y++ {
				for x := 0; x < 89; x++ {
					dx := 11 + x
					if side == 1 {
						dx = 302 - x
					}
					if display.Indices[(15+y)*320+dx] != record[768+y*89+x]+byte(bank) {
						match = false
						break
					}
				}
			}
			if match {
				if s.Portraits[side] >= 0 {
					return nil
				}
				s.Portraits[side] = character
			}
		}
		if character := s.Portraits[side]; character >= 0 {
			record := a.data[character*8689 : (character+1)*8689]
			for y := 0; y < 89; y++ {
				for x := 0; x < 89; x++ {
					dx := 11 + x
					if side == 1 {
						dx = 302 - x
					}
					expected[(15+y)*320+dx] = record[768+y*89+x] + byte(bank)
				}
			}
		}
	}
	if s.Portraits[s.Player] != s.Cursor || s.Player == 1 && s.Portraits[0] < 0 {
		return nil
	}
	borders := map[int]bool{}
	for column := 0; column < 8; column++ {
		x0, x1 := 28+33*column, 60+33*column
		for y := 150; y <= 182; y++ {
			for x := x0; x <= x1; x++ {
				if x == x0 || x == x1 || y == 150 || y == 182 {
					borders[y*320+x] = true
				}
			}
		}
	}
	for at, v := range display.Indices {
		if borders[at] && (v == 240 || v == 241) {
			s.Selectors = append(s.Selectors, [3]int{at % 320, at / 320, int(v)})
		}
		if v != expected[at] {
			if !borders[at] || (v != 240 && v != 241) {
				return nil
			}
			expected[at] = v
		}
	}
	if !bytes.Equal(expected, display.Indices) {
		return nil
	}
	return s
}

func (g *Game) drawSelectionHD(dst *ebiten.Image, s *selectionHDState) bool {
	a := g.selectionHD
	if a == nil || !a.loaded || s == nil {
		return false
	}
	left, top := float64(g.activeRect.Min.X), float64(g.activeRect.Min.Y)
	box := func(x, y, w, h int, c color.RGBA) {
		vector.DrawFilledRect(dst, float32(left+float64(x*3)), float32(top+float64(y*3)), float32(w*3), float32(h*3), c, false)
	}
	box(0, 0, 320, 200, color.RGBA{79, 79, 79, 255})
	draw := func(im *ebiten.Image, x, y, w, h float64, mirror bool) {
		op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
		sx := w * 3 / float64(im.Bounds().Dx())
		if mirror {
			sx = -sx
			x += w
		}
		op.GeoM.Scale(sx, h*3/float64(im.Bounds().Dy()))
		op.GeoM.Translate(left+x*3, top+y*3)
		dst.DrawImage(im, op)
	}
	draw(a.logo, 16, 70, 275, 67.5, false)
	for side, character := range s.Portraits {
		x := 9
		if side == 1 {
			x = 212
		}
		box(x, 13, 93, 93, color.RGBA{18, 14, 10, 255})
		box(x, 13, 91, 91, color.RGBA{228, 186, 46, 255})
		if character >= 0 {
			draw(a.art[fmt.Sprintf("left-%d", character)], float64(x+2), 15, 89, 89, side == 1)
		} else {
			box(x+2, 15, 89, 89, color.RGBA{185, 0, 0, 255})
		}
	}
	draw(a.art["selection-vs"].SubImage(image.Rect(47, 67, 1547, 930)).(*ebiten.Image), 110, 40, 93, 58, false)
	for i := 0; i < 8; i++ {
		box(28+33*i, 150, 33, 33, color.RGBA{21, 21, 21, 255})
		draw(a.art[fmt.Sprintf("left-%d", i)], float64(29+33*i), 151, 31, 31, false)
	}
	for _, p := range s.Selectors {
		c := s.Palette[p[2]]
		box(p[0], p[1], 1, 1, color.RGBA{c[0], c[1], c[2], 255})
	}
	return true
}
