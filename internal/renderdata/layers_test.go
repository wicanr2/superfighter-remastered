package renderdata

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestOriginalLayerReplayAndSpritePlacement(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original fixtures not supplied")
	}
	dir := filepath.Join(root, "sprite-layers-v1")
	var receipt struct {
		Frames []struct{ Fixture string } `json:"layer_frames"`
	}
	read := func(path string) []byte {
		t.Helper()
		b, e := os.ReadFile(path)
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	if e := json.Unmarshal(read(filepath.Join(dir, "receipt.json")), &receipt); e != nil {
		t.Fatal(e)
	}
	sources := map[int][]byte{0: read(filepath.Join(original, "SFMAN01.DAT")), 4: read(filepath.Join(original, "SFMAN05.DAT"))}
	tested, sprites := 0, 0
	for _, frame := range receipt.Frames {
		if frame.Fixture == "" {
			continue
		}
		stem := frame.Fixture
		var meta []struct {
			Kind string
			Draw *struct {
				Player, Character, Slot, X, Y, Width, Height int
				Flags                                        uint8
				Palette                                      uint8
				Top                                          int `json:"top_clip"`
				Left                                         int `json:"left_clip"`
				Right                                        int `json:"right_clip"`
				Offset                                       int `json:"source_file_offset"`
			}
		}
		if e := json.Unmarshal(read(filepath.Join(dir, stem+"-layers.json")), &meta); e != nil {
			t.Fatal(e)
		}
		layers := make([]Layer, len(meta))
		for i, m := range meta {
			name := filepath.Join(dir, stem+"-layer-"+string([]byte{'0', byte('0' + i)}))
			layers[i] = Layer{Indices: read(name + ".idx"), Coverage: read(name + ".mask")}
			if d := m.Draw; d != nil {
				s := Sprite{Player: d.Player, Character: d.Character, Slot: d.Slot, X: d.X, Y: d.Y, Width: d.Width, Height: d.Height, Flags: d.Flags, PaletteBase: d.Palette, TopClip: d.Top, LeftClip: d.Left, RightClip: d.Right}
				layers[i].Sprite = &s
				origin, clip := s.Placement()
				expected := make([]byte, Pixels)
				mask := make([]byte, Pixels)
				source := sources[d.Character]
				stride := (d.Width + 1) / 2
				for y := 0; y < d.Height; y++ {
					for x := 0; x < d.Width; x++ {
						v := source[d.Offset+2+y*stride+x/2]
						if x%2 == 0 {
							v >>= 4
						} else {
							v &= 15
						}
						if v == 0 {
							continue
						}
						px, py := origin.X+x, origin.Y+y
						if s.Flags&64 != 0 {
							px = origin.X + d.Width - 1 - x
						}
						if s.Flags&128 != 0 {
							py = origin.Y + d.Height - 1 - y
						}
						if px >= clip.Min.X && px < clip.Max.X && py >= clip.Min.Y && py < clip.Max.Y {
							n := py*320 + px
							expected[n] = v | d.Palette
							mask[n] = 1
						}
					}
				}
				for n, v := range mask {
					if (v != 0) != (layers[i].Coverage[n] != 0) || v != 0 && expected[n] != layers[i].Indices[n] {
						t.Fatalf("original placement differs: %s layer %d at %d,%d", stem, i, n%320, n/320)
					}
				}
				sprites++
			}
		}
		pixels := read(filepath.Join(dir, stem+".idx"))
		if !Match(layers, pixels) {
			t.Fatal("original frame replay failed", stem)
		}
		layers[0].Coverage[0] = 0
		if Match(layers, pixels) {
			t.Fatal("incomplete base accepted")
		}
		layers[0].Coverage[0] = 1
		pixels[0] ^= 1
		if Match(layers, pixels) {
			t.Fatal("mismatched frame accepted")
		}
		tested++
	}
	if tested != 16 || sprites != 32 {
		t.Fatalf("fixtures=%d sprites=%d", tested, sprites)
	}
}
