# 014：mode 13h 顯示視窗與開場頂列問題

狀態：READY，限定候選執行器 API；原生接入仍待完成。日期：2026-10-19。目標為修正原貌與 HD 的顯示來源。先補足 dosgolem 的唯讀候選 API，再接入原生呈現；候選輸出通過不等於玩家主入口已修正。

## 問題與範圍

目前 `oracle.Screen`／`Indexed` 在鏈結 mode 13h 讀 A0000 起的 64,000 bytes，固定 320×200。遊戲實際把 CRTC 顯示起點設為 960，並把垂直顯示結束設為 7Fh。忽略它們會露出用作暫存的頂列，且漏掉可見範圍最末四列。不能以裁掉上方十二列或拉伸剩餘 188 列取代完整顯示。

本規格的候選 API 處理固定 320 像素寬的鏈結 mode 13h、雙字組位址、列距與可見高度。未知模式、水平平移、分割、非鏈結、越出線性 64 KiB 的映射均明確拒絕。既有 `Screen`、`Indexed`、存檔與 CPU 執行不改動；共用 dosgolem 來源維持唯讀。

## 平台前提

- [FreeVGA CRTC registers](https://www.scs.stanford.edu/22wi-cs212/pintos/specs/freevga/vga/crtcreg.htm)：0Ch／0Dh 合成顯示起點；14h bit6 開啟雙字組定址，起點乘四。13h 的列距是暫存器值乘二再乘記憶體位址大小，本模式為乘八。12h 加 07h 的溢位位元決定有效掃描線數；除以 09h 低五位加一，才是記憶體像素列數。
- [FreeVGA sequencer operation](https://www.scs.stanford.edu/21wi-cs140/pintos/specs/freevga/vga/vgaseq.htm)：256 色輸出與一般 16 色的水平像素時序不同。本次不重寫 dosgolem 的水平時序模型。
- 固定 dosgolem 模型的 `setModeTiming(13h)` 將水平顯示結束正規化為 27h，`setMode13` 設 13h／14h／17h 為 28h／40h／A3h。候選 API 的寬固定 320，只接受這個既有水平設定；不把此正規化欄位稱為完整硬體暫存器模型。

這是硬體規格近似（hardware-spec approximation），不稱逐掃描線或實機像素 parity。既有 planar `DisplayStart()` 的位址基準不適用本次鏈結雙字組輸出，不能直接沿用其乘數。

## 原版選值與證據

- SF.EXE SHA-256：`24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`。
- dosgolem 獨立副本 1715 檔，manifest SHA-256：`6ad93295a80dbf590b88b64fab3acf1ffa6c31a32eb305e0a53936cb849f9732`。主機共用來源與正式工作副本均不因候選研究改寫。
- 已證實於正常樣本：`tools/display_receipt.go` 走 NOKEY／SF.COM 啟動鏈、普通選單與選角，`display-ports-v1` 保存 67 個開場及首次對戰樣本、完整 65,536 bytes 視訊記憶體、原版埠寫入與步數。
- 原版在第 118,519,370 步寫 CRTC 12h = 7Fh，未改水平或列距設定。runtime `01B9:3E5Ch` 的既有 IDA 匯出另顯示以 DS:1334h 乘 80 寫 0Ch／0Dh；樣本均為 12×80 = 960。這裡只引用遊戲選值，不再逆向標準 VGA 語意。
- 平台公式導出顯示起點 3,840 bytes、列距 320、可見 320×192，最後一點為 A0000 相對偏移 65,279。原版寫入選值為已證實；公式與顯示輸出仍標硬體規格近似。`tools/display_reference.py` 獨立重組，輸出與雜湊在 `display-ports-v1/reference.json`。

## 候選 API 契約

READY 審查依 `display-ports-v1/reference.json` 的全部 67 個獨立顯示視窗、完整尾列與埠選值，以及原始 VGA 公開契約。原貌預覽已目視核對頂端資料列消失、人物／介面及底部完整。來源程式與資料不修改；水平時序正規化與可見區映射的限制維持明示。

- 在新的研究目錄複製已驗的 1715 份來源，只新增 machine 與 oracle 各一個程式檔及測試檔。準備工具先核對既有 manifest，輸出新的候選 manifest。未接原生主入口前，正式 `workplace/dosgolem-source` 與 `go.work` 不改。
- `Machine.LinearScanout()`／`Oracle.LinearScanout()` 回傳寬、高、起點 bytes、列距 bytes、CRTC 複本與逐點色號複本。只讀，不增加步數、不讀寫 I/O 埠、不改選擇器、VRAM、CPU 或輸入。
- 模式須為 13h 且仍鏈結，水平設定須是既有模型的 27h；14h bit6 必須為一。08h 的平移、屬性 13h 的平移、09h bit7 的額外掃描重複與可見區內的 line compare 不在此版本範圍。列距不得小於 320，整個視窗必須落在 A0000 的 64 KiB 內。未滿足時回明確錯誤，不回截短或猜補的圖。
- 可見高度依實際暫存器計算，須為完整記憶體像素列。每列從 `起點 + y×列距` 複製 320 bytes。來源在 64 KiB 範圍以外時不猜環繞、平面或 SVGA bank 語意。
- `Oracle.Screen`／`Indexed` 的固定線性語意保持不變，舊原貌、寫入觀測、記憶體快照與存檔證據可繼續核對。候選 API 另有名稱，不能把既有收據重新命名成已套用顯示起點。

## 原生接入仍待完成

原生層須同時處理原貌、HD 背景、人物、HUD、陰影與開場字圖的座標映射，並讀到舊 64,000 bytes 以外仍可見的四列。原始完整分層與繪製前底層保留在原 VRAM 座標空間；顯示映射是其後的獨立步驟。不能只移動字圖或只把 HD 內容往上挪。

接入前保存現行 9623266 的二進位與精確編譯輸入，既有收據保留版本身分。完整顯示映射、視窗比例與回退須有實際呈現證據才接入正式路徑。此文件不代替尚未定案的正式像素比例或預設 HD 模式。

現行四個二進位與 30 個精確編譯輸入已保存於 `workplace/native-rounds-v1/build-baseline`，身分見該目錄的 `source.json`。正式執行器仍為 1715 檔，未加入候選 API；現行玩家入口頂列問題仍存在。

## 候選實作與已驗證部分

- 原始候選程式與測試在 `tools/dosgolem-display/`。`tools/prepare_linear_scanout.py` 先核對固定正式 manifest，建立 `workplace/display-runtime-study-v1/dosgolem-source`；原 1715 檔逐字不變，只新增四檔，共 1719 檔。完整身分見 `candidate-manifest.json`，專用 workspace 為該研究目錄的 `go.work`。
- `display-runtime-study-v1/tests.log` 的候選 API、17 個拒絕條件與相鄰舊契約回歸通過，go vet 通過。記憶體快照與狀態檔往返後的顯示內容相同，回傳色號與 CRTC 不與機器共用儲存。
- `linear-scanout-api-v2` 用該 workspace 重走普通選單與選角，67 格輸出與獨立埠重組完全相同。API 呼叫前後的 VRAM、暫存器、步數、埠序列與舊 API 不變；與未加候選來源的基準比，67 個已記錄畫格狀態、VRAM 雜湊及步數一致。這不是未受控亂數跨執行 parity 的聲明。
- v2 另記原版場景、相機與背景來源。67 格最末四列均逐點等於原始背景對應位置，足以支援後續 HD 尾列檢查。正式呈現仍須逐格檢查，不由這些樣本假定所有尾列都沒有前景。
- `tools/audit_linear_scanout.py` 核對正式來源未變、候選四檔、67 個顯示輸出與尾列，以及現行四個二進位仍綁定原編譯輸入；收據為 `workplace/linear-scanout-audit.json`。其中 `native_projection_integrated` 明確為 false。

後續測試使用研究 workspace 時，在 Docker 內設定 `GOWORK=/project/workplace/display-runtime-study-v1/go.work`。正常原版重跑入口是 `tools/linear_scanout_receipt.go`，輸出目錄須為新的 `workplace/` 子目錄，且需保留 `display-ports-v1` 的基準。不要改正式 `go.work` 讓候選實作無聲進入玩家路徑。

## 驗收

1. 平台邊界測試驗起點／列距／高度、完整尾列、回傳複本、拒絕未知映射與兩種保存後還原。
2. 67 個正常原版樣本的候選 API 與獨立埠重組逐點一致，舊 64,000 bytes API 及原版狀態不變。
3. 原生接入後由普通標題進入開場、一般對戰與結果，驗原貌／HD 同狀態切換、頂列消失、四列尾端保留與未知映射整張回退。

第一、二項通過只證明候選執行器能力；第三項未完成前，玩家主入口仍列未修正。原版、VRAM、截圖及含原版資料收據只留本機。
