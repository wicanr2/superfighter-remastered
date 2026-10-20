# 043：主色盤的額外圖像

狀態：CONFORMED，限定下列原始來源、核心三組普通路徑及第一人 Linux 原生畫面。原版證據及實作前審查見 `workplace/primary-extra-research-v1/review.json`，READY 全文另存 `043-ready.md`。本項修正鬼丸正常蓄力後出拳的 path 38 額外圖像遭「特效色盤未對應」拒絕，以及第二人返回點未觀測的缺口。

## 固定輸入及範圍

SF.EXE SHA 24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300，原檔、執行器、Go 與目前 042 程式身分沿 CONTEXT。special-onimaru-v3 的 sample-18 為序號 221、246,505,248 步，layer_error 是「特效色盤未對應」，不是未知的泛用重組失敗。

既有 beginEffect 只接受 D0h／F0h，再以對應玩家的原版 72 槽 RAM 指標核對來源。新探針由正常選角 5／4、PK 及後蓄／前拳輸入，獨立保存全部 blit 寄存器、返回位址、兩人來源表匹配、完整 packed bytes 與 CPU 前後／覆蓋。位址採 runtime 01B9:IP、DS 相對資料與原檔偏移，分別記錄；不推測改名。

## 已審查證據

| 結論 | 等級與定位 |
|---|---|
| 鬼丸額外圖像使用第一組角色色盤 | 已證實；P0 5／4、P1 4／5 及同角 5／5 各 200 格、404 次 blit，其中四次為來源槽 35，全部 CPU 色號及覆蓋差異為零 |
| 原始圖像身分 | 已證實；SFMAN06.DAT SHA `f398370820cfebbce670433130fd3718651ed4943259604fb55c851fa3906cbb`，原檔偏移 83706，17×66，packed SHA `ced0a80c16760634f865d7879786a00ad2a5e4d5fb1790f5c610c15b596d99d4`，指標表與執行中 DS:SI 對應 |
| 兩側色盤來源 | 已證實；普通 C0h／E0h 為 DAT AC8h 起十六色，同角第二人 E0h 為 MAN.COL 的角色 5 區塊。MAN.COL SHA `7153214bf444684179b5296ad1c4dfc874385cbf6e2d5e0c215c13e711749ce5` |
| 原呼叫允許主／第二色盤 | 已證實；IDA 9.4 正式 DB 複本匯出 `ida-v2.json`。IDA MZ linear `sub_142C0` 的 14351h／14355h／14358h 為 `mov dh,ds:2F04h; and dh,10h; add dh,C0h`，來源表 1706h／1708h 加 132Ah。`sub_14461` 的 144F2h／144F6h／144F9h 對應 E0h，來源表 1826h／1828h 加 132Ch |
| 觀測到的返回點 | 已證實；P0 IDA 14390h bytes E85503 呼叫 sub_146E8，runtime 返回 01B9:4393；P1 IDA 14520h bytes E84201 呼叫 sub_14665，runtime 返回 01B9:4523。IDA linear 與 runtime IP 差 10000h，均非原檔偏移 |
| 原檔及工具 | SF.EXE 固定雜湊同上；dosgolem 副本 manifest SHA `d79cc85bc1ce29dbe54c19e7857a9ac07b2e3a1754fb342632ead9e36e619fc3`；Go 1.24.13；IDA 9.4、292 函式，正式 DB SHA `5a122f625e659633f1e29ea1cb024fb4b1c31405031bf90d92dfe115ac00e2ca`，不改名或 bytes |

三份正常探針為 `primary-extra-oracle-v2`、`primary-extra-p2-oracle-v1`、`primary-extra-duplicate-oracle-v1`。獨立核對保存原圖、完整寫入、RAM 背景／角色／額外層重組及來源指標，報告為各自的 source-review.json。普通鍵盤序列及步數記於 receipt；沒有狀態注入、練習模式或重擲挑結果，亦不宣稱與舊 Core 的輪詢時點完全相同。

## 實作契約

