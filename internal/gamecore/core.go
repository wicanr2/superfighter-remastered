// Package gamecore 以 public oracle API 包裹固定原版；輸入契約見規格 004、005。
package gamecore

import (
	"bytes"
	"crypto/sha256"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"sort"

	"github.com/wicanr2/dosgolem/oracle"
)

type Source struct {
	Player int
	Name   string
	Keys   []uint8
}
type phase struct {
	keys   []uint8
	frames int
}
type shortcut struct {
	phases           []phase
	index, remaining int
	keys             []uint8
}
type Status struct {
	Paused    bool    `json:"paused"`
	Battle    bool    `json:"battle"`
	Steps     uint64  `json:"steps"`
	Frames    uint64  `json:"frames"`
	Mode      int     `json:"mode"`
	Fighters  [2]int  `json:"fighters"`
	Paths     [2]int  `json:"paths"`
	KeyValues [2]int  `json:"key_values"`
	Quick     [2]bool `json:"quick"`
	Error     string  `json:"error,omitempty"`
}

// Core 由桌面 Update 所在執行緒獨占；沒有背景 goroutine 或網路。
type Core struct {
	o            *oracle.Oracle
	paused       bool
	manual       map[string]Source
	jobs         [2]*shortcut
	frames       uint64
	counter      uint16
	seen         bool
	err          string
	presentation Presentation
}

var allowed = [2]map[uint8]bool{
	{0x10: true, 0x11: true, 0x12: true, 0x1e: true, 0x20: true, 0x2c: true, 0x2d: true, 0x2e: true, 0x0f: true, 0x2a: true},
	{0x47: true, 0x48: true, 0x49: true, 0x4b: true, 0x4d: true, 0x4f: true, 0x50: true, 0x51: true, 0x1c: true, 0x36: true},
}

