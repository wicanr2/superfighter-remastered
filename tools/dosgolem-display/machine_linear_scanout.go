package machine

import "fmt"

// LinearScanout 為固定 320 像素鏈結 mode 13h 的唯讀顯示複本。
// 舊 Indexed 仍回線性記憶體；此型別的起點與高度依 CRTC 計算。
// 契約與限制見快打至尊 docs/spec/014-mode13-scanout.md。
type LinearScanout struct {
	Width     int       `json:"width"`
	Height    int       `json:"height"`
	StartByte int       `json:"start_byte"`
	PitchByte int       `json:"pitch_byte"`
	CRTC      [32]uint8 `json:"crtc"`
	Indices   []uint8   `json:"-"`
}

// LinearScanout 只讀鏈結 13h 的線性 64 KiB，不猜測平面、bank 或環繞。
// 這是公開 VGA 契約的有限近似，沒有逐掃描線暫存器鎖存時序。
func (m *Machine) LinearScanout() (LinearScanout, error) {
	if m.VideoMode() != 0x13 || m.planarOn || !m.VGA.chain4() {
		return LinearScanout{}, fmt.Errorf("顯示視窗只支援鏈結 mode 13h")
	}
	c := m.VGA.crtc
	// 27h 是既有 BIOS 模型的水平正規化；此 API 不重定義水平時序。
	if c[1] != 0x27 || c[0x14]&0x60 != 0x40 || c[0x17]&0x8b != 0x83 {
		return LinearScanout{}, fmt.Errorf("顯示視窗的水平或記憶體位址設定未支援")
	}
	if c[8]&0x7f != 0 || c[9]&0x80 != 0 || m.VGA.ac[0x13]&15 != 0 || m.VGA.seq[1]&0x20 != 0 || m.VGA.gc[6]&0x0c > 4 {
		return LinearScanout{}, fmt.Errorf("顯示視窗的平移、掃描或記憶體映射未支援")
	}
	scansPerRow := int(c[9]&31) + 1
	scans := (int(c[0x12]) | int(c[7]&2)<<7 | int(c[7]&0x40)<<3) + 1
	lineCompare := int(c[0x18]) | int(c[7]&0x10)<<4 | int(c[9]&0x40)<<3
	if scans%scansPerRow != 0 || lineCompare < scans-1 {
		return LinearScanout{}, fmt.Errorf("顯示視窗的分割或不完整像素列未支援")
	}
	// FreeVGA：雙字組起點乘四，Offset 的列距為值乘二再乘四。
	start := (int(c[0x0c])<<8 | int(c[0x0d])) * 4
	pitch, height := int(c[0x13])*8, scans/scansPerRow
	if height < 1 || pitch < VideoWidth || start+(height-1)*pitch+VideoWidth > 65536 {
		return LinearScanout{}, fmt.Errorf("顯示視窗超出線性 64 KiB 或列距不足")
	}
	result := LinearScanout{Width: VideoWidth, Height: height, StartByte: start, PitchByte: pitch, CRTC: c, Indices: make([]uint8, VideoWidth*height)}
	for row := 0; row < height; row++ {
		at := int(VideoSeg)*16 + start + row*pitch
		copy(result.Indices[row*VideoWidth:(row+1)*VideoWidth], m.Mem[at:at+VideoWidth])
	}
	return result, nil
}
