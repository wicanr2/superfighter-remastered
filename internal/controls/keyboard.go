package controls

import "fmt"

var KeyboardActions = [14]string{"左上", "上", "右上", "左", "右", "左下", "下", "右下", "拳", "腳", "快捷 1", "快捷 2", "快捷 3", "快捷 4"}

var KeyboardScans = [2][10]uint8{
	{0x10, 0x11, 0x12, 0x1e, 0x20, 0x2c, 0x2d, 0x2e, 0x0f, 0x2a},
	{0x47, 0x48, 0x49, 0x4b, 0x4d, 0x4f, 0x50, 0x51, 0x1c, 0x36},
}

func KeyboardDefaults() [][]string {
	return [][]string{
		{"Q", "W", "E", "A", "D", "Z", "X", "C", "Tab", "ShiftLeft", "Digit1", "Digit2", "Digit3", "Digit4"},
		{"Numpad7", "Numpad8", "Numpad9", "Numpad4", "Numpad6", "Numpad1", "Numpad2", "Numpad3", "Enter", "ShiftRight", "Digit7", "Digit8", "Digit9", "Digit0"},
	}
}

func KeyboardKeys() []string {
	names := []string{"Tab", "Enter", "NumpadEnter", "Space", "ShiftLeft", "ShiftRight", "ControlLeft", "ControlRight",
		"ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End", "PageUp", "PageDown", "Insert",
		"Minus", "Equal", "BracketLeft", "BracketRight", "Backslash", "Semicolon", "Quote", "Comma", "Period", "Slash", "Backquote",
		"NumpadAdd", "NumpadSubtract", "NumpadMultiply", "NumpadDivide", "NumpadDecimal"}
	for c := 'A'; c <= 'Z'; c++ {
		names = append(names, string(c))
	}
	for i := 0; i <= 9; i++ {
		names = append(names, fmt.Sprintf("Digit%d", i), fmt.Sprintf("Numpad%d", i))
	}
	for i := 1; i <= 8; i++ {
		names = append(names, fmt.Sprintf("F%d", i))
	}
	return names
}

func KeyLabel(name string) string {
	if name == "" {
		return "未綁定"
	}
	if len(name) == 6 && name[:5] == "Digit" {
		return name[5:]
	}
	switch name {
	case "Enter":
		return "Enter／NumEnter"
	case "ShiftLeft":
		return "左 Shift"
	case "ShiftRight":
		return "右 Shift"
	}
	return name
}

func KeyAliases(name string) []string {
	if name == "" {
		return nil
	}
	if name == "Enter" {
		return []string{"Enter", "NumpadEnter"}
	}
	return []string{name}
}

func validateKeyboard(bindings [][]string) error {
	if len(bindings) != 2 {
		return fmt.Errorf("鍵盤設定必須有兩名玩家")
	}
	allowed := map[string]bool{}
	for _, name := range KeyboardKeys() {
		allowed[name] = true
	}
	used := map[string]string{}
	for p, row := range bindings {
		if len(row) != len(KeyboardActions) {
			return fmt.Errorf("第 %d 人鍵盤欄位數錯誤", p+1)
		}
		for action, name := range row {
			if name != "" && !allowed[name] {
				return fmt.Errorf("不支援或保留的按鍵：%s", name)
			}
			for _, key := range KeyAliases(name) {
				if owner := used[key]; owner != "" {
					return fmt.Errorf("%s 已綁定%s", KeyLabel(key), owner)
				}
				used[key] = fmt.Sprintf("第 %d 人%s", p+1, KeyboardActions[action])
			}
		}
	}
	return nil
}

func (s *Settings) BindKey(player, action int, key string) error {
	if player < 0 || player >= 2 || action < 0 || action >= len(KeyboardActions) {
		return fmt.Errorf("鍵盤欄位錯誤")
	}
	if err := s.Validate(); err != nil {
		return err
	}
	old := s.Keyboard[player][action]
	s.Keyboard[player][action] = key
	if err := s.Validate(); err != nil {
		s.Keyboard[player][action] = old
		return err
	}
	return nil
}

// 鍵名只在前端轉成已驗掃描碼；不合併相反方向，也不合成斜鍵。
func (s Settings) KeyboardInput(pressed func(string) bool) (scans [2][]uint8, quick [2][4]bool, neutral bool) {
	neutral = true
	for p, row := range s.Keyboard {
		for action, name := range row {
			down := false
			for _, key := range KeyAliases(name) {
				down = down || pressed(key)
			}
			if !down {
				continue
			}
			neutral = false
			if action < 10 {
				scans[p] = append(scans[p], KeyboardScans[p][action])
			} else {
				quick[p][action-10] = true
			}
		}
	}
	return
}
