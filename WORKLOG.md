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
- 本輪程式與文件已存入獨立 Git 提交 `00dfe7e28206e8b7947b316c7c82c8282873f84a`，共 69 追蹤檔。`workplace/github-hd-study-00dfe7e.bundle` 保存完整歷史並通過 bundle verify；原版、生成美術及研究輸入均未納入，沒有重試或宣稱遠端已建立。
- 最後再次核對兩份專用 audit，背景版 audit 已明示二進位使用前版來源，不能冒充新角色版。16 份文件、176 個本機連結檢查通過；Docker 內 find 無 root-owned 檔案或 Markdown 目錄。所有 kdzz 容器均已結束並刪除，沒有背景工作或新建工具 image。

## 2026-10-19：再次請求建立 GitHub 儲存庫

- 使用者再次要求建立儲存庫並上傳成果。沿用預定名稱 `wicanr2/superfighter-remastered` 與私人設定，修正 AGENTS 中已過時的遠端未授權敘述。
- 依主機規則嘗試以主機權限執行 `gh auth status`，自動核准政策拒絕提升權限。未搬運憑證、未改用容器 gh，也未將受限環境結果當成主機登入狀態。遠端建立與推送仍未完成。
- 沿用既有獨立 Git 副本保存最新程式、規格、歷史整理、授權及自有設定畫面；原版包、研究輸入、HD 衍生美術與二進位均排除。README 與 CONTEXT 補上五層角色版已有正常流程收據、目前六層來源尚待 GUI 重驗的界線。
- 本輪僅做上傳準備與文件修正，沒有重新建置或執行遊戲。Git 提交、完整 bundle 與排除檢查完成後保存於本機，不能據此宣稱 GitHub 儲存庫已存在。

## 2026-10-19：原生角色 HD、六層合成與跨平台流程

- 上一 Goal 回合分類為 progress：最新來源已保存成提交 `24eeca9` 與完整 Git 備份。遠端存取不阻塞本機 HD，Goal 持續為「完成快打至尊HD」。本輪命中逆向、規格閘門、文件職責及結論回填路由，沿用逆向與內建 imagegen 技能。
- 審查規格 008 後接入原生角色。五層首版通過 Linux 十三項，但整條原貌介面帶會遮擋高跳，先依既有 IDA 背景 RET 證據修訂契約，再分成六層。純背景與實際介面／特效寫入分開，角色直接用高解析圖集及已驗原版矩形、鏡像與裁切合成，不改玩法。
- 素材載入逐項核對合法原版來源、72 槽指標、完整 packed bytes、尺寸、PNG 雜湊、透明矩形、正常色盤與原版圖層重組。缺件、未知翻轉／裁切／色盤、來源不符皆整張回退，不產生半套角色。
- 目前 `native-actors-v4`、`windows-actors-v4`、`native-actors-missing-v1` 各十三項通過。正常標題進雙打、行走、雙跳、新空中踢擊、兩人獨立放開、R1、暫停、同狀態切換、第五招／空格、保存重啟及失焦均有收據；缺件素材另驗全畫面回退。每組十二張六層擷取獨立重組，Linux／Wine 同狀態三張原貌資料一致，HD 遊戲區切回逐點相同。
- Windows 測試解出 GLFW 同放兩鍵與 Win32 個別 Shift 狀態的差異，先以獨立只讀探針取得四組原生 VK 證據，再補規格 005 及 Windows 適配，兩人左右 Shift 獨立放開已通過。沒有修改固定依賴或共用執行器。
- 內建 image_gen 繼續補斬／法蘭克姿態與特效，原 PNG、提示詞、來源參考及雜湊逐批保存在本機。實際透明間隔與等分線略有偏差，已修正登錄邊界，沒有以 Python 修改生成圖。原生已驗群組為 v3，後續群組完成度另見 CONTEXT。
- `go test -count=1 -p 1 ./...` 與 `go vet -p 1 ./...` 已以真實原版及角色群組通過。首輪被舊版來源存檔誤納入套件搜尋，新增該存檔的獨立 module 後同命令乾淨重跑；屬研究目錄隔離問題。四個角色版二進位重建，各保存編譯前後來源及輸出雜湊，再與 GUI 收據核對。
- README 已換上目前角色 HD、空中踢擊、雙跳與手把設定入口，舊比較稿與背景版收據保留歷史身分。完整 HD HUD、特效呈現、其他角色／場景／介面、完整回合、替代色盤及實體平台手把仍未完成，不將局部綠燈外推整個 Goal。
- 後續完成斬／法蘭克全部 144 個來源槽，共 117 組不同原始 bytes；十一張原始透明 PNG 含 121 張人物與特效圖，群組為 `hd-characters-study-v5`。特效圖仍未接入原生，不能把來源槽齊全當成完整動畫或 HD 特效完成。
- 最新 `native-actors-v6` 與 `windows-actors-v6` 各十四項，`native-actors-missing-v2` 十三項通過。新增 slot 56 退步的原生截圖與來源核對，兩平台各十三張六層擷取獨立重組通過。Linux 同狀態範例有 47,978 個原角色輸出像素改變，35,451 個最後原貌層像素保留；跨平台是不同即時執行，未宣稱跨平台同狀態。
- `windows-actors-v5` 的設定測試曾在三次快速點擊後只走到第二個角色。改成只讀前端更新序號及滑鼠持續狀態，驅動確認每次按下／放開均被取樣，乾淨重跑到 v6 通過。僅增加研究觀測欄位與測試等待，不改玩家的按鍵或滑鼠操作規則。
- 最新完整群組重新通過 `go test`、`go vet`，四平台中間二進位與逐目標編譯收據已更新。README、唯一現況、工作清單、003／008 及驗證矩陣均指向 v6；早期 v4／v5 收據保留原版本身分。下一步沿正常 R1 路徑查證並接入特效，再推進 HD HUD 及其他角色／場景。
- 最終 native-character-audit 通過原始資料、1715 份來源、四個實際編譯收據、十四／十四／十三項 GUI、144 槽群組及擁有權核對。16 份文件的 190 個本機連結與 Python 語法檢查通過；原版及衍生美術持續排除 Git。最新來源同步到獨立 Git 副本，完整備份放 workplace/github-native-hd.bundle；遠端未推送。
- 本批 Docker 測試容器均已結束並刪除，沒有新建 image。Docker 內 find 未發現 root-owned 檔案或誤建的 Markdown 目錄；沒有留下 Xvfb、Wine 或遊戲背景程序。

## 2026-10-19：特效切片與最新 GitHub 上傳準備

