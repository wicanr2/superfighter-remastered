# 031：鬼丸勝利姿態與文字

狀態：CONFORMED，限定第一人正常首勝取樣、文字及下一回合清除。日期：2026-10-20。`workplace/onimaru-victory-evidence-review.json` 綁定 DRAFT、正常來源及候選 Go 嚴格讀取，審查 SHA-256 `7d66f96c14b6707c5ea19849797201a9cdd0737ac0967f7fbf0b76d90706bee3`。沿用[鬼丸一般姿態](022-onimaru-hd.md)、[獨立 WIN 來源](017-victory-pose-banks.md)及[勝負文字](016-hd-victory-messages.md)。第二人、完整動畫及其他模式另驗。

## 已有原版證據

- 固定 SF.EXE SHA-256 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`，NAME.XBB SHA-256 `60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82`。執行器沿現行 `workplace/dosgolem-patched-manifest.json`，不改共用來源。
- GGWIN.FIG 共 12,362 bytes，SHA-256 `2ec882c5a3827d249c8048ef33c0604c4b5be2b5626e37ed3db5ae1bd78ec233`。檔案偏移 60h 指標表、180h 圖像基底，72 個入口對應四組 bytes。來源偏移為 384、2329、4274、8076，尺寸依序 58×67、58×67、76×100、83×102。來源、別名與參考圖保存於 `workplace/onimaru-victory-source-v1/manifest.json`，沿先前 remaining-victory-source-v1，工具為 Pillow 11.3.0，已證實於原檔。
- Go 1.24.13 的 `onimaru-victory-core-diagnostic-v1` 以正常 5／4 選角、普通方向與拳取得首勝，生命 124／0、計時 56、winner word 0005h。五個保存畫格與 29 個 WIN 取樣已由原檔重組，取樣槽 0／2／3，下一回合快照清空，槽 1 只具靜態證據。這是單核心來源診斷，不宣稱觀測不改原版狀態。
- 正常勝負姓名 ONIMALU／NAME 槽 5、runtime caller IP 39DCh、SI 0EC9h、矩形 (104,54,72,11)；WIN／槽 17、caller IP 39F9h、SI 368Ch、矩形 (185,54,31,11)。完整原字圖與來源已與凍結快照獨立重組，實檔與 runtime 定位分開記錄。
- 原圖正常色盤為 SFMAN06 的 AC8h 前 48 bytes，等於 GGWIN 前 48 bytes，正常首勝讀取 palette_base C0h，已證實於凍結快照。GGWIN header 的 78–95 bytes 與一般第二色盤不同，本切片不用該區作正常色盤契約。準備工具先前誤比較整個 96-byte header，後又誤比色盤索引 0；兩項假設均已由正常快照的 C0h 定位否定，沒有修改原版或降低來源檢查。

## 候選與接入範圍

四格透明圖集沿原 WIN 的兩種彎腰扶杖姿態、舉杖與舉臂姿態。沿用現有 HD 的綠灰皮膚、禿頭、紫色眼睛、紫衣橘金邊、橘褐木杖、木製義足與另一腳白色綁帶。不變更原動作、造型決定、碰撞、傷害、速度或輸入。

內建 imagegen 的 2172×724 原 PNG SHA-256 `e5e7b4295c74f9857dc2fb9883cfbf1fb94c0d35bddeef385c16d6f51f463984`，精確請求、透明矩形與原 bytes 保存在 `workplace/onimaru-victory-art-v1`。四格經透明分隔與外緣檢查，未修改 PNG。

候選 `hd-characters-onimaru-victory-v1` 保留已驗的 1093 鍵與 60 PNG，只新增角色 5 的 72 個 `source_bank=victory` 入口與一張 PNG，共 1165 鍵／61 PNG／十六來源。使用現有版本 3 角色格式，不涉及 029 的多場景格式。缺件、未知來源或未支援色盤沿既有整格原貌回退。

只有正常來源、字圖與候選讀取審查通過後才升 READY，再加入 ONIMALU 勝負姓名。垂直鏈為原 WIN 檔 → 指標及來源鍵 → typed Sprite／VictoryState → 嚴格選擇 → GPU → 同狀態切換與下一回合清除。既有設定與保存不變。

## 驗收閘門

1. 四組原圖、透明矩形、72 入口、舊包不變及 Go 嚴格讀取通過。
2. 普通選角、方向與拳取得首勝，獨立重組原圖與 ONIMALU／WIN 字圖，核對下一回合清除；不注入生命、座標、勝負或亂數結果。
3. READY 後以成對核心驗原狀態及即時 RGB 不變。Linux／Wine 各七張正常首勝、切換與下一回合通過；缺鬼丸 WIN 的舊包另驗勝利整格原貌及下一回合恢復。
4. 真實字圖與來源拒絕、完整程式測試／vet、四平台精確編譯來源通過後才移入目前 bin。部分結果保留 READY，不稱 CONFORMED。

生成 PNG 與清單依使用者的 HD 上傳授權收錄 `assets/hd/`。原版、參考色號／色盤、原圖、私有執行器及含原版內容的研究收據仍留本機。候選不等於正常接入或完整 HD 完成。

## 驗證結果

`onimaru-victory-core-v1` 完成 12,272 個成對邊界，原狀態與即時 RGB 相同。29 個 WIN 取樣及五個保存畫格通過原檔獨立重組，取樣槽 0／2／3；槽 1 保留靜態證據，不稱完整動畫。

`native-onimaru-victory-v1`／`windows-onimaru-victory-v1` 各七張完整通過，普通輸入取得首勝，ONIMALU WIN、同狀態切換、恢復逐點一致及下一回合清除均已核對。兩平台各案例內 GPU 字圖變動 5,943 點、金色實心 1,701 點，寫入限制在原字圖矩形，另目視人物、字形及原貌；不稱跨平台同狀態。

`native-onimaru-victory-missing-v1` 使用缺鬼丸 WIN 的 1093 鍵群組，七張驗勝利整格原貌與下一回合恢復 HD。真實字圖、錯來源拒絕、全部 internal／cmd 測試及 go vet 通過，完整結果在 `onimaru-victory-checks-v3.log`。v1 的舊格式測資錯誤及 v2 的 signal:killed 原檔均保留。v3 只設定測試環境 GOMEMLIMIT=1GiB，容器仍限 1.5GiB，記憶體事件沒有 OOM；未修改產品規則或正式執行參數。

四份 ELF／PE／兩種 Mach-O 均核對 37 份實際編譯輸入。移入目前 bin 的收據為 `onimaru-victory-build-v1/promotion.json`，前版四份及原收據保留於 `phoenix-victory-build-v1/bin`。Windows Wine 不代替 Windows／macOS 真機或實體手把驗收。
