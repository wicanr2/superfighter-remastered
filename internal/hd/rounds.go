package hd

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"image"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type Rounds struct {
	text    [2]hudGlyph
	digits  []byte
	palette [16][3]uint8
}
type RoundSelection struct {
	Label    string
	Window   image.Rectangle
	Replace  []byte
	Underlay renderdata.Layer
}

func LoadRounds(root string) (*Rounds, error) {
	names, e := checkedFile(root, "NAME.XBB", "60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82", 20000)
	if e != nil {
		return nil, e
	}
	digits, e := checkedFile(root, "0-9.XBB", "07a3829bbb7ec794459e83d6f2776c31b00c10fcc7a256871cb5fc16ec295fc9", 2100)
	if e != nil {
		return nil, e
	}
	palette, e := checkedFile(root, "BOARD.COL", "33e622fa0d23ed7875b4c33e16a7e2bcc0cda4d849a419bcbe185e1db5456e71", 768)
	if e != nil {
		return nil, e
	}
	if len(names) != 17474 || len(digits) != 2100 || len(palette) != 768 {
		return nil, fmt.Errorf("開場訊息來源尺寸錯誤")
	}
	a := &Rounds{digits: digits}
	for i := range a.text {
		at := int(binary.LittleEndian.Uint16(names[(12+i)*2:]))
		w, h := int(names[at]), int(names[at+1])
		if at < 46 || at+2+w*h > len(names) || h != 15 || w != []int{78, 96}[i] {
			return nil, fmt.Errorf("開場訊息字圖錯誤")
		}
		a.text[i] = hudGlyph{w, h, names[at+2 : at+2+w*h]}
	}
	for i := range a.palette {
		for k := 0; k < 3; k++ {
			v := palette[i*3+k]
			if v > 63 {
				return nil, fmt.Errorf("開場色盤錯誤")
			}
			a.palette[i][k] = v<<2 | v>>4
		}
	}
	return a, nil
}

func (a *Rounds) Reference(s renderdata.RoundSnapshot) ([]byte, bool) {
	if _, ok := s.Window(); !ok {
		return nil, false
	}
	index := 0
	if s.Stage >= 2 {
		index = 1
	}
	glyph := a.text[index]
	out := make([]byte, 1442)
	out[0], out[1] = 96, 15
	for row := 0; row < 15; row++ {
		copy(out[2+row*96:], glyph.pixels[row*glyph.width:(row+1)*glyph.width])
	}
	if index == 0 {
		for row := 0; row < 15; row++ {
			start := int(s.RoundIndex+1)*210 + row*14
			copy(out[83+row*96:97+row*96], a.digits[start:start+14])
		}
	}
	return out, true
}

func (a *Rounds) Select(s *renderdata.RoundSnapshot, layers []renderdata.Layer, palette [256][3]uint8, counter uint16) (*RoundSelection, string) {
	if s == nil || !s.Complete || s.Counter != counter || len(s.Source) != 1442 || len(s.Underlay.Indices) != 64000 || len(s.Underlay.Coverage) != 64000 || len(layers) < 6 {
		return nil, "等待完整開場訊息"
	}
	window, ok := s.Window()
	if !ok {
		return nil, "開場訊息窗口未對應"
	}
	expected, ok := a.Reference(*s)
	if !ok || !bytes.Equal(expected, s.Source) || fmt.Sprintf("%x", sha256.Sum256(s.Source)) != s.SourceSHA256 {
		return nil, "開場訊息來源未對應"
	}
	for i, c := range a.palette {
		if palette[0xa0+i] != c {
			return nil, "開場訊息色盤未對應"
		}
	}
	last := layers[len(layers)-1]
	if last.Sprite != nil || len(last.Indices) != 64000 || len(last.Coverage) != 64000 {
		return nil, "開場訊息圖層未完整"
	}
	indices, coverage := append([]byte(nil), s.Underlay.Indices...), append([]byte(nil), s.Underlay.Coverage...)
	selection := &RoundSelection{Label: fmt.Sprintf("ROUND %d", s.RoundIndex+1), Window: window, Replace: make([]byte, 64000), Underlay: s.Underlay}
	if s.Stage >= 2 {
		selection.Label = "FIGHT !"
	}
	for row := 0; row < 15; row++ {
		for col := 0; col < s.Width; col++ {
			v := expected[2+row*96+s.Column+col]
			if v != 0 {
				at := (s.Y+row)*320 + s.X + col
				indices[at], coverage[at], selection.Replace[at] = v|0xa0, 1, 1
			}
		}
	}
	if s.Stage == 1 && s.HalfWidth == 4 {
		next := *s
		next.Stage = 2
		fight, _ := a.Reference(next)
		copy(indices, fight)
		for i := range fight {
			coverage[i] = 1
		}
	}
	for i := range indices {
		if s.Underlay.Coverage[i] > 1 || indices[i] != last.Indices[i] || coverage[i] != last.Coverage[i] {
			return nil, "開場訊息覆蓋未重組吻合"
		}
	}
	return selection, "HD 回合開場訊息"
}
