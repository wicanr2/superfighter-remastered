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

## 2026-10-20 鬼丸一般姿態與原姓名整合

- 上輪 9a123c5 完成鳳凰限定切片。本輪核對工作樹及容器後，沿完整 HD 目標繼續鬼丸，沒有重試 GitHub 權限或重新開啟已完成切片。
- 依原圖製作灰綠駝背、紫袍、尖義足與彎頭木杖，保留槽 35 的獨立木杖／小手及槽 41 的全紫／白外線。內建 imagegen 共八份精確請求，六張採用 PNG 對應 66 組不同來源，保存於 onimaru-art-v1。
- 最後六格的初稿及背景修正版均沒有 Alpha 255，最大值 254，被未改動的登錄器拒絕。保留原稿及拒用紀錄，重新從原姿態與已通過首稿生成 v3 後通過；沒有程式改 PNG、放寬檢查或切換 CLI／模型。
- NAME 槽 5 的 72×11 字圖目視為 ONIMALU，第六字母遮罩等於 BULLET 的兩個 L，並與 SARORKOV 的 R 不同。實檔偏移 0EC9h，完整字圖 SHA-256 f042edee422d72080dde3af3da8b9a627d0247284fad2dde731ae90e40c1b55f。畫面保留本包拼法，設定 ID onimaru 及中文名鬼丸不變。
- 661 鍵／37 PNG／九份來源群組保留原 589 鍵與全部舊 PNG。Go 嚴格讀取驗 72 槽、66 組來源及 124 個正常 consumer，通過後 022 由 DRAFT 升 READY。DRAFT 原文與來源身分在 onimaru-evidence-review.json，原候選測試來源另存 onimaru-source-v1/candidate-test-source.go。
- 隔離 feature/onimaru-hd 只補姓名與普通操作工具。第二人採已驗的普通 Left 路徑選法蘭克，未改核心、資料格式、步速、設定或快捷。完整 internal／cmd 測試及 go vet 通過；真實原生 HUD 的 ONIMALU／72×11 與未知角色拒絕另驗通過。
- 四個候選使用 Go 1.24.13，ELF／PE／兩種 Mach-O 及精確 35 份編譯輸入通過。沿用既有建置與三平台 GUI 映像，未新建映像、在主機執行工作負載或更動共用 dosgolem。
- native-onimaru-v1／windows-onimaru-v1 各七項、九張擷取通過；native-onimaru-missing-v1 九張整格原貌。獨立工具由原檔重組人物、背景、陰影與姓名；各自恢復 HD 逐點一致，核心、來源、設定及指派不變。鬼丸輸出各變動 17,316 點，姓名 7,128 點；字形及造型位置另與原貌目視核對，不稱跨平台同狀態。
- 022 升限定 CONFORMED。c2f95b6 完成隔離接入，b4f7e79 合入進度分支。README 加入鬼丸目前畫面及跳躍；四個已驗候選與原編譯收據原封移入 bin，記錄為 onimaru-build-v1/promotion.json。舊鳳凰四份保留於 phoenix-build-v1/bin，由 onimaru-pre-integration-baseline.json 綁定。
- 下一角色嵐已解 72 槽／59 組原圖，hd-frame-lan-v1 正常 6／4 共 124 格的完整 bytes 與屋頂吻合。私有探針使用第二人普通 Left 兩次，來源 SHA 與收據相符，尚未生成 HD 或接原生。
- 本輪建置、正常來源探針、Xvfb／Wine 與三個 GUI 案例容器均已結束。沒有重啟舊勝利工作；019 的 Wine 下一回合仍未驗完。完整 HD、其餘角色／場景／畫面、各角色 WIN／特效／快捷及完整動畫、實體平台／雙手把、音訊／速度與正式封包仍待完成，Goal 保持 active。
- 自有來源、文件及完整 Git 歷史保存於獨立副本與 workplace/github-onimaru-integration-progress.bundle，逐檔身分見 github-onimaru-integration-progress-source.json。原版、衍生美術、研究資料與二進位仍排除 Git，遠端未建立或推送。
- 收尾工具先誤用舊角色成功標記，再以不存在的 effect 欄位分類，將 13 個 palette_bank=1 入口算入一般槽。對照實際日誌、manifest 及 Go 型別後修正工具，保留一般 432／特效 13／WIN 216 的原預期，未改素材、程式或產品驗收門檻；乾淨重跑收尾核對。

## 2026-10-20 嵐一般姿態與姓名整合

- 前一輪 GitHub 工作因主機權限政策拒絕而未建立或推送，對 HD 目標沒有進展。本輪核對現況、工作樹及容器，沿復古重製路由與內建 imagegen 繼續嵐，未重試 GitHub 權限。
- 依 SFMAN07 的 59 組原圖製作六張圖集，保留紅長衫、白袖口、深褐褲及原側。獨立氣勁與槽 39 的褐色輪廓依原圖保存，不自行推定觸發條件。原參考最後十一格拆成八格與三格；只整理原圖參考，未以程式修改生成美術。
- 八格初稿因第二排第三、四格沒有完整透明間隔而拒絕，診斷在 lan-art-v1/rejected-04.json。內建工具重排 v2 通過，原稿及七份精確請求保留；六張採用 PNG bytes 不變，沒有放寬透明或來源門檻。
- 原姓名為 LAN，NAME 槽 6、實檔偏移 11E3h、31×11；原字圖 SHA-256 2e79ac33da75905e9f9e9cfa6347083f8170594bb87d3b6a7f397e47354edf41。設定 ID lan 及兩人逐角色四格格式保持原狀。
- 候選 733 鍵／43 PNG／十份來源保留舊 661 鍵與所有舊 PNG。Go 嚴格讀取驗 72 槽、59 組來源及正常 6／4 的 124 格，通過後審查升 READY。DRAFT 原文、提示詞、來源及初始測試身分保存於 lan-evidence-review.json。
- 隔離 feature/lan-hd 只補 LAN 姓名及普通操作核對工具。Linux／Wine 以正常選角各完成行走、蹲、跳、拳及切換七項、九張擷取。每個案例內核心、來源、設定及指派不變，恢復 HD 逐點一致；缺件九張整格原貌。獨立重組、造型及字形目視通過，023 升限定 CONFORMED。
- 完整 internal／cmd 測試與 go vet 通過，真實原生 HUD 的 LAN／31×11 與未知拒絕另驗。四個候選的 ELF／PE／兩種 Mach-O 及 35 份編譯輸入通過；原封移入 bin，記錄為 lan-build-v1/promotion.json。鬼丸四份留於 onimaru-build-v1/bin，lan-pre-integration-baseline.json 綁定其身分。
- README 加入嵐的整合畫面、跳躍、原貌與恢復 HD，操作範例改用現行 733 鍵群組；CONTEXT、工作清單與驗證矩陣同步。原版、衍生美術、研究收據及二進位仍排除 Git，不作 Release 或正式封包。
- 下一角色金太極已解 72 槽／57 組。私有探針以第二人普通 Left 三次選法蘭克，hd-frame-kim-v1 正常 7／4 共 124 格的完整 bytes 與屋頂吻合，kim-source-review.json 綁定來源。尚無 HD 稿或原生接入。
- 本輪沿用既有 Go、三平台 GUI 與 Pillow 映像，沒有新增映像或修改共用 dosgolem。來源探針、建置、測試、Xvfb／Wine 與三個 GUI 案例均已結束；沒有重啟舊首勝工作。完整 HD、其他角色／場景／畫面、WIN／特效／快捷與完整動畫、實體平台／雙手把、音訊／速度及正式封包仍待完成，Goal 保持 active。
- 隔離接入 commit 54b91d0，782f921 合入進度分支；主工作目錄的自有來源同步保存於 /tmp/kdzz-superfighter-publish。收尾備份使用 workplace/github-lan-integration-progress.bundle 與 github-lan-integration-progress-source.json，GitHub 遠端仍未建立或推送。

## 2026-10-20 金太極一般姿態與姓名整合

- 接續嵐的 ee4dd6e 基底，在隔離 feature/kim-hd 製作金太極。內建 imagegen 保存六份精確請求、五張採用 PNG，對應 57 組不同來源及 72 槽。大刀、護肩、胸飾、綁帶及獨立氣勁沿原圖，未改生成 PNG bytes。
- 02 旋轉初稿因缺完整透明分隔被拒，原稿與 rejected-02.json 保留；內建工具重排 02-v2 後通過同一門檻。第一次群組建立失敗後，工具流程仍啟動測試而缺檔失敗，保留 kim-candidate-checks-v1.log；修正順序，以 v2 乾淨通過。這是工具順序問題，未放寬產品門檻。
- 原姓名 KING TAI CHI 位於 NAME 槽 7、實檔 133Ah、109×11，字圖像素 SHA ed6ce285ff8784b6d9dd0485185336bc4ae9c9c0a4db5d110c56a138d4a484be。Go 嚴格讀取驗 72 槽／57 組、124 個正常 consumer 及原 733 鍵不變，審查後 024 升 READY，再接姓名。設定 ID kim、原版核心、步速、規則與快捷均未改。
- 首輪 native-kim-v1 在跳躍後按拳未捕捉姿態。正常探針證明落地槽 0 仍可處於跳躍路徑 4；外部放開、重按 Tab 後捕捉到拳姿，只作診斷，不計驗收。修正測試為按鍵清空、待機圖及原版路徑 0 才進下一動作。乾淨 native-kim-v2、windows-kim-v1 及 native-kim-missing-v1 各七項、九張獨立重組全部通過，原失敗與診斷輸入保留。
- Linux／Wine 各案例內切換保留核心、來源、設定及指派，恢復 HD 逐點一致；缺件九張整格原貌。人物輸出各變動 24,741 點、姓名 10,791 點，正常站姿、跳躍、原貌及 Wine 畫面另目視。像素數相同不稱跨平台同狀態。
- 完整 internal／cmd 測試及 go vet、後續真實 HUD 姓名／尺寸與未知拒絕測試通過。四個候選 ELF／PE／兩種 Mach-O 的 35 份精確編譯輸入通過，沿用既有工具映像，不改共用 dosgolem。原封移入 bin 的記錄為 kim-build-v1/promotion.json，舊嵐四份在 lan-build-v1/bin。
- 024 升限定 CONFORMED。README 加入金太極目前畫面、跳躍與同狀態切換，範例改用 805 鍵／48 PNG 群組。八名可選角色一般來源共 576 槽、463 組不同 bytes；登錄齊全不當作完整動畫或全遊戲完成。
- 三個乾淨 GUI 案例、診斷、建置與測試均已結束；沒有重啟舊首勝工作。完整 HD、WIN／替代色盤／快捷與完整動畫、其餘角色／場景／畫面、實體平台／雙手把、音訊／速度及正式封包仍待完成。本輪依使用者「繼續」推進 HD，不把一般來源登錄當作整個目標完成。原版、衍生美術、研究收據及二進位仍排除 Git，遠端未建立或推送。
- 隔離接入 commit 1096a38，1aac2b2 合入進度分支。自有來源備份使用 workplace/github-kim-integration-progress.bundle，逐檔、原始資料、執行器、編譯來源與本機連結稽核記錄為 github-kim-integration-progress-source.json。現行 main 穩定基底不移動，本輪專案容器均已移除。

## 2026-10-20 魔王選角與小丑 HD

- 接續完整 HD 目標。使用者追加像 Bison 一樣讓三名魔王可選，並確認單打、雙打都開放。讀取 grilling、逆向重製與 IDA 入口，先查目前包，未直接套青衫版本相關的 EXE 修改。
- 發現目前包右移已為十一人，左移及原滑鼠仍為八人。原版 v1 探針每鍵只跑固定一百萬步，沒有等輸入完成，保留失敗；v2 等原游標改變及鍵盤佇列清空後，四組雙打、v3 三組單打均通過，三名魔王兩側基本操作有收據。原版檔案及狀態不寫回。
- 025 經來源審查 READY 後新增十一人按鈕、普通 Right／Return 定位、標準手把共用導航、排程確認與取消。角色表及設定加入 spider／clown／joe，舊八人配置不覆寫，蜘蛛女預設後兩格空白。只有已驗斬四招可實際快捷，未開魔王巨集。
- 第一批 Linux 三單打／三雙打及 Wine 單打／雙打通過，但目視看到魔王索引的八人縮圖框越界直線。025 返回 DRAFT，另用 IDA 9.4 原資料庫直接查框線與肖像常式。補證探針先漏算已拷貝的 60h，再將右鏡像起點少算一點；原始兩份失敗保留，依原指令修正，v3 十五個肖像及獨立影本通過。
- 顯示修正只在選角觀測 VRAM 寫入，濾除非法框線到獨立影本，不改原版 RAM、CPU、角色或核心流程。補證審查 READY 後接入。修正版 Linux／Wine 各單打及雙打通過，四份獨立核對共十二張原肖像及實際視窗逐點相同、沒有頂列直線，原 RGB 另存。025 升限定 CONFORMED，完整單打過關／結局仍未驗。
- 同時整理三名魔王原圖：蜘蛛女 45 組、小丑 62 組、印第安喬 44 組，均 72 入口。蜘蛛女首張原造型請求被內建圖片工具拒絕，保存錯誤與請求 ID，未改造型。改續小丑，六份精確請求及六張生成原 PNG 全通過透明門檻，沒有程式修改 PNG。
- 小丑保留 JOKER／52×11 原姓名。877 鍵／54 PNG／十二份來源保留舊 805 鍵及全部舊 PNG，124 個正常 9／4 consumer 通過。026 先審查 READY 再接姓名；完整程式測試及 vet 通過，後續真實 HUD 姓名與未知拒絕另驗。
- Linux／Wine 小丑各七項、九張完整來源重組及切換通過；缺件九張整格原貌。各案例內核心、來源、設定與指派相同，恢復 HD 逐點一致，人物輸出 27,594 點及姓名 5,148 點變動另目視。026 升限定 CONFORMED，不稱跨平台同狀態或完整動畫已驗。
- 四份最終二進位及原編譯收據保存於 boss-clown-build-v2/bin，37 份精確輸入、檔頭及七個最終 GUI 案例均核對，原封移入 bin，舊金太極四份留於 kim-build-v1/bin。首版 boss-build-v1 仍保存其來源及收據，沒有將八組舊 GUI 換名為新版證據。
- README 加入十一人選角、第二人魔王與小丑 HD／跳躍／原貌／恢復截圖，現況、清單及驗證矩陣同步。沿用既有 Docker 映像，IDA、Go、交叉編譯、Xvfb／Wine 與圖片核對容器均有界並移除，沒有新增映像、改共用 dosgolem、建立 Release 或推送 GitHub。
- 本批自有來源與完整歷史備份使用 workplace/github-boss-clown-integration-progress.bundle 及 github-boss-clown-integration-progress-source.json。原版、衍生美術、私有執行器、研究收據及二進位仍排除 Git。接著繼續印第安喬與其餘 HD，完整目標尚未完成。
- 隔離接入 commit 5dba2f1，dcdaff5 合入進度分支；main 保留既有穩定基底。GitHub 遠端未建立或推送。

## 2026-10-20 印第安喬一般 HD 與姓名整合

- 沿復古重製規格及文件職責路由，製作印第安喬 44 組原圖的四張 HD 圖集。原 PNG bytes、四份精確內建 imagegen 請求及透明檢查保存在 joe-art-v1。949 鍵／58 PNG／十三份來源保留舊 877 鍵及全部舊 PNG。
- 原姓名 INDIAN JOE 位於 NAME 槽 10、實檔 1C9Eh、96×11。初版正常探針兩人同時出拳，誤把同階段 path 10 的槽 11／12 列為拳擊期望。三個原生 v1 等不到該姿態而中止，保留圖片及原審查，不當通過。規格退回 DRAFT，以只有第一人按拳的正常 v2 重取 124 格，確認 path 27 使用槽 5／6／7；追加 joe-punch-source-correction.json，補證審查後再升 READY。
- 原生 v2 等明確拳擊槽 6／7 及 path 27，Linux／Wine 各七項、九張完整來源重組、切換及 Linux 缺件九張原貌全部通過。各案例內恢復 HD 逐點一致，人物輸出變動 33,291 點、姓名 9,504 點，另目視站姿、跳、拳、原貌與 Wine；不稱跨平台同狀態。
- 完整 internal／cmd 測試與 go vet 通過。補證後候選來源及真實 HUD 的 INDIAN JOE／96×11、未知拒絕定向測試通過。四份 ELF／PE／兩種 Mach-O 綁定 37 份實際編譯輸入，原封移入 bin，記錄為 joe-build-v1/promotion.json。舊魔王選角／小丑四份仍在 boss-clown-build-v2/bin。
- 首次隔離複製遭 Docker socket 存取拒絕後，依賴它的工作仍被啟動，因缺工作區掛載點而退出；修正順序及隔離掛載後重跑。單檔唯讀掛載不能讓 gofmt 原子換檔，改用已檢查 UID 的明確來源目錄；純 Python 映像缺 Go，建置核對改回既有 Go 映像。這些均為工具與環境錯誤，未改產品門檻。
- README 加入印第安喬目前畫面、跳、原貌及恢復 HD；CONTEXT、清單、驗證矩陣及規格同步。027 限定 CONFORMED。沿用既有映像，沒有改共用 dosgolem、玩法、速度、設定格式或快捷。原版、衍生美術、收據與二進位繼續排除 Git；未建立 Release 或推送 GitHub。
- 子彈下一批 WIN 靜態來源為 CCWIN.FIG，72 入口／四組圖。原參考、精確內建請求及四格透明候選保存於 bullet-victory-source-v1、bullet-victory-art-v1，未接 production，也未將靜態解碼當正常勝利收據。
- 蜘蛛女原服裝生成被拒後，先展示全覆蓋紫色連身衣比較稿。使用者明確選擇「採用比較稿的連身衣 HD」，因此該圖成為已授權造型參考；原 PNG、請求及原失敗仍保留。只改 HD 服裝，原版姿態、操作與規則保留，接著繼續製作。
- 本批建置、來源探針、測試與 GUI 容器已結束並移除。自有來源與完整歷史備份使用 workplace/github-joe-integration-progress.bundle，核對記錄為 github-joe-integration-progress-source.json。完整 HD、魔王過關／結局、實體平台／雙手把、音訊／速度與正式封包尚未完成。

## 2026-10-20 子彈首勝 HD 與後續來源

- 印第安喬接入 c68ecaf，f57e573 合入進度分支，183 份自有檔案與主工作根相同；完整歷史 bundle 的 20 refs 及 SHA-256 7e3a2ca56d788b7a471afd0224fd4897cd12762db21ee30e646fc5d9123de1a5 通過。收尾核對 128 原檔、1719 執行器來源及 479 本機 Markdown 連結。
- 子彈 CCWIN.FIG 四組原圖依內建 imagegen 製作一張 2172×724 透明原 PNG，沒有程式修改。1021 鍵／59 PNG／十四來源保留舊 949 鍵，Go 嚴格候選讀取通過。原檔前 96 bytes 與 SFMAN03 的 AC8h 正常色盤相同。
- 單核心診斷先以普通方向與拳取得正常 2／4 首勝，生命 124／0、計時 51，五張來源獨立重組及下一回合清除通過。獨立工具初版誤讀 HUD 的 health 欄位，實際 schema 為 display_health；修正工具後乾淨重跑，不改產品。DRAFT 及來源審查綁定於 bullet-victory-evidence-review.json，028 升 READY 後才補 BULLET 勝負姓名。
- 成對核心再驗 6,018 邊界的狀態與即時 RGB 不變、11 個 WIN 取樣、槽 0／2／3 及五張保存畫格，均由原檔重組；槽 1 只有靜態證據。完整 internal／cmd 測試與 go vet、真實原字圖及錯來源拒絕通過。
- Linux／Wine 的正常首勝與 Linux 缺 WIN 三個案例各七張完整通過。普通操作取得擊倒，BULLET WIN、原貌／HD／恢復及下一回合清除均核對；缺件時勝利整格原貌，下一回合恢復 HD。每個平台內恢復逐點一致，GPU 字圖各 5,109 變動點／1,552 金色實心點，另目視，不稱跨平台同狀態。
- 028 升限定 CONFORMED。四個候選 ELF／PE／兩種 Mach-O 與 37 份精確編譯來源通過，原封移入 bin，舊印第安喬四份保存於 joe-build-v1/bin。README 加入目前勝利、原貌及恢復圖，現行群組改為 1021 鍵，工作文件同步。
- 蜘蛛女的已選定全覆蓋連身衣十二格稿，仍被內建工具於輸出階段拒絕，請求 ID 18314280-85c6-4256-8e08-d2aa8d613bfe。沒有 PNG，也沒有反覆重試或改變已選方案；accepted-design.json 與 covered-generation-failure-00.json 分別保存決定與失敗。正常 8／4 的 124 格來源及 WIDOW／57×11 姓名已驗，原生仍保留原貌。
- 道場下一背景依 I5 原構圖生成 1922×818 候選原 PNG，來源與精確請求在 dojo-art-v1，尚未接 production。正常 0／0 的 124 格均為 scene 0，背景 RAM、角色 bytes 與八份背景色盤全部吻合，camera 80–145；dojo-source-review-v1.json 綁定來源。後續才處理多場景載入與原生接入。
- 沿用既有 Docker 映像，沒有改共用 dosgolem、原版規則／速度、設定格式、快捷或歷史收據。子彈建置、來源、測試與 GUI 工作均已結束；道場來源亦已結束。自有來源與完整歷史保存於 workplace/github-bullet-victory-integration-progress.bundle，核對記錄為 github-bullet-victory-integration-progress-source.json。未推送、未發布，完整 HD 與正式封包仍未完成。

