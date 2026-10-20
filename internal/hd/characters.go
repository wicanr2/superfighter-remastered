package hd

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"image"
	"image/png"
	"io"
	"os"
	"path/filepath"
	"strings"

	"github.com/wicanr2/superfighter-remastered/internal/renderdata"
)

type CharacterSource struct {
	SourceBank string `json:"source_bank,omitempty"`
	Character int    `json:"character"`
	File      string `json:"file"`
	SHA256    string `json:"sha256"`
}
type CharacterAtlas struct {
	File   string `json:"file"`
	SHA256 string `json:"sha256"`
	Width  int    `json:"width"`
	Height int    `json:"height"`
}
type CharacterPose struct {
	SourceBank string `json:"source_bank,omitempty"`
	PaletteBank  int    `json:"palette_bank,omitempty"`
	Character    int    `json:"character"`
	Slot         int    `json:"slot"`
	Width        int    `json:"width"`
	Height       int    `json:"height"`
	SourceOffset int    `json:"source_offset"`
	SourceSHA256 string `json:"source_sha256"`
	Atlas        string `json:"atlas"`
	Rect         [4]int `json:"rect"`
}
type CharacterManifest struct {
	Version  int               `json:"version"`
	Kind     string            `json:"kind"`
	Sources  []CharacterSource `json:"sources"`
	Atlases  []CharacterAtlas  `json:"atlases"`
	Poses    []CharacterPose   `json:"poses"`
	Evidence []string          `json:"evidence"`
}
type PoseArt struct {
	Pose   CharacterPose
	Image  image.Image
	Bounds image.Rectangle
	packed []byte // 使用者原檔的唯讀切片；不寫入 JSON 或發行素材。
}
type Characters struct {
	Manifest CharacterManifest
	poses    map[[3]int]*PoseArt
	palettes map[[2]int][16][3]uint8
	alternatePalettes map[int][16][3]uint8
	alternatePoses map[[3]int]*PoseArt
	secondaryMainPoses map[[3]int]*PoseArt
}

func graphicBank(name string) (int,bool) {
	switch name {case "","normal":return 0,true;case "victory":return 1,true;default:return 0,false}
}

func characterArtKey(character,slot,palette int,sourceBank string) ([3]int,bool) {
	bank,ok:=graphicBank(sourceBank);if !ok{return [3]int{},false}
	if bank==1 {if palette!=0{return [3]int{},false};return [3]int{character,slot,2},true}
	return [3]int{character,slot,palette},true
}

func checkedFile(dir, name, want string, limit int64) ([]byte, error) {
	if name == "" || name == "." || strings.ContainsAny(name, "/\\:") || filepath.Base(name) != name {
		return nil, fmt.Errorf("素材檔名錯誤")
	}
	path := filepath.Join(dir, name)
	info, e := os.Lstat(path)
	if e != nil {
		return nil, e
	}
	if !info.Mode().IsRegular() || info.Size() > limit {
		return nil, fmt.Errorf("素材型態或大小錯誤")
	}
	f, e := os.Open(path)
	if e != nil {
		return nil, e
	}
	defer f.Close()
	b, e := io.ReadAll(io.LimitReader(f, limit+1))
	if e != nil {
		return nil, e
	}
	if int64(len(b)) > limit {
		return nil, fmt.Errorf("素材超過大小限制")
	}
	if want != "" && fmt.Sprintf("%x", sha256.Sum256(b)) != want {
		return nil, fmt.Errorf("素材雜湊不符：%s", name)
	}
	return b, nil
}

