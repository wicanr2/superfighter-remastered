// Package desktop 是三平台共用的原生視窗與輸入適配，不啟動網路服務。
package desktop

import (
	"bytes"
	"embed"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"math"
	"os"
	"path/filepath"
	"time"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/inpututil"
	"github.com/hajimehoshi/ebiten/v2/text/v2"
	"github.com/hajimehoshi/ebiten/v2/vector"
	"github.com/wicanr2/superfighter-remastered/internal/controls"
	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

//go:embed assets/NotoSansCJKtc-Regular.otf assets/OFL.txt assets/source.json
var assets embed.FS

const Width, Height = 1120, 820

var screenRect = image.Rect(80, 64, 1040, 664)

type Options struct {
	Root, DataDir, Observe, Capture, HDAssets, HDCharacters string
	QuitAfter                                               time.Duration
}
type device struct {
	id       ebiten.GamepadID
	name     string
	standard bool
}
type widget struct {
	rect     image.Rectangle
	label    string
	action   func(int)
	focus    int
	disabled bool
}
type Game struct {
	core             *gamecore.Core
	settings         controls.Settings
	settingsPath     string
	settingsWritable bool
	face             *text.GoTextFace
	texture          *ebiten.Image
	rgba             []byte
	devices          []device
	assigned         [2]ebiten.GamepadID
	armed            [2]bool
	keyboardArmed    bool
	starts           [2]bool
	shoulders        [2][4]bool
	confirm          [2]bool
	lastMenu         [2]time.Time
	panel            bool
	editing          [2]int
	focus            int
	notice           string
	opts             Options
	started          time.Time
	capture          bool
	updates          uint64
	hdAssets         *hd.Assets
	hdTexture        *ebiten.Image
	hdEnabled        bool
	hdActive         bool
	hdReason         string
	hdCharacters     *hd.Characters
	layerTextures    []*ebiten.Image
	layerRGBA        [][]byte
	actorTextures    map[*hd.PoseArt]*ebiten.Image
}

func New(opts Options) (*Game, error) {
	if e := os.MkdirAll(opts.DataDir, 0755); e != nil {
		return nil, e
	}
	c, e := gamecore.New(opts.Root, filepath.Join(opts.DataDir, "dos"))
	if e != nil {
		return nil, e
	}
	b, _ := assets.ReadFile("assets/NotoSansCJKtc-Regular.otf")
	font, e := text.NewGoTextFaceSource(bytes.NewReader(b))
	if e != nil {
		c.Close()
		return nil, e
	}
	path := filepath.Join(opts.DataDir, "settings.json")
	s, se := controls.Load(path)
	g := &Game{core: c, settings: s, settingsPath: path, settingsWritable: se == nil, face: &text.GoTextFace{Source: font, Size: 20}, assigned: [2]ebiten.GamepadID{-1, -1}, opts: opts, started: time.Now(), notice: "按開始，從原版標題選擇單打或雙打。"}
	if se != nil {
		g.notice = "設定無法讀取，保留原檔並使用預設；本次不覆寫。"
	}
	if opts.HDAssets != "" {
		g.hdAssets, e = hd.Load(opts.HDAssets)
		if e != nil {
			g.notice = "HD 素材無法載入，保留原貌。"
		}
	}
	if opts.HDCharacters != "" {
		g.hdCharacters, e = hd.LoadCharacters(opts.HDCharacters, opts.Root)
		if e != nil || g.hdAssets == nil {
			g.hdCharacters = nil
			g.notice = "HD 角色與背景素材無法完整載入，保留原貌。"
		} else {
			if g.hdCharacters.HasEffects() {
				c.EnableEffects()
			} else {
				c.EnableLayers()
			}
		}
	}
	return g, nil
}
func (g *Game) Close() { g.core.Close() }
func (g *Game) pause(value bool) {
	g.core.Pause(value)
	g.armed = [2]bool{}
	g.keyboardArmed = false
	g.shoulders = [2][4]bool{}
	if value {
		g.notice = "已暫停。"
	} else {
		g.notice = "請從原版畫面繼續操作。"
	}
}
func (g *Game) save() {
	if !g.settingsWritable {
		g.notice = "原設定有錯誤，本次變更僅保留在記憶體。"
		return
	}
	if e := g.settings.Save(g.settingsPath); e != nil {
		g.notice = "設定保存失敗：" + e.Error()
	} else {
		g.notice = "兩名玩家各角色的四格設定已保存。"
	}
}
func (g *Game) openSettings() {
	g.panel = !g.panel
	g.pause(true)
	if g.panel {
		s := g.core.Status()
		for p, c := range s.Fighters {
			if c >= 0 && c < len(controls.Catalog) {
				g.editing[p] = c
			}
		}
	}
}
func (g *Game) scanDevices() {
	g.devices = nil
	present := map[ebiten.GamepadID]bool{}
	for _, id := range ebiten.AppendGamepadIDs(nil) {
		present[id] = true
		g.devices = append(g.devices, device{id, ebiten.GamepadName(id), ebiten.IsStandardGamepadLayoutAvailable(id)})
	}
	for p, id := range g.assigned {
		if id >= 0 && !present[id] {
			g.core.CancelPad(p)
			g.assigned[p] = -1
			g.armed[p] = false
			g.shoulders[p] = [4]bool{}
			g.notice = fmt.Sprintf("第 %d 人手把已斷線，請重新指派。", p+1)
		}
	}
}
func (g *Game) nextDevice(p, delta int) {
	ids := []ebiten.GamepadID{-1}
	for _, d := range g.devices {
		if d.standard && d.id != g.assigned[1-p] {
			ids = append(ids, d.id)
		}
	}
	i := 0
	for j, id := range ids {
		if id == g.assigned[p] {
			i = j
		}
	}
	g.assigned[p] = ids[(i+delta+len(ids))%len(ids)]
	g.armed[p] = false
	g.starts[p] = false
	g.shoulders[p] = [4]bool{}
	g.core.CancelPad(p)
}
func (g *Game) deviceName(p int) string {
	for _, d := range g.devices {
		if d.id == g.assigned[p] {
			return d.name
		}
	}
	return "未指派手把"
}
func (g *Game) quick(p, slot int) {
	s := g.core.Status()
	c := s.Fighters[p]
	if c < 0 || c >= len(controls.Catalog) {
		return
	}
	ch := controls.Catalog[c]
	move := g.settings.Players[p][ch.ID][slot]
	if move == 0 {
		return
	}
	if e := g.core.Quick(p, move); e != nil {
		g.notice = e.Error()
	} else {
		g.notice = fmt.Sprintf("第 %d 人：%s", p+1, ch.Moves[move-1])
	}
}
func (g *Game) fields() []widget {
	var out []widget
	for p := 0; p < 2; p++ {
		x := 58 + p*530
		c := controls.Catalog[g.editing[p]]
		out = append(out, widget{image.Rect(x, 190, x+474, 232), g.deviceName(p), func(delta int) { g.nextDevice(p, delta) }, p * 6, false})
		out = append(out, widget{image.Rect(x, 280, x+474, 322), c.Name, func(delta int) { g.editing[p] = (g.editing[p] + delta + len(controls.Catalog)) % len(controls.Catalog) }, p*6 + 1, false})
		for slot := 0; slot < 4; slot++ {
			i := slot
			m := g.settings.Players[p][c.ID][slot]
			name := "未綁定"
			if m > 0 {
				name = c.Moves[m-1]
			}
			out = append(out, widget{image.Rect(x+70, 344+slot*60, x+474, 390+slot*60), name, func(delta int) {
				v := g.settings.Players[p][c.ID]
				v[i] = (v[i] + delta + len(c.Moves) + 1) % (len(c.Moves) + 1)
				g.settings.Players[p][c.ID] = v
				g.save()
			}, p*6 + 2 + slot, false})
		}
	}
	return out
}
func (g *Game) widgets() []widget {
	s := g.core.Status()
	out := []widget{
		{image.Rect(24, 12, 196, 52), "開始／繼續", func(int) { g.panel = false; g.pause(false) }, -1, false},
		{image.Rect(208, 12, 330, 52), "暫停", func(int) { g.pause(true) }, -1, false},
		{image.Rect(342, 12, 564, 52), "手把與快捷設定", func(int) { g.openSettings() }, -1, false},
		{image.Rect(576, 12, 710, 52), "全螢幕", func(int) { ebiten.SetFullscreen(!ebiten.IsFullscreen()) }, -1, false},
		{image.Rect(722, 12, 940, 52), "原貌／HD 背景", func(int) { g.hdEnabled = !g.hdEnabled; g.notice = "呈現已切換，角色與操作沿用原版。" }, -1, g.hdAssets == nil},
	}
	if g.opts.HDCharacters != "" {
		out[4].label = "原貌／HD 角色"
		out[4].action = func(int) { g.hdEnabled = !g.hdEnabled; g.notice = "已切換原貌／HD。" }
	}
	if g.panel {
		return append(out, g.fields()...)
	}
	for p := 0; p < 2; p++ {
		for slot := 0; slot < 4; slot++ {
			i := slot
			label := controls.Slots[slot]
			disabled := s.Paused || !s.Battle
			c := s.Fighters[p]
			if c >= 0 && c < len(controls.Catalog) {
				ch := controls.Catalog[c]
				move := g.settings.Players[p][ch.ID][slot]
				if move > 0 {
					label += " " + ch.Moves[move-1]
				} else {
					label += " 空"
					disabled = true
				}
			}
			if p == 1 && s.Mode == 0 {
				disabled = true
			}
			x := 24 + p*552 + slot*132
			out = append(out, widget{image.Rect(x, 714, x+124, 760), label, func(int) { g.quick(p, i) }, -1, disabled})
		}
	}
	return out
}

var keyMap = map[ebiten.Key]struct {
	p    int
	scan uint8
}{
	ebiten.KeyQ: {0, 0x10}, ebiten.KeyW: {0, 0x11}, ebiten.KeyE: {0, 0x12}, ebiten.KeyA: {0, 0x1e}, ebiten.KeyD: {0, 0x20}, ebiten.KeyZ: {0, 0x2c}, ebiten.KeyX: {0, 0x2d}, ebiten.KeyC: {0, 0x2e}, ebiten.KeyTab: {0, 0x0f}, ebiten.KeyShiftLeft: {0, 0x2a},
	ebiten.KeyNumpad7: {1, 0x47}, ebiten.KeyNumpad8: {1, 0x48}, ebiten.KeyNumpad9: {1, 0x49}, ebiten.KeyNumpad4: {1, 0x4b}, ebiten.KeyNumpad6: {1, 0x4d}, ebiten.KeyNumpad1: {1, 0x4f}, ebiten.KeyNumpad2: {1, 0x50}, ebiten.KeyNumpad3: {1, 0x51}, ebiten.KeyEnter: {1, 0x1c}, ebiten.KeyNumpadEnter: {1, 0x1c}, ebiten.KeyShiftRight: {1, 0x36},
}
var dirs = [2][3][3]uint8{{{0x10, 0x11, 0x12}, {0x1e, 0, 0x20}, {0x2c, 0x2d, 0x2e}}, {{0x47, 0x48, 0x49}, {0x4b, 0, 0x4d}, {0x4f, 0x50, 0x51}}}

func (g *Game) Update() error {
	g.updates++
	if g.opts.QuitAfter > 0 && time.Since(g.started) > g.opts.QuitAfter {
		return ebiten.Termination
	}
	g.scanDevices()
	if inpututil.IsKeyJustPressed(ebiten.KeyF12) {
		g.capture = true
	}
	if !ebiten.IsFocused() {
		if !g.core.Status().Paused {
			g.pause(true)
		}
		g.observe()
		return nil
	}
	if inpututil.IsKeyJustPressed(ebiten.KeyEscape) {
		if g.panel {
			g.panel = false
		} else {
			g.pause(!g.core.Status().Paused)
		}
		g.observe()
		return nil
	}
	if inpututil.IsKeyJustPressed(ebiten.KeyF10) {
		g.openSettings()
		g.observe()
		return nil
	}
	if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) {
		x, y := ebiten.CursorPosition()
		pt := image.Pt(x, y)
		for _, w := range g.widgets() {
			if pt.In(w.rect) {
				if !w.disabled {
					w.action(1)
				}
				g.observe()
				return nil
			}
		}
	}
	if g.panel {
		if inpututil.IsKeyJustPressed(ebiten.KeyTab) || inpututil.IsKeyJustPressed(ebiten.KeyArrowDown) {
			g.focus = (g.focus + 1) % 12
		}
		if inpututil.IsKeyJustPressed(ebiten.KeyArrowUp) {
			g.focus = (g.focus + 11) % 12
		}
		delta := 0
		if inpututil.IsKeyJustPressed(ebiten.KeyArrowLeft) {
			delta = -1
		}
		if inpututil.IsKeyJustPressed(ebiten.KeyArrowRight) || inpututil.IsKeyJustPressed(ebiten.KeyEnter) {
			delta = 1
		}
		if delta != 0 {
			for _, w := range g.fields() {
				if w.focus == g.focus {
					w.action(delta)
				}
			}
		}
		g.observe()
		return nil
	}
	s := g.core.Status()
	keyboard := [2]map[uint8]bool{{}, {}}
	any := false
	for key, value := range keyMap {
		if keyboardPressed(key) {
			any = true
			keyboard[value.p][value.scan] = true
		}
	}
	if !any {
		g.keyboardArmed = true
	}
	if !s.Battle && !s.Paused {
		for key, name := range map[ebiten.Key]string{ebiten.KeyArrowLeft: "Left", ebiten.KeyArrowRight: "Right", ebiten.KeyArrowUp: "Up", ebiten.KeyArrowDown: "Down", ebiten.KeyEnter: "Return", ebiten.KeyNumpadEnter: "Return"} {
			if inpututil.IsKeyJustPressed(key) {
				if e := g.core.MenuKey(name); e != nil {
					g.notice = e.Error()
				}
			}
		}
	}
	if !s.Paused {
		x, y := ebiten.CursorPosition()
		if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) && image.Pt(x, y).In(screenRect) {
			if e := g.core.Mouse((x-screenRect.Min.X)/3, (y-screenRect.Min.Y)/3, true); e != nil {
				g.notice = e.Error()
			}
		}
		if inpututil.IsMouseButtonJustReleased(ebiten.MouseButtonLeft) {
			_ = g.core.Mouse(0, 0, false)
		}
	}
	var sources []gamecore.Source
	for p := 0; p < 2; p++ {
		ks := []uint8{}
		if g.keyboardArmed && s.Battle && !s.Paused {
			for k := range keyboard[p] {
				ks = append(ks, k)
			}
		}
		sources = append(sources, gamecore.Source{Player: p, Name: "keyboard", Keys: ks})
	}
	var rising [2][]int
	startToggled := false
	for p, id := range g.assigned {
		var scans []uint8
		if id >= 0 {
			press := func(b ebiten.StandardGamepadButton) bool { return ebiten.IsStandardGamepadButtonPressed(id, b) }
			start := press(ebiten.StandardGamepadButtonCenterRight)
			if start && !g.starts[p] && g.armed[p] && !startToggled {
				g.pause(!g.core.Status().Paused)
				startToggled = true
			}
			g.starts[p] = start
			x, y := ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickHorizontal), ebiten.StandardGamepadAxisValue(id, ebiten.StandardGamepadAxisLeftStickVertical)
			neutral := math.Hypot(x, y) < .25
			for b := ebiten.StandardGamepadButton(0); b <= ebiten.StandardGamepadButtonMax; b++ {
				if press(b) {
					neutral = false
				}
			}
			if neutral {
				g.armed[p] = true
			}
			if g.armed[p] && !g.core.Status().Paused {
				dx, dy := 0, 0
				if press(ebiten.StandardGamepadButtonLeftLeft) {
					dx--
				}
				if press(ebiten.StandardGamepadButtonLeftRight) {
					dx++
				}
				if press(ebiten.StandardGamepadButtonLeftTop) {
					dy--
				}
				if press(ebiten.StandardGamepadButtonLeftBottom) {
					dy++
				}
				if dx == 0 && dy == 0 && math.Hypot(x, y) > .30 {
					dir := int(math.Round(math.Atan2(y, x) / (math.Pi / 4)))
					v := [8][2]int{{1, 0}, {1, 1}, {0, 1}, {-1, 1}, {-1, 0}, {-1, -1}, {0, -1}, {1, -1}}[(dir+8)%8]
					dx, dy = v[0], v[1]
				}
				if s.Battle {
					if dx != 0 || dy != 0 {
						scans = append(scans, dirs[p][dy+1][dx+1])
					}
					if press(ebiten.StandardGamepadButtonRightLeft) {
						scans = append(scans, []uint8{0x0f, 0x1c}[p])
					}
					if press(ebiten.StandardGamepadButtonRightBottom) {
						scans = append(scans, []uint8{0x2a, 0x36}[p])
					}
					buttons := [4]ebiten.StandardGamepadButton{ebiten.StandardGamepadButtonFrontTopRight, ebiten.StandardGamepadButtonFrontBottomRight, ebiten.StandardGamepadButtonFrontTopLeft, ebiten.StandardGamepadButtonFrontBottomLeft}
					for i, b := range buttons {
						down := press(b)
						if down && !g.shoulders[p][i] {
							rising[p] = append(rising[p], i)
						}
						g.shoulders[p][i] = down
					}
				} else {
					if (dx != 0 || dy != 0) && time.Since(g.lastMenu[p]) > 220*time.Millisecond {
						name := "Down"
						if dx < 0 {
							name = "Left"
						} else if dx > 0 {
							name = "Right"
						} else if dy < 0 {
							name = "Up"
						}
						_ = g.core.MenuKey(name)
						g.lastMenu[p] = time.Now()
					}
					down := press(ebiten.StandardGamepadButtonRightBottom)
					if down && !g.confirm[p] {
						_ = g.core.MenuKey("Return")
					}
					g.confirm[p] = down
				}
			}
		}
		sources = append(sources, gamecore.Source{Player: p, Name: "pad", Keys: scans})
	}
	if e := g.core.SetInput(sources); e != nil {
		g.notice = e.Error()
	}
	for p, slots := range rising {
		for _, i := range slots {
			g.quick(p, i)
		}
	}
	if e := g.core.Step(250000); e != nil {
		g.notice = "執行停止：" + e.Error()
	}
	g.observe()
	return nil
}
func (g *Game) observe() {
	if g.opts.Observe == "" {
		return
	}
	value := struct {
		FrontendUpdates    uint64                `json:"frontend_updates"`
		MouseLeft          bool                  `json:"mouse_left"`
		Editing            [2]int                `json:"editing"`
		Core               gamecore.Status       `json:"core"`
		Panel              bool                  `json:"panel"`
		Settings           controls.Settings     `json:"settings"`
		Assigned           [2]ebiten.GamepadID   `json:"assigned"`
		SettingsPath       string                `json:"settings_path"`
		Notice             string                `json:"notice"`
		Presentation       gamecore.Presentation `json:"presentation"`
		HDEnabled          bool                  `json:"hd_enabled"`
		HDActive           bool                  `json:"hd_active"`
		HDReason           string                `json:"hd_reason"`
		HDCharactersActive bool                  `json:"hd_characters_active"`
	}{FrontendUpdates: g.updates, MouseLeft: ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft), Editing: g.editing, Core: g.core.Status(), Panel: g.panel, Settings: g.settings, Assigned: g.assigned, SettingsPath: g.settingsPath, Notice: g.notice, Presentation: g.core.Presentation(), HDEnabled: g.hdEnabled, HDActive: g.hdActive, HDReason: g.hdReason, HDCharactersActive: g.hdActive && g.hdCharacters != nil}
	b, e := json.MarshalIndent(value, "", "  ")
	if e == nil {
		e = os.WriteFile(g.opts.Observe+".tmp", b, 0600)
		if e == nil {
			e = os.Rename(g.opts.Observe+".tmp", g.opts.Observe)
		}
	}
	if e != nil {
		g.notice = "觀測檔寫入失敗：" + e.Error()
	}
}
func (g *Game) label(dst *ebiten.Image, box image.Rectangle, value string, ink color.Color) {
	if box.Dy() < 28 || box.Dx() < 4 {
		return
	}
	width, _ := text.Measure(value, g.face, 0)
	if width > float64(box.Dx()) {
		r := []rune(value)
		for len(r) > 0 {
			r = r[:len(r)-1]
			candidate := string(r) + "…"
			w, _ := text.Measure(candidate, g.face, 0)
			if w <= float64(box.Dx()) {
				value = candidate
				break
			}
		}
		if len(r) == 0 {
			value = "…"
		}
	}
	op := &text.DrawOptions{}
	op.GeoM.Translate(float64(box.Min.X), float64(box.Min.Y+(box.Dy()-28)/2))
	op.ColorScale.ScaleWithColor(ink)
	text.Draw(dst, value, g.face, op)
}
func (g *Game) Draw(dst *ebiten.Image) {
	dst.Fill(color.RGBA{11, 16, 27, 255})
	frame := g.core.Presentation()
	var w, h int
	var rgb []byte
	if g.hdAssets != nil && len(frame.Pixels) == 64000 {
		w, h = 320, 200
		rgb = make([]byte, 64000*3)
		for i, v := range frame.Pixels {
			color := frame.Palette[v]
			copy(rgb[i*3:i*3+3], color[:])
		}
	} else {
		w, h, rgb = g.core.RGB()
	}
	if g.texture == nil || g.texture.Bounds().Dx() != w || g.texture.Bounds().Dy() != h {
		g.texture = ebiten.NewImage(w, h)
		g.rgba = make([]byte, w*h*4)
	}
	for i := 0; i < w*h; i++ {
		copy(g.rgba[i*4:i*4+3], rgb[i*3:i*3+3])
		g.rgba[i*4+3] = 255
	}
	g.texture.WritePixels(g.rgba)
	g.hdActive = false
	g.hdReason = "原貌"
	charactersDrawn := false
	if g.hdEnabled && g.hdAssets != nil {
		if g.opts.HDCharacters != "" {
			charactersDrawn, g.hdReason = g.drawCharacterFrame(dst, frame)
			g.hdActive = charactersDrawn
		} else {
			mask, ok, reason := g.hdAssets.Foreground(hd.Frame{Scene: frame.Scene, CameraX: frame.CameraX, BackgroundSHA256: frame.BackgroundSHA256, Pixels: frame.Pixels, Palette: frame.Palette})
			g.hdReason = reason
			if ok {
				g.drawBackground(dst, frame)
				g.texture.WritePixels(mask)
				g.hdActive = true
			}
		}
	}
	op := &ebiten.DrawImageOptions{}
	op.GeoM.Scale(float64(screenRect.Dx())/float64(w), float64(screenRect.Dy())/float64(h))
	op.GeoM.Translate(float64(screenRect.Min.X), float64(screenRect.Min.Y))
	if !charactersDrawn {
		dst.DrawImage(g.texture, op)
	}
	s := g.core.Status()
	state := "對戰中"
	if s.Paused {
		state = "已暫停"
	} else if !s.Battle {
		state = "標題／選角"
	}
	if g.hdActive {
		state += " HD"
	}
	g.label(dst, image.Rect(952, 14, 1096, 50), state, color.RGBA{255, 220, 110, 255})
	if g.panel {
		vector.DrawFilledRect(dst, 24, 80, 1072, 690, color.RGBA{17, 29, 48, 255}, false)
		g.label(dst, image.Rect(52, 94, 1072, 130), "手把與快捷設定　Tab 選欄位，左右調整，Esc 關閉", color.White)
		for p := 0; p < 2; p++ {
			x := 58 + p*530
			g.label(dst, image.Rect(x, 145, x+474, 183), fmt.Sprintf("第 %d 人手把", p+1), color.White)
			g.label(dst, image.Rect(x, 238, x+474, 277), "設定角色，不改變原版選角", color.RGBA{170, 190, 220, 255})
			for i, slot := range controls.Slots {
				g.label(dst, image.Rect(x, 344+i*60, x+66, 390+i*60), slot, color.White)
			}
		}
		g.label(dst, image.Rect(58, 610, 1060, 654), "R1／R2／L1／L2 最多四格，可選第五招或留空。", color.White)
		g.label(dst, image.Rect(58, 658, 1060, 702), "斬四招已啟用；其他角色快捷待驗。近身投技不自動接近。", color.RGBA{255, 220, 110, 255})
		if len(g.devices) == 0 {
			g.label(dst, image.Rect(58, 710, 1060, 748), "尚未偵測到手把。USB／藍牙配對請由作業系統完成。", color.RGBA{170, 190, 220, 255})
		} else {
			for _, d := range g.devices {
				if !d.standard {
					g.label(dst, image.Rect(58, 710, 1060, 748), "部分手把缺少標準配置，目前無法指派這些裝置。", color.RGBA{255, 220, 110, 255})
					break
				}
			}
		}
	} else {
		for p := 0; p < 2; p++ {
			name := "等待選角"
			c := s.Fighters[p]
			if c >= 0 && c < len(controls.Catalog) {
				name = controls.Catalog[c].Name
			}
			g.label(dst, image.Rect(24+p*552, 672, 552+p*552, 708), fmt.Sprintf("第 %d 人：%s", p+1, name), color.White)
		}
	}
	for _, w := range g.widgets() {
		bg := color.RGBA{35, 50, 75, 255}
		if g.panel && w.focus == g.focus && w.focus >= 0 {
			bg = color.RGBA{57, 82, 121, 255}
		}
		vector.DrawFilledRect(dst, float32(w.rect.Min.X), float32(w.rect.Min.Y), float32(w.rect.Dx()), float32(w.rect.Dy()), bg, false)
		ink := color.RGBA{237, 243, 255, 255}
		if w.disabled {
			ink = color.RGBA{120, 139, 165, 255}
		}
		g.label(dst, image.Rect(w.rect.Min.X+10, w.rect.Min.Y+4, w.rect.Max.X-10, w.rect.Max.Y-4), w.label, ink)
	}
	g.label(dst, image.Rect(24, 778, 1096, 814), g.notice, color.RGBA{255, 220, 110, 255})
	if g.capture {
		g.capture = false
		path := g.opts.Capture
		if path == "" {
			path = filepath.Join(filepath.Dir(g.settingsPath), "screenshot.png")
		}
		pixels := make([]byte, Width*Height*4)
		dst.ReadPixels(pixels)
		img := &image.RGBA{Pix: pixels, Stride: Width * 4, Rect: image.Rect(0, 0, Width, Height)}
		f, e := os.Create(path + ".tmp")
		if e == nil {
			e = png.Encode(f, img)
			if closeErr := f.Close(); e == nil {
				e = closeErr
			}
		}
		if e != nil {
			g.notice = "擷取失敗：" + e.Error()
		}
		if e == nil && g.opts.Observe != "" && g.hdAssets != nil && len(frame.Pixels) == 64000 {
			e = os.WriteFile(path+".idx", frame.Pixels, 0600)
			if e == nil {
				var data []byte
				data, e = json.Marshal(frame.Palette)
				if e == nil {
					e = os.WriteFile(path+".palette.json", data, 0600)
				}
			}
			if e != nil {
				g.notice = "畫格證據寫入失敗：" + e.Error()
			}
		}
		if e == nil && g.opts.Observe != "" && g.opts.HDCharacters != "" && frame.LayersComplete {
			var data []byte
			data, e = json.MarshalIndent(frame, "", "  ")
			if e == nil {
				e = os.WriteFile(path+".frame.json", data, 0600)
			}
			for i, layer := range frame.Layers {
				if e != nil {
					break
				}
				e = os.WriteFile(fmt.Sprintf("%s.layer-%02d.idx", path, i), layer.Indices, 0600)
				if e == nil {
					e = os.WriteFile(fmt.Sprintf("%s.layer-%02d.mask", path, i), layer.Coverage, 0600)
				}
			}
		}
		if e == nil {
			e = os.Rename(path+".tmp", path)
		}
		if e != nil {
			_ = os.Remove(path + ".tmp")
			g.notice = "擷取失敗：" + e.Error()
		}
	}
}
func (g *Game) Layout(int, int) (int, int) { return Width, Height }
