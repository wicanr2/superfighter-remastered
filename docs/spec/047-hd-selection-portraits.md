# 047：選角肖像 HD 候選

狀態：DRAFT。沿已確認的 B 街機手繪方向，補齊選角肖像美術；本項先保存候選，不更動正式選角、角色導航、資料格式或原版規則。

## 來源與範圍

原檔為 BIGFIG.XBB，固定版本及原消費端沿 [025](025-boss-selection.md)。原檔有十一筆 21F1h bytes，前 60h 為三十二個六位元 RGB 色，肖像色號位於每筆 300h 起，恰為 89×89。這些數值為原檔偏移，不與 IDA MZ linear 或 runtime 01B9:IP 混用。原 `sub_10E86` 的 SI 前進順序與兩側鏡像／定位已由 025 核對，不重新逆向無關 helper。

BIGFIG.XBB SHA-256 為 `4897b865c3fef8fd1c788ec5e32226de7086dbd8ff1987a5efc62ea15bd29477`。工具版本為 Pillow 11.3.0，UID 1000、無網路的既有 Docker；生成採內建 image_gen，工具未公開底層模型版本。

[匯出工具](../../tools/export_selection_portraits.py)核對原檔 SHA、完整長度、十一個角色識別字、色號與色盤界限，輸出只在 workplace。原肖像及原色盤不加入 Git。匯出是素材參考，不取代已驗正常選角或新增正常玩家路徑證據。

本輪候選以原肖像的臉、髮型、表情、衣著配色、朝向與構圖為準，產出真正高解析重繪。不得從一般動作圖裁一個臉就宣稱完成，也不以檔名代替角色身分。每張保存生成原 bytes、精確提示詞、來源 SHA、尺寸與審查限制。生成式重繪是美術近似，不稱逐像素原版 parity。

## 首輪十一人候選

十一張生成原 PNG 均為 1254×1254、完整不透明，已保存於既有候選目錄，沒有另造執行期資料格式。斬先作畫風參照，其餘十張仍各自以自己的原肖像控制角色身分，斬圖只控制筆觸。精確提示詞、原檔偏移／色號／色盤雜湊及輸出身分見 [來源清單](../../assets/hd/candidates/selection-portraits-source.json)。

| 角色 | 已保存候選 | 目視特徵與待複核處 |
|---|---|---|
| 斬 | [肖像](../../assets/hd/candidates/selection-jaan-v1.png) | 方形平頭、灰白髮紋與黑邊白服；頭部與頸部比例仍是重繪近似 |
| 薩爾可夫 | [肖像](../../assets/hd/candidates/selection-sarkov-v1.png) | 光頭、長鬍、咬牙及紅巾；鬍鬚量感與尖端形狀待複核 |
| 子彈 | [肖像](../../assets/hd/candidates/selection-bullet-v1.png) | 藍黃兜帽、金色瀏海與抬拳；瀏海遮眼程度及拳頭比例待複核 |
| 鳳凰 | [肖像](../../assets/hd/candidates/selection-phoenix-v1.png) | 棕髮、回首與紫紅黃邊衣服；髮量、肩部及五官比例為近似 |
| 法蘭克 | [肖像](../../assets/hd/candidates/selection-frank-v1.png) | 長銀髮、鬍渣、微笑與青藍衣緣；髮束及鬍渣細節為重繪 |
| 鬼丸 | [肖像](../../assets/hd/candidates/selection-onimaru-v1.png) | 灰綠面部、金屬板、黃眼、紫色頭罩；面部與金屬板比例待複核 |
| 嵐 | [肖像](../../assets/hd/candidates/selection-lan-v1.png) | 棕色短髮及紅色高領；臉型、髮束及神情仍待定版 |
| 金太極 | [肖像](../../assets/hd/candidates/selection-kim-v1.png) | 前額禿頂、後掠黑髮、大金環及側面咬牙；耳環大小與邊界裁切待驗 |
| 蜘蛛女 | [肖像](../../assets/hd/candidates/selection-spider-v1.png) | 金髮、紫色臉部彩繪及抬顎；彩繪邊界為近似，只含臉／髮／頸，不是戰鬥動作圖 |
| 小丑 | [肖像](../../assets/hd/candidates/selection-clown-v1.png) | 圓禿頭、厚下顎、斜笑與頸前辮子；左緣辮梢／裝飾細節待複核 |
| 印第安喬 | [肖像](../../assets/hd/candidates/selection-joe-v1.png) | 紅白臉部圖樣、長鼻與怒吼；頭飾及齒形細節為重繪近似，待複核 |

[純 HD 候選接觸圖](../screenshots/selection-portrait-candidates.png)已目視；原圖與候選並列圖只留 `workplace/selection-portrait-import-v1/original-vs-candidate.png`。這是素材預覽，未把生成圖包裝成正常原生選角擷取。

