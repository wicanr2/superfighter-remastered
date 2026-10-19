package desktop

import (
	"image"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

// drawRetainedBackground 保留 oracle 線性畫面中未被開場背景覆寫的頂列。
func (g *Game) drawRetainedBackground(dst *ebiten.Image, frame gamecore.Presentation) {
	if frame.RetainedBackgroundRows == 0 {
		return
	}
	rgba := g.layerRGBA[0]
	clear(rgba)
	for i, v := range frame.Layers[0].Indices[:frame.RetainedBackgroundRows*320] {
		c := frame.Palette[v]
		copy(rgba[i*4:i*4+3], c[:])
		rgba[i*4+3] = 255
	}
	g.layerTextures[0].WritePixels(rgba)
	op := &ebiten.DrawImageOptions{}
	op.GeoM.Scale(float64(screenRect.Dx())/320, float64(screenRect.Dy())/200)
	op.GeoM.Translate(float64(screenRect.Min.X), float64(screenRect.Min.Y))
	dst.SubImage(screenRect).(*ebiten.Image).DrawImage(g.layerTextures[0], op)
}

func (g *Game) drawRoundMessage(dst *ebiten.Image, s *hd.RoundSelection) {
	texture := g.hudLabel(s.Label)
	sx, sy := float64(screenRect.Dx())/320, float64(screenRect.Dy())/200
	clip := image.Rect(screenRect.Min.X+int(float64(s.Window.Min.X)*sx), screenRect.Min.Y+int(float64(s.Window.Min.Y)*sy), screenRect.Min.X+int(float64(s.Window.Max.X)*sx), screenRect.Min.Y+int(float64(s.Window.Max.Y)*sy)).Intersect(screenRect)
	op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
	op.GeoM.Scale(96*sx/float64(texture.Bounds().Dx()), 15*sy/float64(texture.Bounds().Dy()))
	op.GeoM.Translate(float64(screenRect.Min.X)+112*sx, float64(screenRect.Min.Y)+56*sy)
	if g.capture && g.opts.Observe != "" {
		g.roundCaptureBefore = make([]byte, screenRect.Dx()*screenRect.Dy()*4)
		dst.SubImage(screenRect).(*ebiten.Image).ReadPixels(g.roundCaptureBefore)
	}
	dst.SubImage(clip).(*ebiten.Image).DrawImage(texture, op)
	if g.capture && g.opts.Observe != "" {
		g.roundCaptureAfter = make([]byte, screenRect.Dx()*screenRect.Dy()*4)
		dst.SubImage(screenRect).(*ebiten.Image).ReadPixels(g.roundCaptureAfter)
	}
	g.hdRoundsActive = true
}
