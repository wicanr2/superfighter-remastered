package renderdata

import "image"

// RoundSnapshot 保存繪製前的階段；原版在此次繪製後才更新階段。
type RoundSnapshot struct {
	Counter      uint16 `json:"counter"`
	RoundIndex   uint16 `json:"round_index"`
	Stage        uint16 `json:"stage"`
	HalfWidth    uint16 `json:"half_width"`
	Column       int    `json:"column"`
	Width        int    `json:"width"`
	X            int    `json:"x"`
	Y            int    `json:"y"`
	SourceSHA256 string `json:"source_sha256"`
	Complete     bool   `json:"complete"`
	Source       []byte `json:"-"`
	Underlay     Layer  `json:"-"`
}

func (s RoundSnapshot) Window() (image.Rectangle, bool) {
	if s.RoundIndex > 8 || s.Stage > 3 || s.HalfWidth < 4 || s.HalfWidth > 68 || s.HalfWidth%4 != 0 {
		return image.Rectangle{}, false
	}
	column, width := max(0, 48-int(s.HalfWidth)), min(96, int(s.HalfWidth)*2)
	if s.Column != column || s.Width != width || s.X != 112+column || s.Y != 56 {
		return image.Rectangle{}, false
	}
	return image.Rect(s.X, s.Y, s.X+width, s.Y+15), true
}
