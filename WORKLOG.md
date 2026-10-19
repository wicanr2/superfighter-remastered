# 快打至尊 Remastered：工作歷程

目前狀態見 [CONTEXT.md](CONTEXT.md)，穩定規則與文件索引見 [AGENTS.md](AGENTS.md)。本檔採追加記錄。

## 2026-10-19：下載與規範初始化

- 依使用者要求下載指定頁面使用的 jsdos 包，保存為 `快打至尊.jsdos`。
- Docker 內驗證 ZIP CRC、130 個項目及 `.jsdos/dosbox.conf`，SHA-256 與來源物件檔名一致。
- 依 `/init` 要求讀取 zeliard AGENTS、dosgolem README／CLAUDE 與接入規格，載入知識路由中的生命週期、dosgolem 與文件職責入口。
- 已讀取逆向重製、grill-me 與 grilling 技能。沿用 dosgolem 架構，未代選 HD 畫風、倍率與發行範圍。
- Docker 內初查 `PLAY.BAT`、`README.TXT`、jsdos 設定及主要執行檔雜湊；發現同名 `SF.COM`／`SF.EXE` 與不同的兩份 `AIDATA.DAT`。
- 建立 AGENTS、CONTEXT、WORKLIST、WORKLOG 及 `.gitignore`。本輪沒有新增目錄、實作程式、執行遊戲、修改參考專案、建立遠端或發布產物。
- 使用既有 `python:3.13.7-slim`，容器使用 UID/GID 1000:1000、資源限制與 `--rm`；盤點容器禁止網路且來源唯讀。
- 收尾驗證通過：四份 Markdown 的相對連結均存在，五個新增檔案均已加入 AGENTS 索引，原始遊戲包 SHA-256 不變，文件擁有權為 1000:1000，工作根沒有 root-owned 檔案或誤建的 `*.md` 目錄。
- `docker ps -a --filter name=kdzz-` 回傳空清單，本輪容器已清除。沒有建置新 image，沒有 Git commit 或 push。

## 2026-10-19：來源盤點與首次啟動探針

- 使用者授權開始已列出的來源盤點與 dosgolem 接入工作。
- 依文件職責建立 `tools/` 保存可重現研究工具，`workplace/` 保存本機原始副本、隔離資料、建置快取與收據。先前沒有等價目錄；原始 jsdos 不搬移。
- 沿用 `dosgolem-go-ebiten:1.24-r1`，已確認提供 Go 1.24.13 與 Python 3。共用 dosgolem 工作樹乾淨，唯讀掛載。
- 安全解包完成，共 128 檔；作弊資料隔離。建立原始及補丁來源 manifest，原始 jsdos 不變。
- 首次啟動重現監督佇列 IF 缺口。建立規格 001，最小正常結束／TSR 時鐘案例先失敗；限定修正後 DOS／machine 套件通過，原版啟動鏈可自然到標題，規格限定 CONFORMED。補丁僅在本專案工作副本，未改共用來源。
- 已由正常操作到選角、原版設定頁與首戰。一次 Return 的乾淨流程到 Jaan 對 Frank；對戰 IRQ1 按下／放開各送一次。尚未完成結算、返回、多鍵、音訊、桌面與手把實測。
- 使用 IDA Pro 9.4 查選角鍵盤消費端，輸出保留原始位址、bytes 與未知語意。工具的 ASCII 輸出與掃描碼字串問題修正後乾淨重跑；未把環境／腳本失敗寫成產品缺陷。
- 早期截圖停在選角的解釋已由後續正常首戰收據修正；勘誤追加於 RESEARCH-LOG，現況與驗證矩陣同步更新。
- 收尾稽核通過，完整結果見 `workplace/research-audit.json`：128 個來源檔、共用來源、獨立補丁副本及 17 份收據的已登錄產物雜湊均相符，文件連結、工具語法與擁有權正確。
- 本輪 `kdzz-` 容器清單已清空，共用 dosgolem 的 `git status --short` 仍為空。沒有 Git commit、push 或公開產物；未建立新工具鏈 image。

