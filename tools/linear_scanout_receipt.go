// 正常原版輸入驗候選顯示 API；使用研究目錄的 GOWORK，不改正式執行器。
package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"reflect"

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
	encode := func(v any) []byte { b, e := json.MarshalIndent(v, "", "  "); must(e); return append(b, '\n') }
	writeJSON := func(name string, v any) { write(name, encode(v)) }
	baselinePath := "/project/workplace/display-ports-v1/receipt.json"
	baseline, e := os.ReadFile(baselinePath)
	must(e)
	var previous struct {
		Frames []map[string]any `json:"frames"`
	}
	must(json.Unmarshal(baseline, &previous))
	script, e := os.ReadFile("/project/tools/linear_scanout_receipt.go")
	must(e)
	write("linear_scanout_receipt.go", script)
	candidate, e := os.ReadFile("/project/workplace/display-runtime-study-v1/candidate-manifest.json")
	must(e)
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
		rows, stage, half := o.Byte(oracle.Far(ds, 0x1334)), word(0x131a), word(0x131c)
		key := fmt.Sprintf("%d-%d-%d", rows, stage, half)
		if seen[key] {
			return
		}
		seen[key] = true
		index := len(frames)
		stem := fmt.Sprintf("display-%03d", index)
		vram := o.Bytes(oracle.Far(0xa000, 0), 65536)
		legacy := o.Indexed()
		beforeRegs := o.Regs()
		beforeSteps := o.Steps()
		beforePorts := len(o.PortWrites())
		scanout, e := o.LinearScanout()
		must(e)
		if !reflect.DeepEqual(beforeRegs, o.Regs()) || beforeSteps != o.Steps() || beforePorts != len(o.PortWrites()) || !bytes.Equal(vram, o.Bytes(oracle.Far(0xa000, 0), 65536)) || !bytes.Equal(legacy, o.Indexed()) {
			panic("display API changed original state or legacy view")
		}
		record := map[string]any{"fixture": stem, "steps": o.Steps(), "mode": o.VideoMode(), "rows": rows, "round_index": word(0x1318), "round_state_after_draw": stage, "half_width_after_draw": half, "program_crtc_start": word(0x1330), "vram_sha256": digest(vram), "port_writes": len(o.PortWrites())}
		if index >= len(previous.Frames) || !bytes.Equal(encode(record), encode(previous.Frames[index])) {
			panic(fmt.Sprintf("normal original baseline changed at frame %d", index))
		}
		expected, e := os.ReadFile(filepath.Join("/project/workplace/display-ports-v1", stem+".scanout.idx"))
		must(e)
		if !bytes.Equal(scanout.Indices, expected) || scanout.Width != 320 || scanout.Height != 192 || scanout.StartByte != 3840 || scanout.PitchByte != 320 {
			panic("candidate display does not match independent normal reference")
		}
		write(stem+".api.idx", scanout.Indices)
		writeJSON(stem+".api.json", scanout)
		writeJSON(stem+".game.json", map[string]any{"camera_x": word(0x1332), "scene": word(0x1338), "background_sha256": digest(o.Bytes(oracle.Far(word(0xc), 0), 480*204))})
		frames = append(frames, record)
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
	if len(frames) != 67 || len(previous.Frames) != len(frames) {
		panic("incomplete normal display coverage")
	}
	writeJSON("receipt.json", map[string]any{"kind": "candidate scanout API over normal original menu path; not native desktop acceptance", "baseline_receipt_sha256": digest(baseline), "candidate_manifest_sha256": digest(candidate), "script_sha256": digest(script), "frames": frames, "unimplemented": o.Unimplemented(), "legacy_and_original_unchanged": true, "state_control": "normal menu only; API observes registers/memory without writes"})
	fmt.Println("candidate scanout frames", len(frames), "original steps", o.Steps(), "legacy unchanged")
}