## 2026-10-20 多場景背景草案

- 子彈首勝接入 6c549de，1a3080e 合入進度分支，185 份自有來源與工作根相同。完整 Git 備份 22 refs，SHA-256 a99bba3cdf4367deeb26ad257cee844db9dca8a7d8d6bc76d6999fae91fe209a，128 原檔／1719 執行器來源／490 本機 Markdown 連結通過核對。該批容器全部移除。
- 建立 029 DRAFT，提議同一版本 2 背景包自動對應屋頂、道場，舊屋頂包不需轉檔。依使用者的資料格式決策規則及 grilling 技能提出相容方案，等待回答前不進 production；正常來源與候選已備妥，原生現行仍是單屋頂包。其他 WIN 製作繼續。

## 2026-10-20 鳳凰首勝 HD

- 多場景包確認尚待回答，繼續不依賴新格式的鳳凰 WIN。EEWIN 三組原圖、6279 bytes、72 入口與正常色盤核對；內建 imagegen 生成一張 2172×724 三格透明原 PNG，精確請求、SHA 及矩形保存在 phoenix-victory-art-v1。沒有修改生成 PNG bytes。
- 正常 3／4 單核心診斷以普通方向與拳取得首勝，生命 124／0、計時 51，四張凍結畫格、八個 WIN 取樣與下一回合清除由原檔獨立重組。候選 1093 鍵／60 PNG 保留舊 1021 鍵；DRAFT、候選與正常來源審查後 030 升 READY，再補 PHO HUANG 勝負姓名。
- 成對核心完成 5,952 邊界，狀態及即時 RGB 相同，WIN 取樣為槽 0／2，槽 1 只有靜態證據。真實 PHO HUANG／WIN 原字圖、位置與錯來源拒絕、完整 internal／cmd 測試及 go vet 通過；不把單元測試當完整動畫驗收。
- Linux／Wine 首勝與 Linux 缺件三案例各七張完整重組通過。每個案例內原貌／HD／恢復的核心、來源及設定相同，恢復逐點一致；勝利 GPU 字圖各 6,881 變動點、1,970 金色實心點，另目視人物、名字及原貌。下一回合快照清空；缺 WIN 的舊群組勝利整格原貌、下一回合恢復 HD。
- 030 升限定 CONFORMED，四份 ELF／PE／兩種 Mach-O 的 37 份實際編譯輸入通過，原封移入 bin；舊子彈首勝四份在 bullet-victory-build-v1/bin，移入收據為 phoenix-victory-build-v1/promotion.json。README 加入鳳凰首勝、原貌與恢復圖，現行群組改為 1093 鍵／60 PNG，工作文件同步。
- 另將剩餘六份 WIN 原檔靜態解碼為 432 入口／30 組：鬼丸 4、嵐 6、金太極 8、蜘蛛女 5、小丑 3、印第安喬 4。來源、雜湊及別名保存於 remaining-victory-source-v1/manifest.json，尚未作正常消費端或 HD 接入聲明。
- 原版、衍生美術、私有執行器、收據與二進位繼續排除 Git。沿用既有映像，未改共用 dosgolem、原版規則／速度、設定或快捷；鳳凰全部建置、核心、測試及 GUI 容器均已結束。自有來源與完整歷史備份為 workplace/github-phoenix-victory-integration-progress.bundle，核對記錄為 github-phoenix-victory-integration-progress-source.json，遠端未建立或推送。029 仍為 DRAFT，未實作多場景新格式。
- 隔離接入 commit 8539701，490d8b4 合入進度分支；main 保留 636f6ad 穩定基底。多場景確認仍待回答，未將未決格式寫進正式程式。

## 2026-10-20 優先建立 GitHub 儲存庫

- 使用者再次指定先建立儲存庫。沿用已授權的私人設定、自有來源與文件範圍；上傳副本乾淨，現行進度 HEAD 為 72724e9，未改程式或 HD 分支。
- 主機權限的 gh auth status 被環境的禁止提權政策拒絕。一般權限檢查回報登入失敗，不能當作主機憑證失效證據；git ls-remote origin 可達 GitHub，但回覆 Repository not found，不能區分不存在或無存取權。
- 實際執行 gh repo create wicanr2/superfighter-remastered --private，因無法連上 api.github.com 失敗。未建立、未推送，未將預定 URL 宣稱為成果連結。已在 CONTEXT 更新實際結果及恢復後推送目前 HEAD 到遠端 main 的命令。
- 本輪僅更新文件，不重跑程式測試。Docker 清單初查沒有 kdzz 容器，後續映像檢查遭 socket 權限拒絕；未啟動新容器、建立映像或發布套件。既有完整歷史 bundle 保留，不覆寫已保存的歷史收據。

## 2026-10-20 GitHub 確認與工作樹搬移

- 使用者已自行建立遠端並要求移入 workspace。git ls-remote 成功核對 HEAD 及 refs/heads/main 均為 69f91cd5513625b5942701b7ed7afc35c461cc16，與本機最新成果相同，確認先前建立及上傳受阻已解除。
- 父目錄 .git 是受保護的空目錄。完整 Git 工作樹因此從 /tmp/kdzz-superfighter-publish 移至 /home/anr2/cht/快打至尊/superfighter-remastered，沒有另建研究目錄或同步副本。先在容器核對 188 個自有檔案與原工作根相同、UID/GID 1000:1000 及目標不存在。main 從 636f6ad 快進至已核對的遠端提交，追蹤 origin/main，所有舊分支與提交保留。
- workplace、快打至尊.jsdos 與 go.work 隨工作樹移入。父目錄同名符號連結保留舊路徑，原版資料與 HD 美術繼續被 Git 排除。父目錄 AGENTS、CONTEXT、README 指向新入口，其餘來源保留搬移前快照，後續只編輯新工作樹。
- 新工作樹 AGENTS 記錄唯一目錄與掛載方式，README 加入遠端穩定連結，CONTEXT 修正遠端及現行分支狀態。歷史 WORKLOG 與 source.json 的未推送欄位保留當時事實，不重寫舊收據。
- Docker 搬移檢查通過 128 原檔、1719 執行器來源、四份二進位及各 37 份精確編譯輸入，歷史完整 bundle 雜湊未變。所有六個 Go 套件在新掛載位置離線解析成功。所有權及錯誤的 .md 目錄檢查通過。沒有遊戲程式變更，不重跑 GUI 或整套遊戲測試。
- git fetch 有一次 DNS 失敗，後續 ls-remote 再次核對相同遠端提交；GitHub API 讀取仍無法連線，未另行確認可見性欄位，授權仍限私人設定。一次文件編輯容器遭 Docker socket 權限拒絕，改用儲存庫檔案編輯工具；後續唯讀驗證與 Go 路徑檢查均成功，未視為產品缺陷。
- 本批容器使用 --rm，收尾沒有 kdzz 容器，未建立映像或 Release。HD 接續新工作樹的 WORKLIST；029 多場景格式仍待回答，蜘蛛女仍保留已選連身衣與生成拒絕紀錄，未重新決定造型或資料格式。
- 搬移文件提交 c809fbe 已成功推送 origin/main，ls-remote 再次核對遠端完整提交 c809fbe9cd8c12a7bc94fbe64846fa12218755d2，本機工作樹乾淨。507 個本機 Markdown 引用及三個相容連結通過；首版檢查誤將兩個掛載點的路徑字串直接比較，改用 samefile 核對檔案身分後通過，沒有修改產品或連結來迎合檢查。

## 2026-10-20 HD 素材上傳授權與整理

- 使用者明確要求「HD素材上傳」。此新授權取代本批生成圖只留本機的舊限制，仍不包含原版檔案、原版色號與色盤、原圖、私有執行器或含原版內容的收據，也不變更儲存庫可見性或建立 Release。
- 命中復古重製與文件職責路由，讀取 reverse-engineer-retro-game-remake、文件職責與 README 標準。先核對實際清單，確認現行角色包 60 PNG／1093 鍵；初次盤點假定存在 registration.json 而中止，實際只有 manifest.json 與勝利登錄紀錄，改按實際檔案盤點，未補造研究證據。
- 新增 assets/hd 作為受版控的 HD 輸入。既有 internal/desktop/assets 專供字型，docs/screenshots 保存介面截圖，workplace 保存研究及中間產物，都不適合代替正式素材來源目錄。assets/hd 的 README 與 catalog 由 AGENTS 及主 README 索引，不建立交付或研究目錄。
- 本次收錄現行角色圖集與清單、屋頂生成圖、道場候選及已選定的蜘蛛女連身衣圖。候選狀態保留，不把上傳當作遊戲接入或完整 HD 驗收；原 PNG 只複製，不重新編碼。
- 實際收錄 assets/hd 共 66 檔，含 63 PNG、角色 manifest、逐檔 catalog 及 README。影像與角色清單共 79,479,947 bytes。60 張角色圖集均依 SHA-256 回查既有生成來源，三張背景／造型圖亦與原生成檔相同，沒有提交原版參考色號、色盤或原圖。
- Pillow 11.3.0 解碼與 PNG 完整性、catalog 大小／尺寸／雜湊、全部複製來源、1093 個登錄鍵、66 檔精確收錄範圍及 523 個本機 Markdown 引用通過。以 assets/hd/characters 實際載入的既有 TestCharacterPackSourceSelectionAndAtomicRejection 通過，未跳過，16.28 秒，證明目前讀取端可用這份包並維持來源選擇及損壞拒絕。
- README 改列已收錄 HD 圖與角色包，加入屋頂及鳳凰 WIN 原圖預覽，仍標示本機整合截圖、原版資料及屋頂參考層的邊界。AGENTS 與 CONTEXT 記錄本次新授權，歷史 WORKLOG、生成來源與舊 rights 欄位保留原日期事實，未改寫舊圖或宣稱完整 HD 完成。
- 素材提交 4209aad83089c7f74c5ef853a4f1d865e6739f78 已成功推送 origin/main，ls-remote 核對相同完整提交，當時本機工作樹乾淨。提交前核對只有 66 個素材檔及四份既有文件，沒有原版或其他工作區路徑。全工作樹 find 的 root-owned 檔案與錯誤 .md 目錄檢查無結果。
- 本輪所有素材、圖片與 Go 驗證容器均以 --rm 結束，沒有新增映像或持續工作；檢查時另有其他專案的 sc-cht-i010-reg-l3-18172 容器，未停止或修改。GitHub API 及匿名連線檢查仍受網路限制，未聲稱另驗可見性欄位，也未改變遠端可見性。沒有建立 Release、重建二進位或修改正式玩法。

## 2026-10-20 接續鬼丸首勝 HD

- 使用者要求繼續。沿現況表接續未做的鬼丸 WIN，029 多場景格式仍待回答，蜘蛛女生成拒絕不重試。命中 RE→spec 閘門，載入對應入口及 imagegen 技能，使用內建圖片工具沿既定 B 畫風生成。
- 新增並索引 031 DRAFT。來源沿 remaining-victory-source-v1 的 GGWIN 四組／72 入口，先補正常首勝證據，不把靜態解碼當玩家路徑完成。新增的 onimaru-victory-source-v1、onimaru-victory-art-v1 及核心診斷都沿既有 workplace，分別保存本切片來源、精確請求與執行收據，不建立第二套研究根目錄。
- victory_core_receipt 擴充原八人診斷選角，角色大於法蘭克時以普通 Left 選回第二人法蘭克，仍核對實際角色。這是蒐證工具，不修改正式輸入、核心狀態或遊戲規則；正式姓名接入須等 031 READY。

## 2026-10-20 README 的 GitHub 圖片入口

- 使用者指出 README 的本機圖片在 GitHub 無法顯示。原因為圖片及連結指向被排除的 workplace；先前只檢查本機檔案存在，不能證明遠端可讀。
- README 改為只嵌入已版控的屋頂、鳳凰 WIN 圖集及手把設定介面，保留素材預覽與實機截圖的標示。移除只在本機存在的圖片／收據連結，驗證與來源回到 CONTEXT 及驗證矩陣，不上傳原版截圖來填補連結。
- 本次修正不影響已確認的 HD 範圍，鬼丸 WIN 製作持續。首頁檢查改為逐項比對 Git 追蹤清單，不能只用工作區 exists 判斷。
- 首頁修正 76817b0 已推送，53 個相對連結與三張圖片逐項比對 Git 清單通過。新增 tools/verify_readme_links.py 並於 AGENTS 索引，往後可重複檢查，不再只確認本機存在。
- 隨鬼丸正常首勝驗證完成，另將這張 HD 整合截圖原封收錄 docs/screenshots/onimaru-victory-hd.png，SHA-256 824aea2202f87759c898ec545fb0d5e82cb6bd670137d6499aea6c79d99abbf7；source.json 保存二進位、候選角色包、七張 GUI 案例及獨立重組的雜湊。沿使用者先前要求整合截圖、此次 HD 上傳及 GitHub 圖片修正的授權處理。原貌對照、原版參考圖、分層與原始收據仍未提交。首頁分別標示 HD 素材預覽、HD 實機截圖與核心啟動前的設定畫面。

## 2026-10-20 鬼丸首勝 HD 接入結果

- GGWIN.FIG 為 12,362 bytes，四組／72 入口。正常 5／4 以普通方向與拳取得首勝，生命 124／0、計時 56，ONIMALU／NAME 槽 5、SI 0EC9h、caller IP 39DCh、矩形 (104,54,72,11)，WIN 為槽 17、SI 368Ch、caller 39F9h、矩形 (185,54,31,11)。Go 1.24.13 單核心診斷的五張來源與 29 個 WIN 取樣已由原檔重組，槽 0／2／3 動態、槽 1 靜態，下一回合清除通過。
- 準備工具先誤判 WIN 的全部 96-byte header 都應等於一般色盤，後又誤讀色盤索引 0。實際 GGWIN 與正常第一色盤前 48 bytes 相同，差異只有未使用的第二色盤 78–95 bytes；正常快照明示 palette_base C0h，據此否定兩個錯誤假設，未放寬 renderer 或修改原版。Docker 內行工具連續遭 socket 權限拒絕，改將相同準備工具保存於 workplace 後在既有容器工具鏈執行，沒有退回主機執行分析。
- 內建 imagegen 產出一張 2172×724 透明四格原 PNG，SHA-256 e5e7b4295c74f9857dc2fb9883cfbf1fb94c0d35bddeef385c16d6f51f463984；精確請求、原圖及透明矩形在 onimaru-victory-art-v1，PNG 未改。1165 鍵／61 PNG／十六來源保留舊 1093 鍵及舊圖，Go 嚴格讀取通過。
- 031 先 DRAFT，再以 onimaru-victory-evidence-review.json 的正常來源、字圖、候選與精確請求審查升 READY，之後才加入 ONIMALU 勝負文字。成對核心完成 12,272 邊界，原狀態及即時 RGB 相同，29 個取樣及五張保存來源獨立重組通過。
- Linux／Wine 正常首勝及 Linux 缺件三案例各七張完整通過。每個案例內原貌／HD／恢復的核心、來源及設定相同，恢復逐點一致；GPU 字圖各 5,943 變動點、1,701 金色實心點，另目視字形及人物。缺鬼丸 WIN 的舊包勝利整格原貌、下一回合恢復 HD。不稱跨平台同狀態或完整動畫。
- 全套檢查 v1 揭露舊格式測資只剔除第二色盤，卻保留版本 3 的 WIN source／pose，該測資無法成為合法版本 1。修正為同時排除 WIN 記錄，未改 production 接受規則。v2 在 HD 套件出現 signal:killed，未保留 cgroup 原因，不宣稱已證實 OOM。既有圖集解碼為 RGBA 已需 383,713,236 bytes，對照 Go 1.24.13 本機 SetMemoryLimit 文件後，僅在測試設定 GOMEMLIMIT=1GiB，容器仍限 1.5GiB。v3 完整 internal／cmd 測試及 go vet 通過，HD 套件 213.791 秒，記憶體事件沒有 OOM；三份原 log 與 v3-memory.json 全保留。
- 031 升限定 CONFORMED。四份 ELF／PE／兩種 Mach-O 各核對 37 份精確編譯輸入，原封移入 bin，收據為 onimaru-victory-build-v1/promotion.json；舊鳳凰版及原收據留在 phoenix-victory-build-v1/bin。建置核對 metadata 已按目前規格及修正後測試檔重生，沒有用重新編譯掩蓋來源身分。
- assets/hd 已升為 64 PNG、67 檔，素材及角色清單共 80,516,869 bytes；舊 63 PNG 不變，新圖及 1165 鍵清單與已驗候選一致，紀錄為 onimaru-victory-asset-promotion.json。README 保留現行整合截圖，CONTEXT、工作清單、驗證矩陣及素材入口同步；其餘五份 WIN 的二十六組來源待續。
- 本輪沒有改共用 dosgolem、原版 EXE、遊戲規則／速度、設定格式或快捷。原版資料、原貌對照、分層、私有執行器與研究收據留本機；未建立 Release 或正式封包。029 仍為 DRAFT，蜘蛛女仍保留已選連身衣及原生成拒絕，不重問已確認選項。
- 收尾 onimaru-victory-integration-audit.json 通過：259 份追蹤檔、128 原檔、1719 執行器來源、37 份編譯輸入、三個七張正常 GUI、12,272 成對邊界、64 張生成 PNG 及兩張截圖，共 66 個受版控 PNG。457 個本機 Markdown 引用、README 的 57 個 Git 相對連結與四張圖片通過，README 無 workplace 圖片連結。來源與圖片逐檔 SHA-256、Python 語法、root-owned 檔案及錯誤 .md 目錄檢查通過。
- 本輪具名 kdzz-onimaru 容器均已結束並移除，沒有新增或替換映像；其他專案容器維持原狀。原生成 PNG、精確內建 imagegen 提示詞、DRAFT 審查及歷史失敗紀錄留在本機原位置，可從 031 與本輪工作紀錄回查。
- 接入提交 3c899a8f70ef68f3624db8e5cc6c17637509ded8 已成功推送 origin/main，ls-remote 核對相同完整提交。本機工作樹乾淨，README 的 HD 實機截圖、角色新圖、清單與程式均已包含於此遠端提交；未推送原版資料或建立 Release。

## 2026-10-20：練習模式、雙方滿血及原生介面

