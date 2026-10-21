package hd

import (
	_ "embed"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

//go:embed background-sources.json
var backgroundDefinitions []byte

type BackgroundDefinition struct {
	Scene           int    `json:"scene"`
	Source          string `json:"source"`
	SourceSHA256    string `json:"source_sha256"`
	ReferenceSHA256 string `json:"reference_sha256"`
	PaletteSHA256   string `json:"palette_sha256"`
	ImageFile       string `json:"image_file"`
	ImageSHA256     string `json:"image_sha256"`
	ImageWidth      int    `json:"image_width"`
	ImageHeight     int    `json:"image_height"`
}

func BackgroundDefinitions() []BackgroundDefinition {
	var definitions []BackgroundDefinition
	if json.Unmarshal(backgroundDefinitions, &definitions) != nil {
		return nil
	}
	return definitions
}

func backgroundDefinition(scene int) (BackgroundDefinition, bool) {
	for _, d := range BackgroundDefinitions() {
		if d.Scene == scene {
			return d, true
		}
	}
	return BackgroundDefinition{}, false
}

func (a *Assets) ForScene(scene int) *Assets {
	if a == nil {
		return nil
	}
	if a.backgrounds != nil {
		return a.backgrounds[scene]
	}
	if a.Manifest.Scene != scene {
		return nil
	}
	return a
}

func loadBackgroundCollection(dir string, b []byte) (*Assets, error) {
	var m struct {
		Version     int      `json:"version"`
		Kind        string   `json:"kind"`
		Backgrounds []string `json:"backgrounds"`
	}
	if e := strictJSON(b, &m); e != nil {
		return nil, e
	}
	if m.Version != 2 || m.Kind != "background-collection" || len(m.Backgrounds) < 1 || len(m.Backgrounds) > 11 {
		return nil, fmt.Errorf("HD 背景集合格式錯誤")
	}
	a := &Assets{backgrounds: map[int]*Assets{}}
	pixels := 0
	for _, name := range m.Backgrounds {
		if name == "." || name == ".." || name == "" || strings.ContainsAny(name, "/\\:") || filepath.Base(name) != name {
			return nil, fmt.Errorf("HD 背景成員路徑錯誤")
		}
		child := filepath.Join(dir, name)
		info, e := os.Lstat(child)
		if e != nil {
			return nil, e
		}
		if !info.IsDir() || info.Mode()&os.ModeSymlink != 0 {
			return nil, fmt.Errorf("HD 背景成員型態錯誤")
		}
		childBytes, e := ReadArt(child, "manifest.json", "", 16384)
		if e != nil {
			return nil, e
		}
		var shape struct {
			Version int `json:"version"`
		}
		if json.Unmarshal(childBytes, &shape) != nil || shape.Version != 1 {
			return nil, fmt.Errorf("HD 背景集合不可巢狀")
		}
		entry, e := Load(child)
		if e != nil {
			return nil, e
		}
		pixels += entry.Manifest.ImageWidth * entry.Manifest.ImageHeight
		if pixels > 32*1024*1024 {
			return nil, fmt.Errorf("HD 背景集合像素總量過大")
		}
		if a.backgrounds[entry.Manifest.Scene] != nil {
			return nil, fmt.Errorf("HD 背景來源重複")
		}
		a.backgrounds[entry.Manifest.Scene] = entry
	}
	return a, nil
}
