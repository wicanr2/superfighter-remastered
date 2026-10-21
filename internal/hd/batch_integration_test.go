package hd_test

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/gamefiles"
	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

func TestRealElevenSceneCollectionAndAtomicFailure(t *testing.T) {
	root, art := os.Getenv("KDZZ_BATCH_ORIGINAL"), os.Getenv("KDZZ_BATCH_ART")
	if root == "" || art == "" {
		t.Skip("private originals and project art not supplied")
	}
	output := filepath.Join(t.TempDir(), "collection")
	if err := gamefiles.EnsureBackgroundCollection(root, art, output); err != nil {
		t.Fatal(err)
	}
	a, err := hd.Load(output)
	if err != nil {
		t.Fatal(err)
	}
	for scene := 0; scene < 11; scene++ {
		b := a.ForScene(scene)
		if b == nil || b.Manifest.Scene != scene || len(b.Reference) != 480*204 || b.Image == nil {
			t.Fatal("missing real scene", scene)
		}
	}
	if a.ForScene(-1) != nil || a.ForScene(11) != nil {
		t.Fatal("unknown scene accepted")
	}
	path := filepath.Join(output, "scene-00", "reference.idx")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	data[0] ^= 1
	if err := os.WriteFile(path, data, 0600); err != nil {
		t.Fatal(err)
	}
	if _, err := hd.Load(output); err == nil {
		t.Fatal("partially corrupt collection accepted")
	}
	images, err := hd.LoadScreens(art)
	if err != nil || len(images) != 33 {
		t.Fatal("screen group", len(images), err)
	}
}

func TestRealCompleteSpiderCharacterPack(t *testing.T) {
	root, art := os.Getenv("KDZZ_BATCH_ORIGINAL"), os.Getenv("KDZZ_BATCH_ART")
	if root == "" || art == "" {
		t.Skip("private originals and project art not supplied")
	}
	characters, err := hd.LoadCharacters(filepath.Join(art, "characters"), root)
	if err != nil {
		t.Fatal(err)
	}
	if len(characters.Manifest.Poses) != 1630 || len(characters.Manifest.Sources) != 22 || len(characters.Manifest.Atlases) != 78 {
		t.Fatal("complete Spider pack rejected or changed")
	}
	counts := map[string]int{}
	for _, pose := range characters.Manifest.Poses {
		if pose.Character == 8 {
			if pose.Atlas == "spider-low-guard.png" {
				t.Fatal("mixed old costume")
			}
			bank := pose.SourceBank
			if bank == "" {
				bank = "normal"
			}
			counts[bank]++
		}
	}
	if counts["normal"] != 72 || counts["victory"] != 72 {
		t.Fatal("missing original aliases", counts)
	}
	bad := t.TempDir()
	if err := os.WriteFile(filepath.Join(bad, "manifest.json"), make([]byte, (1<<20)+1), 0600); err != nil {
		t.Fatal(err)
	}
	if a, err := hd.LoadCharacters(bad, root); a != nil || err == nil {
		t.Fatal("unbounded manifest accepted")
	}
}
