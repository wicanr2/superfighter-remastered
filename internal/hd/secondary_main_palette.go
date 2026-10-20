package hd

// addSecondaryMainPose 只建立同一原稿的唯讀配色視圖，主角色與額外圖像分開選擇。
func (a *Characters) addSecondaryMainPose(original *PoseArt) {
	if original.Pose.PaletteBank != 0 {
		return
	}
	bank, normal := graphicBank(original.Pose.SourceBank)
	base, haveBase := a.palettes[[2]int{original.Pose.Character, 0}]
	secondary, haveSecondary := a.palettes[[2]int{original.Pose.Character, 1}]
	if !normal || bank != 0 || !haveBase || !haveSecondary {
		return
	}
	var active uint16
	stride := (original.Pose.Width + 1) / 2
	for y := 0; y < original.Pose.Height; y++ {
		for x := 0; x < original.Pose.Width; x++ {
			value := original.packed[2+y*stride+x/2]
			if x%2 == 0 {
				value >>= 4
			} else {
				value &= 15
			}
			if value != 0 {
				active |= 1 << value
			}
		}
	}
	if active == 0 {
		return
	}
	for i := 1; i < 16; i++ {
		for j := i + 1; j < 16; j++ {
			if active&(1<<i) != 0 && active&(1<<j) != 0 && base[i] == base[j] && secondary[i] != secondary[j] {
				return
			}
		}
	}
	if a.secondaryMainPoses == nil {
		a.secondaryMainPoses = map[[3]int]*PoseArt{}
	}
	key, _ := characterArtKey(original.Pose.Character, original.Pose.Slot, 1, original.Pose.SourceBank)
	a.secondaryMainPoses[key] = &PoseArt{Pose: original.Pose, Bounds: original.Bounds, packed: original.packed,
		Image: &alternateCharacterImage{Image: original.Image, base: base, alternate: secondary, active: active}}
}
