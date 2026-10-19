# 001：監督佇列的新程式中斷狀態

狀態：CONFORMED，限定監督佇列入口與啟動鏈。範圍限定 dosgolem 本專案工作副本，不修改遊戲規則或原始檔。

## 問題與證據

- 固定輸入及雜湊見 [CONTEXT.md](../../CONTEXT.md)。dosgolem 基底 commit 為 `f79eab6db8c64a524a06535e53e5d32b0bbcf7c8`，完整來源身分保存在 `workplace/dosgolem-source-manifest.json`。
- `workplace/probe-startup-2m/` 保存原始失敗。NOKEY 常駐後，監督佇列進入 `SF.COM`；兩百萬步時 `IF=false`、IRQ0 次數為零，`AH=2Ch` 回傳時間持續為零。此觀察已證實，尚不單獨證明修法。
- 原始碼 `internal/dos/exec.go` 的 `spawnQueued → enterProgram` 設定新程式暫存器與入口，沒有開啟 IF。`internal/machine/loader.go` 的直接載入路徑 `setEntry` 有設定 IF。此差異已證實。
- `internal/dos/dos.go` 的 DOS 時間來自 `Machine.Ticks`；`internal/machine/machine.go` 的 IRQ0 在 IF 關閉時只掛起、不送出。這是本次症狀的完整程式資料流。
- 平台前提採 [DOSBox-X 的 DOS_Execute](https://github.com/joncampbell123/dosbox-x/blob/master/src/dos/dos_execute.cpp) 的 LOADNGO 入口：交出新程式前開啟 IF。此為成熟實作契約，不以遊戲迴圈重新發明 DOS 時間。

## 契約

1. `spawnQueued` 成功載入新程式，在 `enterProgram` 後開啟 CPU IF。
2. 保留其他旗標與既有 PSP、暫存器、佇列、記憶體及回收語意。
3. 只改監督佇列入口；不在遊戲內定時設 IF、不注入時間、不跳過 `SF.COM`。
4. 前一程式正常結束或 TSR 常駐時都適用；沒有佇列時的既有行為保持。
5. 共用 `/home/anr2/cht/dosgolem` 唯讀，變更先保存在本專案 `workplace/dosgolem-source`，以受版控補丁重生。

## 驗證

- 自製最小 DOS 程式：前一程式 CLI 後結束或常駐，下一程式用 AH=2Ch 等待非零時間，再正常離開。基底應重現等待不前，修正後須經 IRQ0 自然完成。
- 執行 dosgolem `internal/dos` 與 `internal/machine` 相關測試。
- 以相同原始檔、啟動鏈與兩百萬步重跑，確認 IRQ0 與時間自然前進，記錄後續停止原因。不能只以單元測試宣稱遊戲可玩。

證據審查：`workplace/queue-test-before.txt` 已在未修改基底重現正常結束與 TSR 兩案例皆停在 `ticks=0`。`probe-startup-2m-clean` 移除不適用的 PNG 匯出後仍重現 IF 關閉，排除截圖錯誤是遊戲阻塞的原因。平台參考全文與 SHA-256 已保存於 `workplace/platform-reference/`。據此先通過 READY 審查，再執行下列整合測試與原版重跑。

修正後驗證：`workplace/queue-test-after.txt` 的 DOS 與 machine 套件通過，包含兩個原先失敗的時鐘案例。`probe-startup-if-2m` 在相同兩百萬步已有 3 次 IRQ0，DOS 時間由零進至 16 個百分之一秒。此時恰停在 DOS 中斷處理內，採樣 IF=false 不表示入口仍錯；實際 IRQ0 次數與時間才是進展證據。`probe-startup-if-40m` 經原有 `SF.COM` 自行 EXEC `SF.EXE`，進入 13h 標題選單；原始檔未變。選角確認、完整對戰與精確時序不在本規格的 CONFORMED 範圍。

## 限制

本契約不證明 `SF.COM` 的所有用途、COMMAND.COM 完整相容性、原版對戰、音訊或手把已完成。第一份失敗另含不適用文字模式的 PNG 匯出錯誤，須保留原收據並以修正後收據工具乾淨重跑。
