package gamecore

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/originalaudio"
)

type AudioCue struct {
	Kind         string `json:"kind"`
	SourceSHA256 string `json:"source_sha256,omitempty"`
	Control      uint16 `json:"control,omitempty"`
	Repeats      uint16 `json:"repeats,omitempty"`
	Steps        uint64 `json:"steps"`
}
type audioRecording struct {
	enabled  bool
	sources  map[string]originalaudio.SourceClip
	cues     []AudioCue
	rejected uint64
}

// EnableAudio only observes original calls. It never enables a DOS sound card.
func (c *Core) EnableAudio()           { c.audio.enabled = true }
func (c *Core) DrainAudio() []AudioCue { out := c.audio.cues; c.audio.cues = nil; return out }
func (c *Core) RejectedAudio() uint64  { return c.audio.rejected }
func (c *Core) emitAudio(kind string, seg, off, control, repeats uint16) {
	if !c.audio.enabled {
		return
	}
	event := AudioCue{Kind: kind, Control: control, Repeats: repeats, Steps: c.o.Steps()}
	if kind != "stop-music" {
		head := c.o.Bytes(oracle.Far(seg, off), 32)
		length := 0
		if kind == "music" {
			if !bytes.Equal(head[:4], []byte("MThd")) || binary.BigEndian.Uint32(head[4:]) != 6 || !bytes.Equal(head[14:18], []byte("MTrk")) {
				c.audio.rejected++
				return
			}
			size := binary.BigEndian.Uint32(head[18:])
			if size > 200000 {
				c.audio.rejected++
				return
			}
			length = 22 + int(size)
		} else {
			if !bytes.Equal(head[:17], []byte("Compact PCM File\x1a")) {
				c.audio.rejected++
				return
			}
			length = 32 + int(binary.LittleEndian.Uint16(head[27:]))
		}
		if length < 33 || uint32(seg)*16+uint32(off)+uint32(length) > 0x100000 {
			c.audio.rejected++
			return
		}
		event.SourceSHA256 = fmt.Sprintf("%x", sha256.Sum256(c.o.Bytes(oracle.Far(seg, off), length)))
		source, ok := c.audio.sources[event.SourceSHA256]
		if !ok || source.Kind != kind {
			c.audio.rejected++
			return
		}
	}
	if len(c.audio.cues) >= 128 {
		c.audio.rejected++
		return
	}
	c.audio.cues = append(c.audio.cues, event)
}
func (c *Core) installAudio() {
	c.audio.sources = map[string]originalaudio.SourceClip{}
	for _, clip := range originalaudio.Sources().Clips {
		c.audio.sources[clip.SHA256] = clip
	}
	// Source sub_18318 has already stopped the old song at this instruction.
	c.o.OnCall(oracle.Far(0x01b9, 0x8320), func(o *oracle.Oracle) {
		if !c.audio.enabled {
			return
		}
		r := o.Regs()
		c.emitAudio("music", o.Word(oracle.Far(r.SS, r.BP+8)), o.Word(oracle.Far(r.SS, r.BP+6)), 0, 0)
	})
	c.o.OnCall(oracle.Far(0x01b9, 0x8381), func(o *oracle.Oracle) { c.emitAudio("stop-music", 0, 0, 0, 0) })
	c.o.OnCall(oracle.Far(0x01b9, 0x981e), func(o *oracle.Oracle) {
		if !c.audio.enabled {
			return
		}
		r := o.Regs()
		seg := o.Word(oracle.Far(r.CS, 0x1580+((r.AX>>5)&6)))
		off := o.Word(oracle.Far(seg, (r.AX&63)*2))
		c.emitAudio("voice", seg, off, r.BX, r.CX)
	})
	c.o.OnCall(oracle.Far(0x01b9, 0x9873), func(o *oracle.Oracle) {
		if !c.audio.enabled {
			return
		}
		r := o.Regs()
		c.emitAudio("voice", r.ES, r.DI, r.BX, r.CX)
	})
}
