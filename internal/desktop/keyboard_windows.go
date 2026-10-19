package desktop

import (
	"syscall"

	"github.com/hajimehoshi/ebiten/v2"
)

var getAsyncKeyState = syscall.NewLazyDLL("user32.dll").NewProc("GetAsyncKeyState")

// GLFW 的 Shift-up 處理會一併釋放兩鍵；用個別 VK 保留另一玩家的按住狀態。
// 呼叫端先檢查視窗焦點，並沿用暫停、設定及重新啟用閘門。
func keyboardPressed(key ebiten.Key) bool {
	var vk uintptr
	switch key {
	case ebiten.KeyShiftLeft:
		vk = 0xa0
	case ebiten.KeyShiftRight:
		vk = 0xa1
	default:
		return ebiten.IsKeyPressed(key)
	}
	state, _, _ := getAsyncKeyState.Call(vk)
	return state&0x8000 != 0
}
