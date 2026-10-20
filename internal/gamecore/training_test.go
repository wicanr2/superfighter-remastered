package gamecore

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

func TestTrainingNormalPlayerPaths(t *testing.T) {
	root := os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" {
		t.Skip("local original sources not supplied")
	}
	receipts := map[string]any{}
	for _, versus := range []bool{false, true} {
		name := "single"
		if versus {
			name = "versus"
		}
		t.Run(name, func(t *testing.T) {
			c, err := New(root, t.TempDir())
			if err != nil {
				t.Fatal(err)
			}
			defer c.Close()
			c.EnableHUD()
			if versus {
				c.SetTraining(true)
			}
			if c.Status().Training.Active || c.Status().Training.Modified {
				t.Fatal("training changed state before battle")
			}
			c.Pause(false)
			step := func(n uint64) {
				t.Helper()
				if err := c.Step(n); err != nil {
					t.Fatal(err)
				}
			}
			advance := func(n uint64) {
				t.Helper()
				end, deadline := c.Status().Frames+n, c.Status().Steps+200_000_000
				for c.Status().Frames < end {
					if c.Status().Steps >= deadline {
						t.Fatal("frame deadline", c.Status())
					}
					step(100_000)
				}
			}
			step(40_000_000)
			x := 55
			if versus {
				x = 125
			}
			if err = c.Mouse(x, 181, true); err != nil {
				t.Fatal(err)
			}
			step(1_000_000)
			_ = c.Mouse(0, 0, false)
			step(24_000_000)
			if err = c.o.SendKeys("Return"); err != nil {
				t.Fatal(err)
			}
			step(20_000_000)
			if versus {
				if err = c.o.SendKeys("Return"); err != nil {
					t.Fatal(err)
				}
			}
			advance(16)
			ds, ok := c.dataSegment()
			if !ok {
				t.Fatal("normal battle absent")
			}
			ai := [2]int{}
			for p, ip := range []uint16{0x18f2, 0x1927} {
				p := p
				c.o.OnCall(oracle.Far(0x1b9, ip), func(o *oracle.Oracle) {
					if o.Byte(oracle.Far(ds, uint16(0x3eb7+p))) == 4 && o.Byte(oracle.Far(ds, 0x3eba)) != 0 {
						ai[p]++
					}
				})
			}
			if !versus {
				// 對照沒有訓練掛鉤的獨立 Oracle，從同一完整機器狀態前進。
				raw, e := oracle.LoadProgram(filepath.Join(root, "NOKEY.EXE"), root, " /y")
				if e != nil {
					t.Fatal(e)
				}
				raw.SetScratch(t.TempDir())
				raw.Restore(c.o.Save())
				for i := 0; i < 32; i++ {
					step(1_000_000)
					if e = raw.Run(1_000_000); e != nil {
						t.Fatal(e)
					}
					if c.o.Regs() != raw.Regs() || !bytes.Equal(c.o.Bytes(oracle.Far(ds, 0), 65536), raw.Bytes(oracle.Far(ds, 0), 65536)) || !bytes.Equal(c.o.Indexed(), raw.Indexed()) {
						t.Fatal("disabled training changed original", i)
					}
				}
				raw.Close()
				for c.Status().Health == [2]uint16{124, 124} {
					advance(8)
					if c.Status().Frames > 150 {
						t.Fatal("no ordinary AI hit")
					}
				}
				if ai[1] == 0 {
					t.Fatal("baseline AI never acted")
				}
				receipts[name+"_baseline"] = c.Status()
				testTrainingRejections(t, c, ds)
				c.SetTraining(true)
			}
			advance(2)
			if !c.Status().Training.Active || !c.Status().Training.Modified {
				t.Fatal("training not active", c.Status())
			}
			frozen := c.Status().Training.Timer
			ai = [2]int{}
			advance(64)
			if ai != [2]int{} {
				t.Fatal("AI consumed actions during training", ai)
			}
			if s := c.Status(); s.Health != [2]uint16{124, 124} || s.Pending != [2]uint16{} || s.Timer != frozen {
				t.Fatal("neutral lock", s)
			}
			// 原版站立兩格有一像素繪圖偏移；驗中立輸入及站立路徑，保留呼吸動畫。
			before := c.Presentation().Actors
			for i := 0; i < 24; i++ {
				advance(1)
				if !versus && c.Status().Paths[1] != 0 {
					t.Fatal("AI left idle path", c.Status())
				}
			}
			after := c.Presentation().Actors
			abs := func(n int) int {
				if n < 0 {
					return -n
				}
				return n
			}
			if !versus && (abs(before[1].X-after[1].X) > 2 || abs(before[1].Y-after[1].Y) > 2) {
				t.Fatal("idle AI moved", before[1], after[1])
			}
			input := func(p int, keys ...uint8) {
				t.Helper()
				if err := c.SetInput([]Source{{Player: p, Name: "keyboard", Keys: keys}}); err != nil {
					t.Fatal(err)
				}
			}
			attack := func(p int) {
				t.Helper()
				for cycle := 0; cycle < 2; cycle++ {
					f := c.Presentation()
					dir := uint8(0x20)
					if p == 0 && f.Actors[0].X > f.Actors[1].X {
						dir = 0x1e
					}
					if p == 1 {
						dir = 0x4b
						if f.Actors[1].X < f.Actors[0].X {
							dir = 0x4d
						}
					}
					input(p, dir)
					for walk := 0; walk < 140; walk++ {
						f = c.Presentation()
						d := f.Actors[0].X - f.Actors[1].X
						if d < 0 {
							d = -d
						}
						if d <= 44 {
							break
						}
						advance(1)
					}
					punch := uint8(0xf)
					if p == 1 {
						punch = 0x1c
					}
					input(p, punch)
					advance(40)
					input(p)
					advance(30)
				}
			}
			attack(0)
			if versus {
				attack(1)
			}
			s := c.Status()
			if s.Training.Hits[1] == 0 || (versus && s.Training.Hits[0] == 0) || s.Health != [2]uint16{124, 124} || s.Pending != [2]uint16{} || s.Timer != frozen {
				t.Fatal("both-side damage protection", s)
			}
			board, e := hd.LoadHUD(root)
			if e != nil {
				t.Fatal(e)
			}
			f := c.Presentation()
			if f.HUD == nil {
				t.Fatal("HUD snapshot absent")
			}
			if selection, reason := board.Select(f.HUD, f.Pixels, f.Palette, f.Layers); selection == nil {
				t.Fatal("healed original bitmap incompatible with HD", reason)
			}
			if !f.Training.Active || !f.Training.Modified {
				t.Fatal("frame lost training attribution")
			}
			receipts[name+"_locked"] = s
			c.Pause(true)
			old := c.Status()
			step(2_000_000)
			if c.Status().Steps != old.Steps {
				t.Fatal("pause advanced training")
			}
			c.SetTraining(false)
			if c.Status().Training.Active || c.Status().Training.Requested || !c.Status().Training.Modified {
				t.Fatal("disable attribution", c.Status())
			}
			c.Pause(false)
			ai = [2]int{}
			advance(64)
			if c.Status().Timer >= frozen || (!versus && ai[1] == 0) {
				t.Fatal("time/AI failed to resume", c.Status(), ai)
			}
			if versus {
				attack(0)
				attack(1)
				if c.Status().Health[0] == 124 || c.Status().Health[1] == 124 {
					t.Fatal("damage did not resume both sides", c.Status())
				}
			}
			receipts[name+"_disabled"] = c.Status()
			fresh, e := New(root, t.TempDir())
			if e != nil {
				t.Fatal(e)
			}
			defer fresh.Close()
			if fresh.Status().Training.Requested || fresh.Status().Training.Modified {
				t.Fatal("training persisted across restart")
			}
		})
	}
	if out := os.Getenv("KDZZ_TRAINING_RECEIPT"); out != "" && !t.Failed() {
		b, e := json.MarshalIndent(receipts, "", "  ")
		if e != nil {
			t.Fatal(e)
		}
		if e = os.WriteFile(out, b, 0644); e != nil {
			t.Fatal(e)
		}
	}
}