- 使用者指定練習模式的雙方鎖血、時間暫停及 AI 不動作，另確認「雙方補滿並鎖住滿血」。入口為工具列、F9 及 `-training`；保留普通單打／雙打選角與既有兩人手把輸入。重啟預設關閉，曾介入保留 modified，與原版 oracle／HD 對拍分開。
- 路由命中 RE 技能、規格閘門、IDA 9.4 與文件職責。以既有 AI／HUD 匯出及窄範圍 IDA 補證，保留原名、原運算元與位址空間。032 依 DRAFT、動態差異探針、證據審查、READY、正式實作、限定 CONFORMED 前進。原版檔與共用 dosgolem 唯讀。
- `training-probe-v3` 的同狀態分支驗單打 AI 中立／恢復與雙打兩側各三次命中。v1 同時攻擊只中一側、v2 關閉後擊倒仍等活動畫格，皆是探針問題；v3 分開攻擊並在正常終止後停止。v1／v2 檔及失敗保留。
- 正式 `internal/gamecore/training.go` 只在明示訓練請求及可操作回合介入。傷害增量清零但保留暈眩及受擊，時間由原版畫數字，AI 結果在輸入歷史前清中立。滿血條讀固定 BOARD.XBB，不內嵌原圖；HD 層仍只讀。未知來源／指令、展示模式、既成擊倒與零時間均不介入。
- `training-core-v3.json`、`training-checks-v3.log／json` 通過真實普通單／雙打、32 個未啟用獨立 Oracle 比較邊界、七個拒絕邊界、暫停、重新啟動、關閉恢復、原檔 HUD 重組、internal／cmd 全套可用測試與 vet。單打補血前 96／124，鎖血後維持 124／124；雙打兩側各兩次有效命中，關閉後均為 74。測試環境 GOMEMLIMIT=1GiB、容器 1.5GiB；oom／oom_kill 皆零。舊 HD 外部 fixture 未另供給，不冒稱完整 HD 動畫重驗。
- 核心 v1 測試把原版站立兩格的一像素偏移當成移動；v2 修正站立／中立判準後通過，v3 再加入拒絕邊界並全套通過。只改驗證判準，正式程式保留原版呼吸動畫。初版來源快照保存在 `training-core-v1-test-source.go`。
- Linux 單打 `training-native-single-v1` 七項、Linux 雙打 HD `training-native-v4` 八項、Wine 雙打 HD `training-wine-v2` 八項通過，均走普通視窗選單。預選、F9、暫停時關閉、繼續倒數、戰鬥中再開、重啟預設、命令列預選、截圖標記及 HD 介面逐項核對。Windows／macOS 真機、實體手把及完整魔王／勝負流程未重驗。
- 原生 v1 誤用不存在的背景目錄後停止；v2 原版滑鼠短按錯過 DOS 輪詢，改依既有工具維持至 125 萬步；v3 的單打正常選到金太極場景，既有單場景包正確回退，不能拿它驗屋頂 HD。v4 改正常雙打選斬／法蘭克，單打另驗。Wine v1 狀態檔先於可見視窗的競態由有界視窗等待修正，v2 通過。這些環境與腳本紀錄不列產品缺陷，沒有加遊戲特例。
- README 新增實際 HD 練習截圖 `docs/screenshots/training-hd.png`，SHA-256 `a0caf30e4014c6f2ab85870993e4de7e42394c659e89680ca9d4464090ae790d`。視覺檢查確認工具列、生命、99 計時與底列標記可讀；來源、二進位、素材及收據雜湊追加於 source.json。所有 60 個 README 相對連結及五張圖片均由 Git 追蹤清單核對通過，沒有 workplace 圖片嵌入。
- 四平台各自編譯並核對 38 份實際來源、ELF／PE／兩種 Mach-O 與雜湊，八份二進位／編譯收據原封移入 bin，見 `training-build-v1/promotion.json`。鬼丸前版保留於 `onimaru-victory-build-v1/bin`，歷史收據不覆寫。沒有建立 Release、tag 或正式封包。
- `training-integration-audit-v1.json` 通過：128 原檔、1719 執行器來源、64 生成 PNG 皆未變；264 個 Git 追蹤檔、67 PNG、38 編譯來源、三組原生收據、截圖及設定範圍皆核對。沒有 root-owned 檔案或誤建 .md 目錄。本輪 kdzz-training 容器全部結束並移除，未建立新映像，其他專案資源不動。來源與練習功能準備提交；推送結果另記。
- 功能提交 `38088ee6b420f43caeea64c1b146d22ceb59d868` 已成功推送 `origin/main`，`ls-remote` 核對相同完整提交。新增程式、規格、測試、README 練習截圖及來源紀錄皆已在遠端；原版、私有執行器、研究收據及中間二進位沒有推送。這次只追加提交結果，沒有修改已通過的程式或素材。

## 2026-10-20：蜘蛛女外部 HD 圖去背

- 使用者提供 `/home/anr2/cht/快打至尊/spider-woman-hd/spider-hd-png` 的五張 1168×784 RGBA 圖。原圖只把部分白格設為透明，灰色棋盤仍是不透明像素，五張均無法通過原有透明分隔登錄。
- 純去背的內建 imagegen 請求仍被輸出安全檢查以 sexual 拒絕，request ID `efb1a218-2cc6-49df-b249-0b8d412341a0`。使用者隨後明確回覆「授權」Python 去背，才改用 Docker 內 Pillow 11.3.0，沒有重試圖片模型或重畫角色。初始盤點與拒絕記錄在 `workplace/spider-art-v1/user-art-inspection-v1.json`。
- 新增 `tools/remove_sprite_checkerboard.py` 並掛入 AGENTS 索引。從已透明像素與外框追蹤連通淺灰背景，只將背景 alpha 設零；所有位置的 RGB、尺寸、檔名及原始五張檔案 SHA-256 均維持。沒有猜補肢體、重排圖格或改寫正式角色包。
- 輸出在同一素材目錄的 `transparent-v1/`，ZIP 為 `transparent-v1.zip`，含五張 PNG、處理清單及說明。ZIP SHA-256 `e41d80e61057163e7e9c8723ed36252eb4f10ae4870c7e3a6fc0a3574e66c85d`。五張各新增 419705／370934／379841／375519／384352 個透明像素，PNG 重讀與 ZIP CRC 通過。
- 深色及白色底逐張目視確認棋盤背景去除，並獨立檢查 RGB／尺寸逐點相同、四角全透明及既有 atlas_regions 分隔通過。驗證在 `workplace/spider-art-v1/alpha-validation-v1.json`，雙底預覽為同目錄 `alpha-review-v1.png`。
- 實際圖格依檔名為 00 九格、01 十二格、02 五格、03 十二格、win 十二格。02 目視為站立勝利稿，win 是一般動作圖；多個原版倒地、翻轉與特效姿勢未在候選中保留。去背完成不代表動作對應或遊戲接入完成，現行遊戲仍用原貌，後續先核對可用範圍。
- 這批處理使用 non-root、network none、有界資源及 timeout 的一次性容器；原始輸入另以唯讀覆蓋掛載。未建映像、未建 Release，既有未完成 HD 改動維持；本輪的檔案擁有權與容器清理另於收尾核對。
- 收尾核對：五份原 PNG 與來源 ZIP 雜湊未變，輸出 PNG／manifest／ZIP 內容及 CRC、腳本語法與 git diff --check 均通過。成品 ZIP 為 5,062,675 bytes。全工作樹及素材目錄沒有 root-owned 檔案或誤建 .md 目錄，本輪 kdzz-spider-alpha 容器均已移除；沒有修改其他專案資源。

## 2026-10-20：蜘蛛女姿勢審查與逐格補稿

- 使用者說「ok go」後，沿現有角色來源契約核對五張外部稿。低伏待機、倒地、翻轉與效果輪廓無法直接按檔名對應；`workplace/spider-art-v1/pose-review-v1.json` 與 `source-vs-candidate-v2.png` 保留首批差異。這是目視來源審查，不是正常玩家路徑驗收。沒有以站姿或蹲姿替換原版倒地，也沒有放寬正式圖集的缺件回退。
- 使用者接著要求缺少圖片的提示詞。新增並索引 `tools/export_spider_corrections.py`，輸出逐張原圖、逐張英文提示詞、使用者外部稿的透明造型參考與中文說明。首批十張為一般槽 21／24／29／33／34／43／44 的缺件，以及 0／1／41 的低伏修正；其餘三十五張尚未審查通過，不表示只補十張就完整。
- 原始 packed bytes 核對一般槽 0／1／41 分別與 JJWIN 槽 0／1／2 完全相同，這三張通過後可共用，不必重畫。槽 43 實際尺寸為 94×1，只確認是細長圖像來源，未將用途猜定為投射物；槽 44 描述原圖黃色輪廓，沒有猜補招式觸發。
- 補稿包 `workplace/spider-corrections-v2.zip` 為 1,039,569 bytes，SHA-256 `fa2cbcb7d9374af4abc24cd6321fe784333788bf5fd201ce42a14ecb01b5e05d`。十張原版 PNG 與來源清單雜湊、造型參考逐檔複製、ZIP CRC、中文檔名 UTF-8 旗標與中文說明 UTF-8 BOM／CRLF 通過。v1 保留產生紀錄，v2 補齊跨平台文字換行，不覆寫既有包。
- 原圖交接包只供本機，不加入 Git；工具與索引可版控。圖片生成交由使用者的其他模型，本次沒有再次呼叫被拒絕的圖片工具。其餘三人 WIN 的正常原生驗證同時繼續。

## 2026-10-20：金太極、小丑與印第安喬勝利 HD 接入

- 使用者要求卡點先跳過、先完成一輪 HD。033 經正常來源診斷、原姓名、生成 PNG 與透明矩形審查升 READY，加入三人勝利姓名後完成限定 CONFORMED。嵐兩份稿 alpha 最大值只有 254，未修改圖片或放寬門檻；蜘蛛女外部圖改走逐格補稿，道場只整理候選及來源，不擅自實作 029 新格式。
- 金太極 IIWIN／小丑 DDWIN／印第安喬 KKWIN 合計十五組不同圖像，新增三張內建 imagegen 原 PNG 與 216 個 WIN 鍵。金太極 WIN header 與一般色盤不相同的初始研究假設，已由實際 C0h palette 讀取推翻；失敗研究腳本保留，未修改原檔。原版 WIN 表位於 60h、payload 位於 180h，與一般來源分開。
- 三人成對核心分別 7,596／5,505／8,919 邊界，共 22,020 次原狀態及即時 RGB 比較通過，18 張畫格與十二個 WIN 取樣由原檔獨立重組。工具早期只接受固定兩張 capture，擴充為明示 pose_captures 加兩張生命週期圖，保留序列驗證；不是來源或產品缺陷。
- Linux 正常選單、普通移動與拳擊取得三人首勝，並以舊包驗缺金太極 WIN 的整格回退。四案例各七張原檔重組、原貌／HD／恢復同狀態、恢復逐點一致與下一回合清除通過。小丑是時間到後 124／4 判勝，沒有修改傷害或偽造擊倒。GPU 文字變動點依金太極／小丑／喬為 7540／4775／7098，金色點 2142／1415／2092，全部限於原 NAME 矩形；另目視三組人物與字形。
- 真實候選及三個姓名 fixture 的 Go 測試通過，驗 1381 鍵／64 PNG／十九來源、舊基底保持、每角 72 槽及損壞原 SI 拒絕。完整可用 internal／cmd 測試與 vet 通過，log 為 `workplace/hd-first-pass-v1/go-checks.log`；完整套件沒有另供舊外部 HD fixture，不冒稱全動畫重驗。
- 四平台各核對 38 份實際編譯輸入及檔頭，八份編譯產物／收據原封移入 bin，前版 training-build-v1/bin 不變。這次只驗 Linux 原生首勝，沒有跑 Wine、Windows／macOS 真機或實體手把；未建 Release、tag 或正式封包。
- 公開素材升為 67 張生成 PNG、73 檔，catalog 七十筆 payload 共 84,002,886 bytes。舊 61 張角色 PNG 不變，新圖與清單吻合已驗候選。道場新增來源清單與精確提示詞，候選狀態保留。README 新增實際印第安喬首勝 HD 擷取，來源與比較收據、二進位及素材身分寫入 docs/screenshots/source.json。
- 接入與中間二進位移入證據為 `workplace/hd-first-pass-v1/promotion.json`、`workplace/first-pass-hd-build-v1/promotion.json`。128 原檔與 1719 執行器來源均未變；本輪未改遊戲規則、練習模式、快捷或設定格式。首頁、現況表、工作清單、規格與驗證矩陣同步，完整 HD 仍未完成。
- 收尾 `integration-audit-v1.json` 通過原檔、執行器、67 張生成 PNG、70 筆素材、28 張正常原生擷取、實際素材來源及 bin 原封移入。README 的 62 個相對連結、六張圖片均已納入 Git；Python 語法、git diff --check、工作樹 root-owned／誤建 .md 目錄檢查通過。本輪 kdzz-first-pass／kdzz-spider 容器均已結束並移除，未新增映像或清理其他專案資源。
- 接入提交 `8f1f5bde4ed76cd6c163a4ce5efb931b03b5634a` 已推送 `origin/main`，`ls-remote` 核對相同完整提交，工作樹乾淨。三張新 WIN 圖、角色清單、印第安喬 HD 截圖、道場索引及補稿工具均已在遠端；蜘蛛女原始參考、去背外部稿、原圖 ZIP、私有執行器與中間二進位仍保留本機。

## 2026-10-20：第二批蜘蛛女十張補稿的本地去背

- 使用者提供父目錄 `spider-woman-hd/spider-normal-hd-png-v2`，明確指定使用本地工具處理透明色。沿已授權的 Python 路徑，在 Docker 內使用既有 Pillow 11.3.0 工具鏈，未呼叫圖片生成模型。
- 十張來源均為 784×1168 RGBA，只有部分白格透明，灰色棋盤仍寫在圖內。沿原 `remove_sprite_checkerboard.py` 的連通淺灰背景遮罩處理，原圖唯讀掛載。只修改背景 alpha，所有 RGB、尺寸、檔名與十份來源 SHA-256 不變。
- 工具說明原先寫死五張，這次改由實際處理數量產生，並將 README.txt 寫成 UTF-8 BOM／CRLF。去背演算法與門檻未調整，不修改前次輸出。
- 成品目錄為父目錄 `spider-woman-hd/spider-normal-hd-png-v2-transparent-v1`，同名 ZIP 為 8,528,750 bytes，SHA-256 `c9a24071206197ff557d25a3728261cb9f0d61b24e5812db8700fb4273bee229`。ZIP 含十張 PNG、manifest.json 與 README.txt。
- `workplace/spider-art-v1/alpha-normal-v2-validation.json` 獨立核對十張原始／輸出雜湊、逐像素 RGB、尺寸、彩色前景 alpha 保持、四角透明、PNG 重讀、ZIP CRC／每項內容及 UID/GID 1000。兩頁深色／白底預覽亦已目視，檔名為同目錄 `alpha-normal-v2-preview-0.png`／`alpha-normal-v2-preview-1.png`。
- 本次只完成去背，沒有重排檔名、核准動作對應或更新正式角色包；完整 HD 與來源對應仍依現有工作清單。原版、使用者輸入及十張透明成品留本機，不新增公開圖片。
- 本輪一次性處理／驗證容器均已結束並移除，未建立映像。工作樹與素材目錄的 root-owned 檔案／誤建 .md 目錄檢查及 git diff --check 通過；其他專案資源未動。

## 2026-10-20：蜘蛛女十五張外部 HD 稿收錄 repo

- 使用者再次要求「那就繼續囉 hd記得放進去 repo」。依此收錄前次兩批去背成品，取代這十五張外部生成圖只留本機的舊限制。原版參考圖、原始外部輸入、原圖交接 ZIP、私有執行器與研究收據仍保留本機。
- 新增 `tools/import_spider_candidates.py`，在 Pillow 11.3.0 容器內重新核對十五張原始輸入／去背結果的 SHA-256、RGB、alpha 及尺寸，再逐檔複製到 `assets/hd/candidates/spider/{atlases-v1,cels-v2}`。匯入不縮放、翻轉或重新編碼，沒有將候選塞進正式角色清單。
- `source.json` 保存兩批輸入、處理工具與清單雜湊、模型版本未提供的限制及逐檔審查。候選 README 列明五張圖集的實際格數，以及十張補稿的七個明顯檔名／姿勢不符；00／01／21 三張仍需核對朝向與肢體，沒有把相似姿勢升格為來源對應。
- 為原版忠實度取捨做 `workplace/spider-art-v1/low-guard-prototype-v1.png` 的離線試排。使用正常來源 01-idle、角色 8 的槽 41 與外部 normal-01，標明未套正式 CRTC、非原生視窗驗收。早期試排誤把 idle 限為槽 0／1，查看收據後確認第三個低伏來源為 41，僅訂正試排條件。比較圖含原版畫面，沒有加入公開 repo。
- 已展示原版／相近低伏試排，依 grilling 詢問是否先採相近姿勢、缺件回退原貌，或繼續保留原版輪廓；正式接入依賴此選擇，候選保存與推送不受影響。這不是新的遊戲規則或資料格式實作，未新增 production spec 或修改正式動畫對照。
- 素材目錄目前 82 張 PNG、90 檔，catalog 86 筆 payload 共 97,619,462 bytes。正式角色包仍是 1381 鍵／64 PNG／十九來源，manifest SHA-256 `fbb4d57d313d2d9e01383c4f95468826e41c225d062ecef1bc506df0e72a2df9` 不變。
- `workplace/spider-art-v1/repo-audit-v1.json` 通過全部收錄 PNG、檔案大小／尺寸／雜湊、十五張複製來源、128 原檔與 1719 執行器來源保持。README 的 63 個相對連結、六張圖片及三份素材索引的 44 個相對連結都已由 Git 清單核對；Python 語法、git diff --check 與 root-owned／誤建 .md 目錄檢查通過。沒有改 Go 正式程式，因此未重跑無關的遊戲測試或重建二進位。
- 提交 `ed213c387bc936e579237fc7220a591f7ca8c238` 已推送 origin/main，遠端分支核對相同完整提交。初次合併命令的工具呼叫曾出現 Docker socket 拒絕及 Git DNS 失敗；將相同命令分開呼叫後成功，未改憑證、網路或產品程式，記為呼叫環境限制。本輪 kdzz-spider 容器已全部移除，未新增映像或清理其他專案資源。

## 2026-10-20：蜘蛛女低伏定版與接入

- 使用者回覆「ok 同意這版蜘蛛女」，確認已展示的相近低伏。基底 HEAD 為 `6b6b42bcb9d7c016611e1d209ef00cfe7ef11193`。本輪命中復古 remake、規格閘門及文件路由，沿原 124 格／WIDOW 證據建立 034，完成 DRAFT 審查後升 READY，才改正式包與顯示分支。
- 新增單張低伏正規化工具，從已公開 normal-01 做逐像素水平鏡像，僅裁全透明留白並保留一像素邊。原候選不改，正式圖為 716×563。登錄一般 0／1／41 與相同 bytes 別名，共三十鍵；一張靜態近似稿不稱完整動畫。新包 1411 鍵／65 PNG／二十來源，舊 1381 鍵／64 PNG 不變。
- 首次候選載入因 96 Mi 像素預算拒絕。舊包已用 100,646,903 像素，只剩 16,393；裁切後新圖 403,108，仍需擴額。034 先記錄實際需求，總上限改為有界 100 Mi，來源、檔案與矩形驗證照舊。被拒候選及其證據保留 `hd-characters-spider-low-guard-rejected-v1`。
- Linux 與缺件案例各四項、五張通過。初版驗證腳本在暫停中按住方向，恢復時被既有鍵盤保護清空，屬腳本順序問題；停止兩個容器並保留 `*-input-before-resume`，改為恢復後再按鍵，從相同普通入口乾淨重跑。修正版驗低伏、移動整格原貌、釋放恢復與暫停同狀態切換。十張原始畫格由原檔獨立重組，恢復 HD 逐點一致。
- 真實候選、未覆蓋來源拒絕、WIDOW／57×11 及損壞 HUD 測試通過，八個既有角色的真實姓名測試通過。原本用蜘蛛女 8 當未知角色的拒絕案例改驗 11。完整可用 internal／cmd 測試及 vet 通過，紀錄於 `spider-low-guard-build-v1/tests.log`。一次帶全部外部 fixture 的擴大試跑達 180 秒期限，未完成、未列入通過聲明；最小充分的指定測試及無外部 fixture 套件測試另行完成。
- 三平台四種架構各核對 38 份實際編譯輸入、ELF／PE／兩種 Mach-O，八檔原封移入 workplace/bin。建置及 promotion.json 在 `spider-low-guard-build-v1`，033 舊版保留。正式 Go 來源未在編譯或原生驗證期間改動。
- 公開素材成為 83 PNG／92 檔，catalog 為 88 項、98,133,629 bytes。新素材、處理來源與實際 HD 截圖已入工作樹，README、候選頁、唯一現況、待辦及驗證矩陣已同步。034 僅限第一側 Linux 低伏，其他動作、WIN、完整動畫、Wine／真機及實體手把未驗。原版圖、原色號、私有執行器與原貌收據不上傳。
- 收尾核對與 Git 推送結果追加於本節後續紀錄；本輪 Docker 一次性容器均使用 UID/GID 1000，完成後檢查本專案容器與擁有權。
- 收尾核對通過：原始包、128 原檔及 1719 份執行器來源不變；83 PNG、catalog 全部大小／尺寸／雜湊正確；新圖逐像素等於已確認稿的鏡像及透明裁切。README 65 個相對連結與三份素材索引共 48 個連結均存在且受 Git 追蹤。final-audit.json 保存結果。沒有 root-owned 檔案或誤建 .md 目錄；Docker 以工作樹掛載過濾為空，本輪容器已移除，未建立新 image。
- 接入提交 d4e940ed03f3f456cf8c0f138a1fa2c30a76fd1d 已推送 origin/main，ls-remote 核對完整提交相同。後續只補本項推送與交接紀錄，未再改程式、素材或二進位。

