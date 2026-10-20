package desktop

import (
	"fmt"
	"image"
	"image/color"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/inpututil"
	"github.com/wicanr2/superfighter-remastered/internal/controls"
)

func keyCode(name string) ebiten.Key {
	var key ebiten.Key
	if err := key.UnmarshalText([]byte(name)); err != nil {
		panic(err)
	} // 設定已經 controls.Validate 核對。
	return key
}

func (g *Game) keyboardFields() []widget {
	var out []widget
	for p := 0; p < 2; p++ {
		x := 58 + p*530
		for action := range controls.KeyboardActions {
			player, index := p, action
			name := controls.KeyLabel(g.settings.Keyboard[p][action])
			if g.binding && g.bindingPlayer == p && g.bindingAction == action {
				name = "按下新鍵；Esc 取消"
			}
			out = append(out, widget{image.Rect(x+112, 224+action*32, x+474, 252+action*32), name, func(int) {
				g.binding = true
				g.bindingPlayer = player
				g.bindingAction = index
				g.bindingArmed = false
				g.notice = fmt.Sprintf("第 %d 人%s：按新鍵，Delete 清空，Esc 取消。", player+1, controls.KeyboardActions[index])
			}, p*14 + action, false})
		}
	}
	return out
}

func (g *Game) captureBinding() {
	keys := inpututil.AppendPressedKeys(nil)
	if !g.bindingArmed {
		if len(keys) == 0 {
			g.bindingArmed = true
		}
		return
	}
	if inpututil.IsKeyJustPressed(ebiten.KeyEscape) {
		g.binding = false
		g.notice = "已取消，保留原鍵位。"
		return
	}
	name := ""
	found := inpututil.IsKeyJustPressed(ebiten.KeyDelete) || inpututil.IsKeyJustPressed(ebiten.KeyBackspace)
	if !found {
		for _, candidate := range controls.KeyboardKeys() {
			if inpututil.IsKeyJustPressed(keyCode(candidate)) {
				name = candidate
				found = true
				break
			}
		}
	}
	if !found {
		if len(inpututil.AppendJustPressedKeys(nil)) > 0 {
			g.notice = "此鍵為前端保留鍵或不支援，請換一個鍵。"
		}
		return
	}
	if err := g.settings.BindKey(g.bindingPlayer, g.bindingAction, name); err != nil {
		g.notice = err.Error()
		return
	}
	g.binding = false
	g.keyboardArmed = false
	g.keyboardQuick = [2][4]bool{}
	g.save()
}

func (g *Game) drawKeyboardLabels(dst *ebiten.Image) {
	for p := 0; p < 2; p++ {
		x := 58 + p*530
		g.label(dst, image.Rect(x, 186, x+474, 220), fmt.Sprintf("第 %d 人鍵盤", p+1), color.White)
		for i, label := range controls.KeyboardActions {
			g.label(dst, image.Rect(x, 224+i*32, x+106, 252+i*32), label, color.White)
		}
	}
	g.label(dst, image.Rect(58, 718, 1060, 754), "點欄位或按 Enter 後重綁；Delete 清空，Esc 取消。衝突不覆寫。", color.White)
}