- 依規格 009 審查原版特效來源、第二色盤及順序，再接原生呈現。兩份探針共 1015 次 blit、483 格重組吻合，另獨立重組 19 個保存畫格。新素材在 study-v7 登錄 144 個正常槽與 13 個第二色盤特效鍵；原圖、提示詞及未採用圖仍保存在本機。
- Linux 的 native-effects-v3 十五項與 native-frank-effects-v1 十四項正常入口通過。獨立核對 16／15 張完整分層擷取；兩人的特效同狀態切換通過。真實 fixture 與舊版素材相容測試通過；開／關特效觀測的 456 個邊界原版狀態相同。四個實際編譯收據及檔頭已重新核對。
- native-effects-v1 曾碰到測試程式 180 秒退出期限；v2 混合兩人特效後未取得斬 R1 的預期路徑，尚未判明 GUI 原因。後續兩個特效案例各用乾淨正常對局驗證，未改快捷規則。核心控制實驗在兩種觀測設定均能於法蘭克出招後再到斬 24h；此結果不能代替失敗的 GUI 案例。
- windows-effects-v1 及 windows-frank-effects-v1 的正常入口等待逾時，本版 Wine GUI 尚未通過。保留失敗收據，前一角色版十四項不能代替目前特效版。HD HUD、其餘角色、完整回合、實體雙手把及真機仍未完成。
- 使用者要求建立 GitHub 儲存庫並上傳成果。主機 `gh auth status` 的提升權限呼叫遭環境自動核准政策拒絕，禁止 sandbox_approval。沒有取得主機憑證結果，沒有搬運憑證或改由容器 gh 繞過；遠端建立與 push 尚未完成。
- 最新自有程式、規格及文件同步到既有 `/tmp/kdzz-superfighter-publish`，保存為獨立 Git 提交及 `workplace/github-native-effects.bundle`。保留原版包、研究原圖、HD 衍生美術、二進位及本機設定的排除；Git 備份不等於遠端已建立。

## 2026-10-19：原生生命、計時與名字

- 前一 Goal 回合屬 progress：完成特效來源的 Git 提交 3807ee3 與完整備份。本輪回到 HD，沒有重試受權限政策拒絕的 GitHub 操作，也沒有縮減完整 HD 目標。
- Wine 初次特效驗證因正常入口等待逾時停止；同程式單獨重跑後到特效。原貌狀態與色盤相同，GPU 畫面卻有六個像素每通道相差一階。沿固定 Ebitengine 2.9.9 的 Unmanaged 契約改用獨立角色／特效紋理後，斬與法蘭克切回逐點一致。舊原圖、失敗收據與特效二進位均保留，未放寬比較容差。
- IDA 9.4 由正常主迴圈追到 BOARD.XBB、NAME.XBB、0-9.XBB、BOARD.COL 與原版介面繪製。hud-draw-v3 以普通鍵盤移動／拳擊打出第一次擊倒及第二回合，1176 次介面繪製、等值覆蓋均吻合。33 個原檔獨立重組樣本與顯示勝場鎖存審查後，規格 010 先升 READY，再接正式呈現。
- 生命使用原版逐格扣減的顯示值，計時使用原版數字。加入只讀 HUD 快照及原介面之前的原貌層；保留所有原圖層供逐點重組，再用原生高解析紋理畫名字／數字及生命條。勝場圖示、中央訊息與陰影仍原貌。沒有新增設定／存檔版本、按鍵、規則或原版寫入。
- 原生首版 native-hud-frank-v1 顯示玩家二標記殘留。BOARD.XBB 的獨立 fixture 重現後，改由原檔非零邊界取安全矩形，驗證所有應替換的 HUD 像素均納入。擷取腳本曾將 .hud-under.idx 誤當主 .idx 而漏複製，修正精確檔名比對後乾淨重跑，不補造舊側檔。首版二進位及精確編譯輸入另存原目錄。
- native-hud-frank-v2、windows-hud-v1、windows-hud-frank-v1 各十六項與各十六張完整分層擷取通過，含同狀態切換、設定重啟、失焦；法蘭克兩案例另驗實際扣血。native-hud-legacy-v1 十三項及缺件整張原貌回退通過。Windows 使用 Wine，實體平台與手把仍未驗。
- hud-core-compat-v1 的 456 個邊界在開／關觀測時原貌、色盤、角色、狀態與步數相同，取得 448 個完整 HUD 快照。hud-checks-v2.log 全套 go test 與 go vet 通過，33 個 HUD 與 19 個特效樣本沒有跳過。四個介面版二進位已重建並核對實際編譯來源、輸出與平台檔頭。
- native-hud-audit 核對 128 原檔、1715 份執行器來源及原有 1713 檔不變、四份編譯、157 個素材鍵與上述 GUI／回退，依此將 010 在明列範圍升 CONFORMED。README 換目前整合截圖入口，CONTEXT、WORKLIST、003／008 與驗證矩陣同步回填。剩餘 HD 及完整流程仍留待辦。
- 自有來源續存獨立 Git 副本及 workplace/github-native-hud.bundle，原版、衍生美術及二進位排除。最終文件、來源與 Docker 清理核對於本節後續記錄；未建立 Release 或正式發行包。
- 最終 native-hud-audit 通過目前編譯與三個十六項／一個十三項 GUI，18 份 Markdown 的 221 個本機連結、十個新增入口及 24 份 Python 語法核對通過。工作根沒有 root-owned 檔案或誤建的 Markdown 目錄，kdzz 容器清單已清空，沒有新建 image 或留下 Xvfb／Wine 背景程序。下一輪先驗原生完整回合、結果／返回與快照生命週期，再續陰影、勝場／回合及其餘美術。

## 2026-10-19：完整比賽驗證與執行環境受阻

- GitHub 回合只核對既有 989c1ca 原始碼 bundle 與獨立 Git 副本，未建立遠端。主機 gh auth status 的提升權限請求遭自動核准政策拒絕，沒有重新判定憑證或繞過限制。
- 本輪重新取得既有原生 GUI 工作 session 8448 的執行輸出，確認它仍在第二回合，而非只依狀態檔假定存活。之後同一 handle 回報退出碼 1，failure.json 記錄遊戲本身退出碼 0、步數 791,750,000。測試使用 900 秒自動結束，未完成第二次擊倒、結算與返回；這是驗證期限不足，不據此宣稱玩法故障。
- 原生四張擷取及其舊 comparison.json 只驗到正常對戰、首個擊倒、換場與第二回合，選用原貌與即時原版 RGB 相同。未擴張為完整比賽或完整 HD 通過。match-core-v1 的普通輸入收據另走完兩次擊倒至結果報紙，離開對戰後快照清空，但不代替 GUI 驗收。
- 調整 desktop_match_smoke.py：預設執行期限改為 1800 秒並可用 --quit-after-seconds 設定；失敗另記命令、實際經過時間及工具雜湊。調整 verify_match_capture.py：完整模式要求成功收據、兩次擊倒、八張具名擷取、事件核心一致及結果／返回的原貌來源；部分檢查必須指定 --partial，另寫 comparison-partial.json。
- 上述兩項工具調整尚未重跑。Docker socket 存取回報 permission denied，沒有改在主機執行測試、分析或遊戲。舊測試 session 99164 已無 handle，現存 log 只能確認測試輸出與已啟動 go vet，未取得退出碼，不能宣稱本輪完整檢查通過。
- CONTEXT、WORKLIST 回填實際結果與下一步。原版與 HD 衍生素材留在本機；本輪沒有 commit、push、正式封包或新 image。既有 GUI handle 已終止，但目前無法查 Docker 容器清單及清理狀態。恢復 Docker 存取後，先核對清理及檔案擁有權，再以新輸出目錄重跑完整比賽及獨立驗證，續做剩餘 HD。