## 2026-10-20：鍵盤組態、首版封包與本機原曲影片

- 使用者授權鍵盤重綁與四格快速出招、魔王選角、三平台封包、README 故事及截圖、Release。後續明確指定公開包不含遊戲，本機完整版要含遊戲；影片只留本機、使用原版音樂，另評估音樂與語音 HD。快捷範圍確認為先發布已驗功能，明列其他角色限制，不等待全部角色。基底為 cce25aadca358797cd7473f24295d3140b997f4b。
- 載入復古 remake、規格閘門、文件、版號、dist-all、RRSAL、推廣片與原音樂來源路由，並讀 grilling／grill-me。035、036 完成證據審查與 READY 後才接正式路徑；既有雙人、四格與魔王決策不重問。版號統一 v.0.1.0-20261020。
- 新增每人十四個鍵盤欄位、設定面板鍵盤頁、捕捉中立閘門、衝突／保留鍵拒絕及重啟保存。設定版本 1 只補可選欄位，舊檔讀取不回寫。Enter 與數字鍵盤 Enter 保留原第二人拳別名。鍵盤四格共用手把角色招式，只有已驗斬四招啟用，其他角色明示拒絕；沒有改招式、傷害或連發規則。
- 鍵盤正常路徑在 Linux／Windows Wine 各六項通過，收據為 workplace/keyboard-native-v1／keyboard-wine-v1。從原版零步設定、衝突拒絕、還原／清空、重啟、兩人方向與拳腳獨立、兩人斬第一招 path 24h、按住只請求一次均核對。首次腳本讓 P1 飛行特效打斷 P2，未達預期路徑；保留 *-attack-overlap，加入原版待機／無特效／無待結傷害的出招前提，乾淨重跑通過，不改遊戲規則。斬四招完整原版證據沿用 004。
- 新增合法來源匯入：內嵌 125 個正常根目錄檔案的大小與 SHA，沒有原版 bytes。原目錄或 jsdos ZIP 先全驗，再原子建立新目錄，拒絕既有目的地、惡意路徑、重複及來源不符。HD 屋頂參考由使用者原檔建立，公開包不含 reference.idx／palette.rgb。正式程式增加 -version、自動封包資產與 macOS Resources 根定位。
- 可用 internal／cmd 全套測試與 vet、實際 125 檔匯入及 HD 參考測試通過，記錄 workplace/keyboard-release-build-v1/tests.log。使用既有 dosgolem-go-ebiten:1.24-r1 與 tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1 建置四架構，每份綁定 43 份實際編譯輸入及版本。四份檔頭與來源核對後，八檔原封移入 workplace/bin，034 前版保留，promotion.json 保存前後 SHA。沒有擴跑舊外部動畫 fixture 或重建無關工具鏈。
- 新版正常魔王單打五項及三個肖像重組通過；新版蜘蛛女 HD 四項／五張及原檔獨立比較通過。初次並行載入約一億像素圖集超過舊三十秒腳本期限，日誌無產品錯誤；保留 *-startup-budget，觀察程序仍活著後將載入等待改為九十秒，以同一 image／同一正常入口重跑，沒有改正式載入或狀態。
- tools/package_release.py 收集實際十一個依賴模組及 Go／Noto 授權，乾淨建立 dist-all/v.0.1.0-20261020 的八包。patch 四份各約 100 MB，只含引擎、可公開 HD、文件與匯入功能；full-local 四份各約 101 MB，各含 125 原檔，均排除作弊資料。ZIP 固定日期、可執行權限、UTF-8 BOM 說明、完整 manifest／SHA／CRC 與公開原版雜湊排除通過。macOS 數字平台欄位為 0.1.0，完整版本另保存在原生 release 欄位；兩種 Mach-O 與四個 plist 已驗，沒有真機／簽章聲明。
- tools/package_startup_smoke.py 從解壓包驗 Linux／Wine 公開及本機共四次啟動、程式版本、公開缺資料提示、ZIP 匯入、拒絕覆寫、125 檔、HD 參考與原生視窗開始執行。Wine 初次觀測檔先於視窗可見，腳本搜尋視窗失敗；保留 windows-startup-window-race 與匯入成品，改成有界等待可見視窗，從未匯入的乾淨公開包重跑通過。這是自動化時序問題，正式程式未改。
- tools/package_smoke.py 在 sc-cht-dosboxx-bridge:e0b4287-r1 執行實際 Linux Go 程式，沒有使用 DOSBox 作原版收據。正常選角斬／法蘭克、HD、鍵盤快捷及移動、真實 X11 失焦／恢復按住中立、F9 滿血練習四項通過，並錄十八秒原生畫面。三張對戰／出招／練習截圖由原始資料重組六層、姓名、HUD、陰影及顯示起點，結果為 smoke/linux-play-record/capture-comparison.json。
- 原音訊盤點確認 SF000.MUS 有十五段完整標準 MIDI，十七個 PPM 容器有四十筆 Compact PCM。PCM 編碼／取樣率／角色標籤仍未知，不猜補。首段 MIDI 用 TiMidity++ 2.14.0 與 FluidR3_GM.sf2 軟體演奏，沒有重作旋律、沒有原機 DAC／OPL 音色聲明。格式、原 bytes 及工具雜湊見 workplace/original-audio-v1，公開評估寫在 docs/audio-hd-assessment.md；遊戲音訊串流仍未完成。
- tools/promo_release.py 完成本機六十秒影片：1280×720／30fps／AAC 48kHz 雙聲道，十八秒原生實錄，其餘明示靜態截圖與標題。來源／分鏡／字幕邊界／字型／SoundFont 雜湊完整；完整解碼、無黑幀、音量峰值 -1 dB、聯絡表及實際操作畫面抽看通過。實錄有數秒畫面停留，原生來源與成片凍結檢測均保存，不稱正式速度通過；技術音量不等於人耳抽聽。首輪字幕超出底部安全邊界由工具拒絕，依實際字框重排後才合成。影片 SHA-256 為 721376ad5a00ad7f71b1708bb9208d9d640456445ed82bbe90b154bef30bae54，成品只留本機 promo。
- README 補官方來源的故事背景、首版與限制、鍵盤／手把說明及本輪五張新擷取。GitHub 圖片只引用受追蹤檔案；source.json 記錄版本／來源／收據／二進位 SHA。HD 包仍是 1411 鍵／65 PNG／二十來源，公開資產 83 PNG／92 檔不變；完整 HD、其他快捷、音訊、正式速度、實體手把與真機仍待完成。
- final-audit.json 核對原始 jsdos、128 原檔與 1719 執行器來源不變、README 七十個受追蹤相對連結、七張截圖來源、文件索引、Python 語法與 macOS metadata。全工作樹沒有 root-owned 檔案或誤建 .md 目錄。已驗二進位與封包雜湊不因文件收尾改動。
- GitHub 發布工具限定四個 patch ZIP 與 release-manifest.json，先草稿、核對遠端大小與 SHA 再發布。既有 gh 設定中的舊憑證失效；改用已存在且有效的 Git credential store 唯讀供容器取得 GH_TOKEN，沒有搬運、輸出、保存或修改憑證。GitHub release list 為空，尚無相同 tag。後續實際提交、發布與遠端核對追加於下方。
- 首次來源提交 35075f4d0cc83c920d222f35cc56cee1ff474f59 已推送。五個資產上傳草稿後，工具用 tags API 查未發布草稿得到 404，沒有發布或覆寫。改由授權可見的 releases 清單查唯一草稿，再核對 target／資產；這是發布工具的查詢錯誤，封包與正式程式 bytes 不變。修正提交另推送，草稿目標在正式 tag 建立前更新到修正版。
- 發布工具修正提交 807579d01c145db327050c2e870e2bf46e6bcb68 已推送，草稿目標更新後再次驗五個資產。2026-10-20T12:59:06Z 正式發布 v.0.1.0-20261020；公開 Release URL 為 https://github.com/wicanr2/superfighter-remastered/releases/tag/v.0.1.0-20261020。四個 ZIP 與 manifest 的 GitHub SHA-256 digest／大小全部吻合，只有五個指定資產，沒有 full-local／promo／原版資料；git ls-remote 核對正式 tag 等於該完整提交。發布後只補文件，沒有移動 tag、改動封包或重發。
- 發布後匿名下載核對回 404。登入查 repo metadata 確認目前為 PRIVATE，正式 Release 為 published、非 draft，五個資產 SHA 正確。沒有以匿名失敗宣稱發布失敗，也沒有自行改可見性；README、現況與 036 補充需有權限帳號登入。以上「公開包」是素材權利與內容分類，Release URL 本身仍受私人儲存庫存取控制。後續使用有權限 API 與實際 manifest 下載核對遠端圖片及資料。
- remote-download-check.json 通過有權限帳號的實際 manifest 下載及 SHA，五張本輪 README 圖片由 GitHub contents API 讀回 bytes，均與本機完全相同。github-verify.json 再核對已發布版本的五個資產，正式 tag 保持 807579d。後續文件收尾不改任何遊戲、素材或封包 bytes。
- 收尾再核對 43 份編譯輸入、原始包／128 原檔／1719 執行器來源、七張截圖、相對連結、索引、Python 語法及 macOS metadata，均通過；沒有 root-owned 檔案或誤建 .md 目錄。以本工作樹掛載過濾 Docker 容器為空，本輪一次性容器全部移除，沒有新增映像或清理其他專案資源。

重現命令在容器 `/project` 內執行，原版掛 `/orig` 唯讀，工作樹與 workplace 為本專案輸出。每次 docker run 均使用 --rm、--user 1000:1000、--network none、相稱資源限制與 timeout；只有 GitHub API 上傳開網路。

```sh
python3 tools/build_desktop.py verify --output-dir /project/workplace/keyboard-release-build-v1/bin --receipt /project/workplace/keyboard-release-build-v1/build-verification.json
python3 tools/package_release.py audit
python3 tools/package_startup_smoke.py --platform windows-amd64 --output /project/dist-all/v.0.1.0-20261020/smoke/windows-startup
python3 tools/promo_release.py prepare
python3 tools/promo_release.py render
python3 tools/promo_release.py check
```

前兩項可以直接重驗既有輸出。啟動測試需要新輸出目錄與乾淨解壓的公開包；不要在已匯入的測試副本重跑並誤判來源缺少檢查。影片 prepare 用 sc-cht-hdtools:pillow11.3.0-r1，render／check 用 fd2-promo:20261017-r1；目視抽查及其紀錄另人工補入 promo-checks.json。

## 2026-10-20：嵐勝利 HD 與其餘九景首輪稿

- 本輪接續 active goal「完成快打至尊HD」，前一輪為首版發布的實質進展，不把首版當作完整 HD 完成。開工核對 main 的 2d917260120d0ceeca66b9b82edca652c591d031 與乾淨工作樹；載入復古 remake、規格閘門、文件、imagegen、grilling 及版號規則。原版、執行器、已發布版本及父目錄快照不改。
- 嵐舊六格 WIN 圖再次交內建 image_gen 去除底色，結果仍為 alpha 0..254，保留 lan-win-alpha-v2.png／request／inspection，不降低檢查條件。曾詢問是否沿用本地工具修 alpha；之後改走可獨立完成的來源核對與新稿路徑，沒有因沉默視為授權，也沒有本地去背。
- 從正常 6／4 選角、靠近與拳擊取得嵐首勝。lan-diagnostic-v2 有 8,835 次單核心觀測、十三個 WIN 取樣、四種實際來源及下一回合清除；六份畫格由原檔獨立重組圖層、HUD、陰影與 CRTC。它不是成對對拍。NAME.XBB 槽 6 的 LAN、runtime SI 11E3h、caller 01B9:39DCh、矩形 (125,54,31,11)，以及 WIN 槽 17／SI 368Ch／01B9:39F9h／(165,54,31,11) 均核對原 bytes。
- 查明 HHWIN 六組中的 0／1 與一般來源完整 bytes 相同，重用已驗 lan-poses-00.png 的兩格；只有 2／3／4／5 需要新稿。內建 image_gen 直接依原四姿態及現有 HD 身分生成 1448×1086 四格，PNG SHA 為 5b6a313c5443ad0ef373165549b820a5ff0e5f8456cd347f1b2499fc803a5a48。alpha 0..255、透明間隔及未貼邊通過，原 PNG bytes 保留。舊六格半透明候選未接入，無須等待其去背決定。
- 037 先建立 DRAFT、保存正常來源／姓名／實際色盤及候選審查，再升 READY，才加入 LAN 字圖分支與 WIN 登錄。tools/prepare_lan_victory.py 保留舊 1411 鍵與 65 PNG，增加 72 個 WIN 鍵、一張新圖及一份 HHWIN 來源，成為 1483 鍵／66 PNG／二十一來源。沒有改規則、快捷、設定格式、原版狀態或多場景格式。
- 真實七十二入口／六組來源、兩組重用、舊群組保持、LAN 原字圖與篡改拒絕測試通過。可用 internal／cmd 套件測試及 vet 通過，未另供整批舊外部動畫 fixture。Go 及精確版本凍結後建四架構，均核對 43 份實際輸入、ELF／PE／兩種 Mach-O；正式版號依規則升為未發行 v.0.1.1-20261020，已發行 v.0.1.0 不覆寫。
- lan-paired-v2 通過 8,835 成對邊界，原版狀態與即時 RGB 一致；十三個 WIN 取樣及六份原檔重組通過。核心實際來源為槽 0／3／4／5；原生首勝另驗到槽 2，沒有將六組靜態對照稱為六組動態已驗。
- sc-cht-dosboxx-bridge:e0b4287-r1 內執行真實 Linux Go 程式，正常原生 native-lan-victory-v2 與舊包 native-lan-victory-missing-v2 各七張通過。前者 LAN WIN 矩形內變動 3,730 點、金色字圖 1,039 點；原貌／HD／恢復原始狀態相同，切回逐點一致，下一回合清除。後者缺 WIN 整格原貌，下一回合恢復 HD。沒有用 DOSBox 代替 dosgolem 收據，也沒有強制勝利、鎖血或狀態注入。本切片未驗 Wine、第二人、真機、實體手把或完整動畫。
- 037 限定 CONFORMED 後，已驗候選及八份二進位／收據移入 assets/hd/characters 與 workplace/bin；keyboard-release-build-v1 保留首版，lan-victory-build-v1/promotion.json 記錄前後 SHA。第一次移入預檢誤將本機基底的 evidence-review.json 當成公開檔案，尚未寫入即拒絕；改核對公開既有檔及清單所有圖集後通過。這是移入工具的檔案範圍錯誤，不改圖或放寬來源檢查。
- 依已確認的 B 街機手繪方向，內建 image_gen 另為 I1／I3／I4／I7／I8／I9／I10／I12／I13 生成九景首輪稿。約 1920×818，PNG 共 21,785,162 bytes。tools/organize_background_candidates.py 先全批驗原檔 SHA、PNG、尺寸、比例及不透明性，再原封收錄候選。初次腳本在 Pillow 解碼後才 verify，遇 API 順序限制，未寫入；改為先 verify、再重開檢像素後通過，沒有重生或編輯圖。
- 九景的原 SHA、參考 PNG SHA、精確提示詞與生成原 bytes 由 assets/hd/candidates/backgrounds-source.json 保存。I3 提示詞誤稱中央動物為 lion，原圖與候選實為象，保留原提示詞並註明它不是事實證據。小字、群像、裝飾及構圖仍為候選；僅屋頂已接，029 格式決定與九景正常 scene／捲動尚未驗，沒有自動將候選放進 production。十一份 XGB 含屋頂／道場均已有首輪稿。
- 素材成為 93 PNG／104 檔，catalog 一百筆 payload 共 120,619,633 bytes。README 新增正常原生 LAN WIN 畫面與來源雜湊；CONTEXT 唯一現況、WORKLIST、驗證矩陣與素材索引同步，區分 main 未發行開發版及已發布首版。原版資料、原圖、背景色盤及原始收據不上傳。

本輪主要命令在上述受限、非 root Docker 工具鏈內執行；資料掛 /orig 唯讀，工作樹掛 /project。建置、測試、重組及原生自動化均未在主機啟動。

```sh
go run -p 1 tools/victory_core_receipt.go -out /project/workplace/hd-first-pass-v1/lan-diagnostic-v2 -hd-characters /project/assets/hd/characters -player0 6 -diagnostic -pose-samples
python3 tools/prepare_lan_victory.py --output /project/workplace/hd-characters-lan-victory-v1
go test -p 1 ./internal/hd -run TestLanVictory -count=1 -v
go run -p 1 tools/victory_core_receipt.go -out /project/workplace/hd-first-pass-v1/lan-paired-v2 -hd-characters /project/workplace/hd-characters-lan-victory-v1 -player0 6 -pose-samples
python3 tools/desktop_match_smoke.py --binary /project/workplace/lan-victory-build-v1/bin/superfighter-linux-amd64 --output /project/workplace/hd-first-pass-v1/native-lan-victory-v2 --hd-characters /project/workplace/hd-characters-lan-victory-v1 --player0 6 --victory-only --quit-after-seconds 1800
python3 tools/verify_victory_animation.py /project/workplace/hd-first-pass-v1/lan-paired-v2 --original-root /orig --background /project/workplace/hd-rooftop-study --core
```

重建嵐包需以保留的 hd-characters-spider-low-guard-v1 作 --base，並指定新輸出；上述未加 --base 的命令記錄當時尚未接入前的輸入。Go 真實 fixture 測試需 KDZZ_HD_FIXTURES=/project/workplace、KDZZ_ORIGINAL_ROOT=/orig。首版 Release、八包與本機影片本輪不重發，完整 HD 目標仍保持 active。

- 收尾 final-audit.json 通過 128 原檔／1719 執行器來源不變、93 PNG／一百筆 payload、118 個首頁及素材索引的受追蹤相對連結、八張截圖、四份編譯收據與 43 份輸入。首版八個 ZIP 及影片 SHA 全部保持，沒有 root-owned 檔案或誤建 .md 目錄。本工作樹掛載過濾的 Docker 容器為空，本輪容器均已移除，沒有新建映像或清理其他專案資源。
- 缺件原生案例當時使用尚未更新的 assets/hd/characters；現在重跑需指定保留的 workplace/hd-characters-spider-low-guard-v1。打包工具預設改讀目前 workplace/bin，避免開發版誤選固定首版編譯目錄；未執行新封包或新 Release 發布。提交及遠端核對後續記錄另補。
- 嵐／九景接入提交 3411450b75c5d1cf9681386687eeb8770f3b6ac1 已推送 origin/main，ls-remote 核對一致；首版 tag 仍固定 807579d01c145db327050c2e870e2bf46e6bcb68。後續只補來源研究與文件，不移動已發布 tag。

## 2026-10-20：多場景確認前的十一景正常來源補證

- 依 grilling 對 JSON schema 的確認要求，向使用者呈現同包自動切換並相容舊包、或每次指定單景的選擇；未收到答案，不改 029 格式。嵐舊稿的本地去背選擇已由直接生成新四格的獨立路徑解除，不依賴沉默授權。
- 新增 tools/stage_source_receipt.go，先從固定原版 XGB 嚴格解碼十一檔，再以正常標題、雙打選角走 0／0..10，各取待機與二十格普通行走。只讀 Core 快照，沒有加入正式背景讀取器、改規則、鎖血、傳送或寫入狀態。初次編譯把無回傳值的 Close 當作 error，尚未建立輸出即失敗；修正探針後，以同一 image／命令乾淨重跑，沒有改 production。
- dosgolem-go-ebiten:1.24-r1，Go 1.24.13，--rm／--network none／--memory 1g／--cpus 2／--pids-limit 128／--user 1000:1000、外層 1200 秒限制。實跑十一個正常選角案例完成，背景對應 0:I5、1:I12、2:I4、3:I7、4:I2、5:I3、6:I10、7:I9、8:I8、9:I1、10:I13.XGB。每景 camera 80／105、原色盤、完整 RAM hash 與 320×200 背景裁切均吻合。
- tools/verify_stage_sources.py 由原檔獨立解碼，重組二十二份背景，核對來源 SHA、runtime scene、單調步數／serial、完整圖層、無練習修改、原色盤與每列裁切；原來源及正常框架都通過。production 的 43 份輸入仍與已驗嵐編譯相同，runtime manifest SHA 為 d79cc85bc1ce29dbe54c19e7857a9ac07b2e3a1754fb342632ead9e36e619fc3。收據為 workplace/stage-source-v1/receipt.json／source-comparison.json。
- 此證據只限普通雙打兩個取樣，不能外推全部 camera、單打順序、HD 幾何或原生背景已接。029 維持 DRAFT，補入原 scene／檔名表；RESEARCH-LOG 追加推論等級與位址基準。候選來源清單追加已驗 scene 與收據 SHA，圖片 bytes 不變，catalog 同步；現行一百筆 payload 為 120,620,400 bytes，仍是 93 PNG／104 檔。

