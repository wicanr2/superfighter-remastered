package desktop

import (
	"fmt"
	"image"
	"image/color"
	"math"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/text/v2"
	"github.com/hajimehoshi/ebiten/v2/vector"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

// hudLabel 以實際字圖邊界建立獨立高解析紋理；描邊也包含於安全矩形。
func (g *Game) hudLabel(value string) *ebiten.Image {
	if g.hudLabels == nil {
		g.hudLabels = map[string]*ebiten.Image{}
	}
	if cached := g.hudLabels[value]; cached != nil {
		return cached
	}
	face := &text.GoTextFace{Source: g.face.Source, Size: 64}
	glyphs := text.AppendGlyphs(nil, value, face, nil)
	bounds := image.Rectangle{}
	for _, glyph := range glyphs {
		if glyph.Image == nil {
			continue
		}
		r := image.Rect(int(math.Floor(glyph.X)), int(math.Floor(glyph.Y)), int(math.Ceil(glyph.X))+glyph.Image.Bounds().Dx(), int(math.Ceil(glyph.Y))+glyph.Image.Bounds().Dy())
		bounds = bounds.Union(r)
	}
	texture := ebiten.NewImageWithOptions(image.Rect(0, 0, bounds.Dx()+6, bounds.Dy()+6), &ebiten.NewImageOptions{Unmanaged: true})
	draw := func(dx, dy float64, ink color.Color) {
		for _, glyph := range glyphs {
			if glyph.Image == nil {
				continue
			}
			op := &ebiten.DrawImageOptions{}
			op.GeoM.Translate(glyph.X-float64(bounds.Min.X)+3+dx, glyph.Y-float64(bounds.Min.Y)+3+dy)
			op.ColorScale.ScaleWithColor(ink)
			texture.DrawImage(glyph.Image, op)
		}
	}
	for _, offset := range []image.Point{{-2, 0}, {2, 0}, {0, -2}, {0, 2}, {-1, -1}, {1, -1}, {-1, 1}, {1, 1}} {
		draw(float64(offset.X), float64(offset.Y), color.RGBA{35, 25, 59, 255})
	}
	draw(0, 0, color.RGBA{255, 209, 68, 255})
	g.hudLabels[value] = texture
	return texture
}

// hudWinTexture 用曲線重繪原版的拇指圖示，保留同向輪廓與安全邊界。
func (g *Game) hudWinTexture() *ebiten.Image {
	if g.hudWinMarker != nil {
		return g.hudWinMarker
	}
	texture := ebiten.NewImageWithOptions(image.Rect(0, 0, 120, 144), &ebiten.NewImageOptions{Unmanaged: true})
	var hand vector.Path
	hand.MoveTo(12, 133.2)
	hand.LineTo(12, 62.4)
	hand.QuadTo(12, 54, 24, 54)
	hand.LineTo(40.8, 54)
	hand.QuadTo(46.8, 51.6, 51.6, 39.6)
	hand.LineTo(61.2, 9.6)
	hand.QuadTo(64.8, 2.4, 73.2, 6)
	hand.QuadTo(80.4, 9.6, 79.2, 20.4)
	hand.LineTo(75.6, 46.8)
	hand.LineTo(98.4, 46.8)
	hand.QuadTo(112.8, 46.8, 112.8, 58.8)
	hand.QuadTo(112.8, 66, 106.8, 69.6)
	hand.QuadTo(115.2, 73.2, 112.8, 82.8)
	hand.QuadTo(112.8, 88.8, 108, 92.4)
	hand.QuadTo(114, 98.4, 109.2, 108)
	hand.QuadTo(108, 114, 102, 116.4)
	hand.QuadTo(105.6, 126, 96, 130.8)
	hand.LineTo(68.4, 136.8)
	hand.LineTo(21.6, 136.8)
	hand.QuadTo(12, 136.8, 12, 133.2)
	hand.Close()
	options := func(ink color.Color) *vector.DrawPathOptions {
		op := &vector.DrawPathOptions{AntiAlias: true}
		op.ColorScale.ScaleWithColor(ink)
		return op
	}
	vector.FillPath(texture, &hand, nil, options(color.RGBA{255, 209, 68, 255}))
	vector.StrokePath(texture, &hand, &vector.StrokeOptions{Width: 5.4}, options(color.RGBA{77, 43, 39, 255}))
	var cuff vector.Path
	cuff.MoveTo(17, 61)
	cuff.LineTo(35, 61)
	cuff.LineTo(35, 130)
	cuff.LineTo(17, 130)
	cuff.Close()
	vector.FillPath(texture, &cuff, nil, options(color.RGBA{222, 159, 29, 255}))
	var fingers vector.Path
	fingers.MoveTo(50, 68)
	fingers.QuadTo(77, 62, 106, 70)
	fingers.MoveTo(50, 89)
	fingers.QuadTo(78, 82, 107, 92)
	fingers.MoveTo(50, 110)
	fingers.QuadTo(77, 105, 101, 116)
	vector.StrokePath(texture, &fingers, &vector.StrokeOptions{Width: 3.6}, options(color.RGBA{143, 77, 35, 255}))
	var highlight vector.Path
	highlight.MoveTo(58, 39)
	highlight.LineTo(65, 15)
	highlight.MoveTo(44, 60)
	highlight.QuadTo(62, 54, 86, 54)
	vector.StrokePath(texture, &highlight, &vector.StrokeOptions{Width: 4}, options(color.RGBA{255, 245, 174, 255}))
	g.hudWinMarker = texture
	return texture
}

func (g *Game) drawHUD(dst *ebiten.Image, selected *hd.HUDSelection) {
	sx, sy := float64(screenRect.Dx())/320, float64(screenRect.Dy())/200
	physical := func(rect image.Rectangle) image.Rectangle {
		return image.Rect(screenRect.Min.X+int(float64(rect.Min.X)*sx), screenRect.Min.Y+int(float64(rect.Min.Y+selected.State.Rows)*sy), screenRect.Min.X+int(float64(rect.Max.X)*sx), screenRect.Min.Y+int(float64(rect.Max.Y+selected.State.Rows)*sy))
	}
	fill := func(rect image.Rectangle, ink color.Color) {
		vector.DrawFilledRect(dst, float32(rect.Min.X), float32(rect.Min.Y), float32(rect.Dx()), float32(rect.Dy()), ink, false)
	}
	label := func(rect image.Rectangle, value string) {
		box := physical(rect)
		texture := g.hudLabel(value)
		op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
		op.GeoM.Scale(float64(box.Dx())/float64(texture.Bounds().Dx()), float64(box.Dy())/float64(texture.Bounds().Dy()))
		op.GeoM.Translate(float64(box.Min.X), float64(box.Min.Y))
		dst.DrawImage(texture, op)
	}
	for p := 0; p < 2; p++ {
		fill(physical(selected.Layout.Bars[p]), color.RGBA{255, 245, 199, 255})
		inside := physical(selected.Layout.Interior[p])
		fill(inside, color.RGBA{119, 37, 58, 255})
		remaining := int(float64(inside.Dx()) * float64(selected.State.Health[p]) / 124)
		if p == 0 {
			inside.Min.X = inside.Max.X - remaining
		} else {
			inside.Max.X = inside.Min.X + remaining
		}
		if !inside.Empty() {
			fill(inside, color.RGBA{255, 212, 38, 255})
			top := inside
			top.Max.Y = top.Min.Y + max(1, inside.Dy()/3)
			fill(top, color.RGBA{255, 245, 126, 255})
			bottom := inside
			bottom.Min.Y = bottom.Max.Y - max(1, inside.Dy()/4)
			fill(bottom, color.RGBA{222, 159, 29, 255})
		}
		label(selected.Layout.Players[p], fmt.Sprintf("%dP", p+1))
		name := "JAAN"
		if selected.State.Characters[p] == 4 {
			name = "FRANK"
		}
		label(selected.Layout.Names[p], name)
		for _, marker := range selected.Layout.WinMarkers[p] {
			box := physical(marker)
			texture := g.hudWinTexture()
			op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
			op.GeoM.Scale(float64(box.Dx())/float64(texture.Bounds().Dx()), float64(box.Dy())/float64(texture.Bounds().Dy()))
			op.GeoM.Translate(float64(box.Min.X), float64(box.Min.Y))
			dst.DrawImage(texture, op)
		}
	}
	label(selected.Layout.Timer, fmt.Sprintf("%02d", selected.State.Timer))
	g.hdHUDActive = true
}
