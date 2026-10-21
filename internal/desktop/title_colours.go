package desktop

import (
	"fmt"
	"image"
	"image/color"
	"math"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

// This maps the evidenced colour cycle onto new painted art. The spatial mask
// is an HD material approximation, not an original-pixel material assertion.
func titleHDPhases(root string, original image.Image) ([8]*ebiten.Image, error) {
	var textures [8]*ebiten.Image
	b, e := hd.ReadArt(root, "TITLE.CPM", "a4790f1da67dbff8eec45c573826b95ee9e9c48ed165f99dfc1cf9176ef03f10", 4<<20)
	if e != nil {
		return textures, e
	}
	_, _, _, base, e := hd.DecodeCPM(b, 320, 200)
	if e != nil {
		return textures, e
	}
	b, e = hd.ReadArt(root, "SFNAME.CPM", "9268d0093b84b67508ea1e2280ec5707c20b6d31a929bfd736b89e132a1842bc", 4<<20)
	if e != nil {
		return textures, e
	}
	w, h, decoded, _, e := hd.DecodeCPM(b, 320, 200)
	if e != nil {
		return textures, e
	}
	if w != 285 || h != 94 {
		return textures, fmt.Errorf("標題字標來源尺寸錯誤")
	}
	if original == nil || original.Bounds().Dx() != 1983 || original.Bounds().Dy() != 793 {
		return textures, fmt.Errorf("HD 字標尺寸錯誤")
	}
	bounds := image.Rectangle{Min: original.Bounds().Max, Max: original.Bounds().Min}
	used := map[byte]bool{}
	for _, v := range decoded[:285*69] {
		if v >= 1 && v <= 15 {
			used[v] = true
		}
	}
	for y := 0; y < 793; y++ {
		for x := 0; x < 1983; x++ {
			_, _, _, a := original.At(x, y).RGBA()
			if a >= 16*257 {
				bounds.Min.X = min(bounds.Min.X, x)
				bounds.Min.Y = min(bounds.Min.Y, y)
				bounds.Max.X = max(bounds.Max.X, x+1)
				bounds.Max.Y = max(bounds.Max.Y, y+1)
			}
		}
	}
	if bounds.Empty() {
		return textures, fmt.Errorf("HD 字標沒有可見圖像")
	}
	material := make([]float32, 1983*793)
	for y := bounds.Min.Y; y < bounds.Max.Y; y++ {
		for x := bounds.Min.X; x < bounds.Max.X; x++ {
			u := (float64(x-bounds.Min.X)+.5)*285/float64(bounds.Dx()) - .5
			v := (float64(y-bounds.Min.Y)+.5)*69/float64(bounds.Dy()) - .5
			left, top := int(math.Floor(u)), int(math.Floor(v))
			fx, fy := u-float64(left), v-float64(top)
			sum := 0.0
			for dy := 0; dy < 2; dy++ {
				for dx := 0; dx < 2; dx++ {
					sx, sy := left+dx, top+dy
					if sx < 0 || sx >= 285 || sy < 0 || sy >= 69 {
						continue
					}
					value := decoded[sy*285+sx]
					if value < 7 || value > 14 {
						continue
					}
					wx, wy := 1-fx, 1-fy
					if dx == 1 {
						wx = fx
					}
					if dy == 1 {
						wy = fy
					}
					sum += wx * wy
				}
			}
			material[y*1983+x] = float32(sum)
		}
	}
	for phase := 0; phase < 8; phase++ {
		target := base
		for i := 0; i < 8; i++ {
			target[7+i] = base[7+(i+phase)%8]
		}
		cache := map[[3]byte][3]byte{}
		out := image.NewNRGBA(original.Bounds())
		for y := 0; y < 793; y++ {
			for x := 0; x < 1983; x++ {
				p := color.NRGBAModel.Convert(original.At(x, y)).(color.NRGBA)
				rgb := [3]byte{p.R, p.G, p.B}
				if p.A != 0 {
					mapped, ok := cache[rgb]
					if !ok {
						var delta [3]float64
						sum := 0.0
						exact := false
						for i := 1; i <= 15; i++ {
							if !used[byte(i)] {
								continue
							}
							distance := 0.0
							for k := 0; k < 3; k++ {
								d := float64(rgb[k]) - float64(base[i][k])
								distance += d * d
							}
							if distance == 0 {
								mapped = target[i]
								exact = true
								break
							}
							weight := 1 / ((distance + 16) * (distance + 16))
							sum += weight
							for k := 0; k < 3; k++ {
								delta[k] += weight * (float64(target[i][k]) - float64(base[i][k]))
							}
						}
						if !exact {
							for k := 0; k < 3; k++ {
								mapped[k] = byte(math.Max(0, math.Min(255, math.Round(float64(rgb[k])+delta[k]/sum))))
							}
						}
						cache[rgb] = mapped
					}
					blend := float64(material[y*1983+x])
					for k := 0; k < 3; k++ {
						mapped[k] = byte(math.Max(0, math.Min(255, math.Round(float64(rgb[k])+(float64(mapped[k])-float64(rgb[k]))*blend))))
					}
					p.R, p.G, p.B = mapped[0], mapped[1], mapped[2]
				}
				out.SetNRGBA(x, y, p)
			}
		}
		texture := ebiten.NewImageFromImageWithOptions(out, &ebiten.NewImageFromImageOptions{Unmanaged: true})
		textures[phase] = texture.SubImage(image.Rect(61, 153, 1952, 621)).(*ebiten.Image)
	}
	return textures, nil
}
