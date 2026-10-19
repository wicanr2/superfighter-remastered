package gamecore

import (
	"crypto/sha256"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type roundRecording struct {
	enabled bool
	pending *renderdata.RoundSnapshot
	sp      uint16
	bgSP    uint16
}

// EnableRounds 只觀測原版開場拷貝與訊息；不改寫任何遊戲狀態。
func (c *Core) EnableRounds() {
	if c.rounds.enabled {
		return
	}
	c.EnableLayers()
	c.rounds.enabled = true
	c.o.OnCall(oracle.Far(0x1b9, 0x3e09), func(o *oracle.Oracle) {
		r := &c.recording
		if len(r.layers) > 0 && r.retainedRows > 0 && !r.backgroundDone && c.rounds.bgSP == o.SP() {
			return
		}
		ds, ok := c.dataSegment()
		if !ok {
			return
		}
		rows := int(o.Byte(oracle.Far(ds, 0x1334)))
		c.beginLayers(o)
		if rows != 12 || len(r.layers) != 1 {
			r.reason = "開場背景保留列尚未驗證"
			return
		}
		r.retainedRows = rows
		c.rounds.bgSP = o.SP()
		// 頂列是此次背景拷貝前的基底，並非本次寫入事件。
		copy(r.layers[0].Indices, o.Bytes(oracle.Far(o.Word(oracle.Far(ds, 0xe)), 0), rows*320))
		for i := 0; i < rows*320; i++ {
			r.layers[0].Coverage[i] = 1
		}
	})
	c.o.OnCall(oracle.Far(0x1b9, 0x3e43), func(o *oracle.Oracle) {
		r := &c.recording
		if r.retainedRows == 12 && len(r.layers) == 1 && !r.backgroundDone && c.rounds.bgSP == o.SP() && r.reason == "" {
			r.backgroundDone = true
			r.layers = append(r.layers, newRaster())
		}
	})
	c.o.OnCall(oracle.Far(0x1b9, 0x3635), func(o *oracle.Oracle) {
		r := &c.recording
		if r.retainedRows != 12 || !r.backgroundDone || len(r.layers) < 6 || r.reason != "" || o.StackWord(0) != 0x3599 {
			return
		}
		if c.rounds.pending != nil {
			return
		}
		ds, ok := c.dataSegment()
		if !ok || uint32(o.ES())*16 != r.base || o.DSReg() != o.ES() {
			return
		}
		last := r.layers[len(r.layers)-1]
		if last.Sprite != nil {
			return
		}
		word := func(off uint16) uint16 { return o.Word(oracle.Far(ds, off)) }
		source := o.Bytes(oracle.Far(o.DSReg(), 0), 1442)
		c.rounds.pending = &renderdata.RoundSnapshot{Counter: word(0x1a), RoundIndex: word(0x1318), Stage: word(0x131a), HalfWidth: word(0x131c), Column: int(o.SI()), Width: int(o.CX()), X: int(o.DI()) % 320, Y: int(o.DI()) / 320, Source: source, SourceSHA256: fmt.Sprintf("%x", sha256.Sum256(source)), Underlay: renderdata.Layer{Indices: append([]byte(nil), last.Indices...), Coverage: append([]byte(nil), last.Coverage...)}}
		c.rounds.sp = o.SP()
	})
	c.o.OnCall(oracle.Far(0x1b9, 0x3634), func(o *oracle.Oracle) {
		if s := c.rounds.pending; s != nil && o.SP() == c.rounds.sp+4 {
			s.Complete = true
		}
	})
}
