# 快打至尊 Remastered：目前狀態

更新日期：2026-10-19。此檔為唯一現況，工作順序見 [WORKLIST.md](WORKLIST.md)，穩定規則與文件索引見 [AGENTS.md](AGENTS.md)。

## 已確認方向

- 參考 `/home/anr2/cht/zeliard` 的包裹與呈現方式。
- dosgolem 直接執行原版核心，本專案處理前端、手把與 HD 呈現。
- 使用者明確指定三平台原生桌面：Windows、macOS、Linux。玩家入口不使用 web；舊 HTTP／HTML 及瀏覽器收據只保留研究用途。
- 支援手把操作與 HD。原生背景、兩名角色的部分動作及素材登錄已接入，其他角色與畫面仍在製作。
- 使用者於 2026-10-19 回覆「ok B」，選定 HD 的 B「街機手繪」方向；只確認畫風，原版造型仍為修正依據。
- 使用者後續明確同意 HD 規格開工，首批為屋頂、斬、法蘭克與對戰介面；技術未知仍依規格閘門處理。
- 已授權逐角色快速出招，最多四格，R1／R2／L1／L2 預設對應絕招 1／2／3／4；五招角色可任選四招。兩名玩家分開保存設定，並規劃雙手把雙打。

## 唯一現況表

| 項目 | 狀態 | 最近證據與限制 |
|---|---|---|
| jsdos 下載 | 已完成 | 1,281,787 bytes；SHA-256 與來源物件檔名一致；ZIP CRC 通過 |
| 來源盤點 | 已完成 | 128 個檔案、130 個 ZIP 項目；逐檔 SHA-256；作弊資料隔離；原始副本唯讀使用 |
| 研究工具 | 已建立 | 安全盤點、IDA、逐次繪製與完整 RAM 分層；規格 007 的通用觀測介面限定 CONFORMED，獨立副本新增兩檔，共用來源未改 |
| dosgolem 啟動 | 已到第一場對戰 | 獨立副本補齊監督佇列 IF；正常鏈到標題、選角、Jaan 對 Frank；結算與返回尚未驗 |
| 原版輸入 | 雙人基本輸入與斬四招已驗 | 正常單打、雙打各 25 組基本輸入；雙打兩人的斬各四招均進入原版對應路徑；十二輪詢蓄力是已驗充分條件，未稱最短時間 |
| 前端與手把 | 三平台共用原生桌面已接核心 | Ebitengine 視窗、鍵鼠、標準手把指派、四格設定與來源所有權。最新 Linux 特效版兩次正常流程分別十五／十四項通過；Windows Wine 十四項是前一角色版，最新特效版尚待重驗。實體手把未驗 |
| HD | 屋頂、部分角色及 13 組特效已接原生 | study-v7 共 144 組正常來源槽及 13 組第二色盤特效。Linux 斬／法蘭克特效分別取得同狀態原貌、HD 與切回畫面，16／15 張擷取獨立重組通過。特效僅支援已驗未裁切幾何；完整動畫、HUD、其他角色及畫面未完成 |
| AI 研究 | 靜態載入與決策鏈已定位 | AIDATA 為 3×192 bytes，策略 byte 乘 16 進角色輸入序列；CHEAT 檔是 169-byte ASCII，未替換正常資料或宣稱實跑效果 |
| 歷史資料 | Markdown 與快照已保存 | 青衫及 SP Moves、十張原圖、八名角色招式比較及青衫另載三頭目；差異並列，來源雜湊可回查 |
| 原版版本與玩法 | 部分已觀察 | 包內 README 自述 v2.0，實跑帶第三方啟動殼；本包是目前基準，不能宣稱未修改原始發行版；控制方式仍在核對 |
| 平台與發布 | Windows／macOS／Linux 已定 | Linux amd64、Windows amd64、macOS Intel／Apple Silicon 已重建特效版，各保存實際編譯來源。最新版 Windows Wine 正常入口等待逾時，尚未通過 GUI；未作 Windows／macOS 真機、簽章或正式封包 |

## 固定輸入

來源頁：<https://dos.zczc.cz/games/%E5%BF%AB%E6%89%93%E8%87%B3%E5%B0%8A/>。

下載物件：<https://binary.dos.lol/aaec980cbef5679fda8274ed3549eccc97229be48221360427718a1e635f9b1d.zip>。

本地原始檔：[快打至尊.jsdos](快打至尊.jsdos)。SHA-256：

```text
aaec980cbef5679fda8274ed3549eccc97229be48221360427718a1e635f9b1d
```

