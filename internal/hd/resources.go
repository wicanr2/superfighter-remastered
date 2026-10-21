package hd

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/png"
	"io"
	"os"
	"path/filepath"
	"strings"
)

// DecodeCPM decodes the evidenced byte-index RLE container, with explicit bounds.
func DecodeCPM(b []byte, maxWidth, maxHeight int) (int, int, []byte, [256][3]uint8, error) {
	var palette [256][3]uint8
	if len(b) < 6 {
		return 0, 0, nil, palette, fmt.Errorf("圖像表頭不足")
	}
	w, h := int(binary.LittleEndian.Uint16(b)), int(binary.LittleEndian.Uint16(b[2:]))
	if w < 1 || h < 1 || w > maxWidth || h > maxHeight || b[4] > 1 {
		return 0, 0, nil, palette, fmt.Errorf("圖像尺寸或格式錯誤")
	}
	at := 5
	if b[4] == 1 {
		if len(b) < 774 {
			return 0, 0, nil, palette, fmt.Errorf("圖像色盤不足")
		}
		for i := range palette {
			for k := 0; k < 3; k++ {
				v := b[5+i*3+k]
				if v > 63 {
					return 0, 0, nil, palette, fmt.Errorf("圖像色盤越界")
				}
				palette[i][k] = v*4 + v/16
			}
		}
		at = 773
	}
	marker := b[at]
	at++
	out := make([]byte, 0, w*h)
	for at < len(b) {
		value, count := b[at], 1
		at++
		if value == marker {
			if at+2 > len(b) {
				return 0, 0, nil, palette, fmt.Errorf("圖像 run 截斷")
			}
			count = int(b[at])
			value = b[at+1]
			at += 2
		}
		if count < 1 || len(out)+count > w*h {
			return 0, 0, nil, palette, fmt.Errorf("圖像 run 越界")
		}
		for i := 0; i < count; i++ {
			out = append(out, value)
		}
	}
	if len(out) != w*h {
		return 0, 0, nil, palette, fmt.Errorf("圖像內容長度錯誤")
	}
	return w, h, out, palette, nil
}

func strictJSON(b []byte, into any) error {
	d := json.NewDecoder(bytes.NewReader(b))
	d.DisallowUnknownFields()
	if e := d.Decode(into); e != nil {
		return e
	}
	if e := d.Decode(&struct{}{}); e != io.EOF {
		return fmt.Errorf("素材清單含額外資料")
	}
	return nil
}

// ReadArt only reads regular files below the supplied art directory.
func ReadArt(root, name, want string, limit int64) ([]byte, error) {
	if name == "" || strings.ContainsAny(name, "\\:") || filepath.IsAbs(name) || filepath.ToSlash(filepath.Clean(name)) != name || name == "." || strings.HasPrefix(name, "../") {
		return nil, fmt.Errorf("HD 路徑錯誤")
	}
	path := root
	for _, part := range strings.Split(name, "/") {
		path = filepath.Join(path, part)
		info, e := os.Lstat(path)
		if e != nil {
			return nil, e
		}
		if info.Mode()&os.ModeSymlink != 0 {
			return nil, fmt.Errorf("HD 不接受符號連結")
		}
	}
	return checkedFile(filepath.Dir(path), filepath.Base(path), want, limit)
}

type ScreenImage struct {
	Key    string `json:"key"`
	File   string `json:"file"`
	SHA256 string `json:"sha256"`
	Width  int    `json:"width"`
	Height int    `json:"height"`
}
type ScreenManifest struct {
	Version int           `json:"version"`
	Kind    string        `json:"kind"`
	Images  []ScreenImage `json:"images"`
}

// LoadScreens validates a complete group before returning any screen artwork.
func LoadScreens(root string) (map[string]image.Image, error) {
	b, e := ReadArt(root, "screens.json", "", 64<<10)
	if e != nil {
		return nil, e
	}
	var m ScreenManifest
	if e = strictJSON(b, &m); e != nil {
		return nil, e
	}
	wanted := map[string]bool{"title-person": true, "title-logo": true, "selection-vs": true, "paper": true}
	for i := 0; i < 11; i++ {
		wanted[fmt.Sprintf("left-%d", i)] = true
		wanted[fmt.Sprintf("right-%d", i)] = true
	}
	for i := 0; i < 7; i++ {
		wanted[fmt.Sprintf("flag-%d", i)] = true
	}
	if m.Version != 1 || m.Kind != "hd-screen-art" || len(m.Images) != len(wanted) {
		return nil, fmt.Errorf("畫面 HD 清單不完整")
	}
	out := map[string]image.Image{}
	pixels := 0
	for _, row := range m.Images {
		if !wanted[row.Key] || out[row.Key] != nil || len(row.SHA256) != 64 || row.Width < 1 || row.Height < 1 || row.Width > 4096 || row.Height > 4096 {
			return nil, fmt.Errorf("畫面 HD 鍵或尺寸錯誤")
		}
		pixels += row.Width * row.Height
		if pixels > 64*1024*1024 {
			return nil, fmt.Errorf("畫面 HD 像素總量過大")
		}
		b, e = ReadArt(root, row.File, row.SHA256, 32<<20)
		if e != nil {
			return nil, e
		}
		cfg, e := png.DecodeConfig(bytes.NewReader(b))
		if e != nil {
			return nil, e
		}
		if cfg.Width != row.Width || cfg.Height != row.Height {
			return nil, fmt.Errorf("畫面 HD 實際尺寸不符")
		}
		im, e := png.Decode(bytes.NewReader(b))
		if e != nil {
			return nil, e
		}
		out[row.Key] = im
	}
	return out, nil
}
