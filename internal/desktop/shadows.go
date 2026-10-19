package desktop

import (
	"image"
	"math"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

// drawShadows 在實際 viewport 像素計算柔邊與重疊，不放大原版棋盤點陣。
func (g *Game) drawShadows(dst *ebiten.Image, selected *hd.ShadowSelection) {
	sx, sy := float64(g.paintRect.Dx())/320, float64(g.paintRect.Dy())/200
	width, height := g.paintRect.Dx(), int(9*sy)
	if g.shadowTexture == nil {
		g.shadowTexture = ebiten.NewImageWithOptions(image.Rect(0, 0, width, height), &ebiten.NewImageOptions{Unmanaged: true})
		g.shadowRGBA = make([]byte, width*height*4)
	}
	if g.shadowDraws != selected.Draws || g.shadowCamera != selected.CameraX {
		clear(g.shadowRGBA)
		for player, draw := range selected.Draws {
			clip := selected.Clips[player]
			if clip.Empty() {
				continue
			}
			for y := 0; y < height; y++ {
				v := ((float64(y)+.5)/sy - 4.5) / 4.5
				for x := int(float64(clip.Min.X) * sx); x < int(float64(clip.Max.X)*sx); x++ {
					u := ((float64(x)+.5)/sx - float64(draw.X) - 29.5) / 29.5
					strength := min(1.0, max(0.0, (1-u*u-v*v)*3))
					alpha := uint8(math.Round(128 * strength))
					at := (y*width+x)*4 + 3
					g.shadowRGBA[at] = max(g.shadowRGBA[at], alpha)
				}
			}
		}
		g.shadowTexture.WritePixels(g.shadowRGBA)
		g.shadowDraws, g.shadowCamera = selected.Draws, selected.CameraX
	}
	op := &ebiten.DrawImageOptions{}
	op.GeoM.Translate(float64(g.paintRect.Min.X), float64(g.paintRect.Min.Y)+178*sy)
	strip := dst.SubImage(image.Rect(g.paintRect.Min.X, g.paintRect.Min.Y+int(178*sy), g.paintRect.Max.X, g.paintRect.Min.Y+int(178*sy)+height)).(*ebiten.Image)
	if g.capture && g.opts.Observe != "" {
		g.shadowCaptureBefore = make([]byte, width*height*4)
		strip.ReadPixels(g.shadowCaptureBefore)
	}
	dst.SubImage(g.paintRect).(*ebiten.Image).DrawImage(g.shadowTexture, op)
	if g.capture && g.opts.Observe != "" {
		g.shadowCaptureAfter = make([]byte, width*height*4)
		strip.ReadPixels(g.shadowCaptureAfter)
	}
	g.hdShadowsActive = true
}
