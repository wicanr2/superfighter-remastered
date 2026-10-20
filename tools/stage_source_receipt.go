// Disposable normal-input stage inventory; no production format or state writes.
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }

type background struct {
	file, sourceHash string
	pixels, palette  []byte
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
	writeJSON := func(path string, v any) {
		b, e := json.MarshalIndent(v, "", "  ")
		must(e)
		must(os.WriteFile(path, append(b, '\n'), 0644))
	}
	script, e := os.ReadFile("/project/tools/stage_source_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "stage_source_receipt.go"), script, 0644))
	input, e := os.ReadFile("/project/workplace/source-manifest.json")
	must(e)
	var inventory struct {
		Files []struct{ Name, SHA256 string }
	}
	must(json.Unmarshal(input, &inventory))
	wants := map[string]string{}
	for _, item := range inventory.Files {
		wants[item.Name] = item.SHA256
	}
	var files []string
	for name := range wants {
		if strings.HasPrefix(name, "I") && strings.HasSuffix(name, ".XGB") {
			files = append(files, name)
		}
	}
	sort.Strings(files)
	if len(files) != 11 {
		panic("expected eleven original XGB files")
	}
	references := map[string]background{}
	var decoded []map[string]any
	for _, name := range files {
		b, e := os.ReadFile(filepath.Join("/orig", name))
		must(e)
		if digest(b) != wants[name] || len(b) < 774 || binary.LittleEndian.Uint16(b) != 480 || binary.LittleEndian.Uint16(b[2:]) != 204 || b[4] != 1 {
			panic("source/header mismatch: " + name)
		}
		pixels := make([]byte, 0, 480*204)
		for pos := 774; pos < len(b); {
			value := b[pos]
			pos++
			count := 1
			if value == b[773] {
				if pos+2 > len(b) {
					panic("truncated run")
				}
				count = int(b[pos])
				value = b[pos+1]
				pos += 2
			}
			if count == 0 || len(pixels)+count > 480*204 {
				panic("run out of bounds")
			}
			for i := 0; i < count; i++ {
				pixels = append(pixels, value)
			}
		}
		if len(pixels) != 480*204 {
			panic("decoded dimensions differ")
		}
		palette := make([]byte, 384)
		for i, v := range b[5:389] {
			if v > 63 {
				panic("invalid six-bit palette")
			}
			palette[i] = v<<2 | v>>4
		}
		hash := digest(pixels)
		if _, ok := references[hash]; ok {
			panic("ambiguous reference pixels")
		}
		references[hash] = background{name, wants[name], pixels, palette}
		decoded = append(decoded, map[string]any{"file": name, "source_sha256": wants[name], "pixels_sha256": hash, "palette_sha256": digest(palette)})
	}
	writeJSON(filepath.Join(*out, "decoded-inputs.json"), decoded)
	var stages []map[string]any
	for player1 := 0; player1 < 11; player1++ {
		dir := filepath.Join(*out, fmt.Sprintf("versus-00-%02d", player1))
		must(os.Mkdir(dir, 0755))
		c, e := gamecore.New("/orig", filepath.Join(dir, "user-data"))
		must(e)
		c.EnableEffects()
		c.EnableHUD()
		c.EnableShadows()
		c.EnableRounds()
		c.EnableDisplay()
		c.Pause(false)
		step := func(n uint64) {
			must(c.Step(n))
			if c.Status().Steps > 400_000_000 {
				panic("stage instruction budget exceeded")
			}
		}
		step(40_000_000)
		must(c.Mouse(125, 181, true))
		step(1_000_000)
		must(c.Mouse(125, 181, false))
		step(24_000_000)
		must(c.MenuKey("Return"))
		step(20_000_000)
		for i := 0; i < player1; i++ {
			must(c.MenuKey("Right"))
			step(1_000_000)
		}
		must(c.MenuKey("Return"))
		step(75_000_000)
		selected := c.Status().Fighters
		if selected[0] != 0 || selected[1] != player1 {
			panic(fmt.Sprintf("normal selection mismatch %v", selected))
		}
		ready := func() gamecore.Presentation {
			for {
				f := c.Presentation()
				if c.Status().Battle && f.LayersComplete && f.HUD != nil && f.HUD.State.RoundState == 0 && f.RoundMessage == nil && f.RetainedBackgroundRows == 0 && f.Scanout != nil {
					return f
				}
				step(250_000)
			}
		}
		f := ready()
		ref, ok := references[f.BackgroundSHA256]
		if !ok {
			panic("unknown complete background RAM hash")
		}
		var samples []map[string]any
		save := func(name string, f gamecore.Presentation) {
			if f.BackgroundSHA256 != digest(ref.pixels) || len(f.Layers) == 0 || !f.Layers[0].Background || f.CameraX < 0 || f.CameraX > 160 || len(f.Layers[0].Indices) != 64000 || len(f.Layers[0].Coverage) != 64000 || !f.Scanout.Matches(f.Pixels, f.VRAMTail) {
				panic("incomplete stage source")
			}
			for i := 0; i < 128; i++ {
				for k := 0; k < 3; k++ {
					if f.Palette[i][k] != ref.palette[i*3+k] {
						panic("runtime background palette mismatch")
					}
				}
			}
			for y := 0; y < 200; y++ {
				if !bytes.Equal(f.Layers[0].Indices[y*320:(y+1)*320], ref.pixels[y*480+f.CameraX:y*480+f.CameraX+320]) {
					panic("camera crop differs from original file")
				}
			}
			for _, v := range f.Layers[0].Coverage {
				if v != 1 {
					panic("background coverage incomplete")
				}
			}
			writeJSON(filepath.Join(dir, name+".frame.json"), f)
			writeJSON(filepath.Join(dir, name+".palette.json"), f.Palette)
			must(os.WriteFile(filepath.Join(dir, name+".background.idx"), f.Layers[0].Indices, 0644))
			samples = append(samples, map[string]any{"name": name, "steps": f.Steps, "serial": f.Serial, "scene": f.Scene, "camera_x": f.CameraX, "background_sha256": f.BackgroundSHA256, "background_crop_matches": true, "palette_matches": true, "scanout_matches": true})
		}
		save("idle", f)
		must(c.SetInput([]gamecore.Source{{Player: 0, Name: "keyboard", Keys: []uint8{0x20}}}))
		target := c.Status().Frames + 20
		for c.Status().Frames < target {
			step(250_000)
		}
		must(c.SetInput(nil))
		f = ready()
		save("walk", f)
		must(os.WriteFile(filepath.Join(dir, "reference.idx"), ref.pixels, 0644))
		must(os.WriteFile(filepath.Join(dir, "palette.rgb"), ref.palette, 0644))
		row := map[string]any{"player0": 0, "player1": player1, "scene": f.Scene, "source": ref.file, "source_sha256": ref.sourceHash, "samples": samples, "training_modified": c.Status().Training.Modified}
		writeJSON(filepath.Join(dir, "receipt.json"), row)
		stages = append(stages, row)
		c.Close()
		runtime.GC()
		fmt.Println("verified", player1, "scene", f.Scene, ref.file, "camera", samples[0]["camera_x"], samples[1]["camera_x"])
	}
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "normal versus stage source inventory, not native HD integration", "script_sha256": digest(script), "source_manifest_sha256": digest(input), "go_version": runtime.Version(), "address_space": "gamecore read-only DOS runtime snapshots; no IDA addresses", "decoded": decoded, "stages": stages, "limits": "P1 Jaan / each P2 normal selection; idle and twenty-frame walk samples only, no new renderer format, all-camera coverage, single-player scene order or full HD claim"})
}
