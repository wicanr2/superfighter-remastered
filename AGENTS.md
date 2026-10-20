# 快打至尊 Remastered

## 工作目錄與遠端

- 唯一開發工作樹為 `/home/anr2/cht/快打至尊/superfighter-remastered`。Git 命令、程式編輯與 Docker 的 `/project` 掛載皆使用此目錄。
- 遠端為 `https://github.com/wicanr2/superfighter-remastered.git`，目前使用 `main` 追蹤 `origin/main`。原 `/tmp/kdzz-superfighter-publish` 已移入，不再同步兩份來源。
- `workplace/`、`快打至尊.jsdos` 及 `go.work` 已隨工作樹移入，繼續由 `.gitignore` 排除。父目錄的同名連結只維持歷史路徑；父目錄程式與文件是搬移前快照，不作新修改。
- 遠端與搬移現況見 [CONTEXT.md](CONTEXT.md)，過程見 [WORKLOG.md](WORKLOG.md)。歷史收據保留原日期與雜湊，不隨路徑搬移重寫。

## 每次開工

1. 先讀 [CONTEXT.md](CONTEXT.md) 的唯一現況表，再讀 [WORKLIST.md](WORKLIST.md)。以目前程式與最近實跑收據判斷進度。
2. 查 `/home/anr2/.codex/knowledge-base/knowledge-router.md`，說明命中列與實際載入的入口。只載入本次任務需要的文件。
3. 遵守使用者提供的共用主機衛生規則。回覆與新文件用繁體中文，句子簡短、直接。
4. 既有完成項不因歷史筆記重新開啟。區分「本專案已完成」、「原版證據未知」與「可選美化」。

## 已確認目標與架構

使用者於 2026-10-19 指定：參考 `/home/anr2/cht/zeliard`，以 dosgolem 包裹《快打至尊》原版核心，支援手把操作，並規劃 HD。

- 原版執行檔負責遊戲規則、角色狀態、碰撞、攻擊判定、AI 與流程。
- dosgolem 負責執行 DOS 程式、機器服務、觀測與可重播輸入。
- 本專案負責啟動適配、桌面呈現、手把映射、設定與 HD 合成。
- 玩家入口固定為 Windows、macOS、Linux 原生桌面程式。使用者已排除 web；HTTP／HTML 只留作研究工具，不作主入口或三平台成品。
- 原貌是行為與畫面的基準；HD 是獨立呈現層。
- 不另建一套玩法引擎，不用推測規則替代原版。dosgolem 缺能力時，記錄缺口並補足通用服務。

架構已定，不重複詢問是否改用 dosgolem。使用者於 2026-10-19 選定 HD 的 B「街機手繪」方向，原圖及雜湊見 [規格 003](docs/spec/003-hd-design.md)。這次只確認畫風，概念稿已列出的造型偏差仍需依原版修正。首批屋頂、斬、法蘭克與對戰介面已獲使用者授權開工；正式倍率、預設模式與公開方式尚未定案；平台固定 Windows、macOS、Linux。不得把 zeliard 的選項當成本作決定。

## 參考來源與界線

| 來源 | 用途 | 不可直接沿用 |
|---|---|---|
| `/home/anr2/cht/zeliard/AGENTS.md` | dosgolem 包裹、原貌與 HD 分離、手把需求、證據與驗收流程 | 該作位址、按鍵、畫布、手繪奇幻畫風、中文化與遠端儲存庫授權 |
| `/home/anr2/cht/dosgolem/README.md`、`CLAUDE.md` | 既有能力、Docker 工具鏈、Go workspace 接入與分層 | 已支援《快打至尊》全遊戲的假定 |
| `/home/anr2/cht/dosgolem/docs/spec/000-index.md` | dosgolem 規格入口；首次接入先讀，再選所需規格 | 僅憑規格存在宣稱本作可執行 |
| `/home/anr2/.codex/knowledge-base/local/retro-remake-end-to-end-playbook.md` | 垂直切片、完成狀態、正常玩家路徑與停止線 | 其他作品的完成門檻與已驗證狀態 |
| `https://chiuinan.github.io/game/game/intro/ch/c51/sf.htm` | 使用者指定的操作、招式與圖片參考；本機快照見 `workplace/manual-reference/source.json` | 網頁自述 v1.1，不能直接取代目前包內自述 v2.0 的輸入證據或套用其修改位元組 |

參考專案與共用 dosgolem 來源唯讀使用。需要修正共用執行器時，在本專案 `workplace/` 建立獨立工作副本，記錄來源 commit 與差異。不直接修改其他專案。

## 原始輸入與啟動鏈

- 原始包為 [快打至尊.jsdos](快打至尊.jsdos)，來源、SHA-256 與已檢查項目見 [CONTEXT.md](CONTEXT.md)。保留原始 bytes，不覆寫、不重包。
- 解包在 Docker 內進行。拒絕絕對路徑、上層跳脫、符號連結與正規化後重複路徑；保留逐檔原名、大小及 SHA-256。
- `.jsdos/dosbox.conf` 的啟動入口是 `play.bat`。`PLAY.BAT` 內容為 `nokey /y` 後執行 `sf`。
- 包內同時有 `SF.COM`、`SF.EXE` 與 `NOKEY.EXE`。先核對命令解析、子程序與輸入準備；直接跑 `SF.EXE` 只算診斷入口，未驗證前不取代正常啟動鏈。
- `AIDATA.DAT` 與 `CHEAT/AIDATA.DAT` 的內容不同。正式基準保留來源根目錄檔案，禁止自動以 `CHEAT/` 內容覆蓋。
- `FIGHT.CFG`、包內既有存檔及其他可寫資料先視為來源。執行、設定變更與測試採另外的可寫層，禁止回寫原始包。
- `README.TXT` 自述為 SUPER FIGHTER v2.0。這只證明包內文字，尚不能證明原始發行版本、未修改狀態或散布權。
- `.DAT`、`.FIG`、`.XBB` 等副檔名不證明格式。資產用途、編碼與角色對應須由 bytes、實際畫面及讀取端查證。

## dosgolem 接入

1. 依規格索引選讀 `001-scope-and-mvp.md`、`005-oracle-api.md`、`006-layering.md`。檔案均位於 `/home/anr2/cht/dosgolem/docs/spec/`；舊規格與目前程式衝突時記錄差異。
2. 在 Docker 內檢查目前 `cmd/probe` 的旗標，以固定指令與時間預算探測。先記錄入口、未實作指令、DOS／BIOS 服務、檔案存取、視訊模式、音訊與停止原因。
3. 首個垂直切片須從正常啟動到可操作選單，再走進一場對戰並正常返回。只顯示片頭或載入 EXE 不算可玩。
4. Go 接入依 dosgolem README 的 workspace 方法，使用本機來源並記錄 commit。不得填入不存在的模組版本，不從外部模組直接 import dosgolem 的 `internal/`。
5. 本作位址、載入器設定、按鍵語意、畫面辨識與 HD 資源對應留在本專案適配層。機器層不得出現《快打至尊》專屬分支。
6. 通用服務缺口依 dosgolem 自身規格處理。不得藉吞錯、跳過必要程式碼或偽造成功狀態讓畫面繼續。
7. dosgolem 是正式原版收據來源。DOSBox／DOSBox-X 僅補足與交叉驗證缺口，擷取標為輔助基準；修正後由 dosgolem 重生收據。
8. 每份收據記錄來源與雜湊、dosgolem commit 及本地差異、工具版本、初始狀態、輸入序列、預算、停止條件、輸出與限制。

## 手把操作

使用者於 2026-10-20 另授權[練習模式 032](docs/spec/032-training-mode.md)：雙方補滿並鎖滿血、停止倒數、AI 輸入中立。這是明示的可關閉規則擴充，只由 gamecore 適配層介入；HD 仍為只讀呈現。曾啟用的執行及其截圖保留 modified 標記，不當作未修改原版對拍。

先核對原版輸入，再定義動作表與預設綁定。不能因為是格鬥遊戲，就自行補上攻擊鍵數、連招或原生搖桿契約。

