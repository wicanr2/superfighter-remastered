package hd

import (
	"bytes"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

// spriteGeometryMatches 以受驗原檔的像素驗證新幾何，不以旗標猜測可見內容。
// 原始覆蓋也必須一致，包含與背景同色的實際寫入。
func spriteGeometryMatches(s *renderdata.Sprite, source []byte, layer renderdata.Layer) bool {
	if s == nil || s.Width < 1 || s.Width > 255 || s.Height < 1 || s.Height > 255 ||
		s.TopClip < 0 || s.TopClip > s.Height || s.LeftClip < 0 || s.LeftClip > s.Width ||
		s.RightClip < 0 || s.RightClip > s.Width || len(layer.Indices) != renderdata.Pixels || len(layer.Coverage) != renderdata.Pixels {
		return false
	}
	stride := (s.Width + 1) / 2
	if len(source) != 2+stride*s.Height || int(source[0]) != s.Width || int(source[1]) != s.Height ||
		(s.LeftClip+1)/2+(s.RightClip+1)/2 > stride {
		return false
	}
	origin, clip := s.Placement()
	var expected, coverage [renderdata.Pixels]byte
	if !clip.Empty() {
		for y := 0; y < s.Height; y++ {
			for x := 0; x < s.Width; x++ {
				value := source[2+y*stride+x/2]
				if x%2 == 0 {
					value >>= 4
				} else {
					value &= 15
				}
				if value == 0 {
					continue
				}
				px, py := origin.X+x, origin.Y+y
				if s.Flags&64 != 0 {
					px = origin.X + s.Width - 1 - x
				}
				if s.Flags&128 != 0 {
					py = origin.Y + s.Height - 1 - y
				}
				if px >= clip.Min.X && px < clip.Max.X && py >= clip.Min.Y && py < clip.Max.Y {
					at := py*320 + px
					expected[at], coverage[at] = value|s.PaletteBase, 1
				}
			}
		}
	}
	if !bytes.Equal(coverage[:], layer.Coverage) {
		return false
	}
	for i, covered := range coverage {
		if covered != 0 && expected[i] != layer.Indices[i] {
			return false
		}
	}
	return true
}
