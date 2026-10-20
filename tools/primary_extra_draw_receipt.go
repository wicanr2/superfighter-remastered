// Disposable normal all-blit pointer/palette probe; default Onimaru, no state writes.
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

	"github.com/wicanr2/dosgolem/oracle"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}
func digest(b []byte) string { return fmt.Sprintf("%x", sha256.Sum256(b)) }
func writeJSON(path string, value any) {
	b, e := json.MarshalIndent(value, "", "  ")
	must(e)
	must(os.WriteFile(path, append(b, '\n'), 0644))
}

type Source struct {
	Player       int    `json:"player"`
	Character    int    `json:"character"`
	Slot         int    `json:"slot"`
	Offset       int    `json:"file_offset"`
	Matches      bool   `json:"bytes_match_source"`
	TableSegment uint16 `json:"table_segment"`
	TableOffset  uint16 `json:"table_offset"`
	BaseSegment  uint16 `json:"base_segment"`
}
type Blit struct {
	Phase             string       `json:"phase"`
	Steps             uint64       `json:"steps"`
	IP                uint16       `json:"runtime_entry_ip"`
	Return            uint16       `json:"runtime_return_ip"`
	SP                uint16       `json:"entry_sp"`
	DS                uint16       `json:"source_ds"`
	SI                uint16       `json:"source_si"`
	ES                uint16       `json:"destination_es"`
	DI                uint16       `json:"destination_di"`
	Width             int          `json:"width"`
	Height            int          `json:"height"`
	Flags             uint8        `json:"flags"`
	Palette           uint8        `json:"palette_base"`
	Top               int          `json:"top_clip"`
	Left              int          `json:"left_clip"`
	Right             int          `json:"right_clip"`
	Role              string       `json:"role"`
	Sources           []Source     `json:"sources"`
	SHA               string       `json:"source_sha256"`
	Colors            [16][3]uint8 `json:"runtime_colors"`
	Differences       int          `json:"pixel_differences"`
	MaskDifferences   int          `json:"mask_differences"`
	Fixture           string       `json:"fixture,omitempty"`
	raw, before, mask []byte
}
type Layer struct {
	Kind         string `json:"kind"`
	Draw         *Blit  `json:"draw,omitempty"`
	Pixels, Mask []byte `json:"-"`
}

