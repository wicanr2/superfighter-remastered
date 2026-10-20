# 045：主角色圖像的第二色盤

狀態：CONFORMED，限定下列兩份原始來源、真實 fixture、338 格核心取樣及正常 Linux 3／4 雙打。原版主圖像也會使用第二組十六色。獨立 Oracle、原呼叫、實際來源色號及不可變調色比較已審查；實作前全文及綁定見 `workplace/secondary-main-research-v1/045-ready.md`、review.json。素材 bytes、清單及原版規則保持。

## 已有線索

`remaining-special-audit-v1/character-03/character-03/sample-07` 是正常 3／4 雙打的普通後蓄／前拳腳序列。鳳凰主圖像來源 48、150×49，palette_base D0h、left_clip 13、flags 42h；完整來源 SHA `0078f98466cd75ed255d75e0cf77d5d996c661e28701c4fba32d140d64515859`。後續法蘭克主圖像來源 54 也出現 F0h。這些是已保存分層事實，不把第一人／第二人、主角色／額外圖像與色盤 bank 混為一談。

044 的 Select 只在 `Effect=true` 時由實際 PaletteBase 選 bank 1，其他主圖像固定 bank 0。因此不能用現有第一色盤美術或取消色盤核對直接放行。先由獨立 Oracle 保存每次 blit 的原始寄存器、來源指標、完整 packed bytes、十六色與 CPU 前後，重組完整畫格，再決定精確素材與 typed 選擇範圍。

固定 EXE、執行器及正式 i64 的身分沿 CONTEXT。位址保留 runtime 01B9:IP、IDA MZ linear、DS 相對指標與原檔偏移各自的基準。原版規則、出招、傷害、動畫、設定與存檔不在本項變更範圍。

## 原版證據

已證實：secondary-main-oracle-v2 的普通 3／4、PK、後蓄及前拳腳序列共 414 次 blit、200 格，全部 CPU 覆蓋／色號與 RAM 重組吻合。主圖像第二色盤有十一筆，鳳凰來源 48 八筆 D0h，法蘭克來源 54 三筆 F0h。每次 DS:SI、玩家 RAM 指標表及完整 packed bytes 吻合原檔，十六色逐項吻合各 DAT AF8h。source-review.json 與工具副本保存完整定位。獨立探針使用原完成畫格計數，不宣稱與舊 Core 輪詢時點相同。

| 來源 | 定位及 SHA-256 |
|---|---|
| SF.EXE | `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300` |
| SFMAN04.DAT | `2cd299e9c10814ae37bb044c2e3ae7adf940d8b1accd8feffa3844bbfb43356b`；來源 48 原檔偏移 121754、150×49，packed SHA 同上 |
| SFMAN05.DAT | `b5b77d590420b92db2d265aa89483de70d58193caf442fd41eba338eb111d653`；來源 54 原檔偏移 148116、112×79，packed SHA `ed02b48b45678f7d042237d4b75d2c3401e825dbb2ad4e270a19068b2c19542e` |

已證實：IDA 9.4／292 函式，唯讀正式 DB 複本的 sub_141FA 在 IDA MZ linear 1425Dh..14264h 為 `mov dh,ds:16EEh; and dh,10h; add dh,C0h`；sub_1439B 在 143FEh..14405h 對 16F6h 作相同遮罩再加 E0h。1428Bh bytes E8D703、1442Ch bytes E83602 呼叫原 sub_14665。原主圖像函式的其他翻轉分支在同一匯出內；實際鳳凰返回 runtime 01B9:429F／42A5，法蘭克返回 01B9:442F。IDA linear 與 runtime IP 差 10000h，均非原檔偏移。不推測改名或追查無關狀態寫入。

工具為 Go 1.24.13、Pillow 11.3.0、IDA 9.4；執行器 manifest SHA `d79cc85bc1ce29dbe54c19e7857a9ac07b2e3a1754fb342632ead9e36e619fc3`，正式 i64 SHA `5a122f625e659633f1e29ea1cb024fb4b1c31405031bf90d92dfe115ac00e2ca` 保持。

## HD 調色與 typed 契約

原圖 bytes 與姿態相同，只改十六色。已看過原版兩色與 secondary-main-preview-v1／v2：全色盤加權的 v1 讓未用到的顏色干擾光暈，棄用；v2 僅採該來源實際非透明像素的色號，青藍主體及淺色輪廓符合原色系。鳳凰使用 7、10..15，法蘭克使用 10..15，沒有同一原 RGB 對應不同目標 RGB 的歧義。這是保留已確認畫稿、尺寸、明暗及 alpha 的 RGB 近似，不稱原版逐像素材質對拍。

