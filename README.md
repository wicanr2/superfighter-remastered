# 快打至尊 Remastered

Windows、macOS、Linux 原生桌面重製。以 dosgolem 執行原版核心，接入雙人手把、逐角色四格快速出招與街機手繪 HD，並保存遊戲歷史。

程式、文件與 [HD 生成素材](assets/hd/README.md)存放於 [GitHub 儲存庫](https://github.com/wicanr2/superfighter-remastered)。原版資料與遊戲二進位不隨儲存庫提供。

玩家入口使用 Ebitengine 原生視窗，直接處理鍵鼠與標準手把。原版核心負責規則、碰撞、AI 及流程。既有網頁只保留研究用途。

## 遊戲與故事背景

《快打至尊》由台灣全崴資訊 C&E 開發，於 1993 年問世，是 DOS 時代的對戰格鬥遊戲。八名格鬥者各有招式與作戰場景，玩家在單打中逐一迎戰對手，也能由兩人直接對戰。年代與開發背景可查[官方歷史介紹](https://www.superfighter.com/)。

故事圍繞毒品集團及其殺手展開。他們暗殺政府高層，向世界宣示對自由的控制，引起聯合國恐慌。八名英雄接受挑戰，迎戰集團的三名頭目。這裡依[官方後來公開的故事介紹](https://www.superfighter.com/sf/index.html)整理；官方 2013 年版本另有新動畫與結局，本專案不將那些內容當成本機 DOS 來源已具備的功能。

本重製保留原版核心，增加原生操作、練習模式與可切換 HD。蜘蛛女、小丑、印第安喬已能在單打、雙打直接選用；完整魔王過關與結局仍待驗證。

## 首版下載與資料準備

首版為 [v.0.1.0-20261020](https://github.com/wicanr2/superfighter-remastered/releases/tag/v.0.1.0-20261020)。Release 提供 Windows、Linux、macOS Intel 與 Apple Silicon 四個程式包、HD 生成素材及資料匯入功能，原版遊戲由玩家自行提供。執行程式時加上 `-import-data 原版目錄或jsdos檔 -data game-data`，會核對固定版本並建立新的資料目錄；既有目錄不覆寫。匯入後會從自己的原版資料準備屋頂 HD 參考。

儲存庫目前為私人，Release 與圖片需由有權限的帳號登入查看。這裡的公開包指排除原版資料的發行內容。

本機完整版另包含合法持有的原版資料，保存在 `dist-all/v.0.1.0-20261020/full-local/`；含原版 MIDI 配樂的推廣片只保存在同版本的 `promo/`，兩者均不上傳。四平台檔案、啟動驗證及已知限制見[發行契約](docs/spec/036-release-packages.md)。

鍵盤可在 F10 設定面板重綁八方向、拳、腳與四格快捷，F8 切換手把／鍵盤頁。第一人四快捷預設為主鍵盤 1／2／3／4，第二人為 7／8／9／0；兩人獨立保存，與手把四格共用角色招式。按住不連發，衝突不覆寫；只有已驗的斬四招能實際出招，其他角色仍明示拒絕。[鍵盤設定範圍](docs/spec/035-keyboard-bindings.md)。

原版音樂已確認十五段 MIDI，Compact PCM 共四十筆；音樂重播與語音修復的可行性及未知項見[音樂與語音 HD 評估](docs/audio-hd-assessment.md)。桌面遊戲的音訊串流與完整 HD 尚未完成。

目前 `main` 的開發版為 `v.0.1.1-20261020`，新增嵐的勝利姿態與 `LAN WIN`，並接入[角色雙向翻轉與頂部裁切](docs/spec/038-character-geometry.md)的逐格來源核對，以及[鳳凰拳腳兩種光效](docs/spec/039-phoenix-effects.md)、[場邊投擲裁切](docs/spec/040-mirrored-edge-clipping.md)與[金太極十種特殊光效](docs/spec/042-kim-effects.md)、[四人二十一個特殊光效](docs/spec/044-remaining-special-effects.md)，並支援[同角色對戰的替代配色](docs/spec/041-duplicate-palettes.md)；首版下載包尚未包含這些更新。其餘九景也已有[首輪 HD 候選稿](assets/hd/candidates/README.md)，與道場同樣等待多場景格式及正常遊戲接入驗證。十一景已補正常捲動來源比較；[石窟與舞廳修稿](assets/hd/candidates/background-revisions-source.json)另存候選，尚未定版。

目前已有原生雙打、兩人拳腳、斬四招、設定保存，以及可切換的屋頂 HD 背景、部分人物動作、已驗招式及鳳凰拳腳光效、柔邊地面陰影、生命條、計時、名字與勝場圖示。開場 `ROUND`／`FIGHT !`、斬首勝的鞠躬與 `JAAN WIN` 已接 HD；第二人法蘭克的抱胸、`FRANK WIN` 與右側首勝也已在 Linux 驗證。Linux 雙打基準曾正常打完兩回合、顯示結果並返回標題，後續擴充另驗各自範圍。完整角色 HD、實體手把、其他角色快捷、音訊與正式速度仍待驗收。最近收據及各平台限制見 [CONTEXT](CONTEXT.md)。

斬與法蘭克已對應全部 144 個一般來源槽、13 個第二色盤特效鍵，以及 WIN 圖像的 144 個入口。鳳凰另補兩個拳腳光效鍵，金太極新增十個第二色盤光效鍵；後續四人特殊技再補二十一鍵。WIN 入口對應七張不同勝利姿態，與一般動作分開辨識；登錄齊全不代表完整動畫已驗。介面基底的 Linux 案例通過 16 項檢查，Windows Wine 的斬、法蘭克案例各通過 16 項，包含特效、介面及同狀態切換。兩平台的法蘭克案例另驗到實際扣血。完整動畫與其他角色仍未完成，製作契約見[角色](docs/spec/008-hd-characters.md)、[特效](docs/spec/009-hd-effects.md)、[戰鬥介面](docs/spec/010-hd-battle-hud.md)及[勝利姿態](docs/spec/017-victory-pose-banks.md)。

原有八名角色、小丑與印第安喬的一般來源已接入原生，實測範圍見[薩爾可夫](docs/spec/018-sarkov-hd.md)、[子彈](docs/spec/020-bullet-hd.md)、[鳳凰](docs/spec/021-phoenix-hd.md)、[鬼丸](docs/spec/022-onimaru-hd.md)、[嵐](docs/spec/023-lan-hd.md)、[金太極](docs/spec/024-kim-hd.md)、[小丑](docs/spec/026-clown-hd.md)與[印第安喬](docs/spec/027-joe-hd.md)。目前開發群組共 1516 個鍵，包含十人的一般來源、蜘蛛女低伏、既有特效與十人的 WIN 入口。[子彈首勝](docs/spec/028-bullet-victory.md)、[鳳凰首勝](docs/spec/030-phoenix-victory.md)與[鬼丸首勝](docs/spec/031-onimaru-victory.md)已驗 Linux／Wine 完整切片；[嵐首勝](docs/spec/037-lan-victory.md)已驗 Linux，薩爾可夫的 Wine 下一回合仍未驗完。同角色替代色盤已接入已登錄姿態，Linux 法蘭克的藍／綠雙色操作與第二人首勝已驗；色彩轉移為 HD 呈現近似。蜘蛛女其餘動作、完整動畫、其他角色快捷及其餘場景仍在製作。

十一人選角已加入蜘蛛女、小丑、印第安喬，單打、雙打皆可選，並保留原版對戰規則。Linux／Wine 已驗正常選角與首戰操作；魔王完整單打過關與結局仍待驗，詳見[選角範圍](docs/spec/025-boss-selection.md)。

## HD 素材

目前收錄 74 張角色／特效圖集、角色登錄清單與屋頂背景；道場及其餘九景候選、蜘蛛女外部稿另標示狀態。內建生成 PNG 保留原 bytes，外部稿的去背處理另作紀錄；逐檔來源與 SHA-256 見 [HD 素材目錄](assets/hd/README.md)。素材上傳不代表完整角色動畫或所有場景已完成。

[街道修稿](assets/hd/candidates/street-i4-v2.png)改善牆面上排塗鴉，另存原 PNG 與[精確提示詞](assets/hd/candidates/street-revision-source.json)。八份同狀態捲動比較已複核；它仍是候選，未接入正式背景。

![十一人選角肖像 HD 候選，尚未接入正式程式](docs/screenshots/selection-portrait-candidates.png)

十一人選角肖像已各自重繪為 1254×1254，保留生成原 PNG 與[精確提示詞](assets/hd/candidates/selection-portraits-source.json)。隔離 Linux 原型已驗雙打兩側大肖像、右側鏡像、原貌切換及未載候選的回退；背景、VS 與縮圖仍為原貌。上圖是美術候選預覽，視覺、版面與載入契約未定，正式選角畫面保持原貌。[來源與限制](docs/spec/047-hd-selection-portraits.md)。

![選角八格與十一格靜態 HD 比較，非遊戲截圖](docs/screenshots/selection-layout-candidates.png)

選角另補[透明紅金 VS](assets/hd/candidates/selection-vs-v1.png)，以上用既有 HD 肖像、灰階字標與重畫框線比較完整構圖。八格方案保留原縮圖位置，十一格方案讓三名魔王同列可見；兩者均為靜態候選。十一格仍需配套調整點選區域與焦點，正式遊戲尚未採用。

[蜘蛛女的十五張外部 HD 稿](assets/hd/candidates/spider/README.md)也已收錄。使用者確認的雙手觸地低伏已接入，另作無損鏡像及透明留白裁切；同一張圖對應三組低伏來源。其他稿仍有姿勢差異，未對應動作整格回退原貌。

![已接入遊戲的屋頂 HD 生成背景](assets/hd/backgrounds/rooftop.png)

![鳳凰勝利 HD 原始圖集](assets/hd/characters/phoenix-win.png)

以上是生成素材預覽；正常遊戲的整合驗證與限制見 [目前狀態](CONTEXT.md)及各規格。

![隔離原生視窗中的標題 HD 候選，尚未接入正式程式](docs/screenshots/title-native-prototype-hd.png)

標題人物與紅金字標已重繪並收錄候選。上圖擷取自隔離的 Linux 原生原型，已驗八個換色相位、原貌切換、設定往返及進入雙打。可見游標、右下邊界、滑鼠進入選角與缺候選回退也已核對。材質分區與正式載入方式尚未定版，正式程式及下載包仍維持原標題；另有[十六步材質換色比較](docs/screenshots/title-palette-candidate.png)。[來源及接入閘門](docs/spec/046-hd-title-menu.md)。

## 目前整合畫面

![鳳凰蓄力出招時的青藍主角色 HD](docs/screenshots/phoenix-secondary-main-hd.png)

![法蘭克受招時的青藍主角色 HD](docs/screenshots/frank-secondary-main-hd.png)

Linux 開發版已接入主角色的第二色盤。正常鳳凰出招與法蘭克受招沿用同姿態 HD，依原版色盤轉為青藍色；原貌切換、恢復與舊程式回退已核對。配色為保留原稿的 RGB 近似，完整動畫另驗。[來源與範圍](docs/spec/045-secondary-palette-main-sprites.md)。

![鳳凰踢擊的金黃 HD 光弧](docs/screenshots/phoenix-gold-arc-hd.png)

![小丑旋轉時分離的青藍光影與橢圓環](docs/screenshots/clown-rings-hd.png)

開發版新增鳳凰、嵐、小丑與印第安喬共 21 個特殊技光效鍵。上述畫面由普通鍵盤出招取得，原版圖層、色盤、原貌切換與恢復已核對；原版規則與快捷範圍保持。[接入與限制](docs/spec/044-remaining-special-effects.md)。

![鬼丸蓄力出招的 HD 武器與角色](docs/screenshots/onimaru-primary-weapon-hd.png)

Linux 開發版以普通後蓄／前拳觸發鬼丸的額外武器。已核對原版主色盤、來源與圖層，原貌切換、恢復及繼續操作通過。沿用既有美術，未擴大快捷出招範圍。[接入範圍](docs/spec/043-primary-palette-extra-sprites.md)。

![金太極正常方向／拳腳觸發的青藍 HD 刀光](docs/screenshots/kim-effects-hd.png)

Linux 開發版以普通鍵盤輸入驗金黃光彈、青藍刀光與拳影三類效果。十個第二色盤來源已補圖；原貌切換、恢復與舊包整格回退已核對，全部動畫與快捷出招仍另驗。[來源與範圍](docs/spec/042-kim-effects.md)。

![法蘭克同角色雙打的藍綠 HD 配色](docs/screenshots/duplicate-frank-hd.png)

Linux 開發版正常同角雙打，第一人藍色、第二人綠色，依原版替代色盤呈現。行走、放開、原貌切換與第二人首勝已核對；HD 配色為保留原稿細節的色彩轉移近似，完整動畫另驗。[來源與範圍](docs/spec/041-duplicate-palettes.md)。

![場邊投擲的雙向翻轉與裁切 HD](docs/screenshots/edge-clip-hd.png)

Linux 開發版以普通移動與拳擊觸發場邊投擲，法蘭克按原版來源翻轉並裁切。新舊程式對照、同狀態原貌切換、恢復與繼續操作均已核對；其他裁切與完整動畫另驗。[來源與範圍](docs/spec/040-mirrored-edge-clipping.md)。

![鳳凰正常出拳的 HD 光效](docs/screenshots/phoenix-effect-hd.png)

Linux 開發版從普通選角、移動與拳腳取得兩種藍色光效，依原版尺寸、朝向及層次呈現。完整素材與舊包回退、原貌切換及恢復已核對；其他招式與全部動畫仍待補。[接入範圍](docs/spec/039-phoenix-effects.md)。

![正常擊倒過場的角色雙向翻轉 HD](docs/screenshots/character-flip-hd.png)

Linux 開發版由普通選角、移動與拳擊進入擊倒過場。這張法蘭克使用原版雙向翻轉，核對來源像素與覆蓋後維持 HD；同狀態切換、恢復與下一回合已驗。頂部裁切另有正常案例，完整動畫仍待補。[接入範圍](docs/spec/038-character-geometry.md)。

![嵐正常首勝與 LAN WIN 的開發版 HD 整合](docs/screenshots/lan-victory-hd.png)

Linux 正常雙打由移動及拳擊取得首勝。人物、姓名、勝場與屋頂同格 HD，原貌／HD 切回及下一回合清除已核對；這是開發版切片，完整動畫仍另驗。[範圍與證據](docs/spec/037-lan-victory.md)。

![首版封包中斬與法蘭克的 HD 對戰](docs/screenshots/battle-hd.png)

從 Linux 完整版解壓後，正常選角進入雙打。屋頂、人物與介面由封包內素材呈現，原版資料只用來執行核心及核對來源。

![蜘蛛女低伏與 WIDOW 姓名的原生 HD 整合](docs/screenshots/spider-low-guard-hd.png)

Linux 普通雙打的蜘蛛女對法蘭克。這是已確認的相近低伏姿勢，同一張稿用於三組待機來源；移動時保留原貌，放開後恢復 HD。切換與缺件回退均已核對，完整動畫仍待補。[接入範圍](docs/spec/034-spider-low-guard.md)。

![印第安喬正常首勝的 HD 整合畫面](docs/screenshots/joe-victory-hd.png)

金太極、小丑與印第安喬的勝利圖、姓名、原貌／HD 切換及下一回合清除已驗 Linux。小丑案例為時間到後判勝；缺少勝利素材時整格回退原貌。[接入範圍](docs/spec/033-first-pass-victories.md)。

![雙方滿血、固定計時與練習模式工具列的原生 HD 畫面](docs/screenshots/training-hd.png)

Linux 原生雙打的練習模式。雙方生命固定滿血、計時停在 99，右上工具列顯示「練習：開」；此圖為暫停擷取。模式會改變規則，不能當作未修改原版對拍。[功能與驗證](docs/spec/032-training-mode.md)。

![鬼丸正常首勝的原生 HD 整合畫面](docs/screenshots/onimaru-victory-hd.png)

Linux 原生版由普通選角、移動與拳擊取得鬼丸首勝，顯示 `ONIMALU WIN`。這個案例的 Linux／Wine 切換與下一回合清除均已核對；這是 HD 整合截圖，尚不代表完整勝利動畫。[來源與範圍](docs/spec/031-onimaru-victory.md)。

![兩人獨立手把指派與四格快捷設定](docs/screenshots/gamepad-settings.png)

Windows 原生程式在 Wine 中顯示的設定介面，擷取於原版核心執行前。可分別指派兩人的手把，逐角色設定 R1／R2／L1／L2。擷取時未連接實體手把。[截圖來源](docs/screenshots/source.json)。

![兩人獨立鍵盤重綁與四格快捷](docs/screenshots/keyboard-settings.png)

F10 開啟「控制與快捷設定」，按 F8 切換到鍵盤頁。圖中示範第一人的方向、拳腳與快捷重綁；Linux／Wine 已驗保存後重啟、兩人獨立輸入及斬快捷按住只出招一次。

十一人選角、十名角色的一般 HD、部分勝利姿態與同狀態切換已按各自範圍驗證。角色圖集見上方 HD 素材；正常玩家路徑、Linux／Wine 差異及未完成項集中於 [目前狀態](CONTEXT.md)與[驗證矩陣](VERIFICATION-MATRIX.md)。

原貌對照、分層與原始收據保存在本機研究工作區。GitHub 首頁的 HD 整合截圖與素材預覽均引用已納入版控的圖片，來源雜湊見[截圖紀錄](docs/screenshots/source.json)。

## 建置與執行

開發建置在 Docker 內執行，工作區需要已準備的 dosgolem 獨立來源及工具鏈，詳見[工作契約](AGENTS.md)和[桌面規格](docs/spec/005-native-desktop.md)。

儲存庫不附原版資料、研究收據、dosgolem 私有來源或本機快取。HD 生成圖與角色清單收錄於 `assets/hd/`，屋頂原版參考色號與色盤仍需本機準備。`go.work.example` 記錄相對目錄配置，準備來源後複製為 `go.work`；原版匯入與來源快照工具為 `tools/prepare.py`，執行器補丁為 `tools/apply_runtime_patch.py`。現行收據中的 `workplace/` 連結僅供本機核對。

目前執行器副本也需要普通記憶體觀測及顯示 API。準備與安裝順序見[規格 007](docs/spec/007-memory-write-observation.md)、[規格 014](docs/spec/014-mode13-scanout.md)及[規格 015](docs/spec/015-native-scanout.md)；安裝工具只修改本專案的獨立副本。

```sh
bash tools/build_desktop.sh
```

開發二進位在 `workplace/bin/`：

| 平台 | 檔案 |
|---|---|
| Linux x86-64 | `superfighter-linux-amd64` |
| Windows x86-64 | `superfighter-windows-amd64.exe` |
| macOS Intel | `superfighter-macos-amd64` |
| macOS Apple Silicon | `superfighter-macos-arm64` |

玩家在自己的電腦執行對應程式，以 `-data` 指定合法原版資料目錄。未指定時尋找 `game-data/`。例如 Windows：

```powershell
.\superfighter-windows-amd64.exe -data .\game-data
```

這些是開發中間產物。玩家 ZIP 封包另由 `tools/package_release.py` 建立；Linux 與 Windows Wine 已驗解壓啟動，macOS 已核對兩種架構及封包內容，尚未簽章或作真機驗收。原版 EXE、COM、DAT、美術及音訊不加入 Git 或公開發行包。

本機屋頂試作素材已備妥時，可加上 `-hd-assets workplace/hd-rooftop-study`，再按「原貌／HD 背景」切換。素材準備與驗證見[背景規格](docs/spec/006-rooftop-background.md)。沒有素材或場景未對應時顯示原貌。

角色與特效試作再加上 `-hd-characters assets/hd/characters`，按「原貌／HD 角色」切換。此群組保留既有基底，包含十人的一般來源、蜘蛛女低伏及十人的 WIN 入口，與本機 `workplace/hd-characters-kim-effects-v1` 的 PNG 及清單相同。背景、兩名角色、來源與圖層全部符合才顯示 HD，缺動作或未知色盤時整張回退。新版仍接受舊版角色素材。基底準備工具為 `tools/prepare_hd_characters.py`，勝利姿態登錄使用 `tools/prepare_victory_characters.py`，一般角色擴充使用 `tools/prepare_character_extension.py`，蜘蛛女限定切片使用 `tools/prepare_spider_low_guard.py`，嵐的來源重用與勝利登錄使用 `tools/prepare_lan_victory.py`。

含特效的新版群組也啟用高解析生命、計時、名字、玩家標記、勝場與地面陰影，來源驗證失敗時整張回退。舊版 1 素材保留原貌介面、特效與陰影。

## 操作

按「開始／繼續」，由原版標題進單打或雙打。「控制與快捷設定」可指派兩人裝置、切換要設定的角色與四招，以及重綁鍵盤；設定角色不改變原版選角。

選角時可用下方十一人按鈕或左右方向選人，再以 Enter、手把確認鍵或「確認選角」決定。三名魔王在兩種模式都可選。舊八人設定會保留原配置，補上魔王欄位；蜘蛛女只有兩招，其餘預設留空。魔王快捷仍待逐招驗證。

| 輸入 | 第一人 | 第二人 |
|---|---|---|
| 方向 | QWE／A D／ZXC | 數字鍵盤 789／4 6／123 |
| 拳 | Tab | Enter |
| 腳 | 左 Shift | 右 Shift |
| 手把拳／腳 | 西側／南側面鍵 | 同左，另行指派裝置 |
| 快捷 | R1／R2／L1／L2 預設招式 1／2／3／4 | 各自保存角色配置 |
| 鍵盤快捷 | 主鍵盤 1／2／3／4 | 主鍵盤 7／8／9／0 |
| 暫停 | Esc 或手把 Start | 共用對局 |
| 練習模式 | F9 或工具列「練習：關／開」 | 共用對局 |
| 設定 | F10 開啟，F8 切頁，Tab 選欄，Esc 關閉 | 同左 |

每名角色最多四格，可選第五招或留空。快捷按住不連發，投技仍須近身。視窗失焦會暫停；手把斷線清除該玩家指派及輸入，重接後需再次指派。

練習模式可在選單預先開啟，也可在戰鬥中切換。啟用後雙方補滿並鎖住滿血、停止倒數，電腦不再主動操作；受擊、擊退、倒地與站立動畫保留，雙打仍可操作兩邊。關閉後恢復扣血、倒數及 AI，生命從當下滿血繼續。已判定勝負的回合等待下一回合啟用。

加上 `-training` 可在啟動時預選練習模式。開關只保留本次執行，重啟預設關閉；練習模式的診斷與截圖會標示已修改規則，驗證範圍見[練習模式規格](docs/spec/032-training-mode.md)。

設定與可寫 DOS 資料存於作業系統的 `SuperfighterRemastered` 使用者設定目錄，可用 `-user-data` 改位置。原始資料維持唯讀。

## 文件

- [工作契約與索引](AGENTS.md)、[目前狀態](CONTEXT.md)、[工作清單](WORKLIST.md)。
- [驗證範圍](VERIFICATION-MATRIX.md)、[研究證據](RESEARCH-LOG.md)、[工作歷程](WORKLOG.md)。
- [原生桌面規格](docs/spec/005-native-desktop.md)、[輸入證據](docs/spec/004-live-input-slice.md)、[手把草案](docs/spec/002-gamepad-design.md)。
- [HD 規格](docs/spec/003-hd-design.md)、[屋頂背景](docs/spec/006-rooftop-background.md)、[角色](docs/spec/008-hd-characters.md)、[特效](docs/spec/009-hd-effects.md)、[戰鬥介面](docs/spec/010-hd-battle-hud.md)、[勝場](docs/spec/011-hd-win-markers.md)、[陰影](docs/spec/012-hd-shadows.md)、[顯示映射](docs/spec/015-native-scanout.md)、[勝負文字](docs/spec/016-hd-victory-messages.md)與[勝利姿態](docs/spec/017-victory-pose-banks.md)。完整動畫、其他勝負分支及其餘角色／場景／畫面仍在製作。
- [青衫與 SP Moves 歷史保存](docs/game-history.md)。

自有程式與文件採 [RRSAL-1.0](LICENSE)，為 source-available 專案。此授權不涵蓋原版遊戲、外站原文與圖片或衍生美術；玩家須自備合法原版。專案與原版權利人沒有隸屬關係。內嵌中文字型另依 [SIL Open Font License](internal/desktop/assets/OFL.txt) 使用。
