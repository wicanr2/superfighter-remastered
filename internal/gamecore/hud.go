package gamecore

import (
	"bytes"
	"crypto/sha256"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type hudRecording struct {
	enabled bool
	setupDS uint16
	wins    [2]uint16
	pending *renderdata.HUDSnapshot
	sp      uint16
}

// EnableHUD 必須在原版開始執行前呼叫。只觀測，沒有資料寫入。
func (c *Core) EnableHUD() {
	if c.hud.enabled {
		return
	}
	c.EnableLayers()
	c.hud.enabled = true
	c.o.OnCall(oracle.Far(0x1b9, 0x34e6), func(o *oracle.Oracle) {
		ds := o.DSReg()
		if !bytes.Equal(o.Bytes(oracle.Far(ds, 0x3f16), 8), []byte{0x1e, 0x2c, 0x2d, 0x2e, 0x20, 0x12, 0x11, 0x10}) {
			return
		}
		c.hud.setupDS = ds
		c.hud.wins = [2]uint16{o.Word(oracle.Far(ds, 0x131e)), o.Word(oracle.Far(ds, 0x1320))}
	})
	c.o.OnCall(oracle.Far(0x1b9, 0x3faa), func(o *oracle.Oracle) {
		r := &c.recording
		ds, ok := c.dataSegment()
		if !ok || ds != c.hud.setupDS || len(r.layers) == 0 || r.layers[len(r.layers)-1].Sprite != nil || r.reason != "" {
			return
		}
		word := func(off uint16) uint16 { return o.Word(oracle.Far(ds, off)) }
		s := renderdata.HUDState{Counter: word(0x1a), Rows: int(o.Byte(oracle.Far(ds, 0x1334))), Health: [2]uint16{word(0x169c), word(0x169e)}, Pending: [2]uint16{word(0x16a0), word(0x16a2)}, Timer: word(0x2f26), Wins: [2]uint16{word(0x131e), word(0x1320)}, DisplayWins: c.hud.wins, Round: word(0x1318), RoundState: word(0x131a), Characters: [2]uint16{word(0x12ac), word(0x12ae)}}
		bitmap := o.Bytes(oracle.Far(word(0xc)+0x1000, 0x8000), 320*32)
		last := r.layers[len(r.layers)-1]
		c.hud.pending = &renderdata.HUDSnapshot{State: s, Bitmap: bitmap, BitmapSHA256: fmt.Sprintf("%x", sha256.Sum256(bitmap)), Underlay: renderdata.Layer{Indices: append([]byte(nil), last.Indices...), Coverage: append([]byte(nil), last.Coverage...)}}
		c.hud.sp = o.SP()
	})
	c.o.OnCall(oracle.Far(0x1b9, 0x3feb), func(o *oracle.Oracle) {
		if c.hud.pending != nil && o.SP() == c.hud.sp {
			c.hud.pending.Complete = true
		}
	})
}
