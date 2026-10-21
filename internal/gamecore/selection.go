package gamecore

import (
	"bytes"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

// Selection 只讀原游標；Target 是前端尚待送完的普通選角輸入。
type Selection struct {
	Player  int  `json:"player"`
	Cursor  int  `json:"cursor"`
	Target  int  `json:"target"`
	Confirm bool `json:"confirm"`
}

// SelectionPresentation 是原輸入輪詢邊界的完整顯示影本，不是即時 VRAM。
type SelectionPresentation struct {
	Serial    uint64
	Steps     uint64
	Selection Selection
	Scanout   *renderdata.Scanout
	Palette   [256][3]uint8
}

func (c *Core) SelectionPresentation() *SelectionPresentation {
	if c.selectionState() == nil || c.selectionPresentation == nil {
		return nil
	}
	out := *c.selectionPresentation
	if out.Scanout != nil {
		s := *out.Scanout
		s.Indices = append([]byte(nil), s.Indices...)
		out.Scanout = &s
	}
	return &out
}

func (c *Core) publishSelection() {
	s := c.selectionState()
	if s == nil || c.selectionCancel == nil || !bytes.Equal(c.o.Bytes(oracle.Far(0x01b9, 0x11d2), 7), []byte{0x33, 0xc0, 0x8e, 0xc0, 0x26, 0x8a, 0x26}) {
		return
	}
	display, palette, err := c.LiveDisplay()
	if err != nil {
		display = nil
	}
	old := c.selectionPresentation
	sameGeometry := old != nil && old.Scanout == nil && display == nil
	if old != nil && old.Scanout != nil && display != nil {
		a, b := old.Scanout, display
		sameGeometry = a.Width == b.Width && a.Height == b.Height && a.StartByte == b.StartByte && a.PitchByte == b.PitchByte && a.CRTC == b.CRTC
	}
	if old != nil && old.Selection.Player == s.Player && old.Selection.Cursor == s.Cursor && old.Palette == palette && sameGeometry && c.selectionPublishedRevision == c.selectionRevision {
		return
	}
	serial := uint64(1)
	if old != nil {
		serial = old.Serial + 1
	}
	if display != nil && display.Width == 320 && display.Height == 200 && display.StartByte == 0 && display.PitchByte == 320 && len(c.selectionPixels) == 64000 {
		display.Indices = append([]byte(nil), c.selectionPixels...)
	}
	c.selectionPresentation = &SelectionPresentation{Serial: serial, Steps: c.o.Steps(), Selection: *s, Scanout: display, Palette: palette}
	c.selectionPublishedRevision = c.selectionRevision
}

func (c *Core) selectionState() *Selection {
	if !c.selecting {
		return nil
	}
	const ds = 0x0bfa
	if !bytes.Equal(c.o.Bytes(oracle.Far(0x01b9, 0x10e0), 6), []byte{0xb5, 0xf1, 0x8b, 0x36, 0xb0, 0x12}) ||
		!bytes.Equal(c.o.Bytes(oracle.Far(ds, 0x3f16), 8), []byte{0x1e, 0x2c, 0x2d, 0x2e, 0x20, 0x12, 0x11, 0x10}) {
		return nil
	}
	mode, cursor := c.o.Word(oracle.Far(ds, 0x18)), int(c.o.Word(oracle.Far(ds, 0x12b0)))
	if mode > 1 || cursor > 10 {
		return nil
	}
	p := 0
	if c.o.Word(oracle.Far(ds, 0x12b4)) == 0x1395 {
		p = 1
	}
	return &Selection{Player: p, Cursor: cursor, Target: c.selectionTarget, Confirm: c.selectionConfirm}
}

func (c *Core) cancelSelectionInput() { c.selectionTarget = -1; c.selectionConfirm = false }

func (c *Core) installSelection() {
	c.cancelSelectionInput()
	c.o.OnCall(oracle.Far(0x01b9, 0x10e0), func(*oracle.Oracle) { c.selecting = true; c.cancelSelectionInput(); c.startSelectionDisplay() })
	c.o.OnCall(oracle.Far(0x01b9, 0x1312), func(*oracle.Oracle) { c.selecting = false; c.cancelSelectionInput(); c.stopSelectionDisplay() })
	c.o.OnCall(oracle.Far(0x01b9, 0x0da6), func(o *oracle.Oracle) {
		c.selectionBorder = c.selectionCancel != nil && o.DSReg() == 0x0bfa && o.SI() >= 8 && o.SI() <= 10
	})
	c.o.OnCall(oracle.Far(0x01b9, 0x0df5), func(*oracle.Oracle) { c.selectionBorder = false })
	c.o.OnCall(oracle.Far(0x01b9, 0x11d2), func(*oracle.Oracle) {
		c.publishSelection()
		s := c.selectionState()
		if s == nil || c.selectionTarget < 0 || c.o.KeysPending() != 0 {
			return
		}
		if s.Cursor != c.selectionTarget {
			if e := c.o.SendKeys("Right"); e != nil {
				c.err = e.Error()
				c.cancelSelectionInput()
			}
			return
		}
		confirm := c.selectionConfirm
		c.cancelSelectionInput()
		if confirm {
			if e := c.o.SendKeys("Return"); e != nil {
				c.err = e.Error()
			}
		}
	})
}

func (c *Core) startSelectionDisplay() {
	if c.selectionCancel != nil || c.selectionState() == nil {
		return
	}
	if !bytes.Equal(c.o.Bytes(oracle.Far(0x1b9, 0x0da6), 13), []byte{0xb8, 0, 0xa0, 0x8e, 0xc0, 0xb1, 3, 0xd3, 0xe6, 0x8b, 0x84, 0xd9, 0x12}) ||
		!bytes.Equal(c.o.Bytes(oracle.Far(0x1b9, 0x0df4), 2), []byte{0xfc, 0xc3}) {
		return
	}
	c.selectionPixels = c.o.Indexed()
	c.selectionPresentation = nil
	c.selectionRevision = 0
	c.selectionPublishedRevision = 0
	var err error
	c.selectionCancel, err = c.o.ObserveWrites(0xa0000, 0xaf9ff, func(event oracle.MemoryWrite) {
		if !c.selectionBorder {
			if c.selectionPixels[int(event.Address-0xa0000)] != event.Value {
				c.selectionRevision++
			}
			c.selectionPixels[int(event.Address-0xa0000)] = event.Value
		}
	})
	if err != nil {
		c.selectionPixels = nil
	}
}

func (c *Core) stopSelectionDisplay() {
	if c.selectionCancel != nil {
		c.selectionCancel()
		c.selectionCancel = nil
	}
	c.selectionPixels = nil
	c.selectionBorder = false
	c.selectionPresentation = nil
}

// SelectionDisplay 只改獨立顯示影本，RGB() 仍回傳原版實際輸出。
func (c *Core) SelectionDisplay() *renderdata.Scanout {
	if c.selectionState() == nil || len(c.selectionPixels) != 64000 {
		return nil
	}
	live, _, err := c.LiveDisplay()
	if err != nil || !live.Valid() || live.Width != 320 || live.Height != 200 || live.StartByte != 0 || live.PitchByte != 320 {
		return nil
	}
	out := *live
	out.Indices = append([]byte(nil), c.selectionPixels...)
	return &out
}

// ChooseCharacter 不直接寫原版角色，只在原輸入輪詢逐鍵定位。
func (c *Core) ChooseCharacter(character int) error {
	if character < 0 || character > 10 {
		return fmt.Errorf("角色超出範圍")
	}
	if c.paused || c.selectionState() == nil {
		return fmt.Errorf("目前不在可操作選角畫面")
	}
	c.selectionTarget = character
	c.selectionConfirm = false
	return nil
}

func (c *Core) selectionKey(name string) (bool, error) {
	s := c.selectionState()
	if s == nil {
		return false, nil
	}
	if name == "Left" || name == "Right" {
		base := s.Cursor
		if c.selectionTarget >= 0 {
			base = c.selectionTarget
		}
		delta := 1
		if name == "Left" {
			delta = -1
		}
		return true, c.ChooseCharacter((base + delta + 11) % 11)
	}
	if name == "Return" && c.selectionTarget >= 0 {
		c.selectionConfirm = true
		return true, nil
	}
	c.cancelSelectionInput()
	return false, nil
}
