package hd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"
)

func fixture() (*Assets, Frame) {
	a := &Assets{Reference: bytes.Repeat([]byte{7}, 480*204)}
	for i := range a.Palette {
		a.Palette[i] = [3]uint8{uint8(i), uint8(i), uint8(i)}
	}
	f := Frame{Scene: 4, CameraX: 80, BackgroundSHA256: ReferenceSHA256, Pixels: bytes.Repeat([]byte{7}, 64000)}
	for i, v := range a.Palette {
		f.Palette[i] = v
	}
	f.Palette[193] = [3]uint8{200, 180, 140}
	return a, f
}
func TestForegroundKeepsActorsEffectsHUDAndInput(t *testing.T) {
	a, f := fixture()
	f.Pixels[80*320+40] = 193
	f.Pixels[180*320+40] = 160
	f.Pixels[100*320+90] = 15
	before := append([]byte(nil), f.Pixels...)
	mask, ok, why := a.Foreground(f)
	if !ok {
		t.Fatal(why)
	}
	for _, i := range []int{10*320 + 10, 80*320 + 40, 180*320 + 40, 100*320 + 90} {
		if mask[i*4+3] != 255 {
			t.Fatalf("original foreground removed at %d", i)
		}
	}
	i := 100*320 + 200
	if !bytes.Equal(mask[i*4:i*4+4], []byte{0, 0, 0, 0}) {
		t.Fatal("transparent pixel must be premultiplied black")
	}
	if !bytes.Equal(f.Pixels, before) {
		t.Fatal("original frame mutated")
	}
}
func TestUnsupportedSourcesReturnCompleteOriginal(t *testing.T) {
	a, f := fixture()
	for _, change := range []func(*Frame){func(f *Frame) { f.Scene = 0 }, func(f *Frame) { f.CameraX = -1 }, func(f *Frame) { f.CameraX = 160 }, func(f *Frame) { f.BackgroundSHA256 = "unknown" }, func(f *Frame) { f.Palette[7] = [3]uint8{} }, func(f *Frame) { f.Pixels = f.Pixels[:2] }} {
		copy := f
		change(&copy)
		mask, ok, _ := a.Foreground(copy)
		if ok || mask != nil {
			t.Fatal("unknown input produced partial HD frame")
		}
	}
}
func TestRealOriginalFramesPreserveEveryForegroundPixel(t *testing.T) {
	root := os.Getenv("KDZZ_HD_FIXTURES")
	assets := os.Getenv("KDZZ_HD_ASSETS")
	if root == "" || assets == "" {
		t.Skip("local copyrighted fixtures not supplied")
	}
	a, e := Load(assets)
	if e != nil {
		t.Fatal(e)
	}
	tested := 0
	for _, name := range []string{"hd-frame-single-v2", "hd-frame-versus-v2"} {
		dir := filepath.Join(root, name)
		b, e := os.ReadFile(filepath.Join(dir, "receipt.json"))
		if e != nil {
			t.Fatal(e)
		}
		var r struct {
			Frames []struct {
				Scene         int    `json:"scene"`
				CameraX       int    `json:"camera_x"`
				BackgroundSHA string `json:"background_ram_sha256"`
			}
		}
		if e = json.Unmarshal(b, &r); e != nil {
			t.Fatal(e)
		}
		files, e := filepath.Glob(filepath.Join(dir, "*.idx"))
		if e != nil {
			t.Fatal(e)
		}
		for _, file := range files {
			var frameNo int
			if _, e = fmt.Sscanf(filepath.Base(file), "%d-", &frameNo); e != nil {
				t.Fatal(e)
			}
			meta := r.Frames[frameNo-1]
			pixels, e := os.ReadFile(file)
			if e != nil {
				t.Fatal(e)
			}
			pb, e := os.ReadFile(file[:len(file)-4] + "-palette.json")
			if e != nil {
				t.Fatal(e)
			}
			frame := Frame{Scene: meta.Scene, CameraX: meta.CameraX, BackgroundSHA256: meta.BackgroundSHA, Pixels: pixels}
			if e = json.Unmarshal(pb, &frame.Palette); e != nil {
				t.Fatal(e)
			}
			mask, ok, why := a.Foreground(frame)
			if !ok {
				t.Fatal(file, why)
			}
			transparent := 0
			for i, v := range pixels {
				if i/320 < HUDRows || v >= 128 {
					if mask[i*4+3] != 255 {
						t.Fatal("foreground lost", file, i)
					}
					rgb := frame.Palette[v]
					if !bytes.Equal(mask[i*4:i*4+3], rgb[:]) {
						t.Fatal("original color changed", file, i)
					}
				}
				if mask[i*4+3] == 0 {
					transparent++
				}
			}
			if transparent < 10000 {
				t.Fatal("no useful HD background", file, transparent)
			}
			tested++
		}
	}
	if tested != 16 {
		t.Fatalf("wanted 16 original frame samples, got %d", tested)
	}
	// 損壞素材必須在載入時失敗，不產生半套背景。
	bad := t.TempDir()
	entries, e := os.ReadDir(assets)
	if e != nil {
		t.Fatal(e)
	}
	for _, item := range entries {
		data, e := os.ReadFile(filepath.Join(assets, item.Name()))
		if e != nil {
			t.Fatal(e)
		}
		if item.Name() == "rooftop.png" {
			data[16] ^= 1
		}
		if e = os.WriteFile(filepath.Join(bad, item.Name()), data, 0600); e != nil {
			t.Fatal(e)
		}
	}
	if _, e = Load(bad); e == nil {
		t.Fatal("corrupt HD image accepted")
	}
}