## 2026-10-19：依說明書設計手把與 HD

- 讀取使用者指定的說明書頁面，保存完整 HTML 與兩張原圖，逐檔記錄 URL、時間與 SHA-256。圖片實際為標題及森林對戰，沒有 HD 分層素材。初次檢視誤用 Big5，依頁面 meta 與 bytes 改用 UTF-8 BOM 解碼；原始下載 bytes 未改。
- 網頁自述 v1.1，目前包內自述 v2.0。將八方向、Tab／Enter 拳、左右 Shift 腳及後退防禦作為待實測候選；不套用頁面的破解、簡易招式或作弊修改。
- 建立 DRAFT 規格 002、003，並加入 AGENTS 與 CONTEXT 索引。手把提案採西側拳、南側腳，Start 使用前端暫停，避開 Esc 按住補血。沒有接入遊戲或宣稱原版動作表已完整證實。
- 建立 `tools/gamepad-preview.html`，可用螢幕按鈕、方向鍵與 J／K 預覽，支援瀏覽器標準手把讀取；沒有注入 dosgolem。死區、相反方向與輸入來源優先序皆標為原型選擇，未作正式規則。
- 使用內建 imagegen，以同一張 dosgolem 首戰截圖生成 A 忠實精修與 B 街機手繪。原始生成檔已複製到 `workplace/design/`；提示詞、來源雜湊、輸出尺寸及雜湊存為 prompts.json 與 manifest.json。實際各 1586×992，角色髮型、服裝與比例偏差已列明，沒有當成正式資產或同狀態驗證。
- 已展示兩稿並提出單一畫風問題；目前沒有採用任一畫風。倍率、像素比例、首批範圍、預設模式與手把正式配置仍待確認。
- 檢查通過：原始包及手冊快照雜湊、文件與預覽資源連結、文件索引正對照、DOM ID 與程式引用、Node 22 JavaScript 語法、檔案 UID/GID 與主機衛生。詳見 `workplace/design/audit.json`。沒有瀏覽器實際操作、實體手把或遊戲接入驗收。
- 為確認既有瀏覽器工具鏈，查過三個既有 image；未提供可用工具，其中 dkk-pdf 缺 Python。沒有退回主機執行，也沒有新增重複 image。
- 本輪容器均有資源限制、UID/GID 1000:1000、有界執行與自動清理；只有說明書下載開網路。`docker ps -a --filter name=kdzz-` 已為空，工作根沒有 root-owned 檔案或誤建的 Markdown 目錄。沒有改共用 dosgolem、Git commit、push 或公開素材。

## 2026-10-19：確認 B 街機手繪方向

- 使用者回覆「ok B」，只確認先前問題中的 HD 畫風。採 B 街機手繪，A 保留作比較歷史；既有造型偏差仍依原版修正，未把倍率、首批範圍、預設模式或手把配置一併視為確認。
- 同步 AGENTS、CONTEXT、WORKLIST、規格 003 與 HTML 預覽的現況。規格維持 DRAFT，記錄 B 原圖路徑及 SHA-256；保留原始生成 bytes，沒有重畫或改圖。
- 本輪命中文件職責路由，讀取 `local/project-document-responsibilities.md`，並依 grilling 的決策後記錄規則更新既有文件，沒有新增台帳或目錄。
- 文件套用初次因末段定位不符而整批未寫入；核對原檔後移除多餘定位，成功套用。這是編輯工具定位問題，沒有產品缺陷。
- Docker 內驗證 B 雜湊不變、五個入口已同步、Markdown 連結存在、UID/GID 為 1000:1000，沒有 root-owned 檔案或誤建的 Markdown 目錄。只是文件與預覽文字變更，未重跑遊戲或宣稱動態 HD 完成。
- `docker ps -a --filter name=kdzz-` 為空。本輪未建 image、未改共用 dosgolem、未執行 Git commit 或 push。

