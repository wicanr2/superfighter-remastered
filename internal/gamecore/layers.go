package gamecore

import (
	"bytes"
	"crypto/sha256"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type layerRecording struct {
	enabled        bool
	cancel         func()
	layers         []renderdata.Layer
	pending        [2]bool
	seen           [2]bool
	reason         string
	base           uint32
	backgroundDone bool
	effects        bool
	effectReturn   uint16
	effectSP       uint16
}

// EnableLayers 必須在開始執行前呼叫。模式切換不改觀測或原版狀態。
func (c *Core) EnableLayers() {
	if c.recording.enabled {
		return
	}
	c.recording.enabled = true
	c.o.OnCall(oracle.Far(0x1b9, 0x3de4), c.beginLayers)
	c.o.OnCall(oracle.Far(0x1b9, 0x3e08), func(*oracle.Oracle) {
		r := &c.recording
		if len(r.layers) > 0 && !r.backgroundDone {
			r.backgroundDone = true
			r.layers = append(r.layers, newRaster())
		}
	})
	for _, ip := range []uint16{0x4665, 0x46e8, 0x477e, 0x480a} {
		c.o.OnCall(oracle.Far(0x1b9, ip), c.beginSprite)
	}
	for p, ip := range []uint16{0x42a5, 0x4446} {
		p := p
		c.o.OnCall(oracle.Far(0x1b9, ip), func(*oracle.Oracle) {
			r := &c.recording
			if !r.pending[p] || len(r.layers) == 0 {
				return
			}
			r.pending[p] = false
			r.layers = append(r.layers, newRaster())
		})
	}
	for _, ip := range []uint16{0x4393, 0x45af, 0x4618} {
		c.o.OnCall(oracle.Far(0x1b9, ip), func(o *oracle.Oracle) {
			r := &c.recording
			if !r.effects || r.effectReturn == 0 || r.effectReturn != o.IP().Off || o.SP() != r.effectSP+2 {
				return
			}
			r.effectReturn = 0
			r.layers = append(r.layers, newRaster())
		})
	}
}

// EnableEffects 沿用素材版本 1 的入口；只有版本 2 素材才另開特效分層。
func (c *Core) EnableEffects() { c.EnableLayers(); c.recording.effects = true }
func newRaster() renderdata.Layer {
	return renderdata.Layer{Indices: make([]byte, renderdata.Pixels), Coverage: make([]byte, renderdata.Pixels)}
}
func (c *Core) stopLayers() {
	r := &c.recording
	if r.cancel != nil {
		r.cancel()
		r.cancel = nil
	}
	r.layers = nil
	r.pending = [2]bool{}
	r.seen = [2]bool{}
	r.backgroundDone = false
	r.effectReturn = 0
	c.hud.pending = nil
	c.clearShadows()
}
func (c *Core) beginLayers(o *oracle.Oracle) {
	if !c.recording.enabled {
		return
	}
	c.stopLayers()
	r := &c.recording
	r.reason = ""
	ds, ok := c.dataSegment()
	if !ok {
		r.reason = "尚未取得對戰資料段"
		return
	}
	r.base = uint32(o.Word(oracle.Far(ds, 0x0e))) * 16
	r.layers = []renderdata.Layer{newRaster()}
	r.layers[0].Background = true
	var e error
	r.cancel, e = o.ObserveWrites(r.base, r.base+renderdata.Pixels-1, func(event oracle.MemoryWrite) {
		if len(r.layers) == 0 {
			return
		}
		layer := &r.layers[len(r.layers)-1]
		i := int(event.Address - r.base)
		layer.Indices[i] = event.Value
		layer.Coverage[i] = 1
	})
	if e != nil {
		r.layers = nil
		r.reason = "原版合成緩衝區未對應"
	}
}
func (c *Core) beginSprite(o *oracle.Oracle) {
	r := &c.recording
	if !r.enabled || len(r.layers) == 0 || r.reason != "" {
		return
	}
	ret := o.StackWord(0)
	p := -1
	switch ret {
	case 0x428e, 0x4294, 0x429f, 0x42a5:
		p = 0
	case 0x442f, 0x4435, 0x4440, 0x4446:
		p = 1
	}
	if p < 0 {
		if r.effects && (ret == 0x4393 || ret == 0x45af || ret == 0x4618) {
			c.beginEffect(o)
		}
		return
	}
	if r.pending[p] {
		return
	}
	if r.seen[p] || len(r.layers) >= 38 || !r.backgroundDone {
		r.reason = "角色繪製次序未對應"
		return
	}
	ds, ok := c.dataSegment()
	if !ok {
		r.reason = "角色資料段未對應"
		return
	}
	header := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2)
	w, h := int(header[0]), int(header[1])
	if w == 0 || h == 0 {
		r.reason = "角色來源尺寸錯誤"
		return
	}
	raw := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2+(w+1)/2*h)
	s := &renderdata.Sprite{Player: p, Character: int(o.Word(oracle.Far(ds, uint16(0x12ac+p*2)))), Slot: int(o.Byte(oracle.Far(ds, []uint16{0x16f2, 0x16fa}[p]))), X: int(int16(o.Word(oracle.Far(ds, uint16(0x16d6+p*2))))) - int(o.Word(oracle.Far(ds, 0x1332))), Y: int(int16(o.Word(oracle.Far(ds, uint16(0x16de+p*2))))), Width: w, Height: h, Flags: uint8(o.CX()), PaletteBase: uint8(o.DX() >> 8), TopClip: int(o.DX() & 255), LeftClip: int(o.BX() & 255), RightClip: int(o.BX() >> 8), SourceSHA256: fmt.Sprintf("%x", sha256.Sum256(raw))}
	if uint32(o.ES())*16 != r.base {
		r.reason = "角色目的緩衝區未對應"
		return
	}
	layer := newRaster()
	layer.Sprite = s
	r.layers = append(r.layers, layer)
	r.pending[p] = true
	r.seen[p] = true
}
func (c *Core) finishLayers(frame *Presentation) {
	r := &c.recording
	if !r.enabled {
		return
	}
	if r.cancel != nil {
		r.cancel()
		r.cancel = nil
	}
	if len(r.layers) > 0 {
		if r.reason == "" && r.backgroundDone && r.effectReturn == 0 && (r.effects || len(r.layers) == 6) && renderdata.Match(r.layers, frame.Pixels) {
			frame.Layers = r.layers
			frame.LayersComplete = true
		} else {
			frame.LayerError = r.reason
			if frame.LayerError == "" {
				frame.LayerError = "原版圖層未完整或重組不符"
			}
		}
	} else {
		old := c.presentation
		// IRQ 可重訪完成點；完整內容及定位都相同才沿用原快照。
		if old.LayersComplete && frame.Counter == old.Counter && frame.Scene == old.Scene && frame.CameraX == old.CameraX && frame.DrawPriority == old.DrawPriority && frame.BackgroundSHA256 == old.BackgroundSHA256 && frame.Actors == old.Actors && frame.Palette == old.Palette && bytes.Equal(frame.Pixels, old.Pixels) {
			frame.Layers = old.Layers
			frame.LayersComplete = true
		} else {
			frame.LayerError = "等待完整原版圖層"
		}
	}
	r.layers = nil
}