```sh
go run -p 1 tools/stage_source_receipt.go -out /project/workplace/stage-source-v1
python3 tools/verify_stage_sources.py /project/workplace/stage-source-v1 --original-root /orig
```

前一命令需新輸出目錄，後者可直接重驗現有收據。原版、圖像參考與 runtime snapshots 只留本機；公開 Git 只存探針／驗證工具、原檔身分、推論等級及候選來源索引。

- 補證收尾再次通過完整輸入／素材核對，首頁及素材索引相對連結增為 119 個；沒有新增原始遊戲資料、音訊或影片進 Git。十一景工作容器已完成並移除，工作樹掛載過濾為空；UID/GID 與 .md 目錄檢查通過。production Go、四平台編譯、93 PNG 及首版封包 bytes 均保持，僅補工具、來源證據與候選 metadata。
## 2026-10-20：角色雙向翻轉與頂部裁切接入

- 接續使用者確認的首版快捷限制。路由命中復古重製、規格閘門及 README，沿用 reverse-engineer-retro-game-remake 與 008。029 格式仍待回答，沒有以繼續授權代替格式選擇。
- 從正常原生圖層定位法蘭克槽 28 的 C2h，以及槽 27 的 TopClip 9。verify_character_geometry.py 直接讀原檔，獨立重組原 blit、CPU 覆蓋／色號及矩形翻轉／裁切等價性；2,298／2,168 寫入點吻合。審查在 character-geometry-evidence-v1/review.json，038 經 DRAFT／審查升 READY 後實作。
- LoadCharacters 保存受驗來源私有切片；geometry.go 只在新幾何逐格核對 CPU 原層，通過才用既有 Placement／GPU 翻轉／裁切。缺層或不符仍整格原貌。特效、未知色盤、資料格式、原版規則／座標／輸入不改，不把原檔 bytes 寫入 JSON 或素材。
- 真實兩案例的完整群組、六項篡改拒絕及合法空裁切測試通過；可用 internal／cmd 測試及 vet 通過，記錄為 character-geometry-build-v1/tests.log。未另提供的舊外部 fixture 不稱全數重驗。
- 既有 Go 1.24.13／cross image 編譯三平台四架構，44 份實際輸入與 ELF／PE／兩種 Mach-O 標頭核對。Linux SHA 為 2d0105c6f24c35aa4f94764ea18eea67ef17fb09b648d2ba424ba02d8aa2db82。八份二進位／build.json 精確晉升 workplace/bin，前一嵐版保留；promotion.json 保存前後 SHA。仍是未發行 v.0.1.1-20261020。
- 原生實驗在 sc-cht-dosboxx-bridge:e0b4287-r1 內執行實際 Go 程式，未使用 DOSBox 作原版收據。容器 --rm／--network none／--user 1000:1000，GUI 限 3g／2 CPU／256 pids／1950 秒，程序由 finally 結束。原檔及固定 runtime 副本唯讀。
- character-geometry-native-c0-v1 為嵐、character-geometry-native-top-v2 為金太極，均正常雙打對法蘭克。普通選角、移動及拳擊取得首勝，每案七張原流程加三張新幾何，共二十張。獨立原檔／全層／HUD／陰影／CRTC 重組、同狀態原貌切換／HD 恢復逐點及正常下一回合清除通過。可見角色 HD 變動點 16,317／14,121，另目視對齊與頂緣裁切；不外推全部動畫。
- top-v1 已擷取裁切，但 watcher 在外層滑鼠按住期間重入 click，放開滑鼠令 mouse_left 等待逾時。failure.json 原樣保留，不建立通過收據。只修正腳本 click／key 的互斥，用同一 image／同一二進位重跑 top-v2 通過。c0-v1 成功收據仍綁定當時腳本副本，沒有改遊戲速度／座標／規則。
- 038 限定 CONFORMED，008 補後續解決入口，CONTEXT／WORKLIST／驗證矩陣同步。README 加入 character-flip-hd.png，既有截圖 source.json 保存來源與收據 SHA。原貌及原始圖層只留本機。

主要重驗命令在受限容器內執行，/project 為工作樹、/orig 唯讀。原生輸出及審查重生工具均要求全新目錄，各 verifier 可直接重驗既有收據。

```sh
KDZZ_HD_FIXTURES=/project/workplace KDZZ_ORIGINAL_ROOT=/orig go test -p 1 ./internal/hd -run TestCharacterGeometry -count=1 -v
go test -p 1 ./internal/... ./cmd/...
go vet -p 1 ./internal/... ./cmd/...
python3 tools/character_geometry_smoke.py --binary /project/workplace/character-geometry-build-v1/bin/superfighter-linux-amd64 --output /project/workplace/character-geometry-native-top-v2 --hd-characters /project/assets/hd/characters --player0 7 --victory-only --geometry top --quit-after-seconds 1800
python3 tools/verify_native_character_geometry.py /project/workplace/character-geometry-native-top-v2 --original-root /orig --background /project/workplace/hd-rooftop-study
python3 tools/verify_victory_animation.py /project/workplace/character-geometry-native-top-v2 --original-root /orig --background /project/workplace/hd-rooftop-study
python3 tools/build_desktop.py verify --output-dir /project/workplace/character-geometry-build-v1/bin --receipt /project/workplace/character-geometry-build-v1/build-verification.json
```

C0 案例用 player0 6／geometry c0；沒有重建已發布封包或移動 tag。

- final-audit.json 通過 128 原檔／1719 runtime 來源不變、93 PNG／100 筆素材共 120,620,400 bytes 不變、1483 鍵／66 PNG 不變、四平台 44 份編譯輸入與二進位、122 個首頁及素材索引受追蹤相對連結。首版八包與本機影片 SHA 全部保持，無 root-owned 檔案或 .md 目錄。sf-geometry 容器已完成並移除，未建新映像或清理其他專案資源。
- 完整 HD、其他角色快捷、替代色盤與全部動畫、其他平台／實體手把仍另續；首版已發布範圍及音訊評估保持。功能提交 64379b961f9b7a08ed20b8f9469c40136e3a5ad3 已推送 origin/main 並由 ls-remote 核對；首版 tag 仍固定 807579d01c145db327050c2e870e2bf46e6bcb68。

## 2026-10-20：十一人正常動作取樣與鳳凰拳腳光效

- 前輪 038 是實際進展。本輪重新核對乾淨工作樹、唯一現況與路由，命中復古重製／對拍及 spec 閘門，沿用 reverse-engineer-retro-game-remake。029 仍待格式決定，不依沉默實作；先處理可獨立推進的角色正常動作。
- 新增 hd_motion_coverage.go，十一人逐一從正常雙打入口對法蘭克，依十七個普通方向／蹲／跳／拳腳階段取樣，沒有訓練、傳送、強制勝利或快捷。hd-motion-coverage-v1 保存 4,803 個 serial 與缺件原因；verify_hd_motion_coverage.py 獨立核對原檔指標、packed SHA、保存 CPU 遮罩／色號重組。不是完整動畫、每一格或受控 RNG 對拍。
- 找到鳳凰普通拳腳會畫第二色盤的槽 60／58，原包缺鍵使 15 格回退。另發現同角色色盤不符、少量場邊 C0h 加奇數裁切，以及蜘蛛女十八個實際未覆蓋鍵。後三項保留證據及待辦，不因光效接入稱為完成。
- 依 imagegen 技能用內建工具生成兩格透明原 PNG。精確提示詞及參考身分存 phoenix-effects-art-v1/request.json，新圖 1774×887 RGBA、alpha 0..255、SHA 3f02eaff747f18818c3ad46a8bc2aad38454c79918e0a7652f57ee6988bc76c7。只複製生成 bytes，沒有本地去背、縮放或重編碼。原始參考圖留本機。
- phoenix-effects-source-v1 補足兩種光效的正常 CPU 層。SFMAN04.DAT SHA 2cd299e9c10814ae37bb044c2e3ae7adf940d8b1accd8feffa3844bbfb43356b，實檔 152727／148526、32×40／22×25、805／318 寫入點與第二色盤全吻合。原圖形、朝向及透明區域目視通過，039 經 DRAFT／來源及畫稿審查升 READY，才以 prepare_phoenix_effects.py 登錄既有 palette_bank=1。
- 新群組 hd-characters-phoenix-effects-v1 為 1485 鍵／67 PNG／二十一來源，manifest SHA 2557a3bc5136cd8ff403632f28e161c7d9c1aacd82c3984dbcdf0079ea0c9a8d。舊 1483 鍵及 66 PNG 不變，總像素 104,196,077、清單 517,863 bytes，未修改現行限制或格式。phoenix-effects-comparison-v1 於同一正常核心畫格比較兩群組，437 格中成功由 418 增至 433，新增 15 格、無舊成功退回。另四格場邊仍保守回退。
- 真實兩份 CPU fixture 的完整群組及未知槽、壞來源、錯色盤基底、色號變更拒絕通過；可用 internal／cmd 測試及 vet 通過，見 phoenix-effects-art-v1/tests.log。未另供舊外部 fixture 的套件不稱全部動畫重驗。
- phoenix_effects_smoke.py 用 Linux 現行原生二進位，普通選角、移動及拳腳擷取兩光效。完整／舊包各八張，共十六張；verify_phoenix_effects.py 由原檔重組完整層、HUD、陰影、CRTC 及光效像素。兩種同狀態切換／恢復逐點及解除暫停後正常站立通過，新光效可見變動點 7,245／2,862；舊包兩光效都整格原貌。另目視圖形、原版翻轉及遮擋。未外推第二人、所有動作、Wine／真機或實體手把。
- 工具沿既有 Docker image、--rm／--network none／--user 1000:1000、資源限制及逾時；原檔及固定 runtime 副本唯讀。原生 GUI 限 3g／2 CPU／256 pids／960 秒，Xvfb 與遊戲由 finally 收尾。沒有在主機啟動工作負載、建立重複工具 image 或修改共用執行器。
- 完整驗證後三個素材檔晉升 assets/hd/characters，記錄於 phoenix-effects-art-v1/promotion.json。catalog 為 94 PNG／102 筆 payload／121,070,684 bytes，目錄 106 檔。README、素材索引及截圖來源同步；phoenix-effects-source.json 保留可讀的精確提示詞。039 限定 CONFORMED，原版圖像與原始收據不上傳。
- 本輪為資料擴充，現行四平台二進位及 44 份編譯輸入與 038 完全相同，build-verification.json 只更新文件／測試 metadata，沒有假稱重新編譯。未重建首版八包或影片，未建立新 Release。

以下命令皆在上述受限容器內執行。/orig 唯讀，輸出目錄必須全新；現行素材已晉升，重建須指定保留的舊群組。

```sh
go run -p 1 tools/hd_motion_coverage.go -out /project/workplace/hd-motion-coverage-v1 -hd-characters /project/workplace/hd-characters-lan-victory-v1
python3 tools/verify_hd_motion_coverage.py /project/workplace/hd-motion-coverage-v1 --characters /project/workplace/hd-characters-lan-victory-v1
python3 tools/prepare_phoenix_effects.py --base /project/workplace/hd-characters-lan-victory-v1 --output /project/workplace/hd-characters-phoenix-effects-v1
go run -p 1 tools/hd_motion_coverage.go -out /project/workplace/phoenix-effects-comparison-v1 -character 3 -hd-characters /project/workplace/hd-characters-phoenix-effects-v1 -baseline /project/workplace/hd-characters-lan-victory-v1
KDZZ_HD_FIXTURES=/project/workplace KDZZ_ORIGINAL_ROOT=/orig go test -p 1 ./internal/hd -run TestPhoenixEffects -count=1 -v
python3 tools/phoenix_effects_smoke.py --binary /project/workplace/bin/superfighter-linux-amd64 --output /project/workplace/phoenix-effects-native-full-v1 --hd-characters /project/workplace/hd-characters-phoenix-effects-v1
python3 tools/verify_phoenix_effects.py /project/workplace/phoenix-effects-native-full-v1
```

原始 coverage-v1 於工具增加單角及同格比較旗標前執行，收據綁定當時工具副本。重生可用新輸出；重驗已保存資料則沿該副本 SHA，不能要求歷史工具副本與現行 gofmt 後版本相同。缺件原生案例另指定舊群組並加 --expect-original。

- final-audit.json 通過 128 原檔／1719 runtime 來源不變、全部 94 PNG／102 payload、全部舊鍵／PNG、四份二進位與 44 份輸入、128 個首頁及素材索引受追蹤相對連結。首版八個 ZIP 與本機影片 SHA 保持，無 root-owned 或 .md 目錄；專案掛載過濾無容器殘留。功能提交 e4e46a34a25d236f6163a5b6fffa2052d9a0c417 已推送 origin/main 並由 ls-remote 核對；首版 tag 仍固定 807579d01c145db327050c2e870e2bf46e6bcb68。
- 下一步依最新取樣處理場邊幾何及同角色色盤，再續蜘蛛女與其餘畫面；029 格式仍待回答。完整 HD 目標保持 active，沒有以十七階段取樣或兩光效代替全目標。

## 2026-10-20：雙向翻轉場邊裁切補正

- 上輪鳳凰光效為實際進展。本輪查乾淨工作樹與現況，命中復古重製／畫面對拍及規格閘門；分析原函式時讀 use-ida-pro-9-4 與指定工具鏈入口。技能是指向 ida_94_official 的連結，第一次僅掛 .codex 時讀不到，改用已存在的實體專案唯讀掛載；沒有修改上游。image inspect 子命令遇 sandbox 的 Docker socket 拒絕，標準 docker inspect 成功，未改用主機工具或更換 image。
- 沿既有 ida-pro-9.4-idapython:py312-v1 與 UID 1000，在 sf-hd-draw-v2.i64 的一次性副本查詢四支原 blit，每支六個直接 caller。正式 DB 未用作 IDA 寫入目標，SHA 保持 5a122f625e659633f1e29ea1cb024fb4b1c31405031bf90d92dfe115ac00e2ca；原檔／runtime 副本唯讀。輸出 schema、IDA 9.4、SF.EXE SHA 與舊 bytes／operand 皆核對，收據為 edge-clip-research-v1/ida.json。log 只留本機，不複製授權環境至 Git。
- 原 sub_146E8 在 14729h..1472Fh 將右裁切移入 BL，sub_1480A 的 14854h..14858h 則保留左裁切。現行共用公式錯把兩者當相同。verify_edge_clipping.py 從原檔及四份正常 CPU 層獨立重組，槽 10／11 的 2,603／2,499 寫入點全部吻合左起點；舊公式有 2,006／3,209 不符點。完整影像翻轉與裁切亦相同，review.json 綁定來源、工具及 DB 身分。
- 040 經 DRAFT／審查升 READY，才只修改 Placement 的 C0h 來源起點；只水平翻轉與目的 clip 不變。共享獨立 verifier 同步原版差異。沒有移除 038 每格 CPU 核對或整格回退，沒有改原版程式、規則、動畫、位置及資料格式。
- 真實四份 CPU fixture、三份完整群組與壞遮罩拒絕通過；蜘蛛女只驗法蘭克目標層，不假稱缺稿本體已完成。038 兩類舊幾何、鳳凰兩光效、十六份原畫格／三十二個定位樣本、可用 internal／cmd 測試與 vet 通過，記錄於 edge-clip-build-v1/tests.log。
- Linux／Windows／macOS Intel／Apple Silicon 在既有 Go 1.24.13 工具鏈編譯，44 份實際輸入及標頭核對。Linux SHA 56c9aa72fba9d04f83d59077ae9528333bdfef338d4773a0adb54166facfaae2，四平台精確產物與 build.json 晉升 bin，promotion.json 保存前後 SHA；038 二進位保留在 character-geometry-build-v1/bin。開發版仍未發行 v.0.1.1-20261020。
- edge-native-0-new-v1／0-old-v1 各五張，以正常選角及十七階段普通動作重現槽 10 的 C0h／RightClip 1。新版本維持 HD，舊程式整格原貌；同格原圖層、HUD、陰影與 CRTC、模式切換、恢復逐點及繼續操作通過，HD 可見變動 20,835 點。
- 子彈 v1..v3 沒有捕捉目標，failure.json 原樣保留。兩次同類失敗後重查正常玩家驗證路由，對照 phase_states／原始取樣，分清換邊、接近及普通拳與投技。v2 曾跳過前跳、v3 曾加入普通雙人接近與單拳，皆未觸發，不稱有效修法。v4 仍在原本十七階段的 close-punch 進入 path 37 並擷取槽 11／RightClip 9；沒有執行備用的接近或方向加拳分支。未驗備用程式已移除，不把成功歸因於未執行操作，也未調正式程式或亂數。
- edge-native-2-new-v4 五張已獨立重組通過，2,499 原始寫入點、16,272 可見 HD 變動點；切換維持原狀態，恢復逐點及繼續操作通過，另目視場邊截斷與原版層次。三份成功收據共十五張，各自綁定當時的自動化副本。GUI 輸入時機可能改變投技先決條件，不宣稱每次重放都逐格相同；幾何原檔／CPU 對拍不依賴挑選亂數結果。
- 全部工作在受限 Docker，--rm／--network none／--user 1000:1000。GUI 3g／2 CPU／256 pids／1560 秒，IDA 2g／2 CPU／128 pids／300 秒，Go 建置有界；Xvfb／遊戲均由 finally 結束。未在主機跑分析或遊戲，未新建重複 image。
- 040 限定 CONFORMED，008／038 加後續解決入口，唯一現況、工作清單及驗證矩陣同步。README 新增 edge-clip-hd.png，來源及 SHA 保存於既有截圖索引。沒有原貌圖、色盤、資料庫或原始 CPU 層進 Git。
- 同角色法蘭克的第二人 16 色，在 MAN.COL 實檔 192 及 REFMAN.PIC 實檔 209 找到相同 48 bytes；來源身分保存在 alternate-palette-source.json。尚未證明 runtime 選哪份或 HD 調色方法，只新增來源事實，不接未證實色盤。

重驗命令於上述容器執行，輸出必須全新；原生／來源 verifier 可重驗既有資料。回查 GUI 失敗先讀 failure.json／phase_states，不因未捕捉目標改正式定位。

```sh
python3 tools/verify_edge_clipping.py --research /project/workplace/edge-clip-research-v1
KDZZ_HD_FIXTURES=/project/workplace KDZZ_ORIGINAL_ROOT=/orig go test -p 1 ./internal/hd -run 'Test(MirroredEdge|CharacterGeometry|PhoenixEffects)' -count=1 -v
KDZZ_HD_FIXTURES=/project/workplace KDZZ_ORIGINAL_ROOT=/orig go test -p 1 ./internal/renderdata -run TestOriginalLayerReplayAndSpritePlacement -count=1 -v
python3 tools/edge_clipping_smoke.py --binary /project/workplace/edge-clip-build-v1/bin/superfighter-linux-amd64 --output /project/workplace/edge-native-0-new-v1 --hd-characters /project/assets/hd/characters --player0 0
python3 tools/verify_edge_native.py /project/workplace/edge-native-0-new-v1
python3 tools/build_desktop.py verify --output-dir /project/workplace/edge-clip-build-v1/bin --receipt /project/workplace/edge-clip-build-v1/build-verification.json
```

舊程式對照指定 character-geometry-build-v1/bin 並加 --expect-original；第二新案例用 player0 2。實際成功腳本副本保留於各收據目錄，現行工具已移除未執行備用分支。

- 收尾核對 128 原檔／1719 runtime、原 i64、94 PNG／102 payload 共 121,070,684 bytes、1485 鍵／67 PNG、四份新二進位與 44 份輸入通過。README 與素材索引有 131 個受追蹤相對連結；首版八 ZIP 與本機影片 SHA 保持，沒有 root-owned／.md 目錄或專案容器殘留。建稽核腳本的一次動態 shell 命令遇 Docker socket 拒絕，後續改用掛載的 Python 檔在容器內生成及執行，通過 final-audit.json；沒有回到主機分析。
- 下一步為同角色色盤、蜘蛛女其餘動作及其他畫面；029 格式仍待回答。完整 HD 保持 active，未重發首版、移動 tag 或把已驗切片當全目標。功能提交 57dc20cb0df83fbd6a8a4e95c99bd0aa354fd6c8 已推送 origin/main 並由 ls-remote 核對；首版 tag 仍固定 807579d01c145db327050c2e870e2bf46e6bcb68。