| 項目 | 要求與驗收 |
|---|---|
| [背景修稿收錄](tools/import_background_revisions.py)、[修稿來源與提示詞](assets/hd/candidates/background-revisions-source.json) | 保留首輪原 PNG，另存石窟／舞廳構圖修稿的原 bytes 與來源；候選狀態不視為正式接入 |
| 設定入口 | 前端提供可辨識的「手把設定」入口；可用鍵盤開啟、取消與離開，避免未綁定時無法設定 |
| 裝置 | 選擇作業系統已辨識的 USB 或藍牙手把，顯示名稱及連線狀態；藍牙配對由作業系統處理 |
| 綁定 | 方向鍵、類比軸及按鈕可綁定已證實的遊戲動作，支援重綁、取消、還原與衝突提示 |
| 輸入注入 | 依原版實際讀取方式選擇掃描碼或 DOS 搖桿介面；分開驗證按下、持續按住、放開與同時按鍵 |
| 格鬥操作 | 抽測斜方向、方向加攻擊、多鍵與快速轉向；保留輸入順序，不以單次按鍵 API 冒充連續狀態 |
| 相反方向 | 先量原版鍵盤的上下／左右同按行為；未定規格前不自行加入清除、優先序或最後輸入優先 |
| 類比軸 | 死區、方向門檻與遲滯由可撤回試作及操作驗證決定；不臆定正式數值 |
| 輸入所有權 | 手把、鍵盤與設定介面的按住狀態分開追蹤；單一來源放開不得取消另一來源仍按住的動作 |
| 設定隔離 | 重綁與前端選單攔下自己的事件，避免同時觸發遊戲動作；進出介面要釋放或明確恢復按鍵 |
| 生命週期 | 啟動後接入、斷線、重連、切換裝置與失焦不得留下卡鍵；無手把時保留鍵盤備援 |
| 設定保存 | 裝置及映射設定獨立於原版檔案；重啟後恢復，不只用當次列舉索引識別裝置 |
| 玩家模式 | 先查原版單／雙人模式與各自按鍵。若實作雙手把，須明確指派玩家並驗證兩邊輸入不串線 |

自動測試驗映射、順序、按住／放開、輸入隔離與斷線清理。實體驗收另記錄平台、型號、USB／藍牙連線方式及結果。合成事件不等於手把實測通過。

使用者於 2026-10-19 明確授權逐角色快速出招，最多四格，預設 R1／R2／L1／L2 對應絕招 1／2／3／4；有五招的角色可任選四招。兩名玩家各自保存角色配置，並規劃兩支手把雙打。詳細契約與原型限制見 [規格 002](docs/spec/002-gamepad-design.md)。快捷以原版輸入序列出招，時序、朝向及狀態條件須實測；不藉此直接改寫招式、傷害或蓄力規則。未授權的連發、任意跨招巨集、輸入寬容度與指令緩衝修改仍不加入正式路徑。

## HD 規劃與呈現契約

HD 採 B「街機手繪」方向，目前仍在規劃與試作階段。以下是查證與試作順序，尚未定案量產範圍。

| 階段 | 工作 | 進入下一階段的條件 |
|---|---|---|
| H0 原貌基準 | 正常玩家路徑擷取標題、選角、對戰與結算；量畫布、像素比例、色盤、遮擋與動畫節點 | dosgolem 可重播；來源、狀態與畫格定位可回查 |
| H1 小範圍比較稿 | 從已證實來源選一個場景，呈現原貌及候選 HD；角色與 HUD 必須可辨讀 | 提供同狀態比較與短片，由使用者選畫風、範圍、倍率與預設模式 |
| H2 動態垂直切片 | 在已確認範圍內覆繪代表角色及必要姿態，驗鏡像、透明、陰影、遮擋與特效 | 正常對戰連續播放，無殘影、漂移、錯幀及操作回饋延遲；未知姿態可安全退回 |
| H3 擴充與收尾 | 依已確認範圍逐組擴充場景、角色、介面與特效 | 每組有來源與授權記錄、缺件退回及正常玩家路徑驗證 |

- HD 素材以目標解析度直接合成。最近鄰放大、濾鏡或將高清圖縮回原尺寸都不能單獨宣稱完成 HD 美術。
- 保留原始畫面擷取路徑；呈現層不寫回原版視訊記憶體或遊戲狀態。
- 先取得可信的繪製事件、來源鍵、角色姿態與完整畫格，再決定覆繪。單張畫面相似不足以識別整段動畫。
- 每組素材記錄來源檔及偏移或事件、雜湊、尺寸、錨點、鏡像、透明、遮擋與權利分類。未驗證的索引與尺寸不得進正式呈現。
- 缺件、損壞、來源不符或未知姿態時，按規格退回完整一致的原貌單位。切換先驗證整組資產，不能出現載入一半的角色或畫面。
- 原版角色座標、碰撞與攻擊判定保持原版狀態。HD 不另推導命中框，不自行延長動畫、補幀或修改速度。
- 切換原貌／HD 不重開局、不重擲亂數、不改寫原版設定或存檔。
- 工具列與設定介面不得遮擋計時、生命、角色或操作資訊。Esc、Start 等按鍵先查原版用途；前端暫停、模擬暫停與原版暫停分別定義。
- 畫風與操作取捨先用可丟棄比較稿或短片確認。使用者定版後保存原稿與決定，實作對照相同狀態；不得自行改構圖與比例。
- 音樂、音效重製與新增中文化不在本輪預設範圍。先盤點現有語言與音訊，不套用 zeliard 的翻譯需求。

## 證據與規格閘門

正式流程：原版證據 → DRAFT 規格 → 證據審查 → READY → 實作 → 同狀態驗證 → CONFORMED。

- 使用「已證實、強推論、假說、未知」四級。可執行、可解碼與單元測試通過不能自行升級原版語意。
- 原始 bytes、函式名、位址空間、偏移及運算元保持可回查。推測語意用分級註解與外部索引附加。
- 只追查目前玩家阻塞點需要的最小充分證據。無關 helper、驅動程式與完整 executable 翻譯不列為完成目標。
- 需要反組譯時讀 `/home/anr2/.codex/skills/use-ida-pro-9-4/SKILL.md` 及 `/home/anr2/ida_94_official/knowledge-base/ida-94-tools.md`，沿用 IDA Pro 9.4 工具鏈。本專案已驗 `ida-pro-9.4-idapython:py312-v1` 的 UID 1000 與 UTF-8 JSON 匯出；不因其他 tag 較新就換 image。`.i64` 的交叉參照與資料流為主，攤平 `.asm` 只作線索。
- 硬體時序先讀 `/home/anr2/.codex/knowledge-base/local/retro-platform-spec-first.md`。DAC、PIT 與音訊時鐘採已知平台契約，規格近似明確標示，不追求未授權的逐週期考古。
- 亂數測試執行前固定種子或受控條件，記錄方法。不重擲挑結果，不把測試條件永久鎖入正式遊戲。
- 修改架構、資料格式、原版忠實度、操作體驗或公開方式前，依 `/home/anr2/.codex/skills/grilling/SKILL.md` 先查證、展示取捨並取得決定。已確認的 dosgolem 架構不再重問。

## 驗收與停止線

| 範圍 | 最小必要證據 |
|---|---|
| 原版核心 | 正常啟動、選單、選角、一場對戰、結果與返回；記錄未走過模式 |
| 手把 | 正常選單與對戰、連續輸入、多鍵、斷線與重連；單元測試及實體測試分開列 |
| HD | 同狀態原貌／HD 截圖、連續動畫、原版狀態不變、缺件與未知畫格退回 |
| 設定與持久化 | 前端設定重啟恢復，原始資料雜湊不變；原版若有存檔功能再驗正常存讀，不臆造存檔介面 |
| 音訊與效能 | 對戰實際播音與人耳抽聽，輸入到畫面回饋、呈現積壓與模擬時間推進；不能只驗片頭 |

測試從正常入口進入，不以 direct-entry、座標注入、無敵、強制勝利或來源包的作弊資料替代。HD 比較分開驗「原版狀態不變」與「呈現符合定版」，不要求美化畫面逐像素等於原貌。

一場對戰只證明該切片，不能宣稱所有角色、雙人模式、全流程或可通關。完成聲明限於目前實測範圍。

## Docker 與主機衛生