## 2026-10-19：原生 HD 勝場與完整雙打返回

- 前一輪調整驗證工具屬 progress。本輪直接 Docker 呼叫可用；先前把複合主機指令的 socket 拒絕歸成整個 Docker 工具鏈受阻，判定過廣，已修正 CONTEXT。沿用既有映像，沒有在主機執行分析、遊戲或測試。
- 重跑前先驗兩份 Python 語法、四個二進位及 88 筆實際編譯輸入。native-match-v2 正常標題、雙打選角、普通移動及拳擊，完成兩次擊倒、結果報紙及 Return 返回標題，八張擷取通過。離開對戰後完整快照清空，兩張非對戰 viewport 逐點等於即時原貌；沒有改生命、勝負、座標或亂數。
- 勝場擴充前，把上述基準四個二進位、22 份精確編譯輸入及來源雜湊另存 native-match-v2/build-baseline。前一介面版二進位也已保留於 native-hud-frank-v2，避免新版覆寫後讓舊收據失去版本身分。
- NAME.XBB 的 10×12 拇指圖示及 93 點非零來源、兩側位置、勝場鎖存與 33 個真實 fixture 經獨立核對後，規格 011 由 DRAFT 升限定 READY。原生程式以高解析曲線重繪拇指，使用獨立 GPU 紋理；加入已鎖存勝場的精確非零替換，原始圖層及玩法核心不變。右側及第二圖示只有本輪靜態證據，仍列驗收限制。
- native-win-markers-v1 以目前勝場版正常取得首勝，七張擷取及原版六層獨立重組通過。三張暫停切換的核心、色號、色盤、快照與即時 RGB 相同，恢復 HD 的遊戲區逐點一致；勝場區已換新圖。與完整比賽基準相比，只有三份前端／HD 呈現檔改變，核心來源相同。這不把歷史完整比賽二進位改稱目前版本。
- win-markers-checks-v1 有兩項因環境變數誤寫為 KDZZ_HD_CHARACTER_ASSETS 而跳過。修正為既有測試使用的 KDZZ_HD_CHARACTERS 後，v2 全套 go test 與 go vet 通過，33 個 HUD／19 個特效 fixture 沒有跳過。後增的未獲勝區域拒絕檢查另以 win-marker-coverage-v1 重跑 33 個 fixture 通過。
- 比賽驗證工具現在分完整比賽、首勝圖示及明示部分檢查。完整模式會拒絕舊失敗收據；首勝模式核對同狀態切換；兩者均重組實際原版圖層並保存 PNG 及側檔雜湊。新增側檔雜湊檢查初次誤要求非對戰 frame.json，已依擷取契約改為只對有完整快照的畫格要求，未補造歷史側檔。
- 勝場版的 Linux、Windows、macOS Intel／Apple Silicon 已重建，核對四份編譯來源及 ELF／PE／Mach-O。建置腳本同步改為工作根唯讀、workplace 輸出可寫，原始資料與 dosgolem 別名唯讀。新勝場尚未跑 Wine 或實體平台；前版 Wine 收據不改名。
- 陰影以唯讀原 EXE 建立兩個一次性 IDA 9.4 資料庫，確認 SHADOW.XLP、固定地面列、兩人位置及透明繪製；第二人會直接落入 helper。只保存靜態證據，未接正式陰影。下一步由 dosgolem 普通輸入逐寫對拍，之後再審查 HD 陰影規格。
- README 加目前勝場截圖入口，CONTEXT、WORKLIST、驗證矩陣與較早規格回填現況。完整 HD、其他角色／場景／畫面、音訊、速度、實體手把與正式封包仍未完成。自有來源續存獨立 Git 副本及 github-native-wins.bundle；未建立遠端、push 或 Release。最終來源稽核、備份與 Docker 清理結果續記於本節。
- native-win-markers-audit 最終核對通過：128 原檔、1715 份執行器來源及原有 1713 檔不變、四份編譯、歷史完整比賽八張與目前首勝七張擷取。勝場矩形的背景變化不當作新圖示證據，另核對 254 個原版色盤沒有的原生金色筆畫像素。工作根未發現 root-owned 檔案或誤建 Markdown 目錄；GUI／IDA 容器均已結束，kdzz 清單為空。備份的提交與 bundle 身分記於 workplace/github-native-wins-source.json，不把本輪切片宣稱為完整 HD。

## 2026-10-19：原生柔邊陰影

- 前輪已完成勝場圖示與本機提交 9b5b72b，屬 progress。本輪沿唯一工作清單接續陰影；完整 HD 目標維持，未重開已完成的勝場、基本輸入或舊基準驗收。
- 普通雙打的陰影探針取得 772 次繪製、19 個獨立重組樣本及 5,002 次同值寫入。正常左邊界只有 X=0，未有負 X；保留靜態分支限制，不造測試狀態。來源與審查足夠後，規格 012 從 DRAFT 升限定 READY，再接正式程式。
- 勝場版四個二進位、22 份精確編譯來源及舊稽核先保存於 native-win-markers-v1/build-baseline。新增只讀陰影快照與原生柔邊，原版位置、裁切及繪製順序保留；重疊取最大 alpha。原版圖層不刪改，未知資料整格原貌，舊版 1 素材保留原貌陰影。未新增玩家設定、存檔或素材版本。
- shadow-core-compat-v1 比較 456 個邊界，原貌與狀態相同，取得 448 個完整快照及 24 個雙人畫格。全套 go test 與 go vet 通過，原檔與實際 fixture 沒有跳過；來源損壞、錯誤欄位／色盤與靜態裁切邊界拒絕另驗。
- native-shadows-v1 與 windows-shadows-v1 各十七項正常 GUI 通過，含雙人獨立放開、雙跳、特效、實際扣血、暫停、設定重啟及失焦。各十五張具名擷取完整重組，各十二張原生陰影 alpha／GPU 合成核對通過；Wine 不代替 Windows 真機。
- native-shadow-overlap-v1 以普通走近取得重疊，七張具名擷取與五張陰影合成核對通過，三張確有重疊；暫停三張來源一致、恢復 HD 逐點相同。native-shadow-legacy-v1 十三項、十一張具名擷取及缺件整張原貌通過。
- shadow-match-core-v1 由普通移動與拳擊完成兩次擊倒，兩次擊倒及第二回合陰影快照完整，結果報紙後清空。這是目前核心生命週期證據；原生完整比賽與返回標題仍保留 native-match-v2 的原二進位身分。
- 四個陰影版二進位已重建，原生擷取額外保存陰影之前／之後的 GPU RGBA 及原生 alpha。RGBA8 合成區間與原貌／HD 逐點一致分開驗；沒有放寬切換容差。具名擷取排除暫存 capture.png，不重複計數。
- README 換最新陰影畫面入口，CONTEXT、WORKLIST、矩陣與較早規格回填。下一步中央回合訊息；其餘角色、場景、畫面、完整動畫、音訊、速度、實體平台／手把及正式封包仍未完成。原版資料與衍生美術留本機，GitHub 未建立或推送。
- native-shadows-audit 核對 128 原檔、1715 份執行器來源與原有 1713 檔不變、四份實際編譯、772 次繪製、19 個獨立樣本、24 個雙人畫格、456 個觀測邊界及上述 GUI／生命週期後通過，012 依明列範圍升 CONFORMED。GUI、Wine、探針與一次性檢查容器已結束，kdzz 清單為空。來源提交及 bundle 身分保存於 workplace/github-native-shadows-source.json；本機備份不代表建立遠端或完整 HD 完成。

