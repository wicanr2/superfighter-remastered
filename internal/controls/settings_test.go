package controls

import (
	"os"
	"path/filepath"
	"testing"
)

func TestPlayersAndFifthMoveRoundTrip(t *testing.T) {
	s := Defaults()
	s.Players[0]["phoenix"] = [4]int{5, 0, 3, 1}
	path := filepath.Join(t.TempDir(), "settings.json")
	if e := s.Save(path); e != nil {
		t.Fatal(e)
	}
	loaded, e := Load(path)
	if e != nil {
		t.Fatal(e)
	}
	if loaded.Players[0]["phoenix"] != [4]int{5, 0, 3, 1} || loaded.Players[1]["phoenix"] != [4]int{1, 2, 3, 4} {
		t.Fatal(loaded)
	}
	loaded.Players[1]["jaan"] = [4]int{4, 3, 2, 1}
	if e = loaded.Save(path); e != nil {
		t.Fatal(e)
	}
	loaded, e = Load(path)
	if e != nil || loaded.Players[1]["jaan"] != [4]int{4, 3, 2, 1} {
		t.Fatal(e, loaded)
	}
}
func TestUnknownSettingsPreserved(t *testing.T) {
	path := filepath.Join(t.TempDir(), "settings.json")
	original := []byte(`{"version":99,"players":[]}`)
	if e := os.WriteFile(path, original, 0600); e != nil {
		t.Fatal(e)
	}
	if _, e := Load(path); e == nil {
		t.Fatal("unsupported version accepted")
	}
	actual, _ := os.ReadFile(path)
	if string(actual) != string(original) {
		t.Fatal("original settings overwritten")
	}
	s := Defaults()
	s.Players[0]["jaan"] = [4]int{5, 0, 0, 0}
	if e := s.Save(path); e == nil {
		t.Fatal("unavailable move accepted")
	}
}
