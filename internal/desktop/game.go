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
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

//go:embed assets/NotoSansCJKtc-Regular.otf assets/OFL.txt assets/source.json
var assets embed.FS

const Width, Height = 1120, 820

var screenRect = image.Rect(80, 64, 1040, 664)

type Options struct {
	CaptureFPS                                                       int
	AudioAssets                                                      string
	MuteAudio                                                        bool
	HDScreens                                                        string
	Training                                                         bool
	Root, DataDir, Observe, Capture, HDAssets, HDCharacters, Version string
	QuitAfter                                                        time.Duration
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
	frameDeadline         time.Time
	performanceState      renderPerformance
	battleKey             battleRenderKey
	battleCached          bool
	battleCacheHits       uint64
	originalAudio         *originalAudioPlayer
	screenArtLoaded       bool
	titleHDPaint          *titleHDPaint
	titleHDActive         bool
	selectionHD           *selectionHDAssets
	selectionHDView       *selectionHDState
	selectionHDActive     bool
	resultHD              *resultHDAssets
	resultHDView          *resultHDState
	resultHDActive        bool
	backgroundTextures    map[*hd.Assets]*ebiten.Image
	hdVictories           *hd.Victories
	hdVictoryActive       bool
	victoryCaptureBefore  []byte
	victoryCaptureAfter   []byte
	core                  *gamecore.Core
	settings              controls.Settings
	settingsPath          string
	settingsWritable      bool
	face                  *text.GoTextFace
	texture               *ebiten.Image
	frameCanvas           *ebiten.Image
	backgroundMaskTexture *ebiten.Image
	activeRect            image.Rectangle
	paintRect             image.Rectangle
	rgba                  []byte
	devices               []device
	assigned              [2]ebiten.GamepadID
	armed                 [2]bool
	keyboardArmed         bool
	keyboardQuick         [2][4]bool
	quickRequests         [2][4]uint64
	keyboardPanel         bool
	binding               bool
	bindingArmed          bool
	bindingPlayer         int
	bindingAction         int
	starts                [2]bool
	shoulders             [2][4]bool
	confirm               [2]bool
	lastMenu              [2]time.Time
	panel                 bool
	editing               [2]int
	focus                 int
	notice                string
	opts                  Options
	started               time.Time
	capture               bool
	updates               uint64
	hdAssets              *hd.Assets
	hdTexture             *ebiten.Image
	hdEnabled             bool
	hdActive              bool
	hdReason              string
	hdCharacters          *hd.Characters
	layerTextures         []*ebiten.Image
	layerRGBA             [][]byte
	actorTextures         map[*hd.PoseArt]*ebiten.Image
	hdHUD                 *hd.HUD
	hdHUDRequired         bool
	hdHUDActive           bool
	hudLabels             map[string]*ebiten.Image
	hudWinMarker          *ebiten.Image
	hdShadows             *hd.Shadows
	hdShadowsActive       bool
	shadowTexture         *ebiten.Image
	shadowRGBA            []byte
	shadowDraws           [2]renderdata.Shadow
	shadowCamera          int
	shadowCaptureBefore   []byte
	shadowCaptureAfter    []byte
	hdRounds              *hd.Rounds
	hdRoundsActive        bool
	roundCaptureBefore    []byte
	roundCaptureAfter     []byte
}

