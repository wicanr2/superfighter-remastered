package gamecore

import (
	"bytes"
	"os"
	"testing"
)

func TestOriginalSpriteTableBanks(t *testing.T) {
	root := os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" {
		t.Skip("local original sources not supplied")
	}
	sources := loadSpriteSourceTables(root)
	for _, character := range []int{0, 4} {
		s := sources[character]
		if len(s.normal) != 0x120 || len(s.victory) != 0x120 || bytes.Equal(s.normal, s.victory) {
			t.Fatal("source tables incomplete or ambiguous")
		}
		if classifySpriteTable(s.normal, s) != "" || classifySpriteTable(s.victory, s) != "victory" {
			t.Fatal("original source bank not recognized")
		}
		bad := append([]byte(nil), s.victory...)
		bad[0] ^= 1
		if classifySpriteTable(bad, s) != "unknown" || classifySpriteTable(nil, s) != "unknown" {
			t.Fatal("unknown table guessed")
		}
		if classifySpriteTable(s.normal, spriteSourceTables{normal: s.normal, victory: s.normal}) != "unknown" {
			t.Fatal("ambiguous table guessed")
		}
	}
}
