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