## 2026-10-19：原生開場 ROUND／FIGHT

- 前輪完成自有來源提交 d04670d 與完整 bundle，屬 progress；GitHub 沒有建立或推送。本輪繼續完整 HD Goal，沒有重試受權限政策拒絕的主機操作。
- 沿用 reverse-engineer-retro-game-remake 與 IDA 9.4 技能、規格閘門及既有 image。IDA 兩輪窄匯出保留原名／位址／bytes，定位 NAME 字圖、數字、開場窗口與部分背景。正常輸入 round-draw-v1／v2 各 66 次訊息；發現完整常式還有頂列拷貝後回到規格，再由 v3 核對全部 66 次完整常式與部分背景。
- 規格 013 經審查 READY 後接入只讀快照、頂列保留基底、原檔字圖重組與原生高解析字圖。延伸到整個常式返回才標完成，保留收合最後一格的 FIGHT 暫存拷貝。沒有改核心規則、時間、聲音、快捷、原始資料、素材清單或存檔格式。
- round-core-compat-v1 的 1,508 邊界在觀測開關兩側一致，全部 66 格來源與完整分層可重組。四階段、十二種窗口及末格拷貝均有 fixture；正式對戰清空訊息。新測試另拒絕錯誤來源、欄位、窗口、色盤與覆蓋；原圖層保持不變。
- 最初使用跨平台 image 直接執行全套測試，其預設 cgo=0 使 GLFW 編譯失敗，屬工具環境。round-checks-v3 改用既有 Linux image、明示 cgo=1 與 gcc，乾淨重跑全套 go test／go vet 通過，沒有跳過。Pillow 最初在缺件 image 失敗，改沿用已有鎖版 Pillow image，沒有在主機安裝或執行。
- 四個開場版二進位已重建，保存各自實際編譯輸入；陰影版四個二進位與 26 個輸入已於修改前保存至 native-shadows-v1/build-baseline，綁定 d04670d。Linux／Wine 開場各七項與十張具名擷取，部分窗口、完整 ROUND、FIGHT、三組暫停切回與訊息清除通過。每側六張 GPU 字圖擷取，窗口外完全不變。
- Linux 一般對戰十七項、十五張具名擷取與十二張陰影合成另驗；舊素材十三項、十一張具名擷取及缺件整張原貌通過。README 加目前開場畫面，003／008／010 回填 013 的已解來源與背景差異，沒有重寫舊收據版本身分。
- 開場頂端仍有 oracle CRTC 起點限制，勝負文字及其餘 HD 範圍未完成。正式封包、實體平台／手把、音訊與速度仍待驗。最終來源稽核、提交備份及容器清理身分續存本節後續記錄。
- native-rounds-audit 最終核對 128 原檔、1715 份執行器來源與原有 1713 檔不變、四份實際編譯、全部 66 格來源／完整常式／部分背景、1,508 比較邊界及上述視窗收據後通過，013 僅在第一回合範圍升 CONFORMED。工作根未發現 root-owned 檔案或誤建 Markdown 目錄，kdzz 容器清單為空。自有來源續存獨立 Git 副本與 workplace/github-native-rounds.bundle，提交及逐檔來源身分見 workplace/github-native-rounds-source.json；沒有建立遠端、Release 或正式封包。

## 2026-10-19：CRTC 顯示視窗候選

- 前輪完成原生開場、驗證及 9623266 來源備份，屬 progress。本輪追查開場頂端問題，命中復古平台規格優先路由；查 FreeVGA 原始技術文件與正式副本實作，沒有把標準 VGA 語意重新列成遊戲反組譯任務。
- display-ports-v1 由正常啟動與選角取得 67 格及全部埠。獨立重組確認可見 320×192、起點 3,840 bytes；原先不只露出頂端資料，亦漏掉可見尾四列。原貌重組預覽已目視確認，規格 014 對候選 API 升 READY。
- 正式 1715 檔及 go.work 不動。prepare_linear_scanout 建獨立研究副本，原檔逐字不變，新增 machine／oracle 各一份 API 與測試，共 1719 檔；候選自己的 go.work 用 GOWORK 明示啟用。沒有改共享 dosgolem 或把候選無聲接進玩家入口。
- 候選單元與相鄰原契約回歸、go vet 通過，沒有跳過。測試含完整尾列、起點／列距、只讀與複本、兩種保存還原及 17 個拒絕分支。新 API 保留舊 Indexed／Screen；未知平移、分割或越界映射回錯誤。
- linear-scanout-api-v1 先通過 67 格；為補齊原生尾列來源，v2 追加場景、相機與背景身分再乾淨重跑。67 格仍與獨立顯示重組相同，呼叫前後與舊 API 不變；全部尾四列都能由原背景重組。原生仍須逐格檢查尾列，不把研究樣本當通用無前景假定。
- linear-scanout-audit 通過正式來源、候選四檔、67 格及現行四個二進位身分核對。現行 9623266 二進位與 30 份精確編譯輸入已另存 native-rounds-v1/build-baseline；沒有重新建置或冒稱原生視窗已修正。
- README、CONTEXT、工作清單及驗證矩陣分清候選輸出與原生接線。下一步將原貌、全部 HD 圖層與尾四列一起套用顯示映射，再續勝負訊息及完整 HD 範圍。來源備份、最後擁有權與容器清理核對續記於本節。
- 候選最終稽核通過，正式來源、現行編譯輸入及四個二進位未變；沒有 root-owned 檔案或誤建 Markdown 目錄，研究容器均已結束。自有工具、候選新增來源及文件保存至獨立 Git 副本與 workplace/github-display-candidate.bundle，提交及逐檔身分見 workplace/github-display-candidate-source.json。原生接線與完整 HD 仍未完成，沒有建立 GitHub 遠端或發布封包。