## 2026-10-19：四招快捷、雙手把規劃、HD 開工與資料保存

- 使用者授權逐角色快速出招，明確指定 R1 對應絕招 1、最多四格；有五招角色可選四招。依此建立 R1／R2／L1／L2 預設 1／2／3／4 的設定原型，八名角色分別保存，兩名玩家互不影響。補上空綁定、還原、瀏覽器保存、文字方向鏡像及按下邊緣；沒有猜測出招時序或注入原版。
- 依使用者要求規劃雙手把雙打，設定預覽可選兩名玩家與各自裝置，拒絕同裝置重複指派，斷線清除該指派。第二人的原版輸入、正常雙打與實體裝置仍待驗證；沒有把設定面板當成雙打遊戲完成。
- 使用者明確同意 HD 規格開工，首批屋頂、斬、法蘭克與對戰介面不再列為待確認。規格技術狀態維持 DRAFT，先做來源與分層素材，不把授權當作原版技術證據。
- 建立可撤回的場景蒐證工具，解碼 11 張 XGB 與 3 張 CPM。查得 5-byte header、768-byte 色盤及可變 RLE 標記，修正早期邊界假設後在同一工具鏈重跑。SFNAME.CPM 不符合候選而保留未知，沒有硬套解碼。
- 屋頂定位為 I2.XGB 強推論，原貌色號抽樣與較大遮罩比較均保留實際差異數。用內建 imagegen 生成屋頂背景及兩張真實 alpha 的角色待機圖，保存原始生成檔、提示詞、尺寸與雜湊；新增分層預覽。尚未完成完整姿態、動態合成、穩定來源鍵或遊戲接入。
- 依使用者要求研究 AI，發現包內 DAME 為組合語言文字。只作定位線索，使用既有 IDA Pro 9.4 非破壞匯出原 binary 讀取與消費端。原始 AIDATA 是三個 192-byte 區塊、值域 0–31；CHEAT 檔實為 169-byte ASCII 短檔。已定位策略索引乘 16 選角色輸入序列，確認資料調整可行；短檔效果仍需同狀態實驗，沒有替換正常 AI。
- 青衫原 HTML 保留原始 bytes，補齊離線圖片路徑。新增 SP Moves 原 HTML 及八張角色圖，保存 URL、時間與 SHA-256，補齊原相對圖片路徑。依使用者明確要求建立 `docs/game-history.md`，整理兩站史料、操作、八人招式對照、三頭目、圖片、版本與資料線索，差異並列且注明來源。
- 新工具與歷史文件加入 AGENTS，現況、規格、工作清單及驗證矩陣同步更新。研究細節追加到 RESEARCH-LOG，沒有另建同義台帳或根層研究目錄。
- 驗證通過：12 個原始 HTML／圖片檔雜湊、離線圖片路徑、所有文件連結、索引正對照、DOM ID 與靜態引用、Python／JavaScript 語法、四格與三個五招角色替換、玩家隔離、方向文字鏡像、蓄力標記、非法設定、獨立按下邊緣及設定 JSON 往返。生成素材雜湊、尺寸、RGBA alpha、IDA 原始輸入及輸出 schema、擁有權亦通過。完整結果見 `workplace/implementation-audit.json`。
- 來源比較曾誤用無 Pillow 的盤點 image，修正為既有 `sc-cht-hdtools:pillow11.3.0-r1` 後乾淨重跑。此為環境分類，沒有退回主機執行或記為產品缺陷。
- 本輪均在有界 Docker 內執行，下載才開網路；容器 UID/GID 為 1000:1000。最後 `kdzz-` 容器清單為空，工作根無 root-owned 檔案或誤建的 Markdown 目錄。未建新 image、未改原始 jsdos、正常資料、共用 dosgolem，沒有 Git commit、push 或公開產物。

## 2026-10-19：原貌操作入口、斬四招與瀏覽器驗證

