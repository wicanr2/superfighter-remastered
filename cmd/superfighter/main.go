package main

import (
	"flag"
	"fmt"
	"github.com/hajimehoshi/ebiten/v2"
	"github.com/wicanr2/superfighter-remastered/internal/desktop"
	"github.com/wicanr2/superfighter-remastered/internal/gamefiles"
	"log"
	"os"
	"path/filepath"
	"time"
)

var version = "development"

func packageRoot() string {
	exe, _ := os.Executable()
	base := filepath.Dir(exe)
	if filepath.Base(base) == "MacOS" && filepath.Base(filepath.Dir(base)) == "Contents" {
		return filepath.Join(filepath.Dir(base), "Resources")
	}
	return base
}

func main() {
	showVersion := flag.Bool("version", false, "顯示完整版本後離開")
	importSource := flag.String("import-data", "", "從合法原版目錄或 jsdos ZIP 匯入到 -data；不覆寫既有目錄")
	root := flag.String("data", "game-data", "合法原版資料目錄")
	config := flag.String("user-data", "", "獨立使用者設定與可寫 DOS 資料目錄")
	observe := flag.String("observe", "", "本機驗證用唯讀狀態輸出，不修改遊戲")
	capture := flag.String("capture", "", "F12 擷取路徑")
	hdAssets := flag.String("hd-assets", "", "本機 HD 背景素材目錄；不提供時使用原貌")
	hdCharacters := flag.String("hd-characters", "", "本機 HD 角色素材目錄；搭配 hd-assets 使用")
	quit := flag.Duration("quit-after", 0, "有界驗證時限，例如 90s；0 為不限制")
	training := flag.Bool("training", false, "預先開啟練習模式：雙方滿血、時間停止、電腦中立；F9 可切換")
	flag.Parse()
	if *showVersion {
		fmt.Println(version)
		return
	}
	if *config == "" {
		dir, e := os.UserConfigDir()
		if e != nil {
			log.Fatal(e)
		}
		*config = filepath.Join(dir, "SuperfighterRemastered")
	}
	if !filepath.IsAbs(*root) {
		if _, e := os.Stat(*root); e != nil {
			candidate := filepath.Join(packageRoot(), *root)
			if _, e = os.Stat(candidate); e == nil {
				*root = candidate
			}
		}
	}
	if *importSource != "" {
		if err := gamefiles.Import(*importSource, *root); err != nil {
			log.Fatal(err)
		}
		fmt.Println("原版資料已核對並匯入：", *root)
		return
	}
	if _, err := os.Stat(filepath.Join(*root, "SF.EXE")); err != nil {
		log.Fatal("缺少合法原版資料。請執行：superfighter -import-data 原版目錄或jsdos檔 -data game-data；詳見封包 README。")
	}
	if *hdCharacters == "" {
		candidate := filepath.Join(packageRoot(), "assets", "hd", "characters")
		if _, err := os.Stat(filepath.Join(candidate, "manifest.json")); err == nil {
			*hdCharacters = candidate
		}
	}
	if *hdAssets == "" && *hdCharacters != "" {
		candidate := filepath.Join(*config, "hd-rooftop")
		if err := gamefiles.EnsureBackground(*root, filepath.Join(packageRoot(), "assets", "hd", "backgrounds", "rooftop.png"), candidate); err == nil {
			*hdAssets = candidate
		} else {
			log.Print("HD 背景未準備，保留原貌：", err)
		}
	}
	if *quit < 0 || *quit > 24*time.Hour {
		log.Fatal("驗證時限不合法")
	}
	g, e := desktop.New(desktop.Options{Version: version, Root: *root, DataDir: *config, Observe: *observe, Capture: *capture, HDAssets: *hdAssets, HDCharacters: *hdCharacters, QuitAfter: *quit, Training: *training})
	if e != nil {
		log.Fatal(e)
	}
	defer g.Close()
	ebiten.SetWindowTitle("快打至尊 Remastered " + version)
	ebiten.SetWindowSize(desktop.Width, desktop.Height)
	ebiten.SetWindowResizingMode(ebiten.WindowResizingModeEnabled)
	ebiten.SetRunnableOnUnfocused(true)
	if e = ebiten.RunGame(g); e != nil {
		log.Print(e)
	}
}
