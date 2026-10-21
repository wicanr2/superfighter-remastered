package gamecore

import (
	"bytes"
	"os"
	"testing"

	"github.com/wicanr2/dosgolem/oracle"
)

func TestOriginalAudioCuesDoNotChangeMachine(t *testing.T) {
	root := os.Getenv("KDZZ_ORIGINAL_ROOT")
	if root == "" {
		t.Skip("private original data required")
	}
	a, e := New(root, t.TempDir())
	if e != nil {
		t.Fatal(e)
	}
	defer a.Close()
	b, e := New(root, t.TempDir())
	if e != nil {
		t.Fatal(e)
	}
	defer b.Close()
	a.o.SetClock(0, 0, 0, 0)
	b.o.SetClock(0, 0, 0, 0)
	a.EnableAudio()
	a.Pause(false)
	b.Pause(false)
	cues := []AudioCue{}
	advance := func(n uint64) {
		t.Helper()
		for left := n; left > 0; {
			piece := min(left, 1000000)
			left -= piece
			if e := a.Step(piece); e != nil {
				t.Fatal(e)
			}
			if e := b.Step(piece); e != nil {
				t.Fatal(e)
			}
			if a.o.Regs() != b.o.Regs() || !bytes.Equal(a.o.Bytes(oracle.Far(0, 0), 1<<20), b.o.Bytes(oracle.Far(0, 0), 1<<20)) || a.o.Steps() != b.o.Steps() {
				t.Fatal("audio observation changed original machine", a.o.Steps())
			}
			cues = append(cues, a.DrainAudio()...)
		}
	}
	advance(40000000)
	for _, c := range []*Core{a, b} {
		if e := c.Mouse(120, 181, true); e != nil {
			t.Fatal(e)
		}
	}
	advance(1250000)
	for _, c := range []*Core{a, b} {
		_ = c.Mouse(0, 0, false)
	}
	advance(24000000)
	for _, c := range []*Core{a, b} {
		_ = c.MenuKey("Return")
	}
	advance(20000000)
	for _, c := range []*Core{a, b} {
		_ = c.MenuKey("Right")
	}
	advance(2000000)
	for _, c := range []*Core{a, b} {
		_ = c.MenuKey("Return")
	}
	advance(100000000)
	music, voice := 0, 0
	last := ""
	for _, cue := range cues {
		if cue.Kind == "music" {
			music++
			last = "music"
		}
		if cue.Kind == "voice" {
			voice++
		}
		if cue.Kind == "stop-music" {
			last = "stop"
		}
	}
	if music != 3 || voice < 3 || last != "music" || a.RejectedAudio() != 0 {
		t.Fatal("normal original cues", music, voice, last, a.RejectedAudio())
	}
	if len(b.DrainAudio()) != 0 {
		t.Fatal("disabled audio emitted requests")
	}
	t.Logf("same fixed test clock, 188 paired machine checkpoints; %d music and %d voice cues", music, voice)
}
