# 029：多場景 HD 背景與道場

現況：正式載入與呈現已依 [049](049-hd-batch-integration.md)接入，集中驗證中。本檔保留原型形成時的來源與限制；當時 DRAFT 的載入／視覺決策由 049 統合，不再視為未接入。

## 已有來源與候選

- 屋頂沿[規格 006](006-rooftop-background.md)及[顯示映射](015-native-scanout.md)：I2.XGB、scene 4、480×204；現行原包及原 PNG 保持不變。
- 道場 I5.XGB SHA-256 `44d8adf7662c46396092581175fd0b85ca7179b9f99fe9c66b680f0ff50a9b61`，480×204，像素 SHA-256 `71c366851b72c14b1871906a42f8746fead325a26e4ee25a166b5232fb02c3ae`。Go 1.24.13 的 `hd-frame-dojo-v1` 正常 0／0 選角，在 runtime 01B9:5DD3 取 124 格，scene 0、camera 80–145；背景 RAM、兩人 packed bytes 與八份原背景色盤均吻合，已證實於取樣。
- 內建 imagegen 候選 1922×818 原 PNG SHA-256 `68a8e64e6e4dc47e61fa52f43e78471a855f6a86e2e8913ba92f13439a3db11b`，保留暖色道場、樑柱、紙窗、空曠前景與三名遠景練武者。精確請求及原 bytes 在 `workplace/dojo-art-v1`；來源審查在 `workplace/dojo-source-review-v1.json`。尚未當作原生接入成果。

## 提議的資料與呈現契約

新版根清單以版本 2 的 `background-collection` 列出子目錄，各子目錄保存單一背景清單、原色號、色盤及 HD PNG。第一包含屋頂與道場；舊版本 1 屋頂包可直接載入，無須轉檔或覆寫。

```json
{"version":2,"kind":"background-collection","backgrounds":["rooftop","dojo"]}
```

- 每個子目錄只有一層相對名稱，拒絕跳脫、符號連結、重複來源、未知欄位與過量成員。任何必要檔案損壞即拒絕整個包，顯示完整原貌。
- 子背景沿現有單景欄位。道場新增已登錄的來源／scene／完整 RAM 雜湊，仍逐格核對原色盤、camera、顯示映射及可見尾列，不由角色或畫面相似度猜場景。
- 原生依每份完整快照選匹配背景。未知場景或未支援狀態整格原貌；角色、陰影、介面及訊息使用同一份來源與背景選擇，不出現半套畫面。
- 只改呈現及本機 HD 素材格式，原版狀態、遊戲規則、速度、輸入、快捷與設定保存不改。原貌模式仍為同格原版。

## 確認後的驗收閘門

1. 審核 124 格正常來源、八份色盤及候選構圖。原版 EXE 與執行器來源沿現行固定身分，不修改共用來源。
2. Go 嚴格讀取兩種包，驗舊屋頂包相容、來源／色盤／尾列／成員損壞拒絕與未知場景回退。
3. READY 後才接入呈現。Linux／Wine 由正常入口選 0／0 道場，驗動作、完整圖層、同狀態切換及缺件原貌。屋頂另抽測，不能只驗新背景。
4. 完整程式測試、精確編譯來源與四平台二進位通過後才移入目前 bin。只驗屋頂及道場，不外推其餘九份 XGB 或完整 HD。

候選、原版與衍生美術只留本機，不加入 Git 或一般發行包。Git 保存自有程式與規格。

## 後續來源補證

使用者後續授權 HD 生成素材收錄 repo，取代上段僅留本機的候選保存限制。原版、原圖、色盤與 raw 收據仍不公開；素材保存不表示已同意本草案的 JSON 格式。

`workplace/stage-source-v1` 由 Go 1.24.13 與固定 dosgolem 副本，正常選第一人斬、逐一選第二人 0..10，再作二十格普通行走。原始 SF.EXE 及 128 檔身分沿 CONTEXT；runtime manifest SHA 為 d79cc85bc1ce29dbe54c19e7857a9ac07b2e3a1754fb342632ead9e36e619fc3。tools/stage_source_receipt.go 為只讀診斷，不新增正式載入格式。

已證實於這二十二份取樣：十一份原 XGB 均為 480×204，表頭後 escape RLE 位於實檔 306h，escape 值位於 305h；原色盤從實檔 5 起讀前 128 色。每景完整 RAM 雜湊、原色盤及 camera 80／105 的 320×200 背景裁切吻合原檔，正常顯示快照亦吻合。獨立 Python 解碼及逐點裁切核對在 source-comparison.json，且 43 份 production 輸入與已驗 037 建置相同。

