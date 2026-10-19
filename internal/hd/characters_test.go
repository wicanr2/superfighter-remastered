package hd

import (
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestCharacterPackSourceSelectionAndAtomicRejection(t *testing.T) {
	pack, original, fixtures := os.Getenv("KDZZ_HD_CHARACTERS"), os.Getenv("KDZZ_ORIGINAL_ROOT"), os.Getenv("KDZZ_HD_FIXTURES")
	if pack == "" || original == "" || fixtures == "" {
		t.Skip("local derivative art and original data not supplied")
	}
	a, e := LoadCharacters(pack, original)
	if e != nil {
		t.Fatal(e)
	}
	var layers []struct {
		Kind string
		Draw *struct {
			Player, Character, Slot, X, Y, Width, Height int
			Flags, Palette                               uint8
			Top                                          int `json:"top_clip"`
			Left                                         int `json:"left_clip"`
			Right                                        int `json:"right_clip"`
			Offset                                       int `json:"source_file_offset"`
		}
	}
	read := func(path string) []byte {
		t.Helper()
		b, e := os.ReadFile(path)
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	root := filepath.Join(fixtures, "sprite-layers-v1")
	if e = json.Unmarshal(read(filepath.Join(root, "frame-0000-layers.json")), &layers); e != nil {
		t.Fatal(e)
	}
	var palette [256][3]uint8
	if e = json.Unmarshal(read(filepath.Join(root, "frame-0000-palette.json")), &palette); e != nil {
		t.Fatal(e)
	}
	frame := make([]renderdata.Layer, len(layers))
	for i, layer := range layers {
		if d := layer.Draw; d != nil {
			data := read(filepath.Join(original, fmt.Sprintf("SFMAN%02d.DAT", d.Character+1)))
			end := d.Offset + 2 + (d.Width+1)/2*d.Height
			frame[i].Sprite = &renderdata.Sprite{Player: d.Player, Character: d.Character, Slot: d.Slot, X: d.X, Y: d.Y, Width: d.Width, Height: d.Height, Flags: d.Flags, PaletteBase: d.Palette, TopClip: d.Top, LeftClip: d.Left, RightClip: d.Right, SourceSHA256: fmt.Sprintf("%x", sha256.Sum256(data[d.Offset:end]))}
		}
	}
	frame[0].Background = true
	frame = append(frame[:1], append([]renderdata.Layer{{}}, frame[1:]...)...)
	selected, reason := a.Select(frame, palette)
	if len(selected) != 2 {
		t.Fatal(reason)
	}
	var body int
	for i, l := range frame {
		if l.Sprite != nil {
			body = i
			break
		}
	}
	for _, change := range []func(*renderdata.Sprite){func(s *renderdata.Sprite) { s.Slot = 56 }, func(s *renderdata.Sprite) { s.SourceSHA256 = "wrong" }, func(s *renderdata.Sprite) { s.Flags = 192 }, func(s *renderdata.Sprite) { s.TopClip = 1 }, func(s *renderdata.Sprite) { s.PaletteBase ^= 16 }} {
		copyFrame := append([]renderdata.Layer(nil), frame...)
		s := *frame[body].Sprite
		change(&s)
		copyFrame[body].Sprite = &s
		if selected, _ := a.Select(copyFrame, palette); selected != nil {
			t.Fatal("unsupported sprite produced partial characters")
		}
	}
	badPalette := palette
	badPalette[192][0] ^= 1
	if selected, _ := a.Select(frame, badPalette); selected != nil {
		t.Fatal("changed palette accepted")
	}
	bad := t.TempDir()
	items, e := os.ReadDir(pack)
	if e != nil {
		t.Fatal(e)
	}
	for _, item := range items {
		b := read(filepath.Join(pack, item.Name()))
		if e = os.WriteFile(filepath.Join(bad, item.Name()), b, 0600); e != nil {
			t.Fatal(e)
		}
	}
	manifestBytes := read(filepath.Join(bad, "manifest.json"))
	var manifest CharacterManifest
	if e = json.Unmarshal(manifestBytes, &manifest); e != nil {
		t.Fatal(e)
	}
	manifest.Poses = append(manifest.Poses, manifest.Poses[0])
	encoded, e := json.Marshal(manifest)
	if e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(filepath.Join(bad, "manifest.json"), encoded, 0600); e != nil {
		t.Fatal(e)
	}
	if got, e := LoadCharacters(bad, original); got != nil || e == nil {
		t.Fatal("duplicate source key accepted")
	}
	if e = os.WriteFile(filepath.Join(bad, "manifest.json"), manifestBytes, 0600); e != nil {
		t.Fatal(e)
	}
	imagePath := filepath.Join(bad, manifest.Atlases[0].File)
	data := read(imagePath)
	before := append([]byte(nil), data...)
	data[20] ^= 1
	if e = os.WriteFile(imagePath, data, 0600); e != nil {
		t.Fatal(e)
	}
	if got, e := LoadCharacters(bad, original); got != nil || e == nil {
		t.Fatal("damaged atlas accepted")
	}
	if !bytes.Equal(read(filepath.Join(pack, manifest.Atlases[0].File)), before) {
		t.Fatal("original art pack mutated")
	}
}