func New(root, scratch string) (*Core, error) {
	for n, want := range map[string]string{"SF.EXE": "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300", "SF.COM": "f194ff7cce7975aabff3f8ec5f92a8b0ca2db0368c33ed29aba7bd7b70f6392e", "NOKEY.EXE": "5757324e9e4cebeda2527b60c3f04fc8628c2a67aba6123282e57eea1a1e8b8c"} {
		b, e := os.ReadFile(filepath.Join(root, n))
		if e != nil {
			return nil, e
		}
		if fmt.Sprintf("%x", sha256.Sum256(b)) != want {
			return nil, fmt.Errorf("原始檔不符：%s", n)
		}
	}
	if e := os.MkdirAll(scratch, 0755); e != nil {
		return nil, e
	}
	o, e := oracle.LoadProgram(filepath.Join(root, "NOKEY.EXE"), root, " /y")
	if e != nil {
		return nil, e
	}
	o.SetScratch(scratch)
	o.Enqueue("SF.COM", "")
	c := &Core{o: o, paused: true, manual: map[string]Source{}}
	o.OnCall(oracle.Far(0x01b9, 0x5d9f), c.frame)
	o.OnCall(oracle.Far(0x01b9, 0x3e9d), c.capturePresentation)
	return c, nil
}
func (c *Core) Close() { c.Release(); c.o.Close() }
func (c *Core) dataSegment() (uint16, bool) {
	if c.o.Word(oracle.Far(0, 0x24)) != 0x524c || c.o.Word(oracle.Far(0, 0x26)) != 0x01b9 {
		return 0, false
	}
	b := c.o.Bytes(oracle.Far(0x01b9, 0x524c), 10)
	if !bytes.Equal(b[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		return 0, false
	}
	ds := uint16(b[6]) | uint16(b[7])<<8
	if !bytes.Equal(c.o.Bytes(oracle.Far(ds, 0x3f16), 8), []byte{0x1e, 0x2c, 0x2d, 0x2e, 0x20, 0x12, 0x11, 0x10}) {
		return 0, false
	}
	return ds, true
}
func (c *Core) Status() Status {
	s := Status{Paused: c.paused, Steps: c.o.Steps(), Frames: c.frames, Mode: -1, Fighters: [2]int{-1, -1}, Error: c.err, Quick: [2]bool{c.jobs[0] != nil, c.jobs[1] != nil}}
	if ds, ok := c.dataSegment(); ok {
		s.Battle = true
		s.Mode = int(c.o.Word(oracle.Far(ds, 0x18)))
		for p := 0; p < 2; p++ {
			s.Fighters[p] = int(c.o.Word(oracle.Far(ds, uint16(0x12ac+p*2))))
			s.Paths[p] = int(c.o.Byte(oracle.Far(ds, uint16(0x16ea+p))))
			s.KeyValues[p] = int(c.o.Byte(oracle.Far(ds, uint16(0x3ef4+p))))
		}
	}
	return s
}
func (c *Core) RGB() (int, int, []byte) { return c.o.ScreenRGB() }
func (c *Core) Pause(value bool)        { c.Release(); c.o.ReleaseButton(0); c.paused = value }
func (c *Core) Release() {
	c.manual = map[string]Source{}
	c.jobs = [2]*shortcut{}
	for _, k := range c.o.HeldKeys() {
		c.o.KeyUp(k)
	}
}
func (c *Core) CancelPad(p int) {
	if p < 0 || p > 1 {
		return
	}
	c.jobs[p] = nil
	delete(c.manual, fmt.Sprintf("%d:pad", p))
	c.aggregate()
}
func (c *Core) Step(budget uint64) error {
	if c.paused || c.err != "" {
		return nil
	}
	_, before := c.dataSegment()
	if e := c.o.Run(budget); e != nil {
		c.err = e.Error()
		c.Pause(true)
		return e
	}
	if _, after := c.dataSegment(); before && !after {
		c.Release()
		c.frames = 0
		c.seen = false
		c.presentation = Presentation{}
	}
	return nil
}
func (c *Core) MenuKey(name string) error {
	if c.paused || c.Status().Battle {
		return nil
	}
	if name != "Return" && name != "Left" && name != "Right" && name != "Up" && name != "Down" {
		return fmt.Errorf("未知選單按鍵")
	}
	if c.o.KeysPending() < 4 {
		return c.o.SendKeys(name)
	}
	return nil
}
func (c *Core) Mouse(x, y int, down bool) error {
	if !down {
		c.o.ReleaseButton(0)
		return nil
	}
	if c.paused || c.Status().Battle {
		return nil
	}
	if x < 0 || x >= 320 || y < 0 || y >= 200 {
		return fmt.Errorf("點選超出遊戲區域")
	}
	if e := c.o.MoveMouse(x, y); e != nil {
		return e
	}
	c.o.PressButton(0)
	return nil
}
func (c *Core) SetInput(sources []Source) error {
	if len(sources) > 4 {
		return fmt.Errorf("輸入來源過多")
	}
	next := map[string]Source{}
	for _, src := range sources {
		if src.Player < 0 || src.Player > 1 || (src.Name != "keyboard" && src.Name != "pad") || len(src.Keys) > 10 {
			return fmt.Errorf("輸入來源錯誤")
		}
		key := fmt.Sprintf("%d:%s", src.Player, src.Name)
		if _, ok := next[key]; ok {
			return fmt.Errorf("輸入來源重複")
		}
		seen := map[uint8]bool{}
		for _, k := range src.Keys {
			if !allowed[src.Player][k] || seen[k] {
				return fmt.Errorf("按鍵不符玩家")
			}
			seen[k] = true
		}
		src.Keys = append([]uint8(nil), src.Keys...)
		sort.Slice(src.Keys, func(i, j int) bool { return src.Keys[i] < src.Keys[j] })
		next[key] = src
	}
	if c.paused || !c.Status().Battle {
		c.Release()
		return nil
	}
	for p := 0; p < 2; p++ {
		for _, name := range []string{"keyboard", "pad"} {
			key := fmt.Sprintf("%d:%s", p, name)
			a, b := c.manual[key].Keys, next[key].Keys
			if len(a) == 0 && len(b) == 0 {
				continue
			}
			if !reflect.DeepEqual(a, b) {
				c.jobs[p] = nil
			}
		}
	}
	c.manual = next
	c.aggregate()
	return nil
}
func (c *Core) aggregate() {
	want := map[uint8]bool{}
	for _, src := range c.manual {
		if c.jobs[src.Player] == nil {
			for _, k := range src.Keys {
				want[k] = true
			}
		}
	}
	for _, j := range c.jobs {
		if j != nil {
			for _, k := range j.keys {
				want[k] = true
			}
		}
	}
	old := map[uint8]bool{}
	for _, k := range c.o.HeldKeys() {
		old[k] = true
		if !want[k] {
			c.o.KeyUp(k)
		}
	}
	var add []int
	for k := range want {
		if !old[k] {
			add = append(add, int(k))
		}
	}
	sort.Ints(add)
	for _, k := range add {
		c.o.KeyDown(uint8(k))
	}
}
func (c *Core) frame(o *oracle.Oracle) {
	ds, ok := c.dataSegment()
	if !ok {
		return
	}
	counter := o.Word(oracle.Far(ds, 0x1a))
	if c.seen && counter == c.counter {
		return
	}
	c.seen = true
	c.counter = counter
	c.frames++
	for p, j := range c.jobs {
		if j == nil {
			continue
		}
		if o.Byte(oracle.Far(ds, 0x169a))&0x80 != 0 || o.Byte(oracle.Far(ds, 0x169b))&0x80 != 0 {
			c.jobs[p] = nil
			continue
		}
		if j.remaining > 0 {
			j.remaining--
		}
		if j.remaining > 0 {
			continue
		}
		j.index++
		if j.index >= len(j.phases) {
			c.jobs[p] = nil
			continue
		}
		j.keys = j.phases[j.index].keys
		j.remaining = j.phases[j.index].frames
	}
	c.aggregate()
}
func (c *Core) Quick(player, move int) error {
	if player < 0 || player > 1 {
		return fmt.Errorf("玩家錯誤")
	}
	ds, ok := c.dataSegment()
	if !ok || c.paused || c.frames == 0 {
		return fmt.Errorf("尚未進入可操作對戰")
	}
	mode := c.o.Word(oracle.Far(ds, 0x18))
	if mode > 1 || (mode == 0 && player == 1) {
		return fmt.Errorf("此玩家目前由電腦控制")
	}
	if c.o.Word(oracle.Far(ds, uint16(0x12ac+player*2))) != 0 {
		return fmt.Errorf("此角色快捷尚未驗證")
	}
	facing := c.o.Byte(oracle.Far(ds, uint16(0x16b4+player)))
	if facing != 0 && facing != 255 {
		return fmt.Errorf("角色朝向未知")
	}
	f, df, d, db, b, u, p, k := uint8(0x20), uint8(0x2e), uint8(0x2d), uint8(0x2c), uint8(0x1e), uint8(0x11), uint8(0x0f), uint8(0x2a)
	if player == 1 {
		f, df, d, db, b, u, p, k = 0x4d, 0x51, 0x50, 0x4f, 0x4b, 0x48, 0x1c, 0x36
	}
	if facing == 255 {
		f, b = b, f
		df, db = db, df
	}
	var phases []phase
	switch move {
	case 1:
		phases = []phase{{[]uint8{f}, 1}, {[]uint8{df}, 1}, {[]uint8{d, p}, 1}}
	case 2:
		phases = []phase{{[]uint8{d}, 1}, {[]uint8{db}, 1}, {[]uint8{b, k}, 1}}
	case 3:
		phases = []phase{{[]uint8{d}, 12}, {[]uint8{u, k}, 1}}
	case 4:
		phases = []phase{{[]uint8{f, p}, 1}}
	default:
		return fmt.Errorf("此招式尚未驗證")
	}
	c.jobs[player] = &shortcut{phases: phases, index: -1}
	c.aggregate()
	return nil
}