func (c *Core) beginEffect(o *oracle.Oracle) {
	r := &c.recording
	if r.effectReturn != 0 {
		if r.effectSP != o.SP() || r.effectReturn != o.StackWord(0) {
			r.reason = "特效呼叫次序未對應"
		}
		return
	}
	if !r.backgroundDone || len(r.layers) >= 38 || r.pending[0] || r.pending[1] || uint32(o.ES())*16 != r.base {
		r.reason = "特效合成緩衝區或次序未對應"
		return
	}
	ds, ok := c.dataSegment()
	if !ok {
		r.reason = "特效資料段未對應"
		return
	}
	palette := uint8(o.DX() >> 8)
	player := -1
	if palette == 0xd0 {
		player = 0
	}
	if palette == 0xf0 {
		player = 1
	}
	if player < 0 {
		r.reason = "特效色盤未對應"
		return
	}
	slot := -1
	for i := 0; i < 72; i++ {
		table := uint16(0x1706 + player*0x120 + i*4)
		seg := o.Word(oracle.Far(ds, table)) + o.Word(oracle.Far(ds, uint16(0x132a+player*2)))
		off := o.Word(oracle.Far(ds, table+2))
		if oracle.Far(seg, off).Linear() == oracle.Far(o.DSReg(), o.SI()).Linear() {
			slot = i
			break
		}
	}
	if slot < 0 {
		r.reason = "特效原始圖像指標未對應"
		return
	}
	header := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2)
	w, h := int(header[0]), int(header[1])
	if w == 0 || h == 0 {
		r.reason = "特效來源尺寸錯誤"
		return
	}
	raw := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2+(w+1)/2*h)
	origin := int(o.ES())*16 + int(o.DI()) - int(r.base)
	if origin < 0 || origin >= renderdata.Pixels {
		r.reason = "特效目的位置越界"
		return
	}
	sprite := &renderdata.Sprite{Effect: true, Player: player, Character: int(o.Word(oracle.Far(ds, uint16(0x12ac+player*2)))), Slot: slot,
		X: origin % 320, Y: origin / 320, Width: w, Height: h, Flags: uint8(o.CX()), PaletteBase: palette, TopClip: int(o.DX() & 255), LeftClip: int(o.BX() & 255), RightClip: int(o.BX() >> 8), SourceSHA256: fmt.Sprintf("%x", sha256.Sum256(raw))}
	layer := newRaster()
	layer.Sprite = sprite
	r.layers = append(r.layers, layer)
	r.effectReturn, r.effectSP = o.StackWord(0), o.SP()
}
