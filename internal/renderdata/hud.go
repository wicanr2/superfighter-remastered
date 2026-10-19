package renderdata

// HUDState 保留規則勝場及本次介面建立時鎖存的顯示勝場。
type HUDState struct {
	Counter     uint16    `json:"counter"`
	Rows        int       `json:"crtc_rows"`
	Health      [2]uint16 `json:"display_health"`
	Pending     [2]uint16 `json:"pending_damage"`
	Timer       uint16    `json:"timer"`
	Wins        [2]uint16 `json:"wins"`
	DisplayWins [2]uint16 `json:"display_wins"`
	Round       uint16    `json:"round_index"`
	RoundState  uint16    `json:"round_state"`
	Characters  [2]uint16 `json:"characters"`
}

type HUDSnapshot struct {
	State        HUDState `json:"state"`
	BitmapSHA256 string   `json:"bitmap_sha256"`
	Complete     bool     `json:"complete"`
	Bitmap       []byte   `json:"-"`
	Underlay     Layer    `json:"-"`
}