- 沿用 `renderdata.Sprite.Effect` 表示額外圖像，不由此推定色盤。P0 接 C0h／D0h，P1 接 E0h／F0h；來源仍須符合該玩家的 72 槽 RAM 指標。
- 新增 4523h 返回點。主色盤 C0h 僅接受 4393h 呼叫、E0h 僅接受 4523h 呼叫；其他未驗主色盤返回點保留原貌。原有 D0h／F0h 分支保留。
- 呈現從實際色盤決定 bank 0／1，必須精確等於 `C0h + player*20h + bank*10h`。既有來源鍵、SHA、尺寸、原圖群組及十六色比對保持。
- bank 0 額外圖像另須逐點核對 packed 來源導出的色號與 CPU 覆蓋。只接受未裁切、不垂直翻轉的已有特效幾何。未知色盤、位置、覆蓋、來源或缺圖整格原貌。
- 同角第二人 bank 0 額外圖像可沿用 041 已驗 MAN.COL 配色；完整色盤及同角身分均須吻合。第二色盤不取得此例外。
- 來源 35 的 HD 已存在於一般圖集，使用相同美術，不新增、改寫或轉製圖片。typed data、包格式、設定與存檔不變。原版規則、招式、傷害、輸入及動畫不改。
- 垂直鏈為原 DAT／MAN.COL → RAM 指標及 blit → 完整圖層 → Select → 既有 HD 圖集 → 正常對戰切換。沒有新增持久狀態。原始素材、IDA 與完整來源收據只留本機，公開只放程式、文件與已收錄 HD。

## 驗收閘門

原檔／原呼叫 → 額外圖像及色盤 → 完整層 → 素材來源 → 同格原貌／HD。須獨立核對 blit 寫入與完整 RAM 重組、真實 fixture／篡改拒絕、正常原生觸發及切換／恢復、既有光效不退步，再核對程式／原資料及四平台建置。缺圖仍回退；來源層修正不等於美術或完整動畫完成。沒有新增存檔、設定或背景包格式。

READY 限定鬼丸這條普通出招路徑，其他主色盤額外來源及未觀測返回點未知。原生第二側與同角動畫若未測，完成聲明必須分開列。HD 配色維持 041 的近似等級。

## 實作驗收

- `special-onimaru-v4` 的正常第一人序列 200 格全部完整、無缺鍵，含原先拒絕的序號 221..224。`primary-extra-core-p2-v1` 與 `primary-extra-core-duplicate-v1` 各 201 格亦全部通過選擇，原檔、完整 CPU 層及實際主色盤由獨立 Python 核對。
- `primary-extra-core-paired-v2` 比較 559 個相同步數邊界，原版狀態、像素、尾列、色盤、角色及計數相同，額外來源 35 實際出現四格。兩側共用 Display 觀測，其餘呈現觀測關／開；不是原版亂數機制對拍。
- 真實 fixture 直接來自獨立 Oracle 的兩側及同角三份完整畫格。來源、槽、玩家、色盤 bank、未知色盤、位置、裁切、翻轉、CPU 覆蓋／色號及十六色篡改均整格拒絕。舊金太極十種第二色盤及同角二十二份來源測試通過。
- `primary-extra-native-full-v2` 及 `old-v2` 各五張正常 Linux 擷取，完整來源、HUD、陰影及 CRTC 重組、原貌切換、恢復與後續操作通過。新版額外圖像有 3,654 個可見像素改變，其中 2,478 個符合橘色色系；舊 042 程式維持整格原貌。已看過實際 HD 武器畫面，原始額外圖像為手杖及握持部位，未新增美術。
- `primary-extra-build-v1` 保存例行測試／vet、三組真實 fixture、四平台二進位與 45 份編譯輸入。Linux SHA `47ff4670d1b726f7ee94cc47be6c30ce3bbd6cb9fd6f3e64c0725cf47f657ad9`。素材仍為 1495 鍵／68 圖集；已發布首版、影片、原始包、執行器與正式 i64 不變。

P1 及同角只驗原始執行與 Select，未驗其原生 GPU 畫面。其他額外圖像、全部招式／動畫、真機、實體手把及遊戲音訊不列為本項完成。
