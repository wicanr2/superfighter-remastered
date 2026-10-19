// Package renderdata 保存只讀完整畫格的圖層，不包含遊戲規則或模擬器。
package renderdata

import "image"

const Pixels = 320 * 200

type Sprite struct {
	Player       int    `json:"player"`
	Character    int    `json:"character"`
	Slot         int    `json:"slot"`
	X            int    `json:"x"`
	Y            int    `json:"y"`
	Width        int    `json:"width"`
	Height       int    `json:"height"`
	Flags        uint8  `json:"flags"`
	PaletteBase  uint8  `json:"palette_base"`
	TopClip      int    `json:"top_clip"`
	LeftClip     int    `json:"left_clip"`
	RightClip    int    `json:"right_clip"`
	SourceSHA256 string `json:"source_sha256"`
}

type Layer struct {
	Background bool    `json:"background,omitempty"`
	Sprite     *Sprite `json:"sprite,omitempty"`
	Indices    []byte  `json:"-"`
	Coverage   []byte  `json:"-"`
}

// Match 先檢查完整原版圖層，才允許替換呈現。
func Match(layers []Layer, pixels []byte) bool {
	if len(pixels) != Pixels || (len(layers) != 5 && len(layers) != 6) || layers[0].Sprite != nil {
		return false
	}
	var players [2]bool
	if len(layers) == 6 && !layers[0].Background {
		return false
	}
	for _, layer := range layers {
		if len(layer.Indices) != Pixels || len(layer.Coverage) != Pixels {
			return false
		}
		if s := layer.Sprite; s != nil {
			if s.Player < 0 || s.Player > 1 || players[s.Player] {
				return false
			}
			players[s.Player] = true
		}
	}
	if !players[0] || !players[1] {
		return false
	}
	for i := 0; i < Pixels; i++ {
		if layers[0].Coverage[i] == 0 {
			return false
		}
		v := layers[0].Indices[i]
		for _, layer := range layers[1:] {
			if layer.Coverage[i] != 0 {
				v = layer.Indices[i]
			}
		}
		if v != pixels[i] {
			return false
		}
	}
	return true
}

// Placement 回傳來源圖像矩形的左上角與原版實際可寫範圍。
// 鏡像的 +1 與成對裁切保留原版 STOSB 的定位，不套一般圖片鏡像假設。
func (s Sprite) Placement() (image.Point, image.Rectangle) {
	l, r := (s.LeftClip+1)/2, (s.RightClip+1)/2
	pairs := (s.Width+1)/2 - l - r
	rows := s.Height - s.TopClip
	if pairs <= 0 || rows <= 0 {
		return image.Point{}, image.Rectangle{}
	}
	x, y := max(s.X, 0), max(s.Y, 0)
	left, top := x-l*2, y-s.TopClip
	clip := image.Rect(x, y, x+pairs*2, y+rows)
	if s.Flags&64 != 0 {
		origin := x + s.Width - s.LeftClip - s.RightClip
		left = origin + r*2 + 1 - s.Width
		clip.Min.X = origin - pairs*2 + 1
		clip.Max.X = origin + 1
	}
	if s.Flags&128 != 0 {
		top = y + rows + 1 - s.Height
		clip.Min.Y = y + 1
		clip.Max.Y = y + rows + 1
	}
	return image.Pt(left, top), clip.Intersect(image.Rect(0, 0, 320, 200))
}
