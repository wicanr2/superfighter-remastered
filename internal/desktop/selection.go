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

func (g *Game) selectionWidgets(s *gamecore.Selection, paused bool) []widget {
	var out []widget
	for i, c := range controls.Catalog {
		character := i
		x, y := 24+(i%6)*180, 700+(i/6)*40
		label := c.Name
		current := s.Cursor
		if s.Target >= 0 {
			current = s.Target
		}
		if current == i {
			label = "● " + label
		}
		out = append(out, widget{image.Rect(x, y, x+172, y+36), label, func(int) {
			if e := g.core.ChooseCharacter(character); e != nil {
				g.notice = e.Error()
			}
		}, -1, paused})
	}
	out = append(out, widget{image.Rect(924, 740, 1096, 776), "確認選角", func(int) {
		if e := g.core.MenuKey("Return"); e != nil {
			g.notice = e.Error()
		}
	}, -1, paused})
	return out
}

func (g *Game) selectionLabel(dst *ebiten.Image, s *gamecore.Selection) {
	value := fmt.Sprintf("第 %d 人選角：左右或點角色，Enter／手把確認。", s.Player+1)
	if s.Target >= 0 {
		value = fmt.Sprintf("第 %d 人選角：正在切換至%s。", s.Player+1, controls.Catalog[s.Target].Name)
	}
	g.label(dst, image.Rect(24, 666, 1096, 698), value, color.White)
}
