# 快打至尊 Remastered：目前狀態

更新日期：2026-10-20。此檔為唯一現況，工作順序見 [WORKLIST.md](WORKLIST.md)，穩定規則與文件索引見 [AGENTS.md](AGENTS.md)。

目前工作樹為 `/home/anr2/cht/快打至尊/superfighter-remastered`，使用 `main` 追蹤 `origin/main`。使用者已建立 [GitHub 儲存庫](https://github.com/wicanr2/superfighter-remastered)，遠端已建立並上傳來源，後續提交與核對見 WORKLOG。父目錄程式與文件只保留舊快照；後續編輯在本工作樹進行。

使用者後續明確要求「HD素材上傳」，本輪又要求「hd記得放進去 repo」。[assets/hd/README.md](assets/hd/README.md)收錄 83 張生成 PNG 及現行角色清單，包含 65 張正式角色／特效圖集、屋頂、道場候選、蜘蛛女舊比較稿及十五張外部候選；逐檔身分見 [catalog.json](assets/hd/catalog.json)。外部稿保留去背處理前後的雜湊。這些授權取代以下舊切片的 HD 圖只留本機限制，原版檔案、原版色號／色盤、原圖、私有執行器與研究收據仍不上傳。沒有改變儲存庫可見性、原版資料權利或 HD 完成標準。

素材及清單共 98,133,629 bytes，整個素材目錄 92 檔。所有 PNG、來源雜湊、尺寸及角色清單均核對；鬼丸首勝 031 及其餘三人首勝 033 已通過限定接入，仍不代表完整角色／場景完成。README 的圖片與相對連結另比對 Git 追蹤清單，HD 整合截圖收錄於 [docs/screenshots/](docs/screenshots/)，原貌對照及原始收據保留本機。

首批 HD 素材提交 `4209aad83089c7f74c5ef853a4f1d865e6739f78` 已成功推送 `origin/main` 並由 `ls-remote` 核對。原版與候選的接入限制不因上傳改變，後續 HD 製作仍依工作清單。

## 已確認方向

- 參考 `/home/anr2/cht/zeliard` 的包裹與呈現方式。
- dosgolem 直接執行原版核心，本專案處理前端、手把與 HD 呈現。
- 使用者明確指定三平台原生桌面：Windows、macOS、Linux。玩家入口不使用 web；舊 HTTP／HTML 及瀏覽器收據只保留研究用途。
- 支援手把操作與 HD。十一人選角已加入三名魔王；原生背景、原有八人、小丑及印第安喬的一般來源已接入。蜘蛛女、完整動畫與其餘畫面仍在製作。
- 使用者於 2026-10-19 回覆「ok B」，選定 HD 的 B「街機手繪」方向；只確認畫風，原版造型仍為修正依據。
- 使用者後續明確同意 HD 規格開工，首批為屋頂、斬、法蘭克與對戰介面；技術未知仍依規格閘門處理。
- 已授權逐角色快速出招，最多四格，R1／R2／L1／L2 預設對應絕招 1／2／3／4；五招角色可任選四招。兩名玩家分開保存設定，並規劃雙手把雙打。

## 唯一現況表

| 項目 | 狀態 | 最近證據與限制 |
|---|---|---|
| 鍵盤重綁與快捷 | 035 限定 CONFORMED | 每人十四欄、兩人四格快捷，保存及舊檔相容。Linux／Wine 各六項正常路徑通過；兩人斬第一招 path 24h、按住一次、方向與拳腳獨立。實際 Linux 封包另驗失焦中立。其他角色快捷仍拒絕，斬完整四招沿用 004 |
| 首版交付 | v.0.1.0-20261020 封包已驗，遠端發布待核對 | dist-all 同版 patch 四包及 full-local 四包逐檔／CRC／SHA 通過。公開不含原版，本機各 125 原檔。Linux／Wine 公開包匯入、拒絕覆寫、兩種包啟動與 HD 自動準備通過；macOS 只驗內容及架構。推廣片只留本機，採原版 MIDI 軟體演奏 |
| 原版音訊與 HD 評估 | 格式盤點完成，遊戲串流未接 | SF000.MUS 十五段 MIDI；十七個 PPM 容器四十筆 Compact PCM。首段原曲供本機影片，語音取樣率／編碼／角色標籤仍未知；見 docs/audio-hd-assessment.md，不稱音訊 HD 完成 |
| 首輪三人 WIN | 已接原生，033 限定 CONFORMED | 該切片 1381 鍵／64 PNG／十九來源。22,020 個成對邊界、18 張原檔重組、真實姓名與新來源測試通過；三個 Linux 首勝及缺件案例各七張切換／清除通過。小丑為時間到判勝。四平台 38 份輸入及 bin 已更新；本切片未驗 Wine／真機。嵐 alpha 與蜘蛛女姿勢卡點先跳過；道場整理完成，029 格式仍待確認 |
| 練習模式 | 已接原生，032 限定 CONFORMED | 工具列／F9／-training 共用；雙方補滿且鎖血、停時、AI 中立，關閉恢復。核心單／雙打、七個拒絕邊界、Linux 單打七項與 Linux／Wine 雙打 HD 各八項通過；重啟預設關，曾啟用標示 modified。完整程式測試及 vet 通過 |
| jsdos 下載 | 已完成 | 1,281,787 bytes；SHA-256 與來源物件檔名一致；ZIP CRC 通過 |
| 來源盤點 | 已完成 | 128 個檔案、130 個 ZIP 項目；逐檔 SHA-256；作弊資料隔離；原始副本唯讀使用 |
| 研究工具 | 已建立 | 安全盤點、IDA、逐次繪製與完整 RAM 分層；規格 007 的通用觀測介面限定 CONFORMED，獨立副本新增兩檔，共用來源未改 |
| dosgolem 啟動 | 原生雙打基準已走完整比賽與返回 | 普通選單、移動與拳擊完成兩次擊倒、結果報紙及返回標題，八張擷取通過。離開對戰後快照清空；此基準二進位另存，勝場擴充另驗首勝 |
| 原版輸入 | 雙人基本輸入與斬四招已驗 | 正常單打、雙打各 25 組基本輸入；雙打兩人的斬各四招均進入原版對應路徑；十二輪詢蓄力是已驗充分條件，未稱最短時間 |
| 前端與手把 | 三平台共用原生桌面已接核心 | 現行 Linux／Wine 首勝與切換通過；一般操作、兩人獨立放開、特效扣血、設定重啟及失焦的十七項證據保留顯示修正基底身分。實體手把未驗 |
| HD | 屋頂、部分角色、13 組特效、介面／勝場、柔邊陰影、開場及兩側首勝已接原生 | 斬首勝已驗兩平台；第二人法蘭克的抱胸、FRANK WIN 與右側勝場已驗 Linux，Wine 達執行期限，尚未通過。兩側核心來源取樣通過；完整動畫及其他角色／畫面未完成 |
| 薩爾可夫一般姿態及姓名 | 已接原生，018 限定 CONFORMED | Linux／Wine 各七項、九張擷取，Linux 缺件九張整格回退通過；45 張姿態對應 72 個一般入口，共 373 鍵。原姓名 SARORKOV，設定識別字仍為 sarkov；勝利、替代色盤、快捷與完整動畫另驗 |
| 薩爾可夫勝利 | 019 READY，Linux 完整與 Wine 部分通過 | 9,290 成對邊界與 23 取樣通過；Linux 與舊素材各七張通過。Wine 六張證明勝利／切換，2400 秒期限前未到下一回合，僅有 partial 報告；三個首勝工作均已結束，不再輪詢舊 handle |
| 子彈一般姿態與姓名 | 已接原生，020 限定 CONFORMED | Linux／Wine 各七項、九張擷取及 Linux 缺件九張回退通過；58 種姿態對應 72 一般入口。原姓名 BULLET，62×11。現行 517 鍵／25 PNG／四平台二進位已整合；WIN、特效、快捷與完整動畫另驗 |
| 鳳凰一般姿態與姓名 | 已接原生，021 限定 CONFORMED | 61 組原圖、72 入口，現行 589 鍵／31 PNG；Linux／Wine 各七項、九張完整重組及 Linux 缺件九張整格原貌通過。原姓名 PHO HUANG／93×11，真實 HUD、Go 測試與四平台編譯來源通過；WIN／快捷與完整動畫另驗 |
| 鬼丸一般姿態與姓名 | 已接原生，022 限定 CONFORMED | 66 組／72 入口、現行 661 鍵／37 PNG；Linux／Wine 各七項、九張完整重組及 Linux 缺件九張整格原貌通過。ONIMALU／72×11 與 L 字模、真實 HUD、Go 測試及四平台來源通過；WIN／快捷與完整動畫另驗 |
| 嵐一般姿態與姓名 | 已接原生，023 限定 CONFORMED | 59 組／72 槽、現行 733 鍵／43 PNG；Linux／Wine 各七項、九張完整重組及 Linux 缺件九張整格原貌通過。LAN／31×11、真實 HUD、完整程式測試與四平台來源通過；bin 已更新，WIN／快捷／完整動畫另驗 |
| 金太極一般姿態與姓名 | 已接原生，024 限定 CONFORMED | 57 組／72 槽、現行 805 鍵／48 PNG，舊 733 鍵不變；Linux／Wine 各七項、九張完整重組及 Linux 缺件九張整格原貌通過。KING TAI CHI／109×11、真實 HUD、完整程式測試與四平台來源通過；bin 已更新，WIN／快捷／完整動畫另驗 |
| 魔王選角 | 已接原生，025 限定 CONFORMED | 單打／雙打可選蜘蛛女、小丑、印第安喬；普通輸入定位，原版程式與狀態不改。原八人框線越界只在獨立呈現影本排除。基底八案例及修正版 Linux／Wine 各單打、雙打通過；十二張原肖像／原生視窗核對，完整 Go 測試及 vet、舊設定補齊通過。完整過關／結局未驗 |
| 小丑 HD | 已接原生，026 限定 CONFORMED | 62 組／72 槽、877 鍵／54 PNG，舊 805 鍵不變；Linux／Wine 各七項、九張完整重組及缺件九張整格原貌通過。JOKER／52×11、真實 HUD、完整程式測試及四平台來源通過；bin 已更新，WIN／快捷／完整動畫另驗 |
| 印第安喬 HD | 已接原生，027 限定 CONFORMED | 44 組／72 槽、949 鍵／58 PNG，舊 877 鍵不變；Linux／Wine 各七項、九張重組及缺件九張整格原貌通過。INDIAN JOE／96×11、真實 HUD、完整 Go 測試及四平台來源通過；拳擊來源已補證為 path 27 的 5／6／7，v1 錯誤期望保留勘誤。WIN／快捷／完整動畫另驗 |
| 蜘蛛女 HD | 034 限定 CONFORMED，低伏已接原生 | 使用者確認 normal-01 相近姿勢；一張稿對應一般 0／1／41 與別名三十鍵。現行 1411 鍵／65 PNG／二十來源，舊 1381 鍵與 64 PNG 不變。Linux 與缺件各四項／五張通過原檔重組、移動整格原貌、放開恢復與同狀態切換。WIDOW、候選與既有八人真實姓名測試通過。其他 42 組一般來源、WIN、完整動畫、第二側與實體手把另驗 |
| 子彈勝利 HD | 已接原生，028 限定 CONFORMED | 1021 鍵／59 PNG，新增四組／72 WIN 入口，舊 949 鍵不變；6,018 成對邊界、11 個 WIN 取樣及五張來源通過。Linux／Wine 各七張勝利、切換與下一回合清除通過，缺件七張回退。完整 Go 測試、真實字圖及四平台 37 份編譯來源通過；第二人／完整動畫另驗 |
| 鳳凰勝利 HD | 已接原生，030 限定 CONFORMED | 1093 鍵／60 PNG，新增三組／72 WIN 入口，舊 1021 鍵不變；5,952 成對邊界、八個 WIN 取樣及四張來源通過。Linux／Wine 各七張與缺件七張回退通過，PHO HUANG WIN、切換、下一回合清除及四平台 37 份來源均核對；第二人／完整動畫另驗 |
| 鬼丸勝利 HD | 已接原生，031 限定 CONFORMED | 1165 鍵／61 PNG，新增四組／72 WIN 入口，舊 1093 鍵不變；12,272 成對邊界、29 個取樣與五張來源通過。Linux／Wine 各七張及缺件七張完整通過，ONIMALU WIN、切換、下一回合、完整測試／vet 與四平台 37 份來源均核對；第二人／完整動畫另驗 |
| 道場 HD 背景 | 029 DRAFT，素材格式確認待回答 | dojo-art-v1 保存 1922×818 原 PNG 與精確請求；正常 0／0 的 124 格、scene 0、背景 RAM／兩人 bytes 及八份色盤通過。建議新版包自動切換屋頂／道場並相容舊包，確認前不接 production；來源身分見 dojo-source-review-v1.json |
| 原生效能診斷 | v2／v3 已判讀，未修改正式程式 | v2 的 20 秒區間推進 875 萬步／14 格，Wine／OpenGL 原生圖形呼叫為主。v3 指定 DirectX 推進 1000 萬步／16 格，cgocall 包含視窗事件與游標呼叫；單次區間不證明解決速度。證據在 desktop-performance-v3/analysis.json |
| 顯示起點修正 | 已接原生，015 限定 CONFORMED | Linux／Wine 各十張開場、Linux 對戰十五張與舊素材十一張全部核對；起點第 7／11／12 列及可見尾端逐格正確，原貌與 HD 共用映射 |
| AI 研究 | 靜態載入與決策鏈已定位 | AIDATA 為 3×192 bytes，策略 byte 乘 16 進角色輸入序列；CHEAT 檔是 169-byte ASCII，未替換正常資料或宣稱實跑效果 |
| 歷史資料 | Markdown 與快照已保存 | 青衫及 SP Moves、十張原圖、八名角色招式比較及青衫另載三頭目；差異並列，來源雜湊可回查 |
| 原版版本與玩法 | 部分已觀察 | 包內 README 自述 v2.0，實跑帶第三方啟動殼；本包是目前基準，不能宣稱未修改原始發行版；控制方式仍在核對 |
| 平台與發布 | 三平台四架構首版已建置 | keyboard-release-build-v1 四份二進位核對 43 份編譯輸入；034 前版保存在 spider-low-guard-build-v1/bin。新版 Linux 魔王單打與蜘蛛女 HD 重驗通過；公開／本機封包各四份。未作 Windows／macOS 真機或簽章 |

## 固定輸入

來源頁：<https://dos.zczc.cz/games/%E5%BF%AB%E6%89%93%E8%87%B3%E5%B0%8A/>。

下載物件：<https://binary.dos.lol/aaec980cbef5679fda8274ed3549eccc97229be48221360427718a1e635f9b1d.zip>。

本地原始檔：[快打至尊.jsdos](快打至尊.jsdos)。SHA-256：

```text
aaec980cbef5679fda8274ed3549eccc97229be48221360427718a1e635f9b1d
```

以下結果由 Docker image `python:3.13.7-slim` 的 `zipfile` 與 `hashlib` 直接讀取包內 bytes。它們是檔案事實，不代表執行行為已驗證。

| 包內路徑 | 大小 bytes | SHA-256 |
|---|---:|---|
| `SF.EXE` | 60,702 | `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300` |
| `SF.COM` | 876 | `f194ff7cce7975aabff3f8ec5f92a8b0ca2db0368c33ed29aba7bd7b70f6392e` |
| `NOKEY.EXE` | 1,220 | `5757324e9e4cebeda2527b60c3f04fc8628c2a67aba6123282e57eea1a1e8b8c` |
| `PLAY.BAT` | 14 | `6e9475c883e145ceb9155c6a3b197b96d4bb34153e994fb0b1791ff521b8b6b4` |
| `FIGHT.CFG` | 224 | `d545fcd56015ed8bc61bcf01758aed45cc9008fb4bb7818056bd51881cead086` |
| `AIDATA.DAT` | 576 | `72b10b129c9f557a8b9beb0a400b5636ab690fec5af97b55672980283042f4d8` |
| `CHEAT/AIDATA.DAT` | 169 | `548a2266a585df51584d2d9902a3ab93e8832b43d54dc7d52344dbdc13839593` |

包內 `.jsdos/dosbox.conf` 的 `[autoexec]`：

```text
echo off
mount c .
c:
play.bat
```

`PLAY.BAT`：

```text
nokey /y
sf
```

本輪以 dosgolem 監督佇列執行 `NOKEY.EXE /y → SF.COM`，再由 `SF.COM` 自行 EXEC `SF.EXE`。這條明示鏈已由原生雙打基準走到結果及返回標題；未執行完整 COMMAND.COM，命令解析不宣稱完整相容。`SF.COM` 的全部修改行為及必要性仍未驗證。`.jsdos/dosbox.conf` 的 `svga_s3` 與 `cycles=auto` 是包裝設定；實際已觀察到模式 13h、320×200，正式遊戲速度與音訊仍未驗。

## 外部參考與能力邊界

- `/home/anr2/cht/zeliard/AGENTS.md`：本輪已讀。沿用工作契約，不沿用遊戲狀態、美術決定或 GitHub 授權。
- `/home/anr2/cht/dosgolem/README.md`、`CLAUDE.md`：已讀。基底 HEAD 為 `f79eab6db8c64a524a06535e53e5d32b0bbcf7c8`；接入時工作樹乾淨，1712 個追蹤檔已建立獨立副本並保存逐檔雜湊。共用來源未改動。
- 既有成功案例不能證明本作可執行。首次接入仍需正常啟動與固定預算探針。

## 待確認決策與下一步

使用者最新指定先完成一輪 HD，卡住就跳過。蜘蛛女改採提供原圖與提示詞，交給使用者的其他模型產出；`workplace/spider-model-handoff-v1.zip` 已驗 ZIP CRC 與逐檔雜湊，含 45 一般單格、五張 WIN 單格及 57 張 PNG，共 75 項、2,640,141 bytes。可讀說明為 `workplace/spider-model-handoff-v1/README.md`，整包只留本機。新原圖修復請求及拒絕保留於 spider-restoration-request-v1.json／failure-v1.json，不重試。舊連身衣定版仍保留供參考，新候選回來後再核對。

十一人選角、小丑 026、印第安喬 027、子彈首勝 028、鳳凰首勝 030 及鬼丸首勝 031 已通過限定範圍；十人一般來源共 720 槽、569 組不同 bytes。蜘蛛女後續改採使用者提供並確認的相近低伏稿，034 已接限定切片；原圖片工具拒絕與舊連身衣稿留作歷史。道場候選背景與來源已備妥，029 的相容多場景包確認待回答；確認前不改格式。其餘勝利、完整動畫、替代色盤及標題／選角／結果仍待做。魔王單打過關與結局另驗。019 的 Wine 下一回合與第二人法蘭克的 Wine 勝利仍未通過，不盲目重跑長場。使用者目標仍是「完成快打至尊HD」，不能以選角或一般來源登錄齊全宣稱完成。

使用者指定的[說明書頁面](https://chiuinan.github.io/game/game/intro/ch/c51/sf.htm)及兩張圖片已存檔，版本自述為 1.1。原生入口目前採西側面鍵拳、南側面鍵腳與八方向；Start／Esc 暫停前端，沒有把 Esc 送原版觸發說明書記載的補血。鍵鼠正常路徑已驗，實體手把另驗；完整手把規格仍有未驗部分。

HD 採 B「街機手繪」。現行群組為 `hd-characters-spider-low-guard-v1`，與公開 `assets/hd/characters` 相同，共 65 張透明圖集、1411 個姿態鍵：十人 720 個一般來源槽、蜘蛛女三十個低伏鍵、13 個第二色盤特效鍵及九人 648 個 WIN 入口。蜘蛛女為使用者明確同意的一張靜態近似稿，未對應動作整格回退。來源槽或別名齊全不等於完整動畫；C0h 同時翻轉、頂部裁切、受擊替代色盤及其餘畫面仍待補。正式倍率、像素比例與預設模式尚未定版。

目前 dosgolem 獨立副本有 1719 份來源，前版 1715 份 bytes 不變，新增四份已驗顯示 API 與測試。舊 manifest 保存於 `dosgolem-patched-manifest-v2.json`，現行身分見 `dosgolem-patched-manifest.json`。四個二進位的實際編譯身分見 `bin/*.build.json`；目前勝負切片以 `victory-core-compat-v2`、`native-victory-v1` 及 `windows-victory-v1` 為準。顯示修正基底的四個二進位與 30 份編譯輸入另存 `native-display-opening-v2/build-baseline`，舊收據保留各自版本身分。

舊 Screen／Indexed／RGB API 仍保留線性 320×200 契約；桌面使用另外的只讀顯示快照，同格保存原圖層、完整尾端與實際可見色號。原貌與 HD 全部圖層共用投影，開場 320×192 居中且維持每像素 3×3；跳躍與踢擊實測起點第 7／11／12 列。來源或尾列不符整格原貌。這是限定硬體規格近似，正式像素比例、實機時序與完整 HD 仍未驗。

快捷四格與雙手把已接本機操作入口，預設 R1／R2／L1／L2 對應 1／2／3／4，兩名玩家各自保存。斬的四招可送原版輸入，其他角色尚未驗證的快捷明示拒絕。投技仍需近身，沒有自動走近或改寫座標。實體裝置驗收仍待進行。

AI 可由外部策略表調整的靜態證據已足夠回答可行性；完整研究在 RESEARCH-LOG。短檔作弊效果的因果仍屬強推論，未作同狀態替換實驗，也未新增 AI 難度設定。032 另在練習模式將 AI 輸入清為中立，不替換 AIDATA；關閉即恢復原版決策。使用者已確認首版發布已驗功能，明列其他角色快捷限制；公開引擎包不含原版，本機完整版含原版，含原曲的影片只放本機。

## 現行證據入口

### 鍵盤與首版交付

- [035 鍵盤](docs/spec/035-keyboard-bindings.md)、[036 發行](docs/spec/036-release-packages.md)是本輪契約；`VERSION` 固定同一版號。建置位於 `workplace/keyboard-release-build-v1`，兩平台鍵盤收據位於 `keyboard-native-v1`／`keyboard-wine-v1`。
- 唯一交付根為 `dist-all/v.0.1.0-20261020/`：`patch` 供公開、`full-local` 只留本機、`promo` 為本機原曲影片、`smoke` 保存解壓啟動與操作證據。根目錄 `SHA256SUMS.json` 記錄八個 ZIP；公開 manifest 只列四個引擎 ZIP。
- `smoke/linux-startup` 與 `windows-startup` 各驗公開／本機兩種包；`linux-play-record` 驗正常雙打 HD、預設快捷、失焦、練習與真實錄影，三張畫面另由原檔重組。`workplace/release-boss-single-v1` 重驗正常魔王單打，`release-spider-hd-v1` 重驗低伏切換與回退。
- README 更新故事出處與本次鍵盤、手把、對戰、練習、蜘蛛女 HD 截圖，來源存 `docs/screenshots/source.json`。原版 raw／音樂／原貌收據均不上傳。影片有原版 MIDI 軟體演奏，沒有宣稱原機 DAC／OPL 音色或遊戲串流已完成。

### 蜘蛛女低伏

- 接入提交 `d4e940ed03f3f456cf8c0f138a1fa2c30a76fd1d` 已推送 origin/main，遠端完整提交核對相同；收尾提交只補交接紀錄。
- [034](docs/spec/034-spider-low-guard.md)限定 CONFORMED。使用者最新回覆「ok 同意這版蜘蛛女」，採已展示的相近低伏。三組正常來源與原姓名沿用已驗 124 格證據；同一張外部稿只作水平鏡像及透明留白裁切，候選原 bytes 保持。
- 現行 `assets/hd/characters` 與 `workplace/hd-characters-spider-low-guard-v1` 相同，1411 鍵／65 PNG／二十來源。清單 SHA-256：`078e8a896968688a23556d03f8335252b07a7add204f9b3b8db2341683f4fd0e`。原版資料與 1719 份執行器來源不改動。
- `native-spider-low-guard-v1` 及 `native-spider-low-guard-missing-v1` 各四項、五張，兩份 spider-comparison.json 驗來源、圖層、HUD、陰影、顯示起點、移動回退與切換；README 已收錄實際 HD 擷取。沒有將離線比較圖冒稱原生畫面。
- `spider-low-guard-build-v1` 保存四平台編譯、檔頭核對、完整可用測試／vet 與八檔原封移入 bin 的 promotion.json。033 舊版保存在 first-pass-hd-build-v1/bin。外部 fixture 僅採已完成的針對測試，不宣稱整批舊動畫重驗。
- 其餘十四張外部稿尚未登錄；其他 42 組一般來源、WIN、第二側、替代色盤及完整動畫另驗。此切片未驗 Wine、真機或實體手把。

### 練習模式

- 功能提交 `38088ee6b420f43caeea64c1b146d22ceb59d868` 已推送 `origin/main` 並由 `ls-remote` 核對；程式、規格與 README 圖片均已包含。收尾提交只補交接紀錄。
- [規格 032](docs/spec/032-training-mode.md)限定 CONFORMED。使用者確認補滿並鎖滿血；工具列、F9 與 `-training` 共用請求，在可操作回合邊界啟用。關閉不倒帶回血；曾介入的執行保留 modified。
- `training-evidence-review-v1.json` 綁定 IDA 與同狀態差異探針；`training-core-v3.json`、`training-checks-v3.log` 及 `training-checks-v3.json` 保存核心、七個拒絕邊界、全套程式測試及 vet。舊 HD 外部 fixture 未另供給；訓練 HUD 由原檔獨立重組。
- `training-native-single-v1` 七項、`training-native-v4` 及 `training-wine-v2` 各八項通過。README 的 [training-hd.png](docs/screenshots/training-hd.png)為 Linux 普通雙打入口、練習中暫停的 HD 擷取；原貌單打及所有原始 sidecar 留本機。
- 四份編譯及 38 份來源在 `training-build-v1`；原版 128 檔、dosgolem 1719 來源及生成 HD 素材不因本功能修改。完整勝負過場、魔王全部動作及實體手把另驗。

### 目前鬼丸勝利整合

- 接入提交 `3c899a8f70ef68f3624db8e5cc6c17637509ded8` 已推送 `origin/main` 並由 `ls-remote` 核對。README 的鬼丸 HD 實機截圖與全部圖片均有 Git 追蹤入口，不再嵌入只存在於 workplace 的圖片。
- [規格 031](docs/spec/031-onimaru-victory.md)限定 CONFORMED。2172×724 四格原 PNG、精確內建 imagegen 請求與 DRAFT 審查在 `onimaru-victory-art-v1` 及 `onimaru-victory-evidence-review.json`。候選保留舊 1093 鍵，現行 1165 鍵／61 PNG／十六來源，亦已同步至 `assets/hd/characters`。
- `onimaru-victory-core-v1` 的 12,272 成對邊界、29 個 WIN 取樣與五張原檔重組通過，原狀態與即時 RGB 相同。Linux／Wine 與缺件三案例各七張完整通過；各案例內恢復逐點一致，GPU 勝負字圖各 5,943 變動點、1,701 金色實心點，另目視。不稱跨平台同狀態或完整動畫。
- 完整 internal／cmd 測試及 go vet 通過，記錄為 `onimaru-victory-checks-v3.log`；測試只加 GOMEMLIMIT=1GiB，容器 1.5GiB 的事件沒有 OOM。v1 測資錯誤及 v2 signal:killed 保留，後者未保留終止原因，不宣稱已證實 OOM。
- 四份二進位與 37 份編譯輸入原封移入 bin，收據為 `onimaru-victory-build-v1/promotion.json`；舊鳳凰版保留於 `phoenix-victory-build-v1/bin`。HD 圖與清單的保存變更見 `onimaru-victory-asset-promotion.json`，舊 63 PNG 不變。正常來源與候選檢查的本機工具位於 workplace 的 onimaru-victory 前綴檔案。

### 鳳凰勝利整合基底

- [規格 030](docs/spec/030-phoenix-victory.md)限定 CONFORMED。三格原 PNG、精確內建請求、原檔及初始候選來源綁定於 `phoenix-victory-evidence-review.json`。1093 鍵／60 PNG 保留舊 1021 鍵；一般、特效及前四人的 WIN 不改。
- `phoenix-victory-core-v1` 的 5,952 個成對邊界、八個 WIN 取樣及四張原檔重組通過。Linux／Wine 與缺件三案例各七張通過，勝利切換及下一回合清除完整。各平台內字圖變動 6,881 點、金色實心 1,970 點，另目視，不稱跨平台同狀態。
- 四份已驗候選原封移入 bin，37 份精確編譯輸入吻合，記錄於 `phoenix-victory-build-v1/promotion.json`；舊子彈四份留於 `bullet-victory-build-v1/bin`。自有來源及完整歷史備份為 `workplace/github-phoenix-victory-integration-progress.bundle`，核對記錄為 `github-phoenix-victory-integration-progress-source.json`。備份當時尚未推送；目前遠端見「GitHub 儲存庫與工作目錄」。

### 子彈勝利整合基底

- [規格 028](docs/spec/028-bullet-victory.md)限定 CONFORMED。候選 1021 鍵／59 PNG 保留舊 949 鍵，新增 CCWIN 四組來源與 72 個 WIN 入口。DRAFT、正常診斷與圖集身分綁定於 `bullet-victory-evidence-review.json`。
- `bullet-victory-core-v1` 的 6,018 個成對邊界、11 個 WIN 取樣及五張保存畫格通過獨立重組。Linux／Wine 與缺件三案例各七張通過，勝利切換及下一回合清除完整。兩平台各案例內字圖變動 5,109 點、金色實心 1,552 點，另目視確認；不稱跨平台同狀態。
- 四份已驗候選原封移入 bin，37 份編譯輸入吻合，記錄於 `bullet-victory-build-v1/promotion.json`；舊印第安喬四份保留於 `joe-build-v1/bin`。自有來源及完整歷史備份為 `workplace/github-bullet-victory-integration-progress.bundle`，稽核記錄為 `github-bullet-victory-integration-progress-source.json`。備份當時尚未推送；目前遠端見「GitHub 儲存庫與工作目錄」。

### 印第安喬整合基底

- [規格 027](docs/spec/027-joe-hd.md)限定 CONFORMED。四張原 PNG 與精確內建 imagegen 請求在 `joe-art-v1`，72 槽／44 組來源、949 鍵及舊 877 鍵不變由 Go 嚴格讀取驗證。補證 DRAFT 與來源身分見 `joe-evidence-review-v2.json`。
- `hd-frame-joe-v2` 正常 10／4 的 124 格，兩人完整 bytes 與屋頂吻合。只有第一人出拳時 path 27 使用 5／6／7；第一份雙人拳階段的 11／12 是 path 10，不再當拳擊期望值。原 v1 與追加勘誤保留於 `joe-punch-source-correction.json`。
- `native-joe-v2`／`windows-joe-v2` 各七項、九張完整重組與切換，缺件九張整格原貌通過；每個案例內恢復 HD 逐點一致。真實 HUD 的 INDIAN JOE／96×11 與未知拒絕通過。四個候選及 37 份實際編譯輸入已核對並原封移入 bin，舊版留在 `boss-clown-build-v2/bin`。
- 自有來源及完整 Git 歷史備份為 `workplace/github-joe-integration-progress.bundle`，逐檔與來源核對記錄為 `github-joe-integration-progress-source.json`。原版、衍生美術、研究收據及二進位不入 Git；備份當時尚未推送，目前遠端見「GitHub 儲存庫與工作目錄」。

### 已保留的角色與勝利基底

- [規格 019](docs/spec/019-sarkov-victory.md)為 READY。只新增勝負姓名角色 1，原版核心未改。`sarkov-victory-core-v1` 的 9,290 個成對比較邊界、23 個 WIN 取樣及六個保存畫格通過獨立來源重組；取樣槽 0／2／3／4，槽 1 只有原檔與登錄證據。`sarkov-victory-checks-v1.log` 記錄完整程式套件測試及 go vet 通過。
- 候選 `hd-characters-sarkov-victory-v1` 保留舊 373 鍵與十九張 PNG，新增 BBWIN 的 72 入口與一張 PNG，共 445 鍵。五張姿態、原 PNG 與內建 imagegen 精確提示詞在 `sarkov-victory-art-v1`。勝利文字實際位置為 SARORKOV (96,54,88,11)、WIN (193,54,31,11)，不改原字圖矩形。
- 三個首勝工作均已結束且容器已移除。Linux 與舊素材各七張通過完整重組；Wine 在 2400.01 秒結束，六張具名擷取通過 `animation-comparison-partial.json`，字圖各 6,890 個變動像素／1,981 個金色點。下一回合未觀察到，原失敗檔不改成成功收據；不再輪詢 71285／23441／8314。
- [規格 020](docs/spec/020-bullet-hd.md)限定 CONFORMED。`native-bullet-v1`／`windows-bullet-v1` 各七項、九張完整重組，`native-bullet-missing-v1` 九張整格原貌通過。兩平台各自切回 HD 逐點一致，設定與來源相同；不稱跨平台同狀態。Go 全套程式測試與 go vet、真實 HUD 的 BULLET／62×11 正向與未知角色拒絕測試均通過。
- 子彈在隔離 `feature/bullet-hd` 接入，只補一般戰鬥姓名，不啟用未驗快捷。舊基底不變，517 鍵／25 PNG 群組與四個已驗編譯產物已移入 bin，紀錄為 `bullet-build-v1/promotion.json`。薩爾可夫勝利的 35 份輸入及四個基底二進位另存 `native-sarkov-victory-v1/build-baseline`；019 的歷史收據不當作新二進位全流程驗收。
- 效能樣本 v1 含正常操作中 F12 的 PNG 壓縮與 GPU 讀回，不用來改遊戲。v2 正常 HD 後的 20.003 秒區間未截圖或送新輸入，推進 875 萬步／14 格；15 秒 CPU 樣本中 commandQueue.flush 至 purego.SyscallN 累計約 51.2%，Game.Draw 約 3.37%。v3 僅指定 DirectX，20.001 秒推進 1000 萬步／16 格；CPU 取樣共 9.52 秒，cgocall 5.17 秒，包含 GLFW 事件／游標呼叫。已核對固定 Ebitengine v2.9.9 的環境選項及 Windows 自動選取契約。兩個單次區間不能證明換後端解決速度，也不足以判定驅動原因；沒有修改遊戲、文字、步速或正式後端。輸入雜湊與限制見 `desktop-performance-v3/analysis.json`，兩容器均已移除，診斷不算正式平台驗收。
- 鳳凰[規格 021](docs/spec/021-phoenix-hd.md)限定 CONFORMED。六張採用 PNG、61 組姿態及九份內建 imagegen 請求存 `phoenix-art-v1`；初版 02／04 缺透明分隔，保留拒用紀錄並用 imagegen 修正留白，沒有改 PNG bytes 或放寬登錄器。589 鍵／31 PNG 群組保留原 517 鍵基底；`phoenix-candidate-checks-v1.log` 驗 72 槽、61 組來源與 124 個正常 consumer，`phoenix-integration-checks-v1.log` 完整程式及 vet 通過。真實 HUD 的 PHO HUANG／93×11 與未知拒絕另由 `phoenix-hud-checks-v1.log` 通過；來源審查在 `phoenix-evidence-review.json`。
- 鳳凰在隔離 feature/phoenix-hd 以 8f70fc5 完成，bb5adef 合入進度分支。`native-phoenix-v2`／`windows-phoenix-v1` 各七項、九張通過獨立來源重組與切換，`native-phoenix-missing-v2` 九張整格原貌；Linux／Wine 姓名各 9,207 點變動，另目視確認字形及人物。兩個 Linux v1 因映像缺 xdotool 在零步結束，僅留環境失敗；v2 使用已確認工具及函式庫的既有三平台映像。三個正常工作及容器均已結束，不再輪詢舊 handle。
- 四個鳳凰編譯產物及原編譯收據已原封移入 bin，35 份輸入吻合，記錄為 `phoenix-build-v1/promotion.json`。舊子彈四份在 `bullet-build-v1/bin`，來源身分由 `phoenix-pre-integration-baseline.json` 綁定。來源與完整 Git 歷史另存 `workplace/github-phoenix-integration-progress.bundle`，逐檔身分見 `workplace/github-phoenix-integration-progress-source.json`；原版、衍生美術及二進位不入 Git。
- 鬼丸[規格 022](docs/spec/022-onimaru-hd.md)限定 CONFORMED。六張採用 PNG 與八份內建 imagegen 請求保留於 `onimaru-art-v1`，最後六格的初稿及修正版 Alpha 最大值 254，被原門檻拒絕；獨立重生的 v3 通過，未改 PNG bytes。661 鍵／37 PNG 保留原 589 鍵與所有舊 PNG，`onimaru-candidate-checks-v1.log` 驗 72 槽、66 組來源與 124 個正常 consumer 通過。DRAFT 原文與來源身分見 `onimaru-evidence-review.json`。
- 原 NAME 槽 5 為 ONIMALU／72×11。第六字母遮罩等於 BULLET 的 L，與 SARORKOV 的 R 不同，證據在 `onimaru-source-v1/name-glyph-review.json`；設定 ID onimaru 不變。隔離 feature/onimaru-hd 的 c2f95b6 只補姓名與普通操作工具，b4f7e79 合入進度分支，未改核心、設定或快捷。完整程式測試／vet 及真實 HUD 定向測試均通過。
- `native-onimaru-v1`／`windows-onimaru-v1` 各七項、九張擷取通過獨立重組與切換，`native-onimaru-missing-v1` 九張整格原貌。各自恢復 HD 逐點一致，鬼丸輸出各 17,316 點、姓名 7,128 點變動，造型及字形另目視核對；不稱跨平台同狀態。三個工作及容器均已結束，不再輪詢舊 handle。
- 四個已驗鬼丸編譯產物及原編譯收據原封移入 bin，35 份輸入吻合，記錄為 `onimaru-build-v1/promotion.json`。舊鳳凰四份保留在 `phoenix-build-v1/bin`，由 `onimaru-pre-integration-baseline.json` 綁定。來源及完整 Git 歷史另存 `workplace/github-onimaru-integration-progress.bundle`，逐檔身分見 `workplace/github-onimaru-integration-progress-source.json`；完整 HD 與遠端上傳仍未完成。
- 鬼丸的 `hd-frame-onimaru-v2` 正常 5／4 共 124 格來源通過。v1 七次 Right 的實際對手為 1，逐步圖在 `onimaru-selection-diagnostic-v1`，不能只由非同步畫面推定每次按鍵消費。私有探針以一個普通 Left 選法蘭克，兩人完整 bytes 與屋頂均吻合；來源雜湊由收據綁定，沒有注入狀態。原生驗證工具沿用同一已驗 Left 路徑。
- 嵐[規格 023](docs/spec/023-lan-hd.md)限定 CONFORMED。`lan-source-v1` 59 組／72 入口、`hd-frame-lan-v1` 正常 6／4 的 124 格來源通過。六張採用 PNG 與七份內建 imagegen 精確請求保留於 `lan-art-v1`；八格初稿缺完整透明分隔而拒絕，重排 v2 通過同一門檻，未改原 PNG bytes。DRAFT、正常來源、候選及初始測試身分保存在 `lan-evidence-review.json`。
- 現行 733 鍵／43 PNG 保留原 661 鍵與所有舊 PNG。只新增 LAN 姓名白名單與普通操作工具，設定、快捷、核心及步速不變。完整 internal／cmd 測試及 go vet、真實 HUD 的 LAN／31×11 與未知角色拒絕通過。`native-lan-v1`／`windows-lan-v1` 各七項、九張完整重組，`native-lan-missing-v1` 九張整格原貌；每個案例切回 HD 逐點一致，嵐輸出各變動 24,372 點、姓名各 3,069 點。另目視確認字形及造型，不稱跨平台同狀態。
- 四個已驗嵐編譯產物與原編譯收據原封移入 bin，35 份輸入吻合，記錄為 `lan-build-v1/promotion.json`。舊鬼丸四份保留在 `onimaru-build-v1/bin`，由 `lan-pre-integration-baseline.json` 綁定。自有來源及完整歷史本機備份為 `workplace/github-lan-integration-progress.bundle`，身分見 `workplace/github-lan-integration-progress-source.json`；原版、衍生美術與二進位不入 Git。
- 下一角色金太極的 `kim-source-v1` 有 57 組不同來源、72 入口，固定 SFMAN08.DAT SHA-256 `5579dee3e846d65905db84d769fae4378051e1a5cec74bed509885754cef165c`。`hd-frame-kim-v1` 普通選角 7／4 共 124 格，兩人完整 bytes 與屋頂吻合；私有探針使用第二人普通 Left 三次，身分由 `kim-source-review.json` 綁定。尚無 HD 稿，不外推原生或完整動畫。
- 來源審查見 [薩爾可夫勝利](workplace/sarkov-victory-evidence-review.json)與[子彈](workplace/bullet-evidence-review.json)。子彈階段備份為 `workplace/github-bullet-integration-progress.bundle`，身分見 `workplace/github-bullet-integration-progress-source.json`。完整 HD、Wine 勝利生命週期與正式交付未完成；目前遠端見「GitHub 儲存庫與工作目錄」。

### 薩爾可夫一般姿態基底

- [規格 018](docs/spec/018-sarkov-hd.md)限定 CONFORMED。`native-sarkov-v2`／`windows-sarkov-v2` 各七項、九張擷取通過，正常選角為 1／4，普通行走、蹲、跳、拳擊及暫停切換完整。人物、屋頂、姓名、陰影同格 HD，沒有用快捷或狀態注入。
- 各目錄 `sarkov-comparison.json` 獨立重組全部九張原版來源。暫停三張的核心、來源與設定相同，恢復 HD 的遊戲區逐點一致。Linux 範例的薩爾可夫輸出變動 28,859 點、法蘭克 22,239 點；姓名矩形有 8,712 點變動。姓名另由真實 HUD 的 Go 測試及目視確認 SARORKOV，不以變動數字單獨證明字形。
- `native-sarkov-missing-v2` 使用舊 v8，九張均整張原貌，操作仍正常推進。三個 v1 目錄保留驗證腳本在落地前按拳的診斷與中止紀錄，不當通過；v2 只修輸入順序。
- `sarkov-integration-checks-v2.log` 的完整程式套件測試及 go vet 通過。四個二進位的 35 份精確編譯輸入均吻合，目前檔案在 `bin/`，原始候選編譯收據與移入紀錄在 `sarkov-build-v1/`。舊 be9a6d3 的四個二進位及來源保存在 `native-frank-victory-v1/build-baseline`。
- 本切片不證明薩爾可夫 WIN、替代色盤、快捷、所有動作、其他角色／場景或實體平台與手把完成。原始包及 dosgolem 來源保持不變；完整 HD 目標仍進行中。
- 整合核對見[收尾來源核對](workplace/sarkov-integration-audit.json)。自有來源與完整歷史保存在[Git 備份](workplace/github-sarkov-integration.bundle)，逐檔身分見[來源紀錄](workplace/github-sarkov-integration-source.json)；原版、衍生美術與二進位不入 Git。目前遠端見「GitHub 儲存庫與工作目錄」。

### 勝負切片基底

- 第二人新增證據：`victory-animation-frank-v1` 的 5,534 個成對邊界與 8 個 WIN 姿態取樣通過；`victory-animation-jaan-v1` 的 5,293 個邊界與 13 個取樣通過。五種姿態來源均由原檔重組，尚未稱原生逐格連續動畫已驗。
- `native-frank-victory-v1` 七張擷取已通過，正常時間結束後原版生命 [76,124]、winner word 8004h；抱胸、FRANK WIN、右側勝場及下一回合 [0,1] 正確。兩張 GPU 勝負字圖各有 5,130 個變動像素、1,444 個金色實心像素，原貌／HD／恢復來源相同且切回逐點一致。
- Wine 首次第二人案例在畫格觀測期限結束，原版當時仍持續推進；`windows-frank-victory-v1` 保留失敗。`windows-frank-victory-v2/failure.json` 證實在 1800 秒上限結束，最後約 11.14 億步、1527 格、計時剩 4、生命 76／124，未到勝利。容器已不存在，不再列為執行中或要求輪詢 session 95060；這是驗證期限不足，不能當成產品失敗或通過。完整兩側稽核仍未達成，後續先研究驗證效能，不盲目重跑整場。
- [兩側勝利稽核工具](tools/audit_victory_animation.py)要求兩側核心與第二人 Linux／Wine 全部收據，缺案例即拒絕，目前沒有完整通過報告。該批收據的 35 份編譯輸入及四個二進位已另存 `native-frank-victory-v1/build-baseline`，來源為 be9a6d3，與上方目前整合版分開。
- 勝利動畫研究基底備份為 `workplace/github-victory-animation-progress.bundle`，逐檔身分見 `workplace/github-victory-animation-progress-source.json`。它保存薩爾可夫接入之前的來源；現行進度以上方切片為準。

- [規格 016](docs/spec/016-hd-victory-messages.md)處理最後完整拷貝後的 NAME 直接顯示寫入。原貌也保存完整 WIN，HD 不修改原版勝負、等待或回合規則。HUD 重建的兩份暫存字圖保留在最後光柵層，不修改原背景。
- [規格 017](docs/spec/017-victory-pose-banks.md)以實際 72-entry RAM 表辨識一般／WIN 圖像來源。斬首勝仍保留原槽 3，讀取真正 46×89 的 WIN 圖，而非一般同槽姿勢。未知表拒絕整格 HD。
- `victory-core-compat-v2` 的 1,479 個正常觀測開／關邊界，原版狀態及即時 RGB 相同。首勝與下一回合兩個快照的背景、人物、HUD、陰影、WIN 文字及可見尾端由原檔獨立重組；下一回合快照清除，勝場顯示為 [1,0]。
- `native-victory-v1`／`windows-victory-v1` 均從正常對戰取得首勝，各七張具名擷取。原貌／HD／切回的來源與核心相同；GPU 字圖只寫入原來源矩形，恢復 HD 逐點一致。獨立核對結果保存為各目錄的 `victory-comparison.json`。Wine 不是 Windows 真機驗收。
- 新版 3 群組共 301 個姿態鍵、四份原來源、十五張圖集。舊 157 個鍵及十三張 PNG 不變，七張勝利姿態登錄成 144 個入口；版本 1／2 仍可讀。全套 Go 測試與 go vet 已通過，記錄為 `victory-checks-v2.log`。`native-victory-legacy-v1` 的七張擷取證實舊版 2 缺 WIN 姿態時整張原貌，下一回合可恢復 HD。
- [首勝畫面](workplace/native-victory-v1/victory-hd.png)已目視確認。正常兩側原版文字證據共有兩個不同勝利、四筆重播記錄；不是四個獨立樣本。第二人 HD 已驗 Linux，Wine、完整勝利動畫、平手及單打特殊分支仍未完成動態驗收。
- [勝負稽核工具](tools/audit_native_victory.py)輸出 `workplace/native-victory-audit.json`，核對 128 原檔、1719 份執行器來源、四份實際編譯、301 個姿態鍵及上述核心／視窗證據。自有來源完整備份為 `workplace/github-native-victory.bundle`，提交與逐檔身分見 `workplace/github-native-victory-source.json`；原版、HD 美術、研究資料與二進位不入 Git。

### 薩爾可夫候選與下一步

- [規格 018](docs/spec/018-sarkov-hd.md) READY。`hd-frame-sarkov-v2` 正常選角為角色 1／4；124 個畫格、11 個薩爾可夫槽的實際指標與完整圖像 bytes 吻合 SFMAN02，背景 RAM 全部等於屋頂。v1 的角色 1／5 保留研究身分，不作對法蘭克證據。
- `sarkov-source-v1` 保存 72 個一般入口、45 組不同來源；`sarkov-art-v1` 保存四張採用 PNG、45 張 HD 姿態、全部提示詞及未採用的留白不足稿。內建 image_gen 生成，原 PNG bytes 不修改。[採用稿提示詞](workplace/sarkov-art-v1/prompts.json)可回查。
- `hd-characters-sarkov-candidate-v1` 共 373 個姿態鍵、五份原檔、十九張 PNG。舊 301 鍵及十五張 PNG 不變，新 72 槽由現有 Go 讀取器及 124 個正常 consumer 核對；正式原生仍使用 v8，不能把候選群組稱為角色已完成。
- 姓名原字圖為八字母 SARORKOV、88×11；先前轉錄漏記第二個 R，已由逐列原始遮罩重新核對。設定識別字 sarkov、中文名與設定格式不改。下一步接入一般人物與原字圖姓名，再驗正常原生操作、缺件回退與三平台；WIN 圖像、快捷與完整動畫另驗。

### 顯示修正基底

以下為 5c1bf7c 的已驗顯示版本。現行勝負版沿用其顯示契約，舊收據與二進位分開保存。

- [規格 015](docs/spec/015-native-scanout.md) 對實測顯示配置限定 CONFORMED。`display-core-compat-v1` 的 1,508 個開／關邊界狀態、舊原貌、即時 RGB 及原圖層相同；66 個完整開場快照由原資料與真實 VRAM 尾端獨立重組。
- `native-display-opening-v2`／`windows-display-opening-v1` 各七項、十張擷取與六張 GPU 字圖核對通過。開場完整顯示原第 12 至 203 列，頂端暫存資料不再露出，底四列保留；原貌／HD／切回的來源及畫面逐點一致。
- `native-display-battle-v2` 十七項、十五張擷取及十二張陰影合成通過，含兩人攻擊、移動、跳躍／踢擊、特效扣血、設定重啟與失焦。正常跳躍及踢擊另見第 11、7 列起點，按每格 CRTC 核對。
- `native-display-legacy-v2` 十三項、十一張擷取驗舊版素材及缺件整張原貌。實體手把及其他角色快捷仍未驗。
- `display-checks-v1.log` 保存全套 Go 測試及 go vet；`display-runtime-installed-tests.log` 保存安裝後 API、17 個拒絕條件、保存還原與只讀複本測試。四個 Linux／Windows／macOS Intel／Apple Silicon 二進位已重建，`desktop-build.json` 與 `bin/*.build.json` 綁定實際來源及輸出。
- 稽核入口為 [tools/audit_native_scanout.py](tools/audit_native_scanout.py)，結果 `workplace/native-display-audit.json` 綁定 128 原檔、1719 份來源、四份實際編譯與 46 張具名映射擷取。前版 9623266 與 30 份編譯輸入保存在 `native-rounds-v1/build-baseline`。舊稽核保留當版身分。
- [目前 HD 開場](workplace/native-display-opening-v2/round-hd.png)已目視確認。自有來源備份為 `workplace/github-native-display.bundle`，逐檔身分見 `workplace/github-native-display-source.json`。原版、衍生美術、收據與二進位不入 Git；目前遠端見「GitHub 儲存庫與工作目錄」。
- 完整 HD、後續回合／勝負訊息、其他角色與場景、完整動作、其他模式、實體平台與雙手把、音訊、速度及正式封包仍未完成。正式倍率與預設模式仍未定案。

### 顯示候選基底

以下保留接入前的候選與 9623266 身分，現行以規格 015 收據為準。

- [規格 014](docs/spec/014-mode13-scanout.md) 對候選 API 限定 READY，玩家主入口未修正。原版埠設定與 VGA 公開契約確認起點 3,840 bytes、列距 320、可見高度 192，最後一點為相對 A0000 的 65,279。`display-ports-v1` 保存 67 格與全部埠，`reference.json` 為獨立硬體規格近似；[原版重組預覽](workplace/display-ports-v1/display-010.scanout.png) 不當作原生 HD 截圖。
- `display-runtime-study-v1` 在研究目錄複製正式 1715 檔，原檔逐字不變，另加四份機器／公開 API 與測試，共 1719 檔。正式來源與 `go.work` 未動；候選的 workspace 與完整檔案身分在該研究目錄。
- 候選測試及 go vet 通過，包含完整尾列、不同起點與列距、兩種保存還原、複本不共用，以及 17 種未知映射拒絕。`linear-scanout-api-v2` 由正常選單重走 67 格，逐點等於獨立顯示重組，舊 API 與呼叫前後原版狀態不變。67 格最後四列亦等於原始背景，後續仍須逐格檢查。
- 稽核入口 `tools/audit_linear_scanout.py`／`workplace/linear-scanout-audit.json` 明示原生未接線。原生下一步須將原貌、HD 全部圖層與四列尾端一起映射，不能只裁掉頂端。現行 9623266 四個二進位與 30 份編譯輸入已保存於 `native-rounds-v1/build-baseline`，既有 GUI 收據仍屬目前未修正的顯示版本。
- 候選工具與文件的自有來源備份為 `workplace/github-display-candidate.bundle`，提交與逐檔身分記於 `workplace/github-display-candidate-source.json`。候選來源副本、VRAM、原版預覽及現行二進位均留本機，不加入 Git 或遠端。

### 顯示修正前的原生開場基底

以下為修正前的 9623266 來源及視窗收據；目前程式已依規格 015 套用顯示映射。

- [規格 013](docs/spec/013-hd-round-messages.md) 限定第一回合。IDA 9.4 定位原訊息、數字、橫向窗口與部分背景；`round-draw-v3` 的 66 次訊息、66 次部分背景與 66 次完整常式返回，全部由原檔獨立重組。階段 1 最末格的頂列 FIGHT 暫存拷貝另驗，沒有把 helper 結束當整個常式完成。
- `round-core-compat-v1` 的 1,508 個開／關觀測邊界，狀態、原貌與實時 RGB 相同；保存全部 66 格分層快照，四階段與十二種窗口齊全。原檔、HUD、陰影與開場訊息可獨立重組；正式對戰後訊息與保留列 metadata 清空。其他回合索引只有靜態來源組合，沒有正常動態驗收。
- `native-rounds-v1`／`windows-rounds-v1` 各七項、十張具名擷取；部分 ROUND 窗口、完整 ROUND、FIGHT 與正式對戰清除均通過。每側六張 GPU 字圖擷取核對窗口外完全不變，三組暫停切換的來源與恢復畫面逐點相同。Wine 不代替 Windows 真機。
- 目前 Linux 一般對戰為 `native-round-battle-v1` 十七項、十五張具名擷取，另核對十二張陰影合成；舊版 1 與缺件整張原貌由 `native-round-legacy-v1` 另驗。全套測試與 go vet 使用 `round-checks-v3`，沒有跳過；最初跨平台 image 預設關閉 cgo 的編譯失敗屬環境，改用既有 Linux image 與明示 cgo 後乾淨重跑。
- 四份實際編譯來源及二進位見 `bin/*.build.json`／`desktop-build.json`，目前來源稽核入口為 `tools/audit_native_rounds.py`。陰影基底的四個二進位、26 個精確編譯輸入及舊稽核保存在 `native-shadows-v1/build-baseline`，綁定 `d04670d`；舊收據保留版本身分。
- 開場背景不覆寫頂端十二列；目前原貌與 HD 都沿 oracle 線性 A0000 契約保留此內容，因此開場頂部仍可見資料列。這是實際可見的 oracle 限制，尚未處理，不能以本切片宣稱完整 HD。
- 自有來源保存於 `workplace/github-native-rounds.bundle`，提交及逐檔雜湊見 `workplace/github-native-rounds-source.json`。原版、衍生美術、研究收據與二進位繼續排除；目前工作樹與遠端見「GitHub 儲存庫與工作目錄」。

### 陰影基底

以下陰影版收據保留 `d04670d` 的版本身分，目前版驗收以開場切片為準。

- [規格 012](docs/spec/012-hd-shadows.md) 經來源審查升 READY 後接入，驗證與稽核後限定 CONFORMED。772 次原版繪製與 19 個獨立重組樣本吻合，保留 5,002 次同值寫入。負 X 裁切及整圖跳過只有靜態邊界測試，不冒充正常樣本。
- `shadow-core-compat-v1` 的 456 個邊界在開／關新觀測時原貌、色盤、角色、狀態及步數相同，取得 448 個完整陰影快照，保存 24 個可重組的雙人原版畫格。`shadow-checks-v1` 全套測試及 go vet 通過，沒有跳過。
- `native-shadows-v1`／`windows-shadows-v1` 各十七項通過，各十五張具名擷取完整重組；各十二張高解析陰影擷取另核對原生 alpha 與 GPU 黑色合成。RGBA8 合成量化區間與切回 HD 逐點一致分開驗，沒有放寬切換比較。
- `native-shadow-overlap-v1` 普通走近取得重疊，七張具名擷取、五張陰影合成核對通過，其中三張確有透明度重疊。`native-shadow-legacy-v1` 十三項及十一張具名擷取驗舊版 1 與缺件整張原貌，沒有混入新版柔邊陰影。
- `shadow-match-core-v1` 以普通輸入走完兩次擊倒及第二回合，當時陰影快照完整；結果報紙階段快照清空。此為目前核心的生命週期證據，原生返回標題仍保留下一節基準的版本身分。
- 四個目前二進位與編譯來源由 `desktop-build.json` 及 `bin/*.build.json` 記錄。勝場版的四個二進位、精確來源、舊稽核已保存於 `native-win-markers-v1/build-baseline`，不把舊收據當目前版。最新稽核入口為 `tools/audit_native_shadows.py`，輸出 `native-shadows-audit.json`。
- 自有來源保存於 `workplace/github-native-shadows.bundle`，備份身分及逐檔雜湊見 `workplace/github-native-shadows-source.json`。原版、衍生美術與二進位不納入提交；目前工作樹與遠端見「GitHub 儲存庫與工作目錄」。

### 勝場與完整比賽基底

以下保留勝場版及完整比賽基準的來源與限制，最新陰影版以本節前方的現況為準。

- [規格 011](docs/spec/011-hd-win-markers.md) 限定 READY。獨立來源核對 33 個 HUD fixture、93 點非零拇指圖像及兩側各兩格靜態位置。原生向量重繪按鎖存的 DisplayWins 顯示，保留完整原版圖層；尚未顯示的勝場不移除原貌像素。右側及第二圖示未作正常 GUI 勝場驗收。
- `native-win-markers-v1` 使用目前 Linux 勝場版，普通移動與拳擊取得第一勝，七張擷取逐點重組原版六層。三張暫停切換的核心、色號、色盤、完整快照及即時 RGB 相同，恢復 HD 的遊戲區逐點一致；勝場區確有 HD 替換。全套測試與 go vet 見 `win-markers-checks-v2`，33 個 HUD／19 個特效 fixture 沒有跳過；新增未獲勝區域的拒絕檢查見 `win-marker-coverage-v1`。
- `native-match-v2` 使用另存的擷取診斷基準，普通選單、移動與拳擊走完兩次擊倒、結果報紙及返回標題，八張擷取通過。對戰六張完整原版分層重組一致；結果／標題整個 960×600 區域等於即時原貌，對戰快照清空。其四個二進位及精確編譯輸入保存在 `native-match-v2/build-baseline`，與目前勝場版分開。兩版 gameplay core 來源相同，僅三份前端／HD 呈現檔改變。
- 原生初次 `native-match-v1` 的 900 秒期限不足，失敗與四張部分擷取保留。1800 秒重跑已通過；部分檢查須指定 `--partial`，另寫 comparison-partial.json，不能代替完整比賽收據。直接 Docker 指令目前可用，先前複合主機指令的 socket 拒絕不再列為整個 Docker 工具鏈受阻。
- 陰影已由原檔及 IDA 9.4 追到載入、兩人位置、固定第 178 列與透明繪製端，證據在 `ida-shadow-v1/v2.json`、`sf-shadow-v1/v2.i64` 及 RESEARCH-LOG。尚未作 dosgolem 逐寫對拍或 HD 替換，不宣稱陰影完成。
- 此切片四份編譯來源、原始資料、首勝與歷史完整比賽的核對入口為 `tools/audit_native_wins.py`，輸出 `workplace/native-win-markers-audit.json`。自有來源保存於 `workplace/github-native-wins.bundle`，逐檔來源與備份身分見 `workplace/github-native-wins-source.json`。原版、衍生美術與二進位排除；目前工作樹與遠端見「GitHub 儲存庫與工作目錄」。

### 介面切片基底

下列收據保存勝場擴充之前的版本；四個基底二進位及來源身分另存於 `native-hud-frank-v2`。不能把舊稽核對四份二進位的結果外推到目前勝場版。

- [規格 010](docs/spec/010-hd-battle-hud.md) 限定生命、計時、名字與玩家標記。`hud-draw-v3` 正常雙打取得 1176 次逐點吻合的介面繪製，普通拳擊至擊倒、第二回合；`hud-reference-v5.json` 的最新 33 個 fixture 由原檔及鎖存欄位獨立重組，`hud-evidence-review.json` 通過。
- `native-hud-frank-v2`、`windows-hud-v1`、`windows-hud-frank-v1` 各十六項正常 GUI 通過，各十六張擷取完整重組及切換核對。法蘭克兩案例包含實際扣血；三個暫停案例的來源狀態與恢復後 HD 畫面相同。Linux 取樣的 27,279 個原 HUD 輸出像素已替換。
- `native-hud-legacy-v1` 十三項通過，舊版 1 群組保持原貌介面；缺件時整個 960×600 遊戲區逐點等於原版。
- `hud-core-compat-v1` 比較開／關特效與 HUD 觀測的 456 個邊界，原貌、色盤、角色、狀態與步數相同，取得 448 個完整 HUD 快照。`hud-checks-v2.log` 的全套測試及 go vet 通過，實際載入 33 個 HUD 與 19 個特效 fixture，沒有跳過。
- `desktop-build.json` 及四份 `bin/*.build.json` 核對目前介面版編譯來源、雜湊及 ELF／PE／兩種 Mach-O。`native-hud-audit.json` 核對原始 128 檔、1715 份來源、157 個素材鍵、三個十六項 GUI 與十三項舊素材回退；不代表完整 HD 或實體平台驗收。
- 早期特效二進位與精確編譯輸入保存在 `native-effects-v4`；首版介面 prototype 保存在 `native-hud-frank-v1`。前者供 GPU 取樣修正回查，後者保留玩家標記殘留與擷取側檔遺漏的歷史，不能當作目前介面驗收。

### 特效基底與來源研究

- [規格 009](docs/spec/009-hd-effects.md) 限定 READY。`effect-draw-v1`／`v2` 共 1015 次 blit、483 個完整畫格吻合；`effect-evidence-review.json` 另獨立重組 19 個保存畫格。
- `hd-characters-study-v7` 為版本 2 素材，13 張透明圖集對應 144 個正常來源槽與 13 個第二色盤特效鍵。新圖與提示詞保存在 `hd-effect-art-v1`／`v2`，原版及衍生素材不入 Git。
- `native-effects-v3/receipt.json` 十五項與 `native-frank-effects-v1/receipt.json` 十四項通過。兩次各由正常標題進入雙打，分開驗斬 R1 與法蘭克手動方向／拳特效，不代表法蘭克快捷已開放。
- 兩份 `comparison.json` 分別核對 16／15 張完整分層擷取；特效暫停切換的來源狀態一致，HD 切回逐點相同。斬 1035、法蘭克 5643 個原特效輸出像素已由 HD 替換。
- `effects-tests.log` 驗 19 個真實特效 fixture、第二色盤隔離、幾何拒絕、正常素材及設定；`effects-compatibility-tests.log` 驗舊版素材。`effect-core-compat-v1/receipt.json` 比較觀測開／關共 456 個邊界，原貌、狀態、色盤與步數相同。
- `windows-effects-v1`、`windows-frank-effects-v1` 保留初次等待逾時；單獨重跑後，v2 的畫面比對發現取樣末位差異。改用獨立 GPU 紋理後，`windows-effects-v3`／`windows-frank-effects-v3` 的原貌／HD 切換逐點相同。現行 GUI 已由上方介面版收據取代。
- 前版角色收據及原二進位另保留於 `native-actors-v6`。下列六層角色版、缺件回退與 native-character-audit 均屬前版證據，不能當成目前特效版的完整稽核。

### GitHub 儲存庫與工作目錄

2026-10-20 使用者已建立 [wicanr2/superfighter-remastered](https://github.com/wicanr2/superfighter-remastered)。`git ls-remote origin` 核對遠端 HEAD 與 main 均為 `69f91cd5513625b5942701b7ed7afc35c461cc16`，包含鳳凰首勝及建立儲存庫嘗試的文件提交。先前「遠端未建立」已是歷史狀態，失敗過程保留於 [WORKLOG.md](WORKLOG.md)。GitHub API 仍無法連線，沒有另外取得可見性欄位；授權繼續限私人設定及自有來源與文件。

完整 Git 儲存庫已從 `/tmp/kdzz-superfighter-publish` 移至 `/home/anr2/cht/快打至尊/superfighter-remastered`，不再維護同步副本。父目錄的 `.git` 受環境保護，因此在其下保存可正常操作的完整工作樹。本機 main 已快進至已核對的遠端提交並追蹤 origin/main；舊進度分支及歷史均保留，沒有重寫提交。

搬移文件提交 `c809fbe` 已推送遠端 main 並重新核對。新位置通過 128 原檔、1719 份執行器來源、四份二進位及 37 份精確編譯輸入檢查；六個 Go 套件離線解析、507 個本機 Markdown 引用及三個相容連結通過。沒有遊戲程式變更。

原版包、workplace 及 go.work 已移入本工作樹，父目錄同名符號連結維持舊路徑。這些檔案繼續被 Git 排除。後續程式、文件編輯與 Docker 的 /project 掛載都使用新工作樹，父目錄其他來源只留搬移前快照。

Git 收錄自有程式、規格、歷史整理、RRSAL-1.0、OFL 字型、不含原版畫面的手把設定截圖，以及使用者追加授權的 `assets/hd/` 生成素材與清單。原版檔案、原版色號／色盤、私有 dosgolem 來源、研究收據及二進位不入 Git，未建立 Release 或正式封包。

現行完整歷史備份為 `workplace/github-phoenix-victory-integration-progress.bundle`，核對記錄為 `github-phoenix-victory-integration-progress-source.json`。其 remote_created／pushed 欄位描述備份當時狀態，保留原檔，不改為本次遠端收據。更早的 github-initial、github-native-victory 等 bundle 亦只描述各自切片。

### 穩定文件與早期切片

下列 native-actors、native-character-audit、hd-audit 及瀏覽器收據保留當版結果。不能將其「當時通過」外推為目前勝場版驗收；目前四個二進位的入口以「最新原生勝場與正常流程」為準。

- [RESEARCH-LOG.md](RESEARCH-LOG.md)：啟動鏈、來源差異、輸入候選與重生方式。
- [VERIFICATION-MATRIX.md](VERIFICATION-MATRIX.md)：已驗範圍與未驗項。
- [規格 001](docs/spec/001-queued-entry-interrupts.md)：監督佇列入口修正，限定範圍 CONFORMED。
- [手把草案](docs/spec/002-gamepad-design.md)、[HD 草案](docs/spec/003-hd-design.md)：說明書導出的設計，均為 DRAFT。
- [原生桌面入口](README.md)：`bash tools/build_desktop.sh` 產生三平台中間二進位，玩家以 `-data` 指定原版資料。此共用主機的建置／GUI 驗證均在 Docker。
- [桌面規格 005](docs/spec/005-native-desktop.md)：限定 READY，明定原生視窗、設定、標準手把與三平台界線。
- `workplace/native-actors-v6/receipt.json`、`windows-actors-v6/receipt.json`：目前 Linux 與 Windows PE 各十四項正常入口、屋頂六層 HD、行走、雙跳、新 slot 25 空中踢擊、slot 56 退步、兩人獨立放開、R1、暫停、設定、保存重啟及失焦通過；README 截圖出自 Linux 此輪。Wine 不能代替 Windows 真機。
- 兩目錄的 `comparison.json`：各十三張原生六層擷取逐點重組回原版；各平台內暫停三張原始色號、色盤與定位相同。Linux 範例的 47,978 個原角色輸出像素已替換、489,092 個背景像素改變、35,451 個最後原貌層像素保留。HD 切回遊戲區逐點相同，不宣稱兩平台即時操作是跨平台同狀態。
- `workplace/native-actors-missing-v2/receipt.json` 與 `comparison.json`：目前 Linux 使用舊版缺件素材，十三項正常流程通過；缺件時整個 960×600 遊戲區與當格原貌逐點相同。`native-actors-fallback-v1` 另保存六層版正常道場九項回退。
- `workplace/windows-shift-v1/receipt.json`：只讀 Win32 探針確認左右 Shift 可獨立取得。限定原因與修復契約見規格 005；修復後 Windows 正常雙打已驗獨立放開。
- `workplace/desktop-build.json`：四個角色版二進位 SHA-256、ELF／PE／Mach-O 檔頭、固定依賴與字型來源；每個 `workplace/bin/*.build.json` 保存實際編譯前後一致的來源及輸出雜湊。
- `workplace/native-character-checks.log`：目前角色版的 `go test -count=1 -p 1 ./...`、`go vet -p 1 ./...` 通過，載入真實原版分層與 144 槽素材。`native-actors-v1/source` 已用獨立 module 隔離，避免其部分存檔誤當正式套件。
- `workplace/native-character-audit.json`：目前四個實際編譯收據、十四／十四／十三項 GUI、原始 128 檔、1715 份 dosgolem 及 144 槽群組核對；不包含完整 HD 或實體平台驗收。
- `workplace/hd-checks.log`：原生背景切片當輪的 `go test -count=1 -p 1 ./...` 與 `go vet` 通過，HD 測試載入 16 張原始畫格。
- `workplace/hd-audit.json`：背景版來源、二進位、GUI 收據與原始資料核對；已明確辨識二進位仍使用前版來源快照。它不驗角色試作，角色研究另以 sprite-study-audit 為準。
- [角色分層規格 008](docs/spec/008-hd-characters.md)：限定 READY，已接六層原生呈現。早期 `sprite-draw-v1`／`sprite-layers-v1` 各 1,432 次繪製吻合；後者 716 個五層歷史畫格全部逐點重組相同，與現在六層收據分開列明。
- [觀測規格 007](docs/spec/007-memory-write-observation.md)：限定 CONFORMED；`workplace/write-observer-test.jsonl` 驗同值重寫、指令起點、獨立取消及完整機器狀態不變。沒有改 CPU 或原版資料。
- `workplace/hd-sprite-art-v1/manifest.json`：四張 1448×1086 透明 PNG，共 48 姿態；提示詞及參考表逐組保存，使用內建 image_gen，僅留本機。
- `workplace/hd-actor-preview-v3/receipt.json`：16 個保存狀態、15 個雙人 HD 比較，缺斬 slot 56 時明示缺件。待機、蹲與跳圖已目視；未作原生完整動畫驗收。
- `workplace/sprite-study-audit.json`：獨立重組 16 個分層 fixture、來源不變、兩個新增觀測檔、48 個透明姿態、索引與回填核對通過。
- [即時輸入規格 004](docs/spec/004-live-input-slice.md)：限定 READY。基本輸入收據在 `workplace/input-single-v2/`、`input-versus-v2/`；兩人四招收據在 `workplace/quick-versus-v3/`，後兩者附執行前 provenance。
- `workplace/live-http-v4/receipt.json`：8 項通過，正常雙打入口、雙人拳腳、來源所有權、R1、單人斷線取消快捷、暫停、失聯清理與非法輸入拒絕；API 檢查，不是硬體驗收。
- `workplace/browser-live-v3/receipt.json`：Chromium 12 項通過，正常雙打入口、雙支合成標準手把、設定輸入隔離、R1 不連發、斷線、窄畫面、設定重載及靜態 HD 示範。沒有實體手把或動態 HD 對拍。
- `workplace/live-build.json`、`live-audit.json`：前輪 HTTP 研究入口的來源、二進位與稽核，不能作原生驗收。
- `workplace/sprite-source-v1/evidence.json`：斬／法蘭克各 72 槽圖集，61／57 個不同圖像位置。後續 IDA 與動態證據已確認本輪取樣的完整圖像 bytes；完整姿態覆蓋及錨點仍未完成。
- [背景規格 006](docs/spec/006-rooftop-background.md)：來源位址、完整畫格、背景合成及回退契約；`hd-frame-single-v2`／`hd-frame-versus-v2` 各 124 畫格，`hd-rooftop-study/manifest.json` 保存本機素材與雜湊。
- [互動配置稿](tools/gamepad-preview.html)：可獨立開啟；支援時可讀瀏覽器標準手把，亦可用方向鍵、J、K 預覽，沒有接入遊戲。
- [四招設定資料](tools/quick-moves.js)：四格驗證、逐角色資料、兩人獨立設定、文字鏡像與按下邊緣；即時入口只啟用已驗的斬四招。
- [HD 分層預覽](tools/hd-preview.html)：背景、兩張透明待機圖與展示介面；素材、尺寸、alpha、雜湊及提示詞見 `workplace/hd-layers/`。
- [遊戲資料保存](docs/game-history.md)：兩站來源、原文快照、原圖與招式差異；快照位於 `workplace/manual-reference/` 及 `workplace/spmoves-reference/`。
- [AI 研究](RESEARCH-LOG.md)：原始位址與證據等級；資料統計見 `workplace/ai-data-evidence.json`，IDA 匯出為 `workplace/ida-ai-v3.json`。
- [A 忠實精修](workplace/design/hd-a-faithful.png)、[B 街機手繪](workplace/design/hd-b-painted.png)：imagegen 概念稿，提示詞見 `workplace/design/prompts.json`，來源及雜湊見 `workplace/design/manifest.json`。
- [標題畫面](workplace/probe-startup-if-40m/screen.png)、[選角畫面](workplace/probe-single-click-60m/screen.png)：由 dosgolem 色號及色盤生成，僅留本機。
- [正常首戰](workplace/probe-fight-baseline-190m/screen.png)、[掃描碼按住／放開後](workplace/probe-fight-held-190m/screen.png)、[原版設定頁](workplace/probe-keyboard-settings-65m/screen.png)：已目視；不是手把或 HD 驗收。
- [啟動研究稽核](workplace/research-audit.json)：來源、補丁與 17 份啟動／輸入收據。
- [前輪稽核](workplace/implementation-audit.json)：來源快照及圖片、四招資料行為、文件索引與連結、素材尺寸及 alpha、IDA 輸出與擁有權通過；不涵蓋後續即時入口。

已有原生桌面切片與三平台中間二進位；沒有正式安裝包、macOS 真機收據、完整 HD、遠端或交付包。原始 jsdos 與共用 dosgolem 未改動。
