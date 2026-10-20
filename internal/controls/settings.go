package controls

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type Character struct {
	ID    string
	Name  string
	Moves []string
}

var Catalog = []Character{
	{"jaan", "斬", []string{"天雷斬", "旋風腿", "鐵頭功", "過肩摔"}},
	{"sarkov", "薩爾可夫", []string{"碎頭捶", "空抓", "折腰摔", "迴旋拋"}},
	{"bullet", "子彈", []string{"蜻蜓點水", "連環踢", "滾踢", "碎頭摔"}},
	{"phoenix", "鳳凰", []string{"火鳳凰", "迴旋腳刀", "倒掛金鉤", "蠍子尾", "反身摔"}},
	{"frank", "法蘭克", []string{"氣動拳", "旋風拳", "翔龍拳", "空旋摔"}},
	{"onimaru", "鬼丸", []string{"旋風忍術", "龜忍術", "空摔", "鬼啃頭"}},
	{"lan", "嵐", []string{"劈掛掌", "龍捲風", "雙截踢", "大佛腳", "大車輪"}},
	{"kim", "金太極", []string{"太極刀光", "太極波", "疾刺", "八卦掌", "空拋"}},
	{"spider", "蜘蛛女", []string{"鞭擊", "後空摔"}},
	{"clown", "小丑", []string{"蝦蟆功", "人肉戰車", "金剛陀螺", "辮子鞭", "辮子功"}},
	{"joe", "印第安喬", []string{"強力迫擊波", "旋轉衝擊", "無影腳", "擒拿摔"}},
}
var Slots = [4]string{"R1", "R2", "L1", "L2"}

type Settings struct {
	Version int                  `json:"version"`
	Players [2]map[string][4]int `json:"players"`
}

func Defaults() Settings {
	s := Settings{Version: 1}
	for p := range s.Players {
		s.Players[p] = map[string][4]int{}
		for _, c := range Catalog {
			var slots [4]int
			for i := range slots {
				if i < len(c.Moves) {
					slots[i] = i + 1
				}
			}
			s.Players[p][c.ID] = slots
		}
	}
	return s
}
func (s Settings) Validate() error {
	if s.Version != 1 {
		return fmt.Errorf("設定版本不支援：%d", s.Version)
	}
	for p := range s.Players {
		for _, c := range Catalog {
			slots, ok := s.Players[p][c.ID]
			if !ok {
				return fmt.Errorf("缺少角色設定：%s", c.ID)
			}
			for _, m := range slots {
				if m < 0 || m > len(c.Moves) {
					return fmt.Errorf("角色招式超出範圍：%s", c.ID)
				}
			}
		}
	}
	return nil
}
func Load(path string) (Settings, error) {
	s := Defaults()
	b, e := os.ReadFile(path)
	if os.IsNotExist(e) {
		return s, nil
	}
	if e != nil {
		return s, e
	}
	var saved Settings
	if e = json.Unmarshal(b, &saved); e != nil {
		return s, e
	}
	// 版本 1 的舊八人設定只補三名新角色；不補壞掉的既有角色。
	for p := range saved.Players {
		if saved.Players[p] == nil {
			continue
		}
		for _, c := range Catalog[8:] {
			if _, ok := saved.Players[p][c.ID]; !ok {
				saved.Players[p][c.ID] = s.Players[p][c.ID]
			}
		}
	}
	if e = saved.Validate(); e != nil {
		return s, e
	}
	return saved, nil
}
func (s Settings) Save(path string) error {
	if e := s.Validate(); e != nil {
		return e
	}
	if e := os.MkdirAll(filepath.Dir(path), 0755); e != nil {
		return e
	}
	b, e := json.MarshalIndent(s, "", "  ")
	if e != nil {
		return e
	}
	f, e := os.CreateTemp(filepath.Dir(path), ".settings-*.json")
	if e != nil {
		return e
	}
	name := f.Name()
	defer os.Remove(name)
	if _, e = f.Write(append(b, '\n')); e != nil {
		f.Close()
		return e
	}
	if e = f.Sync(); e != nil {
		f.Close()
		return e
	}
	if e = f.Close(); e != nil {
		return e
	}
	return os.Rename(name, path)
}