| 第二人索引 | runtime scene | 原檔 | 首輪稿 |
|---:|---:|---|---|
| 0 | 0 | I5.XGB | 道場 |
| 1 | 1 | I12.XGB | 冰原候選 |
| 2 | 2 | I4.XGB | 街道候選 |
| 3 | 3 | I7.XGB | 宮殿候選 |
| 4 | 4 | I2.XGB | 已接屋頂 |
| 5 | 5 | I3.XGB | 叢林候選 |
| 6 | 6 | I10.XGB | 石窟候選 |
| 7 | 7 | I9.XGB | 港口候選 |
| 8 | 8 | I8.XGB | 舞廳候選 |
| 9 | 9 | I1.XGB | 廳堂候選 |
| 10 | 10 | I13.XGB | 火車候選 |

此表為普通雙打來源證據，不外推單打對手／場景順序、全部 camera、HD 構圖或新背景原生接入。新增九景生成原圖與精確提示詞見 assets/hd/candidates/README.md／backgrounds-source.json，尺寸約 1920×818；小字及群像仍需複核。多場景格式選擇仍待使用者回答，029 保持 DRAFT。

## 獨立捲動比較

格式確認前可繼續正常來源及可丟棄比較。background_scroll_receipt.go 以普通雙打選角及雙人左右行走保存完整 CPU 圖層、顯示快照、色盤與相機取樣；背景仍逐格對應原 XGB。background_scroll_preview.py 另核對原檔及前景重組，並以同一相機／顯示起點裁出候選背景，保留原版人物及介面供構圖比較。比較稿留本機，不改原 PNG 或正式呈現，不當作全景 HD 已接入、原生 GPU 或全部相機位置的證據。


### 捲動取樣與視覺複核結果

background-scroll-v1 正常選第一人斬、第二人逐一 0..10。兩人同時左行 96 格、右行 192 格，每景保存八份，共 88 格；各景均觀察到相機 0／159。這是實際觀察集合，並未覆蓋每一個整數相機位置。輸入清除後立即保存的 released 不當作已輪詢中立的證據，未驗放開延遲。

獨立 Python 直接解碼原 XGB、逐點核對背景裁切與全色盤、六層 RAM 重組及 176 份角色 packed 原檔／CPU 覆蓋，並由 CRTC 與完整尾端核對顯示視窗。全部來源通過。background-scroll-preview-v1／v2 各保存 88 張原版／候選比較；以同格相機及顯示起點裁圖，HD 只換背景，人物／陰影／介面仍為原版。這是雙線性全景的軟體比較，不是正式 GPU、全 HD 或完整動畫驗收。

已看十一景全景及各景右端、火車左端，另看石窟／舞廳修稿的原 PNG 及右端比較。首稿石窟欄杆／地板與舞廳舞台／地板交界偏高；兩份內建 imagegen 修稿依原圖改善，仍需構圖複核，另存 v2 原 PNG，沒有覆寫首稿。街道塗鴉字形不同仍待修。原版參考只留本機，修稿與精確提示詞收錄 assets/hd/candidates/background-revisions-source.json。029 仍 DRAFT，沒有因來源或候選比較通過就跳過格式確認或原生接入。

### 街道上排塗鴉修稿

街道另存 [street-i4-v2.png](../../assets/hd/candidates/street-i4-v2.png)，1922×818，生成原 SHA-256 `a44e25713aeced5017d05bbbaad2613fb46674695290d9b8f6ef37c8a425b6bd`。使用內建 image_gen，精確請求與父圖／原檔身分見 [street-revision-source.json](../../assets/hd/candidates/street-revision-source.json)。上排現在可辨讀 SUPER STAR；這是對原塗鴉字形的強推論，沒有從遊戲字串解出。第一張修稿仍未修正字形，留在 workplace/street-revision-v1/rejected-first.png，不加入正式候選清單。

生成式編輯也重畫了文字區外的像素，整圖差異範圍為全幅；區外每色平均絕對差約 9.1–10.2。沒有宣稱原構圖或其他像素完全相同，也不覆寫原 street-i4.png。下方塗鴉及全景細節仍待定版。

`tools/background_scroll_preview.py --scene 2 --street-revision` 只複核本次街道，輸出在 workplace/street-scroll-preview-v1。八份正常取樣、十六個原角色層、原 XGB／色盤／完整層／顯示尾列核對通過；相機兩端 0／159 的比較已目視。這是以同一原相機裁圖、保留原版前景的軟體比較，沒有新增原生背景路徑或正式載入格式。原十一景證據及其餘原稿保持，029 仍 DRAFT，正式接入等待先前格式選擇。
