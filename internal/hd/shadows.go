package hd

import (
	"bytes"
	"image"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

const shadowSourceSHA256 = "a25f777105cc86468c91111152e8ef10dd4911d9b150e3c1a1020e21b7590bf1"

type Shadows struct {
	pixels []byte
	color  [3]uint8
}
type ShadowSelection struct {
	Draws    [2]renderdata.Shadow
	Clips    [2]image.Rectangle
	CameraX  int
	Replace  []byte
	Underlay renderdata.Layer
}

func LoadShadows(root string) (*Shadows, error) {
	b, e := checkedFile(root, "SHADOW.XLP", shadowSourceSHA256, 1000)
	if e != nil {
		return nil, e
	}
	colors, e := checkedFile(root, "BOARD.COL", "33e622fa0d23ed7875b4c33e16a7e2bcc0cda4d849a419bcbe185e1db5456e71", 1000)
	if e != nil {
		return nil, e
	}
	a := &Shadows{pixels: b[2:]}
	for i, v := range colors[21:24] {
		a.color[i] = v<<2 | v>>4
	}
	return a, nil
}

func (a *Shadows) Select(s *renderdata.ShadowSnapshot, layers []renderdata.Layer, palette [256][3]uint8, counter uint16, camera int) (*ShadowSelection, string) {
	if s == nil || !s.Complete || s.Counter != counter || s.CameraX != camera || len(layers) < 6 || !layers[0].Background || layers[1].Sprite != nil || layers[1].Background || s.Underlay.Sprite != nil || s.Underlay.Background || len(layers[1].Indices) != 64000 || len(layers[1].Coverage) != 64000 || len(s.Underlay.Indices) != 64000 || len(s.Underlay.Coverage) != 64000 {
		return nil, "等待完整原版陰影"
	}
	for i, value := range s.Underlay.Coverage {
		if value > 1 || layers[1].Coverage[i] > 1 {
			return nil, "陰影覆蓋資料無效，保留原貌"
		}
	}
	if palette[0xa7] != a.color {
		return nil, "陰影色盤轉換中，保留原貌"
	}
	selection := &ShadowSelection{Draws: s.Draws, CameraX: camera, Replace: make([]byte, 64000), Underlay: s.Underlay}
	indices, coverage := append([]byte(nil), s.Underlay.Indices...), append([]byte(nil), s.Underlay.Coverage...)
	for player, draw := range s.Draws {
		if draw.Player != player || draw.SourceSHA256 != shadowSourceSHA256 {
			return nil, "陰影來源未對應，保留原貌"
		}
		clip, ok := draw.Placement(camera)
		if !ok {
			return nil, "陰影裁切未對應，保留原貌"
		}
		selection.Clips[player] = clip
		for y := clip.Min.Y; y < clip.Max.Y; y++ {
			for x := clip.Min.X; x < clip.Max.X; x++ {
				value := a.pixels[(y-178)*59+draw.LeftClip+x-clip.Min.X]
				if value != 0 {
					at := y*320 + x
					indices[at] = value | 0xa0
					coverage[at] = 1
					selection.Replace[at] = 1
				}
			}
		}
	}
	if !bytes.Equal(indices, layers[1].Indices) || !bytes.Equal(coverage, layers[1].Coverage) {
		return nil, "陰影前後圖層未重組吻合，保留原貌"
	}
	return selection, "HD 陰影"
}