- 分析、搜尋、解包、建置、測試、GUI、音訊與遊戲執行都在 Docker。主機只做必要的 Docker、Git、工作樹檢查及檔案編輯。
- 盤點可沿用 `python:3.13.7-slim`。Go／GUI 工具鏈先查 `/home/anr2/cht/dosgolem/tools/docker/go-ebiten.Dockerfile` 與既有 `dosgolem-go-ebiten:1.24-r1` 的適用性；缺件才修正可重現建置來源。
- 一次性容器用 `--rm`、資源限制與有界執行。預設 `--network none`，只有下載與取依賴開網路。
- 每個掛載先查來源存在、類型及 UID/GID。原始資料與參考專案唯讀；只掛明確輸出可寫，可寫容器指定目前使用者 UID/GID。
- 研究與中間產物放根目錄 `workplace/`。建立前讀 `/home/anr2/.codex/knowledge-base/local/project-document-responsibilities.md`；不另建同義工作區。
- Xvfb 等背景程序有 trap 與有界擁有程序。每批工作後檢查本專案容器、root-owned 檔案及誤建的 `*.md` 目錄，只清理本專案資源。
- 環境失敗與產品缺陷分開記錄。修正環境後以同一容器、同一命令乾淨重跑，不回到主機執行。

## 文件索引

