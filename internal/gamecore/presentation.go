package gamecore

import (
	"crypto/sha256"
	"fmt"

	"github.com/wicanr2/dosgolem/oracle"
	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

// Presentation 是原版完成顯示拷貝後的只讀快照。不是可載入的遊戲存檔。
// Pixels 沿用 oracle.Indexed 的線性 A0000 契約；CRTC 起點另列，未暗中改顯示語意。
type Presentation struct {
	Serial           uint64             `json:"serial"`
	Steps            uint64             `json:"steps"`
	Counter          uint16             `json:"counter"`
	Scene            int                `json:"scene"`
	CameraX          int                `json:"camera_x"`
	CRTCRows         int                `json:"crtc_rows_not_applied_by_oracle"`
	BackgroundSHA256 string             `json:"background_sha256"`
	Pixels           []byte             `json:"-"`
	Palette          [256][3]uint8      `json:"-"`
	Actors           [2]ActorPose       `json:"actors"`
	DrawPriority     uint8              `json:"draw_priority"`
	Layers           []renderdata.Layer `json:"layers,omitempty"`
	LayersComplete   bool               `json:"layers_complete"`
	LayerError       string             `json:"layer_error,omitempty"`
}
type ActorPose struct {
	Character int   `json:"character"`
	Slot      int   `json:"slot"`
	X         int   `json:"x"`
	Y         int   `json:"y"`
	Attr      uint8 `json:"attr"`
	Facing    uint8 `json:"facing"`
}

func (c *Core) Presentation() Presentation { return c.presentation }
func (c *Core) capturePresentation(o *oracle.Oracle) {
	ds, ok := c.dataSegment()
	if !ok {
		return
	}
	segment := o.Word(oracle.Far(ds, 0x0c))
	if segment == 0 {
		return
	}
	w, h, pixels := o.Screen()
	if w != 320 || h != 200 || len(pixels) != 64000 {
		return
	}
	frame := Presentation{Serial: c.presentation.Serial + 1, Steps: o.Steps(), Counter: o.Word(oracle.Far(ds, 0x1a)), Scene: int(o.Word(oracle.Far(ds, 0x1338))), CameraX: int(o.Word(oracle.Far(ds, 0x1332))), CRTCRows: int(o.Byte(oracle.Far(ds, 0x1334))), Pixels: append([]byte(nil), pixels...), Palette: o.Palette()}
	frame.BackgroundSHA256 = fmt.Sprintf("%x", sha256.Sum256(o.Bytes(oracle.Far(segment, 0), 480*204)))
	for p := 0; p < 2; p++ {
		frame.Actors[p] = ActorPose{Character: int(o.Word(oracle.Far(ds, uint16(0x12ac+p*2)))), Slot: int(o.Byte(oracle.Far(ds, []uint16{0x16f2, 0x16fa}[p]))), X: int(int16(o.Word(oracle.Far(ds, uint16(0x16d6+p*2))))) - frame.CameraX, Y: int(int16(o.Word(oracle.Far(ds, uint16(0x16de+p*2))))), Attr: o.Byte(oracle.Far(ds, uint16(0x16fe+p))), Facing: o.Byte(oracle.Far(ds, uint16(0x16b4+p)))}
	}
	frame.DrawPriority = o.Byte(oracle.Far(ds, 0x1335))
	c.finishLayers(&frame)
	c.presentation = frame
}
