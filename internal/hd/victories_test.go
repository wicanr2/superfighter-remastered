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

func TestOriginalVictoryDrawsAndSelection(t *testing.T) {
	root, original := os.Getenv("KDZZ_HD_FIXTURES"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("local original fixtures not supplied")
	}
	a, e := LoadVictories(original)
	if e != nil {
		t.Fatal(e)
	}
	read := func(path string) []byte {
		t.Helper()
		b, e := os.ReadFile(path)
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	tested := 0
	for _, name := range []string{"victory-draw-v1", "victory-draw-v2", "victory-draw-v3"} {
		dir := filepath.Join(root, name)
		var receipt struct {
			Records []struct {
				Fixture string
				State   renderdata.VictoryState
				Draws   []renderdata.VictoryDraw
			}
		}
		if e := json.Unmarshal(read(filepath.Join(dir, "receipt.json")), &receipt); e != nil {
			t.Fatal(e)
		}
		for _, record := range receipt.Records {
			stem := filepath.Join(dir, record.Fixture)
			before, after, mask := read(stem+".before.vram"), read(stem+".after.vram"), read(stem+".mask")
			if len(before) != 65536 || len(after) != 65536 || len(mask) != 65536 {
				t.Fatal("incomplete VRAM")
			}
			s := &renderdata.VictorySnapshot{State: record.State, Draws: record.Draws, Complete: true, Underlay: renderdata.Layer{Indices: append([]byte(nil), before[:64000]...), Coverage: bytes.Repeat([]byte{1}, 64000)}}
			for i := range s.Draws {
				s.Draws[i].Source = read(fmt.Sprintf("%s-draw-%02d.source", stem, i))
			}
			layers := make([]renderdata.Layer, 6)
			layers[5] = renderdata.Layer{Indices: append([]byte(nil), after[:64000]...), Coverage: bytes.Repeat([]byte{1}, 64000)}
			var palette [256][3]uint8
			if e := json.Unmarshal(read(stem+".palette.json"), &palette); e != nil {
				t.Fatal(e)
			}
			selection, why := a.Select(s, layers, palette, s.State.Counter)
			if selection == nil {
				t.Fatal(name, record.Fixture, why)
			}
			if !bytes.Equal(selection.Replace, mask[:64000]) || len(selection.Runs) != 2 {
				t.Fatal("actual STOSB coverage differs")
			}
			if !bytes.Equal(s.Underlay.Indices, before[:64000]) || !bytes.Equal(layers[5].Indices, after[:64000]) {
				t.Fatal("source mutated")
			}
			for _, mutate := range []func(*renderdata.VictorySnapshot){
				func(s *renderdata.VictorySnapshot) { s.Complete = false },
				func(s *renderdata.VictorySnapshot) { s.Draws[0].X++ },
				func(s *renderdata.VictorySnapshot) { s.Draws[0].Caller++ },
				func(s *renderdata.VictorySnapshot) { s.Draws[0].SourceSHA256 = "unknown" },
				func(s *renderdata.VictorySnapshot) { s.Draws[0].SourceSI++ },
				func(s *renderdata.VictorySnapshot) { s.Draws = s.Draws[:1] },
			} {
				bad := *s
				bad.Draws = append([]renderdata.VictoryDraw(nil), s.Draws...)
				mutate(&bad)
				if selected, _ := a.Select(&bad, layers, palette, s.State.Counter); selected != nil {
					t.Fatal("unknown victory input accepted")
				}
			}
			layers[5].Indices[0] ^= 1
			if selected, _ := a.Select(s, layers, palette, s.State.Counter); selected != nil {
				t.Fatal("unobserved write accepted")
			}
			tested++
		}
	}
	if tested != 4 {
		t.Fatal("expected four replays of two unique normal victories", tested)
	}
}

func TestStaticSpecialVictoryGlyphs(t *testing.T) {
	original := os.Getenv("KDZZ_ORIGINAL_ROOT")
	if original == "" {
		t.Skip("local original sources not supplied")
	}
	a, e := LoadVictories(original)
	if e != nil {
		t.Fatal(e)
	}
	for _, test := range []struct {
		slot  int
		state renderdata.VictoryState
		label string
	}{
		{14, renderdata.VictoryState{Characters: [2]uint16{0, 4}, Health: [2]uint16{124, 0}, Flags: [2]uint8{2, 4}}, "YOU WIN"},
		{15, renderdata.VictoryState{Winner: 0x8004, Characters: [2]uint16{0, 4}, Health: [2]uint16{0, 124}, Flags: [2]uint8{2, 4}}, "YOU LOSE"},
		{16, renderdata.VictoryState{Characters: [2]uint16{0, 4}, Health: [2]uint16{124, 124}, Flags: [2]uint8{2, 3}}, "DRAW GAME"},
	} {
		runs, ok := a.Layout(test.state)
		if !ok || len(runs) != 1 || runs[0].Slot != test.slot || runs[0].Label != test.label {
			t.Fatal("static branch differs", test.slot)
		}
		run, g := runs[0], a.glyphs[test.slot]
		source := append([]byte{byte(g.width), byte(g.height)}, g.pixels...)
		d := renderdata.VictoryDraw{Slot: test.slot, X: run.Bounds.Min.X, Y: run.Bounds.Min.Y, Width: g.width, Height: g.height, Caller: run.Caller, SourceSI: a.offsets[test.slot], Palette: 0xa0, Source: source, SourceSHA256: fmt.Sprintf("%x", sha256.Sum256(source))}
		indices, coverage := make([]byte, 64000), make([]byte, 64000)
		if !d.Paint(indices, coverage) {
			t.Fatal("valid original glyph rejected")
		}
		var palette [256][3]uint8
		for i, p := range a.palette {
			palette[0xa0+i] = p
		}
		layers := make([]renderdata.Layer, 6)
		layers[5] = renderdata.Layer{Indices: indices, Coverage: coverage}
		s := &renderdata.VictorySnapshot{State: test.state, Draws: []renderdata.VictoryDraw{d}, Complete: true, Underlay: renderdata.Layer{Indices: make([]byte, 64000), Coverage: make([]byte, 64000)}}
		if selected, why := a.Select(s, layers, palette, 0); selected == nil {
			t.Fatal(why)
		}
		palette[0xa1][0] ^= 1
		if selected, _ := a.Select(s, layers, palette, 0); selected != nil {
			t.Fatal("unknown palette accepted")
		}
	}
}
