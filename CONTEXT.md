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
| dosgolem 啟動 | 原生雙打基準已走完整比賽與返回 | 普通選單、移動與拳擊完成兩次擊倒、結果報紙及返回標題，八張擷取通過。離開對戰後快照清空；此基準二進位另存，勝場擴充另驗首勝 |
| 原版輸入 | 雙人基本輸入與斬四招已驗 | 正常單打、雙打各 25 組基本輸入；雙打兩人的斬各四招均進入原版對應路徑；十二輪詢蓄力是已驗充分條件，未稱最短時間 |
| 前端與手把 | 三平台共用原生桌面已接核心 | 目前顯示修正版 Linux 十七項正常操作通過；Linux／Wine 開場各七項。含兩人獨立放開、特效扣血、設定重啟與失焦；實體手把未驗 |
| HD | 屋頂、部分角色、13 組特效、介面／勝場、柔邊陰影與開場字圖已接原生 | Linux／Wine 第一回合各十張開場擷取、Linux 一般對戰十五張；部分窗口與切回逐點一致。勝負訊息、完整動畫、其他角色及畫面未完成 |
| 顯示起點修正 | 已接原生，015 限定 CONFORMED | Linux／Wine 各十張開場、Linux 對戰十五張與舊素材十一張全部核對；起點第 7／11／12 列及可見尾端逐格正確，原貌與 HD 共用映射 |
| AI 研究 | 靜態載入與決策鏈已定位 | AIDATA 為 3×192 bytes，策略 byte 乘 16 進角色輸入序列；CHEAT 檔是 169-byte ASCII，未替換正常資料或宣稱實跑效果 |
| 歷史資料 | Markdown 與快照已保存 | 青衫及 SP Moves、十張原圖、八名角色招式比較及青衫另載三頭目；差異並列，來源雜湊可回查 |
| 原版版本與玩法 | 部分已觀察 | 包內 README 自述 v2.0，實跑帶第三方啟動殼；本包是目前基準，不能宣稱未修改原始發行版；控制方式仍在核對 |
| 平台與發布 | Windows／macOS／Linux 已定 | 四個顯示修正版二進位已重建；Linux 一般對戰十七項、開場 Linux／Wine 各七項。舊素材回退另驗；未作 Windows／macOS 真機、簽章或正式封包；Wine 不代替真機 |

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

本輪以 dosgolem 監督佇列執行 `NOKEY.EXE /y → SF.COM`，再由 `SF.COM` 自行 EXEC `SF.EXE`。這條明示鏈已由原生雙打基準走到結果及返回標題；未執行完整 COMMAND.COM，命令解析不宣稱完整相容。`SF.COM` 的全部修改行為及必要性仍未驗證。`.jsdos/dosbox.conf` 的 `svga_s3` 與 `cycles=auto` 是包裝設定；實際已觀察到模式 13h、320×200，正式遊戲速度與音訊仍未驗。

## 外部參考與能力邊界

- `/home/anr2/cht/zeliard/AGENTS.md`：本輪已讀。沿用工作契約，不沿用遊戲狀態、美術決定或 GitHub 授權。
- `/home/anr2/cht/dosgolem/README.md`、`CLAUDE.md`：已讀。基底 HEAD 為 `f79eab6db8c64a524a06535e53e5d32b0bbcf7c8`；接入時工作樹乾淨，1712 個追蹤檔已建立獨立副本並保存逐檔雜湊。共用來源未改動。
- 既有成功案例不能證明本作可執行。首次接入仍需正常啟動與固定預算探針。

## 待確認決策與下一步

屋頂、兩人已驗動作／特效及生命、計時、名字、勝場、地面陰影、開場 ROUND／FIGHT 已接原生。顯示起點已依規格 015 修正，下一步處理中央勝負訊息，再擴充其餘動作、替代色盤、角色、場景及標題／選角／結果。使用者 Goal 仍是「完成快打至尊HD」，不能以首批切片宣稱完成。原生雙打基準已走完整比賽及返回，其他模式、其他角色快捷及實體雙手把另驗。規格 004、005、006、008、009、011 限定 READY，007、010、012、013、014、015 限定 CONFORMED；002、003 仍 DRAFT。