[獨立核對](../../tools/verify_selection_portraits.py)直接由原 BIGFIG bytes 逐張重建 RGB，十一張原參考均相同，角色順序、原偏移與雜湊全部吻合。十一張候選的原 PNG、尺寸、不透明度、catalog 對應與純 HD 預覽來源通過；舊 119 筆素材保持。檔案核對不證明臉部完全忠實、版面定版、原生接入或完整 HD。正式程式、1516 個角色鍵、四平台二進位與首版包保持。

## 隔離原生原型

[準備／建置工具](../../tools/prepare_selection_native_prototype.py)只在 `workplace/selection-native-prototype-v2/source` 複製正式來源並套用[繪圖模板](../../tools/selection-native-prototype/desktop.go.in)。Go 1.24.13 的 Linux 原型 SHA-256 為 `cde6e389e4aacb6141e9d5d62192925e9ee540f55f0778a757f2d90623b396ad`，85 份副本檔案與原 46 份編譯輸入綁定在 recipe.json／build.json。沒有改正式 `internal/`、API、設定、素材格式、bin 或發布版。

原型沿既有選角生命週期、獨立過濾顯示影本與原 BIGFIG，核對 `(11,15)` 左側 89×89、右側 x=214..302／y=15..103 的鏡像寫入範圍、完整色號及三十二色原色盤。主動選取側須符合原游標；第二人期間左側也須有有效來源。繪製中間狀態或未知來源保持原貌，不重播舊畫格。GPU 大肖像矩形為 `[113,109,380,376)`／`[722,109,989,376)`，其餘背景、VS、八人原縮圖、十一人前端按鈕及導航保留。

只由 `KDZZ_SELECTION_PROTOTYPE_ART` 啟用候選；未設定時仍核對來源，但完全保留選角原貌。原型固定候選來源清單 SHA `991062cb63228d03458208da002a205487544d99753756f1e1eb41a2216517a3` 與各 PNG，不把這個私人實驗載入方式當成已確認的正式格式。這是原位置的大肖像比較，不代表完整選角 HD 或新的正式版面決定。

[操作工具](../../tools/selection_native_smoke.py)只送正常 X11 鍵鼠，從完整原標題來源確認後進雙打。`selection-native-full-v3` 逐一驗兩側十一人，保存二十九張；`selection-native-fallback-v3` 未載候選，抽斬與三名魔王兩側及同組切換，保存十五張。兩條均在第二人改選法蘭克後，以原確認進入印第安喬對法蘭克的屋頂對戰，肖像覆繪清空、既有對戰 HD 恢復。沒有訓練或原角色／座標／生命／亂數注入。

[獨立核對](../../tools/verify_selection_native.py)通過六十一份原肖像色號及色盤重組、三十八份 GPU 候選身分／鏡像方向辨識，以及所有肖像框外像素逐點保持原貌。蜘蛛女第一側與印第安喬第二側的暫停切換保持核心、呈現、設定及指派，原色號／色盤相同，恢復 HD 後像素完全相同。GPU 採用 Ebitengine 的縮小取樣及 mipmap，Pillow 只用於候選身分／方向比較，不宣稱兩種採樣逐點相同。

兩個 v1 操作工作錯把第二人起始游標當成 0 而超時；實際保留第一人的 10，既有原版 probe-v3 也以第一人為基準移動，修正腳本後才重跑。managed 紋理版的 v2 正常擷取在蜘蛛女恢復時有 386 個像素、每色最多 1 的差異；原核心／原色號／色盤均相同。依 go.mod 固定 Ebitengine v2.9.9 的 `NewImageFromImageOptions.Unmanaged` 契約，隔離肖像改用獨立紋理，保留 mipmap 縮小品質；v3 的兩組恢復逐點相同。差異與自動圖集配置有關屬於強推論，沒有宣稱已證實驅動層原因或其他平台皆解決。失敗及舊程式保留，不再深挖 GPU 驅動。

四十四張擷取只證明上述 Linux 雙打原型。單打、Windows／macOS、實體手把、損壞候選及正式包尚未驗，視覺／裁切／版面與正式載入仍待決定。完整原生畫面含原版背景及縮圖，只留本機；公開接觸圖仍是純 HD 美術預覽，不換名成原生收據。047 維持 DRAFT。

## 後續閘門

1. 十一人的候選逐一檢查角色身分、臉、髮型、服裝、朝向與方形裁切，缺件與失敗明列。
2. 使用者確認選角視覺與載入契約後才審 READY，不將已生成圖片當成默認同意。既有 025 的十一人按鈕與導航保持，不能擅自改成新選角流程。
3. 正式實作必須沿原選角生命週期與可靠來源選擇，來源不符／損壞／缺件退回原貌；原貌切換保持核心、設定與輸入。
4. 正常單打與雙打分別驗第一人／第二人、原版角色／魔王、切換／恢復與確認後清除。材質、版面、正式 API、素材格式及三平台驗收仍未完成。

029 多景格式與 046 標題定版問題仍獨立等待回覆，本候選工作不代答，也不擴張首版 Release。
