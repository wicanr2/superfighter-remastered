package hd

import (
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestDuplicatePaletteNormalSourcesAndRejection(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local duplicate-character originals not supplied")
	}
	a, err := LoadCharacters(filepath.Join(root, "hd-characters-phoenix-effects-v1"), original)
	if err != nil {
		t.Fatal(err)
	}
	readFrame := func(directory, stem string) ([]renderdata.Layer, [256][3]uint8) {
		t.Helper()
		read := func(suffix string) []byte {
			t.Helper()
			b, e := os.ReadFile(filepath.Join(root, directory, stem+suffix))
			if e != nil {
				t.Fatal(e)
			}
			return b
		}
		var f struct {
			Layers []renderdata.Layer `json:"layers"`
		}
		var palette [256][3]uint8
		if e := json.Unmarshal(read(".frame.json"), &f); e != nil {
			t.Fatal(e)
		}
		if e := json.Unmarshal(read(".palette.json"), &palette); e != nil {
			t.Fatal(e)
		}
		for i := range f.Layers {
			f.Layers[i].Indices = read(fmt.Sprintf(".layer-%02d.idx", i))
			f.Layers[i].Coverage = read(fmt.Sprintf(".layer-%02d.mask", i))
		}
		return f.Layers, palette
	}
	known, missing := 0, 0
	for character := 0; character < 11; character++ {
		for _, stem := range []string{"idle", "walk"} {
			t.Run(fmt.Sprintf("%d/%s", character, stem), func(t *testing.T) {
				layers, palette := readFrame(filepath.Join("duplicate-palette-source-v1", fmt.Sprintf("character-%02d", character)), stem)
				complete := true
				for _, l := range layers {
					if s := l.Sprite; s != nil {
						key, _ := characterArtKey(s.Character, s.Slot, 0, s.SourceBank)
						if a.poses[key] == nil {
							complete = false
						}
					}
				}
				selected, why := a.Select(layers, palette)
				if !complete {
					missing++
					if selected != nil {
						t.Fatal("missing Spider pose allowed partial HD")
					}
					return
				}
				if len(selected) != 2 {
					t.Fatal("real duplicate frame rejected", why)
				}
				known++
				n := 0
				for _, l := range layers {
					if s := l.Sprite; s != nil {
						p := selected[n]
						n++
						key, _ := characterArtKey(s.Character, s.Slot, 0, s.SourceBank)
						base := a.poses[key]
						if p.Pose != base.Pose || p.Bounds != base.Bounds {
							t.Fatal("colour transfer changed source or geometry")
						}
						if s.Player == 0 {
							if p != base {
								t.Fatal("first player was recoloured")
							}
							continue
						}
						view, ok := p.Image.(*alternateCharacterImage)
						if !ok || view.Image != base.Image {
							t.Fatal("second player lost immutable source view")
						}
						for y := p.Bounds.Min.Y; y < p.Bounds.Max.Y; y += 13 {
							for x := p.Bounds.Min.X; x < p.Bounds.Max.X; x += 11 {
								_, _, _, before := base.Image.At(x, y).RGBA()
								_, _, _, after := p.Image.At(x, y).RGBA()
								if before != after {
									t.Fatal("alpha changed")
								}
							}
						}
					}
				}
				bad := palette
				bad[225][0] ^= 1
				if selected, _ := a.Select(layers, bad); selected != nil {
					t.Fatal("unknown palette accepted")
				}
				for i, c := range a.alternatePalettes[character] {
					bad[192+i] = c
				}
				if selected, _ := a.Select(layers, bad); selected != nil {
					t.Fatal("first-player alternate accepted")
				}
			})
		}
	}
	if known != 21 || missing != 1 {
		t.Fatal("unexpected registered-source coverage", known, missing)
	}
	layers, palette := readFrame("hd-motion-coverage-v1/character-00", "sample-00")
	if selected, why := a.Select(layers, palette); selected == nil {
		t.Fatal("ordinary different-character baseline rejected", why)
	}
	for i, c := range a.alternatePalettes[4] {
		palette[224+i] = c
	}
	if selected, _ := a.Select(layers, palette); selected != nil {
		t.Fatal("alternate allowed for different characters")
	}
	layers, palette = readFrame("duplicate-palette-source-v1/character-04", "idle")
	without := *a
	without.alternatePalettes = nil
	without.alternatePoses = nil
	if selected, _ := without.Select(layers, palette); selected != nil {
		t.Fatal("missing alternate source allowed HD")
	}
	for i, c := range a.palettes[[2]int{4, 0}] {
		palette[224+i] = c
	}
	if selected, why := without.Select(layers, palette); selected == nil {
		t.Fatal("missing MAN.COL broke original colours", why)
	}
	for key, pose := range a.alternatePoses {
		if pose.Pose.PaletteBank != 0 || key[2] == 1 {
			t.Fatal("effects were recoloured")
		}
	}
	for character := 0; character < 11; character++ {
		base := a.palettes[[2]int{character, 0}]
		alt := a.alternatePalettes[character]
		for _, alpha := range []uint8{1, 127, 128, 254, 255} {
			im := image.NewNRGBA(image.Rect(0, 0, 15, 1))
			for i := 1; i < 16; i++ {
				im.SetNRGBA(i-1, 0, color.NRGBA{R: base[i][0], G: base[i][1], B: base[i][2], A: alpha})
			}
			view := alternateCharacterImage{Image: im, base: base, alternate: alt}
			for i := 1; i < 16; i++ {
				got := color.NRGBAModel.Convert(view.At(i-1, 0)).(color.NRGBA)
				want := color.NRGBA{R: alt[i][0], G: alt[i][1], B: alt[i][2], A: alpha}
				if got != want {
					t.Fatal("source palette anchor or alpha differs", character, i, got, want)
				}
			}
		}
	}
	badRoot := t.TempDir()
	if e := os.WriteFile(filepath.Join(badRoot, "MAN.COL"), []byte("wrong source"), 0644); e != nil {
		t.Fatal(e)
	}
	if e := (&Characters{}).loadAlternatePalettes(badRoot); e == nil {
		t.Fatal("bad MAN.COL accepted")
	}
	if e := (&Characters{}).loadAlternatePalettes(t.TempDir()); e != nil {
		t.Fatal("missing optional legacy palette rejected", e)
	}
}