| 已建立檔案 | 唯一職責 |
|---|---|
| [其餘特殊技素材收錄](tools/import_remaining_effect_assets.py) | 既有 1495 鍵及 PNG 保持，核對六 PNG 原 bytes、21 個鍵及 catalog；來源與原貌收據不公開 |
| [其餘特殊技原生操作](tools/remaining_effects_smoke.py)、[獨立核對](tools/verify_remaining_effects_native.py) | 四人普通方向／拳腳觸發新光效族，驗完整 CPU／HUD／陰影／CRTC、原貌切換與舊包回退 |
| [其餘特殊技真實測試](internal/hd/remaining_effects_test.go) | 四人二十一份原始來源、既有選擇不退步、未知來源／色盤與超量清單拒絕，鳳凰未驗色盤保持回退 |
| [其餘特殊技素材準備](tools/prepare_remaining_special_effects.py) | 先計算二十一鍵與六 PNG 的來源／資源；READY 後沿既有格式加入，保持所有舊圖與姿態 |
| [特殊技候選匯入](tools/import_special_effect_art.py) | 無損保存內建生成 PNG，檢查透明色與既有登錄分隔，失敗稿只留本機，不接正式素材 |
| [特殊技光效參考準備](tools/prepare_special_effect_references.py) | 從已驗原檔及 CPU 證據產生二十一鍵私有參考、五份精確生成請求；不修改正式圖集 |
| [其餘特殊技光效](docs/spec/044-remaining-special-effects.md) | 五人普通輸入稽核、四人二十一個第二色盤缺件與素材審查；鳳凰主圖像色盤拒絕另列，不由補圖猜補 |
| [主色盤原生操作](tools/primary_extra_smoke.py)、[獨立核對](tools/verify_primary_extra_native.py) | 鬼丸正常蓄力後武器的 HD／原貌切換、舊程式整格回退及恢復操作；不代表其他額外圖像全驗 |
| [主色盤成對核心](tools/primary_extra_core_receipt.go)、[真實來源測試](internal/hd/primary_extra_test.go) | 觀測開關不改原版狀態、兩側及同角色盤來源與 CPU 遮罩／色號篡改拒絕 |
| [主色盤原呼叫](tools/ida_primary_extra_evidence.py) | 由唯讀正式資料庫複本匯出兩側額外圖像的原始函式、位址、bytes 與引用，不覆寫命名 |
| [主色盤額外圖像獨立核對](tools/verify_primary_extra.py) | 原始來源指標表、第一色盤、四次 blit／完整 RAM 重組及既有 HD 剪影；來源與額外圖像角色分開 |
| [主色盤額外繪圖](docs/spec/043-primary-palette-extra-sprites.md)、[原始 blit 探針](tools/primary_extra_draw_receipt.go) | 鬼丸 path 38 額外圖像的來源指標、實際色盤及 CPU 寫入審查；未達 READY 不放寬分層／呈現 |
| [金太極光效圖](assets/hd/characters/kim-effects.png)、[來源與精確提示詞](assets/hd/characters/kim-effects-source.json) | 十種第二色盤生成原圖與透明矩形；原始 bytes／色盤／原圖留本機 |
| [金太極光效原生獨立核對](tools/verify_kim_effects.py) | 三類實際原生光效、完整 CPU／HUD／陰影／CRTC、第二色盤、可見替換及模式恢復；不外推十種 GPU 動畫全驗 |
| [金太極原生光效](tools/kim_effects_smoke.py) | 正常鍵盤方向／拳腳觸發金黃彈、青藍刀光與拳影，驗同狀態切換／恢復及舊包回退；不使用快捷或狀態注入 |
| [金太極光效真實測試](internal/hd/kim_effects_test.go) | 十份正常第二色盤 fixture、新群組選擇及來源／未知色盤整格拒絕；不以來源鍵齊全代替動畫驗收 |
| [金太極光效準備](tools/prepare_kim_effects.py) | 綁定 READY 來源與原 PNG，新增十個第二色盤鍵、保留舊素材及清單，核對實際圖集與清單上限 |
| [特殊光效獨立核對](tools/verify_special_effects.py)、[金太極特殊光效](docs/spec/042-kim-effects.md) | 正常序列、全部保存 CPU 層與十份第二色盤原圖，先審查再接既有格式；鬼丸快照缺口另記 |
| [特殊動作來源診斷](tools/special_effects_receipt.go) | 以明示的普通鍵盤序列、正常選角取樣光效與 HD 缺件；不接快捷、不注入狀態，沿 009 的原圖層及第二色盤契約 |
| [背景捲動正常來源](tools/background_scroll_receipt.go)、[私有比較稿](tools/background_scroll_preview.py) | 十一景正常雙打的雙人行走、相機邊界與完整 CPU 圖層；只作捲動／構圖比較，029 格式確認前不接 production |
| [同角色原生色彩核對](tools/verify_duplicate_palette_native.py) | 真實主色盤、原圖層／HUD／陰影／CRTC、藍綠雙色及切換／勝利生命週期，與 HD 配色近似分級 |
| [同角色原生操作](tools/duplicate_palette_smoke.py) | 正常同角法蘭克雙色、第二人行走／放開、同狀態原貌切換與舊程式回退；不改原版狀態 |
| [同角色配色真實測試](internal/hd/duplicate_palette_test.go) | 二十二份正常 fixture、缺稿回退、兩人／異角隔離、來源拒絕及色盤錨點／alpha 保持 |
| [同角色 HD 配色](internal/hd/duplicate_palette.go) | 固定 MAN.COL 原版身分與不可變配色視圖；只在受驗同角第二人主色盤呈現，保留原圖及 alpha |
| [同角色 HD 色彩比較](tools/duplicate_palette_preview.go) | 原稿不變的可丟棄 RGB 色彩轉移呈現，並列原版兩色與 HD；不接正式呈現或假稱逐像素 |
| [同角色色盤獨立核對](tools/verify_duplicate_palettes.py) | 原 DAT／MAN.COL、二十二份正常畫格、四十四份角色層與十一個背景來源，與 HD 呈現證據分開 |
| [同角色正常色盤取樣](tools/duplicate_palette_receipt.go) | 十一人正常雙打同角、兩側待機與行走的原檔色盤及 CPU 層；只讀診斷，不接 HD |
| [同角色替代色盤](docs/spec/041-duplicate-palettes.md)、[原始載入引用](tools/ida_duplicate_palette_evidence.py) | 同角色色盤檔名、原載入端、正常雙打色盤與 HD 比較閘門；不只移除色盤核對 |
| [原生場邊獨立核對](tools/verify_edge_native.py) | 新舊原生畫格的 CPU 來源、完整重組、實際 HD 替換、同狀態切換與恢復後操作 |
| [正常場邊投擲](tools/edge_clipping_smoke.py) | 十七階段普通鍵鼠輸入、場邊 C0h 裁切、暫停切換與恢復後操作；輸入互斥且程序有界 |
| [場邊裁切真實測試](internal/hd/edge_clipping_test.go) | 四份正常場邊 CPU fixture、已知完整群組選擇及壞遮罩拒絕；蜘蛛女未知本體不冒稱完整 HD |
| [場邊裁切獨立審查](tools/verify_edge_clipping.py) | 原 i64 bytes 與四份正常 CPU 層，核對雙向翻轉來源起點及完整影像定位，保留舊錯位量與證據 |
| [雙向翻轉場邊裁切](docs/spec/040-mirrored-edge-clipping.md)、[原始 blit 證據](tools/ida_edge_clip_evidence.py) | 原 i64 的來源位移差異、正常 CPU 層重組與既有 HD 定位修正閘門，保留所有原始名稱 |
| [鳳凰光效原生獨立核對](tools/verify_phoenix_effects.py) | 原檔 CPU 光效、完整原貌／HUD／陰影／CRTC、同狀態切換、實際替換及缺件整格原貌 |
| [鳳凰光效真實測試](internal/hd/phoenix_effects_test.go) | 完整素材與正常 CPU fixture 的光效選擇，以及未知槽、壞來源、錯色盤整格拒絕 |
| [鳳凰光效原生路徑](tools/phoenix_effects_smoke.py) | 普通選角、移動、拳腳兩光效、同狀態原貌／HD／恢復與舊包整格回退；程序有界且收尾清理 |
| [鳳凰光效登錄](tools/prepare_phoenix_effects.py) | READY 審查後以既有第二色盤鍵加入兩光效，核對原 bytes、全部舊鍵及現行資源上限 |
| [動作取樣獨立核對](tools/verify_hd_motion_coverage.py) | 原檔姿態身分、實際缺件鍵、保存 CPU 圖層與鳳凰光效色盤／覆蓋；不把 selector 診斷當 GPU 或全動畫證據 |
| [鳳凰普通光效](docs/spec/039-phoenix-effects.md) | 正常動作發現的第二色盤 58／60 光效、原檔及 CPU 圖層審查、既有格式接入閘門 |
| [正常動作 HD 取樣](tools/hd_motion_coverage.go) | 十一人普通選角、移動／蹲／跳／拳腳的實際素材選擇及回退原因；只讀診斷，不當作全部動畫或原生 GUI 驗收 |
| [角色翻轉與裁切](docs/spec/038-character-geometry.md)、[原版幾何審查](tools/verify_character_geometry.py) | 正常擊倒的雙向翻轉／頂部裁切、原檔與 CPU 逐點覆蓋、既有 HD 定位及接入閘門 |
| [角色幾何核對](internal/hd/geometry.go) | 原檔私有切片與同格 CPU 遮罩／色號的逐點核對；只擴充已證實定位，不改畫稿或資料格式 |
| [角色幾何測試](internal/hd/geometry_test.go) | 真實 C0h／TopClip 9 的完整素材選擇，以及像素、覆蓋、位置與裁切篡改拒絕；空裁切不外推正常玩家樣本 |
| [原生角色幾何](tools/character_geometry_smoke.py) | 正常選角與拳擊擊倒期間捕捉新幾何，原貌／HD 同狀態切換，再繼續正常首勝及下一回合 |
| [原生幾何獨立核對](tools/verify_native_character_geometry.py) | 原始角色像素、實際新幾何、同狀態模式切換及恢復後正常下一回合，不外推全動畫 |
| [嵐的勝利 HD](docs/spec/037-lan-victory.md) | 已驗一般來源重用、四格新稿、獨立 WIN 群組、LAN WIN 姓名及正常首勝接入閘門 |
| [嵐的 WIN 登錄](tools/prepare_lan_victory.py) | 固定來源及原 PNG、兩組既有姿態重用、四組新稿、七十二入口及舊群組保持 |
| [嵐的 WIN 測試](internal/hd/lan_victory_test.go) | 真實七十二入口、六組來源、一般／WIN 同 bytes 重用、原版姓名矩形及篡改拒絕 |
| [其餘九景整理](tools/organize_background_candidates.py)、[候選來源](assets/hd/candidates/backgrounds-source.json) | 九景生成原 PNG、精確提示詞、原版來源 SHA 與未接入狀態；不修改 029 待確認格式 |
| [場景正常來源盤點](tools/stage_source_receipt.go) | 原 XGB 嚴格解碼、正常雙打選角、背景 RAM／色盤／camera crop 的來源證據；只讀診斷，不新增正式素材格式 |
| [十一景獨立核對](tools/verify_stage_sources.py) | 直接以原檔重組二十二份正常待機／移動來源，核對場景、色盤、背景 RAM 與捲動裁切；不當作新背景 HD 已接入 |
| [Release 發布](tools/publish_release.py) | 核對封包／操作／本機影片收據，只上傳四個 patch 引擎包與公開 manifest；先驗草稿資產大小及 SHA-256，才發布，不覆寫已發行版本 |
| [本機推廣片](tools/promo_release.py) | 原生封包錄影、靜態畫面標示、原版 MIDI 配樂、字幕邊界與音畫檢查；成品與來源只留 dist-all 的本機 promo |
| [鍵盤組態](docs/spec/035-keyboard-bindings.md)、[三平台發行](docs/spec/036-release-packages.md) | 使用者指定的鍵盤與四格出招、公開無原版包／本機完整包、私有原曲推廣片與驗收範圍 |
| [鍵盤資料](internal/controls/keyboard.go)、[鍵盤介面](internal/desktop/keyboard.go)、[設定測試](internal/controls/keyboard_test.go) | 兩人十四欄、衝突／保留鍵、原版輸出及中立閘門 |
| [資料匯入](internal/gamefiles/import.go)、[原檔身分](internal/gamefiles/source-manifest.json)、[匯入測試](internal/gamefiles/import_test.go)、[VERSION](VERSION) | 公開包不含原版 bytes；合法來源驗證、全新目錄原子匯入及使用者端屋頂參考準備 |
| [音樂與語音 HD 評估](docs/audio-hd-assessment.md)、[原音訊盤點](tools/inspect_original_audio.py) | 原版 MIDI 與 Compact PCM 證據、HD 可行性、未知格式及本機影片音訊來源界線 |
| [三平台封包工具](tools/package_release.py) | 收集實際依賴授權、四平台公開包與本機完整包、固定版號、逐檔 SHA 及原版資料排除檢查 |
| [鍵盤正常路徑](tools/keyboard_smoke.py)、[封包啟動](tools/package_startup_smoke.py)、[封包操作與錄影](tools/package_smoke.py) | Linux／Wine 重綁及原版出招、公開包匯入／自動 HD 參考、實際封包正常雙打、失焦中立與私有錄影 |
| [蜘蛛女低伏接入](docs/spec/034-spider-low-guard.md)、[準備工具](tools/prepare_spider_low_guard.py) | 已確認的相近低伏稿、三組一般來源與別名、朝向正規化、原姓名及未覆蓋動作回退 |
| [蜘蛛女原生驗證](tools/spider_low_guard_smoke.py)、[獨立核對](tools/verify_spider_low_guard.py)、[來源測試](internal/hd/spider_low_guard_test.go) | 普通雙打低伏、移動原貌回退、釋放恢復、同狀態切換與原字圖／圖層重組 |
| [首輪其餘勝利 HD](docs/spec/033-first-pass-victories.md) | 金太極、小丑、印第安喬的 WIN 擴充；嵐／蜘蛛女卡點先跳過，道場候選另整理，依證據閘門接入 |
| [首輪勝利來源驗證](internal/hd/first_pass_victory_test.go) | 舊包保持、三人 216 個 WIN 鍵、原版真實姓名與損壞來源拒絕；使用 KDZZ_HD_FIXTURES 與 KDZZ_ORIGINAL_ROOT 提供本機資料 |
| [蜘蛛女原圖交接工具](tools/export_spider_reference.py) | 在本機 workplace 輸出原版 PNG、提示詞與可驗 SHA-256 ZIP，不公開原版參考圖 |
| [蜘蛛女逐格補稿工具](tools/export_spider_corrections.py) | 首批十張缺少或姿勢需修正的 PNG、單格提示詞與外部造型參考；核對一般／WIN 同 bytes 別名，本機原圖包不上傳 |
| [棋盤背景去除工具](tools/remove_sprite_checkerboard.py) | 使用者明確授權 Python 後，在 Docker 的 Pillow 工具鏈執行；只改連通淺灰背景的 alpha，另存 PNG 與 ZIP，保留原 RGB、尺寸及原檔。外部圖的姿勢對應另驗 |
| [蜘蛛女候選收錄工具](tools/import_spider_candidates.py)、[候選圖索引](assets/hd/candidates/spider/README.md) | 在 Docker 內核對兩批外部 PNG、去背來源與雜湊並收錄 repo；檔名不是已驗證的動作對照，正式角色包另依接入規格驗收 |
| [候選素材索引](assets/hd/candidates/README.md)、[道場整理工具](tools/organize_dojo_candidate.py) | 道場原生成 PNG、來源與提示詞分開保存；清楚標示候選及尚未接入 |
| [練習模式規格](docs/spec/032-training-mode.md) | 使用者指定的雙方鎖血、停止倒數與 AI 中立；獨立於原版／HD 對拍，依規格閘門接入 |
| [練習適配](internal/gamecore/training.go)、[正常路徑與拒絕邊界](internal/gamecore/training_test.go)、[原生開關驗證](tools/training_smoke.py) | 固定原檔與控制點、雙模式鎖血／停時／AI 中立、原生工具列及 F9、重啟與命令列 |
| [README.md](README.md) | 穩定用途、本機建置與操作入口、現況摘要 |
| [LICENSE](LICENSE) | 自有程式與文件的 RRSAL-1.0 完整條款，排除原版資料及第三方內容 |
| [go.work.example](go.work.example) | 新工作樹的本機 dosgolem 相對目錄範本 |
| [手把設定截圖](docs/screenshots/gamepad-settings.png)、[來源](docs/screenshots/source.json) | 可隨原始碼保存的自有設定介面，未含原版遊戲畫面 |
| [docs/spec/005-native-desktop.md](docs/spec/005-native-desktop.md) | 三平台原生桌面、設定與輸入適配契約，限定 READY |
| [go.mod](go.mod)、[go.sum](go.sum)、[go.work](go.work) | 固定依賴與本機 dosgolem workspace，不虛構公開模組版本 |
| [cmd/superfighter/main.go](cmd/superfighter/main.go) | Windows／macOS／Linux 原生桌面入口，不啟動 HTTP |
| [internal/gamecore/core.go](internal/gamecore/core.go) | public oracle 原版核心、逐來源輸入與已驗快捷適配 |
| [internal/gamecore/presentation.go](internal/gamecore/presentation.go) | 原版完整畫格的只讀背景、色盤、相機與姿態快照 |
| [internal/gamecore/hud.go](internal/gamecore/hud.go)、[介面快照](internal/renderdata/hud.go) | 原介面建立時鎖存勝場，記錄本次 bitmap 與介面之前的原貌層，不寫入原版狀態 |
| [internal/gamecore/layers.go](internal/gamecore/layers.go)、[internal/renderdata/layers.go](internal/renderdata/layers.go) | 原版每次 RAM 寫入、完整圖層快照、鏡像定位與重組契約 |
| [internal/hd/background.go](internal/hd/background.go)、[背景驗證](internal/hd/background_test.go) | 固定屋頂素材群組、完整原貌前景、同畫格背景合成與安全回退 |
| [internal/hd/characters.go](internal/hd/characters.go)、[tools/prepare_hd_characters.py](tools/prepare_hd_characters.py) | 原生角色素材來源、packed bytes、圖集、透明矩形與整組回退 |
| [internal/hd/hud.go](internal/hd/hud.go) | 固定原檔建立介面期望 bitmap，核對原版顯示數值、色盤、透明性與最後覆蓋；不推導玩法 |
| [介面來源驗證](internal/hd/hud_test.go) | 33 個原版 fixture、待扣傷害、顯示勝場鎖存及來源／欄位／色盤損壞拒絕 |
| [internal/controls/settings.go](internal/controls/settings.go)、[設定驗證](internal/controls/settings_test.go) | 兩人逐角色四格配置、第五招、原子保存及錯誤資料保留 |
| [internal/desktop/game.go](internal/desktop/game.go) | Ebitengine 視窗、原生鍵鼠／標準手把、設定與有界中文文字 |
| [Windows 按鍵適配](internal/desktop/keyboard_windows.go)、[其他平台](internal/desktop/keyboard_other.go) | 以個別 Win32 VK 保留左右 Shift 的獨立按住狀態，其他平台沿用 Ebitengine |
| [internal/desktop/characters.go](internal/desktop/characters.go) | 原生 GPU 依原版順序畫高解析角色、特效與介面，保留其他原貌寫入 |
| [internal/desktop/hud.go](internal/desktop/hud.go) | 量實際字圖與描邊邊界，以獨立紋理畫生命、計時、名字及玩家標記；原勝場圖示保留 |
| [角色素材驗證](internal/hd/characters_test.go)、[圖層定位驗證](internal/renderdata/layers_test.go) | 原始 fixture、素材拒絕、完整重組與鏡像／裁切的獨立驗證 |
| [一般角色擷取核對](tools/verify_sarkov_capture.py) | 薩爾可夫預設角色 1；子彈指定 --player0 2；鳳凰指定 --player0 3；鬼丸指定 --player0 5；嵐指定 --player0 6；金太極指定 --player0 7。九張正常原生擷取的來源重組、人物／姓名替換、切換與缺件整格回退 |
| [薩爾可夫勝利規格](docs/spec/019-sarkov-victory.md) | 獨立 BBWIN 來源、原勝負姓名、正常勝利與缺件回退的接入閘門 |
| [子彈一般姿態規格](docs/spec/020-bullet-hd.md)、[候選來源驗證](internal/hd/bullet_test.go) | SFMAN03、58 組姿態、原姓名及正常 consumer；原生接入依規格閘門 |
| [鳳凰一般姿態規格](docs/spec/021-phoenix-hd.md)、[候選來源驗證](internal/hd/phoenix_test.go) | SFMAN04、61 組來源、原姓名 PHO HUANG 與正常 consumer；未達 READY 前只作候選驗證 |
| [鬼丸一般姿態規格](docs/spec/022-onimaru-hd.md)、[候選來源驗證](internal/hd/onimaru_test.go) | SFMAN06、66 組來源、原姓名 ONIMALU 與正常 5／4 consumer；未達 READY 前只作候選驗證 |
| [嵐一般姿態規格](docs/spec/023-lan-hd.md)、[候選來源驗證](internal/hd/lan_test.go) | SFMAN07、59 組來源、原姓名 LAN 與正常 6／4 consumer；未達 READY 前只作候選，不接正式路徑 |
| [金太極一般姿態規格](docs/spec/024-kim-hd.md)、[來源及真實姓名驗證](internal/hd/kim_test.go) | SFMAN08、57 組來源、原姓名 KING TAI CHI 與正常 7／4 consumer；限定 CONFORMED 範圍及完整動畫限制 |
| [十一人與魔王選角規格](docs/spec/025-boss-selection.md) | 原版十一人右移、擴充介面、單打／雙打與設定相容的證據及接入閘門 |
| [選角獨立核對](tools/verify_boss_selection.py) | BIGFIG 原檔肖像、無越界框線及實際原生視窗逐點比較 |
| [選角適配](internal/gamecore/selection.go)、[正常路徑測試](internal/gamecore/selection_test.go)、[十一人介面](internal/desktop/selection.go) | 只讀原游標，送普通輸入定位與確認，保留原規則，取消時不留排程 |
| [小丑 HD 規格](docs/spec/026-clown-hd.md)、[候選驗證](internal/hd/clown_test.go) | SFMAN10、62 組來源、原姓名 JOKER 與正常 9／4 consumer；依規格閘門接入 |
| [印第安喬 HD 規格](docs/spec/027-joe-hd.md)、[候選驗證](internal/hd/joe_test.go) | SFMAN11、44 組來源、原姓名 INDIAN JOE 與正常 10／4 consumer；依規格閘門接入 |
| [子彈勝利規格](docs/spec/028-bullet-victory.md)、[候選驗證](internal/hd/bullet_victory_test.go) | CCWIN 四組來源、72 個獨立 WIN 入口與正常首勝接入閘門 |
| [多場景背景草案](docs/spec/029-multi-scene-backgrounds.md) | 屋頂與道場候選、舊包相容、新版素材清單及原生接入閘門；格式擴充待確認 |
| [鳳凰勝利規格](docs/spec/030-phoenix-victory.md)、[候選來源驗證](internal/hd/phoenix_victory_test.go) | EEWIN 三組來源、PHO HUANG WIN 與正常首勝接入閘門 |
| [特效定位驗證](internal/renderdata/effects_test.go) | 19 個原版特效繪製／完整畫格的獨立幾何、寫入覆蓋與重組核對 |
| [特效素材驗證](internal/hd/effects_test.go) | 原版特效 fixture 的來源、第二組色盤、整格拒絕與版本隔離 |
| [字型來源](internal/desktop/assets/source.json)、[OFL 授權](internal/desktop/assets/OFL.txt) | Noto Sans CJK TC 固定來源、SHA-256 與授權 |
| [tools/build_desktop.sh](tools/build_desktop.sh)、[建置階段](tools/build_desktop.py) | Docker 三平台建置、來源／檔頭核對與中間二進位收據 |
| [tools/desktop_smoke.py](tools/desktop_smoke.py) | Docker Xvfb 正常原生視窗玩家路徑及設定重啟驗證 |
| [tools/desktop_match_smoke.py](tools/desktop_match_smoke.py) | 正常原生雙打至勝負、過場及返回；保存選用原貌與當下原版 RGB，不以改生命或勝負代替 |
| [tools/verify_match_capture.py](tools/verify_match_capture.py) | 獨立核對比賽擷取的選用／即時原版來源、完整原貌回退及離開對戰後快照清除 |
| [勝場規格 011](docs/spec/011-hd-win-markers.md)、[獨立證據工具](tools/hud_wins_evidence.py) | 原版拇指圖像、鎖存勝場及兩側位置來源；高解析呈現依規格狀態接入 |
| [勝場與比賽稽核](tools/audit_native_wins.py) | 核對目前勝場版、另存的完整比賽基準、四平台編譯來源、原檔與實際擷取；不替代完整 HD 驗收 |
| [陰影規格 012](docs/spec/012-hd-shadows.md)、[普通輸入探針](tools/shadow_draw_receipt.go) | 原版陰影來源、位置、裁切及逐次寫入證據；依規格閘門接入 HD |
| [陰影獨立重組](tools/shadow_reference.py) | 由固定 XLP 原檔重組實際 before／after／mask，核對裁切、同值寫入與色盤 |
| [陰影快照](internal/renderdata/shadows.go)、[只讀觀測](internal/gamecore/shadows.go)、[來源選取](internal/hd/shadows.go)、[原生呈現](internal/desktop/shadows.go) | 保留原版圖層及陰影之前的點陣層，驗完來源後畫原生柔邊陰影 |
| [陰影原版畫格驗證](internal/hd/shadows_test.go)、[裁切邊界](internal/renderdata/shadows_test.go) | 真實雙人快照、原貌重組、損壞拒絕；未觸發分支另標靜態來源 |
| [原生陰影像素核對](tools/verify_shadow_capture.py) | 原版陰影底層與寫入、實際解析度 alpha、最大重疊及原生 GPU 黑色合成；量化與切換逐點一致分開驗 |
| [陰影切片稽核](tools/audit_native_shadows.py) | 原檔、四份實際編譯、772 次繪製、24 個雙人畫格、原生／Wine／重疊／舊素材案例與完整比賽核心生命週期 |
| [tools/windows_native_smoke.py](tools/windows_native_smoke.py) | Docker Wine 的 Windows 原生視窗檢查，不能代替真機驗收 |
| [tools/windows_shift_probe.go](tools/windows_shift_probe.go)、[驅動](tools/windows_shift_probe.py) | Docker Wine 只讀核對 Win32 左右 Shift 的獨立狀態，不改遊戲核心 |
| [tools/go.mod](tools/go.mod) | 讓舊獨立 Go 探針與正式桌面模組隔離，不修改舊收據的工具來源 |
| [AGENTS.md](AGENTS.md) | 穩定目標、工作契約與文件入口 |
| [CONTEXT.md](CONTEXT.md) | 有日期的唯一現況、有效決策、輸入來源與限制 |
| [WORKLIST.md](WORKLIST.md) | 可執行工作、前置條件及完成判準 |
| [WORKLOG.md](WORKLOG.md) | 追加式工作歷程、驗證與清理結果 |
| [RESEARCH-LOG.md](RESEARCH-LOG.md) | 固定來源、啟動鏈、輸入查證與收據重生方式 |
| [VERIFICATION-MATRIX.md](VERIFICATION-MATRIX.md) | 已驗範圍、未驗項與完成聲明邊界 |
| [.gitignore](.gitignore) | 原始遊戲包及本機中間產物的版控排除 |
| [.gitattributes](.gitattributes) | 補丁 context 行的原始空白保留契約 |
| [tools/prepare.py](tools/prepare.py) | Docker 內安全盤點、作弊資料隔離與 dosgolem 來源身分記錄 |
| [tools/probe_receipt.py](tools/probe_receipt.py) | Docker 內有界啟動探針與含失敗結果的完整收據 |
| [tools/queued_entry_test.go](tools/queued_entry_test.go) | dosgolem 工作副本的佇列入口與 IRQ0／DOS 時間整合回歸案例 |
| [tools/apply_runtime_patch.py](tools/apply_runtime_patch.py) | 驗證獨立來源副本，套用規格 001 並記錄補丁與來源身分 |
| [tools/dosgolem-queued-entry.patch](tools/dosgolem-queued-entry.patch) | 僅開啟監督佇列新程式 IF 的獨立來源補丁 |
| [tools/ida_input_evidence.py](tools/ida_input_evidence.py) | IDA 9.4 原始輸入候選、函式與位址證據匯出，不作語意改名 |
| [docs/spec/001-queued-entry-interrupts.md](docs/spec/001-queued-entry-interrupts.md) | 監督佇列新程式 IF 契約與驗證範圍 |
| [docs/spec/002-gamepad-design.md](docs/spec/002-gamepad-design.md) | 說明書導出的手把配置、輸入生命週期與待驗契約，DRAFT |
| [docs/spec/003-hd-design.md](docs/spec/003-hd-design.md) | HD 來源、兩種畫風比較、動態切片與驗收界線，DRAFT |
| [tools/gamepad-preview.html](tools/gamepad-preview.html) | 不注入遊戲的手把互動配置稿與本機 HD 圖比較入口 |
| [tools/quick-moves.js](tools/quick-moves.js) | 可撤回的逐角色四招設定、指令文字鏡像與按下邊緣原型，沒有遊戲注入 |
| [tools/hd-preview.html](tools/hd-preview.html) | HD 背景、兩張透明角色與展示介面的分層試作，未接核心 |
| [tools/hd_source_probe.py](tools/hd_source_probe.py) | Docker 內場景、CPM 及角色姿態候選解碼、色號抽樣與圖集蒐證 |
| [tools/hd_frame_receipt.go](tools/hd_frame_receipt.go) | 正常單打／雙打的完整畫格、背景來源、姿態指標、座標及鏡像蒐證 |
| [tools/sprite_draw_receipt.go](tools/sprite_draw_receipt.go) | 正常雙打逐次核對角色繪製、鏡像定位、裁切與原始 bytes 的只讀探針 |
| [tools/effect_draw_receipt.go](tools/effect_draw_receipt.go) | 正常出招記錄全部 blit、實際來源指標、特效色盤與完整分層，僅供證據研究 |
| [tools/effect_reference.py](tools/effect_reference.py) | 依原版特效繪製收據的實際色盤建立重繪參考，避免誤用人物正常色盤 |
| [tools/effect_core_receipt.go](tools/effect_core_receipt.go) | 正常輸入下比較開關特效觀測的原版狀態、畫格及指令步數，不修改遊戲狀態 |
| [tools/ida_hud_evidence.py](tools/ida_hud_evidence.py) | IDA 9.4 的生命、計時及原介面繪製直接引用與函式匯出，保留原始名稱，不能代替動態驗證 |
| [tools/hud_draw_receipt.go](tools/hud_draw_receipt.go) | 正常雙打的介面 bitmap、原始欄位、每次 RAM 寫入與完整繪製後畫面實驗，尚非 HD 驗收 |
| [tools/match_core_receipt.go](tools/match_core_receipt.go) | 以 public Core 與普通雙打輸入走完整比賽，保存畫面及快照生命週期，不注入勝負或生命 |
| [tools/hud_reference.py](tools/hud_reference.py) | 從 BOARD、NAME、0-9 與原版色盤獨立重組介面，核對動態 bitmap fixture |
| [tools/hd_sprite_reference.py](tools/hd_sprite_reference.py) | 供重繪使用的原版姿態、尺寸與位置參考表，不把放大圖稱為 HD 美術 |
| [tools/hd_actor_preview.go](tools/hd_actor_preview.go) | 以原版分層收據核對 HD 姿態、鏡像與裁切的可丟棄比較稿 |
| [tools/audit_sprite_study.py](tools/audit_sprite_study.py) | 獨立重組分層收據，核對角色素材、觀測介面與證據版本 |
| [docs/spec/006-rooftop-background.md](docs/spec/006-rooftop-background.md) | 原生屋頂 HD 背景的同畫格合成、完整原貌前景及回退契約 |
| [docs/spec/007-memory-write-observation.md](docs/spec/007-memory-write-observation.md) | 同值重寫也可觀測的通用 public oracle 薄介面與取消契約 |
| [docs/spec/008-hd-characters.md](docs/spec/008-hd-characters.md) | 六層原生角色、姿態來源、重繪登錄與完成門檻，限定 READY |
| [docs/spec/009-hd-effects.md](docs/spec/009-hd-effects.md) | 原版順序的特效分層、第二組色盤、素材相容與回退，證據審查入口 |
| [docs/spec/010-hd-battle-hud.md](docs/spec/010-hd-battle-hud.md) | 生命、計時、名字、顯示勝場鎖存與原介面覆蓋，原生高解析 HUD 的來源與驗收閘門 |
| [tools/apply_write_observer.py](tools/apply_write_observer.py)、[觀測來源](tools/dosgolem-observer/memory_write_observer.go)、[合成程式驗證](tools/dosgolem-observer/memory_write_observer_test.go) | 在獨立副本新增通用 RAM 觀測，逐字保留前版 manifest |
| [tools/prepare_hd_background.py](tools/prepare_hd_background.py) | Docker 準備本機背景素材與來源 manifest，保留原 PNG bytes |
| [tools/verify_hd_capture.py](tools/verify_hd_capture.py) | Docker 核對原生同狀態 PNG、前景保留與 HD 切換重現性 |
| [tools/verify_character_capture.py](tools/verify_character_capture.py) | Docker 獨立重組原生六層畫格，核對角色替換、介面遮擋、同狀態切換及整張回退 |
| [tools/audit_hd.py](tools/audit_hd.py) | Docker 核對目前來源、三平台二進位、HD 收據、文件回填與擁有權 |
| [tools/audit_native_characters.py](tools/audit_native_characters.py) | Docker 核對六層角色版的逐平台實際編譯來源、正常視窗、獨立重組及完整回退 |
| [tools/audit_native_hud.py](tools/audit_native_hud.py) | 目前生命／計時／名字與特效切片的來源、四份編譯、正常 GUI、原貌回退、獨立重組與擁有權核對 |
| [tools/round_draw_receipt.go](tools/round_draw_receipt.go) | 正常雙打開場的中央回合訊息、展開裁切與逐寫重組探針，未接 HD |
| [docs/spec/013-hd-round-messages.md](docs/spec/013-hd-round-messages.md) | 回合開場訊息、部分背景保留與原生字圖的證據及接入閘門，第一回合限定 CONFORMED |
| [tools/round_reference.py](tools/round_reference.py) | 從 NAME／數字原檔獨立重組開場訊息，驗證來源、動畫裁切與等值寫入覆蓋 |
| [tools/round_core_receipt.go](tools/round_core_receipt.go) | 正常選單開場的核心觀測開關比較、66 格分層快照與正式對戰清除核對 |
| [tools/verify_round_capture.py](tools/verify_round_capture.py) | 獨立重組開場完整圖層，驗原生文字 GPU 窗口與暫停切換逐點還原 |
| [tools/audit_native_rounds.py](tools/audit_native_rounds.py) | 顯示修正前開場版的原檔、四平台編譯、獨立重組、正常視窗與歷史陰影基底核對 |
| [tools/display_receipt.go](tools/display_receipt.go) | 正常選單路徑的 VGA 埠序列、顯示起點與完整 64 KiB 視訊記憶體蒐證 |
| [tools/display_reference.py](tools/display_reference.py) | 依公開 VGA 契約、正常埠序列與完整視訊記憶體獨立重組顯示視窗 |
| [docs/spec/014-mode13-scanout.md](docs/spec/014-mode13-scanout.md) | mode 13h 顯示起點、實際高度與原生接入閘門，API 限定 CONFORMED |
| [tools/prepare_linear_scanout.py](tools/prepare_linear_scanout.py) | 先核對 1715 份原來源，再建立新增四檔的獨立顯示研究副本與 Go workspace |
| [tools/linear_scanout_receipt.go](tools/linear_scanout_receipt.go) | 透過候選 API 重跑正常原版，逐點比對 67 個獨立顯示視窗及原版狀態不變 |
| [tools/audit_linear_scanout.py](tools/audit_linear_scanout.py) | 核對正式副本、候選新增四檔、67 格輸出與尾列；明示原生接線尚未完成 |
| [docs/spec/015-native-scanout.md](docs/spec/015-native-scanout.md) | 原生原貌／HD 全圖層、動態可見區與尾列的接入契約，限定 CONFORMED |
| [tools/install_linear_scanout.py](tools/install_linear_scanout.py) | 保留正式 manifest v2，只在本專案副本新增已驗顯示 API 四檔 |
| [tools/audit_native_scanout.py](tools/audit_native_scanout.py) | 核對原生顯示映射、完整尾列、核心不變與目前四份編譯及正常視窗 |
| [docs/spec/016-hd-victory-messages.md](docs/spec/016-hd-victory-messages.md) | 中央勝負訊息、介面重建與顯示後直接 VRAM 繪製，斬正常首勝限定 CONFORMED |
| [tools/victory_draw_receipt.go](tools/victory_draw_receipt.go) | 正常雙打勝負文字來源、實際 STOSB 位址／同值寫入與完整顯示重組研究 |
| [tools/victory_reference.py](tools/victory_reference.py) | 從 NAME 原檔獨立核對勝負文字、透明覆蓋、同值寫入與實際可見視窗 |
| [tools/victory_core_receipt.go](tools/victory_core_receipt.go) | 正常首勝與下一回合的成對核心觀測比較、完整原貌及全部 HD 來源選擇核對 |
| [tools/verify_victory_capture.py](tools/verify_victory_capture.py) | 正常勝利的獨立原檔／完整圖層重播、WIN 圖像群組、原生字圖邊界、同狀態切換與舊素材整格回退 |
| [tools/verify_victory_animation.py](tools/verify_victory_animation.py) | 兩側正常首勝的 WIN 姿態取樣、來源與圖層重組，以及第二人原生勝利字圖、切換與下一回合清除 |
| [tools/audit_victory_animation.py](tools/audit_victory_animation.py) | 同時要求兩側核心來源與第二人 Linux／Wine 首勝收據；缺案例不輸出通過稽核 |
| [tools/audit_native_victory.py](tools/audit_native_victory.py) | 核對勝負切片的原檔、七個姿態來源、四份編譯、正常核心／視窗收據及舊版缺件回退 |
| [internal/renderdata/victories.go](internal/renderdata/victories.go)、[核心觀測](internal/gamecore/victories.go) | 規格 016 的勝負狀態、不可變直接繪製快照與最後介面光柵觀測 |
| [internal/hd/victories.go](internal/hd/victories.go)、[原生字圖](internal/desktop/victories.go) | 原 NAME 字圖、位置與完整覆蓋驗證，以及同一顯示映射的金色高解析呈現 |
| [internal/hd/victories_test.go](internal/hd/victories_test.go) | 兩組正常勝者的四份重播、實際 STOSB 覆蓋、錯誤來源拒絕及特殊字圖靜態邊界驗證 |
| [docs/spec/017-victory-pose-banks.md](docs/spec/017-victory-pose-banks.md) | WIN 圖像表與一般動作槽的來源區分、素材相容及斬首勝接入，限定 CONFORMED |
| [tools/victory_pose_reference.py](tools/victory_pose_reference.py) | 解碼斬／法蘭克 WIN 圖像 144 個入口、七個不同來源及原姿勢參考 |
| [tools/character_pose_reference.py](tools/character_pose_reference.py) | 依固定原檔與既知格式整理其他角色的 72 個 SFMAN 槽、別名及參考圖；不當作正常動態來源驗證 |
| [tools/prepare_character_extension.py](tools/prepare_character_extension.py) | 保留基底原 PNG，登錄其他角色一般姿態的候選群組；來源、透明區與全部別名先驗，原生驗收另記 |
| [docs/spec/018-sarkov-hd.md](docs/spec/018-sarkov-hd.md) | 薩爾可夫的一般來源、原字圖 SARORKOV、候選姿態與原生接入契約，限定 READY |
| [internal/hd/sarkov_test.go](internal/hd/sarkov_test.go) | 既有 Go 讀取器核對薩爾可夫候選群組、72 個入口、基底不變及 124 個正常原版 consumer；原生 UI 另驗 |
| [internal/gamecore/sprite_sources.go](internal/gamecore/sprite_sources.go) | 以完整 RAM 指標表與原檔表辨識一般／勝利圖像，保留原動作槽號 |
| [internal/gamecore/sprite_sources_test.go](internal/gamecore/sprite_sources_test.go)、[素材群組測試](internal/hd/victory_poses_test.go) | 原表辨識、未知／歧義拒絕、301 個姿態登錄與舊素材隔離；正常玩家分類另驗 |
| [tools/prepare_victory_characters.py](tools/prepare_victory_characters.py) | 保留舊 PNG，準備含兩種圖像群組的版本 3 私有試作素材及來源登錄 |
| [tools/dosgolem-display/machine_linear_scanout.go](tools/dosgolem-display/machine_linear_scanout.go)、[機器測試](tools/dosgolem-display/machine_linear_scanout_test.go)、[公開 API](tools/dosgolem-display/oracle_linear_scanout.go)、[API 測試](tools/dosgolem-display/oracle_linear_scanout_test.go) | 已驗鏈結顯示視窗的新增來源與測試，原生接入依規格 015 |
| [internal/renderdata/rounds.go](internal/renderdata/rounds.go)、[核心觀測](internal/gamecore/rounds.go)、[來源重組](internal/hd/rounds.go) | 規格 013 的開場窗口、繪製前快照與原檔來源驗證 |
| [internal/desktop/rounds.go](internal/desktop/rounds.go) | 原生高解析開場字圖與未覆寫頂列的呈現 |
| [tools/ida_ai_evidence.py](tools/ida_ai_evidence.py) | IDA 9.4 AI 載入與決策的原始位址、運算元及 bytes 匯出 |
| [docs/game-history.md](docs/game-history.md) | 青衫與 SP Moves 的歷史、招式、圖片快照與差異索引 |
| [docs/spec/004-live-input-slice.md](docs/spec/004-live-input-slice.md) | 已驗原版雙人鍵盤與斬的快捷輸入切片，限定 READY |
| [tools/input_receipt.go](tools/input_receipt.go) | public oracle API 的正常入口、同快照基本輸入與招式輪詢實驗 |
| [tools/play_server.go](tools/play_server.go) | 舊 HTTP 研究工具，原生主入口見規格 005 |
| [tools/live-play.html](tools/live-play.html) | 即時原貌、雙手把指派與逐角色四格設定介面 |
| [tools/live_smoke.py](tools/live_smoke.py) | 正常玩家路徑的本機 HTTP 整合檢查，不冒充 GUI 或手把實測 |
| [tools/build_play.sh](tools/build_play.sh) | Docker 內驗證 dosgolem 來源、建置操作入口並記錄雜湊 |
| [tools/play.sh](tools/play.sh) | 舊 HTTP 研究工具啟動，不作玩家入口 |
| [tools/browser_smoke.mjs](tools/browser_smoke.mjs) | Docker 內 Chromium 正常玩家路徑、合成雙手把與設定檢查，不能代替實體裝置驗收 |