## 2026-10-19：原生顯示映射與完整尾列

- 前輪保存 ce68420 來源與 github-upload-ready.bundle，屬進展；GitHub 無法連線且連線外掛未接通，沒有建立或推送。這輪續做 HD，沿規格 015 的 READY 契約接入。
- 安裝後 1719 份執行器來源與 v2 備份核對通過，原有 1715 檔不變。核心明示啟用只讀顯示快照，同格保存舊 64,000 bytes、原圖層、真實尾端 1,536 bytes 與實際可見色號；舊 RGB／Indexed 語意不變。
- 原生畫面共用可見矩形與 VRAM 合成原點，背景、人物、特效、HUD、勝場、陰影及開場字圖一起投影。每像素保持 3×3，320×192 居中；完整保留可見尾端，逐格來源不符則整張原貌。
- 全套 Go 測試及 go vet 通過；新增 67 個真實顯示／尾列 fixture 與未知幾何、尾端前景拒絕檢查。安裝後 API、17 拒絕分支、兩種保存、只讀複本測試通過。display-core-compat-v1 的 1,508 個開／關邊界狀態、舊畫面、即時 RGB 與原圖層相同，66 格由原檔及尾端完整重組。
- Linux／Wine 開場各七項、十張擷取與六張 GPU 字圖通過。一般對戰十七項、十五張擷取與十二張陰影合成；舊素材十三項、十一張擷取及缺件整張原貌均通過。四個二進位已重建並核對實際編譯來源與檔頭。
- 首跑原生因容器漏掛 /orig 結束，補掛後乾淨重跑。一般與舊素材同跑均在 45 秒啟動門檻逾時，核心當時仍在前進；未修改產品或拉長腳本期限，改逐一以相同 image／命令重跑後通過。失敗目錄保留原身分。
- 首版彙總稽核誤將開場第十二列寫死；實際正常跳躍／踢擊已驗到第 11、7 列。改依當格 CRTC 與原版欄位核對，沒有放寬像素比較。原貌、HD 與獨立重組都已使用當格幾何；四個案例共 46 張映射擷取稽核通過。
- 規格 014／015 限定 CONFORMED，006／013 回填接入勘誤；README 更新整合畫面，CONTEXT／WORKLIST／驗證矩陣指向新稽核。完整 HD、後續訊息、其餘角色／場景／完整動畫、實體平台與雙手把、音訊、速度、正式封包仍未完成。
- 自有來源續存獨立 Git 副本及 workplace/github-native-display.bundle，逐檔來源與備份身分見 workplace/github-native-display-source.json。原版、衍生美術、收據與二進位繼續排除；沒有遠端或 Release。最後來源核對、擁有權與容器清理於本輪收尾驗證。

## 2026-10-19：再次整理 GitHub 上傳來源

- 使用者再次授權建立儲存庫並上傳成果，沿用預定私人儲存庫 `wicanr2/superfighter-remastered`。受限環境的登入檢查失敗；主機權限檢查遭 granular 權限政策拒絕。未取得主機登入狀態，也沒有建立或推送遠端。
- 保留既有 `main` 的顯示修正驗證版本。勝負文字、WIN.FIG 來源辨識及姿態接入的最新開發中程式另存 `wip/victory-hd`，不把尚未整合驗證的來源當作完成版本。
- 完整來源備份保存於 `workplace/github-upload-latest.bundle`，來源清單與分支提交另存 `workplace/github-upload-latest-source.json`。只納入自有來源、文件、授權字型與既有設定截圖，排除原版、衍生美術、收據、二進位與本機設定。本輪不改遊戲實作，不重新建置或執行遊戲。

## 2026-10-19：正常首勝文字與獨立勝利姿態接入

- 前輪屬進展：保存 86f67a7 開發中來源與完整 Git 備份，GitHub 仍受權限政策限制。本輪回到完整 HD Goal，未重試被拒絕的遠端操作。命中規格閘門、文件職責、README 及結論回填路由。
- 延續勝負文字證據：原版先重建介面、拷貝畫面，再直接寫入 NAME 文字。重建前於 runtime 33F4h、返回 5E77h 重開最後光柵觀測，保留兩份 2884-byte 暫存字圖與新 HUD。重建後的原背景未改，原貌也保存完整 WIN。定位、推論等級及兩側原版證據補入 RESEARCH-LOG。
- 初次成對工具因勝利人物不是 SFMAN 同槽來源而拒絕，失敗保存於 victory-core-compat-v1；單核心 diagnostic-v1 只定位來源。IDA 指出 WIN.FIG 的 60h 表及 180h 圖像基底。兩原檔 144 個入口、七個不同來源已核對，圖像群組與色盤群組分開，不改原槽號。
- 內建 image_gen 的七張透明勝利姿態登錄於版本 3 的 hd-characters-study-v8，共 301 姿態鍵、四份原檔、十五張 PNG。舊 157 鍵及十三張 PNG bytes 不變；未知表、來源不符與缺件整格原貌。新 Go 測試驗 RAM 表辨識、群組隔離、144 個 WIN 入口與舊格式拒絕，完整測試及 go vet 通過。
- 首跑檢查使用容器 login shell，PATH 被重設而找不到 gofmt；改用同一 image 的非 login shell 重跑後通過，屬環境問題。記錄為 victory-checks-v2.log。沒有改主機工具鏈、共享 dosgolem 或原始資料。
- victory-core-compat-v2 由正常標題／選角／移動／拳擊取得首勝，1,479 個觀測開／關邊界的原版狀態及即時 RGB 相同。兩格完整來源、圖層、WIN 圖像與文字、HUD、陰影及可見尾端由獨立 Python 核對；下一回合清除勝負快照並顯示勝場 [1,0]。
- Linux native-victory-v1 與 Windows Wine windows-victory-v1 各七張具名擷取通過。斬鞠躬與 JAAN WIN 同格 HD，原貌／HD／恢復的核心與來源相同，恢復畫面逐點一致；兩平台各兩張 GPU 字圖均只寫入原矩形，各有 4,190 個變動像素、1,191 個金色實心像素。
- native-victory-legacy-v1 以舊版 2 素材走同一正常路徑，七張擷取核對通過；缺 WIN 姿勢時三張切換全部等於完整原貌，下一回合恢復 HD。獨立檢查最初誤從 capture.json 讀取 presentation，修正為由逐次 observe 事件讀取，並與實際擷取核心／旗標／serial 交叉核對；同一容器重跑後通過，沒有改產品或像素判準。
- 規格 016／017 依上述限定範圍升 CONFORMED，008 回填 WIN 圖像來源，README 加最新勝利圖及手把／四格入口說明，CONTEXT、WORKLIST 與驗證矩陣更新。原版證據是兩個不同正常勝者、四筆重播；修正 review 曾把四筆當作四組的計數。
- 四個中間二進位已重建並核對來源及檔頭。native-victory-audit 通過 128 原檔、1719 份來源且原 1715 檔不變、四份實際編譯、301 姿態鍵、核心與二十一張原生擷取。前版 5c1bf7c 四個二進位及 30 份編譯輸入另存 display 基底，舊收據不換版本身分。
- 第二人正常勝利 HD、完整勝利動畫、其他角色／場景／畫面、替代色盤、其他快捷、實體平台與雙手把、音訊、速度及正式封包仍未完成。Goal 保持 active。自有來源續存獨立 Git 副本與 github-native-victory.bundle，逐檔身分見 github-native-victory-source.json；原版、衍生美術及二進位繼續排除，未建立遠端或 Release。
- 收尾核對 25 份 Markdown 的 353 個相對連結及全部 Python 語法通過；未發現 root-owned 檔案或誤建 Markdown 目錄。Wine 前綴的 z: 連結以 lstat 核對連結本身，不把其指向的容器根誤報為專案檔案。所有本輪核心、建置、Xvfb／Wine 與檢查容器均已結束，kdzz 容器清單為空。