// 相鄰邊界的受控單元實驗，不能取代上方普通選單與對戰路徑。
func testTrainingRejections(t *testing.T, c *Core, ds uint16) {
	t.Helper()
	state, host := c.o.Save(), c.training
	cases := []struct {
		name   string
		change func()
	}{
		{"zero health", func() { c.o.WriteU16(oracle.Far(ds, 0x169c), 0) }},
		{"lethal pending", func() { c.o.WriteU16(oracle.Far(ds, 0x16a0), c.o.Word(oracle.Far(ds, 0x169c))) }},
		{"knockout started", func() { c.o.WriteU8(oracle.Far(ds, 0x169a), 1) }},
		{"expired clock", func() { c.o.WriteU16(oracle.Far(ds, 0x2f26), 0) }},
		{"attract mode", func() { c.o.WriteU16(oracle.Far(ds, 0x18), 4) }},
		{"unknown code", func() { c.o.WriteU8(oracle.Far(0x1b9, 0x18f2), 0x90) }},
		{"unknown health art", func() { c.training.loadError = "invalid source" }},
	}
	for _, tc := range cases {
		c.o.Restore(state)
		c.training = host
		c.SetTraining(true)
		tc.change()
		before := c.o.Bytes(oracle.Far(ds, 0), 65536)
		c.trainingFrame(ds)
		if c.training.Active || c.training.Modified || !bytes.Equal(before, c.o.Bytes(oracle.Far(ds, 0), 65536)) {
			t.Fatal("training wrote rejected state", tc.name, c.Status())
		}
	}
	c.o.Restore(state)
	c.training = host
}
