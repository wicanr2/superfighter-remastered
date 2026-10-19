package oracle

import (
	"bytes"
	"testing"

	"github.com/wicanr2/dosgolem/internal/machine"
)

func TestLinearScanoutPublicReadOnlyCopy(t *testing.T) {
	m := machine.New()
	m.SetVideoMode(0x13)
	for i := 0; i < 65536; i++ {
		m.Mem[0xa0000+i] = uint8(i / 320)
	}
	for _, pair := range [][2]uint8{{0x12, 0x7f}, {0x0c, 3}, {0x0d, 0xc0}} {
		m.Out8(0x3d4, pair[0])
		m.Out8(0x3d5, pair[1])
	}
	o := &Oracle{m: m}
	raw := o.Indexed()
	steps := o.Steps()
	ports := len(o.PortWrites())
	s, e := o.LinearScanout()
	if e != nil {
		t.Fatal(e)
	}
	if s.Height != 192 || s.Width != 320 || s.StartByte != 3840 || s.Indices[0] != 12 || s.Indices[len(s.Indices)-1] != 203 {
		t.Fatal("wrong public scanout")
	}
	s.Indices[0] = 255
	s.CRTC[0x0d] = 0
	again, e := o.LinearScanout()
	if e != nil || again.Indices[0] != 12 || again.CRTC[0x0d] != 0xc0 {
		t.Fatal("output aliases state")
	}
	w, h, pixels := o.Screen()
	if w != 320 || h != 200 || !bytes.Equal(raw, pixels) || !bytes.Equal(raw, o.Indexed()) || o.Steps() != steps || len(o.PortWrites()) != ports {
		t.Fatal("legacy API or execution changed")
	}
}