## 2026-10-21：同角色雙色 HD 與第二人首勝

- 依既有 B 畫風及保留原版辨識範圍接續 041。固定 IDA 9.4 image 查原 i64 一次性副本，直接字串 xref 為空，改由 immediate operand 與資料段基底找到原 man.col 載入端；原名／bytes／位址分級保留。正式庫及原檔唯讀。
- Docker Go 1.24.13 執行 duplicate_palette_receipt.go，十一人正常同角雙打各待機／行走；獨立 verify_duplicate_palettes.py 核對二十二格、四十四角色層、原色盤及十一景來源。四組私有比較覆蓋十一人；印第安喬錯用特效槽的早稿保留，以正常槽 1 補正。
- READY 後接入不可變配色視圖。只接受同角色第二人的完整已驗主色盤，原圖與 alpha 保持；FX、第一人、異角及未知色盤不套用。HD RGB 轉移是呈現近似，沒有移除來源核對、改姿態鍵或原版狀態。
- duplicate-palette-build-v1/tests.log 保存真實二十二份 fixture 的二十一選擇／一份缺稿回退、色盤錨點／透明度、壞檔與未知拒絕、先前幾何／光效及可用 internal／cmd 測試／vet。四平台建置為四十五份實際編譯輸入，逐平台來源與檔頭核對後移入 bin，040 基底保留於 edge-clip-build-v1。
- duplicate-palette-native-new-v1／old-v1 因腳本把 KP_Left 的觀測值誤判為 1 而失敗，保留 failure。正常來源確認為 2，只修腳本；v2 新／舊程式各七張通過行走、放開、同狀態切換與恢復。這是驗證腳本問題，不列產品缺陷。
- duplicate-palette-win-core-v1 經 5,543 成對邊界、八份 WIN 取樣及四份來源重組；Linux duplicate-palette-win-native-v1 七張，綠色第二人首勝、FRANK WIN、切換／恢復、下一回合與右側一勝通過。此案時間歸零、生命 76／124，未冒稱擊倒。verify_duplicate_palette_native.py 獨立核對三組二十一張的完整來源與藍綠可見服裝。
- README 新增同角雙色截圖，圖片及 source.json 收錄 Git；原貌、原色盤、比較稿及完整收據留本機。素材維持 1485 鍵／67 圖集、94 PNG，沒有改生成圖。跨日沿用已凍結、未發行的 v.0.1.1-20261020，不移動首版 tag 或重包已發布檔案。
- 首版範圍再次依使用者回覆確認：鍵盤重綁、魔王選角及已驗斬四招，其他角色四格可保存而實際快捷拒絕。首版已發布；本輪 041 屬後續開發版，不改既有 Release 範圍。029 多場景格式待回答，蜘蛛女其餘稿、完整動畫、其餘畫面及音訊仍未完成。
- final-audit.json 通過：128 原檔、1719 執行器來源、94 PNG／102 素材、1485 鍵／67 圖集、正式 i64、首版八包及影片雜湊保持；四平台 45 份輸入與晉升八檔吻合，134 個 README 相對連結可由 Git 清單找到。二十一張新原生收據及相依檔雜湊通過，沒有 root-owned 檔或誤建 Markdown 目錄；專案 Docker 容器清單為空。首版 tag 仍為 807579d01c145db327050c2e870e2bf46e6bcb68。
- 實作、來源工具、041 與 README 截圖已提交為 81e9e23a9a9cb269ce21ed5f306a5fc3b75f6143，成功推送 origin/main；ls-remote 核對一致，首版 tag 保持。工作樹當時乾淨，本筆只追加推送紀錄。


## 2026-10-21：十一景捲動與兩張候選修稿

- 上輪 041 是有效進展，維持完整 HD 目標。載入現況、029、規格閘門及 grilling；重新呈現同包自動切換／單景啟動選項，尚未收到答案，不改 production。獨立先做正常來源與可丟棄比較。
- Docker Go 1.24.13 執行 background_scroll_receipt.go，正常雙打十一景，兩人左行 96／右行 192 格；每景八份，共 88 格，所有景觀察到相機 0／159。不是每個 camera 值都已擷取；released 立即保存不作中立輪詢證據。指令上限每景八億步，程序 900 秒外層期限，原檔及執行器副本唯讀。
- Pillow 11.3.0 執行 background_scroll_preview.py，原 XGB、背景色盤／裁切、完整 CPU 層、176 份角色原 bytes／覆蓋與顯示尾列獨立核對通過。第一輪與修稿比較各 88 張；原版前景保留，未當作原生 HD。來源執行及兩次比較工作已 terminal 0，沒有重開活著的工作。
- 檢視十一景全景與右端、火車左端及石窟／舞廳修稿，發現底線偏高與街道字形差異。依 imagegen 技能使用內建工具，各產生一張 B 畫風修稿；改善但尚未定版，不用調參數或 Python 扭圖當作忠實度通過。兩份原 PNG、原來源／父稿 SHA 與精確提示詞由 import_background_revisions.py 收錄，舊 PNG 全部保持。
- 素材目前 96 PNG／105 筆 payload／125,079,293 bytes，目錄 109 檔；角色包仍 1485 鍵／67 圖集。原圖／色盤、原版前景比較及 raw 收據只留 workplace。README 只更新穩定候選入口，029 仍 DRAFT。四平台 041 程式、VERSION 及首版八包／影片／tag 均不改。
- background-scroll-preview-v2/final-audit.json 通過：102 筆原 payload 逐筆保持，新增兩張 PNG 及一份來源 JSON；128 原檔、1719 執行器檔、正式 i64、四平台 45 份實際編譯輸入及已發布八包／影片均吻合。88 格／176 角色來源與兩輪比較逐檔 SHA 可回查，141 個 README 相對連結可由 Git 清單找到。沒有 root-owned 檔或 Markdown 目錄，專案 Docker 容器為空；Git diff --check 通過。第一輪 verifier 原始碼已按其既有 SHA 保存，沒有以新版工具冒充舊收據。
- 來源工具、兩張修稿、精確提示詞及文件已提交 a3a4cd8ce66ae2201b2733902cf0818d908105e7 並成功推送 origin/main，ls-remote 核對一致；首版 tag 仍為 807579d01c145db327050c2e870e2bf46e6bcb68。本筆只追加推送紀錄。


## 2026-10-21：金太極十種特殊光效接入

- 上輪背景捲動及修稿為有效進展。029 格式仍待回答，本輪不重問或依沉默實作；改從特殊動作正常來源推進 HD。載入 remake／驗證／規格閘門與 009。
- special_effects_receipt.go 以明示鍵盤序列取樣。鬼丸 PK 114 格維持 HD；蓄力後出拳 v2／v3 於相同原 frame 空層，v3 補存 failure 與 sample-18。沒有補圖放行或再盲重跑，缺口另列。金太極四組普通方向／拳腳取得 352 格、十份第二色盤來源，二十五格缺件。
- verify_special_effects.py 獨立核對原檔、來源、CPU 覆蓋與第二色盤。初版 verifier 沿用每個長階段都有 draw 的假設，在兩個一輪詢階段失敗；改檢查明示階段子集及順序，缺少畫面階段明列，不改產品。十份光效及完整 CPU 重組通過。
- 使用內建 imagegen，依原圖生成青藍拳影／刀光、金黃彈，保存原 PNG、提示詞、參考 SHA 與透明矩形。READY 後以既有版本 3 登錄十鍵，所有舊姿態／PNG 不變；只將圖集上限由 100 增至 101 Mi 像素，最壞 RGBA 增 4 MiB，其他驗證保持。候選總像素 105,769,615，清單 521,555 bytes。
- special-kim-v2 同格新舊選擇 327→352，補齊 25 格、無退步；十份真實 fixture、未知槽／壞來源／錯色盤拒絕，以及 038／040／041／039 既有測試通過。首次全套測試帶入所有 fixture 環境，120 秒範圍太大而逾時，tests.log 原樣保留；在同工具鏈移除該全域 fixture 環境後，例行 internal／cmd 與 vet 通過於 routine-checks.log，沒有把環境／測試範圍問題列產品缺陷。
- Linux kim-effects-native-full-v1 十一張及 old-v2 十一張通過普通選角、實際方向／拳腳、三類光效、完整原圖層／介面／陰影／CRTC、第二色盤、切換／恢復逐點及繼續操作。新例可見變動點 4,023／12,983／6,506。old-v1 未觸發首招，失敗及原腳本保留；新版腳本等待原版 key_values 實際讀入後計最低輪詢，old-v2 成功，沒有重寫舊成功收據或宣稱跨案例相同時序。
- 四平台四十五份編譯輸入、檔頭及逐檔 SHA 通過後晉升八檔至 bin，041 基底保留。素材晉升為 1495 鍵／68 圖集，整個目錄 97 PNG／107 payload／125,769,763 bytes、111 檔；原資料及已發布首版不變。README 補青藍刀光的正常 HD 截圖，圖與精確提示詞一起收錄 repo。
- 原 READY spec 已存 kim-effects-art-v1/042-ready.md，prepare_kim_effects.py 原始碼及審查 SHA 一同保留。重生舊 READY 審查時，Docker 將該已驗檔唯讀覆蓋 /project/docs/spec/042-kim-effects.md，執行 `python tools/prepare_kim_effects.py --base workplace/hd-characters-phoenix-effects-v1 --output workplace/<新的輸出目錄>`；不把目前 CONFORMED 的文件雜湊或新包冒充當時輸入。
- kim-effects-build-v1/final-audit.json 通過：原 1485 鍵／67 PNG、104 筆未變 payload、128 原檔、1719 執行器來源、正式 i64、首版八包及影片均保持；只更新角色 manifest 並加入新圖／來源。現行 1495 鍵／68 圖集、97 PNG／107 payload、147 個 README 相對連結及四平台 45 份輸入核對。22 張新原生畫格、25 格同格改善、READY 快照及來源 SHA 可回查；沒有 root-owned 檔、誤建 Markdown 目錄或專案殘留容器，git diff --check 通過。
- 實作、圖集／提示詞與正常 HD 截圖提交 f7c5ce2ffebe5730ae575fd505ea66ced51e5aa1，成功推送 origin/main 並由 ls-remote 核對。首版 tag 仍是 807579d01c145db327050c2e870e2bf46e6bcb68；本筆只追加推送紀錄。

## 2026-10-21：鬼丸額外武器分層與 HD

- 根因為主色盤額外圖像遭既有 D0h／F0h 限制拒絕，第二人另缺 4523h 返回。先以正常原版兩側／同角各 200 格、404 次 blit 及 IDA 9.4 原呼叫審查，保存 READY 全文及雜湊後才實作 043。
- 分層只接受已驗主色盤返回點及對應玩家 RAM 指標；HD 依實際色盤選 bank，主色盤額外圖像再核對 CPU 覆蓋／色號。同角替代色沿 041；既有美術、原版規則、輸入及存檔保持。
- 三組正式 Core 共 602 格全部完整且選到 HD，559 個觀測關／開成對邊界的原版狀態及像素一致。Linux 新／舊程式各五張完整核對切換／恢復與繼續操作；新版來源 35 武器維持 HD，舊版安全原貌。README 已加入實際 HD 截圖及來源。
- Go 例行測試／vet、三組真實來源／拒絕及金太極第二色盤／同角回歸通過，真實 fixture 組 22.583 秒。四平台四十五份編譯輸入及檔頭通過；primary-extra-build-v1 保存八個編譯產物／收據及 promotion.json，移入 bin。Linux SHA 47ff4670d1b726f7ee94cc47be6c30ce3bbd6cb9fd6f3e64c0725cf47f657ad9，版本仍為未發行 v.0.1.1-20261020。042 基底及已發布首版八包／影片／tag 不覆寫。
- 驗證條件及診斷腳本失敗、原因與乾淨重跑見 RESEARCH-LOG 的 043 紀錄。第二人及同角只驗原執行／Select；完整動畫、蜘蛛女其餘動作、背景、音訊及實體手把另續。029 格式仍等原問題回覆，不自行決定。
- 收尾核對與 Git 推送結果另追加；所有正式來源及原始資料唯讀，容器使用有界 --rm／UID 1000。

- 最終稽核 `primary-extra-build-v1/final-audit.json` 通過：128 原檔、1719 執行器來源、正式 i64、97 PNG／107 catalog／111 素材檔及首版八包／原曲影片不變。149 個 README 相對連結均已追蹤，無原版或 raw 暫存入 Git；擁有權／誤建目錄通過，本專案容器已清空。
- 實作提交 `8f4209345f3235cd569a5adf2459683a2950268f` 已推送 origin/main，遠端完整提交相同。首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`；本段為其後的文件收尾，不建立新 Release。

## 2026-10-21：044 四人二十一份特殊技 HD 光效

- 上一輪為已完成的鬼丸修正；本輪為具體進展。先走五人普通方向／拳腳，共 1,654 格，獨立原檔／CPU 審查發現鳳凰三鍵、嵐七鍵、小丑八鍵、印第安喬三鍵。子彈該序列 266 格無缺件；快捷維持既有已驗範圍。
- 使用內建 imagegen 補六張透明原 PNG，保留精確請求、生成原 bytes、原始參考及修稿。小丑舊稿三格連接失真不註冊，另生成分離光影，按實際 58／59／57 的形狀順序登錄 2／0／1。嵐原稿 alpha 0..254 符合既有載入器，初匯入腳本誤要求 255，依原載入契約修正；沒有修改或正規化生成 PNG。
- READY 審查保存於 remaining-special-audit-v1/art-v1。新清單 530,039 bytes、115,204,291 像素；僅將解析上限 512→520 KiB、圖集 101→110 Mi 像素，容納最小必要資源，不改格式或放鬆來源／色盤檢查。正式清單 1516 鍵／74 圖集，SHA 164eef46667563bed1d239a2af113f95f47e7a8831f98f82ffe97e3fc13adb20。
- 四人同格新／舊素材比較 1,388 格，補齊 76 格，沒有原成功格退步；鳳凰十格其他色盤拒絕保持。21 真實來源／篡改／超量拒絕、既有同角／金太極／鬼丸回歸通過，真實組 37.787 秒；例行 Go 測試及 vet 通過。
- Linux 新包六個光效族、四人代表舊包五個光效，共 49 張完整核對原檔、RAM 層、HUD／陰影／CRTC、同狀態切換／恢復及光效消失後操作。小丑舊包只以新局分離光影作完整代表案例，其他舊包長序列／光彈嘗試未通過，失敗保留，不重試到碰巧成功。新包兩類皆通過。嵐／喬的初版驗證曾把待機當光效清空，腳本修正後乾淨重跑；不列為產品缺陷。
- 六 PNG 及來源／精確提示詞已收錄 assets/hd/characters。現有 103 PNG、114 catalog、130,915,661 payload bytes、118 素材檔，所有舊 PNG／姿態保持。README 加入兩張正常遊戲 HD 擷取，原貌、原曲、原始 palette 與 raw 收據不上傳。
- remaining-effects-build-v1 四平台／45 份實際編譯輸入、檔頭及八檔晉升通過；Linux SHA 5834c7b894ab51116e8ac6a58e4069c637cc4a852124564e93eeeb8853c7429d。未發行版仍為 v.0.1.1-20261020；043 二進位保留，首版八包、影片與 tag 不變。
- 重建素材用 tools/prepare_remaining_special_effects.py 的 --base workplace/hd-characters-kim-effects-v1，原稿／審查在 art-v1；CONFORMED 文件取代 READY 後，先將 art-v1/044-ready.md 唯讀覆蓋掛載到 docs/spec/044-remaining-special-effects.md 再重建新輸出，不偽造目前文件的 READY 身分。正式圖片不重生成，來源及輸出雜湊皆保留。
- 後續仍有鳳凰其他色盤、蜘蛛女其餘姿勢／勝利、背景格式決定及標題／選角／結果等完整 HD，不能以這批光效完成宣稱全作完成。收尾與推送結果另追加。

- 最終 remaining-effects-build-v1/final-audit.json 通過：128 原檔、1719 執行器來源、正式 i64、首版八包及本機原曲影片不變。1516 鍵／74 圖集、舊 1495 鍵、103 PNG／114 catalog／118 素材檔及六圖原 bytes 核對，155 個 README 相對連結均已追蹤。沒有原版、raw 或工作產物入 Git；擁有權／誤建目錄通過，所有本專案容器均已清空。
- 實作提交 `d23429413aaa6ffbe4a4c83ee6f0142b267b5b36` 已推送 origin/main，完整遠端提交核對相同。首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`；本段為其後的文件收尾，不建立新 Release。

## 2026-10-21：045 主角色第二色盤接入

- 續 044 十格色盤拒絕。原呼叫與獨立原版 414 次 blit／200 格證實主角色也使用 D0h／F0h，來源為鳳凰 48／法蘭克 54。先比較實際來源色號與 HD 調色，保存 READY 全文及 review.json 後才改正式 Select。
- 使用原 bank 0 的同姿態不可變視圖，限該來源實際非透明色號參與 RGB 轉移，保留 alpha／PNG／清單。每次選擇核對完整十六色及原 CPU 幾何，不轉用額外光效美術。修正與回填索引見 045；原版規則、快捷、存檔與素材格式保持。
- secondary-main-core-v3 的 338 格全維持 HD；與 044 同序列來源 trace 比較補十格、無退步。Linux 新／舊程式各八張普通出招／受招，獨立核對原檔、完整層／HUD／陰影／CRTC、切回原貌、恢復與後續操作。兩張 HD 整合截圖及來源已加入 README，原貌及完整收據留本機。
- 例行 internal／cmd 測試及 vet 通過。兩來源真實 fixture、同角替代色、金太極、鬼丸及四人光效回歸 67.790 秒通過；失敗工具紀錄與原因另見 RESEARCH-LOG，不因 hash 失敗忽略來源檢查。
- 四平台每份 46 個編譯輸入與 ELF／PE／Mach-O 架構核對通過。secondary-main-build-v1 保存二進位與收據，Linux SHA ae99fbe7b609afeb96d262ac1d9d4c511fdb76f9252a02ca0e30dfbf908c2a7d；045 沿未發行 v.0.1.1-20261020，044 舊版保留。素材仍為 1516 鍵／74 圖集、103 PNG／114 catalog／118 檔。
- 完整 HD 仍有蜘蛛女其餘姿勢／WIN、背景與標題／選角／結果等工作。029 格式問題仍待原回覆，不因普通繼續擴張授權。本輪不新建 Release；首版八包、原曲影片與 tag 保持。最終稽核、二進位晉升、容器清理及推送結果另追加。

