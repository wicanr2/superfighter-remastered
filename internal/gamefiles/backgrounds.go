package gamefiles

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

// EnsureBackgroundCollection creates references from the user's originals only.
func EnsureBackgroundCollection(root, artRoot, output string) error {
	if _, err := os.Lstat(output); err == nil {
		_, err = hd.Load(output)
		return err
	} else if !os.IsNotExist(err) {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(output), 0755); err != nil {
		return err
	}
	tmp, err := os.MkdirTemp(filepath.Dir(output), ".backgrounds-")
	if err != nil {
		return err
	}
	defer os.RemoveAll(tmp)
	var names []string
	for _, d := range hd.BackgroundDefinitions() {
		b, err := os.ReadFile(filepath.Join(root, d.Source))
		if err != nil {
			return err
		}
		if digest(b) != d.SourceSHA256 {
			return fmt.Errorf("背景來源不符：%s", d.Source)
		}
		w, h, pixels, palette, err := hd.DecodeCPM(b, 480, 204)
		if err != nil {
			return err
		}
		if w != 480 || h != 204 || digest(pixels) != d.ReferenceSHA256 {
			return fmt.Errorf("背景原色號不符：%s", d.Source)
		}
		colours := make([]byte, 384)
		for i := 0; i < 128; i++ {
			copy(colours[i*3:i*3+3], palette[i][:])
		}
		if digest(colours) != d.PaletteSHA256 {
			return fmt.Errorf("背景原色盤不符：%s", d.Source)
		}
		image, err := hd.ReadArt(artRoot, d.ImageFile, d.ImageSHA256, 32<<20)
		if err != nil {
			return err
		}
		name := fmt.Sprintf("scene-%02d", d.Scene)
		names = append(names, name)
		child := filepath.Join(tmp, name)
		if err := os.Mkdir(child, 0755); err != nil {
			return err
		}
		m := hd.Manifest{Version: 1, Kind: "scene-background", Scene: d.Scene, Source: d.Source, SourceSHA256: d.SourceSHA256, Width: 480, Height: 204, ReferenceFile: "reference.idx", ReferenceSHA256: d.ReferenceSHA256, PaletteFile: "palette.rgb", PaletteSHA256: d.PaletteSHA256, ImageFile: "background.png", ImageSHA256: d.ImageSHA256, ImageWidth: d.ImageWidth, ImageHeight: d.ImageHeight}
		metadata, err := json.MarshalIndent(m, "", "  ")
		if err != nil {
			return err
		}
		for file, data := range map[string][]byte{"reference.idx": pixels, "palette.rgb": colours, "background.png": image, "manifest.json": metadata} {
			if err := os.WriteFile(filepath.Join(child, file), data, 0644); err != nil {
				return err
			}
		}
	}
	if len(names) != 11 {
		return fmt.Errorf("背景來源集合不完整")
	}
	metadata, err := json.Marshal(struct {
		Version     int      `json:"version"`
		Kind        string   `json:"kind"`
		Backgrounds []string `json:"backgrounds"`
	}{2, "background-collection", names})
	if err != nil {
		return err
	}
	if err := os.WriteFile(filepath.Join(tmp, "manifest.json"), metadata, 0644); err != nil {
		return err
	}
	if _, err := hd.Load(tmp); err != nil {
		return err
	}
	return os.Rename(tmp, output)
}
