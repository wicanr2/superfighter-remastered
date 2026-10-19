package dos

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/wicanr2/dosgolem/internal/machine"
)

// The child must receive a real IRQ0 and a changing DOS clock without STI.
// This checks the machine-to-DOS wiring, rather than reading a flag we set.
func TestQueuedEntryClockAfterDisabledInterrupts(t *testing.T) {
	for _, resident := range []bool{false, true} {
		name := "normal_exit"
		parent := []byte{0xFA, 0xB8, 0x00, 0x4C, 0xCD, 0x21}
		if resident {
			name = "resident_exit"
			parent = []byte{0xFA, 0xBA, 0x40, 0x00, 0xB8, 0x00, 0x31, 0xCD, 0x21}
		}
		t.Run(name, func(t *testing.T) {
			root := t.TempDir()
			child := []byte{
				0xB4, 0x2C, 0xCD, 0x21, // mov ah,2Ch; int 21h
				0x08, 0xD2, 0x74, 0xF8, // or dl,dl; jz start
				0xB8, 0x2A, 0x4C, 0xCD, 0x21, // normal exit 42
			}
			if err := os.WriteFile(filepath.Join(root, "CLOCK.COM"), child, 0o600); err != nil {
				t.Fatal(err)
			}
			m := machine.New()
			if err := m.LoadCOM(parent); err != nil {
				t.Fatal(err)
			}
			d := New(m, root)
			defer d.Close()
			d.Install()
			d.Enqueue("CLOCK.COM", "")
			for i := 0; i < 2_000_000 && !d.Exited; i++ {
				if err := m.Step(); err != nil {
					t.Fatal(err)
				}
			}
			if !d.Exited || d.ExitCode != 42 || m.Ticks == 0 {
				t.Fatalf("clock did not progress: exited=%v code=%d ticks=%d", d.Exited, d.ExitCode, m.Ticks)
			}
		})
	}
}
