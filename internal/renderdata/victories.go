package renderdata

import "image"

func VictoryFigureFile(character int) string {
	names:=[11]string{"AAWIN.FIG","BBWIN.FIG","CCWIN.FIG","EEWIN.FIG","FFWIN.FIG","GGWIN.FIG","HHWIN.FIG","IIWIN.FIG","JJWIN.FIG","DDWIN.FIG","KKWIN.FIG"}
	if character<0 || character>=len(names){return ""};return names[character]
}

type VictoryState struct {
	Counter    uint16    `json:"counter"`
	Round      uint16    `json:"round_index"`
	Winner     uint16    `json:"winner_word"`
	Mode       uint16    `json:"mode"`
	Characters [2]uint16 `json:"characters"`
	Health     [2]uint16 `json:"health"`
	Flags      [2]uint8  `json:"flags_3eb7_3eb8"`
	Rows       uint8     `json:"crtc_rows"`
	Timer      uint16    `json:"timer"`
}

// DrawCount 只描述原版文字分支，不替原版判定勝負。
func (s VictoryState) DrawCount() int {
	if s.Health[0] == s.Health[1] || s.Flags[0] == 4 || s.Flags[1] == 4 {
		return 1
	}
	return 2
}

type VictoryDraw struct {
	Slot         int    `json:"slot"`
	X            int    `json:"x"`
	Y            int    `json:"y"`
	Width        int    `json:"width"`
	Height       int    `json:"height"`
	SourceSI     uint16 `json:"source_si"`
	SourceDS     uint16 `json:"source_ds"`
	Caller       uint16 `json:"caller_ip"`
	Palette      uint8  `json:"palette"`
	SourceSHA256 string `json:"source_sha256"`
	Source       []byte `json:"-"`
}

func (d VictoryDraw) Bounds() (image.Rectangle, bool) {
	if d.Width < 1 || d.Height < 1 || d.Width > 320 || d.Height > 200 || d.X < 0 || d.Y < 0 || d.X > 320 || d.Y > 200 || d.X+d.Width > 320 || d.Y+d.Height > 200 || len(d.Source) != 2+d.Width*d.Height || int(d.Source[0]) != d.Width || int(d.Source[1]) != d.Height {
		return image.Rectangle{}, false
	}
	return image.Rect(d.X, d.Y, d.X+d.Width, d.Y+d.Height), true
}

// Paint 保留原 helper 的低四位透明與 OR BH；只能寫入呼叫者提供的複本。
func (d VictoryDraw) Paint(indices, coverage []byte) bool {
	if _, ok := d.Bounds(); !ok || len(indices) != Pixels || coverage != nil && len(coverage) != Pixels {
		return false
	}
	for y := 0; y < d.Height; y++ {
		for x := 0; x < d.Width; x++ {
			v := d.Source[2+y*d.Width+x]
			if v&15 != 0 {
				at := (d.Y+y)*320 + d.X + x
				indices[at] = v | d.Palette
				if coverage != nil {
					coverage[at] = 1
				}
			}
		}
	}
	return true
}

type VictorySnapshot struct {
	State    VictoryState  `json:"state"`
	Draws    []VictoryDraw `json:"draws"`
	Complete bool          `json:"complete"`
	Underlay Layer         `json:"-"`
}