- 接續使用者「ok 繼續啦」。命中規格閘門、dosgolem 對拍、文件職責與 README 路由，讀取相應單一入口；較早規格回填另讀 re-resolution-backlinks，將必要勘誤及索引寫回規格 002／004。沿用逆向技能及既有 IDA 9.4 工具鏈，沒有重新要求已取得的授權。
- 原版單打與雙打各驗 25 組方向、拳腳、多鍵及放開。兩人的斬各驗四招，全部進入對應原版路徑。近身投技以普通行走準備；快捷沒有自動移動、跳蓄力或改寫角色。新收據附執行前腳本及來源身分，舊失敗保留。
- 規格 004 限定 READY 後，建立 Go 本機入口與瀏覽器介面。核心、規則及狀態仍由 dosgolem 執行原版；支援原版滑鼠／選單、原貌畫面、雙人掃描碼、四格設定、逐來源按住所有權、前端暫停、失焦與三秒失聯清理。實際快捷先啟用已驗斬四招，其他角色明示拒絕。
- 修正設定面板攔住手把 Start、UI 按鈕 Enter 不漏到 P2、Enter／NumpadEnter 共用掃描碼的獨立放開，以及裝置改派／斷線明確取消該玩家快捷。另一人的指派與輸入保留。
- `live-http-v4` 八項通過；`browser-live-v3` Chromium 12 項通過。正常入口、雙人同時拳腳、R1、按住不連發、暫停、設定保存與重載、斷線、窄畫面及靜態 HD 預覽均有收據。手把為瀏覽器合成裝置，不宣稱實體驗收。
- 使用既有 Go image 建置，初次因平行編譯與 pids 上限出現資源錯誤，設 GOMAXPROCS=2、CGO_ENABLED=0、-p 1 後重跑通過。GUI 首次暫停斷言先讀到前端樂觀狀態，改驗伺服器確認後的步數；新增斷線斷言曾誤讀 Go byte slice JSON，修正腳本 Base64 解碼後通過。環境與腳本問題未記為遊戲缺陷。
- 沿用原有 image 檢查後仍缺瀏覽器，拉取固定版本 Playwright image，搭配同版套件及 lockfile；測試不開網路。沒有在主機啟動 Node、Python、瀏覽器或遊戲。
- 原版斬／法蘭克各 72 槽姿態圖已解碼，分別為 61／57 個不同位置。逐圖透明 PNG、指標與雜湊保存；候選格式維持強推論，尚未接動態 HD。新增 README 與 Docker 建置／啟動腳本，全部工具與文件有索引。
- 最終稽核 `workplace/live-audit.json` 通過：128 個來源檔、1713 個 dosgolem 副本檔、目前二進位與收據一致性、姿態圖雜湊、文件連結與回填索引、語法及擁有權。Go vet 亦通過。另以啟動腳本的相同 Docker 參數確認主機 `127.0.0.1:8086` 可連，初始暫停且執行步數為零。
- 啟動驗證容器已明確停止並自動刪除，最後 `docker ps -a --filter name=kdzz-` 為空。工作根沒有 root-owned 檔案或誤建的 Markdown 目錄；保留現用固定 Playwright image。原始包、來源檔與共用 dosgolem 未改動，沒有 Git commit、push、遠端或發行包。

## 2026-10-19：依使用者修正，改為三平台原生桌面

