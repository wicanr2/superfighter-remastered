package desktop

import (
	"fmt"
	"image"
	"image/color"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/controls"
	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
)

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