// LoadCharacters 一次驗整組來源與素材，失敗時不傳回部分角色。
func LoadCharacters(dir, originalRoot string) (*Characters, error) {
	b, e := checkedFile(dir, "manifest.json", "", 520<<10)
	if e != nil {
		return nil, e
	}
	var m CharacterManifest
	decoder := json.NewDecoder(bytes.NewReader(b))
	decoder.DisallowUnknownFields()
	if e = decoder.Decode(&m); e != nil {
		return nil, e
	}
	if e = decoder.Decode(&struct{}{}); e != io.EOF {
		return nil, fmt.Errorf("角色素材清單有額外資料")
	}
	if (m.Version != 1 && m.Version != 2 && m.Version != 3) || m.Kind != "original-draw-characters" || len(m.Sources) == 0 || len(m.Sources) > 22 || len(m.Atlases) == 0 || len(m.Atlases) > 128 || len(m.Poses) == 0 || len(m.Poses) > 11*216 {
		return nil, fmt.Errorf("角色素材版本或數量錯誤")
	}
	a := &Characters{Manifest: m, poses: map[[3]int]*PoseArt{}, palettes: map[[2]int][16][3]uint8{}}
	sources := map[[2]int][]byte{}
	for _, source := range m.Sources {
		bank,valid:=graphicBank(source.SourceBank);key:=[2]int{source.Character,bank}
		file,minSize:=fmt.Sprintf("SFMAN%02d.DAT",source.Character+1),0xc48
		if bank==1{file,minSize=renderdata.VictoryFigureFile(source.Character),0x180}
		if source.Character < 0 || source.Character > 10 || !valid || m.Version<3 && source.SourceBank!="" || source.File != file || sources[key] != nil || len(source.SHA256) != 64 {
			return nil, fmt.Errorf("角色來源重複或未對應")
		}
		data, e := checkedFile(originalRoot, source.File, source.SHA256, 4<<20)
		if e != nil {
			return nil, e
		}
		if len(data) < minSize {
			return nil, fmt.Errorf("角色來源過短")
		}
		sources[key] = data
		if bank==1{continue}
		for bank := 0; bank < min(m.Version,2); bank++ {
			var palette [16][3]uint8
			for i := range palette {
				for k := 0; k < 3; k++ {
					v := data[0xac8+bank*48+i*3+k]
					if v > 63 {
						return nil, fmt.Errorf("角色來源色盤錯誤")
					}
					palette[i][k] = v<<2 | v>>4
				}
			}
			a.palettes[[2]int{source.Character, bank}] = palette
		}
	}
	if err := a.loadAlternatePalettes(originalRoot); err != nil {
		return nil, err
	}
	images := map[string]image.Image{}
	totalPixels := 0
	for _, atlas := range m.Atlases {
		if images[atlas.File] != nil || len(atlas.SHA256) != 64 || atlas.Width < 1 || atlas.Height < 1 || atlas.Width > 4096 || atlas.Height > 4096 {
			return nil, fmt.Errorf("角色圖集重複或尺寸錯誤")
		}
		totalPixels += atlas.Width * atlas.Height
		// 044 的光效群組共 115,204,291 像素；110 Mi 保留明確總量限制。
		if totalPixels > 110*1024*1024 {
			return nil, fmt.Errorf("角色圖集超過記憶體限制")
		}
		data, e := checkedFile(dir, atlas.File, atlas.SHA256, 32<<20)
		if e != nil {
			return nil, e
		}
		cfg, e := png.DecodeConfig(bytes.NewReader(data))
		if e != nil {
			return nil, e
		}
		if cfg.Width != atlas.Width || cfg.Height != atlas.Height {
			return nil, fmt.Errorf("角色圖集實際尺寸不符")
		}
		img, e := png.Decode(bytes.NewReader(data))
		if e != nil {
			return nil, e
		}
		images[atlas.File] = img
	}
	for _, pose := range m.Poses {
		bank,validBank:=graphicBank(pose.SourceBank)
		key,validKey := characterArtKey(pose.Character,pose.Slot,pose.PaletteBank,pose.SourceBank)
		data := sources[[2]int{pose.Character,bank}]
		img := images[pose.Atlas]
		if !validBank || !validKey || m.Version<3 && pose.SourceBank!="" || pose.Slot < 0 || pose.Slot >= 72 || pose.PaletteBank < 0 || pose.PaletteBank >= min(m.Version,2) || data == nil || img == nil || a.poses[key] != nil || sources[[2]int{pose.Character,0}]==nil {
			return nil, fmt.Errorf("角色姿態重複或來源缺少")
		}
		table,payload:=0xb28,0xc48;if bank==1{table,payload=0x60,0x180}
		pointer := table + pose.Slot*4
		offset := payload + int(binary.LittleEndian.Uint16(data[pointer:]))*16 + int(binary.LittleEndian.Uint16(data[pointer+2:]))
		if offset < payload || offset+2 > len(data) {
			return nil, fmt.Errorf("角色原始指標越界")
		}
		w, h := int(data[offset]), int(data[offset+1])
		end := offset + 2 + (w+1)/2*h
		if w < 1 || h < 1 || end > len(data) || pose.Width != w || pose.Height != h || pose.SourceOffset != offset || fmt.Sprintf("%x", sha256.Sum256(data[offset:end])) != pose.SourceSHA256 {
			return nil, fmt.Errorf("角色姿態來源不符")
		}
		r := image.Rectangle{Min: image.Pt(pose.Rect[0], pose.Rect[1]), Max: image.Pt(pose.Rect[2], pose.Rect[3])}
		if r.Empty() || !r.In(img.Bounds()) {
			return nil, fmt.Errorf("角色圖集矩形越界")
		}
		opaque, clear := false, false
		for y := r.Min.Y; y < r.Max.Y; y++ {
			for x := r.Min.X; x < r.Max.X; x++ {
				_, _, _, alpha := img.At(x, y).RGBA()
				if alpha == 0 {
					clear = true
				}
				if alpha >= 0x8000 {
					opaque = true
				}
			}
		}
		if !opaque || !clear {
			return nil, fmt.Errorf("角色素材缺少圖像或透明區")
		}
		a.poses[key] = &PoseArt{Pose: pose, Image: img, Bounds: r, packed: data[offset:end]}
		a.addAlternatePose(key, a.poses[key])
		a.addSecondaryMainPose(a.poses[key])
	}
	return a, nil
}

