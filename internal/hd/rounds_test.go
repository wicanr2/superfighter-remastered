package hd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"image"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/gamecore"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestRoundPairedOriginalFramesAndRejection(t *testing.T) {
	root, fixtures := os.Getenv("KDZZ_ORIGINAL_ROOT"), os.Getenv("KDZZ_HD_FIXTURES")
	if root == "" || fixtures == "" {
		t.Skip("local original round fixtures not supplied")
	}
	a, e := LoadRounds(root)
	if e != nil {
		t.Fatal(e)
	}
	hud, e := LoadHUD(root)
	if e != nil {
		t.Fatal(e)
	}
	shadows, e := LoadShadows(root)
	if e != nil {
		t.Fatal(e)
	}
	directory := filepath.Join(fixtures, "round-core-compat-v1")
	read := func(name string) []byte {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(directory, name))
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	var receipt struct {
		Fixtures []string `json:"round_fixtures"`
		Checks   int      `json:"checks"`
	}
	if e = json.Unmarshal(read("receipt.json"), &receipt); e != nil {
		t.Fatal(e)
	}
	if len(receipt.Fixtures) != 66 || receipt.Checks < 1500 {
		t.Fatal("incomplete paired original opening")
	}
	stages, widths := map[uint16]bool{}, map[int]bool{}
	copied := 0
	for _, stem := range receipt.Fixtures {
		var f gamecore.Presentation
		if e = json.Unmarshal(read(stem+".frame.json"), &f); e != nil {
			t.Fatal(e)
		}
		if e = json.Unmarshal(read(stem+".palette.json"), &f.Palette); e != nil {
			t.Fatal(e)
		}
		f.Pixels = read(stem + ".idx")
		for i := range f.Layers {
			f.Layers[i].Indices = read(stem + fmt.Sprintf(".layer-%02d.idx", i))
			f.Layers[i].Coverage = read(stem + fmt.Sprintf(".layer-%02d.mask", i))
		}
		if !renderdata.Match(f.Layers, f.Pixels) || f.RetainedBackgroundRows != 12 || f.RoundMessage == nil {
			t.Fatal(stem, "original frame mismatch")
		}
		s := f.RoundMessage
		s.Source = read(stem + ".round.source")
		s.Underlay = renderdata.Layer{Indices: read(stem + ".round-under.idx"), Coverage: read(stem + ".round-under.mask")}
		before := append([]byte(nil), f.Layers[len(f.Layers)-1].Indices...)
		selected, why := a.Select(s, f.Layers, f.Palette, f.Counter)
		if selected == nil {
			t.Fatal(stem, why)
		}
		if !bytes.Equal(before, f.Layers[len(f.Layers)-1].Indices) {
			t.Fatal("original layer modified")
		}
		window, ok := s.Window()
		if !ok || window != selected.Window {
			t.Fatal("window mismatch")
		}
		writes := 0
		for i, v := range selected.Replace {
			if v != 0 {
				writes++
				if !image.Pt(i%320, i/320).In(window) || f.Layers[len(f.Layers)-1].Coverage[i] != 1 {
					t.Fatal("replacement outside original message writes")
				}
			}
		}
		if writes == 0 {
			t.Fatal("missing actual source writes")
		}
		stages[s.Stage], widths[s.Width] = true, true
		if s.Stage == 1 && s.HalfWidth == 4 {
			copied++
		}
		f.HUD.Bitmap = read(stem + ".hud.bitmap")
		f.HUD.Underlay = renderdata.Layer{Indices: read(stem + ".hud-under.idx"), Coverage: read(stem + ".hud-under.mask")}
		if got, why := hud.Select(f.HUD, f.Pixels, f.Palette, f.Layers); got == nil {
			t.Fatal(stem, "HUD", why)
		}
		f.Shadows.Underlay = renderdata.Layer{Indices: read(stem + ".shadow-under.idx"), Coverage: read(stem + ".shadow-under.mask")}
		if got, why := shadows.Select(f.Shadows, f.Layers, f.Palette, f.Counter, f.CameraX); got == nil {
			t.Fatal(stem, "shadows", why)
		}
		for _, mutate := range []func(*renderdata.RoundSnapshot){
			func(s *renderdata.RoundSnapshot) { s.Complete = false }, func(s *renderdata.RoundSnapshot) { s.Counter++ }, func(s *renderdata.RoundSnapshot) { s.Stage = 4 }, func(s *renderdata.RoundSnapshot) { s.HalfWidth = 0 }, func(s *renderdata.RoundSnapshot) { s.Column++ }, func(s *renderdata.RoundSnapshot) { s.Width++ }, func(s *renderdata.RoundSnapshot) { s.X++ }, func(s *renderdata.RoundSnapshot) { s.Y++ }, func(s *renderdata.RoundSnapshot) { s.RoundIndex = 9 }, func(s *renderdata.RoundSnapshot) { s.SourceSHA256 = "wrong" },
		} {
			bad := *s
			mutate(&bad)
			if got, _ := a.Select(&bad, f.Layers, f.Palette, f.Counter); got != nil {
				t.Fatal(stem, "bad state accepted")
			}
		}
		bad := *s
		bad.Source = append([]byte(nil), s.Source...)
		bad.Source[100] ^= 1
		if got, _ := a.Select(&bad, f.Layers, f.Palette, f.Counter); got != nil {
			t.Fatal("bad source accepted")
		}
		bad = *s
		bad.Underlay.Coverage = append([]byte(nil), s.Underlay.Coverage...)
		bad.Underlay.Coverage[0] = 2
		if got, _ := a.Select(&bad, f.Layers, f.Palette, f.Counter); got != nil {
			t.Fatal("bad underlay mask accepted")
		}
		palette := f.Palette
		palette[0xa0][0] ^= 1
		if got, _ := a.Select(s, f.Layers, palette, f.Counter); got != nil {
			t.Fatal("bad palette accepted")
		}
	}
	if len(stages) != 4 || len(widths) != 12 || copied != 1 {
		t.Fatal("incomplete stage/window/post-copy coverage")
	}
	t.Logf("verified actual opening frames: %d; stages %d; widths %d; post-copy %d", len(receipt.Fixtures), len(stages), len(widths), copied)
	copyRoot := t.TempDir()
	for _, name := range []string{"NAME.XBB", "0-9.XBB", "BOARD.COL"} {
		b, e := os.ReadFile(filepath.Join(root, name))
		if e != nil {
			t.Fatal(e)
		}
		if name == "NAME.XBB" {
			b[8506] ^= 1
		}
		if e = os.WriteFile(filepath.Join(copyRoot, name), b, 0600); e != nil {
			t.Fatal(e)
		}
	}
	if _, e = LoadRounds(copyRoot); e == nil {
		t.Fatal("damaged source accepted")
	}
}
