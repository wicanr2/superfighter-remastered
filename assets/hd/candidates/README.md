# HD 候選素材

目前接入以 [049](../../../docs/spec/049-hd-batch-integration.md)與[素材現況](../README.md)為準。十一景、標題、十一人選角肖像、VS、結果報紙、敗者肖像與七旗已進正式載入。街道、石窟、舞廳採 v2 修稿；選角保留八格及既有十一人姓名按鈕。

蜘蛛女四張 `spider-covered-v3-*.png` 原稿與透明圖集已保存，[完整來源及提示詞](../characters/spider-complete-source.json)可回查。使用者已選 B 全覆蓋連身衣，144 個一般／WIN 入口已進正式清單，原 PNG 保持。

## 素材製作紀錄

以下保留各批產生時的來源與原型紀錄；其中「未接入」描述當時狀態，現況由上方入口統一維護。


本目錄保存候選與來源資訊。是否已接入遊戲，以本表及[目前狀態](../../../CONTEXT.md)為準。

| 素材 | 來源與提示詞 | 狀態 |
|---|---|---|
| [七面結果旗幟向量總覽](../../../docs/screenshots/result-flag-candidates.png) | [來源與幾何紀錄](result-flags-source.json)，七組 SVG／1300×660 PNG；使用專案向量程式，沒有圖片模型提示詞 | 048 DRAFT，保留原配色與配置，形狀／徽記為向量近似；未接原生或正式載入 |
| [十一人敗者肖像總覽](../../../docs/screenshots/result-portrait-candidates.png) | [來源與完整提示詞](result-portraits-source.json)，十張新原 PNG 加首輪法蘭克，原檔偏移與參照逐人記錄 | [正常原生取樣](../../../docs/screenshots/result-portraits-native.png)已補齊十一人，048 DRAFT；傷勢／表情為近似，正式載入及其餘結果另驗 |
| [結果報紙底圖](result-newspaper-v1.png)、[法蘭克敗者肖像](result-loser-frank-v1.png)、[靜態比較](../../../docs/screenshots/result-newspaper-candidate.png) | [來源與完整提示詞](result-source.json)，保留兩張生成原 bytes | [048 DRAFT](../../../docs/spec/048-hd-result-newspaper.md)，[三種標題](../../../docs/screenshots/result-outcomes-native.png)與[第二人結果](../../../docs/screenshots/result-player2-native-prototype-hd.png)已有正常原生取樣、切換／回退及返回；細字、標題與傷勢仍近似，未接正式程式 |
| [紅金 VS](selection-vs-v1.png)、[完整選角靜態比較](../../../docs/screenshots/selection-layout-candidates.png) | [來源與完整提示詞](selection-vs-source.json)，1589×990 透明生成原 PNG | 原八格與十一格並列候選；不是原生擷取，未修改滑鼠區域或正式程式 |
| [十一人選角肖像](../../../docs/spec/047-hd-selection-portraits.md)、[並列預覽](../../../docs/screenshots/selection-portrait-candidates.png) | [來源與精確提示詞](selection-portraits-source.json)，十一張 1254×1254 生成原 PNG | 隔離 Linux 原型已驗雙打兩側大肖像、鏡像及切換；仍待定版，未接正式選角，不代替戰鬥動作圖 |
| [標題人物](title-person-v1.png)、[紅金字標](title-logo-v1.png) | [來源與精確提示詞](title-source.json)，保留生成原 bytes | 已在[隔離原生原型](../../../docs/screenshots/title-native-prototype-hd.png)驗換色、游標與正常操作；未定版或接正式程式，見 [046](../../../docs/spec/046-hd-title-menu.md) |
| [廳堂](hall-i1.png)、[叢林](jungle-i3.png)、[街道](street-i4.png) | I1／I3／I4.XGB；[來源與精確提示詞](backgrounds-source.json) | 首輪候選已保存，尚未接入 |
| [宮殿](palace-i7.png)、[舞廳](auditorium-i8.png)、[港口](harbor-i9.png) | I7／I8／I9.XGB；[來源與精確提示詞](backgrounds-source.json) | 首輪候選已保存，尚未接入 |
| [石窟](grotto-i10.png)、[冰原](icefield-i12.png)、[火車](train-i13.png) | I10／I12／I13.XGB；[來源與精確提示詞](backgrounds-source.json) | 首輪候選已保存，尚未接入 |
| [石窟 v2](grotto-i10-v2.png)、[舞廳 v2](auditorium-i8-v2.png) | [修稿來源與精確提示詞](background-revisions-source.json) | 改善首稿底線偏高；仍待構圖複核，未定版或接入，原稿保持 |
| [街道 v2](street-i4-v2.png) | [修稿來源與精確提示詞](street-revision-source.json) | 上排字形改為 SUPER STAR，八份正常來源的捲動比較已驗；下方塗鴉及整體構圖仍待定版，未接正式程式，舊稿保持 |
| [道場](dojo.png)，1922×818 | [來源清單](dojo-source.json)、[精確生成提示詞](dojo.prompt.txt) | 已核對 I5.XGB／scene 0 的 124 個正常畫格與八份色盤。新版背景格式待確認，首輪先跳過接入 |
| [蜘蛛女連身衣比較稿](spider-coverage.png) | 原版姿勢與其他模型提示詞由本機交接包提供；見[交接工具](../../../tools/export_spider_reference.py) | 舊選定造型保留。內建工具無法產出完整圖集，遊戲暫用原貌 |
| [蜘蛛女外部 HD 稿](spider/README.md)，兩批十五張 | 使用者提供；[來源清單](spider/source.json)保留輸入與處理雜湊 | 已本地去背並收錄。normal-01 依 [034](../../../docs/spec/034-spider-low-guard.md) 接入相近低伏；其餘姿態仍待補 |

道場 PNG 保留生成原 bytes，沒有重新縮放或編碼。來源清單是候選資料索引，不是執行期素材包；直接傳給 `-hd-assets` 尚不能顯示道場。接入契約見[規格 029](../../../docs/spec/029-multi-scene-backgrounds.md)。

新增九景也保留內建 image_gen 的原 PNG bytes，尺寸約 1920×818。場景名稱只描述圖像，不推定正式關卡名稱。小字、群像、裝飾及構圖仍需接入前複核；I3 的提示詞誤稱中央動物為獅子，原圖與候選實為象，精確原提示詞保留並註記。後續已由正常雙打補證十一景的原版 scene、RAM、色盤及 camera 80／105 裁切，表見 [029](../../../docs/spec/029-multi-scene-backgrounds.md)；HD 捲動對齊、正式載入、全部 camera 與單打順序仍未驗證，不能把候選圖當作已接入的背景。

街道修稿為生成原 PNG，1922×818；SUPER STAR 是對原塗鴉字形的強推論，未從遊戲文字資料解出。店名 SILVER SLIPPER／GRILL 保留。生成工具也重畫文字區外的像素，來源檔保存差異量測，不宣稱只有文字像素改變。八份比較使用同一原相機與顯示範圍，前景仍為原版，屬於軟體構圖比較。正式多場景載入仍待 029 確認。

原版背景色號、色盤、原圖與研究收據仍保存在本機，不隨此目錄公開。生成素材的上傳授權與原作素材的散布權分開。