- 使用者明確指出「不用 web，就是三平台」。前輪瀏覽器入口降為研究工具，玩家入口改為 Windows、macOS、Linux 原生程式；同步 AGENTS、CONTEXT、README、工作清單及規格回填，不沿用平台未定或 HTTP 即成品的斷言。
- 命中跨平台重製、規格閘門、文件職責與 README 路由，讀取逆向、grilling 及相關入口。三平台方向由使用者直接指定，沒有重問已確認架構。新增規格 005 限定 READY，沿用規格 004 已驗原版輸入，不增加遊戲規則。
- 新建 cmd 與 internal 作正式原生入口及適配層；既有 tools 保存獨立研究探針，不適合作正式程式主結構。以相對路徑 go.work 接本機 dosgolem，沒有虛構公開模組版本；獨立 tools/go.mod 隔離舊 Go 片段，不改舊探針 bytes 或歷史收據。
- 原生視窗直接呼叫 public oracle API。接上原貌 RGB、正常啟動鏈、鍵鼠、兩個原生標準手把指派、四格與第五招設定、來源所有權、斬四招、設定隔離、暫停、失焦與斷線清理。沒有啟動 HTTP 或嵌入瀏覽器。設定與 DOS 可寫資料分開置於使用者目錄，原始資料唯讀。
- 內嵌 Noto Sans CJK TC，鎖定上游 commit f8d157532fbfaeda587e826d4cd5b21a49186f7c，保存 OTF、OFL 全文、URL 及雜湊。文字先量測、超長省略，沒有用缺字方塊作中文設定介面。
- 沿用 dosgolem Go image 編譯 Linux，跨平台及 GUI 使用既有 tokugawa 工具鏈。後者缺 Linux X11 標頭，核對原 Dockerfile 後分工使用既有 image，未另建重複 image。字型所需套件原 image 沒快取，下載固定版本到專案自有 cache，後續編譯與測試關網路。
- Linux amd64、Windows amd64、macOS amd64／arm64 已編譯；四個檔頭、架構、來源及雜湊收據見 desktop-build.json。macOS 首次編譯超過批次 240 秒，保留快取並以有界單一架構續建完成；不是遊戲缺陷。尚未建立正式版號、安裝包、簽章、Release 或 dist-all 交付。
- Linux 原生 GUI 首輪八項通過，正常標題、雙人選角、兩人拳腳、共用掃描碼釋放、R1、暫停、四格／第五招／留空、玩家隔離、程序重啟及失焦。Windows Wine 首輪在視窗尚未映射時強制焦點造成 BadMatch；改等可見視窗，在相同 image 重跑三項通過。Wine 非 Windows 真機，瀏覽器合成手把也未換名當原生硬體驗收。
- 設定單元測試與 go vet 已通過。首次 vet 因冷快取時間上限停止，後續完成；環境及測試腳本失敗留存。最終 workspace 二進位的重跑、完整稽核及清理結果見本節後續紀錄。
- 最終四個 workspace 二進位重建後，`desktop-gui-v2` 的 Linux 原生八項、`windows-native-v3` 的 Wine 三項全部通過。`desktop-checks.json` 記錄根模組 `go test -p 1 ./...` 與 `go vet` 均成功；舊多 main 研究工具已由子模組隔離。
- `desktop-audit.json` 通過目前來源／二進位／收據一致性、128 份原始資料雜湊與唯讀、1713 份 dosgolem 副本、Noto 及 OFL、文件連結與索引、語法及擁有權。README 主入口改為原生程式與 build_desktop.sh，沒有 HTTP 啟動流程。
- 最後 `docker ps -a --filter name=kdzz-` 為空，Xvfb、Wine 及所有建置／驗證容器均已結束並刪除。工作根無 root-owned 檔案或 Markdown 目錄；本輪沿用既有 image，沒有新建重複 image、改共用 dosgolem、Git commit、push、公開素材或發布套件。macOS 真機、實體雙手把、完整回合、音訊與動態 HD 仍未完成。

## 2026-10-19：README 整合截圖與原生屋頂 HD 背景

