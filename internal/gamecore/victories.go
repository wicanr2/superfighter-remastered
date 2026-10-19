package gamecore

import (
	"bytes"
	"crypto/sha256"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type victoryRecording struct {
	enabled, active, failed bool
	sp, drawSP              uint16
	base                    Presentation
	state                   renderdata.VictoryState
	current                 *renderdata.VictoryDraw
	draws                   []renderdata.VictoryDraw
	expected                []byte
}

func cloneRaster(layer renderdata.Layer) renderdata.Layer {
	layer.Indices = append([]byte(nil), layer.Indices...)
	layer.Coverage = append([]byte(nil), layer.Coverage...)
	return layer
}
func cloneLayers(layers []renderdata.Layer) []renderdata.Layer {
	result := make([]renderdata.Layer, len(layers))
	for i, layer := range layers {
		result[i] = cloneRaster(layer)
	}
	return result
}

// EnableVictory 觀測最後介面重建及直接 VRAM 文字，不修改原版狀態。
func (c *Core) EnableVictory() {
	if c.victory.enabled {
		return
	}
	c.victory.enabled = true
	c.o.OnCall(oracle.Far(0x1b9, 0x33f4), c.prepareVictoryHUD)
	c.o.OnCall(oracle.Far(0x1b9, 0x3963), c.beginVictory)
	c.o.OnCall(oracle.Far(0x1b9, 0x3685), c.beginVictoryDraw)
	c.o.OnCall(oracle.Far(0x1b9, 0x36ae), c.endVictoryDraw)
	c.o.OnCall(oracle.Far(0x1b9, 0x3a3f), c.endVictory)
}

func (c *Core) prepareVictoryHUD(o *oracle.Oracle) {
	r := &c.recording
	if o.StackWord(0) != 0x5e77 || !r.enabled || len(r.layers) != 0 || r.cancel != nil {
		return
	}
	ds, ok := c.dataSegment()
	old := c.presentation
	if !ok || !old.LayersComplete || len(old.Layers) < 6 || old.Layers[len(old.Layers)-1].Sprite != nil {
		return
	}
	seg := o.Word(oracle.Far(ds, 0xe))
	if old.Palette != o.Palette() || !bytes.Equal(old.Pixels, o.Bytes(oracle.Far(seg, 0), renderdata.Pixels)) {
		return
	}
	r.layers = cloneLayers(old.Layers)
	r.base = uint32(seg) * 16
	r.reason = ""
	r.backgroundDone = true
	r.pending = [2]bool{}
	r.seen = [2]bool{true, true}
	r.effectReturn = 0
	r.retainedRows = 0
	var err error
	r.cancel, err = o.ObserveWrites(r.base, r.base+renderdata.Pixels-1, func(w oracle.MemoryWrite) {
		last := &r.layers[len(r.layers)-1]
		at := int(w.Address - r.base)
		last.Indices[at] = w.Value
		last.Coverage[at] = 1
	})
	if err != nil {
		r.layers = nil
		r.reason = "勝負介面觀測未對應"
	}
}

func (c *Core) beginVictory(o *oracle.Oracle) {
	v := &c.victory
	if v.active {
		if v.sp != o.SP() {
			v.failed = true
		}
		return
	}
	ds, ok := c.dataSegment()
	if !ok {
		return
	}
	word := func(off uint16) uint16 { return o.Word(oracle.Far(ds, off)) }
	v.active = true
	v.sp = o.SP()
	v.base = c.presentation
	v.current = nil
	v.draws = nil
	v.expected = append([]byte(nil), o.Bytes(oracle.Far(0xa000, 0), renderdata.Pixels)...)
	v.failed = !v.base.LayersComplete || !bytes.Equal(v.base.Pixels, v.expected)
	v.state = renderdata.VictoryState{Counter: word(0x1a), Round: word(0x1318), Winner: word(0x1322), Mode: word(0x18), Characters: [2]uint16{word(0x12ac), word(0x12ae)}, Health: [2]uint16{word(0x169c), word(0x169e)}, Flags: [2]uint8{o.Byte(oracle.Far(ds, 0x3eb7)), o.Byte(oracle.Far(ds, 0x3eb8))}, Rows: o.Byte(oracle.Far(ds, 0x1334)), Timer: word(0x2f26)}
}

func (c *Core) beginVictoryDraw(o *oracle.Oracle) {
	v := &c.victory
	if !v.active || o.ES() != 0xa000 {
		return
	}
	if v.current != nil {
		if v.drawSP != o.SP() {
			v.failed = true
		}
		return
	}
	v.drawSP = o.SP()
	header := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2)
	w, h := int(header[0]), int(header[1])
	slot := -1
	for i := 0; i < 22; i++ {
		if o.Word(oracle.Far(o.DSReg(), uint16(i*2))) == o.SI() {
			slot = i
			break
		}
	}
	if w < 1 || h < 1 || w > 320 || h > 200 || slot < 0 {
		v.failed = true
		return
	}
	source := append([]byte(nil), o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2+w*h)...)
	d := &renderdata.VictoryDraw{Slot: slot, X: int(o.DI()) % 320, Y: int(o.DI()) / 320, Width: w, Height: h, SourceSI: o.SI(), SourceDS: o.DSReg(), Caller: o.StackWord(0), Palette: uint8(o.BX() >> 8), Source: source, SourceSHA256: fmt.Sprintf("%x", sha256.Sum256(source))}
	if _, ok := d.Bounds(); !ok {
		v.failed = true
		return
	}
	v.current = d
}

