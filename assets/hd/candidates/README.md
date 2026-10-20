# HD 候選素材

本目錄保存候選與來源資訊。是否已接入遊戲，以本表及[目前狀態](../../../CONTEXT.md)為準。

| 素材 | 來源與提示詞 | 狀態 |
|---|---|---|
| [標題人物](title-person-v1.png)、[紅金字標](title-logo-v1.png) | [來源與精確提示詞](title-source.json)，保留生成原 bytes | 黑紫人物、四字字標與四按鈕的[靜態構圖候選](../../../docs/screenshots/title-menu-candidate.png)；另有[十六步材質換色比較](../../../docs/screenshots/title-palette-candidate.png)，仍未定版或接原生，見 [046](../../../docs/spec/046-hd-title-menu.md) |
| [廳堂](hall-i1.png)、[叢林](jungle-i3.png)、[街道](street-i4.png) | I1／I3／I4.XGB；[來源與精確提示詞](backgrounds-source.json) | 首輪候選已保存，尚未接入 |
| [宮殿](palace-i7.png)、[舞廳](auditorium-i8.png)、[港口](harbor-i9.png) | I7／I8／I9.XGB；[來源與精確提示詞](backgrounds-source.json) | 首輪候選已保存，尚未接入 |
| [石窟](grotto-i10.png)、[冰原](icefield-i12.png)、[火車](train-i13.png) | I10／I12／I13.XGB；[來源與精確提示詞](backgrounds-source.json) | 首輪候選已保存，尚未接入 |
| [石窟 v2](grotto-i10-v2.png)、[舞廳 v2](auditorium-i8-v2.png) | [修稿來源與精確提示詞](background-revisions-source.json) | 改善首稿底線偏高；仍待構圖複核，未定版或接入，原稿保持 |
| [道場](dojo.png)，1922×818 | [來源清單](dojo-source.json)、[精確生成提示詞](dojo.prompt.txt) | 已核對 I5.XGB／scene 0 的 124 個正常畫格與八份色盤。新版背景格式待確認，首輪先跳過接入 |
| [蜘蛛女連身衣比較稿](spider-coverage.png) | 原版姿勢與其他模型提示詞由本機交接包提供；見[交接工具](../../../tools/export_spider_reference.py) | 舊選定造型保留。內建工具無法產出完整圖集，遊戲暫用原貌 |
| [蜘蛛女外部 HD 稿](spider/README.md)，兩批十五張 | 使用者提供；[來源清單](spider/source.json)保留輸入與處理雜湊 | 已本地去背並收錄。normal-01 依 [034](../../../docs/spec/034-spider-low-guard.md) 接入相近低伏；其餘姿態仍待補 |

道場 PNG 保留生成原 bytes，沒有重新縮放或編碼。來源清單是候選資料索引，不是執行期素材包；直接傳給 `-hd-assets` 尚不能顯示道場。接入契約見[規格 029](../../../docs/spec/029-multi-scene-backgrounds.md)。

新增九景也保留內建 image_gen 的原 PNG bytes，尺寸約 1920×818。場景名稱只描述圖像，不推定正式關卡名稱。小字、群像、裝飾及構圖仍需接入前複核；I3 的提示詞誤稱中央動物為獅子，原圖與候選實為象，精確原提示詞保留並註記。後續已由正常雙打補證十一景的原版 scene、RAM、色盤及 camera 80／105 裁切，表見 [029](../../../docs/spec/029-multi-scene-backgrounds.md)；HD 捲動對齊、正式載入、全部 camera 與單打順序仍未驗證，不能把候選圖當作已接入的背景。

原版背景色號、色盤、原圖與研究收據仍保存在本機，不隨此目錄公開。生成素材的上傳授權與原作素材的散布權分開。
