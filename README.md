# 快打至尊 Remastered

Windows、macOS、Linux 原生桌面重製。以 dosgolem 執行原版核心，接入雙人手把、逐角色四格快速出招與街機手繪 HD，並保存遊戲歷史。

玩家入口使用 Ebitengine 原生視窗，直接處理鍵鼠與標準手把。原版核心負責規則、碰撞、AI 及流程。既有網頁只保留研究用途。

目前已有原生雙打、兩人拳腳、斬四招、設定保存與可切換的屋頂 HD 背景。人物、招式與戰鬥介面保留原版。完整角色 HD、實體手把、完整回合、其他角色快捷、音訊與正式速度仍待驗收。最近收據及各平台限制見 [CONTEXT](CONTEXT.md)。

角色 HD 已有斬與法蘭克共 48 個重繪姿態。首版原生播放已通過 Linux 正常雙打、行走、跳躍及缺姿態回退等 13 項檢查，收據在 `workplace/native-actors-v1/receipt.json`。目前來源正將五層改為六層，分開純背景與介面寫入；這版尚待原生視窗重驗。完整動作仍未完成，製作契約見[角色規格](docs/spec/008-hd-characters.md)。

## 目前整合畫面

![兩人獨立手把指派與四格快捷設定](docs/screenshots/gamepad-settings.png)

Windows 原生程式在 Wine 中顯示的設定介面，擷取於原版核心執行前。可分別指派兩人的手把，逐角色設定 R1／R2／L1／L2。擷取時未連接實體手把。[截圖來源](docs/screenshots/source.json)。

以下對戰圖片含原版及衍生美術，僅留本機工作區，GitHub 不收錄圖片檔：

[屋頂 HD 整合畫面](workplace/hd-native-v2/hd-rooftop.png)

Linux 原生整合版，從原版標題正常進入斬對法蘭克雙打。屋頂使用高解析背景，人物動作、陰影、招式與上方介面保留原貌；下方是兩人的四格快捷。這是背景切片，完整角色 HD 仍在製作。

[HD 對局中的手把與第五招設定](workplace/hd-native-v2/native-settings.png)

兩人獨立的手把指派與角色快捷設定。圖中第一人選鳳凰第五招並將 R2 留空，第二人的配置保持獨立。擷取時沒有接實體手把，實體裝置驗收仍待進行。

兩圖出自同一份[原生視窗測試收據](workplace/hd-native-v2/receipt.json)。另有同狀態的[原貌](workplace/hd-native-v2/original-paused.png)、[HD 背景](workplace/hd-native-v2/hd-paused.png)與[逐點核對](workplace/hd-native-v2/comparison.json)。原始 PNG 保留於本機工作區。

## 建置與執行

開發建置在 Docker 內執行，工作區需要已準備的 dosgolem 獨立來源及工具鏈，詳見[工作契約](AGENTS.md)和[桌面規格](docs/spec/005-native-desktop.md)。

儲存庫不附原版資料、HD 衍生美術、研究收據、dosgolem 私有來源或本機快取。`go.work.example` 記錄相對目錄配置，準備來源後複製為 `go.work`；原版匯入與來源快照工具為 `tools/prepare.py`，執行器補丁為 `tools/apply_runtime_patch.py`。現行收據中的 `workplace/` 連結僅供本機核對。

```sh
bash tools/build_desktop.sh
```

開發二進位在 `workplace/bin/`：

| 平台 | 檔案 |
|---|---|
| Linux x86-64 | `superfighter-linux-amd64` |
| Windows x86-64 | `superfighter-windows-amd64.exe` |
| macOS Intel | `superfighter-macos-amd64` |
| macOS Apple Silicon | `superfighter-macos-arm64` |

玩家在自己的電腦執行對應程式，以 `-data` 指定合法原版資料目錄。未指定時尋找 `game-data/`。例如 Windows：

```powershell
.\superfighter-windows-amd64.exe -data .\game-data
```

這些是中間產物，尚未製作正式安裝包、macOS 簽章或 Release。原版 EXE、COM、DAT、美術及音訊不內嵌，不加入 Git 或一般發行包。

本機屋頂試作素材已備妥時，可加上 `-hd-assets workplace/hd-rooftop-study`，再按「原貌／HD 背景」切換。素材準備與驗證見[背景規格](docs/spec/006-rooftop-background.md)。沒有素材或場景未對應時顯示原貌。

## 操作

按「開始／繼續」，由原版標題進單打或雙打。「手把與快捷設定」可指派兩人裝置、切換要設定的角色與四招；設定角色不改變原版選角。

| 輸入 | 第一人 | 第二人 |
|---|---|---|
| 方向 | QWE／A D／ZXC | 數字鍵盤 789／4 6／123 |
| 拳 | Tab | Enter |
| 腳 | 左 Shift | 右 Shift |
| 手把拳／腳 | 西側／南側面鍵 | 同左，另行指派裝置 |
| 快捷 | R1／R2／L1／L2 預設招式 1／2／3／4 | 各自保存角色配置 |
| 暫停 | Esc 或手把 Start | 共用對局 |
| 設定 | F10；Tab 選欄位，左右調整，Esc 關閉 | 同左 |

每名角色最多四格，可選第五招或留空。快捷按住不連發，投技仍須近身。視窗失焦會暫停；手把斷線清除該玩家指派及輸入，重接後需再次指派。

設定與可寫 DOS 資料存於作業系統的 `SuperfighterRemastered` 使用者設定目錄，可用 `-user-data` 改位置。原始資料維持唯讀。

## 文件

- [工作契約與索引](AGENTS.md)、[目前狀態](CONTEXT.md)、[工作清單](WORKLIST.md)。
- [驗證範圍](VERIFICATION-MATRIX.md)、[研究證據](RESEARCH-LOG.md)、[工作歷程](WORKLOG.md)。
- [原生桌面規格](docs/spec/005-native-desktop.md)、[輸入證據](docs/spec/004-live-input-slice.md)、[手把草案](docs/spec/002-gamepad-design.md)。
- [HD 規格](docs/spec/003-hd-design.md)、[屋頂背景切片](docs/spec/006-rooftop-background.md)、[角色分層](docs/spec/008-hd-characters.md)。背景已接原生對戰，完整角色動畫及介面重繪仍在製作。
- [青衫與 SP Moves 歷史保存](docs/game-history.md)。

自有程式與文件採 [RRSAL-1.0](LICENSE)，為 source-available 專案。此授權不涵蓋原版遊戲、外站原文與圖片或衍生美術；玩家須自備合法原版。專案與原版權利人沒有隸屬關係。內嵌中文字型另依 [SIL Open Font License](internal/desktop/assets/OFL.txt) 使用。
