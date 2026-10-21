package desktop

import (
	"fmt"
	"image"
	"image/color"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/controls"
	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
)

// selectionPortraitRect 是已定版 HD 頭像與點選的共同邊界。
func selectionPortraitRect(character int) image.Rectangle {
	if character < 0 || character > 10 {
		return image.Rectangle{}
	}
	x, y := 28+33*character, 127
	if character >= 8 {
		x, y = 110+33*(character-8), 164
	}
	return image.Rect(x, y, x+33, y+33)
}

func (g *Game) selectionPortraitAt(point image.Point) (int, bool) {
	if !g.hdEnabled || !g.selectionHDActive || g.panel || g.activeRect.Empty() {
		return 0, false
	}
	s := g.core.Status()
	if s.Paused || s.Selection == nil {
		return 0, false
	}
	for character := 0; character < 11; character++ {
		r := selectionPortraitRect(character)
		physical := image.Rect(g.activeRect.Min.X+r.Min.X*3, g.activeRect.Min.Y+r.Min.Y*3,
			g.activeRect.Min.X+r.Max.X*3, g.activeRect.Min.Y+r.Max.Y*3)
		if point.In(physical) {
			return character, true
		}
	}
	return 0, false
}

func (g *Game) selectionLabel(dst *ebiten.Image, s *gamecore.Selection) {
	value := fmt.Sprintf("第 %d 人選角：左右或點頭像，Enter／手把確認。", s.Player+1)
	if !g.selectionHDActive {
		value = fmt.Sprintf("第 %d 人選角：左右選人，Enter／手把確認。", s.Player+1)
	}
	if s.Target >= 0 {
		value = fmt.Sprintf("第 %d 人選角：正在切換至%s。", s.Player+1, controls.Catalog[s.Target].Name)
	}
	g.label(dst, image.Rect(24, 666, 1096, 698), value, color.White)
}
