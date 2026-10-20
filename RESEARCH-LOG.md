# 快打至尊 Remastered：研究紀錄

目前狀態見 [CONTEXT.md](CONTEXT.md)，工作順序見 [WORKLIST.md](WORKLIST.md)。證據等級為「已證實、強推論、假說、未知」。

## 2026-10-19：固定來源與啟動鏈

固定輸入為 `快打至尊.jsdos`，SHA-256 `aaec980cbef5679fda8274ed3549eccc97229be48221360427718a1e635f9b1d`。主要包內檔案雜湊見 CONTEXT。`tools/prepare.py` 以 zipfile 核對 CRC、路徑與內容，建立 `workplace/source-manifest.json`；共 128 檔，`CHEAT/AIDATA.DAT` 留在 `workplace/quarantine/`，不進執行根。

解包後 mtime 固定採 ZIP 的 DOS 日期時間並以 UTC 解讀，目的為可重生；這不宣稱原機所在時區。早期 schema 的 manifest 保留於 `workplace/source-manifest-v1.json`，並按收據所列 SHA-256 保存各份 `input-manifest.json`。沒有改寫既有 receipt。

dosgolem 基底：`f79eab6db8c64a524a06535e53e5d32b0bbcf7c8`，工作樹乾淨；1712 個追蹤檔的內容摘要為 `60ddc73343dfb187cef0301804724e2b8dc2e0865040804b514e572eae0522d8`。工具為 `dosgolem-go-ebiten:1.24-r1`，Go 1.24.13。原始檔與共用來源唯讀，輸出 UID/GID 1000:1000。

| 結論 | 等級 | 證據與範圍 |
|---|---|---|
| 包裝入口先 `nokey /y` 再 `sf` | 已證實 | `.jsdos/dosbox.conf` 與 `PLAY.BAT` bytes |
| 明示 `NOKEY.EXE /y → SF.COM` 後，SF.COM 自行 EXEC SF.EXE | 已證實 | `probe-startup-if-40m/stdout.txt` 的 EXEC 與開檔記錄；不宣稱完整 shell 解析 |
| 佇列入口繼承 IF 關閉會阻止時間前進 | 已證實，限定本執行器 | `queue-test-before.txt`、`probe-startup-2m-clean`；資料流與修正見規格 001 |
| 補上佇列入口 IF 後可到標題與選角 | 已證實，限定來源包與工作副本 | `probe-startup-if-40m`、`probe-single-click-60m`；未驗完整對戰 |
| 此包是未修改原始發行版 | 未知 | NFO 自述修改，實跑有第三方啟動殼；不能從 README 版本文字證明零修改 |