- 最終 secondary-main-build-v1/final-audit.json 通過：128 原檔、1719 執行器來源、正式 i64、1516 鍵／74 圖集與 118 素材檔不變；首版八包及本機原曲影片保持。158 個 README 相對連結均已追蹤，四份規格勘誤護欄通過。八個二進位／收據已晉升 bin，044 基底保留；無原版及 raw 入 Git，擁有權／誤建目錄通過，本專案容器已清空。
- 實作提交 `7d577e86ae60569d6107fd65e20324871a56f369` 已推送 origin/main，遠端完整提交核對相同。首版 tag 遠端仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`；本機未抓取該 tag，採遠端核對。本段為文件收尾，沒有新 Release。

## 2026-10-21：046 標題／主選單候選

- 上一輪為 045 已推送進展。本輪轉向完整 HD 中尚缺的標題／主選單，依既定 B 畫風製作黑紫人物與紅金字標兩張原 PNG，分層保存。沒有改正式呈現或格式，046 保持 DRAFT。
- 正常四次啟動、四個原按鈕共 51 份擷取。獨立解析 TITLE.CPM 與無色盤的 SFNAME.CPM，36 份初始標題逐色號重組；完整 RGB 亦吻合。確認原字標會循環換色，取樣兩個相位；初版全靜態色盤假設已訂正，原版動畫不凍結。單打／雙打選角、原設定畫面及正常結束已分別核對。
- assets/hd/candidates 保存兩張生成原 PNG、精確 prompt、SHA、實際尺寸與候選分類。HD 素材增為 105 PNG／117 catalog／121 檔、133,236,952 payload bytes，原 114 筆及正式 1516 鍵／74 圖集保持。沒有重編碼原 PNG。
- tools/preview_title_menu.py 作 1600×1000 靜態構圖。人物／字標按原版矩形縮放，四個標籤範圍有界；字標 alpha 1..15 有雜點，原型採 alpha>=16 的可見 bounds，原稿保持。HD 候選預覽與來源已加入 README，原貌及完整比較留本機，不稱原生整合畫面。
- 正式標題身分、選取狀態、色盤動畫、載入格式及視覺尚待補齊後審 READY。029 原格式問題仍待回覆，不新增未確認的產品決定。四平台程式沿 045 的 46 份編譯輸入，本輪沒有 production 修改，不重建或重發首版。原資料、正式 i64、首版八包及本機原曲影片的收尾稽核與推送結果另記。
- workplace/title-art-v1/final-audit.json 通過：128 原檔、1719 執行器來源、正式 i64、角色清單、四平台程式、首版八包及影片不變；新增兩張 PNG 原 bytes、候選清單與 51 份來源收據核對通過。168 個 README 相對連結均已追蹤，003 勘誤及新檔索引通過，原版及 raw 未加入 Git；擁有權／誤建目錄通過，本專案標題容器已清空。
- 候選與工具提交 `7ab724b2232d683fed43b6a2d310dfca6ec645c6` 已推送 origin/main，遠端完整提交核對相同；首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段為其後的文件收尾，046 仍 DRAFT，沒有新 Release。

## 2026-10-21：046 標題進出、完整換色與材質比較

- 上輪候選已推送，屬於進展。本輪補原標題生命週期、原選項與八相位。IDA 9.4 原函式、正常檔案開啟、重定位及動態 CPU 取樣相互核對，正式 DB 與原版保持。具體定位及失敗分類見 RESEARCH-LOG。
- title-lifecycle-v5 正常鍵盤四選項、原設定往返與單打選角，title-demo-v2 正常閒置至原 mode=4。獨立核對 37／128，共 165 份完整標題、八個字標相位、八筆框線色及游標。原消費點先讀中立再讀按下，避免短按在繪製／ISR 間漏讀；未修改原輸入或規則。
- 全圖 RGB 轉移因原 7／18 同色但材質不同而拒絕。改作原位置遮罩的可丟棄候選，八相位 alpha／零相位／固定下半字標保持，原十六步與四選項接觸圖已目視。材質位置投影維持 hypothesis，不進 production；兩張生成原 PNG 不改、不重生成。
- title-animation-v3 保存八配色、十六格 PNG、候選 GIF 與四選項比較。GIF 只留本機，速度是示意值；README 新接觸圖明列候選及未接原生。新構圖也修正後三個原按鈕各一像素位置差異，舊靜態稿留作歷史。
- 原來源研究已足夠，後續回到正式載入方式、材質視覺與原生驗收，不再深挖檔案 helper 或硬體迴圈。046 仍 DRAFT，029 原格式問題保持；沒有 formal API、資料格式、存檔、原版或四平台程式修改，不重建或重發首版。素材維持 105 PNG／117 catalog／121 檔；收尾與推送另記。
- title-research-v1/final-audit.json 通過候選範圍稽核：165 份原標題、十個 runtime 定位／112 筆 MZ 重定位、八配色／十六步及原稿保留通過。170 個 README 相對連結均已追蹤，003 回填護欄及新檔索引通過。128 原檔、1719 執行器來源、正式 i64、105 PNG／117 catalog／121 檔、四平台 46 份編譯輸入、首版八包及影片保持；沒有原版、raw、GIF 或工作產物加入 Git。擁有權／誤建目錄通過，本專案標題容器已清空。
- 工具與比較稿提交 `08d84714def56c78280a1cd19200002825362feb` 已推送 origin/main，遠端完整提交核對相同；首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段為其後的文件收尾，046 維持 DRAFT，不建立新 Release。

## 2026-10-21：046 隔離原生標題原型

- 使用者確認首版先發布已驗快捷功能，其他角色限制明列；此決定已由既有首版落實，不覆寫已發布封包。本輪接續 HD，把標題比較放入隔離的原生 module。正式 `internal/`、素材格式、46 份編譯輸入及四平台 bin 保持。
- `prepare_title_native_prototype.py` 保存 86 份副本檔案、模板、原編譯輸入及編譯命令；Go 1.24.13 的 Linux 原型 SHA 為 `95f4eeb5471d714d26271576c8dedf33519d84fe89c4cf327d4dc4d7dc6ed331`。輸出只在 title-native-prototype-v1，不晉升正式包。原型以原生命週期及完整當前來源核對後顯示候選，局部或未知狀態退回原貌。
- title-native-full-v1 正常鍵鼠走標題八相位觀測、同狀態切換、設定往返、雙打選角及屋頂對戰，保存九張。title-native-fallback-v1 未載入候選，四張原貌及後續導航通過。原始資料及執行器唯讀，沒有訓練、座標、勝負或亂數注入。
- `verify_title_native.py` 獨立重建十份完整原標題，十三張顯示資料通過。三張暫停切換的原核心／設定／呈現／指派相同，恢復 HD 的像素相同；原生標題 HD 改變 309,024 個可見像素。設定／選角原貌逐點、屋頂完整圖層及離開標題後恢復既有 HD 通過。驗證器初版錯把戰鬥 192 列的 CRTC 顯示當成標題 200 列，依既有可見範圍契約修正並乾淨重跑；不是產品缺陷。
- README 改放真正的原生原型擷取並明列 DRAFT。候選來源與原稿保留，105 PNG／117 catalog／121 檔、1516 鍵／74 圖集不變。可見游標 GPU、本機以外平台、完整速度及正式載入／損壞驗證未完成；材質位置投影仍是假說，原型不當作已定版或正式接入。
- title-native-prototype-v1/final-audit.json 通過：128 原檔、1719 執行器來源、正式 i64、四平台程式、首版八包及原曲影片不變；170 個 README 相對連結均已追蹤。新增工具與截圖有索引，原版／raw／GIF／原型二進位未進 Git。UID／誤建目錄通過，本專案容器均已退出並刪除。029 格式與 046 定版仍待決定，不重開無關 RE。推送結果另記。
- 原型與截圖提交 `0be4aa982678dac8d4d70bf21b5ea3d965c6d177` 已推送 origin/main，遠端完整提交核對相同；首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`。已展示原生候選並詢問視覺選擇，未回答前不將候選視為定版。本段為文件收尾，沒有新 Release。

## 2026-10-21：046 可見游標及滑鼠入口

- 前輪原型與截圖已推送，屬於進展。本輪補未驗的中央／右界／下界可見游標，正式程式、原型模板、二進位、素材格式及發布版保持。
- title-native-cursor-v1 錯把要求座標 318 作實際位置而超時，失敗保留。正常原入口的 title-cursor-source-v2 十二份穩定取樣證實右界最大 x=304、下界最大 y=184；先前 v1 四百萬步不足四個邊界，v2 依既有正常迴圈採有界三千二百萬步，四份即停止。沒有調整遊戲或放寬完整來源比對。
- 原型沿同一 Linux SHA 95f4eeb5471d714d26271576c8dedf33519d84fe89c4cf327d4dc4d7dc6ed331。cursor-v2 十三張正常擷取驗三個位置的完整原標題、游標黑白 GPU 像素、三組同狀態切換／恢復及滑鼠進選角清除。右下界 HD 已目視，完整原源與像素核對通過，不宣稱越界換列可由正常玩家到達。
- 新驗證器也重審前輪九張／四張，總二十六張通過。新報告另存 comparison-v2.json；前輪 comparison.json 由 Git 保存的原驗證器在原工具路徑重生並核對舊 hash，公開截圖的來源關聯不變。新工具對已有且內容不同的報告拒絕覆寫，須明示新檔名。
- CONTEXT／WORKLIST／046／README 已把可見游標改為限定通過，RESEARCH-LOG 保存根因及來源；沒有新增美術或公開原游標擷取。材質與正式載入仍待原問題回答，046 保持 DRAFT，不新建 Release。最終稽核、容器清理與推送另記。
- title-native-cursor-v2/final-audit.json 通過：三份新審查共二十六張擷取、十二份新增來源及舊 165 份標題證據相符；公開截圖引用的歷史報告 hash 保持。128 原檔、1719 執行器來源、正式 i64、105 PNG／117 catalog／121 檔、46 份編譯輸入、四平台程式、首版八包及原曲影片保持。170 個 README 相對連結與工具索引通過，無原版或 raw 入 Git，擁有權／誤建目錄通過，本專案容器已清空。
- 補驗提交 `e9a0f2f76f6aabc509ad7f47d3675e5900e0a15e` 已推送 origin/main，遠端完整提交核對相同；首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段為文件收尾，046 視覺問題保持待回覆，不新增 Release 或重複提問。

## 2026-10-21：街道候選上排塗鴉修稿

- 上輪游標補驗已推送，屬於進展。本輪回到缺少的 HD 內容，核對外部蜘蛛女目錄仍為既有兩批十五張，未按檔名重新接入。029／046 原問題未回答，不擴張為格式或定版同意。
- 依既定 B 畫風與素材上傳授權，以內建 imagegen 修街道上排塗鴉。第一張仍出現錯誤字形，保留 street-revision-v1/rejected-first.png；第二張可辨讀 SUPER STAR，另存 street-i4-v2.png，沒有覆寫舊圖。SUPER STAR 為原圖字形的強推論，未從原字串解出；下方塗鴉仍未核對，不能稱全圖文字完成。
- 新 PNG 為 1922×818，SHA a44e25713aeced5017d05bbbaad2613fb46674695290d9b8f6ef37c8a425b6bd。生成工具也重畫區外像素，整圖差異非零，區外各色平均絕對差約 9.1–10.2；來源清單保存量測及精確請求，不宣稱只有文字像素改變。import_street_revision.py 保存候選原 bytes、兩次請求及舊 117 筆 catalog 作核對。
- 街道八份正常捲動來源、十六個角色 packed 原檔／CPU 層、原 XGB／色盤／完整圖層／CRTC／尾列通過。scene 2／相機 0 與 159 的新比較已目視；前景仍為原版，屬於軟體構圖比較，不是原生 HD 接入。background_scroll_preview.py 新增明示街道修稿及單景篩選，不更動正式程式。
- 新原 PNG 與精確提示詞收錄 assets/hd/candidates，catalog 增為 106 PNG／119 筆／123 檔、135,498,255 payload bytes，舊 117 筆、1516 鍵／74 圖集保持。README／素材索引／029／現況表已更新；另修素材索引把標題誤稱尚無原生候選的舊敘述。正式 bin、首版八包與影片保持，收尾稽核與推送另記。
- street-revision-v1/final-audit.json 通過：八份新比較、十六個原角色層、相機 0／159、生成原 bytes、精確提示詞與舊 117 筆素材保持。175 個 README 相對連結與新檔索引通過；128 原檔、1719 執行器來源、正式 i64、46 份編譯輸入、四平台程式、首版八包及原曲影片不變。未公開原版、raw 或比較圖；UID／誤建目錄通過，本專案容器已清空。
- 修稿與工具提交 `17e43385f7125fb4f95de7fae66c72075fbd809f` 已推送 origin/main，遠端完整提交核對相同；首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段為文件收尾，029 仍 DRAFT，不新增 Release。

## 2026-10-21：047 十一人選角肖像候選

- 上輪街道修稿已推送，屬於進展。本輪回到尚無 HD 美術的選角肖像，沿 025 已驗原消費端與 B 畫風，不重開來源函式考古。047 為 DRAFT，沒有更動正式選角、按鈕／導航、資料格式、角色動作或原版規則。
- export_selection_portraits.py 核對 BIGFIG.XBB SHA 4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477、十一筆 21F1h 與每筆 300h 起的 89×89 色號，輸出原圖只在 selection-portraits-v1。原定位及正常兩側證據沿 025，不把靜態匯出當作新增正常玩家路徑。
- 內建 imagegen 逐一產出十一張 1254×1254、不透明肖像原 PNG。各自原肖像控制身分、顏色與裁切，斬的新稿僅作筆觸參照。全部已與原圖並列目視，主要辨識特徵可對應，但鬍鬚／瀏海／面部彩繪／頭飾及五官比例仍是近似，不宣稱臉部完全忠實。蜘蛛女這次只有臉、髮與頸，不代替仍缺的戰鬥動作。
- import_selection_portraits.py 保存原 bytes、十一份完整提示詞、原來源偏移／色號與色盤 hash，並作純 HD 候選接觸圖。原圖／HD 並列只留本機，公開預覽明列非正式 UI；模型版本未由工具公開，不自行填寫。沒有重編碼生成原 PNG，舊 119 筆素材保持。
- verify_selection_portraits.py 直接從原 bytes 重建十一份 RGB，原參考、角色順序／偏移、候選 PNG、1254×1254／不透明及 catalog／預覽來源核對通過。首版驗證器在 convert 後才呼叫 Pillow verify，觸發檔案生命週期錯誤；改為重新開檔先 verify，乾淨重跑通過，不列產品缺陷。
- 素材現為 117 PNG／131 筆 catalog／135 檔、161,069,925 payload bytes；正式 1516 鍵／74 圖集及 bin 保持。README、素材索引、047、CONTEXT／WORKLIST 已更新。標題定版與背景格式原問題仍待回答，本候選不代答、不擴張首版。最終原始資料／素材／交付／連結與 Docker 衛生稽核、推送另記。
- selection-portrait-import-v1/final-audit.json 通過：十一張 1254×1254 與內建工具原輸出逐檔相同，十一份原 RGB、角色順序／偏移、純 HD 預覽來源及舊 119 筆素材保持。183 個 README 相對連結、047 與新檔索引通過。128 原檔、1719 執行器來源、正式 i64、46 份編譯輸入、四平台程式、首版八包與原曲影片不變。無原版／原色盤／原圖比較或 raw 入 Git，UID／誤建目錄通過，本專案容器已清空。
- 十一人候選與工具提交 `2ad3a012dbef64b77651dd4f098f3a3bd162ab4a` 已推送 origin/main，遠端完整提交核對相同；首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段為文件收尾，047 維持 DRAFT，不建立新 Release。

## 2026-10-21：047 隔離原生選角肖像

- 前輪十一張候選已推送，屬於進展。本輪把它們放入正式來源的隔離副本，僅覆繪原位置兩側大肖像；正式程式、選角按鈕／導航、格式、設定、原 PNG 及 Release 保持。背景、VS 與原八人縮圖仍原貌，不宣稱完整選角 HD。
- prepare_selection_native_prototype.py 保存 85 份副本、模板及原 46 份編譯輸入。原型每次讀原選角狀態、完整過濾顯示、兩側原色號／三十二色，主動側須符合原游標才繪製；未知或繪製中間狀態退回原貌，不重播快取。候選清單及十一張原 PNG 核對後整組載入，未設定原型環境變數時保留原貌。固定載入方式只供研究，不當作正式格式。
- 首輪 full-v1／fallback-v1 錯把第二人起始游標當成 0；原版保留第一人的 10，與既有原探針相同。失敗保留。修正只使腳本依實際游標送正常按鍵，再重跑；沒有調整原遊戲。managed 紋理版 full-v2 另發現蜘蛛女恢復時 386 個像素、各色最多 1 的差異，原狀態與來源相同；fallback-v2 通過，但不把該 managed 版本列為完整原型通過。
- 依固定 Ebitengine v2.9.9 已知 API，原型肖像改用 Unmanaged 獨立紋理，保留 mipmap 縮小品質。selection-native-prototype-v2 的 Linux SHA cde6e389e4aacb6141e9d5d62192925e9ee540f55f0778a757f2d90623b396ad；舊 v1 原型與失敗保留。atlas 相關原因維持強推論，不深挖圖形驅動。
- full-v3 二十九張正常雙打擷取遍歷兩側十一人，fallback-v3 十五張以斬及三魔王兩側抽樣未載候選回退。獨立核對 61 份 BIGFIG 原色號／色盤、38 份 GPU 候選／鏡像方向、框外原貌、兩組暫停切換／恢復及進屋頂對戰清除全部通過。兩組恢復的 HD 像素相同；Pillow 與 GPU 的縮小方法不同，不稱採樣逐點 parity。
- 私有完整原生畫面已目視，含原版背景／縮圖而不公開；README 保留純 HD 接觸圖並更新隔離原型範圍，沒有把候選圖改稱原生收據。素材仍為 117 PNG／131 catalog／135 檔、161,069,925 payload bytes、1516 鍵／74 圖集。047、029、046 的正式視覺／格式閘門保持，未驗單打、其他平台、損壞候選與實體手把。收尾稽核與推送另記。
- selection-native-prototype-v2/final-audit.json 通過：兩條原生路徑共四十四張、61 份原來源及 38 份 GPU 候選／方向辨識，私有編譯來源及只變動肖像儲存方式的對照已核對。183 個 README 相對連結與新檔索引通過；128 原檔、1719 執行器來源、正式 i64、所有素材、正式 46 份編譯輸入、四平台程式、首版八包與原曲影片不變。未公開原版圖／raw／原型二進位；UID／誤建目錄通過，本專案容器已清空。
- 原型與正常流程驗證提交 `68c9fd7aa5b988dbcfff9890dc0a68e823682da4` 已推送 origin/main，遠端完整提交核對相同；首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段為文件收尾，047 保持 DRAFT，不建立新 Release。


## 2026-10-21：047 完整選角靜態 HD 比較

- 使用者首版快捷範圍沿已確認限制，已發布首版保持。本輪接續缺少的選角美術，查證 SELMAN.CPM 是完整選角背景，SELECT.CPM 是設定畫面；沿 025 既有資料，不重開消費端逆向。
- 內建 imagegen 產出一張 1589×990 透明 VS，SHA d2c6d87328e41df73bb7cf7c03c82942390199be6efe965d3a87f9b8700c5c02。import_selection_vs.py 保存生成原 bytes、精確提示詞、原來源 SHA 與透明範圍。S 曲線與 V 比例屬重繪近似，尚未視覺定版。
- preview_selection_screen.py 以 SELMAN、BIGFIG 及八格周界重組二十七份正常來源，完整色號／RGB 與色盤通過。公開靜態比較只使用新 VS、既有十一人 HD 肖像、灰階近似字標、向量框線及字型，不含原圖像素；八格與十一格各作一版，明列非遊戲截圖。十一格配套滑鼠區域與焦點尚未實作，現行正式介面保持。
- 首稿的紅白預留斜紋超出肖像框，屬比較工具繪圖錯誤，失敗圖保留本機；移除該段繪圖後乾淨重跑。最終 selection-screen-preview-v3 公開合圖 SHA b6dedde62247da8c3a28a93e80568f3f056d71010a9c6f5e3c6f5fe38aa77dcd；中間 v2 相同圖樣保留，不覆寫既有來源收據。
- 素材增為 118 PNG／133 catalog／137 檔、162,440,984 payload bytes；舊 131 筆素材、1516 鍵／74 圖集、正式 46 份編譯輸入及 bin 保持。README、047、現況與索引已補比較稿。029／046 原問題仍待回答，047 維持 DRAFT；未新增 Release、未把靜態候選當可操作完成。最終稽核、Docker 清理及推送另記。
- selection-screen-preview-v3/final-audit.json 通過：新增二十七份完整來源重組、VS 原生成 bytes／提示詞與兩版靜態比較，舊 131 筆素材相同。191 個 README 相對連結與工具索引通過；128 原檔、1719 執行器來源、正式 i64、46 份編譯輸入、四平台程式、首版八包及原曲影片不變。無原版圖或 raw 入 Git，UID／誤建目錄檢查通過，本專案本輪容器已清空。
- 素材與比較工具提交 `44ec0bf35687101b203bcb73a060dec8573021e1` 已推送 origin/main，遠端完整提交核對相同；首版 tag 維持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段只記錄推送結果，不將 047 升級為正式完成。


## 2026-10-21：048 結果報紙 HD 首張候選

