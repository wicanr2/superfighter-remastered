package oracle

import (
	"fmt"

	"github.com/wicanr2/dosgolem/internal/machine"
)

// MemoryWrite is a byte write to ordinary RAM, including an unchanged value.
// Address is physical linear; Writer is the runtime instruction start, not IDA.
type MemoryWrite struct {
	Address    uint32
	Old, Value uint8
	Writer     Addr
}

// ObserveWrites observes all ordinary RAM writes in inclusive [lo, hi].
// It does not cover planar VGA memory. The callback shares Run's thread and
// must not run or mutate the machine, or change watches from inside itself.
// Cancel outside callbacks; the returned cancellation function is idempotent.
// Existing OnWrite keeps its separate changed-value-only contract.
func (o *Oracle) ObserveWrites(lo, hi uint32, on func(MemoryWrite)) (func(), error) {
	if lo > hi || hi >= machine.MemSize || on == nil {
		return nil, fmt.Errorf("invalid ordinary RAM write observation")
	}
	id := o.m.WatchWrite(lo, hi, func(m *machine.Machine, address uint32, old, value uint8) {
		cs, ip := m.CPU.OpAddr()
		on(MemoryWrite{Address: address, Old: old, Value: value, Writer: Addr{Seg: cs, Off: ip}})
	})
	active := true
	return func() {
		if active {
			o.m.Unwatch(id)
			active = false
		}
	}, nil
}