- `PaletteBase` 決定實際 bank，主圖像亦可為 `C0h + player*20h + 10h`；`Effect` 仍只決定角色計數、繪製順序及額外圖像幾何限制，不決定色盤。
- bank 1 主圖像使用既有 bank 0、normal 群組的同來源 PoseArt。載入時建立不可變視圖，保留原 Pose／Bounds／packed／Image，RGB 由 AC8h 轉 AF8h。不能把額外光效圖當成主角色圖，也不修改清單登錄。
- 調色沿 041 的距離權重及色差殘值，但僅對 packed 來源實際出現的非零色號加權。精確的已用色盤錨點精確映射；其他 RGB 四捨五入並限於 0..255，alpha 原封保持。來源為空或已用原 RGB 對應不同目標 RGB 時不建立視圖，保持原貌。
- 每次 bank 1 主圖像選擇仍須原 SHA／尺寸、完整十六色吻合，另以實際 packed 來源逐點核對 CPU 遮罩／色號。只有既有 Geometry 支援且符合原層才能畫 HD；未知來源／色盤／位置／裁切拒絕整格。
- 額外 bank 1 圖像仍須明確登錄的光效美術，不能套主圖像調色。bank 0 主圖像、041 同角替代色與 WIN 保持。victory 群組不取得此新視圖。
- 版本 1／2／3、1516 鍵／74 PNG、來源／catalog、520 KiB／110 Mi 像素上限不變；視圖只共用既有影像，沒有新增完整圖集副本、設定或持久狀態。

垂直鏈為原 DAT／原主圖像呼叫 → 相同 Sprite 來源／PaletteBase → 完整層及 CPU 幾何 → 同姿態不可變 HD 調色 → 正常出招／受招 → 同格切換。原版及完整收據只留本機，生成 HD 原 bytes 保持。驗原 Oracle 與真實 fixture、來源／色盤／幾何篡改拒絕、已用色號與 alpha、同格舊／新選擇、正常 Linux 兩側主圖像及原貌切換／恢復，最後核對原版／素材／i64 與四平台。只把實際抽測的來源列為完成，不宣稱全部主圖像色盤或動畫。

## 結論回填索引

不可變鍵為 DOS／上述固定 SF.EXE SHA／IDA MZ linear 1425Dh、143FEh。原始名稱 sub_141FA／sub_1439B、DS 運算元及呼叫 bytes 見原版證據。最終稽核須逐份驗以下標記與連結，缺項即失敗。

| 舊規格 | 必須出現的標記 | 裁定 |
|---|---|---|
| 009-hd-effects.md | 045 勘誤 | bank 不再等同主圖像／特效 |
| 043-primary-palette-extra-sprites.md | 045 勘誤 | 額外圖像規則不變，主圖像可選第二色盤 |
| 044-remaining-special-effects.md | 045 勘誤 | 原十格 unknown 以本項原版證據補足 |
| 041-duplicate-palettes.md | 045 範圍註記 | MAN.COL 與既有全色盤視圖不受影響 |

## 限定驗收結果

- `secondary-main-core-v3` 的 338 格全部通過 HD 選擇，沒有缺鍵或未知幾何。同序列舊 044 收據比較 phase／serial／steps／sprites／health／paths 全部相同，補齊原先十格，沒有退步。舊收據未保存逐格 raw hash，此比較不冒稱舊版全部像素雜湊對拍。
- 真實測試直接載入原 Oracle 七份完整畫格，含五次第二色盤主圖像。兩份來源、已用色號遮罩 FC80h／FC00h、精確錨點、alpha 及原稿身分通過；來源／色盤／位置／裁切／翻轉／CPU 遮罩篡改與歧義 RGB 拒絕通過。041 同角色、042 金太極、043 額外武器及 044 二十一光效的回歸通過。
- `secondary-main-native-v1` 與 `secondary-main-native-old-v1` 各八張普通 Linux 擷取。來源 48 的鳳凰出招及來源 54 的法蘭克受招，完整 CPU 層／來源／AF8h 色盤／HUD／陰影／CRTC 獨立重組吻合。新版青藍 HD、同格原貌、恢復 HD 及放開後繼續操作通過；舊 044 程式在這兩種狀態整格原貌，結束後恢復 HD。實際兩張 HD 已目視並收進 README。
- `secondary-main-build-v1` 保存四平台二進位，每份 46 個編譯輸入；Linux SHA `ae99fbe7b609afeb96d262ac1d9d4c511fdb76f9252a02ca0e30dfbf908c2a7d`。例行 internal／cmd 測試及 vet 已通過。PNG、1516 鍵／74 圖集、來源清單及容量限制不變。

範圍只含上述正常雙打來源與已驗幾何，不代表所有主圖像第二色盤、單打、完整動畫、其他平台 GPU、音訊或實體手把完成。RGB 調色維持 HD 近似，原版與正式 i64、已發布首版及本機原曲影片保持。
