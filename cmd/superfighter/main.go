package main

import (
	"flag"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/desktop"
	"log"
	"os"
	"path/filepath"
	"time"
)

func main() {
	root := flag.String("data", "game-data", "合法原版資料目錄")
	config := flag.String("user-data", "", "獨立使用者設定與可寫 DOS 資料目錄")
	observe := flag.String("observe", "", "本機驗證用唯讀狀態輸出，不修改遊戲")
	capture := flag.String("capture", "", "F12 擷取路徑")
	hdAssets := flag.String("hd-assets", "", "本機 HD 背景素材目錄；不提供時使用原貌")
	hdCharacters := flag.String("hd-characters", "", "本機 HD 角色素材目錄；搭配 hd-assets 使用")
	quit := flag.Duration("quit-after", 0, "有界驗證時限，例如 90s；0 為不限制")
	flag.Parse()
	if *config == "" {
		dir, e := os.UserConfigDir()
		if e != nil {
			log.Fatal(e)
		}
		*config = filepath.Join(dir, "SuperfighterRemastered")
	}
	if !filepath.IsAbs(*root) {
		if _, e := os.Stat(*root); e != nil {
			exe, _ := os.Executable()
			candidate := filepath.Join(filepath.Dir(exe), *root)
			if _, e = os.Stat(candidate); e == nil {
				*root = candidate
			}
		}
	}
	if *quit < 0 || *quit > 24*time.Hour {
		log.Fatal("驗證時限不合法")
	}
	g, e := desktop.New(desktop.Options{Root: *root, DataDir: *config, Observe: *observe, Capture: *capture, HDAssets: *hdAssets, HDCharacters: *hdCharacters, QuitAfter: *quit})
	if e != nil {
		log.Fatal(e)
	}
	defer g.Close()
	ebiten.SetWindowTitle("快打至尊 Remastered")
	ebiten.SetWindowSize(desktop.Width, desktop.Height)
	ebiten.SetWindowResizingMode(ebiten.WindowResizingModeEnabled)
	ebiten.SetRunnableOnUnfocused(true)
	if e = ebiten.RunGame(g); e != nil {
		log.Print(e)
	}
}