func (c *Core) endVictoryDraw(o *oracle.Oracle) {
	v := &c.victory
	if !v.active || v.drawSP == 0 || o.SP() != v.drawSP {
		return
	}
	if d := v.current; d != nil {
		if len(v.draws) >= 2 || !d.Paint(v.expected, nil) || !bytes.Equal(v.expected, o.Bytes(oracle.Far(0xa000, 0), renderdata.Pixels)) {
			v.failed = true
		}
		v.draws = append(v.draws, *d)
	}
	v.current = nil
	v.drawSP = 0
	// 部分或未知文字也保留當時真實原貌，不等待 routine 完成才更新。
	c.capturePresentation(o)
	c.publishVictory()
}

func (c *Core) endVictory(o *oracle.Oracle) {
	v := &c.victory
	if !v.active || o.SP() != v.sp {
		return
	}
	c.capturePresentation(o)
	c.publishVictory()
	c.victory = victoryRecording{enabled: true}
}

func (c *Core) publishVictory() {
	v := &c.victory
	frame := c.presentation
	base := v.base
	if !v.failed && v.current == nil && len(v.draws) == v.state.DrawCount() && base.Counter == frame.Counter && base.Scene == frame.Scene && base.CameraX == frame.CameraX && base.Actors == frame.Actors && base.DrawPriority == frame.DrawPriority && base.BackgroundSHA256 == frame.BackgroundSHA256 && base.Palette == frame.Palette && len(base.Layers) >= 6 {
		layers := cloneLayers(base.Layers)
		last := &layers[len(layers)-1]
		underlay := cloneRaster(*last)
		valid := last.Sprite == nil
		for _, d := range v.draws {
			valid = d.Paint(last.Indices, last.Coverage) && valid
		}
		if valid && renderdata.Match(layers, frame.Pixels) {
			frame.Layers = layers
			frame.LayersComplete = true
			frame.LayerError = ""
			frame.HUD = base.HUD
			frame.Shadows = base.Shadows
			frame.RoundMessage = nil
			frame.Victory = &renderdata.VictorySnapshot{State: v.state, Draws: append([]renderdata.VictoryDraw(nil), v.draws...), Complete: true, Underlay: underlay}
			c.presentation = frame
		}
	}
}
