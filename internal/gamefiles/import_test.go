package gamefiles

import (
	"archive/zip"
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/superfighter-remastered/internal/hd"
)

func TestImportRejectsUnsafeZipAndOverwrite(t *testing.T) {
	for _, name := range []string{"../SF.EXE", "/SF.EXE", "C:/SF.EXE", "safe/../../SF.EXE"} {
		t.Run(name, func(t *testing.T) {
			root := t.TempDir()
			archive := filepath.Join(root, "input.zip")
			f, err := os.Create(archive)
			if err != nil {
				t.Fatal(err)
			}
			w := zip.NewWriter(f)
			entry, err := w.Create(name)
			if err != nil {
				t.Fatal(err)
			}
			entry.Write([]byte("bad"))
			w.Close()
			f.Close()
			dest := filepath.Join(root, "game-data")
			if Import(archive, dest) == nil {
				t.Fatal("unsafe ZIP accepted")
			}
			if _, err := os.Stat(dest); !os.IsNotExist(err) {
				t.Fatal("rejected ZIP created output")
			}
		})
	}
	root := t.TempDir()
	if Import("missing.zip", root) == nil {
		t.Fatal("existing target not protected")
	}
}

func TestLegalSourceImportAndBackground(t *testing.T) {
	source := os.Getenv("KDZZ_ORIGINAL_ROOT")
	project := os.Getenv("KDZZ_PROJECT_ROOT")
	if source == "" || project == "" {
		t.Skip("local legal sources not supplied")
	}
	root := t.TempDir()
	dest := filepath.Join(root, "game-data")
	if err := Import(source, dest); err != nil {
		t.Fatal(err)
	}
	if Import(source, dest) == nil {
		t.Fatal("existing imported data overwritten")
	}
	background := filepath.Join(root, "background")
	if err := EnsureBackground(dest, filepath.Join(project, "assets/hd/backgrounds/rooftop.png"), background); err != nil {
		t.Fatal(err)
	}
	assets, err := hd.Load(background)
	if err != nil {
		t.Fatal(err)
	}
	if len(assets.Reference) != 480*204 || assets.Manifest.ReferenceSHA256 != hd.ReferenceSHA256 {
		t.Fatal("wrong original source")
	}
}
