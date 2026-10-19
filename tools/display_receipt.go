// 正常選單輸入的 VGA 顯示參數與完整 64 KiB 線性視訊記憶體探針。
package main

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	"github.com/wicanr2/dosgolem/oracle"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func main() {
	out := flag.String("out", "", "new output directory")
	flag.Parse()
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	write := func(name string, b []byte) { must(os.WriteFile(filepath.Join(*out, name), b, 0644)) }
	writeJSON := func(name string, v any) {
		b, e := json.MarshalIndent(v, "", "  ")
		must(e)
		write(name, append(b, '\n'))
	}
	script, e := os.ReadFile("/project/tools/display_receipt.go")
	must(e)
	write("display_receipt.go", script)
	exe, e := os.ReadFile("/orig/SF.EXE")
	must(e)
	if digest(exe) != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("wrong original")
	}
	o, e := oracle.LoadProgram("/orig/NOKEY.EXE", "/orig", " /y")
	must(e)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	o.Enqueue("SF.COM", "")
	var frames []map[string]any
	seen := map[string]bool{}
	o.OnCall(oracle.Far(0x1b9, 0x3e9d), func(o *oracle.Oracle) {
		if o.Word(oracle.Far(0, 0x24)) != 0x524c || o.Word(oracle.Far(0, 0x26)) != 0x1b9 {
			return
		}
		isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
		ds := binary.LittleEndian.Uint16(isr[6:8])
		word := func(off uint16) uint16 { return o.Word(oracle.Far(ds, off)) }
		rows := o.Byte(oracle.Far(ds, 0x1334))
		stage := word(0x131a)
		half := word(0x131c)
		key := fmt.Sprintf("%d-%d-%d", rows, stage, half)
		if seen[key] {
			return
		}
		seen[key] = true
		stem := fmt.Sprintf("display-%03d", len(frames))
		vram := o.Bytes(oracle.Far(0xa000, 0), 65536)
		write(stem+".vram", vram)
		write(stem+".legacy.idx", o.Indexed())
		writeJSON(stem+".palette.json", o.Palette())
		frames = append(frames, map[string]any{"fixture": stem, "steps": o.Steps(), "mode": o.VideoMode(), "rows": rows, "round_index": word(0x1318), "round_state_after_draw": stage, "half_width_after_draw": half, "program_crtc_start": word(0x1330), "vram_sha256": digest(vram), "port_writes": len(o.PortWrites())})
	})
	must(o.Run(40_000_000))
	must(o.MoveMouse(125, 181))
	o.PressButton(0)
	must(o.Run(1_000_000))
	o.ReleaseButton(0)
	must(o.Run(24_000_000))
	must(o.SendKeys("Return"))
	must(o.Run(20_000_000))
	for i := 0; i < 4; i++ {
		must(o.SendKeys("Right"))
		must(o.Run(1_000_000))
	}
	must(o.SendKeys("Return"))
	must(o.Run(75_000_000))
	writeJSON("ports.json", o.PortWrites())
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	writeJSON("receipt.json", map[string]any{"kind": "normal original VGA register writes and raw VRAM; no display correction", "input_sha256": digest(exe), "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(manifest), "frames": frames, "unimplemented": o.Unimplemented(), "state_control": "normal menu and keyboard only; no register or memory injection"})
	fmt.Println("frames", len(frames), "ports", len(o.PortWrites()), "steps", o.Steps())
}
