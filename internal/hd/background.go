// Package hd 只讀原版完整畫格，先提供規格 006 的背景試作。
package hd

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"image"
	"image/png"
	"os"
	"path/filepath"
)

const ReferenceSHA256 = "eb1207239c06a0e06cd9ecbb697b4cf7e1421c4dd3e6e2a6794774246eafeb15"
const SourceSHA256 = "81e45c775c79f1dc13f587a63d4bbeb854b9cf9ae8198621c03f6a313ee92e16"
const HUDRows = 48

type Manifest struct {
	Version         int      `json:"version"`
	Kind            string   `json:"kind"`
	Scene           int      `json:"scene"`
	Source          string   `json:"source"`
	SourceSHA256    string   `json:"source_sha256"`
	Width           int      `json:"width"`
	Height          int      `json:"height"`
	ReferenceFile   string   `json:"reference_file"`
	ReferenceSHA256 string   `json:"reference_sha256"`
	PaletteFile     string   `json:"palette_file"`
	PaletteSHA256   string   `json:"palette_sha256"`
	ImageFile       string   `json:"image_file"`
	ImageSHA256     string   `json:"image_sha256"`
	ImageWidth      int      `json:"image_width"`
	ImageHeight     int      `json:"image_height"`
	Evidence        []string `json:"evidence"`
}
type Assets struct {
	Manifest  Manifest
	Image     image.Image
	Reference []byte
	Palette   [128][3]uint8
}
type Frame struct {
	Scene, CameraX   int
	BackgroundSHA256 string
	Pixels           []byte
	Palette          [256][3]uint8
}

func Load(dir string) (*Assets, error) {
	b, e := os.ReadFile(filepath.Join(dir, "manifest.json"))
	if e != nil {
		return nil, e
	}
	if len(b) > 16384 {
		return nil, fmt.Errorf("HD 素材清單過大")
	}
	var m Manifest
	decoder := json.NewDecoder(bytes.NewReader(b))
	decoder.DisallowUnknownFields()
	if e = decoder.Decode(&m); e != nil {
		return nil, e
	}
	if m.Version != 1 || m.Kind != "rooftop-background-study" || m.Scene != 4 || m.Source != "I2.XGB" || m.SourceSHA256 != SourceSHA256 || m.Width != 480 || m.Height != 204 || m.ReferenceSHA256 != ReferenceSHA256 {
		return nil, fmt.Errorf("HD 素材版本或來源不符")
	}
	read := func(name, want string, max int) ([]byte, error) {
		if name == "" || name == "." || filepath.IsAbs(name) || filepath.Base(name) != name {
			return nil, fmt.Errorf("素材檔名錯誤")
		}
		f, e := os.Open(filepath.Join(dir, name))
		if e != nil {
			return nil, e
		}
		defer f.Close()
		info, e := f.Stat()
		if e != nil {
			return nil, e
		}
		if !info.Mode().IsRegular() || info.Size() > int64(max) {
			return nil, fmt.Errorf("素材大小或型態錯誤")
		}
		b, e := os.ReadFile(filepath.Join(dir, name))
		if e != nil {
			return nil, e
		}
		if fmt.Sprintf("%x", sha256.Sum256(b)) != want {
			return nil, fmt.Errorf("素材雜湊不符：%s", name)
		}
		return b, nil
	}
	ref, e := read(m.ReferenceFile, m.ReferenceSHA256, 480*204)
	if e != nil {
		return nil, e
	}
	if len(ref) != 480*204 {
		return nil, fmt.Errorf("背景參考尺寸不符")
	}
	pal, e := read(m.PaletteFile, m.PaletteSHA256, 128*3)
	if e != nil {
		return nil, e
	}
	if len(pal) != 128*3 {
		return nil, fmt.Errorf("背景色盤不足")
	}
	data, e := read(m.ImageFile, m.ImageSHA256, 32<<20)
	if e != nil {
		return nil, e
	}
	cfg, e := png.DecodeConfig(bytes.NewReader(data))
	if e != nil {
		return nil, e
	}
	if cfg.Width != m.ImageWidth || cfg.Height != m.ImageHeight || cfg.Width < 960 || cfg.Height < 600 || cfg.Width > 4096 || cfg.Height > 4096 {
		return nil, fmt.Errorf("HD PNG 尺寸錯誤")
	}
	img, e := png.Decode(bytes.NewReader(data))
	if e != nil {
		return nil, e
	}
	a := &Assets{Manifest: m, Image: img, Reference: ref}
	for i := range a.Palette {
		copy(a.Palette[i][:], pal[i*3:i*3+3])
	}
	return a, nil
}

// Foreground 保留原版完整前景。成功才可在其下方畫整張 HD 背景。
// 返回的透明區只來自已驗原始背景，角色姿態不參與猜測或補圖。
func (a *Assets) Foreground(f Frame) ([]byte, bool, string) {
	if len(f.Pixels) != 64000 {
		return nil, false, "等待完整對戰畫面"
	}
	if f.Scene != 4 || f.BackgroundSHA256 != ReferenceSHA256 {
		return nil, false, "此場景保留原貌"
	}
	if f.CameraX < 0 || f.CameraX > 159 {
		return nil, false, "相機來源未對應，保留原貌"
	}
	for i, p := range a.Palette {
		if p != f.Palette[i] {
			return nil, false, "色盤轉場，保留原貌"
		}
	}
	out := make([]byte, 64000*4)
	for y := 0; y < 200; y++ {
		for x := 0; x < 320; x++ {
			i := y*320 + x
			v := f.Pixels[i]
			if y >= HUDRows && v < 128 && v == a.Reference[y*480+x+f.CameraX] {
				continue
			}
			rgb := f.Palette[v]
			copy(out[i*4:i*4+3], rgb[:])
			out[i*4+3] = 255
		}
	}
	return out, true, "HD 背景；人物與介面保留原貌"
}
