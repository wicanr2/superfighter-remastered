package oracle

import "github.com/wicanr2/dosgolem/internal/machine"

// LinearScanout 為固定鏈結 mode 13h 的顯示幾何與逐點色號複本。
type LinearScanout = machine.LinearScanout

// LinearScanout 套用實際顯示起點、列距與可見高度。
// 不執行指令、不改 I/O 或記憶體；Screen／Indexed 的原契約保持不變。
func (o *Oracle) LinearScanout() (LinearScanout, error) { return o.m.LinearScanout() }