- 使用者要求 README 放目前整合畫面，明確包含手把，並繼續 HD。本輪先放既有原生雙打／手把設定圖，再於背景切片驗證完成後換上實際 HD 屋頂及當輪設定截圖，另連同狀態原貌比較。圖片保留本機工作區。
- 命中 README、文件職責、spec 閘門、逆向與結論回填路由；沿用逆向及 IDA 技能。已確認畫風與首批範圍直接開工，沒有重問架構或新增產品取捨。
- 最小充分 RE 取得背景來源、完整畫格、相機、角色槽與圖像 bytes；正常單／雙打各 124 畫格。新增規格 006，完成證據審查後限定 READY，再實作原生可切換屋頂背景。原始定位、失敗原因與 API 限制追加至 RESEARCH-LOG，規格 003 的 D1 部分閉合已回填。
- 新增只讀完整畫格快照、嚴格素材清單載入、直接高解析背景合成及完整原貌前景。預設原貌，`-hd-assets` 指向本機包後可切換；來源、色盤、相機不符或素材損壞時退回原貌，不改玩法或亂數。角色與 HUD 未換成待機概念圖。
- `hd-native-v1` 的 GUI 行為十項通過，但後續 PNG 驗證發現測試腳本在編碼完成前複製，造成部分圖片截斷。改成 PNG 完成並關閉後原子換名，再以相同容器／命令乾淨重跑到 `hd-native-v2`。原失敗輸出保留，未把抓圖同步問題記成遊戲缺陷。
- 目前 Linux GUI 屋頂十項、道場回退九項與 Windows Wine 三項通過。`verify_hd_capture.py` 核對同狀態色號／色盤相同、190,818 個 HUD／高色盤前景輸出像素保留、385,169 個背景輸出像素改變，切回 HD 的遊戲區逐點相同。兩人拳腳、R1、四格／第五招／留空、設定保存及重啟均在正常原生流程驗證。沒有實體手把收據。
- `go test -count=1 -p 1 ./...` 與 `go vet -p 1 ./...` 通過，HD 環境變數提供 16 張原始完整畫格作實際資料驗證。四個三平台二進位重建且核對檔頭，收據為 desktop-build.json。macOS 仍僅交叉建置，未冒充真機。
- 本輪只完成背景切片，完整角色 HD、鏡像錨點、介面重繪、完整回合、音訊與實體雙手把仍待進行。沿用既有工具 image，未建立正式封包、Git commit、push 或公開素材。最後來源、文件與 Docker 清理驗證見本節後續紀錄。
- 最終 `workplace/hd-audit.json` 通過七類核對：原始包及 128 檔不變且唯讀、1713 份 dosgolem 副本不變、目前四個二進位／GUI 收據與來源雜湊一致、HD 原 PNG 與素材群組、字型／OFL、文件索引及原始位址回填、語法與擁有權。規格驗收敘述更新後重生 build manifest，編譯用 Go 來源與 GUI 二進位雜湊未變。當輪三份 GUI 輸出的 15 張 PNG 全部完整，README 兩張已目視。最後 `docker ps -a --filter name=kdzz-` 為空，無本專案殘留容器、root-owned 檔案或 Markdown 目錄。

## 2026-10-19：GitHub 上傳準備

- 使用者明確授權建立 GitHub 儲存庫並放上成果。預定 `wicanr2/superfighter-remastered`，先採私人設定；沒有公開原版資料或衍生美術的授權。
- 載入 RRSAL-1.0 路由與原始範本，依目前檔案填入完整 LICENSE；README 補 source-available 與第三方字型界線。新增相對路徑 workspace 範本、快取／憑證排除與可隨程式保存的設定截圖。此截圖為原版執行前的原生介面，原 PNG 未修改。
- 主機升權呼叫被自動核准政策拒絕；一般 gh 的 API 連線失敗，repo create 沒有成功。受限 auth status 的 invalid token 訊息不當作主機憑證結論，也沒有搬運憑證、改用容器 gh 或改走其他 app。
- 工作根 git init 遇到 `.git/info` 唯讀；保留原路徑，改在 `/tmp/kdzz-superfighter-publish` 建立獨立上傳工作樹。提交副本不包含原始 jsdos、workplace、執行檔、研究原圖、外站 HTML 或衍生 HD 素材。遠端建立與 push 仍未完成，HD Goal 保持 active。
- 首份提交 `8365aeb91f79032227ff3c4b5cc8daed5fc3e4bd` 含 60 檔，工作樹乾淨，`git diff --cached --check` 通過。原始 patch 的 context 空白以 .gitattributes 保留，未修改其 bytes；go.mod 與研究紀錄僅移除多餘 EOF 空行。沒有加入原始資料、憑證、Python 快取或二進位。`workplace/github-initial-8365aeb.bundle` 已完成並經 `git bundle verify` 驗證，保存完整 main 歷史，避免只留下 /tmp 副本。
- 重新核對目前 build manifest 與 HD audit 均通過；本輪未改 Go 實作。設定截圖已目視，README 可隨 Git 顯示這張不含原版畫面的圖；HD 對戰圖片只保留本機連結。Docker 一次性容器均已結束，沒有建立遠端、推送、發布或公開素材的成功聲明。

