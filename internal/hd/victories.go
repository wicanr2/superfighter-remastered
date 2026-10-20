package hd

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"image"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type Victories struct {
	glyphs  [22]hudGlyph
	offsets [22]uint16
	palette [16][3]uint8
}
type VictoryRun struct {
	Slot   int
	Label  string
	Bounds image.Rectangle
	Caller uint16
}
type VictorySelection struct {
	Runs     []VictoryRun
	Replace  []byte
	Underlay renderdata.Layer
}

func LoadVictories(root string) (*Victories, error) {
	names, e := checkedFile(root, "NAME.XBB", "60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82", 20000)
	if e != nil {
		return nil, e
	}
	palette, e := checkedFile(root, "BOARD.COL", "33e622fa0d23ed7875b4c33e16a7e2bcc0cda4d849a419bcbe185e1db5456e71", 768)
	if e != nil {
		return nil, e
	}
	if len(names) != 17474 || len(palette) != 768 {
		return nil, fmt.Errorf("勝負文字來源尺寸錯誤")
	}
	a := &Victories{}
	for i := range a.glyphs {
		off := binary.LittleEndian.Uint16(names[i*2:])
		at := int(off)
		if at < 46 || at+2 > len(names) {
			return nil, fmt.Errorf("勝負字圖索引越界")
		}
		w, h := int(names[at]), int(names[at+1])
		if w < 1 || h < 1 || at+2+w*h > len(names) {
			return nil, fmt.Errorf("勝負字圖尺寸越界")
		}
		a.offsets[i] = off
		a.glyphs[i] = hudGlyph{w, h, names[at+2 : at+2+w*h]}
	}
	for i := range a.palette {
		for k := 0; k < 3; k++ {
			v := palette[i*3+k]
			if v > 63 {
				return nil, fmt.Errorf("勝負字圖色盤錯誤")
			}
			a.palette[i][k] = v<<2 | v>>4
		}
	}
	return a, nil
}

func (a *Victories) Layout(s renderdata.VictoryState) ([]VictoryRun, bool) {
	if s.Round > 8 || s.Health[0] > 124 || s.Health[1] > 124 || s.Timer > 99 || s.Characters[0] > 10 || s.Characters[1] > 10 {
		return nil, false
	}
	run := func(slot, x int, label string, caller uint16) VictoryRun {
		g := a.glyphs[slot]
		return VictoryRun{slot, label, image.Rect(x, 54, x+g.width, 54+g.height), caller}
	}
	if s.Health[0] == s.Health[1] {
		return []VictoryRun{run(16, 110, "DRAW GAME", 0x3984)}, true
	}
	if s.Flags[0] == 4 || s.Flags[1] == 4 {
		slot, label := 14, "YOU WIN"
		if s.Winner != s.Characters[0] {
			slot, label = 15, "YOU LOSE"
		}
		return []VictoryRun{run(slot, 160-a.glyphs[slot].width/2, label, 0x3a32)}, true
	}
	character := int(s.Winner & 255)
	label := ""
	switch character {
	case 0:
		label = "JAAN"
	case 1:
		label = "SARORKOV"
	case 2:
		label = "BULLET"
	case 3:
		label = "PHO HUANG"
	case 4:
		label = "FRANK"
	case 5:
		label = "ONIMALU"
	case 6:
		label = "LAN"
	case 7:
		label = "KING TAI CHI"
	case 9:
		label = "JOKER"
	case 10:
		label = "INDIAN JOE"
	default:
		return nil, false
	}
	if s.Winner&0x7f00 != 0 || s.Winner&0x8000 == 0 && uint16(character) != s.Characters[0] || s.Winner&0x8000 != 0 && uint16(character) != s.Characters[1] {
		return nil, false
	}
	w := a.glyphs[character].width
	x := 160 - (w+40)/2
	return []VictoryRun{run(character, x, label, 0x39dc), run(17, x+w+9, "WIN", 0x39f9)}, true
}

func (a *Victories) Select(s *renderdata.VictorySnapshot, layers []renderdata.Layer, palette [256][3]uint8, counter uint16) (*VictorySelection, string) {
	if s == nil || !s.Complete || s.State.Counter != counter || len(layers) < 6 || len(s.Underlay.Indices) != 64000 || len(s.Underlay.Coverage) != 64000 {
		return nil, "等待完整勝負文字"
	}
	runs, ok := a.Layout(s.State)
	if !ok || len(runs) != len(s.Draws) {
		return nil, "勝負文字分支未對應"
	}
	for i, p := range a.palette {
		if palette[0xa0+i] != p {
			return nil, "勝負文字色盤未對應"
		}
	}
	last := layers[len(layers)-1]
	if last.Sprite != nil || len(last.Indices) != 64000 || len(last.Coverage) != 64000 {
		return nil, "勝負文字圖層未完整"
	}
	indices, coverage := append([]byte(nil), s.Underlay.Indices...), append([]byte(nil), s.Underlay.Coverage...)
	selection := &VictorySelection{Runs: runs, Replace: make([]byte, 64000), Underlay: s.Underlay}
	for i, d := range s.Draws {
		run := runs[i]
		g := a.glyphs[run.Slot]
		source := append([]byte{byte(g.width), byte(g.height)}, g.pixels...)
		bounds, valid := d.Bounds()
		if !valid || d.Slot != run.Slot || d.SourceSI != a.offsets[run.Slot] || d.Caller != run.Caller || d.Palette != 0xa0 || bounds != run.Bounds || !bytes.Equal(d.Source, source) || d.SourceSHA256 != fmt.Sprintf("%x", sha256.Sum256(source)) {
			return nil, "勝負文字原始來源或位置未對應"
		}
		if !d.Paint(indices, coverage) || !d.Paint(make([]byte, 64000), selection.Replace) {
			return nil, "勝負文字繪製越界"
		}
	}
	for i := range indices {
		if s.Underlay.Coverage[i] > 1 || last.Indices[i] != indices[i] || last.Coverage[i] != coverage[i] {
			return nil, "勝負文字覆蓋未重組吻合"
		}
	}
	return selection, "HD 勝負文字"
}
