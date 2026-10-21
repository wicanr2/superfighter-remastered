// 049: verified original title lifecycle; HD observes and never changes DOS input.
package gamecore

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wicanr2/dosgolem/oracle"
)

type TitleHDInput struct {
	IP         uint16 `json:"runtime_ip"`
	Buttons    uint16 `json:"buttons"`
	OldButtons uint16 `json:"old_buttons"`
	Steps      uint64 `json:"steps"`
}

type TitleHDState struct {
	Selected       int           `json:"selected"`
	Phase          int           `json:"phase"`
	Flash          [3]uint8      `json:"flash_rgb"`
	CursorHidden   bool          `json:"cursor_hidden"`
	CursorOffset   uint16        `json:"cursor_offset"`
	Buttons        [4][4]int     `json:"button_boxes"`
	OriginalSHA256 string        `json:"original_sha256"`
	Pixels         []byte        `json:"-"`
	Palette        [256][3]uint8 `json:"-"`
	Masks          [64]byte      `json:"-"`
}

type titleHDRecording struct {
	active     bool
	stage      string
	input      TitleHDInput
	base       []byte
	palette    [256][3]uint8
	data       []byte
	signatures map[uint16][]byte
}

func decodeTitleCPM(b []byte) ([]byte, error) {
	if len(b) < 6 {
		return nil, fmt.Errorf("short CPM")
	}
	w, h := int(binary.LittleEndian.Uint16(b)), int(binary.LittleEndian.Uint16(b[2:]))
	if w < 1 || w > 320 || h < 1 || h > 200 || b[4] > 1 {
		return nil, fmt.Errorf("CPM header")
	}
	markerAt := 5
	if b[4] == 1 {
		markerAt = 773
	}
	if len(b) <= markerAt {
		return nil, fmt.Errorf("CPM palette")
	}
	marker, p := b[markerAt], markerAt+1
	out := make([]byte, 0, w*h)
	for p < len(b) {
		v, n := b[p], 1
		p++
		if v == marker {
			if p+2 > len(b) {
				return nil, fmt.Errorf("CPM run")
			}
			n = int(b[p])
			v = b[p+1]
			p += 2
		}
		if n == 0 || len(out)+n > w*h {
			return nil, fmt.Errorf("CPM bound")
		}
		for i := 0; i < n; i++ {
			out = append(out, v)
		}
	}
	if len(out) != w*h {
		return nil, fmt.Errorf("CPM size")
	}
	return out, nil
}

func (c *Core) installTitleHD(root string) {
	rec := &titleHDRecording{signatures: map[uint16][]byte{}}
	c.titleHD = rec
	read := func(name, hash string) []byte {
		b, e := os.ReadFile(filepath.Join(root, name))
		if e != nil || fmt.Sprintf("%x", sha256.Sum256(b)) != hash {
			return nil
		}
		return b
	}
	title := read("TITLE.CPM", "a4790f1da67dbff8eec45c573826b95ee9e9c48ed165f99dfc1cf9176ef03f10")
	overlay := read("SFNAME.CPM", "9268d0093b84b67508ea1e2280ec5707c20b6d31a929bfd736b89e132a1842bc")
	exe := read("SF.EXE", "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300")
	if title == nil || overlay == nil || exe == nil {
		return
	}
	base, e := decodeTitleCPM(title)
	if e != nil || len(base) != 64000 {
		return
	}
	top, e := decodeTitleCPM(overlay)
	if e != nil || len(top) != 285*94 {
		return
	}
	for at, v := range top {
		if v != 0 {
			base[(at/285+96)*320+at%285+18] = v
		}
	}
	rec.base = base
	for i := 0; i < 256; i++ {
		for k := 0; k < 3; k++ {
			v := title[5+i*3+k]
			rec.palette[i][k] = v*4 + v/16
		}
	}
	image := append([]byte(nil), exe[int(binary.LittleEndian.Uint16(exe[8:]))*16:]...)
	count, offset := int(binary.LittleEndian.Uint16(exe[6:])), int(binary.LittleEndian.Uint16(exe[24:]))
	for i := 0; i < count; i++ {
		p := offset + i*4
		at := int(binary.LittleEndian.Uint16(exe[p+2:]))*16 + int(binary.LittleEndian.Uint16(exe[p:]))
		if at+2 > len(image) {
			return
		}
		binary.LittleEndian.PutUint16(image[at:], binary.LittleEndian.Uint16(image[at:])+0x01b9)
	}
	rec.data = append([]byte(nil), image[0xabd0:0xac50]...)
	for _, ip := range []uint16{0x0634, 0x02ca, 0x0417, 0x0d42, 0x0b1f, 0x10e0, 0x037a, 0x0b89} {
		rec.signatures[ip] = append([]byte(nil), image[int(ip):int(ip)+16]...)
	}
	for _, entry := range []struct {
		ip     uint16
		stage  string
		active bool
	}{{0x0634, "loading-title", false}, {0x02ca, "title", true}, {0x0417, "leaving-title", false}, {0x0d42, "loading-settings", false}, {0x0b1f, "settings", false}, {0x10e0, "selection", false}} {
		entry := entry
		c.o.OnCall(oracle.Far(0x01b9, entry.ip), func(*oracle.Oracle) {
			rec.active = false
			if bytes.Equal(c.o.Bytes(oracle.Far(0x01b9, entry.ip), 16), rec.signatures[entry.ip]) {
				rec.active = entry.active
				rec.stage = entry.stage
			}
		})
	}
	for _, ip := range []uint16{0x037a, 0x0b89} {
		ip := ip
		c.o.OnCall(oracle.Far(0x01b9, ip), func(*oracle.Oracle) {
			if bytes.Equal(c.o.Bytes(oracle.Far(0x01b9, ip), 16), rec.signatures[ip]) {
				rec.input = TitleHDInput{IP: ip, Buttons: c.o.BX(), OldButtons: c.o.Word(oracle.Far(0x0bfa, 0x1e)), Steps: c.o.Steps()}
			}
		})
	}
}

