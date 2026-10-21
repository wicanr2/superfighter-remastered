package desktop

import (
	"time"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type battleRenderKey struct {
	serial, steps uint64
	hd            bool
	victory       *renderdata.VictorySnapshot
}

type renderFrameTiming struct {
	Draw       uint64  `json:"draw"`
	IntervalMS float64 `json:"interval_ms"`
	DrawMS     float64 `json:"draw_ms"`
}

type renderPerformance struct {
	Draws      uint64              `json:"draws"`
	CacheHits  uint64              `json:"cache_hits"`
	StepMS     float64             `json:"step_ms"`
	UpdateMS   float64             `json:"update_ms"`
	DrawMS     float64             `json:"draw_ms"`
	IntervalMS float64             `json:"interval_ms"`
	FPS        float64             `json:"fps"`
	TPS        float64             `json:"tps"`
	Recent     []renderFrameTiming `json:"recent"`
	last       time.Time
}

func (g *Game) renderPerformance() renderPerformance {
	p := g.performanceState
	p.CacheHits = g.battleCacheHits
	p.FPS, p.TPS = ebiten.ActualFPS(), ebiten.ActualTPS()
	return p
}

func (g *Game) finishPerformanceDraw(started time.Time) {
	p := &g.performanceState
	p.DrawMS = float64(time.Since(started)) / float64(time.Millisecond)
	frame := renderFrameTiming{Draw: p.Draws, IntervalMS: p.IntervalMS, DrawMS: p.DrawMS}
	if len(p.Recent) == 64 {
		copy(p.Recent, p.Recent[1:])
		p.Recent[63] = frame
	} else {
		p.Recent = append(p.Recent, frame)
	}
}
