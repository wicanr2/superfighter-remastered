# 036：三平台封包與本機推廣片

狀態：首版限定 CONFORMED，已發布並核對遠端資產。使用者已要求發布 Release，且明確指定「release 不包含遊戲，但 local 完整版要」。影片只留本機，必須用原版音樂，另評估音樂及語音 HD。

## 範圍與版號

首版用 `v.0.1.0-20261020`，日期依 Asia/Taipei；使用者授權目前可用功能的三平台封包，沒有將部分 HD 改稱全部完成。正式 tag、程式版本、封包、manifest 與 Release 標題皆採相同完整版號；查無既有 tag 才可建立，不覆寫發布。

使用者已確認「首版先發布已驗功能，明列其他角色快捷限制」。實際快捷只開已驗斬四招，其他角色可保存四格配置，輸入明示拒絕。此範圍足以進入本次首版發布，不等待所有角色快捷或完整 HD。

交付根為 `dist-all/<版本>/`，職責依 `/home/anr2/.codex/knowledge-base/local/retro-remake-dist-all-output.md`。Linux amd64、Windows amd64、macOS Intel 與 Apple Silicon 共四份。

macOS 的 CFBundleVersion／CFBundleShortVersionString 依 [Apple 平台格式](https://developer.apple.com/documentation/BundleResources/Information-Property-List/CFBundleVersion)使用三段整數；完整發行版號另存 CFBundleGetInfoString／SuperfighterReleaseVersion。程式視窗、`-version`、manifest、VERSION、tag 與封包仍全用相同完整版號。

## 公開與本機隔離

- patch：只含桌面程式、可公開的自有文件／HD 生成圖、第三方授權及合法資料匯入工具。排除原版 EXE／COM／DAT／FIG／XGB／音訊、背景參考色號／色盤、私有執行器來源、原始收據與含原版音樂的影片。
- full-local：使用合法本機固定來源加入遊戲資料與既有 HD 背景參考，提供直接啟動方式；保持 gitignore，只留本機。兩種包均保留 RRSAL-1.0、字型與實際依賴授權。
- 公開包以匯入工具驗證固定原檔身分，再由使用者的原檔建立 HD 背景參考。資料缺少時給出可操作的匯入提示，不混入來源遊戲。
- promo：原生真實畫面與原版實際音樂，不生成替代音樂。含原版素材的影片及音訊只留本機。音樂／語音 HD 本輪作格式與可行性評估，未知項保持未知。

## 驗收

由乾淨工作目錄與固定輸入建置，逐包核對平台／架構、完整檔案清單、大小與 SHA-256、版本與授權。從封包解出後啟動 Linux／Windows Wine，走正常選角與對戰；macOS 核對 Mach-O 與包內容，沒有真機時明列限制。公開包須驗缺資料提示、匯入後可啟動，以及原版檔案與來源雜湊沒有漏入。

推廣片驗視訊／音訊長度、非靜音、凍結與黑幀、字幕邊界、實際素材雜湊及原音樂來源；原生畫面與靜態說明分開標示。README 增加有出處的故事背景、最新設定與對戰圖、發行入口與完成限制。確認四格鍵盤快捷與魔王選角正常後，再錄影及打包。GitHub 僅發布已核對的 patch 與公開 manifest，full-local、promo、smoke 均不上傳。

## 已驗結果

- `dist-all/v.0.1.0-20261020/smoke/package-audit.json` 通過八個 ZIP 的完整清單、CRC、逐檔 SHA、版本、授權及公開原版排除；各本機包含 125 個固定正常來源檔，作弊資料未加入。根目錄 SHA256SUMS.json 綁定八包，patch/release-manifest.json 只列四包。
- `smoke/linux-startup`／`windows-startup` 各驗公開與本機兩包：實際程式版本、公開包缺資料提示、jsdos ZIP 匯入、拒絕覆寫、125 原檔、自動 HD 參考、正常原生視窗開始執行。Windows 以 Wine 驗；macOS 只驗 Mach-O、兩架構、Info.plist 及內容，未簽章、未作真機驗收。
- `smoke/linux-play-record` 從實際本機封包正常雙打，四項通過：HD 資產自動載入、預設鍵盤快捷／移動、失焦與中立閘門、滿血練習。三張畫面由原始資料獨立重組。現行版魔王單打及蜘蛛女切換另由 workplace/release-boss-single-v1／release-spider-hd-v1 通過。
- 本機影片為 `promo/v.0.1.0-20261020-local-promo.mp4`，60 秒、1280×720、30fps、AAC 48kHz 雙聲道。包含十八秒真實原生錄影，其餘靜態畫面清楚標示；有原版 MIDI 軟體演奏，保留曲目、SoundFont 與來源 SHA。字幕邊界、抽樣畫面、完整解碼、音量與黑幀已驗。原生操作有數秒畫面停留，凍結檢測結果保留，不稱正式速度通過。技術音量檢查不等於人耳抽聽。
- 鍵盤限 035 已驗範圍；斬四招沿用 004 來源，其他角色僅配置。完整 HD、遊戲音訊串流、魔王完整過關與結局、實體手把及平台真機仍未完成，不影響使用者選定的首版有限發布。
- [首版 Release](https://github.com/wicanr2/superfighter-remastered/releases/tag/v.0.1.0-20261020)已發布，tag 固定提交 `807579d01c145db327050c2e870e2bf46e6bcb68`。四個引擎 ZIP 與一份 manifest 的遠端大小、SHA-256 均符合本機核對，沒有完整版或影片。儲存庫目前為 PRIVATE，僅有權限帳號可見；「公開包」指可供公開的內容分類，不代表已變更儲存庫可見性。收據在 smoke/github-publish.json，已發布 tag／Release 不移動或覆寫。

## 重現入口

使用既有 Docker 工具鏈與唯讀原版輸入。`tools/build_desktop.py` 的 linux／cross／verify 產生四平台編譯身分；`tools/package_release.py` 的 licenses／packages／audit 收集授權、建立乾淨八包與檢查。package_startup_smoke.py 驗解壓入口，package_smoke.py 驗操作並錄影，promo_release.py 的 prepare／render／check 合成與檢測本機影片。工具與 Docker 規則見專案 AGENTS.md，實際旗標與收據見 WORKLOG.md。

公開發布使用 `tools/publish_release.py`，在已登入 GitHub CLI 的容器依序執行 draft／publish／verify，均明確指定 `--target` 完整提交。工具檢查本機操作、封包與影片收據，只上傳 patch 四包及 manifest，逐一比對遠端大小及 SHA 後發布。已有版本拒絕重新建草稿；已發行版本不可覆寫。音樂、完整版與原版收據不上傳。

## 暫停後本機交付

使用者要求暫停 HD 開發，僅收尾人工驗證、三平台本機完整版、原曲影片與工作區清理。本機交付版採 `v.0.1.1-20261021`，沒有新增 Release 或 tag；首版 `v.0.1.0-20261020` 保持不變。正式玩家程式只有 VERSION 更新，沿用 045 的 46 份編譯輸入與現行 74 張角色／特效圖集。046／047／048 原型保持 DRAFT，不打入本機包。完整版指含 125 原版資料檔，完整 HD 與遊戲音訊尚未完成。

- `dist-all/v.0.1.1-20261021/SHA256SUMS.json` 綁定八個新 ZIP，`smoke/package-audit.json` 逐檔核對 SHA／CRC／清單、版本、授權及公開原版排除。四個 full-local 分別供 Windows amd64、Linux amd64、macOS Intel／Apple Silicon，只留本機。patch 同步保存引擎對應包，本輪未發布。
- `smoke/linux-startup/receipt.json` 與 `smoke/windows-startup-v2/receipt.json` 各驗公開／完整兩包：版本、原版 125 檔、缺資料提示、安全匯入、拒絕覆寫、自動背景參考、設定面板及正常開始。Windows 在既有 `eob-remake-wine-verify:ubuntu-noble-20261008-r2` 驗證。首次環境缺 Wine 的 `windows-startup` 保留，不算產品失敗。macOS 僅核對 Mach-O、兩架構、plist 與內容。
- `smoke/linux-play-record/receipt.json` 在解壓 Linux 完整包目錄啟動實際二進位，HD 預設資源、快捷／移動、真實失焦與中立、F9 滿血四項通過，保存十八秒實錄。沒有新增完整對戰或正式速度結論。
- `promo/v.0.1.1-20261021-local-promo.mp4` 為 60 秒、1280×720、30fps、AAC 48kHz 雙聲道，沿用原版精確 MIDI 由 TiMidity++／FluidR3 軟體演奏。此為原曲重播，不是原機 OPL 錄音。完整解碼、非靜音、黑幀、字幕邊界及十八秒實錄的凍結檢測通過；接觸圖八格已抽看。完整人工播放與人耳試聽未驗，詳見 `promo/promo-checks.json` 與 `source.json`。

解壓重現入口為 [tools/unpack_release.py](../../tools/unpack_release.py) 的 `--output 全新目錄`，會核對八包並保留執行權限。啟動測試以 `tools/package_startup_smoke.py --extracted-index 該目錄/extracted.json` 指定輸入，避免覆用舊版或已匯入的測試目錄。錄影與合成仍走原工具，使用新 VERSION 的 dist-all 路徑。全部在有資源上限、UID 1000、無網路的一次性 Docker 容器執行。

人工驗證與未實作項目集中在 [WORKLIST](../../WORKLIST.md#人工驗證)。清理收據為本版本 `smoke/workspace-cleanup-plan.json`、`workspace-cleanup.json` 與 `retained-workspace-files.json`；實際腳本另存 `smoke/cleanup-workspace.py`。只移除舊 Wine 前綴及 Go 編譯快取，原始資料、研究證據、執行器、模組快取與所有素材保留。Wine 登錄及非系統設定先存 `full-local/wine-runtime-settings-backup.tar.gz`，逐檔核對後才刪除。Wine 系統 DLL 由原有工具映像重新建立新前綴，再視需要還原設定；Go 編譯快取由保留的模組重建。歷史測試輸出保留原樣，需要重驗時使用新的輸出目錄。

最終稽核在本版本 `smoke/final-audit.py` 與 `final-audit.json`，四個編譯收據另存 `smoke/build-receipts/`。128 原檔、1719 執行器來源、162 素材紀錄與正式角色清單 SHA 均通過；四架構相較 045 只有 VERSION 編譯輸入改變。首版八包、原曲影片與正式 IDA 資料庫保持，588 個文件連結、UID 與誤建目錄檢查通過。這些結果不代替人工試玩或完整 HD 完成證據。

## 集中 HD 與原音本機交付

`v.0.2.0-20261021` 為 049／050 的新本機交付。沒有建立新 Release 或 tag；前版八包與原曲影片保持原 SHA。`dist-all/v.0.2.0-20261021/` 的 patch／full-local 各四包，覆蓋 Linux amd64、Windows amd64、macOS Intel／Apple Silicon。

- 四架構以 Go 1.24.13 固定工具鏈由相同正式來源編譯，每個二進位附實際 compiled_inputs、版本、SHA 與檔頭收據；現行副本在 workplace/bin，原編譯位址 bin-ready 保留。HD 包含十一景、33 畫面圖與完整 1630 鍵／78 圖集。
- 每個 full-local 包含 125 原版檔及 55 原音 OGG，僅留本機；patch 不含原版、OGG、WAV 或 MIDI。每包清單、CRC、SHA、授權、版本、路徑與原版排除均通過，收據在本版 SHA256SUMS.json 及 smoke/package-audit.json。
- 八包解至新的 workplace/hd-batch-integration-v1/release-unpacked-final；Linux 與 Wine 各驗 patch／full-local 啟動、版本、缺資料、安全匯入與拒絕覆寫、設定頁、自動十一景原參考及音訊 bank 載入。收據在 smoke/linux-startup／windows-startup。這些啟動在第一首原音前結束，不稱 Wine 音訊裝置已驗。
- Linux 原音實際裝置路徑為 Oto→ALSA pulse→私有 PulseAudio sink；原始錄音以 parec 的 48 kHz 樣本數對時。55 段轉換與 167 秒實錄、暫停／靜音／恢復及循環的證據只留 workplace/hd-batch-integration-v1/audio-final-v4。沒有新配樂、語音修復或人耳完成聲明。
- 本輪沒有製作 v.0.2.0 推廣片。v.0.1.1 的六十秒原曲影片保持，不能作為新版全部 HD 的影片證據。人工與真機限制見 WORKLIST。

這些新版 ZIP 未公開。下次發行仍先確認最終聲明、真機限制與新版錄影，再使用新的不可覆寫版號。

## v.1.0.0 正式版與新版推廣片

狀態：v1 交付、影片及遠端發布限定 CONFORMED。使用者於 2026-10-21 明確要求正式進入 v1.0.0 並拍攝實際遊玩與魔王選角。沿固定版號採 v.1.0.0-20261021；保留既有已驗功能與限制，不因主版號宣稱全動畫、全過關、真機或實體手把通過。公開內容仍為四個不含原版及原音的引擎包；完整版與含原音的影片只留本機。

影片由三名魔王各自正常雙打選角與實際攻擊錄影組成，以原生 Linux 程式執行，不注入狀態、不加速冒充即時。標題／結尾字卡與實錄分開標示；實錄為主要內容。錄下原程式觸發的音樂與音效，保留原 MIDI 軟體音色與 PCM 近似說明。素材、時間、原始片、編碼命令與雜湊全部可回查。檢查完整解碼、非靜音、音訊削波、黑幀、對戰凍結、字幕邊界、三個選角及實際角色與傷害。封包重新編譯、八包重建與 Linux／Wine 啟動後，沿既有有限發布授權準備正式 Release，原版／原音／影片不公開。

v1 四架構實際編譯來源相較 v.0.2.0 只改 VERSION。八包 SHA／CRC／清單及原版／原音排除、Linux／Wine 各兩包解壓啟動通過。三魔王正常選角、確認與原版輸入戰鬥已錄到，對手生命分別 88／84／79；沒有啟用練習或注入狀態。新版影片為 75 秒，66 秒原生實錄，其餘為明示的片頭／結尾卡。原音由 Oto→ALSA pulse→PulseAudio monitor→parec 收錄，用原始樣本數與視訊進度對時，屬擷取近似；字卡使用同一已驗原音 OGG。

影片 SHA `07cc05854744a233ec7e57ee4e7cf0977de21e217f784bb01d347a66ed74f66e`，1280×720、30/1 fps、AAC 48kHz 雙聲道。完整解碼、峰值 -7.8dB、非靜音、黑幀 0、三段戰鬥大於二秒的凍結 0，文字邊界與八段抽樣圖通過。收據、各段錄影與原始音訊位於本版 promo。人耳與完整人工觀看未簽收。

錄影工具 [record_promo_bosses.py](../../tools/record_promo_bosses.py)從正常標題、雙打、姓名按鈕與確認進入，以鍵鼠正常攻擊；[promo_v1.py](../../tools/promo_v1.py)的 prepare／render／check 保存字卡、來源、時間表、編碼與檢查。assemble 可只重組已編碼片段，固定 CFR 30 與 75 秒，避免逐段 AAC 時戳造成平均幀率偏差。[audit_release_v1.py](../../tools/audit_release_v1.py)另核對原 128 檔、1719 執行器來源、i64、172 素材、舊 24 ZIP／兩支影片、四架構、錄影與 UID。沒有新原版行為研究。

[v1 Release](https://github.com/wicanr2/superfighter-remastered/releases/tag/v.1.0.0-20261021) 已於 2026-10-21T06:19:39Z 發布，tag 指向 f7f6ac667fae36d08bb5106957c1d9e560c6a390。四引擎 ZIP 與 release-manifest.json 的遠端檔名、大小及 SHA-256 均符合本機，沒有其他附件；收據為本版 smoke/github-publish.json／github-verify.json。使用者明確授權一次性容器的 AppArmor 例外，其餘 UID、唯讀、cap-drop 與禁止提升權限限制保留。儲存庫仍為私人，沒有搬運憑證或變更主機安全設定。後續文件提交不移動此 tag 或覆寫附件。

## v.1.0.1 本機流暢度修正版

限定 CONFORMED。依使用者確認的原版節奏／60 fps 輸出與第二排魔王頭像，建立全新 dist-all/v.1.0.1-20261021，不覆寫已發布 tag、附件、舊封包或影片。這是本機修正版，不自動擴張為新版公開發布。四架構逐一核對實際編譯來源、二進位與檔頭，來源只新增呈現優化、固定擷取節奏及頭像介面；原版核心與私有執行器不變。

八包由乾淨輸入重建，patch 排除原版／原音，full-local 各含 125 原檔與 55 OGG。清單、CRC、SHA 及 Linux／Wine 各兩次乾淨解壓啟動通過；完整包、測試原始資料及影片只留本機。Wine 與 macOS 檔頭不等於該平台真機。

三名魔王各由第二排頭像正常選角後攻擊，正式程式以 capture-fps=60 在 ada NVIDIA EGL 執行，三場實際繪圖 59.97–60.00 fps。新片維持 75 秒、66 秒實錄，改為 1280×720、CFR 60/1、AAC 48 kHz 雙聲道；完整解碼、非靜音、峰值 -8.6dB、黑幀 0、戰鬥大於二秒凍結 0、八段畫面及文字邊界通過。影片 SHA `2bfd13390f298a18bfa1dd369dc1505c6e7e8deaa2c619118b485d16a11e656d`。影片直接使用本輪 60 fps 實錄，未補幀、強制勝負或修改時鐘。原版完成畫格仍分開記錄，不宣稱六十個新動作。

工具沿 [record_promo_bosses.py](../../tools/record_promo_bosses.py)的 fps／renderer／portraits 參數及 [promo_v1.py](../../tools/promo_v1.py)的新 60 fps 流程；重現舊片使用舊版來源。效能標準與實測邊界見 [005](005-native-desktop.md#60-fps-流暢度目標)，介面驗收見 [025](025-boss-selection.md#第二排魔王頭像)。本版 smoke／promo 保存編碼、來源、啟動、清理與總稽核收據。實體螢幕、其他平台真機、雙手把、完整動畫／過關及人耳未外推。

## v.1.0.2 雙打介面重打包與 HD 片頭

狀態：限定 CONFORMED。使用者要求重新打包並重錄推廣片，包含遊戲片頭 HD。採新版本 v.1.0.2-20261021，沿現行四架構、八包與本機原音契約。前版 ZIP、影片、tag 與 Release 不覆寫；本輪不新增 GitHub Release。以下契約在建置前以 READY 審查，完成證據附於本節末。

- 從已驗二十七項正常選角的來源重建四架構，更新封包說明：原標題雙打、第一人確認後選第二人、十一個畫面內頭像、魔王第二排，移除畫面外姓名／確認按鈕。設定、原核心與 60 fps 擷取節奏不改。
- 八包依固定 dist-all 契約重建，逐包核對檔案、CRC、SHA、版號、架構及權利分類；Linux／Wine 各對引擎與完整版乾淨解壓啟動。原版與 55 段原音只進 full-local。
- 推廣片重錄正式程式，60 fps NVIDIA EGL 實際 GPU 擷取、保留原版節奏；三魔王各由雙打第一人與第二人正常選角再攻擊，選角片段內要看到兩側完成定位。另錄遊戲內 HD 標題及原音，不用字卡代替片頭。
- 75 秒分鏡：版本字卡三秒、遊戲 HD 標題六秒、三名魔王各六秒選角與十四秒戰鬥、結尾六秒，共六十六秒原生實錄。九段接觸圖，標題、三選角及三實戰分別抽看；保持同一遊戲的金黃／青藍視覺，差異記來源檔。
- 檢查原音非靜音、削波、完整解碼、75 秒／60 fps、黑幀、戰鬥凍結、字幕裁切、原始素材與二進位來源雜湊。HD 標題只聲明實際錄到的正常標題畫面，不擴張為未有素材的完整劇情動畫。影片、原音及完整版維持本機。

四架構 compiled_inputs 相較已驗二十七項介面的來源僅 VERSION 改變，二進位／架構與八包清單、SHA／CRC、原版／原音排除均核對。Linux 與 Wine 各引擎、完整版共四次乾淨解壓啟動通過；設定、自動十一景參考、安全匯入及拒絕覆寫保持。封包說明已加入原雙打流程、第二排魔王、畫面內十一頭像及 capture-fps。新版只有本機交付，不代替其他平台真機。

成片 10,114,027 bytes，SHA a09876bd404d88b86cbe0fc16c58994c407e52a6b40c9a977fc09792f13d8e2c；75 秒、4,500 格、1280×720／60 fps、AAC 48 kHz 雙聲道。原 HD 標題實錄 music-01 峰值 -14.0dB，合成後標題段 -15.5dB；成片峰值 -7.3dB，非靜音、完整解碼、黑幀零、三戰鬥大於二秒凍結零，九段接觸圖及 HD 標題／雙人選角全圖抽查通過。選角抽圖取第 5.5 秒，以核對兩人都已定位。素材來源、聲畫擷取近似、版本與命令全部保存在本版 promo。

三場戰鬥實際繪圖 60.0411／59.9685／60.0018 fps。最新版另在 ada 進行二十秒完整步進／錄影補測，平均 59.9886 fps／TPS，1,201 間隔 p99 24.8805 ms、最大 34.0841 ms，超過 33.3 ms 一次；記錄全部結果，沒有挑重跑的零次樣本。首次量測腳本過早點第二人頭像，補等待已畫出且玩家相符的選角狀態後同工具鏈乾淨重跑，遊戲二進位保持。完整人工播放、人耳、實體螢幕、雙手把及其他平台真機仍未外推。
