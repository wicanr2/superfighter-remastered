package renderdata

import "image"

// Shadow 保存原版 helper 的位置與裁切，不從角色圖片推導影子。
type Shadow struct {
	Player       int    `json:"player"`
	X            int    `json:"x"`
	Y            int    `json:"y"`
	LeftClip     int    `json:"left_clip"`
	RightClip    int    `json:"right_clip"`
	SourceSHA256 string `json:"source_sha256"`
}

type ShadowSnapshot struct {
	Counter  uint16    `json:"counter"`
	CameraX  int       `json:"camera_x"`
	Draws    [2]Shadow `json:"draws"`
	Complete bool      `json:"complete"`
	Underlay Layer     `json:"-"`
}

// Placement 保留原版 16-bit 右界計算及 SUB／SBB 借位；空矩形代表原版跳過。
func (s Shadow) Placement(camera int) (image.Rectangle, bool) {
	if s.Player < 0 || s.Player > 1 || s.Y != 178 || camera < 0 || camera > 159 || s.X < -255 || s.X > 319 || s.LeftClip < 0 || s.LeftClip > 255 || s.RightClip < 0 || s.RightClip > 255 {
		return image.Rectangle{}, false
	}
	left := max(-s.X, 0)
	end := uint16(s.X+camera) + 61
	bound := uint16(camera + 319)
	right := 0
	if end > bound {
		right = int(uint8(end - bound))
	}
	if s.LeftClip != left || s.RightClip != right {
		return image.Rectangle{}, false
	}
	count := uint8(59 - s.LeftClip - s.RightClip)
	if s.LeftClip > 59 {
		count--
	}
	if count&128 != 0 {
		return image.Rectangle{}, true
	}
	if count == 0 || s.LeftClip+int(count) > 59 {
		return image.Rectangle{}, false
	}
	x := max(s.X, 0)
	if x+int(count) > 320 {
		return image.Rectangle{}, false
	}
	return image.Rect(x, 178, x+int(count), 187), true
}
