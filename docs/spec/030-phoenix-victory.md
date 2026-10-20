# 030：鳳凰勝利姿態與文字

狀態：CONFORMED，限定第一人正常首勝取樣、文字及下一回合清除。日期：2026-10-20。`workplace/phoenix-victory-evidence-review.json` 綁定 DRAFT、候選 Go 讀取、四張診斷來源與八個 WIN 取樣的獨立重組。沿用[鳳凰一般姿態](021-phoenix-hd.md)、[獨立 WIN 來源](017-victory-pose-banks.md)與[勝負文字](016-hd-victory-messages.md)。第二人與完整動畫另驗。

## 原版證據

- 固定 SF.EXE SHA-256 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`，NAME.XBB SHA-256 `60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82`，執行器沿現行 `dosgolem-patched-manifest.json`。
- EEWIN.FIG 共 6,279 bytes，SHA-256 `65f8536cdd3ba96c63d116df5c701b401776e39643fb5fb10c790ac1fdeb2a8c`；檔案偏移 60h 表、180h 圖像基底，72 個入口對應三組 bytes。前 96 bytes 等於 SFMAN04 的 AC8h 正常色盤，已證實於原檔。完整來源及別名在 `workplace/phoenix-victory-source-v1/manifest.json`，工具 Pillow 11.3.0。
- `phoenix-victory-core-diagnostic-v1` 經正常 3／4 選角、普通方向與拳取得首勝，生命 124／0、計時 51、winner word 0003h，下一回合快照清空。這是 Go 1.24.13 單核心來源診斷，不宣稱觀測不改原版狀態。
- 正常勝負字圖 PHO HUANG／NAME 槽 3、runtime caller IP 39DCh、SI 0874h、矩形 (94,54,93,11)；WIN／槽 17、caller IP 39F9h、SI 368Ch、矩形 (196,54,31,11)。完整原字圖與來源保留於凍結快照，與上方實檔偏移分開記錄；來源重組尚待審查。

## 候選契約

三格透明候選沿原圖的兩種防備與直身抱拳動作，保留褐髮長辮、桃紅衣、金邊與腰帶、白色手腳包覆及桃紅平鞋。內建 imagegen 的 2172×724 原 PNG SHA-256 `c4c2ba8fdefb79d0041639e958338777bf68264caa2e62d1371ff421d3119556`，精確請求及未改動的原 bytes 在 `workplace/phoenix-victory-art-v1`。

候選 `hd-characters-phoenix-victory-v1` 沿版本 3，保留舊 1021 鍵及 59 PNG，新增角色 3 的 72 個 `source_bank=victory` 入口與一張 PNG，共 1093 鍵／60 PNG／十五來源。未知來源、缺件或未支援色盤仍整格原貌；原版規則、速度、勝負、輸入與設定不改。

正常來源、候選 Go 讀取與字圖審查後才升 READY，再接 PHO HUANG 勝負姓名。一般 HUD 沿 021。原始資料 → WIN 表辨識 → typed Sprite／VictoryState → 嚴格選擇 → GPU → 暫停切換及下一回合清除需完整驗證。

## 驗收

1. 三組原檔與候選透明矩形、72 入口、舊 1021 鍵及 PNG 不變，Go 嚴格讀取通過。
2. 普通方向與拳取得正常首勝，完整原檔重組，核對 WIN 姿態、PHO HUANG／WIN 與下一回合清除，不注入生命、勝負、座標或亂數結果。
3. READY 後成對核心驗狀態／即時 RGB 不變；正常 Linux／Wine 各七張驗首勝、同狀態切換與下一回合清除。缺鳳凰 WIN 的舊群組另驗勝利整格原貌及下一回合恢復。
4. 真實字圖與拒絕、完整程式測試／vet、四平台精確編譯來源通過。未達完整原生閘門時保留 READY，不以 partial 當 CONFORMED。

原版、衍生美術與研究收據只留本機，Git 保存自有程式與文件。

## 驗證結果

`phoenix-victory-core-v1` 正常首勝及下一回合完成 5,952 個成對邊界，狀態與即時 RGB 相同；八個 WIN 取樣含槽 0／2，四個保存畫格由原檔獨立重組。槽 1 只有靜態來源，不稱完整動畫。

`native-phoenix-victory-v1`／`windows-phoenix-victory-v1` 各七張，正常擊倒、PHO HUANG WIN、同狀態切換及下一回合清除通過。每個案例內恢復 HD 逐點一致；兩張 GPU 勝負字圖各 6,881 點變動、1,970 點金色實心，寫入限制在原字圖矩形，另目視造型與字形。不是跨平台同狀態比較。

`native-phoenix-victory-missing-v1` 使用缺鳳凰 WIN 的 1021 鍵群組，七張核對通過：一般對戰與下一回合可 HD，勝利整格原貌。Go 真實原字圖及錯來源拒絕、完整程式測試／vet、四平台的 37 份精確編譯輸入通過。移入收據為 `phoenix-victory-build-v1/promotion.json`，舊子彈首勝四份保留於 `bullet-victory-build-v1/bin`。
