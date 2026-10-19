//go:build windows

// Read-only Win32 key-state probe, separate from the desktop player.
package main

import (
	"encoding/json"
	"os"
	"syscall"
	"time"
)

func main() {
	get := syscall.NewLazyDLL("user32.dll").NewProc("GetAsyncKeyState")
	for start := time.Now(); time.Since(start) < 40*time.Second; time.Sleep(20 * time.Millisecond) {
		left, _, _ := get.Call(0xa0)
		right, _, _ := get.Call(0xa1)
		b, _ := json.Marshal([2]bool{left&0x8000 != 0, right&0x8000 != 0})
		if e := os.WriteFile(os.Args[1]+".tmp", b, 0600); e != nil {
			panic(e)
		}
		if e := os.Rename(os.Args[1]+".tmp", os.Args[1]); e != nil {
			panic(e)
		}
	}
}
