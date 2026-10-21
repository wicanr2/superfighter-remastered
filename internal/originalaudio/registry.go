// Package originalaudio contains source identities, never original audio bytes.
package originalaudio

import (
	"crypto/sha256"
	_ "embed"
	"encoding/json"
	"fmt"
)

//go:embed sources.json
var sourceRegistry []byte

type Source struct {
	File   string `json:"file"`
	SHA256 string `json:"sha256"`
}
type SourceClip struct {
	ID     string `json:"id"`
	Kind   string `json:"kind"`
	File   string `json:"file"`
	Offset int    `json:"offset"`
	Bytes  int    `json:"bytes"`
	SHA256 string `json:"sha256"`
}
type Registry struct {
	Version int          `json:"version"`
	Sources []Source     `json:"sources"`
	Clips   []SourceClip `json:"clips"`
}

func Sources() Registry {
	var r Registry
	if e := json.Unmarshal(sourceRegistry, &r); e != nil {
		panic(e)
	}
	return r
}
func RegistrySHA256() string { return fmt.Sprintf("%x", sha256.Sum256(sourceRegistry)) }
