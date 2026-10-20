// Disposable colour-transfer rendering study; does not modify art or production rendering.
package main

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"math"
	"os"
	"path/filepath"
	"strconv"
	"strings"

	"github.com/wicanr2/superfighter-remastered/internal/hd"
	xdraw "golang.org/x/image/draw"
	"golang.org/x/image/font"
	"golang.org/x/image/font/basicfont"
	"golang.org/x/image/math/fixed"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func sha(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

type transfer struct {
	image.Image
	base, alt [16][3]uint8
	active    map[int]bool
}

func (v transfer) At(x, y int) color.Color {
	p := color.NRGBAModel.Convert(v.Image.At(x, y)).(color.NRGBA)
	if p.A == 0 {
		return p
	}
	rgb := [3]uint8{p.R, p.G, p.B}
	var delta [3]float64
	sum := 0.0
	for i := 1; i < 16; i++ {
		if v.active != nil && !v.active[i] {
			continue
		}
		d := 0.0
		for k := 0; k < 3; k++ {
			q := float64(rgb[k]) - float64(v.base[i][k])
			d += q * q
		}
		if d == 0 {
			return color.NRGBA{v.alt[i][0], v.alt[i][1], v.alt[i][2], p.A}
		}
		weight := 1 / math.Pow(d+16, 2)
		sum += weight
		for k := 0; k < 3; k++ {
			delta[k] += weight * (float64(v.alt[i][k]) - float64(v.base[i][k]))
		}
	}
	out := [3]uint8{}
	for k := 0; k < 3; k++ {
		out[k] = uint8(math.Max(0, math.Min(255, math.Round(float64(rgb[k])+delta[k]/sum))))
	}
	return color.NRGBA{out[0], out[1], out[2], p.A}
}
func main() {
	out := flag.String("out", "", "new output directory")
	requested := flag.String("characters", "0,4", "comma-separated source characters")
	secondary := flag.Bool("secondary-main", false, "prototype primary-to-secondary DAT palettes; character:slot entries")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	bytes, e := os.ReadFile("/project/assets/hd/characters/manifest.json")
	must(e)
	var manifest hd.CharacterManifest
	must(json.Unmarshal(bytes, &manifest))
	col, e := os.ReadFile("/orig/MAN.COL")
	must(e)
	if sha(col) != "7153214bf444684179b5296ad1c4dfc874385cbf6e2d5e0c215c13e711749ce5" {
		panic("source mismatch")
	}
	parts := strings.Split(*requested, ",")
	cellWidth, cellHeight := 300, 340
	if *secondary {
		cellWidth, cellHeight = 500, 400
	}
	canvas := image.NewRGBA(image.Rect(0, 0, cellWidth*4, len(parts)*cellHeight))
	draw.Draw(canvas, canvas.Bounds(), image.NewUniform(color.RGBA{24, 29, 39, 255}), image.Point{}, draw.Src)
	label := func(x, y int, s string) {
		d := font.Drawer{Dst: canvas, Src: image.White, Face: basicfont.Face7x13, Dot: fixed.P(x, y)}
		d.DrawString(s)
	}
	var records []map[string]any
	for row, text := range parts {
		pair := strings.Split(text, ":")
		character, e := strconv.Atoi(pair[0])
		must(e)
		if character < 0 || character > 10 {
			panic("invalid character")
		}
		slot := -1
		if len(pair) == 2 {
			slot, e = strconv.Atoi(pair[1])
			must(e)
		} else {
			frameBytes, e := os.ReadFile(fmt.Sprintf("/project/workplace/duplicate-palette-source-v1/character-%02d/idle.frame.json", character))
			must(e)
			var frame struct {
				Layers []struct{ Sprite *struct{ Player, Slot int } }
			}
			must(json.Unmarshal(frameBytes, &frame))
			for _, l := range frame.Layers {
				if l.Sprite != nil && l.Sprite.Player == 0 {
					slot = l.Sprite.Slot
				}
			}
		}
		if slot < 0 || slot >= 72 {
			panic("normal idle source missing")
		}
		var pose *hd.CharacterPose
		for i := range manifest.Poses {
			p := &manifest.Poses[i]
			if p.Character == character && p.Slot == slot && p.PaletteBank == 0 && p.SourceBank == "" {
				pose = p
				break
			}
		}
		if pose == nil {
			panic("normal pose missing")
		}
		data, e := os.ReadFile(fmt.Sprintf("/orig/SFMAN%02d.DAT", character+1))
		must(e)
		seg, off := binary.LittleEndian.Uint16(data[0xb28+slot*4:]), binary.LittleEndian.Uint16(data[0xb2a+slot*4:])
		at := 0xc48 + int(seg)*16 + int(off)
		width, height := int(data[at]), int(data[at+1])
		stride := (width + 1) / 2
		if sha(data[at:at+2+stride*height]) != pose.SourceSHA256 {
			panic("source pose mismatch")
		}
		var base, alt [16][3]uint8
		var active map[int]bool
		if *secondary {
			active = map[int]bool{}
			for y := 0; y < height; y++ {
				for x := 0; x < width; x++ {
					v := data[at+2+y*stride+x/2]
					if x%2 == 0 {
						v >>= 4
					} else {
						v &= 15
					}
					if v != 0 {
						active[int(v)] = true
					}
				}
			}
		}
		for i := 0; i < 16; i++ {
			for k := 0; k < 3; k++ {
				v := data[0xac8+i*3+k]
				base[i][k] = v<<2 | v>>4
				v = col[character*48+i*3+k]
				if *secondary {
					v = data[0xaf8+i*3+k]
				}
				alt[i][k] = v<<2 | v>>4
			}
		}
		path := filepath.Join("/project/assets/hd/characters", pose.Atlas)
		raw, e := os.ReadFile(path)
		must(e)
		found := false
		for _, atlas := range manifest.Atlases {
			if atlas.File == pose.Atlas {
				found = sha(raw) == atlas.SHA256
			}
		}
		if !found {
			panic("art mismatch")
		}
		f, e := os.Open(path)
		must(e)
		art, e := png.Decode(f)
		must(e)
		must(f.Close())
		rect := image.Rect(pose.Rect[0], pose.Rect[1], pose.Rect[2], pose.Rect[3])
		if !rect.In(art.Bounds()) {
			panic("art rect mismatch")
		}
		indexed := func(pal [16][3]uint8) *image.NRGBA {
			im := image.NewNRGBA(image.Rect(0, 0, width, height))
			for y := 0; y < height; y++ {
				for x := 0; x < width; x++ {
					b := data[at+2+y*stride+x/2]
					v := b & 15
					if x%2 == 0 {
						v = b >> 4
					}
					if v != 0 {
						im.SetNRGBA(x, y, color.NRGBA{pal[v][0], pal[v][1], pal[v][2], 255})
					}
				}
			}
			return im
		}
		for column, entry := range []struct {
			name   string
			im     image.Image
			bounds image.Rectangle
			pixel  bool
		}{
			{"original base", indexed(base), image.Rect(0, 0, width, height), true},
			{"HD base", art, rect, false},
			{"original alternate", indexed(alt), image.Rect(0, 0, width, height), true},
			{"HD RGB residual study", transfer{art, base, alt, active}, rect, false},
		} {
			label(column*cellWidth+12, row*cellHeight+20, fmt.Sprintf("C%d source %d %s", character, slot, entry.name))
			dh := 270
			if *secondary {
				dh = min(320, (cellWidth-40)*height/width)
			}
			dw := dh * width / height
			destination := image.Rect(column*cellWidth+(cellWidth-dw)/2, row*cellHeight+45, column*cellWidth+(cellWidth+dw)/2, row*cellHeight+45+dh)
			if entry.pixel {
				xdraw.NearestNeighbor.Scale(canvas, destination, entry.im, entry.bounds, draw.Over, nil)
			} else {
				xdraw.CatmullRom.Scale(canvas, destination, entry.im, entry.bounds, draw.Over, nil)
			}
		}
		records = append(records, map[string]any{"character": character, "pose": pose, "source_DAT_sha256": sha(data), "art_sha256": sha(raw), "active_source_indices": active})
	}
	f, e := os.Create(filepath.Join(*out, "comparison.png"))
	must(e)
	must(png.Encode(f, canvas))
	must(f.Close())
	script, e := os.ReadFile("/project/tools/duplicate_palette_preview.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "duplicate_palette_preview.go"), script, 0644))
	report := map[string]any{"kind": "disposable RGB-residual HD palette study, not production or original-pixel parity", "secondary_main": *secondary, "manifest_sha256": sha(bytes), "source_MAN_COL_sha256": sha(col), "script_sha256": sha(script), "records": records, "method": "per-pixel unpremultiplied RGB, indices1..15, inverse squared RGB-distance weights with +16 regularization, palette delta residual; exact palette anchors and alpha retained", "limits": "visual prototype only; nearest-colour material inference may affect skin or lighting and needs review"}
	b, e := json.MarshalIndent(report, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "receipt.json"), append(b, '\n'), 0644))
	fmt.Println("rendered disposable palette study", *out)
}
