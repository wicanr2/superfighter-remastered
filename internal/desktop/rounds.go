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
	op.GeoM.Scale(float64(g.paintRect.Dx())/320, float64(g.paintRect.Dy())/200)
	op.GeoM.Translate(float64(g.paintRect.Min.X), float64(g.paintRect.Min.Y))
	dst.SubImage(g.paintRect).(*ebiten.Image).DrawImage(g.layerTextures[0], op)
}

func (g *Game) drawRoundMessage(dst *ebiten.Image, s *hd.RoundSelection) {
	texture := g.hudLabel(s.Label)
	sx, sy := float64(g.paintRect.Dx())/320, float64(g.paintRect.Dy())/200
	clip := image.Rect(g.paintRect.Min.X+int(float64(s.Window.Min.X)*sx), g.paintRect.Min.Y+int(float64(s.Window.Min.Y)*sy), g.paintRect.Min.X+int(float64(s.Window.Max.X)*sx), g.paintRect.Min.Y+int(float64(s.Window.Max.Y)*sy)).Intersect(g.paintRect)
	op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
	op.GeoM.Scale(96*sx/float64(texture.Bounds().Dx()), 15*sy/float64(texture.Bounds().Dy()))
	op.GeoM.Translate(float64(g.paintRect.Min.X)+112*sx, float64(g.paintRect.Min.Y)+56*sy)
	if g.capture && g.opts.Observe != "" {
		g.roundCaptureBefore = make([]byte, g.paintRect.Dx()*g.paintRect.Dy()*4)
		g.frameCanvas.SubImage(screenRect).(*ebiten.Image).ReadPixels(g.roundCaptureBefore)
	}
	dst.SubImage(clip).(*ebiten.Image).DrawImage(texture, op)
	if g.capture && g.opts.Observe != "" {
		g.roundCaptureAfter = make([]byte, g.paintRect.Dx()*g.paintRect.Dy()*4)
		g.frameCanvas.SubImage(screenRect).(*ebiten.Image).ReadPixels(g.roundCaptureAfter)
	}
	g.hdRoundsActive = true
}