平台前提依 [DOSBox-X 的 DOS_Execute](https://github.com/joncampbell123/dosbox-x/blob/master/src/dos/dos_execute.cpp) LOADNGO 入口開啟 IF 的契約。參考原文已保存於 `workplace/platform-reference/dos_execute.cpp`，SHA-256 `7d45bfe461ce09c065c6e7c20ad9ceff18eff5d6f3ffdb96faf26065775dd12b`。補丁不複製該來源碼。修正在獨立副本內，沒有修改共用 dosgolem。

## 收據與失敗分類

| 路徑前綴 `workplace/` | 結果 |
|---|---|
| `probe-startup-2m` | 第一份失敗。啟動殼時間未前進，另有文字模式不能匯出 planar PNG 的工具錯誤 |
| `probe-startup-2m-clean` | 修正截圖工具後仍重現零 IRQ0，證明 PNG 錯誤不解釋啟動阻塞 |
| `probe-direct-exe-2m` | 診斷入口；不取代正常啟動鏈、不作可玩證據 |
| `probe-startup-if-2m` | 相同啟動預算已有 3 次 IRQ0，時間前進 |
| `probe-startup-if-40m` | 正常鏈到標題，320×200 模式 13h |
| `probe-single-click-60m` | 40M 步點選原版單打按鈕，正常到選角 |
| `probe-single-enter-60m` | 定時 IRQ1 Enter 未使標題前進；預設 BIOS handler 下此 API 會停留，不當作遊戲缺陷 |
| `probe-first-fight-100m` | 路徑名稱表示當時測試目標；實際仍在選角，沒有完成對戰 |
| `probe-select-confirm-100m`、`probe-bios-confirm-100m` | 不同注入路徑的確認嘗試，均未完成進入對戰；原收據保留 |
| `probe-settings-60m` | 點選後仍在標題；不能宣稱設定頁已驗 |

每份 receipt 保存命令、指令預算、外層有界程序、退碼、停止原因、工具與來源身分、輸入、原始檔是否不變及產物雜湊。PNG 是 dosgolem 色號及色盤的無損轉存。沒有 DOSBox 圖片代充收據，也沒有原版逐週期一致的聲明。

## 輸入查證

IDA Pro 9.4 使用既有 `ida-pro-9.4-idapython:py312-v1`，原 EXE 唯讀，一次性資料庫存於 workplace。首次因預設 ASCII 編碼不能輸出繁中欄位而失敗；已在工具明示 UTF-8，之後重新建立資料庫，成功匯出 292 個函式的導航資訊。這是工具修正，不是產品缺陷。

`tools/ida_input_evidence.py` 匯出原始函式名、IDA 線性位址、bytes 與 operand，語意預設未知。`ida-input-v3.json` 的 `sub_102CA` 在 IDA `0x1035D`、`0x10362` 比較 BIOS `0000:041A`／`0000:041C` 低位元組，再於 `0x1036C` 呼叫 INT 16h；這些是已讀出的指令事實。尚須以本次執行的相同 bytes、實際 caller 與鍵消費記錄閉合語意，不能直接定為全遊戲輸入契約。

歷史 [Super Fighter FAQ](https://gamefaqs.gamespot.com/pc/580471-super-fighter/faqs/10158) 提供不同鍵盤配置的線索，但與本包是否相同仍未知，不將攻略按鍵直接寫入正式映射。[官方現行頁面](https://www.superfighter.com/sf/index.html) 為另一個 Windows 版本，未下載或換用其程式與素材。

## 重生入口

以下命令都從專案根目錄啟動 Docker。掛載前先確認路徑存在。全新工作區先執行盤點及 `--snapshot`，既有補丁副本不覆寫。

```sh
docker run --rm --user 1000:1000 --memory 512m --cpus 1 --pids-limit 64 --network none \
  --mount "type=bind,source=$PWD,target=/project" \
  --mount "type=bind,source=$PWD,target=/inputs,readonly" \
  --mount type=bind,source=/home/anr2/cht/dosgolem,target=/source,readonly \
  dosgolem-go-ebiten:1.24-r1 timeout 90s python3 /project/tools/prepare.py --snapshot
```

於同一映像與掛載內執行 `python3 /project/tools/apply_runtime_patch.py`。用 Go 1.24.13 在 `/project/workplace/dosgolem-source` 建置 `go build -trimpath -o /project/workplace/bin/probe-queued-if ./cmd/probe`。快取放 workplace，禁止網路；各階段使用 timeout。補丁及測試來源均列於 AGENTS。

```sh
docker run --rm --user 1000:1000 --memory 768m --cpus 1 --pids-limit 64 --network none \
  --mount "type=bind,source=$PWD,target=/project" \
  --mount "type=bind,source=$PWD/workplace/orig,target=/orig,readonly" \
  dosgolem-go-ebiten:1.24-r1 timeout 75s python3 /project/tools/probe_receipt.py \
  --probe /project/workplace/bin/probe-queued-if \
  --source-manifest /project/workplace/dosgolem-patched-manifest.json \
  --output /project/workplace/replay-select --steps 60000000 --timeout 60 \
  --clicks 40000000:55:181
```

輸出目錄必須尚不存在，以保留既有證據。此命令只驗啟動到選角，不驗正式時序、音訊、手把與 HD。

## 同日追加勘誤：選角時點與首戰輸入

早期 100M 步截圖尚在選角，不足以稱為按鍵或選角阻塞。後續證據如下，不刪除原有失敗與嘗試收據：

- `probe-bda-observe-80m`：65M 步由工具送入 Return，BDA 尾指標 1Eh→20h；65,073,029 步由原版 INT 16h 呼叫消耗，頭指標也到 20h，當下 CPU 返回位置為 dosgolem `01B9:11E7`。工具注入寫入時記下的 CPU IP 只表示暫停位置，不能當成 guest 寫入指令。
- `ida-input-v5.json`：對應 IDA MZ 線性 `0x111E5` 的 `INT 16h` 與後續 `sub_110E0` 分支已匯出。位址對應採映像載入段 01B9／IDA 1000 的候選換算；未讀回的 runtime bytes 不升為逐位元組相同。
- `probe-two-confirm-130m`：已到 ROUND1；85M 步的第二個 Return 當時仍在 BDA 佇列，不能把進戰鬥歸因於它。
- `probe-fight-baseline-190m`：從冷啟動，只在 40M 步滑鼠選單打、65M 步送一次 Return，已正常進入 Jaan 對 Frank。由此排除「必須第二次 Return」的解釋，保留較早收據以回查。
- `probe-fight-held-190m`：同一正常前置，160M 步送 Set 1 掃描碼 20h 的按下、180M 步放開；對戰已安裝 `INT 09h → 01B9:524C`，共送出兩次 IRQ1。190M 圖中角色位置與姿態有所改變。此處只證明輸入事件接到對戰，不據此定案 D 的動作方向或所有攻防鍵。
- `probe-keyboard-settings-65m`：35M、38M、41M 步分別送 BIOS Right、Right、Return，原版設定頁正常顯示。畫面提供鍵盤配置線索，尚未驗設定修改與保存。

`-hold` 的目前 `scanOf` 實作只接受有限具名鍵、兩位十六進位掃描碼及數字字元；`d` 會被拒絕。`probe-fight-clean-190m` 保留這份參數錯誤，沒有執行遊戲；改成 `20` 後重新乾淨執行。這是工具介面差異，不是遊戲輸入缺陷。

本輪對戰的亂數內部 seed 未辨識，沒有做規則或 RNG parity 聲明。兩次冷啟動使用相同機器初始條件與前置輸入，但不同操作可以改變 AI、亂數消耗與後續控制流，不能把畫面差異全歸因於單一規則。

## 2026-10-19：背景解碼與 HD 分層來源

問題：先找到可獨立重繪的完整屋頂場景，避免從含角色與 HUD 的單張截圖猜測遮擋。

- 工具：`sc-cht-hdtools:pillow11.3.0-r1`、`tools/hd_source_probe.py`；檔案位址均為原始檔案偏移，沒有混用 IDA 位址。
- 證據：`workplace/hd-source-probe-v3/evidence.json`、`contact-sheet.png` 與逐檔 PNG；輸入及輸出 SHA-256 均在 evidence。
- 候選格式：offset 0、2 為 little-endian 寬高；offset 4 為本次支援值 1；offset 5 起 768 bytes 是 6-bit 色盤；offset 773 是 RLE 標記；offset 774 起以標記、長度、色號展開 run。非標記 byte 作單色號。此為「強推論」的資產格式，尚未完成執行檔讀取端驗證。
- 11 張 XGB 及 SELECT、SELMAN、TITLE 三張 CPM 可完整解碼並耗盡資料，輸出尺寸符合 header。SFNAME.CPM 的 header 不同，保留 unknown，未加入特例猜解。
- 屋頂場景對應 I2.XGB 的強推論由目視與色號比較支持。來源 SHA-256 `81e45c775c79f1dc13f587a63d4bbeb854b9cf9ae8198621c03f6a313ee92e16`，480×204。對 ROUND1 收據作背景中央區 700 點抽樣，最佳裁切起點 80、0，有 633 點相同。另記錄 `background-compare.json` 的較大範圍遮罩比較，54,589 點中 50,749 點相同；遮罩仍含覆蓋物，不宣稱整張圖 parity。
- 第一版把 header 誤當 6 bytes，色盤末端讀到壓縮標記而拒絕解碼。第二版因沒有成功圖而接觸表尺寸為零。依原始 bytes 邊界重新查證後改為 5-byte header，並將壓縮標記由固定 FFh 改為檔案自己的值；I12.XGB 使用 FEh。失敗輸出保留，沒有把同副檔名一概當同格式。
- 已用內建 imagegen 依原始場景與已採 B 畫風生成獨立背景、斬與法蘭克的透明待機圖。原始生成 bytes、尺寸、alpha、雜湊與提示詞在 `workplace/hd-layers/`。預覽為 `tools/hd-preview.html`，屬素材組合試作，沒有動態核心或完整動畫。

## 2026-10-19：AIDATA 可修改性研究

問題：青衫稱替換 CHEAT 資料後對手不再主動攻擊，是否代表 AI 可用外部資料調整。

### 固定輸入與工具

| 檔案 | SHA-256 | 用途 |
|---|---|---|
| SF.EXE | `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300` | 實際執行檔；IDA 9.4 MZ 預設映像段 1000h 的線性位址 |
| AIDATA.DAT | `72b10b129c9f557a8b9beb0a400b5636ab690fec5af97b55672980283042f4d8` | 576 bytes，原始資料唯讀 |
| CHEAT/AIDATA.DAT | `548a2266a585df51584d2d9902a3ab93e8832b43d54dc7d52344dbdc13839593` | 169 bytes，隔離副本；實為 ASCII 說明文字 |
| DAME | `4c61a6d95281a7c952337b7f7b8c6d5f169be9eac0544dd0a6e0e05a75c976f0` | 組合語言來源文字，用作搜尋線索；不是已確認完全對應本執行檔的原始碼 |

IDA 使用既有 `ida-pro-9.4-idapython:py312-v1` 與 `tools/ida_ai_evidence.py`，重建一次性資料庫；正式來源未修改。現行原始指令匯出為 `workplace/ida-ai-v3.json`，六個原函式，共 398 筆指令。逐檔統計與 3 個資料區塊見 `workplace/ai-data-evidence.json`。位址仍使用 IDA 原函式名稱及線性位址；下表的來源標籤只作外部別名。

### 已定位的載入與消費端

| 原始定位 | 附加語意及等級 | 證據 |
|---|---|---|
| IDA `sub_13377`，`0x13377–0x133C4` | 已證實：開啟 AI 檔，按 192 的倍數 seek，讀 192 bytes 至 `ds:15DAh` | `0x13377 mov dx,4015h`；`0x13385 mov cx,0C0h`；`0x13395 mul cx`；`0x133A4 mov dx,15DAh`；DOS seek／read 呼叫 |
| IDA `0x1E425` 的 `aidata.dat` | 已證實：檔名字串；與上述 DS 相對值的對應為強推論 | 檔案 offset `0xE625`；MZ header 512 bytes；資料段基底 `0x1A410` 加 `4015h` 對應字串；自動 xref 未產生，沒有假稱直接 xref |
| IDA `0x13388`、`0x1338B–0x13392` | 已證實：以 `ds:1232h` 選區塊；`ds:18h==4` 時改用區塊 1 | 原始 bytes 與分支；來源 DAME 的 c_level、main_select 僅作名稱線索，難度 UI 對應仍待實測 |
| IDA `sub_11988`、`sub_11AD2` | 強推論：兩人的 AI 主流程；已證實使用兩個 X 值差的絕對值分距離 | 比較常數 `48h` 與 `96h`；無號 `ja` 得三段 ≤72、73–150、>150 |
| IDA `sub_11A73`、`sub_11BBD` | 已證實：讀類別值，乘 12，加距離段乘 4，再加某狀態 byte 的低兩位；從 `ds:15DAh` 取一 byte | `0x11A8C–0x11AA7`、`0x11BCE–0x11BE9`；低兩位屬亂數狀態為來源支持的強推論，未作 seed parity |
| IDA `0x11AAB–0x11AC6`、`0x11BED–0x11C08` | 已證實：選出的 byte 乘 16，再讀各角色序列的控制與輸入值 | 基底分別為 `[si+280Eh]`／`[si+280Fh]` 及 `[si+2CD6h]`／`[si+2CD7h]`；不能把 byte 直接命名成攻擊率 |
| IDA `0x133AE–0x133BA` | 已證實：read 後直接 close，這段沒有核對 read 回傳長度 | 原始控制流；其他路徑是否事先清零不由這段單獨推定 |

原資料正好是 3×192 bytes，每個 byte 均在 0–31。每個區塊可按消費端索引分成每組 12 格，含三個距離段、每段四個候選位置。各類別的玩家可見意義、所有可達狀態及角色序列效果仍未知。

### 研究結論與修改界線

**可以透過外部資料改變 AI 的策略選擇。** 這是決策表與角色輸入序列的組合，不能當成單一「主動攻擊開關」或任意填 0–100 的難度參數。

作弊檔短於一個 192-byte 區塊。若載入區塊 1 或 2，seek 已超過檔尾，正常 DOS read 會讀不到資料；此載入段又沒有核對長度。因此「短檔令表格保留既有／初始資料，連帶減少主動行為」是強推論。尚未從同一 dosgolem 快照替換資料實測，不能把青衫的全部描述寫成已驗結果。

若後續製作 AI 設定，建議保留原版設定為基準，以獨立可還原副本調整既有策略索引的分配，先驗一個難度、一個角色、三種距離。必須拒絕短檔及未知索引，記錄來源雜湊，並以固定初始快照及受控亂數驗證實際動作。這是後續提案，使用者本輪只要求研究，沒有套用新的 AI 行為。

`DAME` 的 R_ai、com_ai_p1、com_ai_p2 名稱只提供定位。實際 binary 的部分防禦分支較文字來源多，已證明不能逐行視為同一版來源。本輪保留原始 IDA 名稱，未改 executable、正常資料或共用 dosgolem。

## 2026-10-19：原版雙人輸入與斬四招

本輪命中規格閘門與 dosgolem 對拍路由，載入 `local/retro-remake-spec-gated-workflow.md`、dosgolem public oracle API 及逆向技能。先驗原版輸入，再將最小契約寫入規格 004，標為限定 READY，最後實作本機瀏覽器入口。完整回合、返回及實體手把仍未驗收。

固定輸入仍為上表的 SF.EXE、SF.COM、NOKEY.EXE。工具為 `dosgolem-go-ebiten:1.24-r1`、Go 1.24.13，來源 HEAD `f79eab6db8c64a524a06535e53e5d32b0bbcf7c8` 加獨立佇列 IF 補丁；manifest SHA-256 為 `6d02e27d6f61bad7b3b3f07c9797fac1c6513b5e3093e41394420b2b8be215f6`。共用來源未改動。

### 原始定位與已驗語意

| 位址空間與原始定位 | 等級與證據 |
|---|---|
| runtime IRQ1 向量 `0000:0024`／`0000:0026` | 已證實：讀回 `01B9:524C`，ISR 前綴 `1E 56 51 50 53 B8` 後的重定位立即值為資料段 `0BFAh` |
| runtime DS 偏移 `3F16h`／`3F1Eh`／`3F26h` | 已證實：兩人各八方向掃描碼及方向位元，逐項按下／放開與原始表比對；表值見規格 004 |
| runtime DS 偏移 `3EF4h`／`3EF5h` | 已證實：拳為 10h、腳為 20h、同按為 30h；放開清除相應位元；雙人同時輸入可得 30h、30h |
| IDA MZ 線性 `0x15296`、`0x15303` 起 | 已證實：兩人拳腳的掃描碼處理；見 `ida-key-reader.json`，未改原函式或運算元 |
| IDA `sub_13C38`，DS 偏移 `12ACh`／`12AEh` | 已證實：以角色索引選資料檔，前端只讀；`ida-live-input.json` 保存原始指令 |
| IDA MZ 線性 `0x15D9F`、`0x15DB5` | 已證實：目前對戰迴圈開始與選取動作後的觀測點；runtime 分別為 `01B9:5D9F`、`01B9:5DB5`，兩種位址基準明確分開 |
| runtime DS 偏移 `16EAh`／`16EBh` | 已證實的限定觀察：斬的四組輸入分別進入 24h、23h、22h、25h，兩名玩家皆通過；不推定所有角色的同 ID 都有相同招式 |
| runtime DS 偏移 `16B4h`／`16B5h` | 已驗斬的左右朝向值 00h／FFh；切片遇到其他值拒絕快捷，未重寫原版朝向 |

初次實驗照 DAME 少了 `PUSH BX` 的前綴判斷而停止。失敗保留在 `input-single-v1`，後續直接讀取 binary 及 runtime bytes 修正辨識，沒有修改遊戲來符合來源文字。

### 同快照實驗與界線

`tools/input_receipt.go` 僅 import public oracle API。正常執行 NOKEY /y → SF.COM，40M 步後滑鼠選模式，按原版 Return 選角，再進入對戰。單打為 Jaan 對 Frank；雙打正常確認兩人，為 Jaan 對 Jaan。之後才保存整機快照，每個輸入變體從同一快照開始。沒有直接進戰鬥、座標注入或替換 AI。

- `input-single-v2`：25 組基本輸入。P2 鍵值能被 IRQ 接收，但單打右側仍由 AI 控制。
- `input-versus-v1`、補齊來源紀錄的 `input-versus-v2`：25 組基本輸入，含兩人八方向、拳、腳、拳腳同按與雙人同按。
- `quick-versus-v2`、補齊來源紀錄的 `quick-versus-v3`：兩人的天雷斬、旋風腿、鐵頭功與過肩摔，共八例。天雷斬為前、前下、下＋拳；旋風腿為下、後下、後＋腳；鐵頭功為下十二次輪詢、上＋腳。十二是充分條件，未宣稱最短蓄力。
- 投技先以普通前走 72 次輪詢準備近身，再送前＋拳。這是實驗準備；快捷本身只有前＋拳，不能自動接近。

收據記錄 raw RNG 候選 bytes，使用同一完整快照控制變體條件；沒有聲稱 seed 數字相同或跨實作亂數一致。oracle.State 不回捲主機檔案控制代碼或外部 held-key 集合；實驗只在主要資產已載入後還原，並明確清除主機 held-key 集合。新收據的 `provenance.json` 在執行前取得腳本、manifest 雜湊、Go 版本與完整命令；舊收據保留原貌。

重生時在 Docker 內、工作目錄 `workplace/dosgolem-source` 執行：

```sh
go run -p 1 /project/tools/input_receipt.go -root /orig -out /project/workplace/新的輸入收據 -mode versus
go run -p 1 /project/tools/input_receipt.go -root /orig -out /project/workplace/新的招式收據 -mode versus -recipes
```

使用 Go image，設 `GOMAXPROCS=2`、`CGO_ENABLED=0`、`GOPROXY=off`、`GOSUMDB=off`，沿用工作區 cache；原始資料掛 `/orig` 唯讀，設定資源與時間限制。這些是研究輸入收據，不是完整可通關證明。

### 即時入口與瀏覽器

`tools/play_server.go` 使用相同 public API、正常鏈及原始輸入，未 import `internal/`。以原版對戰迴圈安排快捷；DS:001Ah 計數防止 IRQ 返回同一 IP 時重複推進階段。手動來源以玩家與鍵盤／手把分開追蹤，最後一個擁有者放開才送 break；新的手動變化中斷該玩家快捷。每個請求都不改寫角色、碰撞、AI、座標或原始資料。

`live-http-v2` 檢查正常雙打入口、雙人拳腳、同鍵多來源、R1、前端暫停、三秒失聯清理與錯誤玩家掃描碼拒絕。`browser-live-v2` 為實際 Chromium 141.0.7390.37，12 項檢查通過，含雙支合成標準手把、設定輸入隔離、單次快捷、斷線、窄畫面與重新載入保存。手把資料只在瀏覽器 Gamepad API 合成，沒有改遊戲狀態，仍不能算實體裝置驗收。

最後補上裝置改派／斷線的明確快捷取消請求，避免中立手把斷線時，原有空輸入心跳無法取消正在蓄力的快捷。`live-http-v4` 的八項檢查通過，新增驗證取消 P1 快捷仍保留 P2 按住；`browser-live-v3` 以更新後二進位重跑 12 項通過，二進位與腳本 SHA-256 保存在各收據。`live-http-v3` 因驗證腳本把 Go 的 byte slice JSON 字串當整數陣列而失敗；改用 Base64 解碼後在同一 image 乾淨重跑通過，沒有改產品來迎合錯誤斷言。

瀏覽器工具採固定版本 `mcr.microsoft.com/playwright:v1.56.1-noble`，digest `sha256:f1e7e01021efd65dd1a2c56064be399f3e4de00fd021ac561325f2bfbb2b837a`，搭配 `playwright@1.56.1` 與本機 lockfile。官方的版本配對契約見 [Playwright Docker 文件](https://playwright.dev/docs/docker)。執行仍在 Docker，測試不開網路；只有 image 與套件下載使用網路。

第一輪 GUI 暫停測試讀到前端先行更新的狀態，誤將伺服器尚未接受命令前的步數當成凍結基準。改為讀取伺服器已確認暫停後的步數，在同一 image 乾淨重跑通過，失敗收據保留。另補上設定面板對手把 Start 的隔離，避免設定期間恢復核心。這兩者分別是驗證腳本問題與介面缺口。

## 2026-10-19：斬與法蘭克的原版姿態圖集

| 固定輸入 | SHA-256 |
|---|---|
| SFMAN01.DAT | `da5de4b2f997e411582949c2f0ab2f0540324f1e83d90bd282b78b2901a860b9` |
| SFMAN05.DAT | `b5b77d590420b92db2d265aa89483de70d58193caf442fd41eba338eb111d653` |

既有 `tools/hd_source_probe.py` 增加 `--sprites` 可撤回解碼。工具仍為 `sc-cht-hdtools:pillow11.3.0-r1`，完整來源及逐圖雜湊在 `workplace/sprite-source-v1/evidence.json`。舊版場景工具另存於 `workplace/hd-source-probe-v3/hd_source_probe.py`，與舊收據雜湊對應，避免後續擴充抹去研究歷史。

格式為強推論，位址均為原始檔案偏移：1536-byte 路徑區、1224-byte 屬性區後，`0xAC8` 為 96-byte 色盤、`0xB28` 為 72 組四位元組指標，圖像 payload 從 `0xC48` 開始。指標的段值是相對 payload，不是 runtime DOS 段；圖像位置為 `0xC48 + segment×16 + offset`。每張圖前兩個 byte 是寬、高；每列向上取整為半寬 bytes，高 nibble 先、低 nibble 後，色號零透明。以 6-bit 色盤的前 16 色解碼。

兩份檔案的 72 槽都在界內，斬有 61 個不同位置，法蘭克有 57 個；保留重複指標，不能稱 72 張不同動畫。輸出包含逐槽透明 PNG 與編號圖集，已目視斬圖集。IDA `sub_13C38` 的順序讀取支持區段邊界，DAME 的 nibble／透明處理只作旁證；完整 runtime 繪製來源鍵、角色鏡像、錨點與姿態語意尚未閉合，因此沒有將圖集當成正式動態 HD 輸入。
## 2026-10-19 追加：屋頂背景與原生完整畫格

本節為追加研究，先前「未驗動態來源鍵」的歷史記載保留。現況及受影響舊規格已回填至 CONTEXT、驗證矩陣與規格 003／006。

- 固定輸入為 SF.EXE，SHA-256 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`；I2.XGB 為 `81e45c775c79f1dc13f587a63d4bbeb854b9cf9ae8198621c03f6a313ee92e16`。IDA 9.4、MZ 映像段 1000h，使用既有 `ida-pro-9.4-idapython:py312-v1`，未作語意改名。
- 已證實：IDA `sub_13DE4` 以 DS:000Ch 的來源、DS:1332h 相機位移，逐列拷貝 204 列，來源步幅 480。`sub_13E5C` 在 `0x13E9A` REP MOVSW、`0x13E9C` POP DS、`0x13E9D` RET，runtime `01B9:3E9D` 可觀測完整畫格。原始 bytes／xref 見 `workplace/ida-hd-draw-v1.json`、`ida-hd-draw-v2.json`。
- 已證實的取樣範圍：`sub_141FA`／`sub_1439B` 使用 DS:16D6h／16D8h 的 X、16DEh／16E0h 的 Y、16F2h／16FAh 的姿態槽；指標表 1706h／1826h、基底 132Ah／132Ch。取樣的完整 4bpp bytes 與原始 SFMAN 資料吻合。四種鏡像繪製函式由 `sub_14665` 起，原始角色使用 C0h／E0h 色盤區段，受擊切 D0h／F0h。完整動畫與鏡像錨點尚未驗收。
- `tools/hd_frame_receipt.go` 由正常標題進單打或雙打，再以方向、蹲跳及拳操作。`hd-frame-single-v2` 的 124／124 個背景 RAM 與 5,719,483 個可見背景候選像素全部吻合；`hd-frame-versus-v2` 正常選斬／法蘭克，124／124 個背景 RAM 與 5,668,375 個候選像素全部吻合。來源圖像 480×204，像素 SHA-256 `eb1207239c06a0e06cd9ecbb697b4cf7e1421c4dd3e6e2a6794774246eafeb15`。
- 勘誤：首版把 DS:1334h 當成線性畫面裁切。核對 dosgolem `Indexed()`／`ScreenRGB()` 後確認目前 API 未套用硬體 CRTC 起點，改依其線性 A0000 契約核對；原失敗收據保留。本輪不修改硬體顯示契約，不宣稱實機捲動／震動 parity。
- 勘誤：雙打首版用 Down 選法蘭克，實際仍是斬。原版為八人單列，後續用四次 Right 正常選角。錯誤選角收據及對應工具 bytes 保留，未改遊戲狀態。
- 原生呈現僅觀測完整畫格，背景以固定 RAM 雜湊、色盤與相機核對後才合成。`workplace/hd-native-v2/comparison.json` 驗證同狀態切換及全部 HUD／高色盤前景輸出，遊戲核心、快捷設定及裝置指派相同。它只證明背景切片，不證明完整角色 HD、實體手把或全遊戲 parity。

## 2026-10-19 追加：角色繪製定位與完整 RAM 分層

本節補齊 HD 角色所需的最小證據，來源仍為固定 SHA-256 的 SF.EXE、SFMAN01.DAT 與 SFMAN05.DAT，完整雜湊列於規格 008。工具為 Go 1.24.13、原版 oracle、既有 IDA 9.4 匯出。IDA MZ 線性位址與 runtime segment:offset 分開使用，以下沒有改原始名稱。

- 已證實的取樣範圍：IDA `sub_141FA`／`sub_1439B` 在 runtime `01B9:42A5`／`01B9:4446` 完成角色主圖像繪製；四個 blit 入口的 ES:DI、BX、CX、DX 與 DS:SI 提供目的位置、成對裁切、鏡像、色盤及完整來源 bytes。`sub_141E0` 的 DS:1335h 決定原版兩人的順序。
- `tools/sprite_draw_receipt.go` 由正常標題選雙打、斬與法蘭克，再操作移動到場邊、普通拳腳、蹲、跳與空中前進。`sprite-draw-v1` 取得 1,432 次角色繪製；以原始 bytes 及入口暫存器獨立預測的完整緩衝區，全部與繪製後 64,000 個像素相同，來源 bytes 也全部相同。
- 已證實：鏡像的 STOSB 寫入起點存在一像素偏移；不能直接用一般圖片鏡像的左上角取代。左右裁切先化為成對像素，奇數裁切會影響來源與起點。計算保留原 16-bit 運算，來源 raw、before／after fixtures 與樣本差異皆可回查。已動態覆蓋 00h、40h、80h、左右裁切；C0h 同時翻轉及負 Y 頂部裁切未動態驗，維持未知覆蓋範圍。
- 既有 public `OnWrite` 只在值改變時通知，不能據此建立完整遮擋。原 machine 的 `WatchWrite` 已包含同值重寫，因此先建立規格 007 DRAFT、審查既有原始碼契約、升 READY，再增加不含遊戲分支的 public 薄介面及合成 COM 驗證。CPU、DOS、硬體 driver 與原版記憶體均未修改。
- 新增的兩份 Go 檔只進本專案獨立 oracle 副本。前 1713 份來源完全不變，舊 manifest 逐字另存，SHA-256 `6d02e27d6f61bad7b3b3f07c9797fac1c6513b5e3093e41394420b2b8be215f6`；新 1715 檔 manifest 為 `6ad93295a80dbf590b88b64fab3acf1ffa6c31a32eb305e0a53936cb849f9732`。來源與套用工具在 tools/dosgolem-observer 及 apply_write_observer.py，可從原副本重生。
- `sprite-layers-v1` 重跑同一正常輸入鏈，716 個完整畫格各分五層，依順序重組與原貌全部逐點相同，底層 64,000 像素完整覆蓋，保留 37,424,320 次同值重寫。1,432 次角色繪製的指令數、座標、姿態、旗標及來源指標與前輪逐項相同，支持新增觀測未改這條玩家路徑。
- 原始色盤取樣只出現 P1 C0h 與 P2 E0h。受擊替代色盤沒有在這輪出現，不能把基本受傷後的畫面稱為替代色盤已驗；特殊技與對應色盤留到相關動作取樣。
- 四張內建 image_gen 姿態表共 48 個角色姿態，依原版修正斬短黑髮／黑腰帶及法蘭克藍背心，原始 PNG 保留，不以濾鏡或待機圖代替動作。素材、逐組提示詞及原版參考表雜湊見 hd-sprite-art-v1/manifest.json。
- `hd-actor-preview-v1` 的 alpha 邊界初始化誤用會正規化座標的 image.Rect，將整格空白也納入縮放，造成人物過窄。保留該版與工具原碼，改成明確的未正規化 Rectangle 累積邊界後，v2／v3 接地與尺寸已目視；這是比較工具的幾何錯誤，不改原版或生成圖來配合錯誤。
- `hd-actor-preview-v3` 以原版分層及 48 姿態比較 16 個狀態，15 個有雙方對應，1 個缺斬 slot 56。原生玩家入口尚未接角色，未驗完整動作或正式 GUI。以上已回填規格 003、008、唯一現況與驗證矩陣，不從片段推論完整 HD 完成。

## 2026-10-19：原生六層與 Windows 持續輸入

- 上節的「尚未接原生」是當時狀態。本輪已依限定 READY 的規格 008 接入播放器，原版資料與原有 1713 份 dosgolem bytes 不變；不是將離線圖片包裝成原生收據。
- 輸入仍是同一 SF.EXE、SFMAN01.DAT、SFMAN05.DAT，雜湊沿用上節；IDA 9.4 的 MZ 線性 `sub_13DE4` 在 `0x13E07` 為 POP DS，`0x13E08` 為 RET。runtime 對應 `01B9:3E08`，可界定純背景複製結束，已證實。原生快照因此分六層，與早期 716 格五層收據分開保存。
- 觀測沿原 RAM 寫入順序記錄純背景、前置介面、第一名角色、原貌寫入、第二名角色及後置原貌寫入。每格先驗純背景完整及六層逐點重組，再替換呈現。這解除原首版整條 48 列原貌覆蓋留下天空帶及遮擋高跳角色的問題，沒有改原版顯示記憶體、位置或動畫。
- `native-actors-v4` 與 `windows-actors-v4` 各十三項正常標題到雙打流程通過，含 slot 25 空中踢擊。每側十二張原生六層快照由 `verify_character_capture.py` 獨立重組並核對相機背景。暫停三張原版色號、色盤及完整定位相同；HD 換回後遊戲區逐點相同。這證明已抽測姿態，不宣稱完整動畫。
- 原生首版色盤與來源 16 色逐項比對，6-bit 轉 8-bit 須用 `(v<<2)|(v>>4)`。只接受 P1 C0h、P2 E0h 與正常來源 RGB。未驗替代色盤、C0h 同時翻轉及頂部裁切仍整張回退。
- 八張角色 PNG 的完整透明列偏離理想等分線 3～12 像素。直接等分曾截去少量肢體並帶入鄰格。已證實修正方法是沿實際全透明列／欄登錄矩形，原 PNG bytes 不變；矩形、界線及工具 SHA-256 存於 registration.json。無透明間隔或實體圖像碰外緣時拒絕，不能用裁圖掩蓋。
- Windows Wine 的正常輸入曾在雙 Shift 按住後放開左鍵，使第二人腳鍵也釋放。固定 Ebitengine 2.9.9 的 `internal/glfw/win32_window_windows.go` 在 `_WM_KEYUP`／`_VK_SHIFT` 分支同時呼叫兩鍵 Release，為已證實來源行為。`windows-shift-v1` 的只讀 Win32 探針則驗 VK_LSHIFT／VK_RSHIFT 的 bit 15 依序為未按、雙按、只放左、全放，四組狀態全部正確。規格 005 先補 READY 契約，再以個別 VK 適配 Shift；修復後 Wine 正常雙打驗獨立放開。不能由此推論 Windows 實體鍵盤已驗收。
- GUI 測試另修正視窗晚於只讀狀態檔出現的等待條件。素材擴充後，舊缺件測試等待的招式已有 HD，屬驗證前提過時；完整群組與舊版缺件群組分開乾淨重跑。`native-actors-missing-v1` 確認缺件時整張原貌，沒有刪改正式群組或原版資料來製造結果。

## 2026-10-19：特效來源與第二色盤

輸入 SF.EXE、SFMAN01.DAT、SFMAN05.DAT 與 SHA-256 完整列於[規格 009](docs/spec/009-hd-effects.md)。使用固定 1715 檔 dosgolem 副本及 Go 1.24.13。位址空間為 runtime `01B9:IP` 與 DS 相對偏移；來源檔偏移分開標示，不混同 IDA 位址。

- 已證實於取樣範圍：effect-draw-v1／v2 共 1015 次繪製的像素與覆蓋吻合，483 格完整重組相同。來源 bytes、RAM 指標、色盤及每份探針原始碼保存於各自收據；effect-evidence-review.json 另獨立重組 19 個保存畫格。
- 追加勘誤：來源 AC8h 的正常人物色盤不能代表特效。49 次特效使用 AF8h 第二組色盤，斬為 D0h、法蘭克為 F0h。先前正常色盤導出的褐色／金色特效圖保留為歷史，不進新版特效對應。
- 已證實於取樣範圍：near-call 返回點 4393h／45AFh／4618h 表示呼叫位置，不能單獨判玩家。先核對色盤，再比較該玩家 72 槽 RAM 指標與實際 DS:SI，使用完整來源 bytes 雜湊識別。
- 特效位置由 ES:DI 相對合成緩衝區取得。取樣只涵蓋未裁切 00h／40h 幾何；未取得場邊裁切樣本，不外推支援。素材缺件、未知色盤或幾何時整格回退。
- effect-core-compat-v1 比較 456 個正常輸入邊界，開／關觀測的原貌、色盤、角色、狀態與指令步數相同。Linux 兩次正常 GUI 的同狀態切換另見 native-effects-v3／native-frank-effects-v1，不宣稱跨執行亂數或實機 parity。

## 2026-10-19：介面 bitmap 與顯示時序

輸入 SF.EXE、BOARD.XBB、NAME.XBB、0-9.XBB、BOARD.COL 的完整 SHA-256 見[規格 010](docs/spec/010-hd-battle-hud.md)。工具為 IDA 9.4、Go 1.24.13、原 1715 檔 dosgolem 副本與獨立 Python 重組。原始定位保存在 ida-hud-v1／v2／v4／v5／v6.json 及各一次性 .i64，沒有自訂改名或寫入正式原始資料庫。

- 已證實：runtime 01B9:3FAAh 的原名 sub_13FAA，把 320×32 的非零介面 bitmap OR A0h，寫到 DS:1334h 乘 320 的合成位置。3FEBh 為恢復 DS 後的 RET。1176 次原版繪製的像素與等值覆蓋吻合，33 個 v3 fixture 可由原檔重組；不是從螢幕 OCR 推算生命與時間。
- 已證實：DS:169Ch／169Eh 是生命條當格顯示值，DS:16A0h／16A2h 是待逐格消費的傷害；sub_13FEC 每次最多扣兩格。HD 不提前扣完待扣傷害。DS:2F26h 是顯示計時數字，sub_13F29 每逢主計數低三位為 7 更新，不另推算成秒。
- 追加勘誤：直接讀 DS:131Eh／1320h 會在勝場圖示尚未更新時提前顯示。舊 hud-draw-v2/hud-0973 與原檔重組差 93 點；正常擊倒後的 v3 證明 sub_133F4 建介面時才採用新值，134E6h RET 可鎖存顯示值。加入顯示勝場鎖存後 v3 全部 33 個保存樣本吻合，原版已進第二回合。
- 追加勘誤：BOARD.COL 的讀入長度 60h 不等於檔案長度。原檔 768 bytes，原版只讀前 96 bytes，介面使用其中 A0h 起的前 16 色。NAME.XBB 的字圖指標及 0-9.XBB 的 210-byte 固定字圖均由實檔與讀取端核對，沒有沿用 SFNAME.CPM 的未知格式假設。
- 已證實：BOARD.XBB 玩家標記的非零邊界是第一人 (4,12)..(17,20)，第二人 (303,12)..(320,20)。首版手動安全矩形漏到最右兩列；以獨立 fixture 重現後改由來源求邊界，原生乾淨重跑無殘留。
- 已證實於取樣範圍：hud-core-compat-v1 比較 456 個正常輸入邊界，開／關特效與介面觀測的原貌、色盤、角色、狀態及步數相同。三個正常原生 GUI 各十六張擷取可重組原版，包含原介面之前的圖層；各自暫停切換來源與恢復後 HD 畫面相同。不宣稱跨執行 RND 或真機 parity。
- GPU 限制：舊 managed 特效紋理在同狀態切回時有六個像素各差一階色值，獨立紋理修正後兩個特效案例及目前三個 HUD 案例逐點相同。自動圖集搬移影響線性取樣座標屬強推論；未做 GPU 指令追蹤，不將浮點呈現差異寫成原版輸入或規則錯誤。

## 2026-10-19：勝場圖像、完整雙打及陰影來源

勝場輸入為規格 010 的五份固定 HUD 原檔。NAME.XBB SHA-256 `60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82`，指標索引 11 指向檔案偏移 8384，header 為 10×12，後接 120 bytes；payload SHA-256 為 `17d411e0e6c1510513c3beabe3d5dbbfc3a524346b06c9a814393b5bb46861dd`，其中 93 點非零。解碼原圖確認為拇指圖示，並非由圖示名稱猜測。

- 已證實的靜態來源：IDA 9.4 的 sub_133F4 在 MZ 線性 `0x1346D..0x13481`、`0x134C5..0x134D9` 讀索引 11，分別以 8006h 加 12×序號、8130h 減 12×序號決定目的地。獨立工具同時核對原 EXE 中唯一一致的指令 bytes，IDA 位址與 EXE 檔案偏移各自保存在 hud-wins-evidence.json，不當成同一個位址。
- 已證實於動態樣本：33 個 hud-draw-v3 fixture 全部逐點重組，hud-0986 顯示第一人一勝。規則勝場較顯示值提早更新的樣本仍採鎖存值。右側及第二圖示的位置只有本輪靜態證據，不稱為正常 GUI 勝場驗收。
- 原生呈現依規格 011 先審查至 READY，再畫高解析向量拇指。只替換已核對的非零 HUD 覆蓋，完整來源層保留；未獲勝的圖示區域不得加入替換。33 個 fixture、原版鎖存及來源損壞拒絕通過；普通輸入取得首勝的三張暫停擷取原貌來源相同，切回 HD 逐點相同。
- 正常流程證據：match-core-v1 到兩次擊倒與結果報紙；native-match-v1 的 900 秒期限不足，保留失敗。native-match-v2 以 1800 秒期限重跑，兩次擊倒、結果報紙及返回標題八張擷取通過。結果與標題整個 viewport 等於即時原貌，快照已清空。此基準另存 build-baseline；目前勝場版另驗首勝，不混淆二進位身分或宣稱跨執行亂數 parity。

陰影輸入 SF.EXE SHA-256 為 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`，SHADOW.XLP 為 `a25f777105cc86468c91111152e8ef10dd4911d9b150e3c1a1020e21b7590bf1`。使用既有 ida-pro-9.4-idapython:py312-v1、UID 1000 的 IDA 9.4，對唯讀 EXE 建立一次性 sf-shadow-v1／v2.i64。292 個函式及輸入雜湊符合；未修改原函式名、位址或運算元。Python 3.13.15、Pillow 11.3.0 的獨立記錄在 shadow-static-evidence.json，IDA v2 匯出 SHA-256 為 `cbcab9d451b814007ff9616ad22c04eda9a4bdbfc8c6843f937ea648fbdc8ea0`。

| 原始定位與位址空間 | 推論等級 | 本輪靜態結論與來源 |
|---|---|---|
| SHADOW.XLP 檔案偏移 0、1、2 | 已證實 | 533 bytes；header 為 59×9，後接 531 個值為 0 或 7 的像素；由實際 bytes 與下列讀取端確認格式 |
| IDA MZ 線性 sub_133C5，`0x133C5..0x133DF` | 已證實 | DS:3FCCh 是原 EXE 的小寫 shadow.xlp 字串；DOS read 請求 227h bytes，目的 DS:1346h。請求 551 bytes 不等於原檔 533 bytes，不推測剩餘緩衝區內容 |
| IDA sub_1411E，`0x1411E..0x14164` | 已證實 | 兩次設定 ES=[DS:000Eh]、DI=DE80h。DE80h 除 320 為第 178 列；X 分支保留 DS:16B4h／16B5h、16E2h／16E4h、133Eh／1340h、16EFh／16F7h 的原偏移，不換成推測性名稱 |
| IDA sub_14167，`0x14167..0x141DF` | 已證實 | 讀 DS:1346h header；零透明，非零 OR A0h，逐列把 ES 加 14h，線性位移為 320。BL／BH 參與左右裁切；右界計算使用 X+61，不能自行改成原圖寬 59 |
| IDA sub_1411E → sub_14167 的控制流 | 已證實 | 第一人由 `0x14141` call；第二人由 `0x14164` 指令後直接落入 helper。不能只用直接 call 交叉參照計算繪製次數 |
| dosgolem 動態覆蓋與 HD 陰影 | 未知 | 尚未取得普通輸入的逐次寫入對拍與新 HD 呈現；本輪不以靜態解出宣稱完成 |

以上位址均為 IDA MZ 線性位址或明示的 DS 相對偏移，來源見 ida-shadow-v2.json 與一次性 .i64。下一步只追正常對戰的兩次陰影繪製、同值覆蓋、裁切及遮擋順序，包含第二人的直接落入路徑與 IRQ 重訪；證據足夠後再建立正式呈現規格。

## 2026-10-19：陰影動態閉合與原生呈現

沿用上節 SF.EXE 與 SHADOW.XLP 的固定 SHA-256，工具為 Go 1.24.13、固定 dosgolem 副本、Python 3.13.15 與 Ebitengine 2.9.9。原版定位仍為 runtime 01B9:4167h／419Ch／41DFh、DS:1346h；與 IDA MZ 線性及原檔偏移分開。沒有修改原版記憶體或共用執行器。

- 已證實於正常樣本：shadow-draw-v1 走正常雙打與八組普通按住／放開輸入，772 次陰影繪製的來源、位置、像素及覆蓋全部相同；19 個保存 before／after／mask 從原始 XLP 獨立重組。保留 5,002 次同值寫入，第二人的直接落入路徑也有實際記錄。
- 證據限制：正常左邊界有 181 次 X=0，右裁切 21 次；負 X 及跳過分支沒有動態樣本。初次獨立檢查要求負 X 而失敗，回查實際範圍後保留這項限制，沒有以座標注入補造。原指令導出的左裁切、SUB／SBB 借位、跳過及零寬拒絕另作靜態邊界測試。
- 規格 012 經上述來源及獨立審查升 READY 後實作。保留原版全部圖層，另存兩人原始陰影位置與繪製前底層；逐點重組陰影後的第一個點陣層才替換。HD 柔邊在原生解析度計算，重疊取最大 alpha，屬新美術呈現，不稱原版 alpha parity。
- 已證實於取樣範圍：shadow-core-compat-v1 的 456 個觀測開／關邊界，原貌、色盤、角色、狀態與步數相同，取得 448 個完整陰影快照；24 個保存雙人畫格通過來源與原貌重組。shadow-match-core-v1 普通拳擊完成兩次擊倒，陰影在兩次擊倒及第二回合均完整，離開對戰後快照清空。
- 原生證據：Linux 與 Windows Wine 各十七項、各十五張具名擷取通過；各十二張另外讀取 GPU 陰影繪製前／後 RGBA 與原生 alpha，核對幾何及黑色合成。普通走近的重疊案例七張具名擷取，其中三張確有 alpha 重疊；原貌／HD 切回 viewport 逐點相同。
- 合成檢查的相鄰 RGBA8 量化區間只用於 GPU alpha 合成，不用於原版寫入、原版重組或暫停切換。暫存 capture.png 不再重複列為新具名畫格。舊版 1 素材十三項、十一張具名擷取及缺件整張原貌另驗，沒有套用新陰影。

至此陰影的正式呈現所需證據已足夠，不再深入無關 helper。中央回合文字、其他角色與場景、完整動畫及實體硬體仍是後續範圍。

## 2026-10-19：開場訊息與部分背景

- 輸入為固定 SF.EXE、NAME.XBB、0-9.XBB、BOARD.COL，完整 SHA-256 與來源契約見[規格 013](docs/spec/013-hd-round-messages.md)。工具為 IDA Pro 9.4、Go 1.24.13、固定 1715 檔 dosgolem 副本，以及 Python 3.13.15／Pillow 11.3.0。IDA MZ 線性與 runtime `01B9:IP` 分列，沒有改原始函式名或操作數。
- 已證實：IDA `sub_134E7` 建立 96×15 暫存字圖，來源為 NAME 槽 12 加數字與槽 13。runtime 3570h 按繪製前階段與半寬選擇橫向窗口；3635h 的非零來源 OR A0h，目的 `(112+來源欄,56)`。第一回合的 66 次 helper 繪製均由原檔獨立重組。
- 已證實：開場 runtime 3E09h 從第十二列開始複製背景，頂列保留原合成段；66 次來源與像素／覆蓋均吻合。此來源與屋頂 480×204 reference.idx 相同。一般對戰 3DE4h 的純背景來源契約未改。
- 實作審查發現 helper 返回後，原常式在階段 1、半寬 4 還會把 FIGHT 圖複製到合成段前 1442 bytes。規格先退回 DRAFT，再以 round-draw-v3 記錄整個常式至 runtime 3634h；66 格最終像素與覆蓋均吻合，才恢復 READY。這推翻「helper 返回等於完整開場常式完成」的假設，v1／v2 仍保留原驗證範圍。
- 原版收據及獨立來源重組在 `round-draw-v3`；IDA 資料庫與匯出、兩輪正常輸入來源雜湊由 `round-evidence-review.json` 索引。四階段與十二種窗口均有正常樣本；回合索引 1..8 只有原始控制流與數字表的靜態證據，不稱正常動態驗收。
- round-core-compat-v1 的 1,508 個觀測開／關邊界，原貌、實時 RGB、狀態、角色、色盤與步數均相同；66 格完整分層、HUD、陰影與開場訊息獨立重組通過。正式對戰後訊息與保留列清空。
- 原生 Linux／Windows Wine 各七項、十張具名擷取通過；每側六張 GPU 字圖擷取在窗口外完全不變，三組暫停切回逐點相同。Linux 一般對戰另十七項、十五張擷取，舊素材十三項及缺件整張原貌另驗。這些是第一回合與抽測路徑證據，沒有外推其他模式、真機或實體手把。
- 開場頂端資料列是目前 oracle 未套用 CRTC 顯示起點的實際可見限制。呈現保留線性原貌，不藏掉來源；後續須補執行器顯示能力。中央勝負文字、完整動畫與其餘角色／場景仍未完成。

## 2026-10-19：鏈結 mode 13h 顯示視窗

- 路由採平台規格優先；以 [FreeVGA CRTC](https://www.scs.stanford.edu/22wi-cs212/pintos/specs/freevga/vga/crtcreg.htm) 與 [sequencer](https://www.scs.stanford.edu/21wi-cs140/pintos/specs/freevga/vga/vgaseq.htm) 的顯示起點、雙字組位址、列距與有效掃描線契約為前提。不深入遊戲的標準硬體 driver 或忙等迴圈。
- 已證實於原版樣本：固定 SF.EXE 的 67 個開場及首次對戰畫格，CRTC 12h 寫 7Fh、起點 0Ch／0Dh 合成 960，DS:1334h 為 12。完整 65,536 bytes VRAM、79,892 筆埠及步數保存在 display-ports-v1，來源 SHA-256 與工具身分見[規格 014](docs/spec/014-mode13-scanout.md)。
- 平台公式導出 320×192、起點 3,840 bytes、列距 320、最後位址相對 A0000 為 65,279。舊 64,000 bytes 的線性 API 會露出頂列，並漏掉最下四列。這推翻只移除頂端十二列就能修正的簡化假設。獨立重組的 67 格及原版預覽均保存於 display-ports-v1，等級為 hardware-spec approximation，沒有實機或逐掃描線 parity 聲明。
- 正式副本及共用來源均未改。在 display-runtime-study-v1 複製正式 1715 檔，只新增 machine／oracle 各一份 API 與測試，共 1719 檔。候選 API 只讀有效視窗，舊 Indexed／Screen 保持固定線性契約；完整來源身分與專用 workspace 都在該研究目錄。
- 候選測試、相鄰舊契約回歸與 go vet 通過，包括不同起點／列距、尾列、兩種保存還原、回傳複本及 17 種未知映射拒絕。候選只支援既有模型的固定鏈結水平設定，不自稱完整 VGA 實作；超出 64 KiB 的環繞、平面及 bank 未猜補。
- linear-scanout-api-v2 透過正常選單重走 67 格，逐點等於獨立顯示重組；API 呼叫前後的 VRAM、暫存器、步數、埠與舊 API 相同。相對未加候選 API 的基準，已保存的 67 個畫格欄位、VRAM 雜湊與步數也相同，不外推未受控亂數跨執行 parity。
- v2 另讀原版相機、場景與背景來源；67 格尾四列均等於原背景對應位置，提供下一步 HD 尾列來源核對。不能以這些樣本假定所有正常對戰尾列都沒有前景，正式呈現仍須逐格驗。
- `linear-scanout-audit.json` 核對正式來源未變、候選四檔、67 格輸出及現行四個二進位來源。原生未改用此 API，頂列問題仍是玩家路徑未完成項；下一步需同時映射原貌、HD 全部圖層及尾列。

## 2026-10-19：勝負文字的直接顯示寫入與勝利圖像群組

輸入 SF.EXE 沿用 SHA-256 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`；NAME.XBB 為 `60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82`。工具為 IDA Pro 9.4 的既有 `ida-pro-9.4-idapython:py312-v1`、Go 1.24.13、1719 檔 dosgolem 獨立副本，以及既有 Pillow 工具鏈。兩份一次性 `.i64` 與 `ida-victory-v1.json`／`v2.json` 保留原名稱、指令與定位。正式契約見[規格 016](docs/spec/016-hd-victory-messages.md)及[規格 017](docs/spec/017-victory-pose-banks.md)。

| 原始定位與位址空間 | 推論等級 | 證據與結論 |
|---|---|---|
| IDA MZ 線性 `0x15E74..0x15E7D`、`sub_13963` | 已證實 | 最終 HUD 重建及完整拷貝之後，原版才把 NAME 勝負圖像直接寫入 A000h。只保存前一張 RAM 合成圖會漏字 |
| runtime `01B9:3685..36AE`，STOSB `3696h` | 已證實於正常兩側勝者 | 低四位零透明，其餘 OR BH。`victory-draw-v1` 的斬擊倒勝利與法蘭克時間結束勝利分別寫入 458／536 點，實際地址和值與原檔完全相同；兩者同值寫入為零 |
| runtime `01B9:33F4`，堆疊返回 `5E77h` | 已證實於 v3 | 最終介面重建之前，合成 RAM 等於最後完整拷貝。可深複製既有圖層，重新觀測最後光柵層，保留後續原版寫入 |
| IDA `0x134E3`、`sub_134E7` | 已證實 | HUD 重建也寫入兩份 ROUND／FIGHT 暫存圖，共 2884 bytes。v2 否定重建後 RAM 等於舊快照的假設；v3 的完整 prefix 與覆蓋可由原檔重組。此內容屬最後光柵層，不能修改背景來源或藏掉前綴 |
| IDA `sub_137A3`／`sub_13883` | 已證實 | 勝利時重載圖像：檔案 60h 起 120h bytes 為 72-entry 表，180h 為圖像基底，分別載入 DS:1706h／1826h。原動作槽 DS:16F2h／16FAh 不變 |
| EXE 檔案偏移 58972，DS 檔案基底 42512 | 已證實 | 十一個 word 指向 AA／BB／CC／EE／FF／GG／HH／II／JJ／DD／KK WIN.FIG 字串。此處為檔案偏移，不是 runtime 或 IDA 線性位址 |
| AAWIN.FIG、FFWIN.FIG 原檔 | 已證實 | 各 72 個有效入口，分別四／三個不同來源；兩者首 96 bytes 等於正常 SFMAN 色盤。斬首勝槽 3 為 46×89，與實際捕獲 SHA-256 `8fe892413a8c7eed1bc5aa14eed38bb7a6b36dc72f9c084a98269c31ef8a5298` 相同 |

- AAWIN.FIG SHA-256 為 `0c332b13bb923116460a7fa8cf474b105d8f1d2b180a8d7ede5af6f92209f8f7`；FFWIN.FIG 為 `2a353085e1ad73d5521bf1c87e45f5678c2d2cd59148f50e291aad6995b3c9c3`。來源、別名、原姿勢圖在 `victory-poses-v1`。最初把 60h／180h 套到 SFMAN 的假設被無效指標否定；一般圖像仍用 B28h／C48h。
- `victory-draw-v2`／`v3` 重播同一第一人勝利，用於補齊重建入口與覆蓋。因此共有兩組不同正常勝者、四組重播記錄，不能算四個獨立勝利樣本。YOU WIN／YOU LOSE／DRAW GAME 只有原控制流、原字圖及靜態邊界驗證，沒有正常動態樣本。
- 初次成對核心接入在人物選擇拒絕，保存於 `victory-core-compat-v1`。單核心 `victory-core-diagnostic-v1` 只用於定位真實 WIN 圖像，不是成對通過收據。依 017 區分來源後，`victory-core-compat-v2` 的 1,479 個正常比較邊界通過，狀態與即時 RGB 不變；首勝與下一回合的完整原檔／圖層獨立重組通過。
- 勝利姿勢以內建 image_gen 生成七張透明圖，原 PNG、提示詞及來源在 `victory-art-v1`。版本 3 群組保留舊 157 個姿態鍵及原圖 bytes，新增 144 個 WIN 入口。登錄齊全不代表完整勝利動畫、第二人正常 HD 或全模式已驗；原生視窗驗收另記。

以上證據已足夠接入此來源與呈現，不再深入無關 helper。原版、圖像、VRAM、資料庫與衍生美術繼續留本機。

## 2026-10-19：兩側勝利取樣與薩爾可夫來源

- 固定 SF.EXE、NAME.XBB 與 1719 檔執行器沿用規格 016／017。本輪沒有修改正式 Go 呈現或原版核心。`victory-animation-jaan-v1` 的 5,293 個成對邊界及 `victory-animation-frank-v1` 的 5,534 個邊界，原版狀態與即時 RGB 相同。
- 已證實於取樣：斬 13 個 WIN 快照涵蓋槽 0／2／3，法蘭克 8 個涵蓋槽 0／2。每 10,000 指令觀察的 serial、counter、來源、文字前後狀態保留；五種來源另存完整畫格並從原檔重組。沒有將取樣稱為原生逐格連續動畫，也未把槽 1 的靜態登錄當作正常動態樣本。
- 已證實於 Linux：第二人正常方向／拳鍵操作，在時間歸零後由原版判法蘭克勝，winner word 8004h、生命 [76,124]。七張擷取、FRANK WIN 原矩形與抱胸來源、同狀態恢復及下一回合 [0,1] 均獨立核對。Windows Wine 仍在重跑，不外推兩平台通過。
- 薩爾可夫原檔 SFMAN02.DAT SHA-256 `e169a26f348ad6efc6563abe945698a7ccc2586134af611b5d5391e7984a30d6`。一般表 B28h、圖像基底 C48h 是檔案位移；72 入口、45 組不同來源均界限核對。`hd-frame-sarkov-v2` 由正常角色 1／4 取得 124 格，在 runtime 01B9:5DD3 逐次核對實際 segment:offset、完整 bytes 與來源，背景 RAM 全部等於 I2.XGB 屋頂。來源位移與 runtime 位址分欄，沒有互換。
- 初次選角研究保留於 v1，實際為角色 1／5，證實第二人的游標沿用第一人位置。v2 改以正常三次 Right 選法蘭克並核對 1／4；沒有用注入或重命名 v1 偽造正確對手。
- NAME 槽 1 的 88×11 原字圖為八字母 SARORKOV。初次轉錄漏記第二個 R，重新展開原 bytes 的逐列遮罩並目視後訂正。設定識別字 sarkov 與中文名不變，原始檔不修改。
- 內建 image_gen 生成四張採用圖集，共 45 張姿態，對應全部 72 個一般來源入口。最後九格的首稿因沒有完整透明列而被拒絕；另生留白修正版，保留原稿與精確提示詞，不放寬登錄條件。候選共 373 鍵，既有 PNG 不變，現有 Go 讀取器及 124 個 consumer 核對通過。正常來源槽覆蓋為 11 種，其餘來源及新角色原生 UI、WIN 圖像與完整動畫仍待驗。

規格 018 已具足一般來源與姓名接入所需證據而升 READY。這只是下一名角色的實作入口，不是該角色 HD 完成或全目標完成的聲明。

## 2026-10-19 薩爾可夫正常原生 consumer 追加驗證

已證實於本次正常樣本：native-sarkov-v2 與 windows-sarkov-v2 由正常選角進入角色 1／4。普通行走取得槽 2、蹲槽 14、跳槽 19、拳擊槽 5，暫停時回槽 0。兩個流程各自保存九張完整畫格，SFMAN02.DAT 一般表 B28h、資料基底 C48h 的指標與完整 packed bytes 均重組吻合；這裡的位址是原檔偏移，不與 runtime segment:offset 混用。

固定輸入為 SF.EXE SHA-256 24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300、SFMAN02.DAT e169a26f348ad6efc6563abe945698a7ccc2586134af611b5d5391e7984a30d6、NAME.XBB 60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82。dosgolem 副本來源仍為既有 1719 檔；原生編譯使用 Go 1.24.13，圖片核對使用 Pillow 11.3.0。工具、全部來源雜湊與四份編譯輸入見 sarkov-integration-audit.json 及 bin/*.build.json。

姓名語意沿用原字圖與原版正常畫面的既有證據，本輪只把已證實的 SARORKOV／88×11 接入呈現，並以真實 HUD 擷取驗來源及未知角色拒絕。沒有新增玩法推論。缺角色 1 的舊 v8 素材在九張擷取均整格回退；這不證明未支援的 WIN、替代色盤與幾何已完成。完整動畫及各快捷仍未知或未驗，不由一般槽登錄數推定。

## 2026-10-20 薩爾可夫 WIN 與子彈一般來源

薩爾可夫：BBWIN.FIG SHA-256 bf9aaca05512785be194558ee45b5e4dcba2b122583d83f9f63e3d577c5cac3d，原檔表 60h／圖像基底 180h，五個不同來源及完整別名存 sarkov-victory-source-v1。正常診斷與成對重播均選角色 1／4，第一人普通拳擊取得勝利，取樣原槽 0／2／3／4 的完整 bytes 與原檔吻合；槽 1 仍為靜態證據。NAME 槽 1／17 的實際 runtime caller IP 為 39DCh／39F9h，source SI 為 01FEh／368Ch，來源與位置獨立重組通過。檔案偏移與 runtime segment:offset 分開記錄，不用語意名覆蓋原定位。輸入雜湊、manifest 與 Go 1.24.13／Pillow 11.3.0 方法見 sarkov-victory-evidence-review.json、core receipt 及規格 019。

已證實於本次成對重播：9,290 個比較邊界，原版狀態及即時 RGB 不變；23 個 WIN serial 取樣及六個保存畫格重組，下一回合清除勝利快照並顯示 1／0。這是取樣與正常生命週期證據，不是每個動畫畫格或原生視窗驗收。五張生成姿態及 72 槽讀取已驗，三個原生工作尚未結束。

子彈：SFMAN03 一般表 B28h／基底 C48h 解出 58 組不同來源。hd-frame-bullet-v1 在 runtime 01B9:5DD3 保存 124 格，實際 2／4 角色、完整指標／bytes、原背景均吻合。NAME 槽 2 的檔案偏移為 05C8h，字圖為 BULLET／62×11，完整字圖 SHA-256 fcbd1dcf514526450e7588972384ed34896a601c1a9e432764fd664ab0e362c8；正常原貌與字圖均已目視。完整輸入 SHA-256、工具與來源記錄在 bullet-evidence-review.json。58 張手繪稿、72 槽與 typed 讀取測試通過，但尚未接入原生，不推定快捷、WIN、特效或完整動畫已驗。

## 2026-10-20 鳳凰一般來源與正常原生追加驗證

已證實於固定來源：SFMAN04.DAT SHA-256 2cd299e9c10814ae37bb044c2e3ae7adf940d8b1accd8feffa3844bbfb43356b；檔案 B28h 的 72-entry 表、C48h 圖像基底、AC8h 正常色盤，解出 61 組不同 bytes。NAME.XBB SHA-256 60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82，槽 3 的檔案偏移 0874h、93×11 字圖為 PHO HUANG，完整像素 SHA-256 be3a0b687780fc71d73935f00062b26c8cd814d45db4617b967122fa13faead9。原始字圖保持不變，設定 ID 沿用 phoenix。

原始程式仍為 SF.EXE SHA-256 24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300。hd-frame-phoenix-v1 由正常 3／4 選角取得 124 個 runtime 01B9:5DD3 完整畫格，兩人指標及 packed bytes 吻合原檔，I2 背景 RAM 相同；角色 3 取樣槽 0／1／2／3／4／6／11／12／16／22／23／24。以上 runtime 段位址與檔案偏移分開使用。Go 1.24.13、Pillow 11.3.0、執行器 1719 檔 manifest、工具及來源雜湊由 phoenix-evidence-review.json 與各收據綁定。

槽 15／39／56／57／58／60 原圖為能量或揮擊，槽 48／59 有洋紅特殊輪廓；只確認圖像，不推定其觸發條件。六張內建 imagegen 透明圖集按原槽及別名登錄，保留這些差異。02／04 初稿沒有完整透明分隔，不能安全裁切；用 imagegen 修正留白後通過未改動的登錄器，原稿及精確提示詞保留，沒有程式修改生成 PNG。

已證實於本次正常原生樣本：native-phoenix-v2／windows-phoenix-v1 的人物、屋頂、原姓名與陰影同格 HD。各自九張擷取從原檔獨立重組；普通行走、蹲、跳、拳及切換通過，恢復 HD 逐點一致，姓名標籤及 93×11 原矩形另由真實 HUD 測試及目視確認。缺角色 3 的舊群組在九張擷取均整格原貌。這只支持規格 021 的限定範圍，不證明完整動畫、WIN、替代色盤、快捷或實體平台／手把完成。

追加前項進度勘誤：薩爾可夫三個首勝工作已全部結束。Linux 與舊素材完整通過，Wine 僅六張勝利／切換且未取得下一回合，019 保持 READY；部分核對不改寫原失敗。子彈一般姿態已於後續 020 限定 CONFORMED，不能沿用前段「尚未接入」作為現況。

## 2026-10-20 Wine 後端 CPU 診斷

已證實於單次診斷區間：OpenGL v2 在 20.003 秒推進 875 萬步／14 格，DirectX 要求的 v3 在 20.001 秒推進 1000 萬步／16 格；均未截圖或送新輸入。v2 CPU 取樣以 commandQueue.flush 至 purego.SyscallN 為主，v3 的 9.52 秒取樣有 5.17 秒 cgocall，呼叫者包含 GLFW 事件分派、輪詢及游標。固定 Ebitengine v2.9.9 的 graphics.go 與 ui_windows.go 確認 directx/opengl 環境選項，及 Windows 10 以上先嘗試 DirectX 的自動選取契約。

輸入二進位、私有取樣入口、CPU 原檔、區間資料、固定 API 來源雜湊與限制保存於 desktop-performance-v3/analysis.json。兩個初始狀態不完全相同的單次區間不足以證明換後端解決速度；精確原因仍未知，不歸咎特定驅動或原版核心。沒有據此修改步速、文字、規則或正式後端。這不是 Windows 真機效能或正式平台驗收。

## 2026-10-20 鬼丸一般來源與正常原生追加驗證

已證實於固定輸入：SFMAN06.DAT SHA-256 f398370820cfebbce670433130fd3718651ed4943259604fb55c851fa3906cbb，實檔 B28h 表、C48h 圖像基底、AC8h 正常色盤，共 72 入口、66 組不同 bytes。SF.EXE 仍為 SHA-256 24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300；執行器以 1719 檔 manifest 綁定，沒有改原版規則或共用來源。

NAME.XBB SHA-256 60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82，槽 5 實檔偏移 0EC9h、72×11，像素 SHA-256 f042edee422d72080dde3af3da8b9a627d0247284fad2dde731ae90e40c1b55f。逐列遮罩與目視確認 ONIMALU，第六字母的二值遮罩 SHA-256 6ffc2bf8409c9fa80dfd4cabb9f5e355ca54095352cbbae44df0a5477f81bd5c，與 BULLET 兩個 L 相同，與 SARORKOV 的 R 不同。設定 ID onimaru 與外站寫法各保留，不自行修正原字圖拼法。比較資料在 onimaru-source-v1/name-glyph-review.json。

hd-frame-onimaru-v2 由正常 5／4 選角，在 runtime 01B9:5DD3 保存 124 個完整畫格，兩人指標與 packed bytes、I2 屋頂 RAM 均吻合。鬼丸取樣槽 0／1／2／3／4／5／6／7／8／19／25／26／27／28；普通拳擊只觀察到槽 8，5／6／7 屬行走樣本，不混稱攻擊。第二人一個普通 Left 選到法蘭克。v1 七次 Right 的實際對手為 1，保留逐步圖，原因未知；已不阻塞來源取得，不深挖選單內部。實檔偏移與 runtime 段位址分開使用。

六張內建 imagegen PNG 按原槽登錄，保留尖義足、彎杖、槽 35 的獨立杖／手與槽 41 紫色／白外線。最後六格的前兩稿 Alpha 最大值 254，被既有門檻拒絕；v3 從原姿態及已通過首稿獨立生成後通過，原 PNG bytes 不改。這只證明採用稿符合透明與來源登錄契約，不推定生成工具失敗的內部原因。

已證實於本次正常原生樣本：native-onimaru-v1／windows-onimaru-v1 各九張由原檔獨立重組，普通行走、蹲、跳、拳及切換通過。每個案例內核心、來源、設定及指派相同，切回 HD 逐點一致；人物與姓名另目視確認。缺鬼丸舊群組的九張均整格原貌。Go 1.24.13 完整程式測試、Pillow 11.3.0 獨立重組與真實 HUD 定向測試通過，工具及輸入雜湊由 onimaru-evidence-review.json、各 receipt 與 comparison 綁定。範圍依規格 022，不外推 WIN、替代色盤、快捷、完整動畫或實體平台。

## 2026-10-20 嵐的一般來源準備

已證實於固定來源：SFMAN07.DAT SHA-256 5dc504b74694c84daf45f79e89ab3725948a82559ca0c92b88eac63130f49148，72 入口、59 組不同 bytes，格式與位址基準同上。lan-source-v1 保留原槽、別名、圖集及逐檔雜湊。

私有 lan-source-probe-left-v1.go 使用正常標題及選角，第二人普通 Left 兩次，實際角色 6／4。hd-frame-lan-v1 共 124 格，兩人圖像 bytes 與 I2 屋頂 RAM 全部吻合；取樣槽 0／1／2／3／4／5／8／15／22／23／24／25／27。探針 SHA 與收據相符，未注入狀態，尚無 HD 稿或原生接入；不以原圖數量宣稱角色完成。

## 2026-10-20 嵐一般姿態與原生追加驗證

接續前述來源，已證實 NAME.XBB 的槽 6 位於實檔 11E3h，31×11 的原字圖為 LAN。NAME.XBB SHA-256 為 60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82，原字圖像素 SHA-256 為 2e79ac33da75905e9f9e9cfa6347083f8170594bb87d3b6a7f397e47354edf41。字圖、尺寸及原圖預覽保存於 lan-source-v1/normal-name.json 與 normal-name.png。

59 組原圖保留深褐短髮、紅長衫、白袖口、深褐褲及白踝布。槽 9／11／12／20／26／57／58 為獨立氣勁，槽 39 是褐色輪廓與桃色外線；這些只證明原圖內容，不推定觸發條件。六張內建 imagegen 圖集按原槽與別名登錄，共 733 鍵／43 PNG，原有 661 鍵與舊 PNG 不變。

八格旋身初稿的第二排第三、四格之間沒有完整透明列，被既有登錄器拒絕。診斷 SHA 綁定於 lan-art-v1/rejected-04.json；內建工具將相同八姿態縮小並重排的 v2 通過。七份精確請求與六張採用稿在 lan-art-v1，原 PNG bytes 不改。lan-evidence-review.json 保存 DRAFT 原文、候選、來源、工具與初始測試身分，先審查升 READY，再接姓名。

已證實於本次正常原生取樣：native-lan-v1／windows-lan-v1 各七項、九張擷取，由 SFMAN、背景及介面原檔獨立重組，行走、蹲、跳、拳與切換均通過。各案例內核心、來源、設定及指派相同，切回 HD 逐點一致；嵐輸出各變動 24,372 點，LAN 區各變動 3,069 點，字形與人物另經目視。native-lan-missing-v1 九張均整格原貌。這些是各平台內的同狀態比較，不稱跨平台同狀態。

Go 1.24.13 完整 internal／cmd 測試與 go vet 通過，真實 HUD 的 LAN／31×11 及未知角色拒絕另驗。Pillow 11.3.0 用於原圖解碼、透明登錄及獨立重組。工具、輸入與擷取 SHA 由 lan-evidence-review.json、各 receipt 及 lan-comparison 綁定。四份 ELF／PE／兩種 Mach-O 的 35 份編譯輸入吻合，原封移入 bin；舊鬼丸基底保持於 onimaru-build-v1/bin。範圍依規格 023 限定 CONFORMED，不外推 WIN、替代色盤、快捷、完整動畫或實體平台。

## 2026-10-20 金太極一般來源準備

已證實於固定來源：SFMAN08.DAT SHA-256 5579dee3e846d65905db84d769fae4378051e1a5cec74bed509885754cef165c，72 入口、57 組不同 bytes，實檔 B28h 表、C48h 圖像基底及 AC8h 正常色盤。kim-source-v1 保存原槽、別名、尺寸、圖集及逐檔 SHA。

kim-source-probe-left-v1.go SHA-256 9fe5e8b1fbc321ba0c0d685566bd16e8694baa1f6f030b443322190ba3d7ce9a，使用普通標題與選角，第二人 Left 三次取得 7／4。hd-frame-kim-v1 在 runtime 01B9:5DD3 的 124 格取樣，兩人圖像完整 bytes 與屋頂 RAM 全部吻合，沒有未實作事件。來源收據 SHA-256 c15024f93d3e2c348e0aeae2f1f7dba2417c092fbc4a18bda0209944f87e3b14；探針與 1719 檔 runtime manifest 均由 kim-source-review.json 核對。取樣待機 0／1、行走 1／2／3、蹲 16、跳 28／29／30、拳 4／11。未注入狀態，尚無 HD 稿或原生接入，不外推其他動作。

## 2026-10-20 金太極一般姿態與原生追加驗證

接續上述來源，已證實 NAME.XBB 槽 7 位於實檔 133Ah，109×11 原字圖為 KING TAI CHI。NAME.XBB SHA-256 為 60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82，像素 SHA-256 為 ed6ce285ff8784b6d9dd0485185336bc4ae9c9c0a4db5d110c56a138d4a484be。設定 ID kim 與中文名金太極不變；normal-name.json／png 保存尺寸與目視來源。

五張內建 imagegen 圖集對應 57 組來源，保留赤裸上身、金邊胸飾、灰護肩、藍褲、綁帶及斜置大刀。槽 6／37／49–56 為獨立氣勁，槽 15 褐金輪廓依原圖保存，只確認圖像內容。前四張各十二格，最後原參考九格改排三欄；只改參考布局，生成 PNG bytes 不改。旋轉稿 02 初版沒有完整透明分隔，既有登錄器拒絕；內建工具重排 02-v2 後通過。六份精確請求與拒用診斷保存於 kim-art-v1，kim-evidence-review.json 綁定 DRAFT、候選、來源及初始測試身分。

已證實於正常來源取樣：release-jump 第 10／11 格為槽 0、路徑 4，第 12 格才為槽 0、路徑 0。首輪視窗測試只看待機圖，過早送拳後未捕捉拳姿；外部放開並重按 Tab 後可捕捉，記錄在 native-kim-v1/diagnostic-only.json，整個案例排除驗收。這支持修正測試的放開等待條件，不推定原版全部輸入緩衝規則；遊戲程式未改。

已證實於乾淨原生樣本：native-kim-v2／windows-kim-v1 各七項、九張擷取，由 SFMAN、屋頂及介面原檔獨立重組，行走、蹲、跳、拳及切換通過。各案例內核心、來源、設定與指派相同，恢復 HD 逐點一致；金太極輸出各變動 24,741 點，姓名各變動 10,791 點，字形及位置另經目視。native-kim-missing-v1 九張均整格原貌。像素數相同不當作跨平台同狀態證據。

Go 1.24.13 完整 internal／cmd 測試及 go vet 通過，後續真實 HUD 測試驗 KING TAI CHI／109×11 及未知角色拒絕。Pillow 11.3.0 作原圖解碼、透明登錄與獨立重組，工具及輸入 SHA 由各 receipt／kim-comparison 綁定。四份候選的 ELF／PE／兩種 Mach-O 及 35 份編譯輸入吻合，原封移入 bin，前一嵐基底仍在 lan-build-v1/bin。八名可選角色的一般來源為 576 槽、463 組不同 bytes，全部群組為 805 鍵／48 PNG／十一份來源。規格 024 限定 CONFORMED，不外推完整動畫、WIN、替代色盤、快捷或實體平台／手把。

## 2026-10-20 十一人選角與魔王原版來源

使用者確認蜘蛛女、小丑、印第安喬在單打、雙打都可選。固定 SF.EXE 仍為 SHA-256 24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300。IDA 9.4 的原 sf-input-v5.i64／匯出已顯示 sub_110E0 在 IDA 線性 112ACh 比較 10，右移十一人循環；11261h／11269h 仍用八人左移，11208h 的滑鼠縮圖上限亦為八人。正常原版 v2 四組雙打與 v3 三組單打探針吻合，沒有原狀態注入。早期以八人取模推算第二人游標的假設不適用目前包，普通選角改依十一人循環，未替換 EXE。

原生新介面透過普通 Right／Return 定位與確認，兩名玩家角色及輸入仍交原版處理。首版 Linux 三單打／三雙打與 Wine 一單打／一雙打通過基本操作，但目視發現魔王縮圖框會畫出直線，不能把這八組當作修正後畫面。規格 025 返回 DRAFT 補證，原收據保留。

新 IDA 9.4 資料庫 sf-boss-selection-v1.i64／ida-boss-selection-v1.json 直接確認 sub_10DA6：IDA 線性 10DADh 將 SI 乘八，10DAFh 起以 DS:12D7h 表畫框，10DF5h 返回；索引 8–10 沒有有效縮圖矩形。只讀候選以 ObserveWrites 重組獨立顯示影本，略過這三個非法索引的框線寫入，原版 RAM、CPU、角色及輸入不寫回。採既有規格 007 的非破壞性觀測契約，執行器 1719 份來源不改。

sub_10E86 的原 BIGFIG.XBB 有十一筆、每筆 21F1h。前 60h 色盤先拷貝，SI 再加 2A0h，因此肖像實檔相對偏移為 300h，89×89。左側 (11,15) 加 A0h，右側從 (302,15) 反向寫 89 點，加 C0h。探針 v1 漏算已前進的 60h，v2 將右鏡像起點少算一點；兩份原失敗及腳本保留。依原指令修正後 v3 十五個肖像全部吻合，正常八人前綴沒有過濾，累計排除 1,280,000 次非法框線寫入。全部原定位及完整 SHA 在 boss-selection-filter-review.json，不把 IDA 線性與 runtime 01B9 段偏移混用。

已證實於修正版取樣：Linux／Wine 各一組單打及雙打完成十一人按鈕、三名原肖像、左循環、原確認、實際模式、兩側基本操作及放開。四份 boss-comparison 共十二張圖的 89×89 原肖像、色盤、實際 960×600 視窗逐點吻合，頂列沒有直線；原 RGB 另存，修正版來源標 selection-filtered-original。舊設定只補三名魔王欄位、載入不覆寫原檔；蜘蛛女兩招，其餘兩格留空，快捷仍只啟用斬。025 限定 CONFORMED，不外推完整單打過關、結局或實體手把。

## 2026-10-20 小丑一般 HD 與 JOKER 姓名

已證實 SFMAN10.DAT SHA-256 31c0547e255f23f1af5d3475ef53c2f82817b3b5f1cdea01340da6c8b14699a4，實檔 B28h 表／C48h 圖像基底／AC8h 正常色盤，共 72 槽、62 組不同 bytes。hd-frame-clown-v1 由正常 9／4 選角、第二人 Left 五次，在 runtime 01B9:5DD3 保存 124 格，兩人完整 bytes 與 I2 屋頂 RAM 相同。取樣槽 0／1／2／3／4／10／11／15／25／26／27，未推定其他動畫或觸發條件。

NAME.XBB SHA-256 60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82，槽 9、實檔 1A60h、52×11 為 JOKER；像素 SHA-256 7e031e7b909b0885d448fb4c8516fe402d1ab5db3fa359a2a6b71899042d9313。六份內建 imagegen 精確請求及原 PNG 保存在 clown-art-v1，62 組保留禿頭黑辮、金黃色正常色盤、紫褲、黃短靴及原獨立氣勁。六張均通過同一透明門檻，候選 877 鍵／54 PNG 保留舊 805 鍵及原 PNG。clown-evidence-review.json 綁定 DRAFT、候選、初始測試及來源身分，先 READY 再接 JOKER。

native-clown-v1／windows-clown-v1 各七項、九張完整重組及同狀態切換通過；native-clown-missing-v1 九張整格原貌。各案例內核心、來源、設定及指派相同，恢復 HD 逐點一致。小丑輸出各變動 27,594 點，姓名各變動 5,148 點；人物、跳躍、原貌與 Wine 畫面已目視。Go 1.24.13 完整程式測試、vet 與真實 HUD 的 JOKER／52×11 通過，Pillow 11.3.0 獨立核對。四份最終 ELF／PE／兩種 Mach-O 綁定 37 份精確編譯來源，026 限定 CONFORMED。

蜘蛛女 SFMAN09 原圖 45 組，第一份內建 imagegen 請求遭 output moderation 拒絕，沒有可採用 PNG。request-00.json 與 generation-failure-00.json 保留工具請求 ID，沒有以程式改造型或繞過工具。印第安喬 44 組原圖待製作；這兩人的 HD 狀態與已可選、可操作分開列示。

## 2026-10-20 印第安喬一般來源及拳擊勘誤

已證實於原檔：SFMAN11.DAT SHA-256 `2533818f4054f0dbbf1476d67f94461be95e903066ea517de33a6adf906afe56`，檔案偏移 B28h 表、C48h 圖像基底、AC8h 正常色盤，72 槽／44 組 bytes。NAME.XBB 槽 10、檔案偏移 1C9Eh、96×11 為 INDIAN JOE，像素 SHA-256 `57040d7fb98abd691ae808d98813218a204bfc459a91a33fed289435602a9b5c`；原 NAME 與 EXE 雜湊沿規格 027。

追加勘誤：hd-frame-joe-v1 兩人同時出拳，角色 10 的槽 11／12 已轉 path 10，不能從階段名稱推定為拳擊。hd-frame-joe-v2 以正常 10／4 選角、第二人普通 Left 六次、只有第一人按拳重取 124 格；runtime 01B9:5DD3 的兩人完整 packed bytes 與 I2 屋頂 RAM 吻合。第一人拳擊 path 27 的槽為 5／6／7，其中 5 亦見於行走。原生驗證改用 6／7 及 path 27，原錯誤 DRAFT 與審查保留於 joe-evidence-review.json，新審查為 joe-evidence-review-v2.json。

Go 1.24.13 嚴格讀取候選與正常來源、完整程式測試及 vet 通過；Pillow 11.3.0 獨立重組 Linux／Wine 各九張與缺件九張。各案例內原版狀態不變、恢復 HD 逐點一致；原版規則與執行器來源未改。027 只限定一般姿態取樣、正常色盤及原姓名，不外推 WIN、完整動畫或過關。

## 2026-10-20 子彈 WIN 靜態來源與候選

已證實於原檔：CCWIN.FIG SHA-256 `1fcf7dda4b8d78e706497f83e188c97890d6d5f17c8e6c65f82088d7b3e28402`，檔案偏移 60h 表、180h 圖像基底，72 入口對應四組 bytes。原圖為兜帽防備至露出金髮的四個姿態；獨立參考與完整來源索引在 bullet-victory-source-v1/manifest.json。這是 Pillow 11.3.0 靜態解碼，尚非正常 WIN consumer 證據。

內建 imagegen 生成四格透明候選，2172×724，SHA-256 `40e9ecc471cb8c1ba71016deba7ceaf70cb1d90bf3e26f4147101a6e168d70d5`。原 PNG、精確請求及嚴格透明矩形保存在 bullet-victory-art-v1；未接 production，仍需正常勝利來源與規格審查。

## 2026-10-20 子彈 WIN 動態來源與接入

補上正常來源：bullet-victory-core-diagnostic-v1 經普通 2／4 選角、方向及拳取得首勝，生命 124／0、計時 51、winner word 0002h，五張原檔重組通過。字圖來源 BULLET／NAME 槽 2，runtime caller IP 39DCh、SI 05C8h、矩形 (109,54,62,11)；WIN／槽 17，caller 39F9h、SI 368Ch、矩形 (180,54,31,11)。完整字圖、SHA 及來源保存在各凍結畫格，runtime 位址與 CCWIN 實檔偏移分開記錄。

來源審查後 028 升 READY，再補勝負姓名。Go 1.24.13 成對核心 6,018 邊界的狀態與即時 RGB 相同，11 個 WIN 取樣含槽 0／2／3，Pillow 11.3.0 獨立重組五張來源通過。Linux／Wine 與缺件三案例各七張完整重組、各自同狀態切換及下一回合清除通過。原字圖拒絕、完整程式測試及四平台 37 份編譯來源通過，028 限定 CONFORMED；槽 1 動態、第二人與完整動畫仍未驗。

## 2026-10-20 蜘蛛女已選造型與新限制

使用者明確選擇全覆蓋紫色連身衣 HD。定版圖 SHA-256 `4cbd89d69901d875587d2fdd471cf487917e357d52c5773b0564ecc2a75b8b74` 與原請求綁定於 spider-art-v1/accepted-design.json。十二格連身衣請求仍被工具於輸出階段拒絕，沒有 PNG；covered-generation-failure-00.json 保存 ID 18314280-85c6-4256-8e08-d2aa8d613bfe。沒有重試相同稿或將比較圖冒充完整動畫。

已證實於正常原版取樣：SFMAN09.DAT SHA-256 `76f1a2484fd551c574279138e16f2f70971c4a7259858406e90c0211a2f3f53e`，72 槽／45 組；hd-frame-spider-v1 正常 8／4 的 124 格、兩人 packed bytes 與屋頂 RAM 相同。原 NAME 槽 8、實檔 17EBh、57×11 為 WIDOW，像素 SHA-256 `87b661f0cebdf76ddc8171241d0135269add91ab45c4a4b294a8cc9d1322f608`。來源與工具身分見 spider-source-review-v1.json；尚未接 HD 或姓名白名單。

## 2026-10-20 道場候選背景與正常來源

已證實於原檔及正常取樣：I5.XGB SHA-256 `44d8adf7662c46396092581175fd0b85ca7179b9f99fe9c66b680f0ff50a9b61`，解碼 480×204，像素 SHA-256 `71c366851b72c14b1871906a42f8746fead325a26e4ee25a166b5232fb02c3ae`。hd-frame-dojo-v1 以正常 0／0 選角取 124 格，runtime 01B9:5DD3 的背景 RAM、角色 bytes 及八份原背景色盤全部吻合，scene 0、camera 80–145；不是所有鏡頭與動畫驗收。

內建 imagegen 依原圖構圖、三名遠景練武者、暖色地板與樑柱製作候選。1922×818 原 PNG SHA-256 `68a8e64e6e4dc47e61fa52f43e78471a855f6a86e2e8913ba92f13439a3db11b`，精確請求及原 bytes 保存於 dojo-art-v1；dojo-source-review-v1.json 綁定 Go 1.24.13／Pillow 11.3.0 來源。候選尚未接多場景背景或正式玩家路徑。

## 2026-10-20 鳳凰 WIN 來源與接入

EEWIN.FIG 共 6,279 bytes，SHA-256 `65f8536cdd3ba96c63d116df5c701b401776e39643fb5fb10c790ac1fdeb2a8c`。實檔 60h 表、180h 圖像基底，72 入口對應三組 bytes；前 96 bytes 與 SFMAN04 的 AC8h 正常色盤相同。原 PNG、來源索引及精確內建請求分別在 phoenix-victory-source-v1、phoenix-victory-art-v1，候選 2172×724 SHA-256 `c4c2ba8fdefb79d0041639e958338777bf68264caa2e62d1371ff421d3119556`，未改原 bytes。

正常 3／4 的單核心診斷以普通方向與拳取得首勝，生命 124／0、計時 51、winner word 0003h。字圖 PHO HUANG／NAME 槽 3，runtime caller IP 39DCh、SI 0874h、矩形 (94,54,93,11)；WIN／槽 17，caller 39F9h、SI 368Ch、矩形 (196,54,31,11)。四張原檔重組及八個 WIN 取樣通過，這些 runtime 定位與實檔偏移分開保存。

來源審查後 030 升 READY。Go 1.24.13 成對核心 5,952 邊界的狀態與即時 RGB 相同，取樣槽 0／2；槽 1 只有靜態來源。Pillow 11.3.0 獨立重組 Linux／Wine 及缺件三案例各七張，勝利、同狀態切換及下一回合清除通過。每個案例內恢復逐點一致，GPU 字圖變動 6,881 點、金色實心 1,970 點，另目視。真實字圖、完整測試／vet 及四平台精確編譯來源通過，030 限定 CONFORMED，不外推第二人或完整動畫。

## 2026-10-20 剩餘 WIN 靜態盤點

`remaining-victory-source-v1/manifest.json` 保存六份原檔及逐組 SHA、實檔偏移、尺寸、別名與參考圖：GGWIN 四組、HHWIN 六組、IIWIN 八組、JJWIN 五組、DDWIN 三組、KKWIN 四組，合計 432 入口／30 組。Pillow 11.3.0 只完成靜態格式及範圍驗證；來源對應沿現行圖像檔索引，後續仍逐角色取正常 consumer，不把解碼當成完整 WIN 或原生驗收。

## 2026-10-20：練習模式控制點與差異實驗

使用者明確指定雙方鎖血、停止計時與 AI 不動作，並確認雙方補滿且鎖滿血。這是可關閉的玩法擴充，證據不列為未修改原版 oracle。契約及位址表見[規格 032](docs/spec/032-training-mode.md)。

固定 SF.EXE SHA-256 為 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`。工具為 IDA Pro 9.4、Go 1.24.13 及現行 1719 檔 dosgolem 獨立副本；原檔及共用來源唯讀。IDA 線性位址以預設映像段 1000h 為基準，runtime 另用 `01B9:IP` 與已驗證 DS，不混列成相同位址。

已證實：IDA sub_15BD8 的 0x15C1C 及 sub_15C51 的 0x15C95 在暈眩增量之後、待扣傷害與致死旗標之前。把該次 CX 傷害增量清零可保留原版受擊及暈眩，避免生命被扣及致死旗標成立。既有 sub_13FEC 再消費待扣傷害，因此啟用時也清除先前尚未扣完的傷害。磁碟上的執行檔與 AIDATA 不修改。

已證實：IDA sub_118BE 以 DS:3EB7h／3EB8h==4 選 AI。runtime 18F2h／1927h 在 AI 完成後、當前輸入與方向歷史之前，清 DS:3EBAh 令下游收到中立；手動分支不清除。IDA sub_13F29 的 runtime 3F41h 在倒數之後、畫數字之前，可回填凍結值並保留原版數字繪製。完整原名、bytes、caller 與指令保存於 `ida-training-v1.json`，沿用既有 `ida-hud-v6.json`、`ida-key-reader.json`。

`training-probe-v3/receipt.json` 使用普通單／雙打入口，再由同一 Save／Restore 機器狀態展開基準及訓練分支，亂數繼承該狀態，沒有重新抽樣或假稱已解出 seed。單打關閉後第一人正常被擊倒；雙打兩側各命中三次，訓練中 124／124、時間 98，關閉後 99／99、時間 85。審查收據 `training-evidence-review-v1.json` 綁定全部輸入 SHA。v1 同時攻擊只命中一側、v2 關閉後仍等活動畫格而逾時，都是探針問題；v3 改分開攻擊，並在原版正常擊倒後停止。舊檔保留。

正式測試 `training-core-v3.json` 的單打先由原版 AI 造成生命 96／124，再開啟補滿。訓練到 479 格仍為 124／124、時間 95，右側兩次有效命中；關閉後時間 91、生命 78／124。雙打訓練到 556 格，雙方各兩次有效命中而維持滿血；關閉後兩側生命 74／74、時間 66。另與沒有訓練掛鉤的獨立 Oracle 從同一狀態比較 32 個百萬步邊界，CPU 暫存器、完整 DS 與即時畫面相同。此未啟用切片才是原版一致性證據。

正式測試也拒絕零生命、致死待扣、已設擊倒旗標、時間歸零、展示模式、未知指令與未知生命條來源，不寫入原版 DS。這七項是受控邊界單元實驗，不冒稱正常玩家路徑。初版測試把站立兩格的一像素繪圖偏移當成移動；v3 改驗中立輸入、站立路徑與兩像素內的原版呼吸動畫。正式程式沒有為此凍結角色動畫。

原版 BOARD.XBB 的兩個滿血矩形由固定雜湊來源讀取，啟用時只回填生命條內部。正式訓練畫格經既有 `hd.HUD.Select` 由原檔獨立重組，確認生命、數字、最後覆蓋與色盤仍吻合；HD 層保持只讀。原生、Wine、截圖與平台驗證範圍續記於 032 及 WORKLOG。

## 2026-10-20：十一景正常雙打來源

固定輸入仍為 CONTEXT 的 SF.EXE 與 128 檔 source-manifest。工具是 Go 1.24.13、固定 1719 份 dosgolem 副本；runtime manifest SHA 為 d79cc85bc1ce29dbe54c19e7857a9ac07b2e3a1754fb342632ead9e36e619fc3。診斷工具與逐檔雜湊由 workplace/stage-source-v1 保存，原檔唯讀。資料取 gamecore 只讀 runtime 快照，不使用或混寫 IDA 線性位址。

已證實於正常雙打：第一人固定 0，第二人逐一 0..10，原版 scene 為 0..10，來源依序為 I5／I12／I4／I7／I2／I3／I10／I9／I8／I1／I13.XGB。每景待機與普通二十格行走各一份，camera 80／105；原檔獨立解碼的 480×204 完整背景 hash、前 128 色與 320×200 裁切均吻合。十一份原檔 SHA、解碼 hash 及二十二份來源保存在 receipt.json，獨立 Python 重組結果為 source-comparison.json。

已證實的檔案格式切片為表頭寬高 480×204、byte 4 為 1、實檔 305h 的 escape、306h 起的 literal／escape-count-value RLE，無零 run、截斷或輸出越界；色盤從實檔 5 起以六位元分量展開。Go 及獨立 Python 對真實十一檔重組一致。這不是原版逐週期顯示或所有 camera／單打順序的證據，也不是九景 HD 已接入。格式決策仍依 [029](docs/spec/029-multi-scene-backgrounds.md) 的 DRAFT 確認閘門。
## 2026-10-20：雙向翻轉及頂部裁切的角色幾何

固定輸入為 SF.EXE SHA 24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300、SFMAN05.DAT SHA b5b77d590420b92db2d265aa89483de70d58193caf442fd41eba338eb111d653。工具是 Go 1.24.13、既有固定 dosgolem 副本、Python 3.13／Pillow 11.3.0。IDA 9.4 MZ 線性 sub_14665／sub_146E8／sub_1477E／sub_1480A 沿 008 的原 bytes；01B9:42A5／4446 是另列的 runtime 完成點，實檔偏移不混同以上位址。

已證實於保存的正常樣本：法蘭克一般槽 28、實檔 76824、105×41、C2h 的 2,298 個寫入點，及槽 27、實檔 73286、103×68、43h／TopClip 9 的 2,168 點，原檔直接重組的遮罩及色號與 CPU 層全部相同。獨立完整矩形翻轉／裁切亦吻合；character-geometry-evidence-v1/review.json 綁定輸入及來源雜湊。不是從畫稿外觀猜定位。

已證實於新正常原生樣本：character-geometry-native-c0-v1 與 character-geometry-native-top-v2 各三張幾何模式切換、七張正常首勝流程，原檔層重組與 CPU 遮罩吻合，原狀態不變、切回 HD 逐點相同，解除暫停後正常下一回合清除。實際位置、裁切、原檔偏移、變動點與收據 SHA 保存於各 geometry-comparison.json。這是 Linux 正常取樣；其他組合及平台未知，不宣稱完整動畫。

每個新幾何正式畫格仍要再次核對完整原版 CPU 層，未吻合則整格原貌。原檔 packed bytes 僅保留於使用者執行期私有記憶體，不加入素材 JSON 或 Git。原檔、共用執行器、1483 鍵美術群組均保持。

## 2026-10-20：十一人普通動作與鳳凰第二色盤光效

輸入固定於 CONTEXT 的 SF.EXE／128 原檔，Go 1.24.13、固定 dosgolem 副本與 Pillow 11.3.0。hd-motion-coverage-v1 的每名角色各自正常啟動、雙打對法蘭克，十七個移動／蹲跳／拳腳階段，共 4,803 個不同 serial 取樣。沒有狀態注入、練習、強制勝利或快捷；不是每個原版畫格、全動畫或受控 RNG 比較。

已證實：獨立工具核對各 sprite 的原始指標、尺寸與 packed SHA，保存的遮罩／色號可重組原圖。鳳凰普通出拳／腳出現第二色盤 D0h 的槽 60／58，原檔為 SFMAN04.DAT SHA 2cd299e9c10814ae37bb044c2e3ae7adf940d8b1accd8feffa3844bbfb43356b。實檔偏移 152727／148526，尺寸 32×40／22×25，805／318 寫入點及全部色號、CPU 覆蓋、既有矩形定位皆吻合。指標表 B28h、payload C48h、第二色盤 AF8h，均為檔案位址，未新設 IDA 名稱。

已證實於取樣：phoenix-effects-comparison-v1 在同一正常原版畫格比較兩素材群組，437 格中舊包 418 格可選，新包 433 格可選，15 格缺件消除且無舊成功回退。四格場邊幾何仍回退；selector 成功不等於 GPU 完整度，另由兩組各八張正常 Linux 原生擷取證明兩光效的畫面替換、同狀態切換及舊包整格原貌。新資料採既有版本 3，不改程式／玩法。

未知／待處理：取樣遇到同角色法蘭克對戰的色盤不符，以及少量 C0h 加奇數場邊裁切未吻合。guard 正確回退，不能只移除核對；原始 sample 及 unresolved_geometry_samples 保存在 source-comparison.json。蜘蛛女另有十八個實際未覆蓋鍵，仍需補稿及 normal consumer。這些不因鳳凰光效通過而解決。
