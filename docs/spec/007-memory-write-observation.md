# 007：完整記憶體寫入觀測

狀態：CONFORMED，限定普通 RAM 的加法觀測介面。日期：2026-10-19。DRAFT 已依既有 WatchWrite／Unwatch、Write8 審查後升 READY，再實作並通過合成 COM 及正常雙打分層驗證；不改 CPU、DOS、視訊或原版資料。

## 問題與既有證據

HD 角色合成需要知道每個像素最後由哪一次繪製寫入。同色重寫仍可能代表投射物、前景或另一角色的遮擋，不能只以值有沒有改變判斷所有權。

基底為 CONTEXT 記錄的 dosgolem commit 與獨立 IF 補丁。既有 `oracle/run.go:OnWrite` 呼叫 `Machine.WatchWrites`，`internal/machine/machine.go` 明確只在 `Mem[a] != v` 時通知。此限制已由原始碼證實，不用它推斷完整像素所有權。

`internal/machine/probe.go:WatchWrite` 已提供每次寫入的多監看點，包含同值重寫；`Write8` 先保存 old、寫入 new，再呼叫 `noteWrite`。`Unwatch` 可獨立取消。以上是既有 Go 原始碼的已證實契約，不是遊戲反組譯位址，也不把它稱為 SF.EXE 的行為。

## 介面與生命週期

- 在獨立 dosgolem 副本新增 `oracle.MemoryWrite`：`Address uint32`、`Old, Value uint8`、`Writer Addr`。Address 是實體線性位址，Writer 是寫入指令起點的 runtime segment:offset，不混成 IDA 位址。
- `ObserveWrites(lo, hi uint32, on func(MemoryWrite)) (cancel func(), err error)` 觀測含兩端的普通 RAM 寫入，包含同值重寫。範圍須在 20 位址空間內且 lo ≤ hi，callback 不可 nil；不符時回錯且不安裝監看。
- 只包裝既有 `Machine.WatchWrite`，保留既有 `OnWrite` 的只通知值變更契約。取消函式可重複呼叫，不取消其他監看。
- callback 與 Run 位於同一執行緒。只讀事件，不寫回記憶體、不呼叫 Run、不在 callback 內註冊或取消監看。場景結束或 Core.Close 時由擁有者取消。
- 本介面只承諾普通 RAM；平面 VGA 的獨立 VRAM 不在範圍內。SF 的軟體合成緩衝區屬普通 RAM，顯示拷貝與 CRTC 限制維持規格 006。

## 來源與驗證

可重現來源檔放 `tools/dosgolem-observer/`，`tools/apply_write_observer.py` 只增加檔案到本專案的 `workplace/dosgolem-source/oracle/`。套用前驗全部舊來源雜湊，逐字保留前版 manifest，再以新 manifest 記錄新增檔、原 manifest 雜湊、規格與套用工具。共用 dosgolem 不改動，舊收據仍以舊 manifest 解釋。

單元驗證採不含原版素材的合成 COM：兩次相同 MOV word、STOSB、REP MOVSW。核對每次位元組事件、舊值、新值、runtime 指令起點、區間、獨立取消與 legacy callback。觀測開／關後的普通 RAM、暫存器、IP、指令數及週期須相同。新 API 不參與存檔，不提供狀態注入。

通過後才用正常標題與對戰路徑驗證原版畫格分層；該玩家契約另寫角色呈現規格。本規格的綠色單元測試不能宣稱角色 HD 或原版顯示 parity。

## 驗證結果

`workplace/write-observer-test.jsonl` 記錄兩個合成 COM 測試通過，包含十次位元組事件、兩次同值重寫、runtime 指令起點、取消與 legacy 契約，以及觀測開／關的完整 RAM、暫存器、IP、步數、週期與 tick 相同。

`workplace/sprite-layers-v1/receipt.json` 取得 716 個正常雙打完整畫格，依觀測分層重組均與原版線性畫面相同，保留 37,424,320 次同值重寫。與未掛完整寫入監看的 `sprite-draw-v1` 比較，1,432 次角色繪製的步數、姿態、座標及來源均相同。這只支持觀測的非侵入性與原版分層，不宣稱 HD 動作已完成。

現行研究副本共 1715 份追蹤來源，舊 1713 份全數不變。舊 manifest bytes 保存為 `workplace/dosgolem-patched-manifest-v1.json`，SHA-256 `6d02e27d6f61bad7b3b3f07c9797fac1c6513b5e3093e41394420b2b8be215f6`。既有原生二進位仍屬前版背景切片，尚未重建為角色分層版本。
