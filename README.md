# 快打至尊 Remastered

Windows、macOS、Linux 原生桌面重製。以 dosgolem 執行原版核心，接入雙人手把、逐角色四格快速出招與街機手繪 HD，並保存遊戲歷史。

玩家入口使用 Ebitengine 原生視窗，直接處理鍵鼠與標準手把。原版核心負責規則、碰撞、AI 及流程。既有網頁只保留研究用途。

目前已有原生雙打、兩人拳腳、斬四招、設定保存，以及可切換的屋頂 HD 背景、部分人物動作、已驗招式特效、柔邊地面陰影、生命條、計時、名字與勝場圖示。開場 `ROUND`／`FIGHT !`、斬首勝的鞠躬與 `JAAN WIN` 已接 HD；第二人法蘭克的抱胸、`FRANK WIN` 與右側首勝也已在 Linux 驗證。Linux 雙打基準曾正常打完兩回合、顯示結果並返回標題，後續擴充另驗各自範圍。完整角色 HD、實體手把、其他角色快捷、音訊與正式速度仍待驗收。最近收據及各平台限制見 [CONTEXT](CONTEXT.md)。

斬與法蘭克已對應全部 144 個一般來源槽、13 組第二色盤特效，以及 WIN 圖像的 144 個入口。WIN 入口對應七張不同勝利姿態，與一般動作分開辨識；登錄齊全不代表完整動畫已驗。介面基底的 Linux 案例通過 16 項檢查，Windows Wine 的斬、法蘭克案例各通過 16 項，包含特效、介面及同狀態切換。兩平台的法蘭克案例另驗到實際扣血。完整動畫與其他角色仍未完成，製作契約見[角色](docs/spec/008-hd-characters.md)、[特效](docs/spec/009-hd-effects.md)、[戰鬥介面](docs/spec/010-hd-battle-hud.md)及[勝利姿態](docs/spec/017-victory-pose-banks.md)。

斬、法蘭克、薩爾可夫、子彈與鳳凰的一般姿態已接入原生，實測範圍見[薩爾可夫](docs/spec/018-sarkov-hd.md)、[子彈](docs/spec/020-bullet-hd.md)與[鳳凰](docs/spec/021-phoenix-hd.md)。目前群組共 589 個鍵，包含五人的一般來源、既有特效與三人的 WIN 入口。薩爾可夫首勝已驗 Linux 完整流程及 Wine 勝利畫面／切換，Wine 下一回合仍未驗完。完整動畫、替代色盤、其他角色快捷及其餘角色／場景仍在製作。

## 目前整合畫面

![兩人獨立手把指派與四格快捷設定](docs/screenshots/gamepad-settings.png)

Windows 原生程式在 Wine 中顯示的設定介面，擷取於原版核心執行前。可分別指派兩人的手把，逐角色設定 R1／R2／L1／L2。擷取時未連接實體手把。[截圖來源](docs/screenshots/source.json)。

以下對戰圖片含原版及衍生美術，僅留本機工作區，GitHub 不收錄圖片檔：

![鳳凰對法蘭克的原生 HD 人物與原姓名](workplace/native-phoenix-v2/hd-paused.png)

鳳凰以原字圖姓名 `PHO HUANG` 顯示，61 組不同來源對應 72 個一般入口。Linux／Wine 各由正常選角驗行走、蹲、跳、拳及切換；[跳躍](workplace/native-phoenix-v2/jump.png)、[同狀態原貌](workplace/native-phoenix-v2/original-paused.png)與[恢復 HD](workplace/native-phoenix-v2/hd-restored.png)已獨立核對。既有兩人手把與四格設定沿用，鳳凰快捷尚未啟用。[範圍與限制](docs/spec/021-phoenix-hd.md)。

![子彈對法蘭克的原生 HD 人物與姓名](workplace/native-bullet-v1/hd-paused.png)

子彈以原姓名 `BULLET` 顯示，58 張姿態對應 72 個一般入口。Linux／Wine 均由正常選角驗行走、蹲、跳、拳擊與切換；[同狀態原貌](workplace/native-bullet-v1/original-paused.png)及[恢復 HD](workplace/native-bullet-v1/hd-restored.png)已獨立核對。快捷與雙人手把入口沿用既有設定，子彈的快捷尚未啟用。[範圍與限制](docs/spec/020-bullet-hd.md)。

![薩爾可夫正常首勝的 HD 姿態與 SARORKOV WIN](workplace/native-sarkov-victory-v1/victory-hd.png)

Linux 以普通方向與拳鍵取得第一人勝利，人物讀取獨立 BBWIN 圖像。七張擷取包含下一回合清除；Wine 另核對到勝利及同狀態切換，尚未取得下一回合收據。[勝利驗證範圍](docs/spec/019-sarkov-victory.md)。

