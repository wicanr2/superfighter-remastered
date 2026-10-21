package gamecore

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/dosgolem/oracle"
)

func TestSelectionPublicationKeepsCompletePortraitAndOriginalMachine(t *testing.T) {
	root := os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" {
		t.Skip("private original data required")
	}
	a, e := New(root, t.TempDir())
	if e != nil {
		t.Fatal(e)
	}
	defer a.Close()
	b, e := New(root, t.TempDir())
	if e != nil {
		t.Fatal(e)
	}
	defer b.Close()
	portraits, e := os.ReadFile(filepath.Join(root, "BIGFIG.XBB"))
	if e != nil {
		t.Fatal(e)
	}
	for _, c := range []*Core{a, b} {
		c.o.SetClock(0, 0, 0, 0)
		c.Pause(false)
	}
	checkpoints, partial := 0, 0
	step := func(n uint64) {
		t.Helper()
		b.stopSelectionDisplay()
		if e := a.Step(n); e != nil {
			t.Fatal(e)
		}
		if e := b.Step(n); e != nil {
			t.Fatal(e)
		}
		b.stopSelectionDisplay()
		if a.o.Regs() != b.o.Regs() || !bytes.Equal(a.o.Bytes(oracle.Far(0, 0), 1<<20), b.o.Bytes(oracle.Far(0, 0), 1<<20)) {
			t.Fatal("publication changed original machine", a.Status().Steps)
		}
		wa, ha, ra := a.RGB()
		wb, hb, rb := b.RGB()
		if wa != wb || ha != hb || !bytes.Equal(ra, rb) {
			t.Fatal("publication changed original RGB")
		}
		checkpoints++
		f := a.SelectionPresentation()
		if f == nil {
			return
		}
		if f.Scanout == nil || len(f.Scanout.Indices) != 64000 || f.Serial == 0 || f.Steps > a.Status().Steps {
			t.Fatal("invalid published frame")
		}
		p, c := f.Selection.Player, f.Selection.Cursor
		for y := 0; y < 89; y++ {
			for x := 0; x < 89; x++ {
				dx := 11 + x
				if p == 1 {
					dx = 302 - x
				}
				if f.Scanout.Indices[(15+y)*320+dx] != portraits[c*8689+768+y*89+x]+byte(160+p*32) {
					t.Fatal("published a partial or mismatched portrait", p, c, f.Serial)
				}
			}
		}
		if live := a.SelectionDisplay(); live != nil && !bytes.Equal(live.Indices, f.Scanout.Indices) {
			partial++
		}
		original := f.Scanout.Indices[0]
		f.Scanout.Indices[0] ^= 255
		f.Palette[0][0] ^= 255
		if a.SelectionPresentation().Scanout.Indices[0] != original {
			t.Fatal("caller modified published frame")
		}
	}
	step(40_000_000)
	for _, c := range []*Core{a, b} {
		_ = c.MenuKey("Right")
		_ = c.MenuKey("Return")
	}
	step(24_000_000)
	for side := 0; side < 2; side++ {
		for _, character := range []int{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0} {
			for _, c := range []*Core{a, b} {
				if e := c.ChooseCharacter(character); e != nil {
					t.Fatal(e)
				}
			}
			end := a.Status().Steps + 12_000_000
			for {
				f := a.SelectionPresentation()
				s := a.Status().Selection
				if f != nil && f.Selection.Player == side && f.Selection.Cursor == character && s != nil && s.Target < 0 {
					break
				}
				if a.Status().Steps >= end {
					t.Fatal("normal selection deadline", a.Status())
				}
				step(100_000)
			}
		}
		for _, c := range []*Core{a, b} {
			_ = c.ChooseCharacter(8 + side*2)
			_ = c.MenuKey("Return")
		}
		end := a.Status().Steps + 40_000_000
		for {
			s := a.Status()
			if side == 0 && s.Selection != nil && s.Selection.Player == 1 || side == 1 && s.Battle {
				break
			}
			if s.Steps >= end {
				t.Fatal("handoff deadline", s)
			}
			step(100_000)
		}
	}
	if a.SelectionPresentation() != nil {
		t.Fatal("selection frame survived exit")
	}
	if partial == 0 {
		t.Fatal("test never observed intermediate original drawing")
	}
	t.Logf("%d fixed-clock paired machine/RGB checkpoints; %d intermediate writes retained behind complete frames", checkpoints, partial)
}