以下結果由 Docker image `python:3.13.7-slim` 的 `zipfile` 與 `hashlib` 直接讀取包內 bytes。它們是檔案事實，不代表執行行為已驗證。

| 包內路徑 | 大小 bytes | SHA-256 |
|---|---:|---|
| `SF.EXE` | 60,702 | `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300` |
| `SF.COM` | 876 | `f194ff7cce7975aabff3f8ec5f92a8b0ca2db0368c33ed29aba7bd7b70f6392e` |
| `NOKEY.EXE` | 1,220 | `5757324e9e4cebeda2527b60c3f04fc8628c2a67aba6123282e57eea1a1e8b8c` |
| `PLAY.BAT` | 14 | `6e9475c883e145ceb9155c6a3b197b96d4bb34153e994fb0b1791ff521b8b6b4` |
| `FIGHT.CFG` | 224 | `d545fcd56015ed8bc61bcf01758aed45cc9008fb4bb7818056bd51881cead086` |
| `AIDATA.DAT` | 576 | `72b10b129c9f557a8b9beb0a400b5636ab690fec5af97b55672980283042f4d8` |
| `CHEAT/AIDATA.DAT` | 169 | `548a2266a585df51584d2d9902a3ab93e8832b43d54dc7d52344dbdc13839593` |

包內 `.jsdos/dosbox.conf` 的 `[autoexec]`：

```text
echo off
mount c .
c:
play.bat
```

`PLAY.BAT`：

```text
nokey /y
sf
```

本輪以 dosgolem 監督佇列執行 `NOKEY.EXE /y → SF.COM`，再由 `SF.COM` 自行 EXEC `SF.EXE`。這條明示鏈已走到標題、選角與首戰；未執行完整 COMMAND.COM，命令解析不宣稱完整相容。`SF.COM` 的全部修改行為及必要性仍未驗證。`.jsdos/dosbox.conf` 的 `svga_s3` 與 `cycles=auto` 是包裝設定；實際已觀察到模式 13h、320×200，正式遊戲速度與音訊仍未驗。

## 外部參考與能力邊界

- `/home/anr2/cht/zeliard/AGENTS.md`：本輪已讀。沿用工作契約，不沿用遊戲狀態、美術決定或 GitHub 授權。
- `/home/anr2/cht/dosgolem/README.md`、`CLAUDE.md`：已讀。基底 HEAD 為 `f79eab6db8c64a524a06535e53e5d32b0bbcf7c8`；接入時工作樹乾淨，1712 個追蹤檔已建立獨立副本並保存逐檔雜湊。共用來源未改動。
- 既有成功案例不能證明本作可執行。首次接入仍需正常啟動與固定預算探針。

## 待確認決策與下一步

六層原生角色已接入並驗證。下一步補齊斬與法蘭克的其餘 HD 姿態、特殊技、倒地及替代色盤，再擴充 HUD、其他角色、場景、標題／選角／結果畫面。使用者目前 Goal 為「完成快打至尊HD」，不能只以屋頂或首批兩人切片宣稱完成。完整回合、其他角色快捷及實體雙手把另續驗。規格 004、005、006、008 限定 READY，007 限定 CONFORMED；002、003 仍 DRAFT。