## 2026-10-19：第二人首勝與下一角色候選

- 前輪為進展：be9a6d3 接通斬首勝人物與文字、同狀態切換及舊素材回退。本輪沿規格與驗收路由續作，Goal 保持「完成快打至尊HD」，沒有重試被環境拒絕的 GitHub 操作。
- 正式 Go 程式與四個二進位不變。研究工具增加第二人普通輸入及回合結束後的姿態取樣；兩側各以 baseline／observed 核心比較，取得 5,293／5,534 個邊界、13／8 個 WIN 快照。完整圖層與五種姿態來源獨立重組通過，下一回合勝負 metadata 清除。
- Linux native-frank-victory-v1 以第二人正常操作取得時間結束勝利，七張擷取通過來源、WIN、抱胸、右側首勝、恢復 HD 逐點一致及下一回合 [0,1]。兩張 GPU 字圖各有 5,130 個變動像素、1,444 個金色實心像素。README 加入目前法蘭克勝利畫面。
- Windows 第一輪在等 180 個畫格時逾時，但原版仍推進到 404M 步、431 格，並未當機。保留 windows-frank-victory-v1 的失敗。畫格觀測改以 180 秒無進展為逾時，整局仍以 1800 秒、外層 1950 秒封頂；沒有改遊戲步速、像素判準或勝負。讀取 cgroup 的 nr_throttled 為零，沒有據此提高 CPU 配額。
- Windows 重跑為 windows-frank-victory-v2，執行 session 95060、容器 kdzz-windows-frank-victory-v2，仍在單獨執行。這是有界且有 finally 清理的現行工作，尚無完成收據；下一輪先核對同一 handle，不因觀測期限重新啟動。新 audit_victory_animation.py 會要求兩側核心及第二人 Linux／Wine 全部案例，缺件即拒絕，不產生假通過。
- 薩爾可夫 SFMAN02 解析 72 個入口、45 組不同來源。正常選角 v1 實際選到 1／5，保留研究身分；從原游標行為修正輸入後，v2 為 1／4、124 格來源及屋頂背景全部吻合。NAME 槽 1 重新核對為八字母 SARORKOV；初稿漏記第二個 R 已訂正，設定 ID sarkov 不變。
- 沿用內建 imagegen 技能，依原像素姿態與既有手繪風格生成薩爾可夫 45 張姿態。四張採用 PNG 與精確提示詞存 sarkov-art-v1；首張留白不足的九格稿被登錄器拒絕，另生 03-v2 並保留原稿。沒有改原 PNG bytes 或放寬透明分隔。一次 Docker 指令的 socket 拒絕改以儲存庫檔案編輯保存請求，未提升權限或改在主機執行工作負載。
- prepare_character_extension 準備 373 鍵候選，保留舊 301 鍵及十五張 PNG，新增 72 槽／四張圖集。TestSarkovCandidateMatchesNormalOriginalSources 與 hd 套件 go vet 通過，核對全部入口、舊基底不變及 124 個正常 consumer。正式原生仍用 v8；候選不當作第三名角色已完成。規格 018 READY，下一步依契約接人物與原姓名。
- be9a6d3 的 35 份精確編譯輸入、四個二進位及編譯收據另存 native-frank-victory-v1/build-baseline，供下一角色實作前保留基準。自有來源續存獨立 Git 副本及 github-victory-animation-progress.bundle，身分見 github-victory-animation-progress-source.json；原版、衍生美術、研究資料及二進位仍排除，遠端未建立或推送。
- 完整動畫、Wine 第二人、薩爾可夫原生、其他角色／場景／畫面、快捷、替代色盤、音訊、速度、實體平台與雙手把及正式封包仍未完成。只保留上述明示的 Wine 有界工作，其他本輪容器均已結束；擁有權、文件連結與原檔檢查於本輪保存時核對。
- 保存前核對 26 份 Markdown、372 個相對連結、全部 Python 語法、128 原檔與 1719 執行器來源通過；沒有 root-owned 檔案或誤建 Markdown 目錄。舊文件／測試檔名已以 grep 反查無遺留引用。四份二進位重驗檔頭及實際編譯輸入通過，沒有重建未改的正式程式。Wine 第二人仍為唯一執行中的本輪容器，結束後才跑完整兩側稽核。

## 2026-10-19 GitHub 建立與上傳狀態複核

- 使用者再次要求建立儲存庫並上傳成果，沿用私人 wicanr2/superfighter-remastered 的準備設定。
- 受限環境 gh auth status 失敗，git ls-remote origin 無法解析 github.com。先前主機權限提升遭自動核准政策拒絕，本輪未重試或搬運憑證；不能由受限檢查判定主機憑證失效。儲存庫建立及 push 仍未完成。
- 獨立 Git 副本的 162 檔、17,628,233 bytes 與工作根逐檔一致，常見憑證格式掃描無命中，既有 github-victory-animation-progress.bundle 通過完整歷史驗證。原版、衍生美術、研究資料與二進位排除；未驗收的四檔薩爾可夫變更仍留在 feature/sarkov-hd。
- 本輪只更新現況與工作歷程，續存獨立 Git 副本及 workplace/github-upload-20261019.bundle。未改程式或重跑產品測試。Docker 檢查容器均以 --rm 結束，工作根沒有 root-owned 檔案或誤建 Markdown 目錄。

## 2026-10-19 薩爾可夫一般姿態與姓名原生整合

