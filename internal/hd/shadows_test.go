package hd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestShadowPairedOriginalFramesAndAtomicRejection(t *testing.T) {
	root, fixtures := os.Getenv("KDZZ_ORIGINAL_ROOT"), os.Getenv("KDZZ_HD_FIXTURES")
	if root == "" || fixtures == "" {
		t.Skip("local original shadow fixtures not supplied")
	}
	a, e := LoadShadows(root)
	if e != nil {
		t.Fatal(e)
	}
	directory := filepath.Join(fixtures, "shadow-core-compat-v1")
	read := func(name string) []byte {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(directory, name))
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	var receipt struct {
		Fixtures []string `json:"shadow_fixtures"`
	}
	if e = json.Unmarshal(read("receipt.json"), &receipt); e != nil {
		t.Fatal(e)
	}
	if len(receipt.Fixtures) == 0 {
		t.Fatal("no actual paired shadow fixtures")
	}
	for _, stem := range receipt.Fixtures {
		var frame gamecore.Presentation
		if e = json.Unmarshal(read(stem+".json"), &frame); e != nil {
			t.Fatal(e)
		}
		if e = json.Unmarshal(read(stem+".palette.json"), &frame.Palette); e != nil {
			t.Fatal(e)
		}
		frame.Pixels = read(stem + ".idx")
		for index := range frame.Layers {
			frame.Layers[index].Indices = read(stem + fmt.Sprintf(".layer-%02d.idx", index))
			frame.Layers[index].Coverage = read(stem + fmt.Sprintf(".layer-%02d.mask", index))
		}
		if !renderdata.Match(frame.Layers, frame.Pixels) || frame.Shadows == nil {
			t.Fatal("original paired frame does not replay", stem)
		}
		frame.Shadows.Underlay = renderdata.Layer{Indices: read(stem + ".shadow-under.idx"), Coverage: read(stem + ".shadow-under.mask")}
		before := append([]byte(nil), frame.Layers[1].Indices...)
		selected, why := a.Select(frame.Shadows, frame.Layers, frame.Palette, frame.Counter, frame.CameraX)
		if selected == nil {
			t.Fatal(stem, why)
		}
		if !bytes.Equal(before, frame.Layers[1].Indices) {
			t.Fatal("source layer changed")
		}
		covered := 0
		for i, v := range selected.Replace {
			if v != 0 {
				covered++
				if frame.Layers[1].Coverage[i] != 1 || frame.Layers[1].Indices[i] != 0xa7 {
					t.Fatal("replacement outside actual shadow writes")
				}
			}
		}
		if covered == 0 {
			t.Fatal("missing paired shadow mask")
		}
		for _, mutate := range []func(*renderdata.ShadowSnapshot){
			func(s *renderdata.ShadowSnapshot) { s.Complete = false },
			func(s *renderdata.ShadowSnapshot) { s.Counter++ },
			func(s *renderdata.ShadowSnapshot) { s.CameraX++ },
			func(s *renderdata.ShadowSnapshot) { s.Draws[0].SourceSHA256 = "wrong" },
			func(s *renderdata.ShadowSnapshot) { s.Draws[1].Player = 0 },
			func(s *renderdata.ShadowSnapshot) { s.Draws[0].LeftClip++ },
			func(s *renderdata.ShadowSnapshot) { s.Draws[0].Y++ },
		} {
			bad := *frame.Shadows
			mutate(&bad)
			if got, _ := a.Select(&bad, frame.Layers, frame.Palette, frame.Counter, frame.CameraX); got != nil {
				t.Fatal("bad shadow state accepted", stem)
			}
		}
		badPalette := frame.Palette
		badPalette[0xa7][0] ^= 1
		if got, _ := a.Select(frame.Shadows, frame.Layers, badPalette, frame.Counter, frame.CameraX); got != nil {
			t.Fatal("unknown shadow palette accepted")
		}
		bad := *frame.Shadows
		bad.Underlay.Coverage = append([]byte(nil), bad.Underlay.Coverage...)
		bad.Underlay.Coverage[0] = 2
		if got, _ := a.Select(&bad, frame.Layers, frame.Palette, frame.Counter, frame.CameraX); got != nil {
			t.Fatal("bad coverage accepted")
		}
	}
	t.Logf("verified actual paired shadow frames: %d", len(receipt.Fixtures))
	copyRoot := t.TempDir()
	for _, name := range []string{"SHADOW.XLP", "BOARD.COL"} {
		b, e := os.ReadFile(filepath.Join(root, name))
		if e != nil {
			t.Fatal(e)
		}
		if name == "SHADOW.XLP" {
			b[2] ^= 1
		}
		if e = os.WriteFile(filepath.Join(copyRoot, name), b, 0600); e != nil {
			t.Fatal(e)
		}
	}
	if _, e = LoadShadows(copyRoot); e == nil {
		t.Fatal("damaged shadow source accepted")
	}
}
