// Package renderdata 保存只讀完整畫格的圖層，不包含遊戲規則或模擬器。
package renderdata

import "image"

const Pixels = 320 * 200

// Scanout 與原 VRAM 圖層分開保存，避免改變既有來源座標。
type Scanout struct {
	Width     int       `json:"width"`
	Height    int       `json:"height"`
	StartByte int       `json:"start_byte"`
	PitchByte int       `json:"pitch_byte"`
	CRTC      [32]uint8 `json:"crtc"`
	Indices   []byte    `json:"-"`
}

func (s *Scanout) Valid() bool {
	return s != nil && s.Width == 320 && s.Height > 0 && s.Height <= 200 && s.StartByte >= 0 && s.StartByte < 65536 && s.PitchByte >= 320 && s.PitchByte <= 65536 && s.StartByte+(s.Height-1)*s.PitchByte+320 <= 65536 && len(s.Indices) == s.Width*s.Height
}

// Matches 逐點核對同一快照的原 64,000 bytes 與 VRAM 尾端。
func (s *Scanout) Matches(raw, tail []byte) bool {
	if !s.Valid() || len(raw) != Pixels || len(tail) != 65536-Pixels {
		return false
	}
	for y := 0; y < s.Height; y++ {
		for x := 0; x < s.Width; x++ {
			at := s.StartByte + y*s.PitchByte + x
			var v byte
			if at < Pixels {
				v = raw[at]
			} else {
				v = tail[at-Pixels]
			}
			if s.Indices[y*s.Width+x] != v {
				return false
			}
		}
	}
	return true
}

type Sprite struct {
	SourceBank   string `json:"source_bank,omitempty"`
	Effect       bool   `json:"effect,omitempty"`
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
	if len(pixels) != Pixels || (len(layers) != 5 && (len(layers) < 6 || len(layers) > 38 || len(layers)%2 != 0)) || layers[0].Sprite != nil {
		return false
	}
	var players [2]bool
	if len(layers) >= 6 && !layers[0].Background {
		return false
	}
	for index, layer := range layers {
		if len(layer.Indices) != Pixels || len(layer.Coverage) != Pixels {
			return false
		}
		if s := layer.Sprite; s != nil {
			if s.Player < 0 || s.Player > 1 || (!s.Effect && players[s.Player]) {
				return false
			}
			if !s.Effect {
				players[s.Player] = true
			}
		}
		if len(layers) >= 6 && index > 0 && ((index%2 == 0) != (layer.Sprite != nil)) {
			return false
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
		sourcePair := r
		if s.Flags&128 != 0 {
			// 原 sub_1480A 保留 BL 的左裁切；只水平翻轉才改讀右側。
			sourcePair = l
		}
		left = origin + sourcePair*2 + 1 - s.Width
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
