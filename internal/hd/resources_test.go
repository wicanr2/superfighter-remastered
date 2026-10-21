package hd

import (
	"bytes"
	"os"
	"path/filepath"
	"testing"
)

func TestCPMBoundariesAndCompleteConsumption(t *testing.T) {
	good := []byte{2, 0, 2, 0, 0, 255, 255, 4, 7}
	w, h, pixels, _, err := DecodeCPM(good, 2, 2)
	if err != nil || w != 2 || h != 2 || !bytes.Equal(pixels, []byte{7, 7, 7, 7}) {
		t.Fatal(w, h, pixels, err)
	}
	for _, bad := range [][]byte{good[:8], {2, 0, 2, 0, 0, 255, 255, 0, 7}, {2, 0, 2, 0, 0, 255, 255, 5, 7}, append(append([]byte(nil), good...), 8), {3, 0, 2, 0, 0, 255, 1, 2, 3, 4, 5, 6}, {2, 0, 2, 0, 2, 255, 1, 2, 3, 4}} {
		if _, _, _, _, err := DecodeCPM(bad, 2, 2); err == nil {
			t.Fatalf("accepted malformed image %v", bad)
		}
	}
}

func TestArtPathsAndSymlinksAreRejected(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "art"), []byte("local"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(filepath.Join(dir, "art"), filepath.Join(dir, "link")); err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{"../art", "./art", "/art", "a/../../art", "link", "a\\art", "a:art"} {
		if _, err := ReadArt(dir, name, "", 1024); err == nil {
			t.Fatal("unsafe path accepted", name)
		}
	}
	if _, err := ReadArt(dir, "art", "", 1024); err != nil {
		t.Fatal(err)
	}
}
