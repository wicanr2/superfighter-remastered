//go:build !windows

package desktop

import "github.com/hajimehoshi/ebiten/v2"

func keyboardPressed(key ebiten.Key) bool { return ebiten.IsKeyPressed(key) }
