package hd

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

func TestOriginalHUDSourcesVisibleHealthAndScoreLatch(t *testing.T) {
	root, fixtures := os.Getenv("KDZZ_ORIGINAL_ROOT"), os.Getenv("KDZZ_HD_FIXTURES")
	if root == "" || fixtures == "" {
		t.Skip("local original HUD fixtures not supplied")
	}
	a, e := LoadHUD(root)
	if e != nil {
		t.Fatal(e)
	}
	var receipt struct {
		Records []struct {
			State   renderdata.HUDState `json:"state"`
			Fixture string              `json:"fixture"`
		} `json:"records"`
	}
	b, e := os.ReadFile(filepath.Join(fixtures, "hud-draw-v3", "receipt.json"))
	if e != nil {
		t.Fatal(e)
	}
	if e = json.Unmarshal(b, &receipt); e != nil {
		t.Fatal(e)
	}
	read := func(name string) []byte {
		t.Helper()
		b, e := os.ReadFile(filepath.Join(fixtures, "hud-draw-v3", name))
		if e != nil {
			t.Fatal(e)
		}
		return b
	}
	var palette [256][3]uint8
	verified, pending, latch := 0, false, false
	for _, record := range receipt.Records {
		if record.Fixture == "" {
			continue
		}
		stem := record.Fixture
		bitmap := read(stem + ".bitmap")
		before, after, mask := read(stem+".before.idx"), read(stem+".after.idx"), read(stem+".mask")
		if e = json.Unmarshal(read(stem+".palette.json"), &palette); e != nil {
			t.Fatal(e)
		}
		full := make([]byte, 64000)
		for i := range full {
			full[i] = 1
		}
		snapshot := &renderdata.HUDSnapshot{State: record.State, Bitmap: bitmap, BitmapSHA256: fmt.Sprintf("%x", sha256.Sum256(bitmap)), Complete: true, Underlay: renderdata.Layer{Indices: before, Coverage: full}}
		layers := make([]renderdata.Layer, 6)
		layers[5] = renderdata.Layer{Indices: after, Coverage: mask}
		selected, reason := a.Select(snapshot, after, palette, layers)
		if selected == nil {
			t.Fatalf("%s: %s", stem, reason)
		}
		if selected.State.Health != record.State.Health {
			t.Fatal("visible health changed")
		}
		for offset, value := range bitmap {
			// 勝場圖示只在前十二列；其餘非零介面像素都應有高解析替換。
			if offset/320 >= 12 && value != 0 && selected.Replace[record.State.Rows*320+offset] != 1 {
				t.Fatalf("%s: original HUD pixel left outside replacement at %d,%d", stem, offset%320, offset/320)
			}
		}
		if record.State.Pending != [2]uint16{} {
			pending = true
		}
		if record.State.Wins != record.State.DisplayWins {
			latch = true
			wrong := *snapshot
			wrong.State.DisplayWins = wrong.State.Wins
			if got, _ := a.Select(&wrong, after, palette, layers); got != nil {
				t.Fatal("raw win count incorrectly replaces visible score latch")
			}
		}
		badPalette := palette
		badPalette[0xae][0] ^= 1
		if got, _ := a.Select(snapshot, after, badPalette, layers); got != nil {
			t.Fatal("wrong HUD palette accepted")
		}
		for _, mutate := range []func(*renderdata.HUDSnapshot){func(s *renderdata.HUDSnapshot) { s.Complete = false }, func(s *renderdata.HUDSnapshot) { s.State.Health[0] = 125 }, func(s *renderdata.HUDSnapshot) { s.State.Timer = 100 }, func(s *renderdata.HUDSnapshot) { s.BitmapSHA256 = "wrong" }} {
			wrong := *snapshot
			mutate(&wrong)
			if got, _ := a.Select(&wrong, after, palette, layers); got != nil {
				t.Fatal("invalid HUD state accepted")
			}
		}
		verified++
	}
	if verified != 33 || !pending || !latch {
		t.Fatalf("coverage fixtures=%d pending=%t latch=%t", verified, pending, latch)
	}
	t.Logf("verified source HUD fixtures: %d, including pending damage and visible score latch", verified)
	copyRoot := t.TempDir()
	for _, name := range []string{"SF.EXE", "BOARD.XBB", "NAME.XBB", "0-9.XBB", "BOARD.COL"} {
		b, e := os.ReadFile(filepath.Join(root, name))
		if e != nil {
			t.Fatal(e)
		}
		if name == "BOARD.XBB" {
			b[0] ^= 1
		}
		if e = os.WriteFile(filepath.Join(copyRoot, name), b, 0600); e != nil {
			t.Fatal(e)
		}
	}
	if _, e = LoadHUD(copyRoot); e == nil {
		t.Fatal("damaged original HUD source accepted")
	}
}