![薩爾可夫對法蘭克的 HD 人物、原姓名與屋頂](workplace/native-sarkov-v2/hd-rooftop.png)

Linux 由正常選角進入薩爾可夫對法蘭克，姓名忠於本包原字圖 `SARORKOV`。人物、屋頂、陰影與介面同格呈現 HD。[同狀態原貌](workplace/native-sarkov-v2/original-paused.png)與[恢復 HD](workplace/native-sarkov-v2/hd-restored.png)已獨立重組並核對切換；Wine 另驗相同流程。下方仍保留兩人的手把與四格快捷入口，薩爾可夫的快捷尚未啟用。

![正常首勝的 HD 鞠躬、勝負文字與雙人快捷列](workplace/native-victory-v1/victory-hd.png)

Linux 原生版由正常對戰取得斬首勝，鞠躬讀取原版獨立 WIN 圖像來源，中央顯示高解析 `JAAN WIN`。[同狀態原貌](workplace/native-victory-v1/victory-original.png)及[切回 HD](workplace/native-victory-v1/victory-restored.png)的核心與來源相同，恢復畫面逐點一致。七張擷取已由原檔重組；文字 GPU 寫入限制在原字圖矩形。這是首勝樣本，其他勝者與完整勝利動畫另驗，詳見[勝負文字規格](docs/spec/016-hd-victory-messages.md)。下方四格快捷與手把設定入口沿用既有操作。

![第二人法蘭克首勝的抱胸、FRANK WIN 與右側勝場](workplace/native-frank-victory-v1/victory-hd.png)

Linux 由第二人正常方向與拳鍵操作，在時間歸零後獲勝，保留原版兩人生命值與結束方式。抱胸讀取 FFWIN.FIG，中央顯示 `FRANK WIN`；[同狀態原貌](workplace/native-frank-victory-v1/victory-original.png)與[恢復 HD](workplace/native-frank-victory-v1/victory-restored.png)已逐點核對，下一回合右側顯示一勝。這個第二人案例的 Windows Wine 驗證達執行期限，尚未取得勝利收據，不稱兩平台均已通過。

![目前整合的 HD 屋頂、人物、介面與開場](workplace/native-display-opening-v2/round-hd.png)

目前原生版已修正顯示起點。原貌與 HD 全部圖層共用實際可見視窗，開場頂端資料列已移出，底部四列完整保留；正常跳躍與踢擊也跟隨原版顯示位移。Linux／Wine 各十張開場擷取、Linux 一般對戰十五張及舊素材十一張已獨立核對，缺件整張回退與切回 HD 逐點一致。這是限定顯示配置的硬體規格近似，實測範圍見[規格 015](docs/spec/015-native-scanout.md)與[目前稽核](workplace/native-display-audit.json)。

下列圖片保存顯示修正前的版本與各自驗證範圍：

[開場 ROUND 1](workplace/native-rounds-v1/round-hd.png)、[FIGHT !](workplace/native-rounds-v1/fight-hd.png)、[部分展開窗口](workplace/native-rounds-v1/round-partial-hd.png)及[同狀態原貌](workplace/native-rounds-v1/round-original.png)。Linux／Wine 各十張擷取驗來源、原生字圖裁切及切回逐點一致；只驗第一回合。頂端保留現有 oracle 線性畫面的原版資料，尚未套用 CRTC 顯示起點。詳見[開場規格](docs/spec/013-hd-round-messages.md)。

頂端問題的[原版重組預覽](workplace/display-ports-v1/display-010.scanout.png)來自獨立規格重組。候選執行器的 67 格輸出核對後，已依[顯示規格](docs/spec/014-mode13-scanout.md)接入目前原生版。

[目前屋頂、人物與柔邊陰影](workplace/native-shadows-v1/hd-rooftop.png)、[正常走近後的重疊陰影](workplace/native-shadow-overlap-v1/hd-paused.png)與[同狀態原貌](workplace/native-shadow-overlap-v1/original-paused.png)。陰影讀取原版位置與裁切，在人物之前合成；重疊取最大透明度。[陰影規格與驗證](docs/spec/012-hd-shadows.md)。

[目前屋頂、人物、介面與 HD 勝場](workplace/native-win-markers-v1/win-hd.png)、[同狀態原貌](workplace/native-win-markers-v1/win-original.png)與[切回 HD](workplace/native-win-markers-v1/win-restored.png)。正常操作取得首勝後，以原版鎖存勝場顯示高解析拇指圖示；七張擷取及原版分層已獨立核對，切回畫面逐點一致。來源與範圍見[勝場規格](docs/spec/011-hd-win-markers.md)。