使用者指定的[說明書頁面](https://chiuinan.github.io/game/game/intro/ch/c51/sf.htm)及兩張圖片已存檔，版本自述為 1.1。原生入口目前採西側面鍵拳、南側面鍵腳與八方向；Start／Esc 暫停前端，沒有把 Esc 送原版觸發說明書記載的補血。鍵鼠正常路徑已驗，實體手把另驗；完整手把規格仍有未驗部分。

HD 採 B「街機手繪」，首批屋頂、斬、法蘭克及介面已獲開工授權。現行群組為 `hd-characters-study-v7`，十三張透明圖集對應 144 個正常色盤來源槽及 13 個第二色盤特效鍵；基本槽共有 117 組不同原始 bytes。原始 PNG、提示詞與雜湊分別在 `hd-sprite-art-v1` 至 `v5`、`hd-effect-art-v1`／`v2`。登錄保留原 PNG bytes。來源槽齊全不等於完整動畫已驗；C0h 同時翻轉、頂部裁切、受擊替代色盤及剩餘介面待補。正式倍率、像素比例與預設模式尚未定版。

目前 dosgolem 獨立副本有 1719 份來源，前版 1715 份 bytes 不變，新增四份已驗顯示 API 與測試。舊 manifest 保存於 `dosgolem-patched-manifest-v2.json`，現行身分見 `dosgolem-patched-manifest.json` 與 `native-display-audit.json`。四個二進位的實際編譯身分見 `bin/*.build.json`，目前原生證據以 native-display 各收據為準。舊陰影、勝場、開場及完整比賽基準保留各自版本身分。

舊 Screen／Indexed／RGB API 仍保留線性 320×200 契約；桌面使用另外的只讀顯示快照，同格保存原圖層、完整尾端與實際可見色號。原貌與 HD 全部圖層共用投影，開場 320×192 居中且維持每像素 3×3；跳躍與踢擊實測起點第 7／11／12 列。來源或尾列不符整格原貌。這是限定硬體規格近似，正式像素比例、實機時序與完整 HD 仍未驗。

快捷四格與雙手把已接本機操作入口，預設 R1／R2／L1／L2 對應 1／2／3／4，兩名玩家各自保存。斬的四招可送原版輸入，其他角色尚未驗證的快捷明示拒絕。投技仍需近身，沒有自動走近或改寫座標。實體裝置驗收仍待進行。

AI 可由外部策略表調整的靜態證據已足夠回答可行性；完整研究在 RESEARCH-LOG。短檔作弊效果的因果仍屬強推論，未作同狀態替換實驗，沒有新增 AI 行為。三平台已固定，公開方式與完整發行門檻尚未決定。

## 現行證據入口

### 目前原生顯示映射

- [規格 015](docs/spec/015-native-scanout.md) 對實測顯示配置限定 CONFORMED。`display-core-compat-v1` 的 1,508 個開／關邊界狀態、舊原貌、即時 RGB 及原圖層相同；66 個完整開場快照由原資料與真實 VRAM 尾端獨立重組。
- `native-display-opening-v2`／`windows-display-opening-v1` 各七項、十張擷取與六張 GPU 字圖核對通過。開場完整顯示原第 12 至 203 列，頂端暫存資料不再露出，底四列保留；原貌／HD／切回的來源及畫面逐點一致。
- `native-display-battle-v2` 十七項、十五張擷取及十二張陰影合成通過，含兩人攻擊、移動、跳躍／踢擊、特效扣血、設定重啟與失焦。正常跳躍及踢擊另見第 11、7 列起點，按每格 CRTC 核對。
- `native-display-legacy-v2` 十三項、十一張擷取驗舊版素材及缺件整張原貌。實體手把及其他角色快捷仍未驗。
- `display-checks-v1.log` 保存全套 Go 測試及 go vet；`display-runtime-installed-tests.log` 保存安裝後 API、17 個拒絕條件、保存還原與只讀複本測試。四個 Linux／Windows／macOS Intel／Apple Silicon 二進位已重建，`desktop-build.json` 與 `bin/*.build.json` 綁定實際來源及輸出。
- 稽核入口為 [tools/audit_native_scanout.py](tools/audit_native_scanout.py)，結果 `workplace/native-display-audit.json` 綁定 128 原檔、1719 份來源、四份實際編譯與 46 張具名映射擷取。前版 9623266 與 30 份編譯輸入保存在 `native-rounds-v1/build-baseline`。舊稽核保留當版身分。
- [目前 HD 開場](workplace/native-display-opening-v2/round-hd.png)已目視確認。自有來源備份為 `workplace/github-native-display.bundle`，逐檔身分見 `workplace/github-native-display-source.json`。原版、衍生美術、收據與二進位不入 Git；GitHub 尚未建立或推送。
- 完整 HD、後續回合／勝負訊息、其他角色與場景、完整動作、其他模式、實體平台與雙手把、音訊、速度及正式封包仍未完成。正式倍率與預設模式仍未定案。

### 顯示候選基底

以下保留接入前的候選與 9623266 身分，現行以規格 015 收據為準。

- [規格 014](docs/spec/014-mode13-scanout.md) 對候選 API 限定 READY，玩家主入口未修正。原版埠設定與 VGA 公開契約確認起點 3,840 bytes、列距 320、可見高度 192，最後一點為相對 A0000 的 65,279。`display-ports-v1` 保存 67 格與全部埠，`reference.json` 為獨立硬體規格近似；[原版重組預覽](workplace/display-ports-v1/display-010.scanout.png) 不當作原生 HD 截圖。
- `display-runtime-study-v1` 在研究目錄複製正式 1715 檔，原檔逐字不變，另加四份機器／公開 API 與測試，共 1719 檔。正式來源與 `go.work` 未動；候選的 workspace 與完整檔案身分在該研究目錄。
- 候選測試及 go vet 通過，包含完整尾列、不同起點與列距、兩種保存還原、複本不共用，以及 17 種未知映射拒絕。`linear-scanout-api-v2` 由正常選單重走 67 格，逐點等於獨立顯示重組，舊 API 與呼叫前後原版狀態不變。67 格最後四列亦等於原始背景，後續仍須逐格檢查。
- 稽核入口 `tools/audit_linear_scanout.py`／`workplace/linear-scanout-audit.json` 明示原生未接線。原生下一步須將原貌、HD 全部圖層與四列尾端一起映射，不能只裁掉頂端。現行 9623266 四個二進位與 30 份編譯輸入已保存於 `native-rounds-v1/build-baseline`，既有 GUI 收據仍屬目前未修正的顯示版本。
- 候選工具與文件的自有來源備份為 `workplace/github-display-candidate.bundle`，提交與逐檔身分記於 `workplace/github-display-candidate-source.json`。候選來源副本、VRAM、原版預覽及現行二進位均留本機，不加入 Git 或遠端。

### 顯示修正前的原生開場基底

以下為修正前的 9623266 來源及視窗收據；目前程式已依規格 015 套用顯示映射。

- [規格 013](docs/spec/013-hd-round-messages.md) 限定第一回合。IDA 9.4 定位原訊息、數字、橫向窗口與部分背景；`round-draw-v3` 的 66 次訊息、66 次部分背景與 66 次完整常式返回，全部由原檔獨立重組。階段 1 最末格的頂列 FIGHT 暫存拷貝另驗，沒有把 helper 結束當整個常式完成。
- `round-core-compat-v1` 的 1,508 個開／關觀測邊界，狀態、原貌與實時 RGB 相同；保存全部 66 格分層快照，四階段與十二種窗口齊全。原檔、HUD、陰影與開場訊息可獨立重組；正式對戰後訊息與保留列 metadata 清空。其他回合索引只有靜態來源組合，沒有正常動態驗收。
- `native-rounds-v1`／`windows-rounds-v1` 各七項、十張具名擷取；部分 ROUND 窗口、完整 ROUND、FIGHT 與正式對戰清除均通過。每側六張 GPU 字圖擷取核對窗口外完全不變，三組暫停切換的來源與恢復畫面逐點相同。Wine 不代替 Windows 真機。
- 目前 Linux 一般對戰為 `native-round-battle-v1` 十七項、十五張具名擷取，另核對十二張陰影合成；舊版 1 與缺件整張原貌由 `native-round-legacy-v1` 另驗。全套測試與 go vet 使用 `round-checks-v3`，沒有跳過；最初跨平台 image 預設關閉 cgo 的編譯失敗屬環境，改用既有 Linux image 與明示 cgo 後乾淨重跑。
- 四份實際編譯來源及二進位見 `bin/*.build.json`／`desktop-build.json`，目前來源稽核入口為 `tools/audit_native_rounds.py`。陰影基底的四個二進位、26 個精確編譯輸入及舊稽核保存在 `native-shadows-v1/build-baseline`，綁定 `d04670d`；舊收據保留版本身分。
- 開場背景不覆寫頂端十二列；目前原貌與 HD 都沿 oracle 線性 A0000 契約保留此內容，因此開場頂部仍可見資料列。這是實際可見的 oracle 限制，尚未處理，不能以本切片宣稱完整 HD。
- 自有來源保存於獨立 Git 副本與 `workplace/github-native-rounds.bundle`，提交及逐檔雜湊見 `workplace/github-native-rounds-source.json`。原版、衍生美術、研究收據與二進位繼續排除，GitHub 沒有建立或推送。

### 陰影基底

以下陰影版收據保留 `d04670d` 的版本身分，目前版驗收以開場切片為準。

- [規格 012](docs/spec/012-hd-shadows.md) 經來源審查升 READY 後接入，驗證與稽核後限定 CONFORMED。772 次原版繪製與 19 個獨立重組樣本吻合，保留 5,002 次同值寫入。負 X 裁切及整圖跳過只有靜態邊界測試，不冒充正常樣本。
- `shadow-core-compat-v1` 的 456 個邊界在開／關新觀測時原貌、色盤、角色、狀態及步數相同，取得 448 個完整陰影快照，保存 24 個可重組的雙人原版畫格。`shadow-checks-v1` 全套測試及 go vet 通過，沒有跳過。
- `native-shadows-v1`／`windows-shadows-v1` 各十七項通過，各十五張具名擷取完整重組；各十二張高解析陰影擷取另核對原生 alpha 與 GPU 黑色合成。RGBA8 合成量化區間與切回 HD 逐點一致分開驗，沒有放寬切換比較。
- `native-shadow-overlap-v1` 普通走近取得重疊，七張具名擷取、五張陰影合成核對通過，其中三張確有透明度重疊。`native-shadow-legacy-v1` 十三項及十一張具名擷取驗舊版 1 與缺件整張原貌，沒有混入新版柔邊陰影。
- `shadow-match-core-v1` 以普通輸入走完兩次擊倒及第二回合，當時陰影快照完整；結果報紙階段快照清空。此為目前核心的生命週期證據，原生返回標題仍保留下一節基準的版本身分。
- 四個目前二進位與編譯來源由 `desktop-build.json` 及 `bin/*.build.json` 記錄。勝場版的四個二進位、精確來源、舊稽核已保存於 `native-win-markers-v1/build-baseline`，不把舊收據當目前版。最新稽核入口為 `tools/audit_native_shadows.py`，輸出 `native-shadows-audit.json`。
- 自有來源續存獨立 Git 副本與 `workplace/github-native-shadows.bundle`，備份身分及逐檔雜湊見 `workplace/github-native-shadows-source.json`。原版、衍生美術與二進位不納入提交；GitHub 仍未建立或推送。

### 勝場與完整比賽基底

以下保留勝場版及完整比賽基準的來源與限制，最新陰影版以本節前方的現況為準。

- [規格 011](docs/spec/011-hd-win-markers.md) 限定 READY。獨立來源核對 33 個 HUD fixture、93 點非零拇指圖像及兩側各兩格靜態位置。原生向量重繪按鎖存的 DisplayWins 顯示，保留完整原版圖層；尚未顯示的勝場不移除原貌像素。右側及第二圖示未作正常 GUI 勝場驗收。
- `native-win-markers-v1` 使用目前 Linux 勝場版，普通移動與拳擊取得第一勝，七張擷取逐點重組原版六層。三張暫停切換的核心、色號、色盤、完整快照及即時 RGB 相同，恢復 HD 的遊戲區逐點一致；勝場區確有 HD 替換。全套測試與 go vet 見 `win-markers-checks-v2`，33 個 HUD／19 個特效 fixture 沒有跳過；新增未獲勝區域的拒絕檢查見 `win-marker-coverage-v1`。
- `native-match-v2` 使用另存的擷取診斷基準，普通選單、移動與拳擊走完兩次擊倒、結果報紙及返回標題，八張擷取通過。對戰六張完整原版分層重組一致；結果／標題整個 960×600 區域等於即時原貌，對戰快照清空。其四個二進位及精確編譯輸入保存在 `native-match-v2/build-baseline`，與目前勝場版分開。兩版 gameplay core 來源相同，僅三份前端／HD 呈現檔改變。
- 原生初次 `native-match-v1` 的 900 秒期限不足，失敗與四張部分擷取保留。1800 秒重跑已通過；部分檢查須指定 `--partial`，另寫 comparison-partial.json，不能代替完整比賽收據。直接 Docker 指令目前可用，先前複合主機指令的 socket 拒絕不再列為整個 Docker 工具鏈受阻。
- 陰影已由原檔及 IDA 9.4 追到載入、兩人位置、固定第 178 列與透明繪製端，證據在 `ida-shadow-v1/v2.json`、`sf-shadow-v1/v2.i64` 及 RESEARCH-LOG。尚未作 dosgolem 逐寫對拍或 HD 替換，不宣稱陰影完成。
- 目前四份編譯來源、原始資料、首勝與歷史完整比賽的核對入口為 `tools/audit_native_wins.py`，輸出 `workplace/native-win-markers-audit.json`。自有來源續存於獨立 Git 副本及 `workplace/github-native-wins.bundle`，逐檔來源與備份身分見 `workplace/github-native-wins-source.json`。原版、衍生美術與二進位排除，遠端仍未建立或推送。

### 介面切片基底

下列收據保存勝場擴充之前的版本；四個基底二進位及來源身分另存於 `native-hud-frank-v2`。不能把舊稽核對四份二進位的結果外推到目前勝場版。

- [規格 010](docs/spec/010-hd-battle-hud.md) 限定生命、計時、名字與玩家標記。`hud-draw-v3` 正常雙打取得 1176 次逐點吻合的介面繪製，普通拳擊至擊倒、第二回合；`hud-reference-v5.json` 的最新 33 個 fixture 由原檔及鎖存欄位獨立重組，`hud-evidence-review.json` 通過。
- `native-hud-frank-v2`、`windows-hud-v1`、`windows-hud-frank-v1` 各十六項正常 GUI 通過，各十六張擷取完整重組及切換核對。法蘭克兩案例包含實際扣血；三個暫停案例的來源狀態與恢復後 HD 畫面相同。Linux 取樣的 27,279 個原 HUD 輸出像素已替換。
- `native-hud-legacy-v1` 十三項通過，舊版 1 群組保持原貌介面；缺件時整個 960×600 遊戲區逐點等於原版。
- `hud-core-compat-v1` 比較開／關特效與 HUD 觀測的 456 個邊界，原貌、色盤、角色、狀態與步數相同，取得 448 個完整 HUD 快照。`hud-checks-v2.log` 的全套測試及 go vet 通過，實際載入 33 個 HUD 與 19 個特效 fixture，沒有跳過。
- `desktop-build.json` 及四份 `bin/*.build.json` 核對目前介面版編譯來源、雜湊及 ELF／PE／兩種 Mach-O。`native-hud-audit.json` 核對原始 128 檔、1715 份來源、157 個素材鍵、三個十六項 GUI 與十三項舊素材回退；不代表完整 HD 或實體平台驗收。
- 早期特效二進位與精確編譯輸入保存在 `native-effects-v4`；首版介面 prototype 保存在 `native-hud-frank-v1`。前者供 GPU 取樣修正回查，後者保留玩家標記殘留與擷取側檔遺漏的歷史，不能當作目前介面驗收。

### 特效基底與來源研究

- [規格 009](docs/spec/009-hd-effects.md) 限定 READY。`effect-draw-v1`／`v2` 共 1015 次 blit、483 個完整畫格吻合；`effect-evidence-review.json` 另獨立重組 19 個保存畫格。
- `hd-characters-study-v7` 為版本 2 素材，13 張透明圖集對應 144 個正常來源槽與 13 個第二色盤特效鍵。新圖與提示詞保存在 `hd-effect-art-v1`／`v2`，原版及衍生素材不入 Git。
- `native-effects-v3/receipt.json` 十五項與 `native-frank-effects-v1/receipt.json` 十四項通過。兩次各由正常標題進入雙打，分開驗斬 R1 與法蘭克手動方向／拳特效，不代表法蘭克快捷已開放。
- 兩份 `comparison.json` 分別核對 16／15 張完整分層擷取；特效暫停切換的來源狀態一致，HD 切回逐點相同。斬 1035、法蘭克 5643 個原特效輸出像素已由 HD 替換。
- `effects-tests.log` 驗 19 個真實特效 fixture、第二色盤隔離、幾何拒絕、正常素材及設定；`effects-compatibility-tests.log` 驗舊版素材。`effect-core-compat-v1/receipt.json` 比較觀測開／關共 456 個邊界，原貌、狀態、色盤與步數相同。
- `windows-effects-v1`、`windows-frank-effects-v1` 保留初次等待逾時；單獨重跑後，v2 的畫面比對發現取樣末位差異。改用獨立 GPU 紋理後，`windows-effects-v3`／`windows-frank-effects-v3` 的原貌／HD 切換逐點相同。現行 GUI 已由上方介面版收據取代。
- 前版角色收據及原二進位另保留於 `native-actors-v6`。下列六層角色版、缺件回退與 native-character-audit 均屬前版證據，不能當成目前特效版的完整稽核。

### GitHub 儲存庫準備

本次使用者再次要求建立與上傳。受限環境的 `gh auth status` 回報登入失敗，但主機權限檢查遭環境政策拒絕，尚不能確認主機憑證失效。沒有建立或推送成功證據，不可把預定 origin 當成已存在的儲存庫。

上傳副本保留 `main` 的顯示修正驗證版本；後續勝負訊息與勝利姿態的開發中來源保存於 `wip/victory-hd`，尚未完成整合驗證。兩個分支的完整本機備份為 `workplace/github-upload-latest.bundle`，逐檔身分與分支提交見 `workplace/github-upload-latest-source.json`。原版、HD 美術、研究輸入及二進位繼續排除。

`native-actors-v1` 保存五層首版來源／二進位，`native-actors-v6` 等保存後續六層版；均為歷史，現行收據以本檔「最新原生介面切片」為準。

使用者已授權建立儲存庫並上傳成果。預定名稱為 `wicanr2/superfighter-remastered`，公開方式未定案，先採私人設定。遠端 API 目前連線失敗，未取得建立成功證據，不宣稱儲存庫已存在。主機升權呼叫亦被環境拒絕，受限環境的 auth 訊息不能當作主機憑證失效的結論。

工作根的 `.git` 在本次環境不可寫，已在 `/tmp/kdzz-superfighter-publish` 準備獨立 Git 提交副本，不改受保護的 metadata。副本只收程式、規格、歷史整理、RRSAL-1.0、中文字型與不含原版畫面的手把設定截圖。原版包、workplace、衍生 HD 美術與二進位皆排除；遠端建立及 push 尚待完成。

首份提交為 `8365aeb91f79032227ff3c4b5cc8daed5fc3e4bd`，共 60 檔；完整 Git 備份為 `workplace/github-initial-8365aeb.bundle`，已通過 `git bundle verify`。可在連線與權限恢復後從該副本推送 main；origin 只保存預定 URL，不表示遠端已建立。後續 HD 變更仍以目前工作根為準。

角色研究早期備份為 `github-hd-study-00dfe7e.bundle`；特效提交為 `3807ee3`，備份 `github-native-effects.bundle`。介面基底、勝場與目前陰影來源分別保存於 `workplace/github-native-hud.bundle`、`github-native-wins.bundle`、`github-native-shadows.bundle`；原版、衍生美術及二進位持續排除，遠端仍未建立或推送。

### 穩定文件與早期切片

下列 native-actors、native-character-audit、hd-audit 及瀏覽器收據保留當版結果。不能將其「當時通過」外推為目前勝場版驗收；目前四個二進位的入口以「最新原生勝場與正常流程」為準。

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
