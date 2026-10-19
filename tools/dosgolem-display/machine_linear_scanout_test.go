package machine

import (
	"bytes"
	"reflect"
	"testing"
)

func scanoutMachine() *Machine {
	m := New()
	m.SetVideoMode(0x13)
	for i := 0; i < 65536; i++ {
		m.Mem[int(VideoSeg)*16+i] = uint8(i*17 + i/256)
	}
	return m
}

func TestLinearScanoutStartPitchHeightAndLegacy(t *testing.T) {
	m := scanoutMachine()
	legacy := m.Indexed()
	base, e := m.LinearScanout()
	if e != nil {
		t.Fatal(e)
	}
	if base.Width != 320 || base.Height != 200 || base.StartByte != 0 || base.PitchByte != 320 || !bytes.Equal(base.Indices, legacy) {
		t.Fatal("BIOS profile does not match legacy at zero start")
	}
	crtcReg(m, 0x12, 0x7f)
	setDisplayStart(m, 960)
	before := append([]byte(nil), m.Mem...)
	regs := *m.CPU
	steps := m.Steps
	ports := len(m.PortLog)
	c := m.VGA.crtc
	selected := m.VGA.crtcIdx
	out, e := m.LinearScanout()
	if e != nil {
		t.Fatal(e)
	}
	if out.Width != 320 || out.Height != 192 || out.StartByte != 3840 || out.PitchByte != 320 {
		t.Fatal("wrong actual display geometry", out)
	}
	for row := 0; row < 192; row++ {
		expected := before[int(VideoSeg)*16+3840+row*320 : int(VideoSeg)*16+3840+(row+1)*320]
		if !bytes.Equal(out.Indices[row*320:(row+1)*320], expected) {
			t.Fatal("row differs", row)
		}
	}
	if !bytes.Equal(before, m.Mem) || !reflect.DeepEqual(regs, *m.CPU) || steps != m.Steps || ports != len(m.PortLog) || c != m.VGA.crtc || selected != m.VGA.crtcIdx {
		t.Fatal("read-only output changed machine")
	}
	if !bytes.Equal(legacy, m.Indexed()) {
		t.Fatal("legacy API changed")
	}
	out.Indices[0] ^= 1
	out.CRTC[0] ^= 1
	again, e := m.LinearScanout()
	if e != nil || again.Indices[0] != before[int(VideoSeg)*16+3840] || again.CRTC != c {
		t.Fatal("returned output aliases machine")
	}
	crtcReg(m, 0x13, 48)
	crtcReg(m, 0x12, 0x7f)
	crtcReg(m, 0x07, 0x1d)
	setDisplayStart(m, 1)
	// VDE=127、每列兩條掃描線，64 列；列距改為 384，起點為 4。
	wide, e := m.LinearScanout()
	if e != nil {
		t.Fatal(e)
	}
	if wide.Height != 64 || wide.PitchByte != 384 || wide.StartByte != 4 || wide.Indices[320] != before[int(VideoSeg)*16+388] {
		t.Fatal("pitch/start not applied")
	}
}

func TestLinearScanoutRejectsUnsupportedMappings(t *testing.T) {
	cases := map[string]func(*Machine){
		"mode":                 func(m *Machine) { m.SetVideoMode(0x12) },
		"unchained":            func(m *Machine) { m.Out8(0x3c4, 4); m.Out8(0x3c5, 4) },
		"horizontal":           func(m *Machine) { crtcReg(m, 1, 0x4f) },
		"non-dword":            func(m *Machine) { crtcReg(m, 0x14, 0) },
		"clock-div4":           func(m *Machine) { crtcReg(m, 0x14, 0x60) },
		"row-map":              func(m *Machine) { crtcReg(m, 0x17, 0xa0) },
		"preset-pan":           func(m *Machine) { crtcReg(m, 8, 1) },
		"byte-pan":             func(m *Machine) { crtcReg(m, 8, 0x20) },
		"double-scan":          func(m *Machine) { crtcReg(m, 9, 0xc1) },
		"horizontal-pan":       func(m *Machine) { m.VGA.ac[0x13] = 2 },
		"screen-disabled":      func(m *Machine) { m.VGA.seq[1] |= 0x20 },
		"memory-map":           func(m *Machine) { m.VGA.gc[6] = 0x0c },
		"split":                func(m *Machine) { crtcReg(m, 0x18, 10); crtcReg(m, 7, 0x0f); crtcReg(m, 9, 1) },
		"partial-row":          func(m *Machine) { crtcReg(m, 0x12, 0x8e) },
		"short-pitch":          func(m *Machine) { crtcReg(m, 0x13, 39) },
		"zero-pitch":           func(m *Machine) { crtcReg(m, 0x13, 0) },
		"tail-out-of-aperture": func(m *Machine) { setDisplayStart(m, 1000) },
	}
	for name, setup := range cases {
		t.Run(name, func(t *testing.T) {
			m := scanoutMachine()
			setup(m)
			out, e := m.LinearScanout()
			if e == nil || out.Indices != nil || out.Width != 0 {
				t.Fatal("unsupported mapping accepted")
			}
		})
	}
}

func TestLinearScanoutBothSavePaths(t *testing.T) {
	m := scanoutMachine()
	crtcReg(m, 0x12, 0x7f)
	setDisplayStart(m, 960)
	want, e := m.LinearScanout()
	if e != nil {
		t.Fatal(e)
	}
	snapshot := m.Snapshot()
	var state bytes.Buffer
	if e = m.SaveState(&state); e != nil {
		t.Fatal(e)
	}
	setDisplayStart(m, 0)
	m.Mem[int(VideoSeg)*16+3840] ^= 1
	m.Restore(snapshot)
	restored, e := m.LinearScanout()
	if e != nil || !reflect.DeepEqual(want, restored) {
		t.Fatal("snapshot lost display", e)
	}
	m2 := New()
	if e = m2.LoadState(&state); e != nil {
		t.Fatal(e)
	}
	loaded, e := m2.LinearScanout()
	if e != nil || !reflect.DeepEqual(want, loaded) {
		t.Fatal("state file lost display", e)
	}
}
