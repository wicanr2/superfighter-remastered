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
