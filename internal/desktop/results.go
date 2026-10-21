// 049: full-source result recognition and HD rendering, original input unchanged.
package desktop

import (
	"bytes"
	"crypto/sha256"
	"fmt"
	"image"
	"image/color"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/text/v2"
)

type resultRaster struct {
	Width, Height int
	RGB           []byte
}
type resultReferences struct {
	Continue                            resultContinueReferences
	Inputs                              map[string]string
	Paper                               []byte
	Left, Right, Outcomes, Flags, Names []resultRaster
}
type resultArtFile struct {
	Key, File, SHA string
	Width, Height  int
	Private        bool
}
type resultHDRecipe struct {
	ReferenceSHA string
	Art          []resultArtFile
}
type resultHDState struct {
	Continue      *resultContinueState `json:"continue,omitempty"`
	Characters    [2]int               `json:"characters"`
	Winner        int                  `json:"winner_player"`
	Outcome       int                  `json:"outcome_record"`
	Flags         [2]int               `json:"flag_records"`
	NamePositions [2]int               `json:"name_positions"`
	OriginalSHA   string               `json:"original_rgb_sha256"`
}
type resultHDAssets struct {
	refs      resultReferences
	art       map[string]*ebiten.Image
	loaded    bool
	lastSHA   string
	lastState *resultHDState
}

func resultDigest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func loadResultHD(root string, images map[string]*ebiten.Image) *resultHDAssets {
	refs, e := buildResultReferences(root)
	if e != nil {
		return nil
	}
	return &resultHDAssets{refs: refs, art: images, loaded: len(images) == 33}
}

func resultCrop(rgb []byte, x, y, w, h int) []byte {
	if x < 0 || y < 0 || x+w > 320 || y+h > 200 || len(rgb) != 192000 {
		return nil
	}
	out := make([]byte, w*h*3)
	for j := 0; j < h; j++ {
		copy(out[j*w*3:(j+1)*w*3], rgb[((y+j)*320+x)*3:((y+j)*320+x+w)*3])
	}
	return out
}
func resultMatch(rgb []byte, patterns []resultRaster, x, y, w, h int) int {
	raw := resultCrop(rgb, x, y, w, h)
	found := -1
	for i, p := range patterns {
		if p.Width == w && p.Height == h && bytes.Equal(raw, p.RGB) {
			if found >= 0 {
				return -1
			}
			found = i
		}
	}
	return found
}
func resultStamp(dst []byte, p resultRaster, x, y int) {
	for j := 0; j < p.Height; j++ {
		copy(dst[((y+j)*320+x)*3:((y+j)*320+x+p.Width)*3], p.RGB[j*p.Width*3:(j+1)*p.Width*3])
	}
}
func (g *Game) resultHDState() *resultHDState {
	a := g.resultHD
	if a == nil || g.core.Status().Battle {
		return nil
	}
	display, palette, e := g.core.LiveDisplay()
	if e != nil || display == nil || !display.Valid() || display.Width != 320 || display.Height != 200 || display.StartByte != 0 || display.PitchByte != 320 {
		return nil
	}
	rgb := make([]byte, 192000)
	for i, v := range display.Indices {
		copy(rgb[i*3:i*3+3], palette[v][:])
	}
	digest := fmt.Sprintf("%s/%s/%d", resultDigest(rgb), resultDigest(display.Indices), g.core.Status().Mode)
	if digest == a.lastSHA {
		return a.lastState
	}
	a.lastSHA = digest
	a.lastState = a.identifyPlainResult(rgb)
	// Core status mode is only exposed during battle. Full SH reconstruction identifies this UI.
	if a.lastState == nil {
		a.lastState = a.identifyContinueResult(rgb, display.Indices, palette)
	}
	return a.lastState
}
func (a *resultHDAssets) identifyPlainResult(rgb []byte) *resultHDState {
	s := &resultHDState{OriginalSHA: resultDigest(rgb)}
	left := resultMatch(rgb, a.refs.Left, 18, 34, 89, 89)
	right := resultMatch(rgb, a.refs.Right, 214, 34, 89, 89)
	if left < 0 || right < 0 || left/11 != right/11 {
		return nil
	}
	s.Winner = left / 11
	s.Characters = [2]int{left % 11, right % 11}
	s.Outcome = resultMatch(rgb, a.refs.Outcomes, 128, 15, 65, 169)
	s.Flags = [2]int{resultMatch(rgb, a.refs.Flags, 30, 154, 65, 33), resultMatch(rgb, a.refs.Flags, 226, 154, 65, 33)}
	if s.Characters[0] < 0 || s.Characters[1] < 0 || s.Outcome < 0 || s.Flags[0] < 0 || s.Flags[1] < 0 {
		return nil
	}
	for side, ch := range s.Characters {
		p := a.refs.Names[ch]
		begin, end := 0, 128
		if side == 1 {
			begin, end = 196, 320
		}
		found := -1
		for x := begin; x+p.Width <= end; x++ {
			if bytes.Equal(resultCrop(rgb, x, 134, p.Width, p.Height), p.RGB) {
				if found >= 0 {
					return nil
				}
				found = x
			}
		}
		if found < 0 {
			return nil
		}
		s.NamePositions[side] = found
	}
	expected := append([]byte(nil), a.refs.Paper...)
	resultStamp(expected, a.refs.Left[left], 18, 34)
	resultStamp(expected, a.refs.Right[right], 214, 34)
	resultStamp(expected, a.refs.Outcomes[s.Outcome], 128, 15)
	resultStamp(expected, a.refs.Flags[s.Flags[0]], 30, 154)
	resultStamp(expected, a.refs.Flags[s.Flags[1]], 226, 154)
	for side, ch := range s.Characters {
		resultStamp(expected, a.refs.Names[ch], s.NamePositions[side], 134)
	}
	if !bytes.Equal(expected, rgb) {
		return nil
	}
	return s
}

