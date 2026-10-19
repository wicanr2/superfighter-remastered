// Disposable HD character composition study over original read-only draw layers.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"image"
	"image/draw"
	"image/png"
	"os"
	"path/filepath"

	"github.com/wicanr2/superfighter-remastered/internal/hd"
	xdraw "golang.org/x/image/draw"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func readJSON(path string, value any) {
	b, e := os.ReadFile(path)
	must(e)
	must(json.Unmarshal(b, value))
}
func readPNG(path string) image.Image {
	f, e := os.Open(path)
	must(e)
	defer f.Close()
	img, e := png.Decode(f)
	must(e)
	return img
}
func savePNG(path string, img image.Image) {
	f, e := os.Create(path)
	must(e)
	must(png.Encode(f, img))
	must(f.Close())
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

type Pose struct {
	Player, Character, Slot, X, Y, Width, Height int
	Flags                                        uint8
	TopClip                                      int `json:"top_clip"`
	LeftClip                                     int `json:"left_clip"`
	RightClip                                    int `json:"right_clip"`
}
type Layer struct {
	Kind string
	Draw *Pose
}
type Art struct {
	Image  image.Image
	Bounds image.Rectangle
}

func paintLayer(target *image.RGBA, pixels, mask []byte, palette [256][3]uint8) {
	img := image.NewRGBA(image.Rect(0, 0, 320, 200))
	for i, v := range pixels {
		if mask == nil || mask[i] != 0 {
			c := palette[v]
			copy(img.Pix[i*4:i*4+3], c[:])
			img.Pix[i*4+3] = 255
		}
	}
	xdraw.NearestNeighbor.Scale(target, target.Bounds(), img, img.Bounds(), draw.Over, nil)
}

func paintActor(target *image.RGBA, pose *Pose, art Art) map[string]any {
	w, h := pose.Width, pose.Height
	img := image.NewRGBA(image.Rect(0, 0, w*3, h*3))
	xdraw.CatmullRom.Scale(img, img.Bounds(), art.Image, art.Bounds, draw.Src, nil)
	flipped := image.NewRGBA(img.Bounds())
	flipX, flipY := pose.Flags&64 != 0, pose.Flags&128 != 0
	for y := 0; y < h*3; y++ {
		for x := 0; x < w*3; x++ {
			sx, sy := x, y
			if flipX {
				sx = w*3 - 1 - x
			}
			if flipY {
				sy = h*3 - 1 - y
			}
			flipped.SetRGBA(x, y, img.RGBAAt(sx, sy))
		}
	}
	leftPairs, rightPairs := (pose.LeftClip+1)/2, (pose.RightClip+1)/2
	pairs := (w+1)/2 - leftPairs - rightPairs
	rows := h - pose.TopClip
	x, y := max(pose.X, 0), max(pose.Y, 0)
	left, top := x-leftPairs*2, y-pose.TopClip
	clip := image.Rect(x, y, x+pairs*2, y+rows)
	if flipX {
		origin := x + w - pose.LeftClip - pose.RightClip
		left = origin + rightPairs*2 + 1 - w
		clip.Min.X = origin - pairs*2 + 1
		clip.Max.X = origin + 1
	}
	if flipY {
		top = y + rows + 1 - h
		clip.Min.Y = y + 1
		clip.Max.Y = y + rows + 1
	}
	clip = image.Rect(clip.Min.X*3, clip.Min.Y*3, clip.Max.X*3, clip.Max.Y*3).Intersect(target.Bounds())
	if !clip.Empty() {
		sub := target.SubImage(clip).(draw.Image)
		bounds := image.Rect(left*3, top*3, (left+w)*3, (top+h)*3)
		draw.Draw(sub, bounds, flipped, image.Point{}, draw.Over)
	}
	return map[string]any{"player": pose.Player, "character": pose.Character, "slot": pose.Slot, "source_size": []int{w, h}, "paint_bbox": []int{art.Bounds.Min.X, art.Bounds.Min.Y, art.Bounds.Max.X, art.Bounds.Max.Y}, "logical_top_left": []int{left, top}, "flags": pose.Flags, "clip": clip}
}

func main() {
	out := flag.String("out", "", "new output directory")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(*out, 0755))
	assets, e := hd.Load("/project/workplace/hd-rooftop-study")
	must(e)
	var reference struct {
		Records []struct {
			Character string
			Batch     int
			Cells     []struct{ Ordinal, Slot int }
		}
	}
	artByPose := map[[2]int]Art{}
	var artManifest struct {
		Records []struct {
			Character, File, Reference string
			Batch                      int
		}
	}
	readJSON("/project/workplace/hd-sprite-art-v1/manifest.json", &artManifest)
	for _, artRecord := range artManifest.Records {
		readJSON(filepath.Join("/project", filepath.Dir(artRecord.Reference), "manifest.json"), &reference)
		for _, record := range reference.Records {
			if record.Character != artRecord.Character || record.Batch != artRecord.Batch {
				continue
			}
			char := 0
			if record.Character == "frank" {
				char = 4
			}
			atlas := readPNG("/project/workplace/hd-sprite-art-v1/" + artRecord.File)
			if atlas.Bounds().Dx()%4 != 0 || atlas.Bounds().Dy()%3 != 0 {
				panic("atlas does not have integer equal cells")
			}
			cw, ch := atlas.Bounds().Dx()/4, atlas.Bounds().Dy()/3
			for _, cell := range record.Cells {
				box := image.Rect(cell.Ordinal%4*cw, cell.Ordinal/4*ch, (cell.Ordinal%4+1)*cw, (cell.Ordinal/4+1)*ch)
				bounds := image.Rectangle{Min: box.Max, Max: box.Min}
				found := false
				for y := box.Min.Y; y < box.Max.Y; y++ {
					for x := box.Min.X; x < box.Max.X; x++ {
						_, _, _, a := atlas.At(x, y).RGBA()
						if a >= 16*257 {
							found = true
							bounds.Min.X = min(bounds.Min.X, x)
							bounds.Min.Y = min(bounds.Min.Y, y)
							bounds.Max.X = max(bounds.Max.X, x+1)
							bounds.Max.Y = max(bounds.Max.Y, y+1)
						}
					}
				}
				if !found {
					panic("empty pose cell")
				}
				artByPose[[2]int{char, cell.Slot}] = Art{atlas, bounds}
			}
		}
	}
	root := "/project/workplace/sprite-layers-v1"
	var receipt struct {
		LayerFrames []struct{ Fixture, Phase string } `json:"layer_frames"`
	}
	readJSON(filepath.Join(root, "receipt.json"), &receipt)
	var results []map[string]any
	for _, frame := range receipt.LayerFrames {
		if frame.Fixture == "" {
			continue
		}
		stem := frame.Fixture
		var layers []Layer
		readJSON(filepath.Join(root, stem+"-layers.json"), &layers)
		var palette [256][3]uint8
		readJSON(filepath.Join(root, stem+"-palette.json"), &palette)
		pixels, e := os.ReadFile(filepath.Join(root, stem+".idx"))
		must(e)
		original := image.NewRGBA(image.Rect(0, 0, 960, 600))
		paintLayer(original, pixels, nil, palette)
		savePNG(filepath.Join(*out, stem+"-original.png"), original)
		var missing [][2]int
		for _, layer := range layers {
			if layer.Kind == "actor" {
				if _, ok := artByPose[[2]int{layer.Draw.Character, layer.Draw.Slot}]; !ok {
					missing = append(missing, [2]int{layer.Draw.Character, layer.Draw.Slot})
				}
			}
		}
		result := map[string]any{"fixture": stem, "phase": frame.Phase, "missing_poses": missing, "hd_active": len(missing) == 0}
		if len(missing) > 0 {
			results = append(results, result)
			continue
		}
		base, e := os.ReadFile(filepath.Join(root, stem+"-layer-00.idx"))
		must(e)
		// Study-only geometry recovery. Production reads camera/source directly from DS.
		camera := -1
		for candidate := 0; candidate <= 159; candidate++ {
			match := true
			for i, v := range base {
				if v < 128 && v != assets.Reference[i/320*480+i%320+candidate] {
					match = false
					break
				}
			}
			if match {
				if camera >= 0 {
					panic("ambiguous background camera")
				}
				camera = candidate
			}
		}
		if camera < 0 {
			panic("unmatched original background")
		}
		painted := image.NewRGBA(original.Bounds())
		fullBackground := image.NewRGBA(image.Rect(0, 0, 1440, 612))
		xdraw.ApproxBiLinear.Scale(fullBackground, fullBackground.Bounds(), assets.Image, assets.Image.Bounds(), draw.Src, nil)
		draw.Draw(painted, painted.Bounds(), fullBackground, image.Pt(camera*3, 0), draw.Src)
		mask, ok, reason := assets.Foreground(hd.Frame{Scene: 4, CameraX: camera, BackgroundSHA256: hd.ReferenceSHA256, Pixels: base, Palette: palette})
		if !ok {
			panic(reason)
		}
		baseImage := &image.RGBA{Pix: mask, Stride: 320 * 4, Rect: image.Rect(0, 0, 320, 200)}
		xdraw.NearestNeighbor.Scale(painted, painted.Bounds(), baseImage, baseImage.Bounds(), draw.Over, nil)
		var actors []map[string]any
		for n, layer := range layers {
			if n == 0 {
				continue
			}
			if layer.Kind == "actor" {
				actors = append(actors, paintActor(painted, layer.Draw, artByPose[[2]int{layer.Draw.Character, layer.Draw.Slot}]))
			} else {
				raw, e := os.ReadFile(filepath.Join(root, fmt.Sprintf("%s-layer-%02d.idx", stem, n)))
				must(e)
				mask, e := os.ReadFile(filepath.Join(root, fmt.Sprintf("%s-layer-%02d.mask", stem, n)))
				must(e)
				paintLayer(painted, raw, mask, palette)
			}
		}
		// Preserve original HUD after both bodies and any later raster effects.
		draw.Draw(painted, image.Rect(0, 0, 960, 48*3), original, image.Point{}, draw.Src)
		savePNG(filepath.Join(*out, stem+"-hd.png"), painted)
		result["camera_x"] = camera
		result["actors"] = actors
		result["output_sha256"] = digest(painted.Pix)
		results = append(results, result)
	}
	b, e := json.MarshalIndent(map[string]any{"kind": "disposable HD pose and anchor study; not production or full-animation acceptance", "fixtures": results, "source": "sprite-layers-v1", "art": "hd-sprite-art-v1", "registration": "generated alpha bounds >=16, mapped to original source image rectangle; original mirror and pair clipping", "camera": "study-only unique complete original background match, production must use runtime DS metadata"}, "", "  ")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "receipt.json"), b, 0644))
	script, e := os.ReadFile("/project/tools/hd_actor_preview.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "hd_actor_preview.go"), script, 0644))
	fmt.Println(string(b))
}
