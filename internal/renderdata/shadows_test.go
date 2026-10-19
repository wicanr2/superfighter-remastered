package renderdata

import (
	"image"
	"testing"
)

func TestShadowOriginalClippingBranches(t *testing.T) {
	// 左負座標及跳過分支由原指令導出，不冒充正常動態 fixture。
	for _, test := range []struct {
		name                   string
		x, left, right, camera int
		want                   image.Rectangle
		valid                  bool
	}{
		{"normal", 40, 0, 0, 80, image.Rect(40, 178, 99, 187), true},
		{"left-static", -5, 5, 0, 80, image.Rect(0, 178, 54, 187), true},
		{"right-observed", 259, 0, 1, 33, image.Rect(259, 178, 317, 187), true},
		{"skip-right-static", 319, 0, 61, 80, image.Rectangle{}, true},
		{"skip-left-static", -70, 70, 0, 80, image.Rectangle{}, true},
		{"zero-width-rejected", 317, 0, 59, 80, image.Rectangle{}, false},
		{"wrong-left", -5, 4, 0, 80, image.Rectangle{}, false},
		{"wrong-camera", 40, 0, 0, 160, image.Rectangle{}, false},
	} {
		t.Run(test.name, func(t *testing.T) {
			got, ok := (Shadow{Player: 0, X: test.x, Y: 178, LeftClip: test.left, RightClip: test.right}).Placement(test.camera)
			if ok != test.valid || got != test.want {
				t.Fatalf("got %v,%t want %v,%t", got, ok, test.want, test.valid)
			}
		})
	}
}
