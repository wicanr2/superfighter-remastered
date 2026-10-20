# 028：子彈勝利姿態與文字

狀態：CONFORMED，限定第一人正常首勝取樣、文字及下一回合清除。日期：2026-10-20。`workplace/bullet-victory-evidence-review.json` 綁定 DRAFT、候選 Go 讀取與五張正常診斷畫格的獨立來源重組。沿用[獨立 WIN 來源](017-victory-pose-banks.md)、[勝負文字](016-hd-victory-messages.md)與[子彈一般姿態](020-bullet-hd.md)。第二人、完整動畫及特殊勝負另驗。

## 原始證據

- 固定 SF.EXE SHA-256 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`，NAME.XBB SHA-256 `60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82`，執行器身分沿 `workplace/dosgolem-patched-manifest.json`。
- 已證實於原檔：CCWIN.FIG SHA-256 `1fcf7dda4b8d78e706497f83e188c97890d6d5f17c8e6c65f82088d7b3e28402`，檔案偏移 60h 的 72 入口、180h 圖像基底，四組不同 bytes。各組來源、別名、尺寸及完整 SHA 在 `workplace/bullet-victory-source-v1/manifest.json`。工具為 Pillow 11.3.0，這些是檔案偏移，與 runtime 位址分開。
- 原圖顯示兜帽防備至露出金髮的四組姿態。`bullet-victory-core-diagnostic-v1` 已由正常 2／4 選角、普通方向與拳取得第一人勝利：生命 124／0、計時 51、winner word 0002h。WIN 來源取樣槽 0／2／3，槽 1 只有原檔證據；下一回合快照清空並顯示 1／0 勝場。這是單核心診斷，不能宣稱觀測不改狀態。
- 正常字圖 consumer：BULLET 為 NAME 槽 2、runtime caller IP 39DCh、source SI 05C8h、矩形 (109,54,62,11)；WIN 為槽 17、caller IP 39F9h、SI 368Ch、矩形 (180,54,31,11)。完整來源及 SHA 在凍結快照；獨立重組審查後才升 READY。

## 候選與接入契約

四格透明候選使用內建 imagegen，原 PNG 為 2172×724，SHA-256 `40e9ecc471cb8c1ba71016deba7ceaf70cb1d90bf3e26f4147101a6e168d70d5`。保留藍紫兜帽運動服、黃條紋、白手部包覆、白靴及原露出金髮的動作。精確請求、來源圖及嚴格透明矩形保存在 `workplace/bullet-victory-art-v1`，未改生成 PNG bytes。

候選 `hd-characters-bullet-victory-v1` 沿版本 3，保留舊 949 鍵及 58 PNG，新增角色 2 的 72 個 `source_bank=victory` 入口與一張 PNG，共 1021 鍵／59 PNG／十四份來源。一般來源、色盤及幾何選擇不變；來源未知、缺件與不支援色盤仍整格原貌。設定保存、原版姿態、碰撞、勝負及速度不因 HD 改動。

正常來源、候選 Go 讀取及勝負字圖審查後才升 READY，之後加入 BULLET 勝負姓名白名單。原始資料 → WIN 表辨識 → typed Sprite／VictoryState → 嚴格選擇 → GPU → 暫停切換及下一回合清除需完整驗證。

## 驗收

1. 四組原檔與候選透明矩形、72 入口、舊 949 鍵與 PNG 不變，Go 嚴格讀取通過。
2. 普通方向及拳鍵取得正常 2／4 首勝，完整原檔重組，查實際 WIN 姿態、姓名與勝負狀態；不注入生命、勝負或座標。
3. READY 後正常成對核心驗觀測不改狀態／RGB，正常 Linux／Wine 各七張驗首勝、同狀態切換及下一回合清除。使用缺子彈 WIN 的舊群組驗一般 HD、勝利整格原貌及下一回合恢復。
4. 真實字圖、完整程式測試及四平台精確編譯來源通過。Wine 或其他案例未達完整門檻時保留 READY，不以 partial 冒充 CONFORMED。

原版、衍生美術、私有執行器及收據只留本機；Git 保存自有程式與文件。

## 驗證結果

`bullet-victory-core-v1` 以正常 2／4 普通方向與拳，取得首勝及下一回合。6,018 個成對比較邊界的狀態與即時 RGB 相同；11 個 WIN 取樣含槽 0／2／3，五個保存畫格由原檔獨立重組。槽 1 仍只有靜態來源，不宣稱完整動畫。

`native-bullet-victory-v1`／`windows-bullet-victory-v1` 各七張，正常擊倒、BULLET WIN、同狀態切換及下一回合清除全部通過。各案例內恢復 HD 逐點一致，兩張勝負 GPU 字圖各 5,109 點變動、1,552 點金色實心；寫入限制在原字圖矩形，造型與字形另目視。不是跨平台同狀態比較。

`native-bullet-victory-missing-v1` 使用缺子彈 WIN 的 949 鍵群組，七張核對通過：一般對戰與下一回合可 HD，勝利整格原貌。Go 真實字圖及來源拒絕、完整程式測試與 vet、四個二進位的 37 份實際編譯輸入通過。移入記錄為 `bullet-victory-build-v1/promotion.json`；舊印第安喬四份保留於 `joe-build-v1/bin`。