func raster(kind string) *Layer {
	return &Layer{Kind: kind, Pixels: make([]byte, 64000), Mask: make([]byte, 64000)}
}
func predict(b *Blit, base uint32) ([]byte, []byte) {
	out, mask := append([]byte(nil), b.before...), make([]byte, 64000)
	stride := (b.Width + 1) / 2
	rows := b.Height - b.Top
	left, right := (b.Left+1)/2, (b.Right+1)/2
	pairs := stride - left - right
	if rows <= 0 || pairs <= 0 || pairs >= 128 {
		return out, mask
	}
	flipX, flipY := b.Flags&64 != 0, b.Flags&128 != 0
	di := int(b.DI)
	if flipX {
		di += b.Width - b.Left - b.Right
	}
	if flipY {
		di += rows * 320
	}
	di &= 65535
	for y := 0; y < rows; y++ {
		sourceRow, sourcePair := y+b.Top, left
		if flipY {
			sourceRow = y
		}
		if flipX && !flipY {
			sourcePair = right
		}
		line := int(b.ES)*16 + di + y*320 - int(base)
		if flipY {
			line = int(b.ES)*16 + di - y*320 - int(base)
		}
		for pair := 0; pair < pairs; pair++ {
			packed := b.raw[2+sourceRow*stride+sourcePair+pair]
			for n := 0; n < 2; n++ {
				v := packed >> 4
				if n == 1 {
					v = packed & 15
				}
				at := line + pair*2 + n
				if flipX {
					at = line - pair*2 - n
				}
				if v != 0 && at >= 0 && at < 64000 {
					out[at] = v | b.Palette
					mask[at] = 1
				}
			}
		}
	}
	return out, mask
}
func main() {
	out := flag.String("out", "", "new output directory")
	root := flag.String("root", "/orig", "original root")
	player := flag.Int("player", 0, "input player 0 or 1; the other player is Frank")
	character := flag.Int("character", 5, "normal selected character 0..10")
	chargeBoth := flag.Bool("charge-both", false, "ordinary forward punch and kick after charge; also save secondary-palette main draws")
	same := flag.Bool("same-character", false, "normal same-character selection")
	flag.Parse()
	if *player < 0 || *player > 1 || *character < 0 || *character > 10 {
		panic("invalid player")
	}
	if *out == "" {
		panic("out required")
	}
	if _, e := os.Stat(*out); !os.IsNotExist(e) {
		panic("output exists")
	}
	must(os.MkdirAll(filepath.Join(*out, "scratch"), 0755))
	hashes := map[string]string{}
	files := map[int][]byte{}
	names := []string{"SF.EXE", "SF.COM", "NOKEY.EXE", "MAN.COL"}
	for _, c := range []int{0, 4, *character} {
		if files[c] == nil {
			b, e := os.ReadFile(filepath.Join(*root, fmt.Sprintf("SFMAN%02d.DAT", c+1)))
			must(e)
			files[c] = b
			hashes[fmt.Sprintf("SFMAN%02d.DAT", c+1)] = digest(b)
		}
	}
	for _, n := range names {
		b, e := os.ReadFile(filepath.Join(*root, n))
		must(e)
		hashes[n] = digest(b)
	}
	if hashes["SF.EXE"] != "24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300" {
		panic("wrong original")
	}
	o, e := oracle.LoadProgram(filepath.Join(*root, "NOKEY.EXE"), *root, " /y")
	must(e)
	defer o.Close()
	o.SetScratch(filepath.Join(*out, "scratch"))
	o.Enqueue("SF.COM", "")
	must(o.Run(40_000_000))
	must(o.MoveMouse(125, 181))
	o.PressButton(0)
	must(o.Run(1_000_000))
	o.ReleaseButton(0)
	must(o.Run(24_000_000))
	firstCharacter := *character
	if *player == 1 && !*same {
		firstCharacter = 4
	}
	for i := 0; i < firstCharacter; i++ {
		must(o.SendKeys("Right"))
		must(o.Run(1_000_000))
	}
	must(o.SendKeys("Return"))
	must(o.Run(20_000_000))
	secondCharacter := 4
	if *player == 1 || *same {
		secondCharacter = *character
	}
	secondDirection, moves := "Right", secondCharacter-firstCharacter
	if moves < 0 {
		secondDirection, moves = "Left", -moves
	}
	for i := 0; i < moves; i++ {
		must(o.SendKeys(secondDirection))
		must(o.Run(1_000_000))
	}
	must(o.SendKeys("Return"))
	must(o.Run(75_000_000))
	if o.Word(oracle.Far(0, 0x24)) != 0x524c || o.Word(oracle.Far(0, 0x26)) != 0x1b9 {
		panic("not normal battle")
	}
	isr := o.Bytes(oracle.Far(0x1b9, 0x524c), 10)
	if !bytes.Equal(isr[:6], []byte{0x1e, 0x56, 0x51, 0x50, 0x53, 0xb8}) {
		panic("ISR mismatch")
	}
	ds := binary.LittleEndian.Uint16(isr[6:8])
	selected := [2]int{int(o.Word(oracle.Far(ds, 0x12ac))), int(o.Word(oracle.Far(ds, 0x12ae)))}
	expected := [2]int{*character, 4}
	if *player == 1 {
		expected = [2]int{4, *character}
	}
	if *same {
		expected = [2]int{*character, *character}
	}
	if selected != expected {
		panic("normal character selection mismatch")
	}
	base := uint32(o.Word(oracle.Far(ds, 0xe))) * 16
	var pending *Blit
	var records []*Blit
	var layers []*Layer
	var frames []map[string]any
	var cancel func()
	phase := ""
	registered := map[uint16]bool{}
	fixtures := map[string]bool{}
	frameFixtures := map[string]bool{}
	o.OnCall(oracle.Far(0x1b9, 0x3de4), func(o *oracle.Oracle) {
		if cancel != nil {
			cancel()
		}
		layers = []*Layer{raster("background")}
		var e error
		cancel, e = o.ObserveWrites(base, base+63999, func(event oracle.MemoryWrite) {
			if len(layers) > 0 {
				l := layers[len(layers)-1]
				i := int(event.Address - base)
				l.Pixels[i] = event.Value
				l.Mask[i] = 1
			}
			if pending != nil {
				pending.mask[int(event.Address-base)] = 1
			}
		})
		must(e)
	})
	o.OnCall(oracle.Far(0x1b9, 0x3e08), func(*oracle.Oracle) {
		if len(layers) == 1 {
			layers = append(layers, raster("raster"))
		}
	})
	finish := func(o *oracle.Oracle) {
		b := pending
		if b == nil || o.SP() != b.SP+2 || o.IP().Off != b.Return {
			return
		}
		pending = nil
		after := o.Bytes(oracle.Far(uint16(base/16), 0), 64000)
		expected, mask := predict(b, base)
		for i, v := range after {
			if v != expected[i] {
				b.Differences++
			}
			if mask[i] != b.mask[i] {
				b.MaskDifferences++
			}
		}
		class := fmt.Sprintf("%04x-%s-%02x-%02x-%d-%d-%d", b.Return, b.SHA, b.Palette, b.Flags&192, b.Top, b.Left, b.Right)
		if (b.Role == "effect" || *chargeBoth && b.Role == "body" && b.Palette&16 != 0) && !fixtures[class] && len(fixtures) < 48 {
			fixtures[class] = true
			b.Fixture = fmt.Sprintf("blit-%04d", len(records))
			must(os.WriteFile(filepath.Join(*out, b.Fixture+".before.idx"), b.before, 0644))
			must(os.WriteFile(filepath.Join(*out, b.Fixture+".after.idx"), after, 0644))
			must(os.WriteFile(filepath.Join(*out, b.Fixture+".source.bin"), b.raw, 0644))
			must(os.WriteFile(filepath.Join(*out, b.Fixture+".mask"), b.mask, 0644))
		}
		b.raw = nil
		b.before = nil
		b.mask = nil
		records = append(records, b)
		if len(layers) > 0 {
			layers = append(layers, raster("raster"))
		}
	}
	for _, ip := range []uint16{0x4665, 0x46e8, 0x477e, 0x480a} {
		ip := ip
		o.OnCall(oracle.Far(0x1b9, ip), func(o *oracle.Oracle) {
			if uint32(o.ES())*16 != base || len(layers) == 0 {
				return
			}
			if pending != nil {
				if pending.SP == o.SP() && pending.IP == ip {
					return
				}
				panic("nested blit")
			}
			h := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2)
			w, height := int(h[0]), int(h[1])
			if w == 0 || height == 0 {
				panic("empty source")
			}
			raw := o.Bytes(oracle.Far(o.DSReg(), o.SI()), 2+(w+1)/2*height)
			ret := o.StackWord(0)
			b := &Blit{Phase: phase, Steps: o.Steps(), IP: ip, Return: ret, SP: o.SP(), DS: o.DSReg(), SI: o.SI(), ES: o.ES(), DI: o.DI(), Width: w, Height: height, Flags: uint8(o.CX()), Palette: uint8(o.DX() >> 8), Top: int(o.DX() & 255), Left: int(o.BX() & 255), Right: int(o.BX() >> 8), Role: "unknown", SHA: digest(raw), raw: raw, before: o.Bytes(oracle.Far(uint16(base/16), 0), 64000), mask: make([]byte, 64000)}
			pal := o.Palette()
			for i := 0; i < 16; i++ {
				b.Colors[i] = pal[int(b.Palette)+i]
			}
			for p := 0; p < 2; p++ {
				character := int(o.Word(oracle.Far(ds, uint16(0x12ac+p*2))))
				data := files[character]
				if data == nil {
					continue
				}
				for slot := 0; slot < 72; slot++ {
					table := uint16(0x1706 + p*0x120 + slot*4)
					seg := o.Word(oracle.Far(ds, table)) + o.Word(oracle.Far(ds, uint16(0x132a+p*2)))
					off := o.Word(oracle.Far(ds, table+2))
					if oracle.Far(seg, off).Linear() != oracle.Far(b.DS, b.SI).Linear() {
						continue
					}
					ptr := 0xb28 + slot*4
					at := 0xc48 + int(binary.LittleEndian.Uint16(data[ptr:]))*16 + int(binary.LittleEndian.Uint16(data[ptr+2:]))
					match := at+len(raw) <= len(data) && bytes.Equal(raw, data[at:at+len(raw)])
					b.Sources = append(b.Sources, Source{Player: p, Character: character, Slot: slot, Offset: at, Matches: match, TableSegment: o.Word(oracle.Far(ds, table)), TableOffset: off, BaseSegment: o.Word(oracle.Far(ds, uint16(0x132a+p*2)))})
				}
			}
			switch ret {
			case 0x428e, 0x4294, 0x429f, 0x42a5, 0x442f, 0x4435, 0x4440, 0x4446:
				b.Role = "body"
			default:
				if len(b.Sources) > 0 {
					b.Role = "effect"
				}
			}
			pending = b
			l := raster(b.Role)
			l.Draw = b
			layers = append(layers, l)
			if !registered[ret] {
				registered[ret] = true
				o.OnCall(oracle.Far(0x1b9, ret), finish)
			}
		})
	}
	o.OnCall(oracle.Far(0x1b9, 0x3e9d), func(o *oracle.Oracle) {
		if len(layers) == 0 {
			return
		}
		if pending != nil {
			panic("unfinished blit")
		}
		if cancel != nil {
			cancel()
			cancel = nil
		}
		replay := make([]byte, 64000)
		coverage := 0
		class := ""
		for _, v := range layers[0].Mask {
			if v != 0 {
				coverage++
			}
		}
		for _, l := range layers {
			for i, v := range l.Mask {
				if v != 0 {
					replay[i] = l.Pixels[i]
				}
			}
			if l.Draw != nil && (l.Draw.Role == "effect" || *chargeBoth && l.Draw.Role == "body" && l.Draw.Palette&16 != 0) {
				class += fmt.Sprintf("-%04x-%02x-%s", l.Draw.Return, l.Draw.Palette, l.Draw.SHA[:8])
			}
		}
		actual := o.Indexed()
		different := 0
		for i, v := range actual {
			if replay[i] != v {
				different++
			}
		}
		frame := map[string]any{"steps": o.Steps(), "counter": o.Word(oracle.Far(ds, 0x1a)), "phase": phase, "camera_x": o.Word(oracle.Far(ds, 0x1332)), "coverage": coverage, "differences": different, "layers": len(layers), "effect_class": class, "matched": different == 0 && coverage == 64000}
		if class != "" && !frameFixtures[class] && len(frameFixtures) < 24 {
			frameFixtures[class] = true
			stem := fmt.Sprintf("frame-%04d", len(frames))
			frame["fixture"] = stem
			must(os.WriteFile(filepath.Join(*out, stem+".idx"), actual, 0644))
			must(o.WritePNG(filepath.Join(*out, stem+".png")))
			writeJSON(filepath.Join(*out, stem+".palette.json"), o.Palette())
			writeJSON(filepath.Join(*out, stem+".layers.json"), layers)
			for i, l := range layers {
				prefix := filepath.Join(*out, fmt.Sprintf("%s.layer-%02d", stem, i))
				must(os.WriteFile(prefix+".idx", l.Pixels, 0644))
				must(os.WriteFile(prefix+".mask", l.Mask, 0644))
			}
		}
		frames = append(frames, frame)
		layers = nil
	})
	var phases []map[string]any
	type inputPhase struct {
		name   string
		keys   []uint8
		frames int
	}

	inputs := []inputPhase{
		{"idle", nil, 12}, {"punch-kick", []uint8{0x0f, 0x2a}, 2}, {"release-pk", nil, 70},
		{"charge-back", []uint8{0x1e}, 24}, {"forward-punch", []uint8{0x20, 0x0f}, 2}, {"release-charge", nil, 90},
	}
	if *player == 1 {
		inputs = []inputPhase{{"idle", nil, 12}, {"punch-kick", []uint8{0x1c, 0x36}, 2}, {"release-pk", nil, 70}, {"charge-back", []uint8{0x4d}, 24}, {"forward-punch", []uint8{0x4b, 0x1c}, 2}, {"release-charge", nil, 90}}
	}
	if *chargeBoth {
		kick := uint8(0x2a)
		if *player == 1 {
			kick = 0x36
		}
		inputs[4].keys = append(inputs[4].keys, kick)
		inputs[4].name = "forward-punch-kick"
	}

	for _, p := range inputs {
		phase = p.name
		for _, k := range o.HeldKeys() {
			o.KeyUp(k)
		}
		for _, k := range p.keys {
			o.KeyDown(k)
		}
		start := len(records)
		counter := o.Word(oracle.Far(ds, 0x1a))
		for i := 0; i < p.frames; i++ {
			for {
				if o.Steps() > 800_000_000 {
					panic("instruction budget")
				}
				must(o.Run(1))
				must(o.RunUntil(oracle.At(oracle.Far(0x1b9, 0x5dd3)), oracle.Budget(5_000_000)))
				v := o.Word(oracle.Far(ds, 0x1a))
				if v != counter {
					counter = v
					break
				}
			}
		}
		phases = append(phases, map[string]any{"name": p.name, "keys": p.keys, "frames": p.frames, "blits": len(records) - start, "paths": []uint8{o.Byte(oracle.Far(ds, 0x16ea)), o.Byte(oracle.Far(ds, 0x16eb))}, "facing": []uint8{o.Byte(oracle.Far(ds, 0x16b4)), o.Byte(oracle.Far(ds, 0x16b5))}})
		fmt.Println(p.name, len(records)-start)
	}
	if cancel != nil {
		cancel()
	}
	script, e := os.ReadFile("/project/tools/primary_extra_draw_receipt.go")
	must(e)
	must(os.WriteFile(filepath.Join(*out, "primary_extra_draw_receipt.go"), script, 0644))
	manifest, e := os.ReadFile("/project/workplace/dosgolem-patched-manifest.json")
	must(e)
	writeJSON(filepath.Join(*out, "receipt.json"), map[string]any{"kind": "normal all-blit/source/palette oracle experiment; not production HD or exact prior-Core-state replay", "address_space": "runtime 01B9:IP; DS-relative tables; source file offsets separately labeled", "inputs": hashes, "script_sha256": digest(script), "dosgolem_manifest_sha256": digest(manifest), "phases": phases, "records": records, "frames": frames, "unimplemented": o.Unimplemented(), "player": *player, "character": *character, "charge_both": *chargeBoth, "same_character": *same, "selected": selected, "game_data_segment": ds, "composition_buffer_segment": uint16(base / 16), "state_control": "normal menu selection and declared keyboard inputs only; independent oracle uses original completed-frame counters, not exact prior Core poll timing; no state/RNG injection"})
	fmt.Println("blits", len(records), "frames", len(frames), "saved blit fixtures", len(fixtures))
}