// Select 先驗完全部角色，呼叫端成功後才可開始畫 HD。
func (a *Characters) Select(layers []renderdata.Layer, palette [256][3]uint8) ([]*PoseArt, string) {
	if len(layers) < 6 || len(layers) > 38 || len(layers)%2 != 0 || !layers[0].Background {
		return nil, "等待完整角色圖層"
	}
	var out []*PoseArt
	var players [2]bool
	characters := [2]int{-1, -2}
	for _, layer := range layers {
		if s := layer.Sprite; s != nil && !s.Effect && s.Player >= 0 && s.Player < 2 {
			characters[s.Player] = s.Character
		}
	}
	sameCharacter := characters[0] >= 0 && characters[0] == characters[1]
	for _, layer := range layers {
		s := layer.Sprite
		if s == nil {
			continue
		}
		if s.Player < 0 || s.Player > 1 || (!s.Effect && players[s.Player]) {
			return nil, "角色次序未對應"
		}
		bank := 0
		if s.PaletteBase == uint8(0xd0+s.Player*0x20) {
			bank = 1
		}
		if s.Effect {
			if s.Flags&192 != 0 && s.Flags&192 != 64 || s.LeftClip != 0 || s.RightClip != 0 || s.TopClip != 0 {
				return nil, "此特效翻轉或裁切保留原貌"
			}
		} else {
			players[s.Player] = true
		}
		key,knownSource:=characterArtKey(s.Character,s.Slot,bank,s.SourceBank)
		if !knownSource{return nil,"角色圖像群組未對應，保留原貌"}
		art := a.poses[key]
		if !s.Effect && bank == 1 {
			art = a.secondaryMainPoses[key]
		}
		if art == nil {
			return nil, "此動作的 HD 素材尚未完成，保留原貌"
		}
		if s.SourceSHA256 != art.Pose.SourceSHA256 || s.Width != art.Pose.Width || s.Height != art.Pose.Height {
			return nil, "角色來源不符，保留原貌"
		}
		if s.PaletteBase != uint8(0xc0+s.Player*0x20+bank*16) {
			return nil, "此色盤保留原貌"
		}
		if (s.Effect && bank == 0 || !s.Effect && (bank == 1 || s.Flags&192 == 192 || s.TopClip != 0)) && !spriteGeometryMatches(s, art.packed, layer) {
			return nil, "翻轉或裁切未吻合原版圖層，保留原貌"
		}
		if !matchesCharacterPalette(palette, s.PaletteBase, a.palettes[[2]int{s.Character, bank}]) {
			alternate, known := a.alternatePalettes[s.Character]
			alternateArt := a.alternatePoses[key]
			if bank != 0 || s.Player != 1 || !sameCharacter || !known || alternateArt == nil ||
				!matchesCharacterPalette(palette, s.PaletteBase, alternate) {
				return nil, "角色色盤轉場，保留原貌"
			}
			art = alternateArt
		}
		out = append(out, art)
	}
	if !players[0] || !players[1] {
		return nil, "等待兩名完整角色"
	}
	return out, "HD 角色與背景"
}

func (a *Characters) HasEffects() bool {
	for _, pose := range a.Manifest.Poses {
		if pose.PaletteBank == 1 {
			return true
		}
	}
	return false
}
