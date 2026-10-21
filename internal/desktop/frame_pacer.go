package desktop

import "time"

// waitRenderFrame 只安排擷取畫面的送出時間，不推進原版或補跑遊戲畫格。
func (g *Game) waitRenderFrame() {
	const period = time.Second / 60
	now := time.Now()
	if g.frameDeadline.IsZero() {
		g.frameDeadline = now.Add(period)
		return
	}
	if now.Before(g.frameDeadline) {
		time.Sleep(g.frameDeadline.Sub(now))
		now = time.Now()
	}
	g.frameDeadline = g.frameDeadline.Add(period)
	if now.After(g.frameDeadline.Add(period)) {
		g.frameDeadline = now.Add(period)
	}
}
