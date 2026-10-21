package originalaudio

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func TestRealOriginalAudioBankAndAtomicImport(t *testing.T) {
	root, original := os.Getenv("KDZZ_ORIGINAL_AUDIO"), os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" || original == "" {
		t.Skip("private original audio not supplied")
	}
	bank, e := Load(root, original)
	if e != nil {
		t.Fatal(e)
	}
	if len(bank.Manifest.Clips) != 55 || len(bank.Clips) != 54 {
		t.Fatal("wrong original source/alias count")
	}
	output := filepath.Join(t.TempDir(), "imported")
	if e = Import(root, original, output); e != nil {
		t.Fatal(e)
	}
	if _, e = Load(output, original); e != nil {
		t.Fatal(e)
	}
	if e = Import(root, original, output); e == nil {
		t.Fatal("existing audio was overwritten")
	}
	file := filepath.Join(output, bank.Manifest.Clips[len(bank.Manifest.Clips)-1].File)
	data, e := os.ReadFile(file)
	if e != nil {
		t.Fatal(e)
	}
	data[len(data)-1] ^= 1
	if e = os.WriteFile(file, data, 0600); e != nil {
		t.Fatal(e)
	}
	if got, e := Load(output, original); got != nil || e == nil {
		t.Fatal("partially corrupt bank accepted")
	}
	// Complete hashes cannot make an unknown cue valid.
	manifest := bank.Manifest
	manifest.Clips[0].ID = "unknown"
	bytes, e := json.Marshal(manifest)
	if e != nil {
		t.Fatal(e)
	}
	if e = os.WriteFile(filepath.Join(output, "manifest.json"), bytes, 0600); e != nil {
		t.Fatal(e)
	}
	if got, e := Load(output, original); got != nil || e == nil {
		t.Fatal("unknown original cue accepted")
	}
}
