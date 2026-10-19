package oracle_test

import (
	"bytes"
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/wicanr2/dosgolem/oracle"
)

func writeObservationProgram(t *testing.T) *oracle.Oracle {
	t.Helper()
	code := []byte{
		0xb8, 0, 0x20, // mov ax,2000h
		0x8e, 0xd8, // mov ds,ax
		0x8e, 0xc0, // mov es,ax
		0xb8, 0x34, 0x12, // mov ax,1234h
		0xa3, 0, 0, // mov [0],ax
		0xa3, 0, 0, // same value written again
		0xbf, 2, 0, // mov di,2
		0xb0, 0x56, // mov al,56h
		0xaa, 0xaa, // stosb, stosb
		0xbe, 0, 0, // mov si,0
		0xbf, 4, 0, // mov di,4
		0xb9, 2, 0, // mov cx,2
		0xf3, 0xa5, // rep movsw
		0xeb, 0xfe, // bounded by caller Run budget
	}
	root := t.TempDir()
	path := filepath.Join(root, "WRITE.COM")
	if e := os.WriteFile(path, code, 0600); e != nil {
		t.Fatal(e)
	}
	o, e := oracle.LoadProgram(path, root, "")
	if e != nil {
		t.Fatal(e)
	}
	t.Cleanup(o.Close)
	return o
}

func TestObserveWritesIncludesRepeatedStoresAndPreservesMachine(t *testing.T) {
	a, b := writeObservationProgram(t), writeObservationProgram(t)
	start := a.IP()
	var events []oracle.MemoryWrite
	legacy := 0
	a.OnWrite(0x20000, 0x20007, func(*oracle.Oracle, oracle.WriteHit) { legacy++ })
	cancel, e := a.ObserveWrites(0x20000, 0x20007, func(hit oracle.MemoryWrite) { events = append(events, hit) })
	if e != nil {
		t.Fatal(e)
	}
	if e = a.Run(50); e != nil {
		t.Fatal(e)
	}
	if e = b.Run(50); e != nil {
		t.Fatal(e)
	}
	wantAddress := []uint32{0x20000, 0x20001, 0x20000, 0x20001, 0x20002, 0x20003, 0x20004, 0x20005, 0x20006, 0x20007}
	wantValue := []uint8{0x34, 0x12, 0x34, 0x12, 0x56, 0x56, 0x34, 0x12, 0x56, 0x56}
	wantIP := []uint16{10, 10, 13, 13, 21, 22, 32, 32, 32, 32}
	if len(events) != len(wantAddress) {
		t.Fatalf("events=%+v", events)
	}
	for i, event := range events {
		old := uint8(0)
		if i == 2 {
			old = 0x34
		}
		if i == 3 {
			old = 0x12
		}
		if event.Address != wantAddress[i] || event.Value != wantValue[i] || event.Old != old || event.Writer.Seg != start.Seg || event.Writer.Off != start.Off+wantIP[i] {
			t.Fatalf("event %d=%+v, entry=%+v", i, event, start)
		}
	}
	if legacy != 8 {
		t.Fatalf("changed-value observer=%d", legacy)
	}
	if !bytes.Equal(a.Bytes(oracle.Phys(0), 1<<20), b.Bytes(oracle.Phys(0), 1<<20)) {
		t.Fatal("observation changed machine memory")
	}
	state := func(o *oracle.Oracle) []any {
		return []any{o.AX(), o.BX(), o.CX(), o.DX(), o.SI(), o.DI(), o.BP(), o.SP(), o.ES(), o.DSReg(), o.IP(), o.Steps(), o.Cycles(), o.Ticks()}
	}
	if !reflect.DeepEqual(state(a), state(b)) {
		t.Fatalf("observation changed machine state: %v / %v", state(a), state(b))
	}
	cancel()
	cancel()
	a.WriteU8(oracle.Phys(0x20000), 0x66)
	if len(events) != 10 || legacy != 9 {
		t.Fatalf("independent cancellation: events=%d legacy=%d", len(events), legacy)
	}
}

func TestObserveWritesBoundsAndIndependentWatchers(t *testing.T) {
	o := writeObservationProgram(t)
	for _, span := range [][2]uint32{{10, 9}, {0, 1 << 20}} {
		if cancel, e := o.ObserveWrites(span[0], span[1], func(oracle.MemoryWrite) {}); e == nil || cancel != nil {
			t.Fatal("invalid range installed watch")
		}
	}
	if cancel, e := o.ObserveWrites(0, 0, nil); e == nil || cancel != nil {
		t.Fatal("nil observer accepted")
	}
	first, second := 0, 0
	a, e := o.ObserveWrites(0x20000, 0x20000, func(oracle.MemoryWrite) { first++ })
	if e != nil {
		t.Fatal(e)
	}
	b, e := o.ObserveWrites(0x20000, 0x20000, func(oracle.MemoryWrite) { second++ })
	if e != nil {
		t.Fatal(e)
	}
	a()
	o.WriteU8(oracle.Phys(0x20000), 0)
	o.WriteU8(oracle.Phys(0x20001), 1)
	if first != 0 || second != 1 {
		t.Fatalf("watch isolation %d / %d", first, second)
	}
	b()
}