func New(opts Options) (*Game, error) {
	if e := os.MkdirAll(opts.DataDir, 0755); e != nil {
		return nil, e
	}
	c, e := gamecore.New(opts.Root, filepath.Join(opts.DataDir, "dos"))
	if e != nil {
		return nil, e
	}
	c.EnableDisplay()
	c.EnableVictory()
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
				g.hdHUDRequired = true
				g.hdHUD, e = hd.LoadHUD(opts.Root)
				if e == nil {
					c.EnableHUD()
				} else {
					g.notice = "HD 介面來源不完整，保留原貌。"
				}
				g.hdShadows, e = hd.LoadShadows(opts.Root)
				if e == nil {
					c.EnableShadows()
				} else {
					g.notice = "HD 陰影來源不完整，保留原貌。"
				}
				g.hdRounds, e = hd.LoadRounds(opts.Root)
				if e == nil {
					c.EnableRounds()
				} else {
					g.notice = "HD 開場訊息來源不完整，保留原貌。"
				}
			} else {
				c.EnableLayers()
			}
		}
	}
	if g.hdHUDRequired {
		g.hdVictories, e = hd.LoadVictories(opts.Root)
		if e != nil {
			g.notice = "HD 勝負文字來源不完整，保留原貌。"
		}
	}
	if opts.Training {
		g.toggleTraining()
	}
	g.selectionHD = loadSelectionHD(opts.Root, nil, nil)
	g.resultHD = loadResultHD(opts.Root, nil)
	if opts.HDScreens != "" {
		images, err := hd.LoadScreens(opts.HDScreens)
		if err != nil {
			g.notice = "HD 畫面素材無法完整載入，保留原貌：" + err.Error()
		} else {
			g.screenArtLoaded = true
			textures := map[string]*ebiten.Image{}
			for key, im := range images {
				textures[key] = ebiten.NewImageFromImageWithOptions(im, &ebiten.NewImageFromImageOptions{Unmanaged: true})
			}
			g.titleHDPaint = loadTitleHD(opts.Root, textures, images["title-logo"])
			g.selectionHD = loadSelectionHD(opts.Root, textures, images["title-logo"])
			g.resultHD = loadResultHD(opts.Root, textures)
		}
	}
	g.initOriginalAudio()
	return g, nil
}
func (g *Game) Close() {
	if g.originalAudio != nil {
		g.originalAudio.close()
	}
	g.core.Close()
}
func (g *Game) pause(value bool) {
	g.core.Pause(value)
	g.armed = [2]bool{}
	g.keyboardArmed = false
	g.keyboardQuick = [2][4]bool{}
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
		g.notice = "兩名玩家的鍵盤與各角色四格設定已保存。"
	}
}
func (g *Game) openSettings() {
	g.binding = false
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

func (g *Game) toggleTraining() {
	enabled := !g.core.Status().Training.Requested
	g.core.SetTraining(enabled)
	g.keyboardArmed = false
	g.armed = [2]bool{}
	g.shoulders = [2][4]bool{}
	if enabled {
		g.notice = "練習已開啟：雙方滿血、停止倒數、電腦中立。F9 可關閉。"
	} else {
		g.notice = "練習已關閉：恢復扣血、倒數及電腦操作。"
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
	g.quickRequests[p][slot]++
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
	if g.keyboardPanel {
		return g.keyboardFields()
	}
	var out []widget
	for p := 0; p < 2; p++ {
		x := 58 + p*530
		c := controls.Catalog[g.editing[p]]
		out = append(out, widget{image.Rect(x, 190, x+474, 232), fmt.Sprintf("第 %d 人：%s", p+1, g.deviceName(p)), func(delta int) { g.nextDevice(p, delta) }, p * 6, false})
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
		{image.Rect(342, 12, 564, 52), "控制與快捷設定", func(int) { g.openSettings() }, -1, false},
		{image.Rect(576, 12, 710, 52), "全螢幕", func(int) { ebiten.SetFullscreen(!ebiten.IsFullscreen()) }, -1, false},
		{image.Rect(722, 12, 940, 52), "原貌／HD 背景", func(int) { g.hdEnabled = !g.hdEnabled; g.notice = "呈現已切換，角色與操作沿用原版。" }, -1, g.hdAssets == nil && !g.screenArtLoaded},
	}
	if g.opts.HDCharacters != "" {
		out[4].label = "原貌／HD 畫面"
		out[4].action = func(int) { g.hdEnabled = !g.hdEnabled; g.notice = "已切換原貌／HD。" }
	}
	trainingLabel := "練習：關"
	if s.Training.Requested {
		trainingLabel = "練習：待"
		if s.Training.Active {
			trainingLabel = "練習：開"
		}
	}
	out = append(out, widget{image.Rect(952, 12, 1096, 52), trainingLabel, func(int) { g.toggleTraining() }, -1, false})
	audioLabel := "原音未匯入"
	if g.originalAudio != nil {
		audioLabel = "原音：關"
		if g.originalAudio.enabled {
			audioLabel = "原音：開"
		}
	}
	out = append(out, widget{image.Rect(952, 778, 1096, 814), audioLabel, func(int) {
		if g.originalAudio != nil {
			g.originalAudio.enabled = !g.originalAudio.enabled
		}
	}, -1, g.originalAudio == nil})
	if g.panel {
		out = append(out,
			widget{image.Rect(58, 140, 270, 178), "手把／角色四格", func(int) { g.keyboardPanel = false; g.binding = false; g.focus = 0 }, -1, false},
			widget{image.Rect(288, 140, 500, 178), "鍵盤組態", func(int) { g.keyboardPanel = true; g.binding = false; g.focus = 0 }, -1, false})
		if g.keyboardPanel {
			out = append(out, widget{image.Rect(58, 676, 350, 714), "兩人鍵盤還原預設", func(int) {
				g.settings.Keyboard = controls.KeyboardDefaults()
				g.binding = false
				g.keyboardArmed = false
				g.save()
			}, -1, false})
		}
		return append(out, g.fields()...)
	}
	if s.Selection != nil {
		return out
	}
	for p := 0; p < 2; p++ {
		for slot := 0; slot < 4; slot++ {
			i := slot
			label := controls.Slots[slot]
			if key := g.settings.Keyboard[p][10+slot]; key != "" {
				label = controls.KeyLabel(key) + "／" + label
			}
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

var dirs = [2][3][3]uint8{{{0x10, 0x11, 0x12}, {0x1e, 0, 0x20}, {0x2c, 0x2d, 0x2e}}, {{0x47, 0x48, 0x49}, {0x4b, 0, 0x4d}, {0x4f, 0x50, 0x51}}}

func (g *Game) Update() error {
	if g.opts.Observe != "" {
		started := time.Now()
		defer func() { g.performanceState.UpdateMS = float64(time.Since(started)) / float64(time.Millisecond) }()
	}
	defer g.updateOriginalAudio()
	g.updates++
	if g.opts.QuitAfter > 0 && time.Since(g.started) > g.opts.QuitAfter {
		return ebiten.Termination
	}
	g.scanDevices()
	if g.panel && g.binding {
		if !ebiten.IsFocused() {
			g.binding = false
			g.bindingArmed = false
			g.notice = "失去焦點，已取消重綁。"
		} else {
			g.captureBinding()
		}
		g.observe()
		return nil
	}
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
	if inpututil.IsKeyJustPressed(ebiten.KeyF9) {
		g.toggleTraining()
		g.observe()
		return nil
	}
	if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) {
		x, y := ebiten.CursorPosition()
		pt := image.Pt(x, y)
		if character, ok := g.selectionPortraitAt(pt); ok {
			if e := g.core.ChooseCharacter(character); e != nil {
				g.notice = e.Error()
			}
			g.observe()
			return nil
		}
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
		if inpututil.IsKeyJustPressed(ebiten.KeyF8) {
			g.keyboardPanel = !g.keyboardPanel
			g.focus = 0
			g.observe()
			return nil
		}
		count := len(g.fields())
		if inpututil.IsKeyJustPressed(ebiten.KeyTab) || inpututil.IsKeyJustPressed(ebiten.KeyArrowDown) {
			g.focus = (g.focus + 1) % count
		}
		if inpututil.IsKeyJustPressed(ebiten.KeyArrowUp) {
			g.focus = (g.focus + count - 1) % count
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
	keyboard, keyboardDown, neutral := g.settings.KeyboardInput(func(name string) bool { return keyboardPressed(keyCode(name)) })
	if neutral {
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
		mouseRect := g.activeRect
		if mouseRect.Empty() {
			mouseRect = screenRect
		}
		if inpututil.IsMouseButtonJustPressed(ebiten.MouseButtonLeft) && image.Pt(x, y).In(mouseRect) {
			if e := g.core.Mouse((x-mouseRect.Min.X)/3, (y-mouseRect.Min.Y)/3, true); e != nil {
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
			for _, k := range keyboard[p] {
				ks = append(ks, k)
			}
		}
		sources = append(sources, gamecore.Source{Player: p, Name: "keyboard", Keys: ks})
	}
	var rising [2][]int
	for p, row := range keyboardDown {
		for i, down := range row {
			if g.keyboardArmed && s.Battle && !s.Paused && down && !g.keyboardQuick[p][i] {
				rising[p] = append(rising[p], i)
			}
			g.keyboardQuick[p][i] = down
		}
	}
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
	var stepStarted time.Time
	if g.opts.Observe != "" {
		stepStarted = time.Now()
	}
	if e := g.core.Step(250000); e != nil {
		g.notice = "執行停止：" + e.Error()
	}
	if g.opts.Observe != "" {
		g.performanceState.StepMS = float64(time.Since(stepStarted)) / float64(time.Millisecond)
	}
	g.observe()
	return nil
}
func (g *Game) observe() {
	if g.opts.Observe == "" {
		return
	}
	value := struct {
		Performance        renderPerformance     `json:"performance"`
		Audio              originalAudioState    `json:"audio"`
		FrontendUpdates    uint64                `json:"frontend_updates"`
		Version            string                `json:"version"`
		MouseLeft          bool                  `json:"mouse_left"`
		Editing            [2]int                `json:"editing"`
		Core               gamecore.Status       `json:"core"`
		Panel              bool                  `json:"panel"`
		KeyboardPanel      bool                  `json:"keyboard_panel"`
		Binding            bool                  `json:"binding"`
		QuickRequests      [2][4]uint64          `json:"quick_requests"`
		Settings           controls.Settings     `json:"settings"`
		Assigned           [2]ebiten.GamepadID   `json:"assigned"`
		SettingsPath       string                `json:"settings_path"`
		Notice             string                `json:"notice"`
		Presentation       gamecore.Presentation `json:"presentation"`
		HDEnabled          bool                  `json:"hd_enabled"`
		HDActive           bool                  `json:"hd_active"`
		HDReason           string                `json:"hd_reason"`
		TitleHDActive      bool                  `json:"title_hd_active"`
		SelectionHDActive  bool                  `json:"selection_hd_active"`
		SelectionHD        *selectionHDState     `json:"selection_hd,omitempty"`
		ResultHDActive     bool                  `json:"result_hd_active"`
		ResultHD           *resultHDState        `json:"result_hd,omitempty"`
		HDCharactersActive bool                  `json:"hd_characters_active"`
		HDHUDActive        bool                  `json:"hd_hud_active"`
		HDShadowsActive    bool                  `json:"hd_shadows_active"`
		HDRoundsActive     bool                  `json:"hd_rounds_active"`
	}{Audio: g.originalAudioState(), FrontendUpdates: g.updates, Version: g.opts.Version, MouseLeft: ebiten.IsMouseButtonPressed(ebiten.MouseButtonLeft), Editing: g.editing, Core: g.core.Status(), Panel: g.panel, KeyboardPanel: g.keyboardPanel, Binding: g.binding, QuickRequests: g.quickRequests, Settings: g.settings, Assigned: g.assigned, SettingsPath: g.settingsPath, Notice: g.notice, Presentation: g.core.Presentation(), HDEnabled: g.hdEnabled, HDActive: g.hdActive, HDReason: g.hdReason, TitleHDActive: g.titleHDActive, SelectionHDActive: g.selectionHDActive, SelectionHD: g.selectionHDView, ResultHDActive: g.resultHDActive, ResultHD: g.resultHDView, HDCharactersActive: g.hdActive && g.hdCharacters != nil && !g.titleHDActive && !g.selectionHDActive && !g.resultHDActive, HDHUDActive: g.hdHUDActive, HDShadowsActive: g.hdShadowsActive, HDRoundsActive: g.hdRoundsActive}
	value.Performance = g.renderPerformance()
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
	if g.opts.CaptureFPS == 60 {
		g.waitRenderFrame()
	}
	if g.opts.Observe != "" {
		started := time.Now()
		if !g.performanceState.last.IsZero() {
			g.performanceState.IntervalMS = float64(started.Sub(g.performanceState.last)) / float64(time.Millisecond)
		}
		g.performanceState.last = started
		g.performanceState.Draws++
		defer g.finishPerformanceDraw(started)
	}
	window := dst
	if g.frameCanvas == nil {
		g.frameCanvas = ebiten.NewImage(Width, Height)
	}
	frame := g.core.Presentation()
	key := battleRenderKey{serial: frame.Serial, steps: frame.Steps, hd: g.hdEnabled, victory: frame.Victory}
	eligible := g.hdEnabled && frame.Serial > 0 && len(frame.Pixels) == 64000
	reuse := eligible && !g.capture && g.battleCached && g.battleKey == key
	if reuse {
		g.battleCacheHits++
	}
	var w, h int
	var rgb []byte
	var display *renderdata.Scanout
	displayError := ""
	selectionFiltered := false
	palette := frame.Palette
	var mapped bool
	if !reuse {
		g.frameCanvas.Fill(color.RGBA{11, 16, 27, 255})
		if len(frame.Pixels) == 64000 {
			w, h = 320, 200
			rgb = make([]byte, 64000*3)
			for i, v := range frame.Pixels {
				color := frame.Palette[v]
				copy(rgb[i*3:i*3+3], color[:])
			}
			display, displayError = frame.Scanout, frame.ScanoutError
		} else {
			w, h, rgb = g.core.RGB()
			var err error
			display, palette, err = g.core.LiveDisplay()
			if clean := g.core.SelectionDisplay(); clean != nil {
				display = clean
				selectionFiltered = true
			}
			if err != nil {
				displayError = err.Error()
			}
		}
		mapped = display.Valid()
		g.activeRect, g.paintRect = screenRect, screenRect
		if mapped {
			w, h = display.Width, display.Height
			rgb = make([]byte, w*h*3)
			for i, v := range display.Indices {
				c := palette[v]
				copy(rgb[i*3:i*3+3], c[:])
			}
			g.activeRect = image.Rect(screenRect.Min.X, screenRect.Min.Y+(600-h*3)/2, screenRect.Max.X, screenRect.Min.Y+(600-h*3)/2+h*3)
			g.paintRect = screenRect.Add(image.Pt(0, (600-h*3)/2-(display.StartByte/320)*3))
		}
		dst = g.frameCanvas.SubImage(g.activeRect).(*ebiten.Image)
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
		g.titleHDActive, g.selectionHDActive, g.resultHDActive = false, false, false
		g.selectionHDView = nil
		g.resultHDView = nil
		g.hdHUDActive = false
		g.hdShadowsActive = false
		g.hdRoundsActive = false
		g.hdVictoryActive = false
		g.victoryCaptureBefore, g.victoryCaptureAfter = nil, nil
		g.roundCaptureBefore, g.roundCaptureAfter = nil, nil
		g.shadowCaptureBefore, g.shadowCaptureAfter = nil, nil
		g.hdReason = "原貌"
		charactersDrawn := false
		backgroundOnly := false
		if g.hdEnabled && g.hdAssets != nil && mapped && g.hdAssets.DisplayMatch(display, frame.Pixels, frame.VRAMTail, hd.Frame{Scene: frame.Scene, CameraX: frame.CameraX, BackgroundSHA256: frame.BackgroundSHA256, Palette: frame.Palette}) {
			if g.opts.HDCharacters != "" {
				charactersDrawn, g.hdReason = g.drawCharacterFrame(dst, frame)
				g.hdActive = charactersDrawn
			} else {
				mask, ok, reason := g.hdAssets.Foreground(hd.Frame{Scene: frame.Scene, CameraX: frame.CameraX, BackgroundSHA256: frame.BackgroundSHA256, Pixels: frame.Pixels, Palette: frame.Palette})
				g.hdReason = reason
				if ok {
					g.drawBackground(dst, frame)
					if g.backgroundMaskTexture == nil {
						g.backgroundMaskTexture = ebiten.NewImage(320, 200)
					}
					g.backgroundMaskTexture.WritePixels(mask)
					backgroundOnly = true
					g.hdActive = true
				}
			}
		} else if g.hdEnabled {
			g.hdReason = "顯示來源或尾列未對應，保留原貌"
		}
		if !mapped && displayError != "" {
			g.hdReason = "顯示映射未支援，保留線性原貌：" + displayError
		}
		if backgroundOnly {
			op := &ebiten.DrawImageOptions{}
			op.GeoM.Scale(3, 3)
			op.GeoM.Translate(float64(g.paintRect.Min.X), float64(g.paintRect.Min.Y))
			dst.DrawImage(g.backgroundMaskTexture, op)
		}
		op := &ebiten.DrawImageOptions{}
		op.GeoM.Scale(float64(g.activeRect.Dx())/float64(w), float64(g.activeRect.Dy())/float64(h))
		op.GeoM.Translate(float64(g.activeRect.Min.X), float64(g.activeRect.Min.Y))
		if !charactersDrawn && !backgroundOnly {
			dst.DrawImage(g.texture, op)
		}
		g.selectionHDView = g.selectionHDState()
		g.resultHDView = g.resultHDState()
		if g.hdEnabled && mapped && len(frame.Pixels) == 0 {
			if title := g.core.TitleHD(); title != nil && g.drawTitleHD(dst, title) {
				g.titleHDActive = true
				g.hdActive = true
				g.hdReason = "HD 標題與主選單"
			} else if view := g.selectionHDView; view != nil && g.drawSelectionHD(dst, view) {
				g.selectionHDView = view
				g.selectionHDActive = true
				g.hdActive = true
				g.hdReason = "HD 選角"
			} else if view := g.resultHDView; view != nil && g.drawResultHD(dst, view) {
				g.resultHDView = view
				g.resultHDActive = true
				g.hdActive = true
				g.hdReason = "HD 結果與繼續介面"
			}
		}
	}
	g.battleCached, g.battleKey = eligible, key
	dst = window
	dst.DrawImage(g.frameCanvas, nil)
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
	if s.Training.Active {
		state += "／練習中"
	} else if s.Training.Requested {
		state += "／" + s.Training.Reason
	}
	if g.panel {
		vector.DrawFilledRect(dst, 24, 80, 1072, 690, color.RGBA{17, 29, 48, 255}, false)
		g.label(dst, image.Rect(52, 94, 1072, 130), "控制與快捷設定　F8 切換頁面，Tab 選欄位，Esc 關閉", color.White)
		if g.keyboardPanel {
			g.drawKeyboardLabels(dst)
		} else {
			for p := 0; p < 2; p++ {
				x := 58 + p*530
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
		}
	} else if s.Selection != nil {
		g.selectionLabel(dst, s.Selection)
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
		paddingY := 4
		if w.rect.Dy() < 36 {
			paddingY = 0
		}
		g.label(dst, image.Rect(w.rect.Min.X+10, w.rect.Min.Y+paddingY, w.rect.Max.X-10, w.rect.Max.Y-paddingY), w.label, ink)
	}
	g.label(dst, image.Rect(24, 778, 940, 814), state+"　"+g.notice, color.RGBA{255, 220, 110, 255})
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
		if e == nil && g.opts.Observe != "" {
			liveW, liveH, liveRGB := g.core.RGB()
			source := "live-original"
			if selectionFiltered {
				source = "selection-filtered-original"
			}
			if len(frame.Pixels) == 64000 {
				source = "completed-battle-frame"
			}
			metadata := map[string]any{"audio": g.originalAudioState(), "core": g.core.Status(), "original_source": source, "selected_width": w, "selected_height": h, "live_width": liveW, "live_height": liveH, "presentation_serial": frame.Serial, "presentation_steps": frame.Steps, "title_hd_active": g.titleHDActive, "selection_hd_active": g.selectionHDActive, "selection_hd": g.selectionHDView, "result_hd_active": g.resultHDActive, "result_hd": g.resultHDView, "hd_enabled": g.hdEnabled, "hd_active": g.hdActive, "hd_shadows_active": g.hdShadowsActive, "display_applied": mapped, "display_error": displayError, "active_rect": g.activeRect, "paint_rect": g.paintRect, "scanout": display}
			var data []byte
			data, e = json.MarshalIndent(metadata, "", "  ")
			if e == nil {
				e = os.WriteFile(path+".capture.json", data, 0600)
			}
			if e == nil {
				e = os.WriteFile(path+".selected.rgb", rgb, 0600)
			}
			if e == nil {
				e = os.WriteFile(path+".live.rgb", liveRGB, 0600)
			}
			if e == nil && mapped {
				e = os.WriteFile(path+".display.idx", display.Indices, 0600)
			}
			if e == nil && len(frame.VRAMTail) > 0 {
				e = os.WriteFile(path+".vram-tail", frame.VRAMTail, 0600)
			}
		}
		if e == nil && g.opts.Observe != "" {
			var data []byte
			data, e = json.Marshal(palette)
			if e == nil {
				e = os.WriteFile(path+".screen-palette.json", data, 0600)
			}
		}
		if e == nil && g.opts.Observe != "" && len(frame.Pixels) == 64000 {
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
			if e == nil && frame.HUD != nil {
				for suffix, pixels := range map[string][]byte{".hud.bitmap": frame.HUD.Bitmap, ".hud-under.idx": frame.HUD.Underlay.Indices, ".hud-under.mask": frame.HUD.Underlay.Coverage} {
					if e = os.WriteFile(path+suffix, pixels, 0600); e != nil {
						break
					}
				}
			}
			if e == nil && frame.Shadows != nil {
				for suffix, pixels := range map[string][]byte{".shadow-under.idx": frame.Shadows.Underlay.Indices, ".shadow-under.mask": frame.Shadows.Underlay.Coverage} {
					if e = os.WriteFile(path+suffix, pixels, 0600); e != nil {
						break
					}
				}
			}
			if e == nil && frame.RoundMessage != nil {
				for suffix, pixels := range map[string][]byte{".round.source": frame.RoundMessage.Source, ".round-under.idx": frame.RoundMessage.Underlay.Indices, ".round-under.mask": frame.RoundMessage.Underlay.Coverage} {
					if e = os.WriteFile(path+suffix, pixels, 0600); e != nil {
						break
					}
				}
			}
			if e == nil && frame.Victory != nil {
				for suffix, pixels := range map[string][]byte{".victory-under.idx": frame.Victory.Underlay.Indices, ".victory-under.mask": frame.Victory.Underlay.Coverage} {
					if e = os.WriteFile(path+suffix, pixels, 0600); e != nil {
						break
					}
				}
				for i, draw := range frame.Victory.Draws {
					if e != nil {
						break
					}
					e = os.WriteFile(fmt.Sprintf("%s.victory-%02d.source", path, i), draw.Source, 0600)
				}
			}
			if e == nil && g.hdVictoryActive && len(g.victoryCaptureBefore) > 0 && len(g.victoryCaptureAfter) > 0 {
				for suffix, pixels := range map[string][]byte{".victory-render-before.rgba": g.victoryCaptureBefore, ".victory-render-after.rgba": g.victoryCaptureAfter} {
					if e = os.WriteFile(path+suffix, pixels, 0600); e != nil {
						break
					}
				}
			}
			if e == nil && g.hdRoundsActive && len(g.roundCaptureBefore) > 0 && len(g.roundCaptureAfter) > 0 {
				for suffix, pixels := range map[string][]byte{".round-render-before.rgba": g.roundCaptureBefore, ".round-render-after.rgba": g.roundCaptureAfter} {
					if e = os.WriteFile(path+suffix, pixels, 0600); e != nil {
						break
					}
				}
			}
			if e == nil && g.hdShadowsActive && len(g.shadowCaptureBefore) > 0 && len(g.shadowCaptureAfter) > 0 {
				for suffix, pixels := range map[string][]byte{".shadow-render-before.rgba": g.shadowCaptureBefore, ".shadow-render-after.rgba": g.shadowCaptureAfter, ".shadow-alpha.rgba": g.shadowRGBA} {
					if e = os.WriteFile(path+suffix, pixels, 0600); e != nil {
						break
					}
				}
				if e == nil {
					var data []byte
					data, e = json.Marshal(map[string]any{"serial": frame.Serial, "width": screenRect.Dx(), "height": len(g.shadowRGBA) / (screenRect.Dx() * 4), "x": g.paintRect.Min.X, "y": g.paintRect.Min.Y + 178*screenRect.Dy()/200})
					if e == nil {
						e = os.WriteFile(path+".shadow-render.json", data, 0600)
					}
				}
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