func (c *Core) TitleHD() *TitleHDState {
	rec := c.titleHD
	if rec == nil || !rec.active || len(rec.base) != 64000 || len(rec.data) != 128 {
		return nil
	}
	if !bytes.Equal(c.o.Bytes(oracle.Far(0x01b9, 0x02ca), 16), rec.signatures[0x02ca]) {
		return nil
	}
	selected := int(c.o.Word(oracle.Far(0x0bfa, 0x18)))
	if selected < 0 || selected > 3 {
		return nil
	}
	live, palette, e := c.LiveDisplay()
	if e != nil || !live.Valid() || live.Width != 320 || live.Height != 200 || live.StartByte != 0 || live.PitchByte != 320 {
		return nil
	}
	result := &TitleHDState{Selected: selected, Phase: -1, Pixels: append([]byte(nil), live.Indices...), Palette: palette, Flash: palette[51]}
	for i := 0; i < 4; i++ {
		for k := 0; k < 4; k++ {
			result.Buttons[i][k] = int(binary.LittleEndian.Uint16(rec.data[64+i*8+k*2:]))
		}
	}
	expected := append([]byte(nil), rec.base...)
	box := result.Buttons[selected]
	at := box[1]*320 + box[0]
	fill := func(n, step int) {
		for j := 0; j < n; j++ {
			expected[at] = 51
			at += step
		}
	}
	fill(box[2]-box[0]+1, 1)
	for i := 0; i < box[3]-box[1]-1; i++ {
		fill(1, 1)
		at += 319
	}
	fill(box[2]-box[0]+1, -1)
	for i := 0; i < box[3]-box[1]-1; i++ {
		fill(1, -1)
		at -= 319
	}
	result.CursorHidden = c.o.Word(oracle.Far(0x0bfa, 0x648)) != 0
	result.CursorOffset = c.o.Word(oracle.Far(0x0bfa, 0x654))
	copy(result.Masks[:], rec.data[:64])
	if !result.CursorHidden {
		for y := 0; y < 16; y++ {
			black, white := binary.LittleEndian.Uint16(rec.data[y*2:]), binary.LittleEndian.Uint16(rec.data[32+y*2:])
			for x := 0; x < 16; x++ {
				position := (int(result.CursorOffset) + y*320 + x) & 65535
				if position >= 64000 {
					continue
				}
				if black&(1<<(15-x)) == 0 {
					expected[position] = 0
				}
				if white&(1<<(15-x)) != 0 {
					expected[position] = 255
				}
			}
		}
	}
	if !bytes.Equal(expected, result.Pixels) {
		return nil
	}
	for i := 0; i < 256; i++ {
		if i >= 7 && i <= 14 || i == 51 {
			continue
		}
		if palette[i] != rec.palette[i] {
			return nil
		}
	}
	for phase := 0; phase < 8; phase++ {
		match := true
		for i := 0; i < 8; i++ {
			if palette[7+i] != rec.palette[7+(i+phase)%8] {
				match = false
			}
		}
		if match {
			result.Phase = phase
			break
		}
	}
	if result.Phase < 0 {
		return nil
	}
	flashKnown := false
	for i := 0; i < 8; i++ {
		var rgb [3]uint8
		for k := 0; k < 3; k++ {
			v := rec.data[96+i*4+k]
			rgb[k] = v*4 + v/16
		}
		if rgb == result.Flash {
			flashKnown = true
		}
	}
	if !flashKnown {
		return nil
	}
	result.OriginalSHA256 = fmt.Sprintf("%x", sha256.Sum256(result.Pixels))
	return result
}