func (g *Game) resultText(dst *ebiten.Image, value string, box image.Rectangle, size float64, thick bool) {
	face := &text.GoTextFace{Source: g.face.Source, Size: size}
	w, h := text.Measure(value, face, 0)
	usableW, usableH := float64(box.Dx()-6), float64(box.Dy()-6)
	factor := 1.0
	if w > usableW {
		factor = usableW / w
	}
	if h*factor > usableH {
		factor = usableH / h
	}
	face.Size *= factor
	w, h = text.Measure(value, face, 0)
	x, y := float64(box.Min.X)+(float64(box.Dx())-w)/2, float64(box.Min.Y)+(float64(box.Dy())-h)/2
	offsets := [][2]float64{{0, 0}}
	if thick {
		offsets = append(offsets, [2]float64{-1, 0}, [2]float64{1, 0}, [2]float64{0, -1}, [2]float64{0, 1})
	}
	for _, d := range offsets {
		op := &text.DrawOptions{}
		op.GeoM.Translate(x+d[0], y+d[1])
		op.ColorScale.ScaleWithColor(color.RGBA{17, 17, 17, 255})
		text.Draw(dst, value, face, op)
	}
}
func (g *Game) drawResultHD(dst *ebiten.Image, s *resultHDState) bool {
	a := g.resultHD
	if a == nil || !a.loaded || s == nil || s.Flags[0] > 6 || s.Flags[1] > 6 {
		return false
	}
	draw := func(key string, x, y, w, h int, mirror bool) {
		im := a.art[key]
		op := &ebiten.DrawImageOptions{Filter: ebiten.FilterLinear}
		sx, sy := float64(w*3)/float64(im.Bounds().Dx()), float64(h*3)/float64(im.Bounds().Dy())
		if mirror {
			sx = -sx
			x += w
		}
		op.GeoM.Scale(sx, sy)
		op.GeoM.Translate(float64(g.activeRect.Min.X+x*3), float64(g.activeRect.Min.Y+y*3))
		dst.DrawImage(im, op)
	}
	draw("paper", 0, 0, 320, 200, false)
	leftKey, rightKey := fmt.Sprintf("left-%d", s.Characters[0]), fmt.Sprintf("right-%d", s.Characters[1])
	if s.Winner == 1 {
		leftKey = fmt.Sprintf("right-%d", s.Characters[0])
		rightKey = fmt.Sprintf("left-%d", s.Characters[1])
	}
	draw(leftKey, 18, 34, 89, 89, false)
	draw(rightKey, 214, 34, 89, 89, true)
	draw(fmt.Sprintf("flag-%d", s.Flags[0]), 30, 154, 65, 33, false)
	draw(fmt.Sprintf("flag-%d", s.Flags[1]), 226, 154, 65, 33, false)
	labels := [11]string{"JAAN", "SARORKOV", "BULLET", "PHO HUANG", "FRANK", "ONIMALU", "LAN", "KING TAI CHI", "WIDOW", "JOKER", "INDIAN JOE"}
	rect := func(x, y, w, h int) image.Rectangle {
		return image.Rect(g.activeRect.Min.X+x*3, g.activeRect.Min.Y+y*3, g.activeRect.Min.X+(x+w)*3, g.activeRect.Min.Y+(y+h)*3)
	}
	g.resultText(dst, labels[s.Characters[0]], rect(18, 130, 89, 20), 37, false)
	g.resultText(dst, labels[s.Characters[1]], rect(214, 130, 89, 20), 37, false)
	headings := [3][]rune{[]rune("壓倒勝"), []rune("逆轉勝"), []rune("險勝")}
	for i, glyph := range headings[s.Outcome] {
		slot := i
		if len(headings[s.Outcome]) == 2 && i == 1 {
			slot = 2
		}
		g.resultText(dst, string(glyph), rect(128, 15+slot*56, 65, 56), 135, true)
	}
	g.drawContinueHD(dst, s.Continue)
	return true
}
