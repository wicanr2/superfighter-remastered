package controls

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestLegacySettingsAddBossesWithoutOverwriting(t *testing.T) {
	s := Defaults()
	s.Players[0]["jaan"] = [4]int{4, 0, 2, 1}
	s.Players[1]["phoenix"] = [4]int{5, 4, 0, 2}
	for p := range s.Players {
		for _, id := range []string{"spider", "clown", "joe"} {
			delete(s.Players[p], id)
		}
	}
	b, err := json.Marshal(s)
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(t.TempDir(), "settings.json")
	if err = os.WriteFile(path, b, 0600); err != nil {
		t.Fatal(err)
	}
	got, err := Load(path)
	if err != nil {
		t.Fatal(err)
	}
	if got.Players[0]["jaan"] != s.Players[0]["jaan"] || got.Players[1]["phoenix"] != s.Players[1]["phoenix"] || got.Players[0]["spider"] != [4]int{1, 2, 0, 0} {
		t.Fatal(got)
	}
	after, _ := os.ReadFile(path)
	if string(after) != string(b) {
		t.Fatal("load overwrote legacy input")
	}
	got.Players[1]["clown"] = [4]int{5, 0, 3, 1}
	if err = got.Save(path); err != nil {
		t.Fatal(err)
	}
	loaded, err := Load(path)
	if err != nil || loaded.Players[1]["clown"] != got.Players[1]["clown"] || loaded.Players[0]["clown"] != [4]int{1, 2, 3, 4} {
		t.Fatal(err, loaded)
	}
	delete(s.Players[0], "jaan")
	b, _ = json.Marshal(s)
	if err = os.WriteFile(path, b, 0600); err != nil {
		t.Fatal(err)
	}
	if _, err = Load(path); err == nil {
		t.Fatal("missing original character accepted")
	}
	after, _ = os.ReadFile(path)
	if string(after) != string(b) {
		t.Fatal("bad input overwritten")
	}
}

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