[屋頂、角色與高解析介面](workplace/native-hud-frank-v2/hd-rooftop.png)、[法蘭克特效與實際扣血](workplace/native-hud-frank-v2/hd-hud-damage.png)、[同狀態原貌](workplace/native-hud-frank-v2/original-frank-effect-paused.png)與[HD](workplace/native-hud-frank-v2/hd-frank-effect-paused.png)。

Linux 原生版由正常標題進入斬對法蘭克雙打。生命條讀取原版逐格扣減的顯示值，計時讀取原版數字；沒有新增扣血或計時規則。特效與介面按原版繪製順序合成，獨立核對見[Linux 收據](workplace/native-hud-frank-v2/comparison.json)。

[空中踢擊](workplace/native-hud-frank-v2/hd-air-kick.png)、[雙人跳躍](workplace/native-hud-frank-v2/hd-jump.png)與[Windows 斬特效](workplace/windows-hud-v1/hd-effect-paused.png)。Windows 原生程式在 Wine 中另走正常流程，不能代替真機驗收。

[HD 對局中的手把與第五招設定](workplace/native-hud-frank-v2/native-settings.png)

兩人獨立的手把指派與角色快捷設定。圖中第一人選鳳凰第五招並將 R2 留空，第二人的配置保持獨立。擷取時沒有接實體手把，實體裝置驗收仍待進行。

勝場圖片出自[首勝與切換收據](workplace/native-win-markers-v1/receipt.json)，其餘 Linux 特效與設定圖片出自[介面基底收據](workplace/native-hud-frank-v2/receipt.json)。完整雙打基準另保存[結果報紙](workplace/native-match-v2/result-newspaper.png)與[返回標題](workplace/native-match-v2/after-result-return.png)，這兩個畫面仍是原貌。原始 PNG、分層與介面底層資料保留於本機工作區。

## 建置與執行

開發建置在 Docker 內執行，工作區需要已準備的 dosgolem 獨立來源及工具鏈，詳見[工作契約](AGENTS.md)和[桌面規格](docs/spec/005-native-desktop.md)。

儲存庫不附原版資料、HD 衍生美術、研究收據、dosgolem 私有來源或本機快取。`go.work.example` 記錄相對目錄配置，準備來源後複製為 `go.work`；原版匯入與來源快照工具為 `tools/prepare.py`，執行器補丁為 `tools/apply_runtime_patch.py`。現行收據中的 `workplace/` 連結僅供本機核對。

目前執行器副本也需要普通記憶體觀測及顯示 API。準備與安裝順序見[規格 007](docs/spec/007-memory-write-observation.md)、[規格 014](docs/spec/014-mode13-scanout.md)及[規格 015](docs/spec/015-native-scanout.md)；安裝工具只修改本專案的獨立副本。

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

角色與特效試作再加上 `-hd-characters workplace/hd-characters-phoenix-candidate-v1`，按「原貌／HD 角色」切換。此群組保留既有基底，包含五人的一般來源及三人的 WIN 入口。背景、兩名角色、來源與圖層全部符合才顯示 HD，缺動作或未知色盤時整張回退。新版仍接受舊版角色素材。此素材群組僅供本機研究，基底準備工具為 `tools/prepare_hd_characters.py`，勝利姿態登錄使用 `tools/prepare_victory_characters.py`，一般角色擴充使用 `tools/prepare_character_extension.py`。

含特效的新版群組也啟用高解析生命、計時、名字、玩家標記、勝場與地面陰影，來源驗證失敗時整張回退。舊版 1 素材保留原貌介面、特效與陰影。

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
- [HD 規格](docs/spec/003-hd-design.md)、[屋頂背景](docs/spec/006-rooftop-background.md)、[角色](docs/spec/008-hd-characters.md)、[特效](docs/spec/009-hd-effects.md)、[戰鬥介面](docs/spec/010-hd-battle-hud.md)、[勝場](docs/spec/011-hd-win-markers.md)、[陰影](docs/spec/012-hd-shadows.md)、[顯示映射](docs/spec/015-native-scanout.md)、[勝負文字](docs/spec/016-hd-victory-messages.md)與[勝利姿態](docs/spec/017-victory-pose-banks.md)。完整動畫、其他勝負分支及其餘角色／場景／畫面仍在製作。
- [青衫與 SP Moves 歷史保存](docs/game-history.md)。

自有程式與文件採 [RRSAL-1.0](LICENSE)，為 source-available 專案。此授權不涵蓋原版遊戲、外站原文與圖片或衍生美術；玩家須自備合法原版。專案與原版權利人沒有隸屬關係。內嵌中文字型另依 [SIL Open Font License](internal/desktop/assets/OFL.txt) 使用。
