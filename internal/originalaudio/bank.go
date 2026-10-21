package originalaudio

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

const Rate = 48000

type Clip struct {
	ID            string     `json:"id"`
	Kind          string     `json:"kind"`
	SourceSHA256  string     `json:"source_sha256"`
	File          string     `json:"file"`
	SHA256        string     `json:"sha256"`
	Duration      float64    `json:"duration_seconds"`
	Frames        int64      `json:"frames"`
	DecodedFrames int64      `json:"decoded_frames"`
	Peak          int        `json:"peak"`
	Clipping      float64    `json:"clipping_ratio"`
	Loop          bool       `json:"loop"`
	Commands      [][]string `json:"conversion_commands"`
	Data          []byte     `json:"-"`
}
type Manifest struct {
	Version        int             `json:"version"`
	Kind           string          `json:"kind"`
	SampleRate     int             `json:"sample_rate"`
	Channels       int             `json:"channels"`
	RegistrySHA256 string          `json:"registry_sha256"`
	Clips          []Clip          `json:"clips"`
	Rights         string          `json:"rights"`
	Renderer       json.RawMessage `json:"renderer"`
	Limits         string          `json:"limits"`
}
type Bank struct {
	Clips    map[string]*Clip
	Manifest Manifest
}

// Keep audio/core independent of the visual HD package, including test builds.
func readAudio(root, name, want string, limit int64) ([]byte, error) {
	if name == "" || name == "." || name == ".." || filepath.Base(name) != name || strings.ContainsAny(name, "/\\:") {
		return nil, fmt.Errorf("原音檔名錯誤")
	}
	path := filepath.Join(root, name)
	info, e := os.Lstat(path)
	if e != nil {
		return nil, e
	}
	if !info.Mode().IsRegular() || info.Size() > limit {
		return nil, fmt.Errorf("原音型態或大小錯誤")
	}
	file, e := os.Open(path)
	if e != nil {
		return nil, e
	}
	defer file.Close()
	data, e := io.ReadAll(io.LimitReader(file, limit+1))
	if e != nil {
		return nil, e
	}
	if int64(len(data)) > limit || want != "" && fmt.Sprintf("%x", sha256.Sum256(data)) != want {
		return nil, fmt.Errorf("原音大小或雜湊不符")
	}
	return data, nil
}

// Import only copies a complete validated local audio pack into a new directory.
func Import(source, original, output string) error {
	bank, e := Load(source, original)
	if e != nil {
		return e
	}
	if _, e = os.Lstat(output); e == nil {
		return fmt.Errorf("原音目錄已存在，不覆寫")
	} else if !os.IsNotExist(e) {
		return e
	}
	if e = os.MkdirAll(filepath.Dir(output), 0755); e != nil {
		return e
	}
	tmp, e := os.MkdirTemp(filepath.Dir(output), ".original-audio-")
	if e != nil {
		return e
	}
	defer os.RemoveAll(tmp)
	for _, clip := range bank.Manifest.Clips {
		if e = os.WriteFile(filepath.Join(tmp, clip.File), clip.Data, 0644); e != nil {
			return e
		}
	}
	manifest, e := json.MarshalIndent(bank.Manifest, "", "  ")
	if e != nil {
		return e
	}
	if e = os.WriteFile(filepath.Join(tmp, "manifest.json"), manifest, 0644); e != nil {
		return e
	}
	return os.Rename(tmp, output)
}

func Load(root, original string) (*Bank, error) {
	raw, e := readAudio(root, "manifest.json", "", 1<<20)
	if e != nil {
		return nil, e
	}
	var m Manifest
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if e = decoder.Decode(&m); e != nil {
		return nil, e
	}
	if decoder.Decode(&struct{}{}) != io.EOF {
		return nil, fmt.Errorf("原音清單含額外資料")
	}
	registry := Sources()
	if m.Version != 1 || m.Kind != "original-audio-ogg" || m.SampleRate != Rate || m.Channels != 2 || m.RegistrySHA256 != RegistrySHA256() || len(m.Clips) != len(registry.Clips) {
		return nil, fmt.Errorf("原音版本或來源不符")
	}
	for _, source := range registry.Sources {
		b, e := os.ReadFile(filepath.Join(original, source.File))
		if e != nil {
			return nil, e
		}
		if fmt.Sprintf("%x", sha256.Sum256(b)) != source.SHA256 {
			return nil, fmt.Errorf("原音來源不符：%s", source.File)
		}
	}
	wanted := map[string]SourceClip{}
	for _, row := range registry.Clips {
		wanted[row.ID] = row
	}
	bank := &Bank{Clips: map[string]*Clip{}, Manifest: m}
	seen := map[string]bool{}
	total := 0
	for i := range bank.Manifest.Clips {
		clip := &bank.Manifest.Clips[i]
		source, ok := wanted[clip.ID]
		if !ok || seen[clip.ID] || clip.Kind != source.Kind || clip.SourceSHA256 != source.SHA256 || clip.Loop != (clip.Kind == "music") || clip.Duration <= 0 || clip.Duration > 1800 || clip.Frames < 1 || clip.Frames > Rate*1800 || clip.DecodedFrames < 1 || clip.DecodedFrames > Rate*1800 || clip.Peak <= 16 || clip.Peak > 32768 || clip.Clipping < 0 || clip.Clipping >= .001 || !strings.HasSuffix(clip.File, ".ogg") || len(clip.SHA256) != 64 {
			return nil, fmt.Errorf("原音項目錯誤：%s", clip.ID)
		}
		clip.Data, e = readAudio(root, clip.File, clip.SHA256, 20<<20)
		if e != nil {
			return nil, e
		}
		total += len(clip.Data)
		if total > 160<<20 || len(clip.Data) < 4 || string(clip.Data[:4]) != "OggS" {
			return nil, fmt.Errorf("原音 OGG 或總量錯誤")
		}
		if bank.Clips[clip.SourceSHA256] == nil {
			bank.Clips[clip.SourceSHA256] = clip
		}
		seen[clip.ID] = true
	}
	return bank, nil
}