新增文件前依文件職責路由檢查等價入口，並在同輪加入本索引或 CONTEXT。後續按需建立 `RESEARCH-LOG.md` 保存逆向證據、`VERIFICATION-MATRIX.md` 保存實測範圍、`docs/spec/` 保存行為契約；不得將未建立檔案列為可用入口。

`README.md` 只放穩定用途、使用方法與現況摘要。完整歷程只進 WORKLOG，唯一現況只進 CONTEXT，不建立重複的 HANDOFF 或 REMAKE-PLAN。

修改 README 的圖片或連結後，使用既有 `tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1` Docker 映像，將本工作樹唯讀掛載為 `/project` 並以該目錄執行 `python3 tools/verify_readme_links.py`。此[檢查工具](tools/verify_readme_links.py)同時比對 Git 追蹤清單與實際檔案，支援首頁的行內 Markdown 相對連結；只在本機存在的 workplace 檔案不能通過。它不檢查外站內容或宣稱 GitHub 頁面已實際渲染。

## 授權、遠端與交付

鬼丸勝利姿態的規格與來源入口見 [031：鬼丸勝利姿態與文字](docs/spec/031-onimaru-victory.md)。新勝利切片在 DRAFT 階段只生成候選與診斷正常來源，READY 後才接正式姓名或呈現分支。

