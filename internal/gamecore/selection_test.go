package gamecore

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"
)

func TestNormalBossSelectionUsesOriginalInputs(t *testing.T) {
	root := os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" {
		t.Skip("local original sources not supplied")
	}
	for _, versus := range []bool{false, true} {
		name := "single"
		if versus {
			name = "versus"
		}
		t.Run(name, func(t *testing.T) {
			c, e := New(root, t.TempDir())
			if e != nil {
				t.Fatal(e)
			}
			defer c.Close()
			if e = c.ChooseCharacter(8); e == nil {
				t.Fatal("selection accepted before title")
			}
			c.Pause(false)
			step := func(n uint64) {
				t.Helper()
				if e := c.Step(n); e != nil {
					t.Fatal(e)
				}
			}
			step(40_000_000)
			x := 55
			if versus {
				x = 125
			}
			if e = c.Mouse(x, 181, true); e != nil {
				t.Fatal(e)
			}
			step(1_000_000)
			_ = c.Mouse(0, 0, false)
			step(24_000_000)
			wait := func(predicate func(Status) bool) {
				t.Helper()
				end := c.Status().Steps + 100_000_000
				for !predicate(c.Status()) {
					if c.Status().Steps >= end {
						t.Fatal("normal path deadline", c.Status())
					}
					step(250_000)
				}
			}
			wait(func(s Status) bool { return s.Selection != nil })
			portraits, err := os.ReadFile(filepath.Join(root, "BIGFIG.XBB"))
			if err != nil || len(portraits) != 11*8689 {
				t.Fatal("original portrait archive", err)
			}
			visitedBoss := false
			for _, character := range []int{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0} {
				if character >= 8 {
					visitedBoss = true
				}
				if e = c.ChooseCharacter(character); e != nil {
					t.Fatal(e)
				}
				wait(func(s Status) bool {
					return s.Selection != nil && s.Selection.Cursor == character && s.Selection.Target < 0
				})
				display := c.SelectionDisplay()
				if display == nil {
					t.Fatal("selection display absent")
				}
				for y := 0; y < 89; y++ {
					for x := 0; x < 89; x++ {
						if got, want := display.Indices[(15+y)*320+11+x], byte(160)+portraits[character*8689+768+y*89+x]; got != want {
							t.Fatalf("original portrait differs character=%d x=%d y=%d got=%d want=%d", character, x, y, got, want)
						}
					}
				}
				if !visitedBoss && !bytes.Equal(display.Indices, c.o.Indexed()) {
					t.Fatal("ordinary roster changed before visiting bosses")
				}
			}
			if e = c.MenuKey("Left"); e != nil {
				t.Fatal(e)
			}
			wait(func(s Status) bool { return s.Selection != nil && s.Selection.Cursor == 10 && s.Selection.Target < 0 })
			if e = c.ChooseCharacter(8); e != nil {
				t.Fatal(e)
			}
			c.Pause(true)
			if s := c.Status().Selection; s == nil || s.Target != -1 || s.Confirm {
				t.Fatal("pause retained queued selection", s)
			}
			c.Pause(false)
			if e = c.ChooseCharacter(9); e != nil {
				t.Fatal(e)
			}
			if e = c.MenuKey("Return"); e != nil {
				t.Fatal(e)
			}
			if versus {
				wait(func(s Status) bool { return s.Selection != nil && s.Selection.Player == 1 })
				if s := c.Status().Selection; s.Target >= 0 || s.Confirm {
					t.Fatal("selection leaked to second player", s)
				}
				if e = c.ChooseCharacter(10); e != nil {
					t.Fatal(e)
				}
				if e = c.MenuKey("Return"); e != nil {
					t.Fatal(e)
				}
			}
			wait(func(s Status) bool { return s.Battle && s.Frames > 8 })
			s := c.Status()
			if s.Fighters[0] != 9 || s.Selection != nil || (versus && (s.Mode != 1 || s.Fighters[1] != 10)) || (!versus && s.Mode != 0) {
				t.Fatal(s)
			}
			if c.selectionCancel != nil || c.SelectionDisplay() != nil {
				t.Fatal("selection observer survived exit")
			}
			if e = c.ChooseCharacter(8); e == nil {
				t.Fatal("selection accepted during battle")
			}
		})
	}
}
