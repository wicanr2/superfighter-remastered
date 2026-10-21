# HD 素材

本目錄保存生成原 PNG、角色圖集、精確提示詞與來源對照。使用者已授權將 HD 素材保存到儲存庫。原版 EXE、DAT、FIG、原圖、色號、色盤與記憶體收據仍只留本機。

正式接入依 [049](../../docs/spec/049-hd-batch-integration.md)。目前共 145 張 PNG、78 張啟用角色／特效圖集、1630 個角色鍵與 33 份介面圖像。四張蜘蛛女新圖集已採使用者選定的 B 版連身衣；素材數量不等於全部動畫已驗。

| 素材 | 正式用途與來源 |
|---|---|
| [角色清單](characters/manifest.json) | 十一人的一般／WIN 與既有特效；完整範圍見 [CONTEXT](../../CONTEXT.md) |
| [畫面清單](screens.json) | 標題人物／字標、VS、十一人正常／敗者肖像、報紙與七旗。缺少任一必要圖即整組拒絕 |
| [十一景身分](../../internal/hd/background-sources.json) | 屋頂、道場及其餘九景；記錄原來源 SHA、原色號／色盤 SHA 與 HD 圖 SHA，不保存原像素 |
| [屋頂](backgrounds/rooftop.png)、[道場與九景來源](candidates/README.md) | 已接同一背景集合；執行時由玩家原檔建立本機參考，不隨發行包帶入原版色號 |
| [街道](candidates/street-i4-v2.png)、[精確提示詞](candidates/street-revision-source.json) | 正式採用修稿；塗鴉與構圖仍是手繪近似 |
| [石窟](candidates/grotto-i10-v2.png)、[舞廳](candidates/auditorium-i8-v2.png)、[提示詞](candidates/background-revisions-source.json) | 正式採用底線修稿，舊生成圖仍保留 |
| [標題來源](candidates/title-source.json) | HD 人物、紅金字標與原按鈕位置。八相位材質投影是美術效果，設定頁保持原貌 |
| [選角肖像](candidates/selection-portraits-source.json)、[VS](candidates/selection-vs-source.json) | 十一人兩側大肖像、右側鏡像、VS、八格縮圖及重畫邊框；三魔王仍用既有姓名按鈕 |
| [結果底圖](candidates/result-source.json)、[敗者肖像](candidates/result-portraits-source.json)、[旗幟](candidates/result-flags-source.json) | 已接結果報紙與單打再戰／放棄，保留玩家位置與原狀態；細字、傷勢、徽記與字型為近似 |
| [蜘蛛女低伏來源](characters/spider-low-guard-source.json) | 使用者已確認的外部稿，無損鏡像及裁切；舊低伏服裝已由使用者選定的 B 版取代，保留作製作紀錄 |
| [蜘蛛女完整 B 版](characters/spider-complete-source.json) | 四張新連身衣原稿、透明拆格圖集、45 組一般／5 組 WIN 來源對照。使用者已選 B 並晉升，144 入口採同服裝，基底朝左與原 DAT 相符，由原 flags 決定鏡像 |
| [蜘蛛女外部稿](candidates/spider/README.md) | 十五張外部模型圖及去背紀錄；檔名不代表已驗姿態對照 |
| [金太極光效](characters/kim-effects-source.json)、[四人特殊技](characters/remaining-special-effects-source.json) | 保留生成原圖及精確提示詞；正常動作、色盤與回退範圍見規格 [042](../../docs/spec/042-kim-effects.md)／[044](../../docs/spec/044-remaining-special-effects.md) |
| [catalog.json](catalog.json) | 172 筆收錄檔案的 SHA-256、大小、尺寸及狀態；不含原版圖像資料 |

生成原 PNG 保留原 bytes。蜘蛛女候選另以本機透明拆格處理，記錄 alpha 門檻、裁切與圖集矩形；原稿與處理結果的雜湊分開保存。原檔名、位移與圖像雜湊只作來源定位，不公開原圖。

引擎封包只收錄正式角色清單實際引用的圖集，以及十一景與畫面清單引用的 HD 圖。未選的候選保存在儲存庫作製作紀錄。程式由封包旁 `assets/hd/` 自動發現；自訂目錄可用 `-hd-assets`、`-hd-characters`、`-hd-screens`。建置與資料匯入見[主 README](../../README.md)。

上傳授權不代表取得原作的公開散布權。本專案程式授權不涵蓋原作角色、場景或第三方來源。原版資料與原曲影片只留本機，Release 排除原版遊戲。
