package desktop

import (
	"image"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

func (g *Game) drawVictory(dst *ebiten.Image, s *hd.VictorySelection) {
	if g.capture && g.opts.Observe != "" {
		g.victoryCaptureBefore = make([]byte, screenRect.Dx()*screenRect.Dy()*4)
		g.frameCanvas.SubImage(screenRect).(*ebiten.Image).ReadPixels(g.victoryCaptureBefore)
	}
	for _, run := range s.Runs {
		box := run.Bounds
		physical := image.Rect(g.paintRect.Min.X+box.Min.X*3, g.paintRect.Min.Y+box.Min.Y*3, g.paintRect.Min.X+box.Max.X*3, g.paintRect.Min.Y+box.Max.Y*3)
		texture := g.hudLabel(run.Label)
		op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
		op.GeoM.Scale(float64(physical.Dx())/float64(texture.Bounds().Dx()), float64(physical.Dy())/float64(texture.Bounds().Dy()))
		op.GeoM.Translate(float64(physical.Min.X), float64(physical.Min.Y))
		dst.SubImage(physical).(*ebiten.Image).DrawImage(texture, op)
	}
	if g.capture && g.opts.Observe != "" {
		g.victoryCaptureAfter = make([]byte, screenRect.Dx()*screenRect.Dy()*4)
		g.frameCanvas.SubImage(screenRect).(*ebiten.Image).ReadPixels(g.victoryCaptureAfter)
	}
	g.hdVictoryActive = true
}