## 2026-10-19：完整角色分層與 48 個 HD 姿態

- 前一 Goal 回合分類為 progress：建立可審核的 Git 提交、授權、素材排除與完整備份；遠端網路仍受阻。主目標保持「完成快打至尊HD」，本輪回到角色，不把 GitHub 受阻當成 HD 無法進行。
- 重新檢查唯一現況、工作清單與規格，命中逆向、spec 閘門、文件職責及結論回填路由。沿用逆向技能與原 IDA 證據，角色圖使用內建 imagegen 技能。沒有更改已確認畫風，也未重新訪談已授權首批範圍。
- 新增正常雙打逐次繪製探針。1432／1432 次角色的來源 bytes 與繪製後 64,000 像素吻合，確認鏡像加一像素與成對裁切，保留原始名稱、位置與證據等級。00h／40h／80h 及左右裁切已動態驗，C0h／頂部裁切仍未動態驗。
- 為分清同值重寫的遮擋，按 DRAFT → 審查 → READY 實作規格 007。只在 dosgolem 獨立副本增加兩份 public 薄觀測／測試檔，未改原有 1713 檔或共用來源。合成 COM 驗 RAM、暫存器、指令起點、步數、週期、取消與 legacy 介面；兩項通過。
- 掛完整 RAM 觀測重跑同一正常輸入鏈，716／716 完整畫格五層重組逐點相同，含 37,424,320 次同值重寫。1432 次新舊繪製的步數、位置、姿態及來源完全相同。007 因此限定 CONFORMED；既有原生二進位仍是前版背景版，未冒充已重建或已接角色。
- 建立原版姿態參考工具，分兩批重繪斬／法蘭克各 24 姿態，共四張 1448×1086 透明 PNG。內建 image_gen 的原始輸出、提示詞、來源與雜湊保存 workplace/hd-sprite-art-v1；沒有用 Python 改生成圖、沒有以放大圖當 HD、沒有加入 Git。
- 離線角色比較稿保留原版每次寫入順序，依當幀姿態、鏡像、裁切與位置合成。首版 alpha bbox 初始化錯誤導致過窄，修正後 v3 已目視待機、蹲、跳與空中姿態。16 個保存狀態有 15 個可畫雙人 HD，缺斬 slot 56 的一格明示缺件，不補猜姿態。
- 新增 008 DRAFT，列明 typed 分層、素材來源、完整動畫、替代色盤、HUD 及原生路徑的下一個閘門。回填 003、README、現況、工作清單及驗證矩陣。完整 Goal 包含其餘正常可見角色、背景與介面；兩人首批比較稿不當成全 HD 完成。
- `workplace/sprite-study-audit.json` 通過原始 128 檔唯讀／雜湊、舊來源不變、兩個新增觀測檔、1432 次新舊資料相同、Python 獨立重組 16 份完整分層 fixture、48 個透明姿態與提示詞、文件回填及擁有權。完整動作、原生角色、HD HUD、其他畫面與實體手把仍未完成，Goal 保持 active。
