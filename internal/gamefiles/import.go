// Package gamefiles 匯入玩家自己的固定版本資料，不包含原版 bytes。
package gamefiles

import (
	"archive/zip"
	"crypto/sha256"
	_ "embed"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path"
	"path/filepath"
	"strings"

	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

//go:embed source-manifest.json
var sourceManifest []byte

type sourceFile struct {
	Name   string `json:"name"`
	SHA256 string `json:"sha256"`
	Bytes  int    `json:"bytes"`
}

func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

// Import 先驗全部資料，再原子建立新目錄；拒絕覆寫既有遊戲。
func Import(source, destination string) error {
	if _, err := os.Lstat(destination); !os.IsNotExist(err) {
		return fmt.Errorf("目標已存在，請指定新的 -data 目錄：%s", destination)
	}
	var list []sourceFile
	if err := json.Unmarshal(sourceManifest, &list); err != nil {
		return err
	}
	info, err := os.Stat(source)
	if err != nil {
		return err
	}
	var archive *zip.ReadCloser
	entries := map[string]*zip.File{}
	if !info.IsDir() {
		archive, err = zip.OpenReader(source)
		if err != nil {
			return err
		}
		defer archive.Close()
		for _, f := range archive.File {
			name := f.Name
			if name == "" || strings.ContainsAny(name, "\\:") || strings.HasPrefix(name, "/") || path.Clean(name) != strings.TrimSuffix(name, "/") || strings.HasPrefix(name, "../") || name == ".." || f.Mode()&os.ModeSymlink != 0 {
				return fmt.Errorf("ZIP 含不安全路徑")
			}
			if _, ok := entries[name]; ok {
				return fmt.Errorf("ZIP 含重複路徑")
			}
			entries[name] = f
		}
	}
	payload := map[string][]byte{}
	for _, item := range list {
		if filepath.Base(item.Name) != item.Name || item.Bytes < 1 || item.Bytes > 4<<20 {
			return fmt.Errorf("匯入清單錯誤")
		}
		var b []byte
		if archive != nil {
			f := entries[item.Name]
			if f == nil || f.UncompressedSize64 != uint64(item.Bytes) || !f.Mode().IsRegular() {
				return fmt.Errorf("缺少或錯誤的來源：%s", item.Name)
			}
			r, e := f.Open()
			if e != nil {
				return e
			}
			b = make([]byte, item.Bytes)
			_, err = io.ReadFull(r, b)
			r.Close()
		} else {
			file := filepath.Join(source, item.Name)
			var stat os.FileInfo
			stat, err = os.Lstat(file)
			if err == nil && (!stat.Mode().IsRegular() || stat.Size() != int64(item.Bytes)) {
				err = fmt.Errorf("來源型態或大小錯誤")
			}
			if err == nil {
				b, err = os.ReadFile(file)
			}
		}
		if err != nil {
			return fmt.Errorf("%s：%w", item.Name, err)
		}
		if digest(b) != item.SHA256 {
			return fmt.Errorf("原版版本或雜湊不符：%s", item.Name)
		}
		payload[item.Name] = b
	}
	parent := filepath.Dir(destination)
	if err := os.MkdirAll(parent, 0755); err != nil {
		return err
	}
	tmp, err := os.MkdirTemp(parent, ".superfighter-import-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(tmp)
	for name, b := range payload {
		if err := os.WriteFile(filepath.Join(tmp, name), b, 0644); err != nil {
			return err
		}
	}
	return os.Rename(tmp, destination)
}

func EnsureBackground(root, imageFile, output string) error {
	b, err := os.ReadFile(filepath.Join(root, "I2.XGB"))
	if err != nil {
		return err
	}
	if digest(b) != hd.SourceSHA256 {
		return fmt.Errorf("屋頂原版來源不符")
	}
	if _, err := os.Stat(output); err == nil {
		_, err = hd.Load(output)
		return err
	} else if !os.IsNotExist(err) {
		return err
	}
	if len(b) < 774 || binary.LittleEndian.Uint16(b) != 480 || binary.LittleEndian.Uint16(b[2:]) != 204 || b[4] != 1 {
		return fmt.Errorf("屋頂來源格式錯誤")
	}
	pixels := make([]byte, 0, 480*204)
	for pos := 774; pos < len(b); {
		value := b[pos]
		pos++
		count := 1
		if value == b[773] {
			if pos+2 > len(b) {
				return fmt.Errorf("截斷 run")
			}
			count = int(b[pos])
			value = b[pos+1]
			pos += 2
		}
		if count == 0 || len(pixels)+count > 480*204 {
			return fmt.Errorf("屋頂 run 越界")
		}
		for i := 0; i < count; i++ {
			pixels = append(pixels, value)
		}
	}
	if len(pixels) != 480*204 || digest(pixels) != hd.ReferenceSHA256 {
		return fmt.Errorf("屋頂參考不符")
	}
	palette := make([]byte, 128*3)
	for i, v := range b[5 : 5+len(palette)] {
		if v > 63 {
			return fmt.Errorf("屋頂色盤錯誤")
		}
		palette[i] = v<<2 | v>>4
	}
	image, err := os.ReadFile(imageFile)
	if err != nil {
		return err
	}
	if digest(image) != "b43472c099a5b11f9732c19a9bc20078f14a0a1a17e020806b5c4e5dcc06d905" {
		return fmt.Errorf("HD 屋頂圖不符")
	}
	m := hd.Manifest{Version: 1, Kind: "rooftop-background-study", Scene: 4, Source: "I2.XGB", SourceSHA256: hd.SourceSHA256, Width: 480, Height: 204,
		ReferenceFile: "reference.idx", ReferenceSHA256: digest(pixels), PaletteFile: "palette.rgb", PaletteSHA256: digest(palette), ImageFile: "rooftop.png", ImageSHA256: digest(image), ImageWidth: 1923, ImageHeight: 818}
	metadata, err := json.MarshalIndent(m, "", "  ")
	if err != nil {
		return err
	}
	parent := filepath.Dir(output)
	if err := os.MkdirAll(parent, 0755); err != nil {
		return err
	}
	tmp, err := os.MkdirTemp(parent, ".rooftop-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(tmp)
	for name, data := range map[string][]byte{"reference.idx": pixels, "palette.rgb": palette, "rooftop.png": image, "manifest.json": append(metadata, '\n')} {
		if err := os.WriteFile(filepath.Join(tmp, name), data, 0644); err != nil {
			return err
		}
	}
	if _, err := hd.Load(tmp); err != nil {
		return err
	}
	return os.Rename(tmp, output)
}
