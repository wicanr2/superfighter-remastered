package gamecore

import (
	"crypto/sha256"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type shadowRecording struct {
	enabled, active, header, failed bool
	player                          int
	sp, ret                         uint16
	seen                            [2]bool
	pending                         *renderdata.ShadowSnapshot
}

func (c *Core) clearShadows() {
	enabled := c.shadows.enabled
	c.shadows = shadowRecording{enabled: enabled}
}

// EnableShadows 只記錄已證實 helper 的呼叫與來源，原版圖層保持不變。
func (c *Core) EnableShadows() {
	if c.shadows.enabled {
		return
	}
	c.EnableLayers()
	c.shadows.enabled = true
	c.o.OnCall(oracle.Far(0x1b9, 0x4167), func(o *oracle.Oracle) {
		r := &c.shadows
		layers := c.recording.layers
		if len(layers) != 2 || !c.recording.backgroundDone || layers[1].Sprite != nil || c.recording.reason != "" || r.failed {
			return
		}
		if r.active {
			if r.sp != o.SP() || r.ret != o.StackWord(0) {
				r.failed = true
			}
			return
		}
		ds, ok := c.dataSegment()
		if !ok || o.DSReg() != ds {
			r.failed = true
			return
		}
		ret := o.StackWord(0)
		player := 1
		if ret == 0x4144 {
			player = 0
		} else if ret != 0x5d09 && ret != 0x5dc4 && ret != 0x5e5b {
			r.failed = true
			return
		}
		if r.seen[player] || player == 1 && !r.seen[0] {
			r.failed = true
			return
		}
		camera := int(o.Word(oracle.Far(ds, 0x1332)))
		counter := o.Word(oracle.Far(ds, 0x1a))
		if player == 0 {
			last := layers[1]
			r.pending = &renderdata.ShadowSnapshot{Counter: counter, CameraX: camera, Underlay: renderdata.Layer{Indices: append([]byte(nil), last.Indices...), Coverage: append([]byte(nil), last.Coverage...)}}
		}
		if r.pending == nil || r.pending.Counter != counter || r.pending.CameraX != camera {
			r.failed = true
			return
		}
		r.pending.Draws[player] = renderdata.Shadow{Player: player, X: int(int16(o.AX() - uint16(camera))), Y: 178}
		r.active, r.header, r.player, r.sp, r.ret = true, false, player, o.SP(), ret
	})
	c.o.OnCall(oracle.Far(0x1b9, 0x419c), func(o *oracle.Oracle) {
		r := &c.shadows
		if !r.active || r.header || r.failed || r.pending == nil {
			return
		}
		ds, ok := c.dataSegment()
		if !ok || o.DSReg() != ds || o.SI() != 0x1346 || uint32(o.ES())*16 != c.recording.base {
			r.failed = true
			return
		}
		draw := &r.pending.Draws[r.player]
		if int(o.DI()) != 178*320+max(draw.X, 0) {
			r.failed = true
			return
		}
		draw.LeftClip, draw.RightClip = int(o.BX()&255), int(o.BX()>>8)
		draw.SourceSHA256 = fmt.Sprintf("%x", sha256.Sum256(o.Bytes(oracle.Far(ds, 0x1346), 533)))
		r.header = true
	})
	c.o.OnCall(oracle.Far(0x1b9, 0x41df), func(o *oracle.Oracle) {
		r := &c.shadows
		if !r.active || r.failed || r.pending == nil {
			return
		}
		if !r.header || o.SP() != r.sp {
			r.failed = true
			return
		}
		r.seen[r.player] = true
		r.active = false
		if r.seen[0] && r.seen[1] {
			r.pending.Complete = true
		}
	})
}
