package desktop

import (
	"encoding/json"
	"os"
	"reflect"
	"testing"
)

func TestResultReferencesAgainstIndependentOriginalReconstruction(t *testing.T) {
	root, path := os.Getenv("KDZZ_BATCH_ORIGINAL"), os.Getenv("KDZZ_RESULT_REFERENCE")
	if root == "" || path == "" {
		t.Skip("private source oracle not supplied")
	}
	actual, err := buildResultReferences(root)
	if err != nil {
		t.Fatal(err)
	}
	b, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var expected resultReferences
	if err := json.Unmarshal(b, &expected); err != nil {
		t.Fatal(err)
	}
	colours := func(values [][3]byte) map[[3]byte]bool {
		out := map[[3]byte]bool{}
		for _, v := range values {
			out[v] = true
		}
		return out
	}
	if !reflect.DeepEqual(colours(actual.Continue.Colours), colours(expected.Continue.Colours)) {
		t.Fatal("original highlight table differs")
	}
	actual.Continue.Colours, expected.Continue.Colours = nil, nil
	if !reflect.DeepEqual(actual, expected) {
		t.Fatal("original result, portrait, flag, name or continuation reconstruction differs from independently verified oracle")
	}
}