- 上輪選角比較已推送，屬於進展。本輪回到尚未製作的結果畫面，不重複標題／背景格式提問，也不將待答分支當已確認。
- export_result_source.py 核對七個原檔，獨立由 SHIN 底圖、BIGFIG 勝者、LOSEFIG 敗者鏡像、WC 結果字、FLAG／FLAG.FIG 色盤與 NAME 姓名重組既有正常斬勝法蘭克結果，完整 64000 像素 RGB 相同。OVER 檔名猜測先被原圖排除，使用 BIGFIG 法蘭克會差 1164 RGB bytes，旗幟需專屬色盤，均未以猜測補洞。沒有新跑完整比賽或聲稱全角色結果驗收。
- 沿 B 畫風用內建 imagegen 產出 1586×992 報紙底圖與 1254×1254 法蘭克受傷肖像。後者以原 LOSEFIG 控制受傷身分、既有正常 HD 控制筆觸；兩張原 PNG 均保留。import_result_candidates.py 保存完整提示詞、來源／原輸出雜湊，另外合成純 HD 比較。原版圖像與收據只留本機。
- 新比較已目視，明列非遊戲擷取。報紙細字是抽象印刷紋理，標題用現代繁中字型重新排字、旗幟向量重畫；法蘭克傷勢與原版不同，都是候選近似，未宣稱原文字／字形或傷勢完全忠實。其餘十人敗者未補，不以一般肖像冒充。
- 現行素材為 120 PNG／136 catalog／140 檔、167,527,365 payload bytes，舊 133 筆保持；1516 鍵／74 圖集、正式 46 份輸入與四平台 bin、首版封包保持。048 DRAFT 與工具／素材／README 索引已補，不新增正式結果 API、格式或 Release。最終稽核、Docker 清理與推送另記。
- result-candidates-v1/final-audit.json 通過：七份原檔／既有正常結果的完整 RGB、兩張生成原 bytes 與提示詞、純 HD 合圖可重生，舊 133 筆素材相同。203 個 README 相對連結、新檔索引、128 原檔、1719 執行器來源、正式 i64、46 份編譯輸入、四平台程式、首版八包及原曲影片核對通過。無原圖或 raw 入 Git，UID／誤建目錄通過；本輪專案容器已清空。
- 結果候選與工具提交 `3e1500398cd386a18a013d0a018678e98e0a485f` 已推送 origin/main，遠端完整提交核對相同；首版 tag 維持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段只記錄推送結果，048 維持 DRAFT，未建立新 Release。


## 2026-10-21：048 十一人敗者肖像候選

- 上輪結果報紙與法蘭克首稿已推送，屬於進展。本輪補其餘十人的敗者美術，沿 B 畫風及既有素材上傳授權，不改正式結果路徑或把未答問題當成定版。
- 十次內建 imagegen 分別參照該人的原 LOSEFIG 受傷肖像與既有正常 HD 身分／筆觸，各產出 1254×1254 不透明 PNG。鳳凰與蜘蛛女保留淚痕；蜘蛛女只有頭髮、臉與頸，不是先前遭拒的身體服裝或戰鬥圖重試。其餘人的表情、嘴角與輕度傷痕逐人指定，未共用一套擦傷當完成。
- import_remaining_result_portraits.py 先從固定 LOSEFIG 原 bytes 重組十一張 89×89 RGB，與原參照逐張相同，再保存十張生成原 bytes、完整提示詞、參照面板／原 RGB／偏移及輸出身分。首輪法蘭克及報紙原圖不變。法蘭克之外的角色身分由原臉部及 BIGFIG 順序交叉核對，仍標靜態強推論，不宣稱正常結果已驗十一人。
- 十一人純 HD 總覽已目視，原對照只留本機。薩爾可夫兩眼閉合、鬼丸嘴巴張幅、嵐浮腫弱化、子彈圓形頰痕及各人五官／傷勢均有近似，逐人記錄，不稱完全忠實或視覺定版。沒有新的正常比賽執行。
- 素材現為 130 PNG／147 catalog／151 檔、190,895,498 payload bytes，舊 136 筆保持。README、048、素材索引與現況表已更新。正式 1516 鍵／74 圖集、46 份編譯輸入、四平台 bin、已發布首版及本機原曲影片保持；048 維持 DRAFT，不新增正式格式或 Release。最終稽核、清理及推送另記。
- result-portraits-import-v1/final-audit.json 通過：十一張原 RGB、十張生成原 bytes／提示詞／參照面板、既有法蘭克與總覽來源；舊 136 筆素材相同。209 個 README 相對連結、工具索引、128 原檔、1719 執行器來源、正式 i64、46 份輸入、四平台程式及首版封包／原曲影片保持。無原圖或 raw 入 Git，UID／誤建目錄檢查通過，本輪專案容器已清空。
- 十人新稿與總覽提交 `708ad1705aca48999deb3670146fb5559851bfcb` 已推送 origin/main，遠端完整提交核對相同；首版 tag 維持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段只保存推送結果，048 仍為美術候選，未新增 Release。


## 2026-10-21：048 目前核心正常結果來源

- 上輪十一人敗者候選已推送，屬於進展。本輪從美術回到接入證據，以目前正式核心重跑正常雙打，沒有把待答視覺或格式問題當成同意。
- result_core_receipt.go 沿既有公開 Core 的普通雙打腳本，新增即時 display／色號／色盤、結果等待與六份穩定取樣、Return 返回，共十三份。原版輸入、角色、生命、勝者、亂數與訓練未注入修改；Go 1.24.13、指令預算 30 億，實際 1,023,750,000 步完成。
- recognize_result_source.py 從七份固定原檔匹配肖像、結果字圖、旗幟及姓名，最後整張 RGB 重組相同才接受。verify_result_lifecycle.py 通過七份完整結果、四份對戰與離戰轉場／返回拒絕、八區單 byte 篡改與長度拒絕。首份 Battle=false 的畫面仍在轉場，不能只靠對戰快照清空顯示結果 HD。
- 驗證器初版把既有 015 的 192 列 scanout 當成 200，另誤套一般矩形到原標題框線。回讀 015／046 後改用既有契約及 border helper，同一原資料重跑通過。返回原標題完整色號／字標與相位確認，沒有修改產品或放寬結果全圖相等。一次工具誤用無 Pillow 的 Python image 已分類環境錯誤，不改走主機。
- 這是目前核心新執行的正常輸入證據，不是固定 RNG 戰鬥 parity 或原生 HD 驗收；只有一組 0／4 結果，單打／其他角色與三種分類另驗。沒有新增美術，仍為 130 PNG／147 catalog／151 檔、190,895,498 payload bytes。048 維持 DRAFT，正式 46 份輸入／bin／首版保持；原生候選接入與視覺／格式閘門另續。最終稽核、清理與推送另記。
- result-core-v1/final-audit.json 通過：十三份新取樣、七份完整結果、八區及長度篡改拒絕、返回原標題重組；source-binding.json 綁定目前 46 份適配來源、Go workspace、執行器 manifest、命令及資源限制。128 原檔、1719 執行器來源、正式 i64、所有素材、四平台程式、首版封包及原曲影片保持。工具索引、既有連結、UID／誤建目錄通過，原圖／raw 只留本機；本輪專案容器已清空。
- 正常結果與來源原型提交 `2d9b823a2f9e0546e800ad29107515faa2d66d73` 已推送 origin/main，遠端完整提交核對相同；首版 tag 維持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段記錄推送結果，048 仍 DRAFT，不新增 Release。


## 2026-10-21：048 隔離原生結果候選

- 上輪正常核心結果來源已推送，屬於進展。本輪把既有候選接進正式來源的隔離副本，沒有把待答視覺／格式問題當成同意。正式 API、資料格式、46 份編譯輸入、bin、原 PNG 與 Release 保持。
- prepare_result_native_prototype.py 複製 85 份來源並記錄原 46 份輸入。23 張生成原 PNG 加兩個既有純 HD 比較中向量旗幟裁切，共 25 項，逐檔核對再載入獨立紋理。七份原檔與整張 RGB 重組始終保持，參照約 1.18 MB 只在 workplace。二進位 SHA 73a49e3fa9accdf087548a39fc2b87eef52f57dc3085101f2ca8f76bf0ae1c62，未晉升正式程式。
- 第一條 full-v1 複用一般腳本，錯把第二回合開場 round_state 非零當結束，零損血卻標 time-expiry。檢查即時狀態及分支後主動停止，保留舊程式、部分圖與 stopped.json。修正只以實際零血判 KO，並要求兩次 KO；沒有因觀測期限到而重開，也沒有改原規則。
- full-v2 與 fallback-v2 各十張，正常鍵鼠完成兩回合零血 KO、結果 HD／原貌／恢復與 Return 返回；fallback 未載候選。verify_result_native.py 通過六份完整原結果、兩份 GPU 候選／鏡像及兩組核心／呈現／設定／指派不變，原貌／回退逐點相同，恢復視區像素完全相同；返回清空結果覆繪。Pillow 只辨識身分，不當 GPU 逐點 oracle。
- 新原生結果截圖已目視並放 README，分類清楚標為隔離原型。視區全為新不透明報紙、生成肖像、向量旗幟與專案字型；原貌圖／參照／色盤只留本機。素材仍為 130 PNG／147 catalog／151 檔、190,895,498 payload bytes。只有 Linux 一組雙打、第 0 結果與兩面旗幟通過，其他角色／模式／結果／旗幟／平台及視覺／正式載入仍待完成；048 DRAFT，不新增 Release。最終稽核、容器清理及推送另記。
- result-native-prototype-v1/final-audit.json 通過：二十張正常原生擷取、六份完整原結果與兩份 GPU 身分／鏡像、切換／恢復及返回清除；參照 JSON 全組重新對原檔，25 項美術及 85 份隔離來源核對。212 個 README 相對連結與工具索引通過；128 原檔、1719 執行器來源、正式 i64、所有素材、正式 46 份輸入、四平台程式、首版封包及原曲影片保持。UID／誤建目錄通過，無原圖／原參照／raw 入 Git，本輪專案容器已清空。
- 隔離原生結果與正常操作驗證提交 `9522381b5444ee305577be290a9031851769ad80` 已推送 origin/main，遠端完整提交核對相同；首版 tag 維持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段只記錄推送結果，048 保持 DRAFT，不新增 Release。


## 2026-10-21：048 七面結果旗幟向量候選

- 上輪結果原生原型已推送，屬於進展。本輪補其餘旗幟並整理完整七面獨立向量候選，保留前輪原生兩面與全部舊 PNG，不改正式或隔離載入程式。
- 先校正接觸圖的比例探測錯誤，原圖按 65:33 重新檢視。固定來源第 1 筆有 98 白色點位，第 3 筆有五個白色圖記；保留原色與不規則位置，沒有擅改現代標準樣式。第 6 筆四組卦線按投影保留完整／中斷配置。原圖、原色盤及並列對照只留本機。
- prepare_result_flag_art.py 延伸既有向量方式，以矩形、橢圓、斜線、星形及多邊形重畫，不使用圖片模型或把原點陣放大。新增七組 SVG／1300×660 PNG，完整來源、幾何指令、輸出 SHA 與逐筆近似記錄於 result-flags-source.json。金色中央徽記為翼形近似，未還原文字或國徽細節。
- 新純 HD 總覽已目視並放 README。素材為 137 PNG／162 catalog／166 檔、191,195,578 payload bytes，舊 147 筆保持；正式 1516 鍵／74 圖集、46 份編譯輸入、四平台 bin、原生 prototype-v1、首版封包與原曲影片保持。新七面尚未接原生或正式程式，048 DRAFT；沒有新的全角色旗幟表或正常結果驗收。最終稽核、清理與推送另記。
- result-flags-art-v1/final-audit.json 通過：七份原 RGB 身分、七組 SVG／PNG／幾何重生、白色點位與卦線分段、SVG 無點陣或外部圖片，舊 147 筆素材相同。218 個 README 相對連結與新檔索引通過；128 原檔、1719 執行器來源、正式 i64、46 份輸入、四平台程式、原生結果原型、首版封包與原曲影片保持。UID／誤建目錄通過，原貌及並列圖未入 Git，本輪專案容器已清空。
- 七面向量旗幟提交 `e77d5a1b3a7f3500f756899ba4d554ac1fb93780` 已推送 origin/main，遠端完整提交核對相同；首版 tag 維持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段保存推送結果，新素材保持候選，不新增 Release。


## 2026-10-21：048 七面旗幟隔離原生取樣

- 沿既有 HD 目標接續，未把首版快捷範圍的回覆當成其他待決視覺／格式同意。首版已發布且保持，其他角色快捷仍明示限制。
- prepare_result_flag_native_prototype.py 在新 prototype-v2 複製 85 份來源，保留 parent recipe／美術與舊私有旗幟。只改副本 result_prototype.go 的清單身分、數量與旗幟上界，23 張原候選加七面新旗幟共 30 項；完整原結果辨識保持。Go 1.24.13 的 Linux SHA 為 bf8ad3f726179fcfbea0270de20eaf1042620d3769956f733067409d13588c80，未移入正式 bin。
- 五組完整素材正常雙打為斬、薩爾可夫、鳳凰、金太極、蜘蛛女對法蘭克，另有薩爾可夫未載素材。各十張、兩次真 KO、三份完整原結果、原貌／恢復及 Return 通過；五組各兩側肖像／鏡像及旗幟 GPU 身分通過，未載素材全視區保持原貌。返回另用 TITLE／SFNAME／原框線重建完整色號，不只判結果消失。
- 小丑 clown-v1 的普通拳擊實際兩次時間到，腳本只接受兩次 KO，最後於零秒、124／4 血及原勝場 2／0 拒絕。保留 failure.json、兩張擷取與原腳本，不重寫舊收據。另建 result_flag_timeout_smoke.py／verify_result_flag_timeout.py，必須實際零秒、原勝場增加及勝者生命較高；回合開場非零狀態不能成立。這是驗證腳本分類修正，不改產品、生命、勝者或判勝規則。
- 新薩爾可夫正常結果截圖已目視並加 README，視區全為新不透明報紙、肖像、七面家族新向量旗幟及專案字型。原貌、色盤、原參照與研究收據仍只在本機。素材保持 137 PNG／162 catalog／166 檔、191,195,578 bytes；正式 1516 鍵／74 圖集、46 份編譯輸入、四平台 bin、首版八包與原曲影片保持。048 仍 DRAFT，視覺／正式載入、其他結果／角色／模式／平台另驗；小丑新執行、最終稽核及推送另記。
- clown-v2 正常兩次時間到、完整結果與 Return 通過，旗幟來源為第 5 筆。新驗證報告沿用的 two-KO 限制文字已修正，首份報告另存，對同批擷取重跑通過。全輪共七組／70 張、21 份完整原結果、12 份 GPU 肖像／方向及 12 份旗幟身分，來源聯集為 0..6；敗者僅法蘭克、WC 僅第 0 筆，不外推全部角色或模式。
- result-native-prototype-v2/final-audit.json 通過：新 30 項美術、85 份副本、首版原型／參照不變，timeout 腳本差異可重建，失敗收據保持。246 個 README／素材索引／048 相對連結與新工具索引通過；128 原檔、1719 執行器來源、正式 i64、166 素材、46 份輸入、四平台 bin、首版封包及本機原曲影片保持。UID／root-owned／誤建目錄檢查通過，本輪容器已清空；不新增 Release。
- 七面旗幟正常原生取樣及截圖提交 `f4d7edc1c29ce9a8d2709c3098dc7814b36489e5` 已推送 origin/main，遠端完整提交核對相同。首次串接命令的推送遇 DNS 失敗，獨立 git push 成功，未改憑證或搬入容器。首版 tag 仍為 `807579d01c145db327050c2e870e2bf46e6bcb68`；本段僅記錄推送結果，048 保持 DRAFT。


## 2026-10-21：048 十一人結果肖像正常取樣

- 上輪七面旗幟已推送，屬於進展。本輪補其餘十名敗者，並配對尚未實跑的五種勝者；沒有將普通繼續當成外觀或附加包定案。新增雙方角色操作及獨立核對工具，保留既有腳本／收據，原型二進位及正式來源保持。
- result-portraits-native-v1 十組普通雙打為 4／0、2／1、5／2、6／3、10／5、0／6、0／7、0／8、0／9、0／10。全部兩次真 KO，共 100 張、30 份完整原結果、20 份 GPU 肖像／方向及 20 份旗幟身分，切換、恢復與完整原標題返回通過。連同前輪，十一種勝者與敗者身分皆有正常原生取樣；WC 僅第 0 筆、第一人獲勝，不外推全部組合或模式。
- 初版準備工具對同名字串的出現次數判斷錯誤，總覽工具另漏了相對路徑正規化；依實際來源修正，生成及同批擷取重跑通過，沒有重跑遊戲來挑成功結果。進度訊息一度錯配索引 2／5／6 的角色名稱，已按來源清單更正為子彈／鬼丸／嵐；實際選角、比對及收據始終使用原索引。
- preview_result_native_portraits.py 只裁已核對的實際右側 HD 肖像，十一人總覽已目視並加入 README／素材索引，沒有混入原貌或放大原圖。048 舊靜態強推論增加回鏈與固定偏移的正常證據表，原 PNG、來源 JSON 及素材數量保持。正式結果外觀與獨立附加包選擇已送出，等待答覆；正式 46 份輸入、bin、首版與本機原曲影片保持，048 仍 DRAFT。最終稽核、清理與推送另記。
- result-portraits-native-v1/final-audit.json 通過：十組新收據、十一種勝者／敗者聯集、總覽每格實際像素／來源、舊分級回鏈與原檔偏移表、工具差異重生均核對。前輪七面旗幟及其失敗收據保持；128 原檔、1719 執行器來源、正式 i64、166 素材、46 份編譯輸入、四平台程式、首版八包及本機影片保持。文件相對連結與新工具索引、UID／root-owned／誤建目錄檢查通過，本輪容器已清空；不新增 Release。
- 正常十一人結果取樣及總覽提交 `0485a8c0024d6f412ad31269b1af9d46b126c60d` 已推送 origin/main，遠端完整提交核對相同；254 個相對連結通過。首版 tag 保持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段只記錄交付，外觀／附加包問題仍待答，048 DRAFT。


## 2026-10-21：048 三類結果與第二人勝方修正

- 上輪十一人來源已推送，屬於進展。本輪沿未答外觀問題獨立補技術證據；正常 1、0、0 與 0、1、0 勝序分別取得原 WC 第 1／2 筆，各十三張及完整原來源、切換／恢復與返回核對通過。結果分類未指定或寫入。
- 第二人連勝首輪未捕獲結果，後來進入原示範對戰；保存 stdout、stopped.json 後主動停止，退出 143，沒有把觀測期限當成程序停止。曾查 Enter 延續可能，未據此修原版或輸入。IDA 9.4 窄查結果呼叫與資產角色，從原函式確認玩家位置不交換，而正常／敗者檔案互換；原 v2 識別器少了左敗／右勝分支。最早的檔名及靜態 DS 導覽未當消費證據；檔案／計時 helper 不再深挖。
- 新 prepare_result_sides_native_prototype.py 在 prototype-v3 複製 85 份來源，僅改 result_prototype.go；原參照各側 22 組、1,880,378 bytes 只留本機，30 項美術保持。Linux SHA 8b2d68d08fcb2597ab2d66dbefda51e2e1ff1b2f6c97900afbccedbcf8c29ad1，Go 1.24.13；新 typed winner_player 是研究資料，正式 API／格式／46 份編譯輸入未改。
- 新 v3 第一人回歸、第二人完整及未載素材各十張，皆正常完成結果與 Return；兩個 P2 案例都是原版兩次時間到。完整原來源、左敗者／右正常肖像及方向、旗幟、切換／恢復與返回通過。舊識別器對相同 P2 原 RGB 拒絕，新版完整接受；首輪原因解讀以追加 correction.json 更正，舊資料不重寫。攻擊鍵、等待及原規則保持。
- 全輪五組接受的取樣共 56 張、15 份完整原結果、8 份肖像／方向與 8 份旗幟身分；篡改／長度／非法角色組合拒絕為 120／30／15。三種標題總覽及第二人實際原生圖已目視，原貌與原色盤仍不公開。原 PNG、素材數量、正式 bin、首版封包及原曲影片保持；外觀／附加包選擇仍待答，048 DRAFT。最終稽核、清理及推送另記。
- result-variants-native-v1/final-audit.json 通過：五組收據、兩版二進位／來源身分、雙側參照的原 bytes 重生、舊資產清單保持、IDA 原位置／bytes、拒絕測試與首輪停止資料／追加勘誤均核對。267 個 README／素材索引／048 連結及新工具索引通過；128 原檔、1719 執行器來源、正式 i64、166 素材、46 份輸入、四平台程式、首版八包及原曲影片保持。UID／root-owned／誤建目錄通過，全部本輪容器已清空；未新增 Release。
- 雙側結果修正及三類取樣提交 `0be5b3f8a382de08b81a5f5d42adf57543ea5355` 已推送 origin/main，遠端完整提交核對相同；首版 tag 維持 `807579d01c145db327050c2e870e2bf46e6bcb68`。本段只記錄交付，正式外觀／附加包問題仍待答，048 DRAFT。
