package desktop

import (
	"image"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func (g *Game) drawBackground(dst *ebiten.Image, frame gamecore.Presentation) {
	if g.hdTexture == nil {
		g.hdTexture = ebiten.NewImageFromImage(g.hdAssets.Image)
	}
	op := &ebiten.DrawImageOptions{}
	op.Filter = ebiten.FilterLinear
	sx, sy := float64(screenRect.Dx())/320, float64(screenRect.Dy())/200
	op.GeoM.Scale(sx*480/float64(g.hdTexture.Bounds().Dx()), sy*204/float64(g.hdTexture.Bounds().Dy()))
	op.GeoM.Translate(float64(screenRect.Min.X)-float64(frame.CameraX)*sx, float64(screenRect.Min.Y))
	dst.SubImage(screenRect).(*ebiten.Image).DrawImage(g.hdTexture, op)
}

func (g *Game) drawCharacterFrame(dst *ebiten.Image, frame gamecore.Presentation) (bool, string) {
	if g.hdCharacters == nil {
		return false, "角色 HD 素材未載入，保留原貌"
	}
	if !frame.LayersComplete || len(frame.Layers) < 6 || !frame.Layers[0].Background {
		return false, "等待完整角色畫面"
	}
	selected, reason := g.hdCharacters.Select(frame.Layers, frame.Palette)
	if selected == nil {
		return false, reason
	}
	_, ok, why := g.hdAssets.Foreground(hd.Frame{Scene: frame.Scene, CameraX: frame.CameraX, BackgroundSHA256: frame.BackgroundSHA256, Pixels: frame.Layers[0].Indices, Palette: frame.Palette})
	if !ok {
		return false, why
	}
	for i, v := range frame.Layers[0].Indices {
		if v != g.hdAssets.Reference[i/320*480+i%320+frame.CameraX] {
			return false, "背景圖層來源未對應，保留原貌"
		}
	}
	// 全部驗完才開始畫，不能留下半套角色或背景。
	g.drawBackground(dst, frame)
	for len(g.layerTextures) < len(frame.Layers) {
		g.layerTextures = append(g.layerTextures, ebiten.NewImage(320, 200))
		g.layerRGBA = append(g.layerRGBA, make([]byte, renderdata.Pixels*4))
	}
	if g.actorTextures == nil {
		g.actorTextures = map[*hd.PoseArt]*ebiten.Image{}
	}
	sx, sy := float64(screenRect.Dx())/320, float64(screenRect.Dy())/200
	actor := 0
	for n, layer := range frame.Layers {
		if n == 0 {
			continue
		}
		if s := layer.Sprite; s != nil {
			art := selected[actor]
			actor++
			texture := g.actorTextures[art]
			if texture == nil {
				fragment := image.NewRGBA(image.Rect(0, 0, art.Bounds.Dx(), art.Bounds.Dy()))
				for y := 0; y < fragment.Bounds().Dy(); y++ {
					for x := 0; x < fragment.Bounds().Dx(); x++ {
						fragment.Set(x, y, art.Image.At(art.Bounds.Min.X+x, art.Bounds.Min.Y+y))
					}
				}
				texture = ebiten.NewImageFromImage(fragment)
				g.actorTextures[art] = texture
			}
			origin, clip := s.Placement()
			if clip.Empty() {
				continue
			}
			physical := image.Rect(screenRect.Min.X+int(float64(clip.Min.X)*sx), screenRect.Min.Y+int(float64(clip.Min.Y)*sy), screenRect.Min.X+int(float64(clip.Max.X)*sx), screenRect.Min.Y+int(float64(clip.Max.Y)*sy)).Intersect(screenRect)
			op := &ebiten.DrawImageOptions{}
			op.Filter = ebiten.FilterLinear
			op.GeoM.Scale(float64(s.Width)*sx/float64(texture.Bounds().Dx()), float64(s.Height)*sy/float64(texture.Bounds().Dy()))
			if s.Flags&64 != 0 {
				op.GeoM.Scale(-1, 1)
				op.GeoM.Translate(float64(s.Width)*sx, 0)
			}
			if s.Flags&128 != 0 {
				op.GeoM.Scale(1, -1)
				op.GeoM.Translate(0, float64(s.Height)*sy)
			}
			op.GeoM.Translate(float64(screenRect.Min.X)+float64(origin.X)*sx, float64(screenRect.Min.Y)+float64(origin.Y)*sy)
			if !physical.Empty() {
				dst.SubImage(physical).(*ebiten.Image).DrawImage(texture, op)
			}
			continue
		}
		rgba := g.layerRGBA[n]
		clear(rgba)
		for i, v := range layer.Indices {
			if layer.Coverage[i] != 0 {
				c := frame.Palette[v]
				copy(rgba[i*4:i*4+3], c[:])
				rgba[i*4+3] = 255
			}
		}
		g.layerTextures[n].WritePixels(rgba)
		op := &ebiten.DrawImageOptions{}
		op.GeoM.Scale(sx, sy)
		op.GeoM.Translate(float64(screenRect.Min.X), float64(screenRect.Min.Y))
		dst.SubImage(screenRect).(*ebiten.Image).DrawImage(g.layerTextures[n], op)
	}
	return true, reason
}