- 核對既有工作狀態後，windows-frank-victory-v2 已在 1800 秒上限結束，最後計時剩 4、生命 76／124。保留 failure.json，不當作通過或產品缺陷，也沒有再盲目重跑整場。
- 在隔離 feature/sarkov-hd 工作樹擴充 HUD 姓名白名單，讓來源選擇回傳 SARORKOV，桌面沿用同一份標籤。未改設定 ID、核心、輸入或資料格式。建置工具可指定輸出位置並停用 VCS 自動蓋章，保留精確編譯輸入。
- 四個候選二進位及完整程式測試先完成。v1 操作腳本在落地前按拳卻等待地面姿態，保留三份 harness-abort.json；v2 等回到站立再送下一動作，沒有放寬像素或來源判準。
- native-sarkov-v2／windows-sarkov-v2 各七項、九張擷取通過；native-sarkov-missing-v2 另九張整格原貌。verify_sarkov_capture 從原檔重組人物、背景、介面及陰影，驗暫停來源相同與恢復 HD 逐點一致。Linux／Wine 截圖已目視姓名、人物與畫面配置，沒有稱跨平台同狀態對拍。
- TestSarkovHUDUsesNormalCapturedName 使用正常視窗的真實 HUD，驗 88×11 姓名矩形、SARORKOV／FRANK 及未知角色拒絕。sarkov-integration-checks-v2.log 記錄全部 internal／cmd 套件測試及 go vet 通過。
- 初次圖片核對選用的跨平台建置 image 沒有 Pillow，改用既有 sc-cht-hdtools:pillow11.3.0-r1 完成同一核對；分類為驗證環境問題。沒有在主機安裝或執行替代工具。
- 核對 be9a6d3 舊四份二進位已有 build-baseline 完整副本後，將已驗候選及其原編譯收據原封移入 bin，保留 sarkov-build-v1/promotion.json。只刷新彙總來源收據，沒有重建未改的編譯輸入。
- 018 升限定 CONFORMED，README 加入目前薩爾可夫畫面，CONTEXT／WORKLIST／驗證矩陣同步。WIN、替代色盤、快捷、完整動畫、其餘角色與畫面、音訊、速度、實體平台及手把、封包與 GitHub 遠端仍未完成；完整 HD Goal 保持進行。
- 本輪來源及完整歷史備份保存為 workplace/github-sarkov-integration.bundle，逐檔來源與產物身分見 github-sarkov-integration-source.json；收尾來源核對見 sarkov-integration-audit.json。原版、衍生美術與二進位排除 Git；本輪容器均以 --rm 收尾。

## 2026-10-20 薩爾可夫勝利實作與子彈候選

- 開工核對 main 636f6ad、工作樹及容器，先前一般姿態已完成。命中規格閘門與原版對拍路由，沿用內建 imagegen 技能及既有 Docker 工具鏈。
- BBWIN.FIG 解出 72 個有效入口、五組不同 bytes，色盤與 SFMAN02 相同。新增角色選擇旗標後，普通選角 1／4、方向及拳擊取得第一人正常勝利；單核心診斷六格獨立重組，實際 winner=1、生命 124／0、計時 21、SARORKOV／WIN 的 caller、SI 與矩形均吻合。
- 五張透明勝利稿以內建 imagegen 生成，原 PNG、精確提示詞及透明登錄存 sarkov-victory-art-v1。WIN 準備工具接受既有版本 3 擴充，保留舊 373 鍵及十九張 PNG，形成 445 鍵／二十張 PNG／六份來源。019 經 DRAFT 與來源審查升 READY，再補角色 1 勝負姓名。
- TestSarkovVictoryUsesSeparateOriginalBank 驗全部新來源、六個正常凍結畫格、原姓名及未知／位置拒絕、舊 373 鍵缺 WIN 回退；完整程式套件測試與 go vet 通過。四個候選編譯完成並核對來源。舊 636f6ad 的 35 份精確輸入及四個二進位先存 diagnostic-v1/build-baseline，沒有覆寫 bin。
- sarkov-victory-core-v1 的 9,290 個成對邊界、23 個 WIN 取樣、六個保存畫格及下一回合清除通過，原版狀態及 RGB 相同。四種 WIN 槽為 0／2／3／4，槽 1 仍只有靜態來源與登錄。
- Linux、Wine、舊素材三個正常首勝工作仍有界執行，session 71285／23441／8314，容器及輸出見 CONTEXT。各程式 2400 秒、外層 2550 秒，沒有動遊戲速度或強制勝利。下一輪核對同一 handle，不重啟正在執行的工作；原生尚未通過，不升 019 CONFORMED 或移入 bin。
- 等待期間準備子彈來源：正常 2／4 選角取得 124 個一致來源及屋頂，SFMAN03 有 58 組不同圖像、72 槽；NAME 槽 2 為 BULLET／62×11，已目視原字圖與正常畫面。五張內建 imagegen PNG 與提示詞存 bullet-art-v1，槽 41 保留全藍受擊閃光。
- 517 鍵／25 張 PNG 的子彈候選保留 445 鍵基底。TestBulletCandidateMatchesNormalOriginalSources 通過，驗 72 槽、58 組來源、124 個正常 consumer 與 15 槽覆蓋。020 經來源審查升 READY，尚未補姓名或人物到原生。
- 來源續存 wip/sarkov-victory 與 github-sarkov-victory-progress.bundle，身分見 github-sarkov-victory-progress-source.json。main 保留已驗一般姿態；新勝利與子彈仍是進度保存。原版、衍生美術及二進位不入 Git，沒有建立或推送遠端。
- 本輪一次性容器均 --rm；只保留上述三個仍需要的有界原生驗證。未建新 image，沒有主機工作負載、root-owned 檔案或誤建 Markdown 目錄。完整 HD Goal 保持進行。

## 2026-10-20 子彈一般姿態整合與勝利驗證結果