使用者指定的[說明書頁面](https://chiuinan.github.io/game/game/intro/ch/c51/sf.htm)及兩張圖片已存檔；其版本自述為 1.1。手把草案採西側面鍵拳、南側面鍵腳與八方向，Start 提議開啟前端暫停選單，避開說明書記載的 Esc 按住補血。這些是提案，仍待目前來源實測與使用者確認。

HD 採 B「街機手繪」，首批屋頂、斬、法蘭克及對戰介面已獲開工授權。屋頂背景與部分角色已接原生，可切回原貌。正式試作群組為 `hd-characters-study-v5`，十一張原始透明圖集共 121 張人物及特效圖，對應 117 組不同原始 bytes，包含兩名角色全部 144 個來源槽；PNG、提示詞與雜湊保存在 `hd-sprite-art-v1` 至 `v5`。登錄沿實際透明間隔，保留完整肢體而不修改 PNG。來源槽齊全不等於完整動畫已驗；特效仍由原貌點陣層繪製，尚未使用新增特效圖。C0h 同時翻轉、頂部裁切、受擊替代色盤及 HD HUD 待補。正式倍率、像素比例與預設模式尚未定版。

研究用 dosgolem 副本現有 1715 份來源，原有 1713 份 bytes 全不變；只在 oracle 新增普通 RAM 每次寫入觀測與合成程式驗證。前版 manifest 逐字保存在 `dosgolem-patched-manifest-v1.json`，新 manifest SHA-256 為 `6ad93295a80dbf590b88b64fab3acf1ffa6c31a32eb305e0a53936cb849f9732`。現行四個原生二進位已重建角色版，每個目標另有編譯前後來源及輸出雜湊收據，不能以舊背景版 GUI 收據冒充目前角色版驗收。

目前 dosgolem 的線性 320×200 API 未套用 CRTC 起點，兩種呈現均沿用相同完整快照。硬體捲動與震動畫面仍屬 oracle 限制，不宣稱實機 CRTC parity。HD 背景只在來源、色盤與相機範圍吻合時啟用，其他情況整張退回原貌。詳見規格 006。

快捷四格與雙手把已接本機操作入口，預設 R1／R2／L1／L2 對應 1／2／3／4，兩名玩家各自保存。斬的四招可送原版輸入，其他角色尚未驗證的快捷明示拒絕。投技仍需近身，沒有自動走近或改寫座標。實體裝置驗收仍待進行。

AI 可由外部策略表調整的靜態證據已足夠回答可行性；完整研究在 RESEARCH-LOG。短檔作弊效果的因果仍屬強推論，未作同狀態替換實驗，沒有新增 AI 行為。三平台已固定，公開方式與完整發行門檻尚未決定。

## 現行證據入口

### 最新特效開發切片

- [規格 009](docs/spec/009-hd-effects.md) 限定 READY。`effect-draw-v1`／`v2` 共 1015 次 blit、483 個完整畫格吻合；`effect-evidence-review.json` 另獨立重組 19 個保存畫格。
- `hd-characters-study-v7` 為版本 2 素材，13 張透明圖集對應 144 個正常來源槽與 13 個第二色盤特效鍵。新圖與提示詞保存在 `hd-effect-art-v1`／`v2`，原版及衍生素材不入 Git。
- `native-effects-v3/receipt.json` 十五項與 `native-frank-effects-v1/receipt.json` 十四項通過。兩次各由正常標題進入雙打，分開驗斬 R1 與法蘭克手動方向／拳特效，不代表法蘭克快捷已開放。
- 兩份 `comparison.json` 分別核對 16／15 張完整分層擷取；特效暫停切換的來源狀態一致，HD 切回逐點相同。斬 1035、法蘭克 5643 個原特效輸出像素已由 HD 替換。
- `effects-tests.log` 驗 19 個真實特效 fixture、第二色盤隔離、幾何拒絕、正常素材及設定；`effects-compatibility-tests.log` 驗舊版素材。`effect-core-compat-v1/receipt.json` 比較觀測開／關共 456 個邊界，原貌、狀態、色盤與步數相同。
- `desktop-build.json` 已重新核對四個特效版二進位的實際編譯來源與雜湊。`windows-effects-v1`、`windows-frank-effects-v1` 在正常入口等待逾時，尚未取得本版 Windows GUI 通過收據；不沿用舊版收據代替。
- 前版角色收據及原二進位另保留於 `native-actors-v6`。下列六層角色版、缺件回退與 native-character-audit 均屬前版證據，不能當成目前特效版的完整稽核。

### GitHub 儲存庫準備

本次上傳前再次嘗試依主機規則執行 `gh auth status`，提升權限仍遭自動核准政策拒絕。未重試受限環境的憑證判定，沒有建立或推送成功證據。最新程式仍先保存於獨立 Git 副本及本機 bundle；不可把預定 origin 當成已存在的儲存庫。

`native-actors-v1` 保存五層首版 Linux 收據及當版來源／二進位，僅供歷史回查。現行六層版以 `native-actors-v6`、`windows-actors-v6` 及 `native-actors-missing-v2` 為準，分別驗新角色動作、Windows 原生適配及缺件回退。

使用者已授權建立儲存庫並上傳成果。預定名稱為 `wicanr2/superfighter-remastered`，公開方式未定案，先採私人設定。遠端 API 目前連線失敗，未取得建立成功證據，不宣稱儲存庫已存在。主機升權呼叫亦被環境拒絕，受限環境的 auth 訊息不能當作主機憑證失效的結論。

工作根的 `.git` 在本次環境不可寫，已在 `/tmp/kdzz-superfighter-publish` 準備獨立 Git 提交副本，不改受保護的 metadata。副本只收程式、規格、歷史整理、RRSAL-1.0、中文字型與不含原版畫面的手把設定截圖。原版包、workplace、衍生 HD 美術與二進位皆排除；遠端建立及 push 尚待完成。

首份提交為 `8365aeb91f79032227ff3c4b5cc8daed5fc3e4bd`，共 60 檔；完整 Git 備份為 `workplace/github-initial-8365aeb.bundle`，已通過 `git bundle verify`。可在連線與權限恢復後從該副本推送 main；origin 只保存預定 URL，不表示遠端已建立。後續 HD 變更仍以目前工作根為準。

角色研究的程式、規格與文件已追加至提交 `00dfe7e28206e8b7947b316c7c82c8282873f84a`，副本共 69 個追蹤檔。完整備份為 `workplace/github-hd-study-00dfe7e.bundle`，已驗證；48 個 HD 姿態及原版分層資料維持本機排除，GitHub 遠端狀態未改。

- [RESEARCH-LOG.md](RESEARCH-LOG.md)：啟動鏈、來源差異、輸入候選與重生方式。
- [VERIFICATION-MATRIX.md](VERIFICATION-MATRIX.md)：已驗範圍與未驗項。
- [規格 001](docs/spec/001-queued-entry-interrupts.md)：監督佇列入口修正，限定範圍 CONFORMED。
- [手把草案](docs/spec/002-gamepad-design.md)、[HD 草案](docs/spec/003-hd-design.md)：說明書導出的設計，均為 DRAFT。
- [原生桌面入口](README.md)：`bash tools/build_desktop.sh` 產生三平台中間二進位，玩家以 `-data` 指定原版資料。此共用主機的建置／GUI 驗證均在 Docker。
- [桌面規格 005](docs/spec/005-native-desktop.md)：限定 READY，明定原生視窗、設定、標準手把與三平台界線。
- `workplace/native-actors-v6/receipt.json`、`windows-actors-v6/receipt.json`：目前 Linux 與 Windows PE 各十四項正常入口、屋頂六層 HD、行走、雙跳、新 slot 25 空中踢擊、slot 56 退步、兩人獨立放開、R1、暫停、設定、保存重啟及失焦通過；README 截圖出自 Linux 此輪。Wine 不能代替 Windows 真機。
- 兩目錄的 `comparison.json`：各十三張原生六層擷取逐點重組回原版；各平台內暫停三張原始色號、色盤與定位相同。Linux 範例的 47,978 個原角色輸出像素已替換、489,092 個背景像素改變、35,451 個最後原貌層像素保留。HD 切回遊戲區逐點相同，不宣稱兩平台即時操作是跨平台同狀態。
- `workplace/native-actors-missing-v2/receipt.json` 與 `comparison.json`：目前 Linux 使用舊版缺件素材，十三項正常流程通過；缺件時整個 960×600 遊戲區與當格原貌逐點相同。`native-actors-fallback-v1` 另保存六層版正常道場九項回退。
- `workplace/windows-shift-v1/receipt.json`：只讀 Win32 探針確認左右 Shift 可獨立取得。限定原因與修復契約見規格 005；修復後 Windows 正常雙打已驗獨立放開。
- `workplace/desktop-build.json`：四個角色版二進位 SHA-256、ELF／PE／Mach-O 檔頭、固定依賴與字型來源；每個 `workplace/bin/*.build.json` 保存實際編譯前後一致的來源及輸出雜湊。
- `workplace/native-character-checks.log`：目前角色版的 `go test -count=1 -p 1 ./...`、`go vet -p 1 ./...` 通過，載入真實原版分層與 144 槽素材。`native-actors-v1/source` 已用獨立 module 隔離，避免其部分存檔誤當正式套件。
- `workplace/native-character-audit.json`：目前四個實際編譯收據、十四／十四／十三項 GUI、原始 128 檔、1715 份 dosgolem 及 144 槽群組核對；不包含完整 HD 或實體平台驗收。
- `workplace/hd-checks.log`：原生背景切片當輪的 `go test -count=1 -p 1 ./...` 與 `go vet` 通過，HD 測試載入 16 張原始畫格。
- `workplace/hd-audit.json`：背景版來源、二進位、GUI 收據與原始資料核對；已明確辨識二進位仍使用前版來源快照。它不驗角色試作，角色研究另以 sprite-study-audit 為準。
- [角色分層規格 008](docs/spec/008-hd-characters.md)：限定 READY，已接六層原生呈現。早期 `sprite-draw-v1`／`sprite-layers-v1` 各 1,432 次繪製吻合；後者 716 個五層歷史畫格全部逐點重組相同，與現在六層收據分開列明。
- [觀測規格 007](docs/spec/007-memory-write-observation.md)：限定 CONFORMED；`workplace/write-observer-test.jsonl` 驗同值重寫、指令起點、獨立取消及完整機器狀態不變。沒有改 CPU 或原版資料。
- `workplace/hd-sprite-art-v1/manifest.json`：四張 1448×1086 透明 PNG，共 48 姿態；提示詞及參考表逐組保存，使用內建 image_gen，僅留本機。
- `workplace/hd-actor-preview-v3/receipt.json`：16 個保存狀態、15 個雙人 HD 比較，缺斬 slot 56 時明示缺件。待機、蹲與跳圖已目視；未作原生完整動畫驗收。
- `workplace/sprite-study-audit.json`：獨立重組 16 個分層 fixture、來源不變、兩個新增觀測檔、48 個透明姿態、索引與回填核對通過。
- [即時輸入規格 004](docs/spec/004-live-input-slice.md)：限定 READY。基本輸入收據在 `workplace/input-single-v2/`、`input-versus-v2/`；兩人四招收據在 `workplace/quick-versus-v3/`，後兩者附執行前 provenance。
- `workplace/live-http-v4/receipt.json`：8 項通過，正常雙打入口、雙人拳腳、來源所有權、R1、單人斷線取消快捷、暫停、失聯清理與非法輸入拒絕；API 檢查，不是硬體驗收。
- `workplace/browser-live-v3/receipt.json`：Chromium 12 項通過，正常雙打入口、雙支合成標準手把、設定輸入隔離、R1 不連發、斷線、窄畫面、設定重載及靜態 HD 示範。沒有實體手把或動態 HD 對拍。
- `workplace/live-build.json`、`live-audit.json`：前輪 HTTP 研究入口的來源、二進位與稽核，不能作原生驗收。
- `workplace/sprite-source-v1/evidence.json`：斬／法蘭克各 72 槽圖集，61／57 個不同圖像位置。後續 IDA 與動態證據已確認本輪取樣的完整圖像 bytes；完整姿態覆蓋及錨點仍未完成。
- [背景規格 006](docs/spec/006-rooftop-background.md)：來源位址、完整畫格、背景合成及回退契約；`hd-frame-single-v2`／`hd-frame-versus-v2` 各 124 畫格，`hd-rooftop-study/manifest.json` 保存本機素材與雜湊。
- [互動配置稿](tools/gamepad-preview.html)：可獨立開啟；支援時可讀瀏覽器標準手把，亦可用方向鍵、J、K 預覽，沒有接入遊戲。
- [四招設定資料](tools/quick-moves.js)：四格驗證、逐角色資料、兩人獨立設定、文字鏡像與按下邊緣；即時入口只啟用已驗的斬四招。
- [HD 分層預覽](tools/hd-preview.html)：背景、兩張透明待機圖與展示介面；素材、尺寸、alpha、雜湊及提示詞見 `workplace/hd-layers/`。
- [遊戲資料保存](docs/game-history.md)：兩站來源、原文快照、原圖與招式差異；快照位於 `workplace/manual-reference/` 及 `workplace/spmoves-reference/`。
- [AI 研究](RESEARCH-LOG.md)：原始位址與證據等級；資料統計見 `workplace/ai-data-evidence.json`，IDA 匯出為 `workplace/ida-ai-v3.json`。
- [A 忠實精修](workplace/design/hd-a-faithful.png)、[B 街機手繪](workplace/design/hd-b-painted.png)：imagegen 概念稿，提示詞見 `workplace/design/prompts.json`，來源及雜湊見 `workplace/design/manifest.json`。
- [標題畫面](workplace/probe-startup-if-40m/screen.png)、[選角畫面](workplace/probe-single-click-60m/screen.png)：由 dosgolem 色號及色盤生成，僅留本機。
- [正常首戰](workplace/probe-fight-baseline-190m/screen.png)、[掃描碼按住／放開後](workplace/probe-fight-held-190m/screen.png)、[原版設定頁](workplace/probe-keyboard-settings-65m/screen.png)：已目視；不是手把或 HD 驗收。
- [啟動研究稽核](workplace/research-audit.json)：來源、補丁與 17 份啟動／輸入收據。
- [前輪稽核](workplace/implementation-audit.json)：來源快照及圖片、四招資料行為、文件索引與連結、素材尺寸及 alpha、IDA 輸出與擁有權通過；不涵蓋後續即時入口。

已有原生桌面切片與三平台中間二進位；沒有正式安裝包、macOS 真機收據、完整 HD、遠端或交付包。原始 jsdos 與共用 dosgolem 未改動。
