package hd

import (
	"fmt"
	"image"
	"image/color"
	"math"
	"os"
)

const alternatePaletteSHA256 = "7153214bf444684179b5296ad1c4dfc874385cbf6e2d5e0c215c13e711749ce5"

func (a *Characters) loadAlternatePalettes(root string) error {
	data, err := checkedFile(root, "MAN.COL", alternatePaletteSHA256, 768)
	if os.IsNotExist(err) {
		return nil // 舊的最小素材／來源根仍可使用原色，替代色保持回退。
	}
	if err != nil {
		return err
	}
	if len(data) != 768 {
		return fmt.Errorf("替代色盤長度不符")
	}
	for _, v := range data {
		if v > 63 {
			return fmt.Errorf("替代色盤分量不符")
		}
	}
	a.alternatePalettes = map[int][16][3]uint8{}
	a.alternatePoses = map[[3]int]*PoseArt{}
	for character := 0; character < 11; character++ {
		if _, known := a.palettes[[2]int{character, 0}]; !known {
			continue
		}
		var palette [16][3]uint8
		for i := range palette {
			for k := range palette[i] {
				v := data[character*48+i*3+k]
				palette[i][k] = v<<2 | v>>4
			}
		}
		a.alternatePalettes[character] = palette
	}
	return nil
}

func (a *Characters) addAlternatePose(key [3]int, original *PoseArt) {
	palette, known := a.alternatePalettes[original.Pose.Character]
	if !known || original.Pose.PaletteBank != 0 {
		return
	}
	a.alternatePoses[key] = &PoseArt{
		Pose: original.Pose, Bounds: original.Bounds, packed: original.packed,
		Image: &alternateCharacterImage{
			Image: original.Image,
			base:  a.palettes[[2]int{original.Pose.Character, 0}], alternate: palette,
		},
	}
}

func matchesCharacterPalette(actual [256][3]uint8, base uint8, expected [16][3]uint8) bool {
	if int(base)+len(expected) > len(actual) {
		return false
	}
	for i, c := range expected {
		if actual[int(base)+i] != c {
			return false
		}
	}
	return true
}

// alternateCharacterImage 是載入時建立的不可變視圖，原 PNG／alpha 不變。
// RGB 色差轉移是 HD 呈現近似；原版色盤身分則由固定來源及 Select 完整核對。
type alternateCharacterImage struct {
	image.Image
	base, alternate [16][3]uint8
	active uint16 // 0 保留 041 全色盤；其他值只使用該來源已用色號。
}

func (v *alternateCharacterImage) ColorModel() color.Model { return color.NRGBAModel }

func (v *alternateCharacterImage) At(x, y int) color.Color {
	p := color.NRGBAModel.Convert(v.Image.At(x, y)).(color.NRGBA)
	if p.A == 0 || v.base == v.alternate {
		return p
	}
	rgb := [3]uint8{p.R, p.G, p.B}
	var delta [3]float64
	sum := 0.0
	for i := 1; i < len(v.base); i++ {
		if v.active != 0 && v.active&(1<<i) == 0 {
			continue
		}
		distance := 0.0
		for k := range rgb {
			d := float64(rgb[k]) - float64(v.base[i][k])
			distance += d * d
		}
		if distance == 0 {
			return color.NRGBA{R: v.alternate[i][0], G: v.alternate[i][1], B: v.alternate[i][2], A: p.A}
		}
		regularized := distance + 16
		weight := 1 / (regularized * regularized)
		sum += weight
		for k := range rgb {
			delta[k] += weight * (float64(v.alternate[i][k]) - float64(v.base[i][k]))
		}
	}
	var output [3]uint8
	for k := range rgb {
		output[k] = uint8(math.Max(0, math.Min(255, math.Round(float64(rgb[k])+delta[k]/sum))))
	}
	return color.NRGBA{R: output[0], G: output[1], B: output[2], A: p.A}
}
