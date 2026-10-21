package desktop

import (
	"encoding/binary"
	"fmt"

	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

// These are source identities, not embedded game bytes. All rasters are built
// from the user's data in memory and are never written to the public art pack.
func buildResultReferences(root string) (resultReferences, error) {
	r := resultReferences{Inputs: map[string]string{
		"SHIN.FIG":    "28659c54fe5ce751c630424c3ef234717debd8aa9fe451eaab1d1e2639670845",
		"BIGFIG.XBB":  "4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477",
		"LOSEFIG.XBB": "b1b1781bc799dca14f3ce0f3b74e451e654bafe88341249a977a34ab909b159c",
		"WC.XBB":      "774f14af079c7148fb05a5db21fdfb17abc0a658c9fcd9a82958166ebaf8b0e0",
		"FLAG.XBB":    "87a5bf27cb516d1e5612252dd0a3dff5f3980c837ea4b96b644ece0257acc6d1",
		"FLAG.FIG":    "64ad397ba0a29808b5e8dc147c456be6c1f26df6d94258a3d2340b0f2a2e51ce",
		"NAME.XBB":    "60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82",
		"SH.XBB":      "852bd5b565dd140c66ccce5c98eeb5dfb209609bacd229e532e2c3fcffdd7191",
		"SF.EXE":      "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300",
	}}
	data := map[string][]byte{}
	for name, hash := range r.Inputs {
		b, e := hd.ReadArt(root, name, hash, 4<<20)
		if e != nil {
			return r, e
		}
		data[name] = b
	}
	w, h, indices, palette, e := hd.DecodeCPM(data["SHIN.FIG"], 320, 200)
	if e != nil {
		return r, e
	}
	if w != 320 || h != 200 {
		return r, fmt.Errorf("原報紙尺寸錯誤")
	}
	r.Paper = sourceRaster(w, h, indices, palette, false).RGB
	_, _, _, flagPalette, e := hd.DecodeCPM(data["FLAG.FIG"], 480, 204)
	if e != nil {
		return r, e
	}
	portrait := func(raw []byte, index int, mirror bool) (resultRaster, error) {
		if len(raw) != 11*8689 || index < 0 || index >= 11 {
			return resultRaster{}, fmt.Errorf("原肖像數量錯誤")
		}
		b := raw[index*8689 : (index+1)*8689]
		var colours [256][3]uint8
		for i := 0; i < 32; i++ {
			for k := 0; k < 3; k++ {
				v := b[i*3+k]
				if v > 63 {
					return resultRaster{}, fmt.Errorf("原肖像色盤錯誤")
				}
				colours[i][k] = v*4 + v/16
			}
		}
		for _, v := range b[768:] {
			if v >= 32 {
				return resultRaster{}, fmt.Errorf("原肖像色號越界")
			}
		}
		return sourceRaster(89, 89, b[768:], colours, mirror), nil
	}
	for _, file := range []string{"BIGFIG.XBB", "LOSEFIG.XBB"} {
		for i := 0; i < 11; i++ {
			p, e := portrait(data[file], i, false)
			if e != nil {
				return r, e
			}
			r.Left = append(r.Left, p)
		}
	}
	for _, file := range []string{"LOSEFIG.XBB", "BIGFIG.XBB"} {
		for i := 0; i < 11; i++ {
			p, e := portrait(data[file], i, true)
			if e != nil {
				return r, e
			}
			r.Right = append(r.Right, p)
		}
	}
	byteSprites := func(b []byte, colours [256][3]uint8, width, height, count int) ([]resultRaster, error) {
		var out []resultRaster
		for pos := 0; pos < len(b); {
			if pos+2 > len(b) {
				return nil, fmt.Errorf("原字圖表頭不足")
			}
			w, h := int(b[pos]), int(b[pos+1])
			end := pos + 2 + w*h
			if w != width || h != height || end > len(b) {
				return nil, fmt.Errorf("原字圖尺寸或界限錯誤")
			}
			out = append(out, sourceRaster(w, h, b[pos+2:end], colours, false))
			pos = end
		}
		if len(out) != count {
			return nil, fmt.Errorf("原字圖數量錯誤")
		}
		return out, nil
	}
	r.Outcomes, e = byteSprites(data["WC.XBB"], palette, 65, 169, 3)
	if e != nil {
		return r, e
	}
	r.Flags, e = byteSprites(data["FLAG.XBB"], flagPalette, 65, 33, 7)
	if e != nil {
		return r, e
	}
	names := data["NAME.XBB"]
	if len(names) < 46 {
		return r, fmt.Errorf("原姓名表不足")
	}
	for i := 0; i < 11; i++ {
		at := int(binary.LittleEndian.Uint16(names[i*2:]))
		if at < 46 || at+2 > len(names) {
			return r, fmt.Errorf("原姓名指標越界")
		}
		w, h := int(names[at]), int(names[at+1])
		end := at + 2 + w*h
		if w < 1 || h != 11 || end > len(names) {
			return r, fmt.Errorf("原姓名尺寸錯誤")
		}
		pixels := make([]byte, w*h)
		for j, v := range names[at+2 : end] {
			if v > 6 {
				return r, fmt.Errorf("原姓名色號錯誤")
			}
			if v != 0 {
				pixels[j] = 1
			}
		}
		var colours [256][3]uint8
		colours[0] = [3]uint8{219, 219, 219}
		r.Names = append(r.Names, sourceRaster(w, h, pixels, colours, false))
	}
	panel := data["SH.XBB"]
	if len(panel) != 7355 || panel[0] != 129 || panel[1] != 57 {
		return r, fmt.Errorf("原繼續面板錯誤")
	}
	r.Continue.Panel = sourceRaster(129, 57, panel[2:], palette, false)
	r.Continue.Indices = append([]byte(nil), panel[2:]...)
	r.Continue.Outlines = [2][4]int{{112, 150, 152, 174}, {168, 150, 208, 174}}
	r.Continue.Erase = palette[32]
	exe := data["SF.EXE"]
	if len(exe) < 0xe862 {
		return r, fmt.Errorf("原程式過短")
	}
	header := int(binary.LittleEndian.Uint16(exe[8:])) * 16
	if header+0xe662 > len(exe) || header+0xac50 > len(exe) {
		return r, fmt.Errorf("原面板資料越界")
	}
	for i, box := range r.Continue.Outlines {
		for j, want := range box {
			if int(binary.LittleEndian.Uint16(exe[header+0xe652+i*8+j*2:])) != want {
				return r, fmt.Errorf("原繼續按鈕不符")
			}
		}
	}
	seen := map[[3]byte]bool{}
	for i := 0; i < 8; i++ {
		var colour [3]byte
		for k := 0; k < 3; k++ {
			v := exe[header+0xac30+i*4+k]
			if v > 63 {
				return r, fmt.Errorf("原脈動色盤錯誤")
			}
			colour[k] = v*4 + v/16
		}
		if !seen[colour] {
			r.Continue.Colours = append(r.Continue.Colours, colour)
			seen[colour] = true
		}
	}
	if len(r.Continue.Colours) != 4 {
		return r, fmt.Errorf("原脈動表數量不符")
	}
	return r, nil
}

func sourceRaster(w, h int, indices []byte, palette [256][3]uint8, mirror bool) resultRaster {
	r := resultRaster{Width: w, Height: h, RGB: make([]byte, w*h*3)}
	for y := 0; y < h; y++ {
		for x := 0; x < w; x++ {
			sourceX := x
			if mirror {
				sourceX = w - 1 - x
			}
			p := palette[indices[y*w+sourceX]]
			copy(r.RGB[(y*w+x)*3:], p[:])
		}
	}
	return r
}
