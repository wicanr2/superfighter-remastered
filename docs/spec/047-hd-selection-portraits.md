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

## 後續閘門

1. 十一人的候選逐一檢查角色身分、臉、髮型、服裝、朝向與方形裁切，缺件與失敗明列。
2. 使用者確認選角視覺與載入契約後才審 READY，不將已生成圖片當成默認同意。既有 025 的十一人按鈕與導航保持，不能擅自改成新選角流程。
3. 正式實作必須沿原選角生命週期與可靠來源選擇，來源不符／損壞／缺件退回原貌；原貌切換保持核心、設定與輸入。
4. 正常單打與雙打分別驗第一人／第二人、原版角色／魔王、切換／恢復與確認後清除。材質、版面、正式 API、素材格式及三平台驗收仍未完成。

029 多景格式與 046 標題定版問題仍獨立等待回覆，本候選工作不代答，也不擴張首版 Release。