- 隔離 feature/bullet-hd 加入原姓名 BULLET，使用正常擷取 HUD 驗 62×11 字圖及未知角色拒絕。完整 internal／cmd 測試與 go vet、後續 HUD 定向測試均通過。未改原版核心、輸入或設定格式。
- native-bullet-v1／windows-bullet-v1 各七項、九張擷取通過正常選角、行走、蹲、跳、拳及同狀態切換；native-bullet-missing-v1 九張均整格原貌。獨立工具由原檔重組來源、圖層、陰影及姓名，並核對切回 HD 逐點一致；已目視 Linux／Wine 圖片。
- 020 限定 CONFORMED。517 鍵／25 PNG 群組保留既有來源，四個候選二進位與原編譯收據移入 bin；promotion.json 保存身分。Win 基底的 35 份輸入及四個二進位另存 native-sarkov-victory-v1/build-baseline，不把舊收據外推到新二進位。
- 薩爾可夫 Linux 與舊素材首勝各七張完整通過。Wine 在 2400.01 秒期限結束，僅六張勝利／切換；新增 --partial-native 僅核對已取得畫面，保存 animation-comparison-partial.json，明列 full_scenario_complete=false。沒有偽造下一回合收據，019 保持 READY。三個首勝容器均已結束。
- 鳳凰正常來源 61 組及 124 個 consumer 通過，內建 imagegen 首批十二張候選保存於 phoenix-art-v1。首稿拒用與修正版、提示詞及透明合成預覽保留；其餘 49 張、完整素材與原生尚未完成。
- Wine CPU 診斷 v1 含 F12 PNG 開銷，不能代表平常對戰。v2 已完成：正常 HD 後 20.003 秒不截圖／不送輸入，推進 875 萬步與 14 格；15 秒取樣以原生圖形呼叫為主，commandQueue.flush 至 purego.SyscallN 約 51.2%，Game.Draw 約 3.37%。未依此猜改遊戲。v3 沿用診斷二進位，只比較 DirectX；有界容器狀態見 CONTEXT。
- feature/bullet-hd 的 5d4400d 已合入 wip/sarkov-victory，整合提交 5c9cbd6。README、現況、清單、驗證矩陣與 019 補上實際範圍；完整 HD 仍未完成。

## 2026-10-20 GitHub 建立與上傳準備

- 使用者要求建立 GitHub 儲存庫並上傳成果。沿用既有私人目標 wicanr2/superfighter-remastered；不擴張為公開發布或 Release。
- 主機 gh auth status 的 require_escalated 呼叫被自動權限政策拒絕，命令未執行，不能據此判定主機憑證失效。沒有改以容器讀取主機憑證或繞過拒絕。GitHub 插件查詢顯示尚未連接，且七日內已建議過，未重複推送安裝提示。
- 最新 166 份自有來源與文件整理到既有獨立 Git 副本 /tmp/kdzz-superfighter-publish。保留 main 已驗基底及 wip/sarkov-victory 最新實作，不以未完成勝利流程覆蓋穩定分支。原版資料、HD 衍生美術、私有 dosgolem、收據、二進位與快取仍排除。
- 本輪準備完整歷史備份 workplace/github-bullet-integration-progress.bundle，逐檔來源及稽核存 github-bullet-integration-progress-source.json。遠端建立與推送仍受環境權限限制，不能聲稱已上傳。
- 保存前確認 v3 已完成 receipt，沒有 failure；20.001 秒區間推進 1000 萬步／16 格。保留 CPU 原樣本供後續判讀，不用單次結果聲稱換後端有效。相關診斷容器已全部結束，kdzz 容器清單為空。

## 2026-10-20 鳳凰一般姿態與原姓名整合

- 上輪 0150a9d 保存完整 Git 上傳前核對，遠端仍受環境權限限制。本輪依完整 HD 目標繼續，沒有重試 GitHub 登入或搬運憑證。
- 沿用內建 imagegen，補齊鳳凰其餘 49 組來源。六張採用 PNG、61 組姿態、九份精確請求在 phoenix-art-v1；02／04 初稿因無完整透明分隔被拒絕，保留原稿與原因後，只重做留白。原 PNG bytes 不改，透明登錄門檻不放寬。
- NAME 槽 3 解碼並目視為 PHO HUANG／93×11，檔案偏移 0874h，完整字圖 SHA-256 be3a0b687780fc71d73935f00062b26c8cd814d45db4617b967122fa13faead9。不改設定識別字 phoenix。完整來源及工具身分見 phoenix-evidence-review.json 與規格 021。
- 589 鍵／31 PNG／八份來源的完整候選保留原 517 鍵及所有舊 PNG。Go 嚴格讀取器驗 72 槽、61 組來源及 124 個正常 consumer 通過後，021 由 DRAFT 升 READY。原候選測試來源另存 phoenix-source-v1/candidate-test-source.go，與審查時雜湊吻合。
- 在隔離 feature/phoenix-hd 補姓名白名單及角色 3 的普通操作／獨立核對工具。未改原版核心、輸入、資料格式或設定。完整 internal／cmd 測試及 go vet 通過；正常原生 HUD 的 PHO HUANG／93×11 與未知拒絕另有定向測試通過。
- 初次隔離工作樹沒有供子掛載使用的 workplace 目錄，唯讀掛載時容器未啟動；建立正確的 UID 1000 掛載點後，用相同工具鏈重跑，四個候選編譯及檔頭／35 份輸入核對通過。沒有另建映像或在主機執行工作負載。
- Linux GUI v1 使用建置映像時缺 xdotool，零步結束；兩份環境失敗原封保留。確認既有三平台映像有 Xvfb／xdotool、ldd 無缺件後，同一普通操作流程在 v2 乾淨重跑。未改原生二進位或放寬驗收門檻。
- native-phoenix-v2／windows-phoenix-v1 各七項、九張擷取，native-phoenix-missing-v2 九張整格原貌，全部由原檔獨立重組通過。兩平台各自恢復 HD 逐點一致，核心、來源、設定與裝置指派不變；不稱跨平台同狀態。鳳凰輸出變動 18,099 點，姓名 9,207 點；字形、人物與跳躍另目視確認。
- 021 升限定 CONFORMED。8f70fc5 完成隔離接入，bb5adef 合入 wip/sarkov-victory；README 加入目前鳳凰及跳躍圖片。四個已驗候選及原編譯收據原封移入 bin，記錄為 phoenix-build-v1/promotion.json；舊子彈四份保留於 bullet-build-v1/bin，來源由 phoenix-pre-integration-baseline.json 綁定。
- 另完成 Wine CPU 診斷判讀及固定 Ebitengine v2.9.9 後端契約核對，輸入雜湊見 desktop-performance-v3/analysis.json。兩個單次區間不構成效能修復證據，未改步速、遊戲、文字或正式後端，也未盲目重跑長勝利案例。
- 下一角色鬼丸已解出 72 槽／66 組原圖。初次正常來源探針實際為 5／1，保留失敗，不冒稱 5／4；選角診斷另存原始畫面，未將錯誤對手套用屋頂或候選。
- 完整 HD、鳳凰 WIN／快捷／特效與完整動畫、其餘角色／場景／畫面、Wine 勝利下一回合、實體平台及雙手把、音訊／速度與正式封包仍未完成。Goal 保持 active。自有來源保存於獨立 Git 及 workplace/github-phoenix-integration-progress.bundle；原版、衍生美術、研究資料與二進位不入 Git。
- 鬼丸後續以一個普通 Left 選到法蘭克，hd-frame-onimaru-v2 共 124 格的實際 5／4、完整圖像 bytes 及屋頂來源全部吻合。私有探針來源 SHA 與收據相符，沒有修改正式工具或原版狀態。原先七次 Right 的錯誤對手及逐步圖保留，原因未證實；不深挖已不阻塞本角色來源準備的選單內部。
