package controls

import (
	"encoding/json"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestKeyboardLegacyAndRoundTrip(t *testing.T) {
	s := Defaults()
	s.Players[0]["phoenix"] = [4]int{5, 0, 2, 1}
	s.Keyboard = nil
	b, _ := json.Marshal(s)
	p := filepath.Join(t.TempDir(), "settings.json")
	if err := os.WriteFile(p, b, 0600); err != nil {
		t.Fatal(err)
	}
	loaded, err := Load(p)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(loaded.Keyboard, KeyboardDefaults()) || !reflect.DeepEqual(loaded.Players, s.Players) {
		t.Fatal("legacy defaults or move settings changed")
	}
	after, _ := os.ReadFile(p)
	if string(after) != string(b) {
		t.Fatal("legacy file overwritten")
	}
	if err := loaded.BindKey(0, 4, "L"); err != nil {
		t.Fatal(err)
	}
	if err := loaded.BindKey(0, 10, "F5"); err != nil {
		t.Fatal(err)
	}
	if err := loaded.Save(p); err != nil {
		t.Fatal(err)
	}
	restored, err := Load(p)
	if err != nil || !reflect.DeepEqual(restored, loaded) {
		t.Fatal(err, restored)
	}
}

func TestKeyboardConflictAndInvalidInput(t *testing.T) {
	s := Defaults()
	for _, key := range []string{"Q", "NumpadEnter", "Escape", "F9", "F10", "F11", "F12", "nonsense"} {
		if err := s.BindKey(0, 10, key); err == nil {
			t.Fatal("conflicting/reserved key accepted", key)
		}
		if s.Keyboard[0][10] != "Digit1" {
			t.Fatal("rejected binding changed old value")
		}
	}
	if err := s.BindKey(0, 10, ""); err != nil {
		t.Fatal(err)
	}
	if err := s.BindKey(1, 10, "Digit1"); err != nil {
		t.Fatal(err)
	}
	s.Keyboard[0] = s.Keyboard[0][:13]
	if s.Validate() == nil {
		t.Fatal("partial row accepted")
	}
}

func TestKeyboardIndependentOriginalOutputs(t *testing.T) {
	s := Defaults()
	if err := s.BindKey(0, 4, "L"); err != nil {
		t.Fatal(err)
	}
	down := map[string]bool{"L": true, "Numpad4": true, "Digit1": true, "Digit8": true}
	scans, quick, neutral := s.KeyboardInput(func(k string) bool { return down[k] })
	if neutral || !reflect.DeepEqual(scans, [2][]uint8{{0x20}, {0x4b}}) || quick != [2][4]bool{{true, false, false, false}, {false, true, false, false}} {
		t.Fatal(scans, quick, neutral)
	}
	scans, quick, neutral = s.KeyboardInput(func(k string) bool { return k == "NumpadEnter" })
	if neutral || len(scans[0]) != 0 || !reflect.DeepEqual(scans[1], []uint8{0x1c}) || quick != [2][4]bool{} {
		t.Fatal("original P2 Enter alias changed")
	}
	_, _, neutral = s.KeyboardInput(func(string) bool { return false })
	if !neutral {
		t.Fatal("released input not neutral")
	}
}
