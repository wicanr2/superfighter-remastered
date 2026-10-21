// 049: title art and original menu geometry.
package desktop

import (
	"encoding/binary"
	"fmt"
	"image"
	"image/color"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/text/v2"
	"github.com/hajimehoshi/ebiten/v2/vector"
	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
)

type titleHDPaint struct {
	person    *ebiten.Image
	phases    [8]*ebiten.Image
	cursor    *ebiten.Image
	rgba      []byte
	cursorKey string
}

func loadTitleHD(root string, images map[string]*ebiten.Image, logo image.Image) *titleHDPaint {
	if len(images) != 33 {
		return nil
	}
	phases, e := titleHDPhases(root, logo)
	if e != nil {
		return nil
	}
	return &titleHDPaint{person: images["title-person"], phases: phases, cursor: ebiten.NewImage(320, 200), rgba: make([]byte, 64000*4)}
}

func (g *Game) drawTitleHD(dst *ebiten.Image, state *gamecore.TitleHDState) bool {
	paint := g.titleHDPaint
	if paint == nil || state == nil {
		return false
	}
	physical := func(x, y float64) (float64, float64) {
		return float64(g.paintRect.Min.X) + x*3, float64(g.paintRect.Min.Y) + y*3
	}
	op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
	op.GeoM.Scale(960.0/1586, 600.0/992)
	op.GeoM.Translate(float64(g.paintRect.Min.X), float64(g.paintRect.Min.Y))
	dst.DrawImage(paint.person, op)
	op = &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
	op.GeoM.Scale(855.0/1891, 207.0/468)
	x, y := physical(18, 96)
	op.GeoM.Translate(x, y)
	dst.DrawImage(paint.phases[state.Phase], op)
	labels := [4]string{"單　打", "雙　打", "設　定", "結　束"}
	face := &text.GoTextFace{Source: g.face.Source, Size: 28.8}
	for i, box := range state.Buttons {
		x, y := physical(float64(box[0]), float64(box[1]))
		w, h := float64(box[2]-box[0]+2)*3, float64(box[3]-box[1])*3
		vector.DrawFilledRect(dst, float32(x), float32(y), float32(w), float32(h), color.RGBA{79, 57, 102, 255}, false)
		ink := color.RGBA{187, 155, 216, 255}
		if i == state.Selected {
			ink = color.RGBA{state.Flash[0], state.Flash[1], state.Flash[2], 255}
		}
		vector.StrokeRect(dst, float32(x+1), float32(y+1), float32(w-2), float32(h-2), 2, ink, false)
		width, height := text.Measure(labels[i], face, 0)
		if width > w-8 || height > h {
			return false
		}
		options := &text.DrawOptions{}
		options.GeoM.Translate(x+(w-width)/2, y+(h-height)/2)
		options.ColorScale.ScaleWithColor(color.RGBA{250, 239, 255, 255})
		text.Draw(dst, labels[i], face, options)
	}
	if !state.CursorHidden {
		key := fmt.Sprintf("%d:%v:%v", state.CursorOffset, state.Palette[0], state.Palette[255])
		if key != paint.cursorKey {
			clear(paint.rgba)
			for y := 0; y < 16; y++ {
				black, white := binary.LittleEndian.Uint16(state.Masks[y*2:]), binary.LittleEndian.Uint16(state.Masks[32+y*2:])
				for x := 0; x < 16; x++ {
					position := (int(state.CursorOffset) + y*320 + x) & 65535
					if position >= 64000 {
						continue
					}
					index := -1
					if black&(1<<(15-x)) == 0 {
						index = 0
					}
					if white&(1<<(15-x)) != 0 {
						index = 255
					}
					if index >= 0 {
						rgb := state.Palette[index]
						copy(paint.rgba[position*4:position*4+3], rgb[:])
						paint.rgba[position*4+3] = 255
					}
				}
			}
			paint.cursor.WritePixels(paint.rgba)
			paint.cursorKey = key
		}
		op = &ebiten.DrawImageOptions{}
		op.GeoM.Scale(3, 3)
		op.GeoM.Translate(float64(g.paintRect.Min.X), float64(g.paintRect.Min.Y))
		dst.DrawImage(paint.cursor, op)
	}
	return true
}
