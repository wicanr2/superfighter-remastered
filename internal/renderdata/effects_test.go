package renderdata

import (
	"encoding/json"
	"fmt"
	"image"
	"os"
	"path/filepath"
	"testing"
)

func TestOriginalEffectGeometryAndFrameReplay(t *testing.T) {
	root := os.Getenv("KDZZ_HD_FIXTURES")
	if root == "" {
		t.Skip("local original effect receipts not supplied")
	}
	read := func(path string) []byte {
		t.Helper()
		b, e := os.ReadFile(path)
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	geometry, frames := 0, 0
	for _, name := range []string{"effect-draw-v1", "effect-draw-v2"} {
		dir := filepath.Join(root, name)
		var receipt struct {
			Records []struct {
				Role, Fixture string
				Width, Height int
				DI            int `json:"destination_di"`
				Flags         uint8
				Top           int `json:"top_clip"`
				Left          int `json:"left_clip"`
				Right         int `json:"right_clip"`
			}
			Frames []struct{ Fixture string }
		}
		if e := json.Unmarshal(read(filepath.Join(dir, "receipt.json")), &receipt); e != nil {
			t.Fatal(e)
		}
		for _, d := range receipt.Records {
			if d.Role != "effect" || d.Fixture == "" {
				continue
			}
			raw := read(filepath.Join(dir, d.Fixture+".source.bin"))
			mask := read(filepath.Join(dir, d.Fixture+".mask"))
			s := Sprite{X: d.DI % 320, Y: d.DI / 320, Width: d.Width, Height: d.Height, Flags: d.Flags, TopClip: d.Top, LeftClip: d.Left, RightClip: d.Right}
			origin, clip := s.Placement()
			expected := make([]byte, Pixels)
			for y := 0; y < s.Height; y++ {
				for x := 0; x < s.Width; x++ {
					packed := raw[2+y*((s.Width+1)/2)+x/2]
					v := packed >> 4
					if x%2 == 1 {
						v = packed & 15
					}
					if v == 0 {
						continue
					}
					sx, sy := x, y
					if s.Flags&64 != 0 {
						sx = s.Width - 1 - x
					}
					if s.Flags&128 != 0 {
						sy = s.Height - 1 - y
					}
					point := origin.Add(image.Pt(sx, sy))
					if point.In(clip) {
						expected[point.Y*320+point.X] = 1
					}
				}
			}
			if len(mask) != Pixels {
				t.Fatal("invalid original mask")
			}
			for i, v := range mask {
				if v != expected[i] {
					t.Fatalf("%s %s geometry differs at %d", name, d.Fixture, i)
				}
			}
			geometry++
		}
		for _, f := range receipt.Frames {
			if f.Fixture == "" {
				continue
			}
			var metadata []struct {
				Kind string
				Draw *struct {
					Sources []struct{ Player int }
					Role    string
				}
			}
			if e := json.Unmarshal(read(filepath.Join(dir, f.Fixture+".layers.json")), &metadata); e != nil {
				t.Fatal(e)
			}
			layers := make([]Layer, len(metadata))
			for i, m := range metadata {
				prefix := filepath.Join(dir, fmt.Sprintf("%s.layer-%02d", f.Fixture, i))
				layers[i] = Layer{Background: i == 0, Indices: read(prefix + ".idx"), Coverage: read(prefix + ".mask")}
				if m.Draw != nil {
					layers[i].Sprite = &Sprite{Player: m.Draw.Sources[0].Player, Effect: m.Draw.Role == "effect"}
				}
			}
			pixels := read(filepath.Join(dir, f.Fixture+".idx"))
			if !Match(layers, pixels) {
				t.Fatalf("%s %s full replay rejected", name, f.Fixture)
			}
			for i := range layers {
				if layers[i].Sprite != nil && layers[i].Sprite.Effect {
					original := *layers[i].Sprite
					layers[i].Sprite.Effect = false
					if Match(layers, pixels) {
						t.Fatal("effect incorrectly accepted as a third body")
					}
					*layers[i].Sprite = original
					break
				}
			}
			frames++
		}
	}
	if geometry != 19 || frames != 19 {
		t.Fatalf("original fixtures missing: geometry %d frames %d", geometry, frames)
	}
}
