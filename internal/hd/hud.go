package hd

import (
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"image"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type hudGlyph struct {
	width, height int
	pixels        []byte
}
type HUD struct {
	board, digits []byte
	names         [12]hudGlyph
	palette       [16][3]uint8
	players       [2]image.Rectangle
}
type HUDLayout struct {
	Names, Players, Bars, Interior [2]image.Rectangle
	Timer                          image.Rectangle
	WinMarkers                     [2][]image.Rectangle
}
type HUDSelection struct {
	State   renderdata.HUDState
	Layout  HUDLayout
	Replace []byte
	Labels  [2]string
}

func LoadHUD(root string) (*HUD, error) {
	files := map[string][]byte{}
	for name, want := range map[string]string{
		"SF.EXE":    "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300",
		"BOARD.XBB": "a1b789d9187f77c70b28a5dfe782af258f6a84c6260ac4b20e55817e0c00b7ff",
		"NAME.XBB":  "60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82",
		"0-9.XBB":   "07a3829bbb7ec794459e83d6f2776c31b00c10fcc7a256871cb5fc16ec295fc9",
		"BOARD.COL": "33e622fa0d23ed7875b4c33e16a7e2bcc0cda4d849a419bcbe185e1db5456e71",
	} {
		b, e := checkedFile(root, name, want, 80000)
		if e != nil {
			return nil, e
		}
		files[name] = b
	}
	if len(files["BOARD.XBB"]) != 10240 || len(files["0-9.XBB"]) != 2100 || len(files["BOARD.COL"]) != 768 {
		return nil, fmt.Errorf("介面來源尺寸錯誤")
	}
	a := &HUD{board: files["BOARD.XBB"], digits: files["0-9.XBB"]}
	for i, value := range a.board {
		if value == 0 {
			continue
		}
		x, y := i%320, i/320
		if x < 18 {
			a.players[0] = a.players[0].Union(image.Rect(x, y, x+1, y+1))
		}
		if x >= 302 {
			a.players[1] = a.players[1].Union(image.Rect(x, y, x+1, y+1))
		}
	}
	for i := range a.names {
		b := files["NAME.XBB"]
		at := int(binary.LittleEndian.Uint16(b[i*2:]))
		w, h := int(b[at]), int(b[at+1])
		if w < 1 || h < 1 || at < 46 || at+2+w*h > len(b) {
			return nil, fmt.Errorf("介面字圖越界")
		}
		a.names[i] = hudGlyph{w, h, b[at+2 : at+2+w*h]}
	}
	for i := range a.palette {
		for k := 0; k < 3; k++ {
			v := files["BOARD.COL"][i*3+k]
			if v > 63 {
				return nil, fmt.Errorf("介面色盤錯誤")
			}
			a.palette[i][k] = v<<2 | v>>4
		}
	}
	return a, nil
}

func (a *HUD) Reference(s renderdata.HUDState) ([]byte, bool) {
	if s.Rows < 0 || s.Rows+32 > 200 || s.Timer > 99 || s.Round > 8 {
		return nil, false
	}
	for p := 0; p < 2; p++ {
		if s.Characters[p] > 10 || s.Health[p] > 124 || s.Pending[p] > s.Health[p] || s.Wins[p] > 2 || s.DisplayWins[p] > s.Wins[p] {
			return nil, false
		}
	}
	out := append([]byte(nil), a.board...)
	draw := func(pixels []byte, w, h, x, y int) bool {
		if len(pixels) != w*h || x < 0 || x+w > 320 || y < 0 || y+h > 32 {
			return false
		}
		for row := 0; row < h; row++ {
			copy(out[(y+row)*320+x:(y+row)*320+x+w], pixels[row*w:(row+1)*w])
		}
		return true
	}
	for p, character := range s.Characters {
		glyph := a.names[character]
		x := 18
		if p == 1 {
			x = 302 - glyph.width
		}
		if !draw(glyph.pixels, glyph.width, glyph.height, x, 21) {
			return nil, false
		}
		glyph = a.names[11]
		for ordinal := 1; ordinal <= int(s.DisplayWins[p]); ordinal++ {
			x = 6 + ordinal*12
			if p == 1 {
				x = 304 - ordinal*12
			}
			if !draw(glyph.pixels, glyph.width, glyph.height, x, 0) {
				return nil, false
			}
		}
	}
	for p, digit := range []int{int(s.Timer) / 10, int(s.Timer) % 10} {
		if !draw(a.digits[digit*210:(digit+1)*210], 14, 15, 145+p*16, 9) {
			return nil, false
		}
	}
	for y := 13; y < 19; y++ {
		for x := 19; x < 143-int(s.Health[0]); x++ {
			out[y*320+x] = 13
		}
		for x := 177 + int(s.Health[1]); x < 301; x++ {
			out[y*320+x] = 13
		}
	}
	return out, true
}

func (a *HUD) Layout(s renderdata.HUDState) HUDLayout {
	layout := HUDLayout{Names: [2]image.Rectangle{image.Rect(18, 21, 18+a.names[s.Characters[0]].width, 32), image.Rect(302-a.names[s.Characters[1]].width, 21, 302, 32)},
		Players:  a.players,
		Bars:     [2]image.Rectangle{image.Rect(18, 12, 143, 20), image.Rect(177, 12, 302, 20)},
		Interior: [2]image.Rectangle{image.Rect(19, 13, 143, 19), image.Rect(177, 13, 301, 19)}, Timer: image.Rect(145, 9, 175, 24)}
	for player, count := range s.DisplayWins {
		for ordinal := 1; ordinal <= int(count); ordinal++ {
			x := 6 + ordinal*12
			if player == 1 {
				x = 304 - ordinal*12
			}
			layout.WinMarkers[player] = append(layout.WinMarkers[player], image.Rect(x, 0, x+a.names[11].width, a.names[11].height))
		}
	}
	return layout
}

func (a *HUD) Select(s *renderdata.HUDSnapshot, pixels []byte, palette [256][3]uint8, layers []renderdata.Layer) (*HUDSelection, string) {
	if s == nil || !s.Complete || len(s.Bitmap) != 10240 || len(pixels) != 64000 || len(s.Underlay.Indices) != 64000 || len(s.Underlay.Coverage) != 64000 || len(layers) < 6 {
		return nil, "等待完整原版介面"
	}
	expected, ok := a.Reference(s.State)
	if !ok {
		return nil, "介面欄位未對應，保留原貌"
	}
	var labels [2]string
	for player, character := range s.State.Characters {
		switch character {
		case 0:
			labels[player] = "JAAN"
		case 1:
			labels[player] = "SARORKOV"
		case 2:
			labels[player] = "BULLET"
		case 3:
			labels[player] = "PHO HUANG"
		case 4:
			labels[player] = "FRANK"
		case 5:
			labels[player] = "ONIMALU"
		default:
			return nil, "此角色的高解析介面尚未完成"
		}
	}
	if fmt.Sprintf("%x", sha256.Sum256(s.Bitmap)) != s.BitmapSHA256 {
		return nil, "介面來源雜湊不符"
	}
	for i, c := range a.palette {
		if palette[0xa0+i] != c {
			return nil, "介面色盤轉換中，保留原貌"
		}
	}
	last := layers[len(layers)-1]
	if last.Sprite != nil || len(last.Coverage) != 64000 || len(last.Indices) != 64000 {
		return nil, "介面圖層未完成"
	}
	selection := &HUDSelection{State: s.State, Layout: a.Layout(s.State), Replace: make([]byte, 64000), Labels: labels}
	rects := []image.Rectangle{selection.Layout.Timer}
	for p := 0; p < 2; p++ {
		rects = append(rects, selection.Layout.Names[p], selection.Layout.Players[p], selection.Layout.Bars[p])
		rects = append(rects, selection.Layout.WinMarkers[p]...)
	}
	for i, v := range s.Bitmap {
		if (v > 15 && v != 0xad && v != 0xae) || v&15 != expected[i] || (v == 0) != (expected[i] == 0) {
			return nil, "原版介面來源未重組吻合"
		}
		if v == 0 {
			continue
		}
		at := s.State.Rows*320 + i
		if pixels[at] != v|0xa0 || last.Coverage[at] != 1 || last.Indices[at] != v|0xa0 {
			return nil, "原版介面覆蓋未對應"
		}
		for _, rect := range rects {
			if image.Pt(i%320, i/320).In(rect) {
				selection.Replace[at] = 1
				break
			}
		}
	}
	return selection, "HD 角色、特效與介面"
}