- 已授權本機接入、原版查證、手把開發、HD 規劃，以及建立 GitHub 儲存庫並上傳自有程式與文件。沿用私人儲存庫設定；未授權推送原版素材、公開衍生美術或發布套件。
- 使用者於 2026-10-20 追加「HD素材上傳」，明確授權將已生成的 HD PNG 與對應清單提交至現有儲存庫。收錄入口為 [assets/hd/README.md](assets/hd/README.md)，逐檔身分見 [assets/hd/catalog.json](assets/hd/catalog.json)。此授權取代先前 HD 生成圖只留本機的限制；不包含原版資料、原版色號／色盤、原圖、私有執行器、記憶體收據、變更儲存庫可見性或建立 Release。
- 使用者另指出 README 的工作區圖片無法在 GitHub 顯示。沿既有「README 放整合截圖」與 HD 上傳授權，已驗的 HD 整合截圖收錄 [docs/screenshots/](docs/screenshots/)，以 [source.json](docs/screenshots/source.json)記錄來源、雜湊與驗證範圍。素材預覽、HD 實機截圖與原貌對照需分清楚；原貌圖、原版參考圖、分層 bytes 與原始收據仍留本機。
- 原版包、EXE／COM、資料、美術、音訊、記憶體快照及含原版內容的收據留在本機。私人儲存庫也不得直接提交。
- 自有程式與文件依使用者共用規則採 RRSAL-1.0。建立 LICENSE 前讀 `/home/anr2/.codex/knowledge-base/local/rrsal-1.0.md`，使用 `/home/anr2/.codex/skills/reverse-engineer-retro-game-remake/assets/project-template/LICENSE` 全文，只替換占位符；原版與第三方素材另查權利。
- 交付根目錄為 `dist-all/`。建立前讀 `/home/anr2/.codex/knowledge-base/local/retro-remake-dist-all-output.md`，由該檔決定子目錄與素材邊界。
- 正式版號採 `v.<主版>.<次版>.<修訂版>-YYYYMMDD`；定版前讀 `/home/anr2/.codex/knowledge-base/local/retro-remake-release-versioning.md`。已發布 tag 與 Release 不覆寫。
- 發行前逐平台驗證封包、啟動、必要素材、設定／存檔位置、SHA-256 與手把實測。容器編譯或 Linux 測試不代替 Windows／macOS 真機驗收。
