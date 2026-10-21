// 只讀原版音訊路徑探針；不寫原記憶體或改音效卡以外的執行設定。
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/wicanr2/dosgolem/oracle"
	"os"
	"path/filepath"
)

func main() {
	root := flag.String("root", "/project/workplace/orig", "original data")
	output := flag.String("output", "", "new local output directory")
	adlib := flag.Bool("adlib", false, "emulate existing OPL2 device")
	flag.Parse()
	if *output == "" {
		panic("output required")
	}
	if e := os.Mkdir(*output, 0755); e != nil {
		panic(e)
	}
	o, e := oracle.LoadProgram(filepath.Join(*root, "NOKEY.EXE"), *root, " /y")
	if e != nil {
		panic(e)
	}
	defer o.Close()
	o.SetScratch(*output)
	o.Enqueue("SF.COM", "")
	o.AdLib(*adlib)
	o.SetClock(0, 0, 0, 0)
	audio := o.NewAudio(22050)
	cues := []map[string]any{}
	for _, ip := range []uint16{0x82cf, 0x8318, 0x8381, 0x981e, 0x9873} {
		ip := ip
		o.OnCall(oracle.Far(0x01b9, ip), func(o *oracle.Oracle) {
			r := o.Regs()
			var seg, off uint16
			if ip == 0x82cf || ip == 0x8318 {
				off = o.Word(oracle.Far(r.SS, r.SP+4))
				seg = o.Word(oracle.Far(r.SS, r.SP+6))
			}
			if ip == 0x981e {
				bank := (r.AX >> 5) & 6
				seg = o.Word(oracle.Far(r.CS, 0x1580+bank))
				off = o.Word(oracle.Far(seg, (r.AX&63)*2))
			}
			if ip == 0x9873 {
				seg = r.ES
				off = r.DI
			}
			header := o.Bytes(oracle.Far(seg, off), 40)
			cues = append(cues, map[string]any{"runtime_linear_offset_from_01b9": fmt.Sprintf("%04x", ip), "steps": o.Steps(), "regs": r, "pointer": []uint16{seg, off}, "header": fmt.Sprintf("%x", header), "header_sha256": fmt.Sprintf("%x", sha256.Sum256(header))})
		})
	}
	var nonzero, samples, opl int
	stages := []map[string]any{}
	run := func(n uint64) {
		for left := n; left > 0; {
			piece := min(left, 250000)
			if e := o.Run(piece); e != nil {
				panic(e)
			}
			left -= piece
			opl += len(o.OPLWrites())
			pcm := audio.Render()
			samples += len(pcm)
			for _, v := range pcm {
				if v != 0 {
					nonzero++
				}
			}
		}
	}
	capture := func(name string) {
		stages = append(stages, map[string]any{"name": name, "steps": o.Steps(), "samples": samples, "nonzero": nonzero, "opl_writes": opl, "regs": o.Regs()})
	}
	run(40000000)
	capture("title")
	if e := o.MoveMouse(120, 181); e != nil {
		panic(e)
	}
	o.PressButton(0)
	run(1250000)
	o.ReleaseButton(0)
	run(24000000)
	capture("selection")
	_ = o.SendKeys("Return")
	run(20000000)
	_ = o.SendKeys("Right")
	run(2000000)
	_ = o.SendKeys("Return")
	run(100000000)
	capture("battle")
	o.KeyDown(0x20)
	run(20000000)
	o.KeyUp(0x20)
	o.KeyDown(0x0f)
	run(30000000)
	o.KeyUp(0x0f)
	capture("punch")
	ops := []oracle.FileOp{}
	for _, f := range o.FileOps() {
		if filepath.Ext(f.Name) == ".MUS" || filepath.Ext(f.Name) == ".PPM" || filepath.Ext(f.Name) == ".mus" || filepath.Ext(f.Name) == ".ppm" {
			ops = append(ops, f)
		}
	}
	counts := map[string]int{}
	for _, w := range o.PortWrites() {
		if w.Port < 0x300 || w.Port == 0x388 || w.Port == 0x389 {
			counts[fmt.Sprintf("%04x", w.Port)]++
		}
	}
	b, _ := json.MarshalIndent(map[string]any{"adlib": *adlib, "stages": stages, "cues": cues, "audio_file_ops": ops, "remaining_port_counts": counts}, "", "  ")
	if e := os.WriteFile(filepath.Join(*output, "receipt.json"), b, 0644); e != nil {
		panic(e)
	}
	fmt.Println("audio probe complete", *output, "cues", len(cues), "OPL", opl, "nonzero", nonzero)
}
