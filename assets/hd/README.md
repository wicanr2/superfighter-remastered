# HD 素材

本目錄保存 HD 生成圖、外部模型候選與角色對應清單。使用者於 2026-10-20 明確要求將 HD 素材上傳至現有 GitHub 儲存庫，因此這批生成圖改為版控。原版 EXE、DAT、FIG、背景色號、色盤、原圖與記憶體收據仍留本機。

| 路徑 | 內容 | 接入狀態 |
|---|---|---|
| [標題人物與字標](candidates/README.md)、[精確提示詞](candidates/title-source.json) | 黑底紫色人物與紅金「快打至尊」透明字標 | 靜態比較候選；未接正式標題與循環換色，見 [046](../../docs/spec/046-hd-title-menu.md) |
| [characters/manifest.json](characters/manifest.json) | 74 張角色與特效圖集、1516 個登錄鍵 | 現行開發素材；包含四人的二十一份特殊技光效。完整動畫及各角色驗收範圍見 [CONTEXT](../../CONTEXT.md) |
| [backgrounds/rooftop.png](backgrounds/rooftop.png) | 屋頂背景，1923×818 | 已接原生；原版參考色號與色盤不隨 Git 提供 |
| [道場候選整理](candidates/README.md) | 道場 PNG、來源雜湊、正常畫格證據與精確提示詞 | 素材已整理；[多場景格式](../../docs/spec/029-multi-scene-backgrounds.md)尚待確認，首輪先跳過接入 |
| [其餘九景](candidates/README.md)、[來源與提示詞](candidates/backgrounds-source.json) | 廳堂、叢林、街道、宮殿、舞廳、港口、石窟、冰原、火車的首輪稿 | 原 scene 與兩個 camera 已由普通雙打補證；保留候選，HD 捲動及正式接入仍未驗 |
| [石窟修稿](candidates/grotto-i10-v2.png)、[舞廳修稿](candidates/auditorium-i8-v2.png) | [來源與精確提示詞](candidates/background-revisions-source.json)，保留首輪原 PNG | 正常捲動比較後改善底線位置，仍未定版或接入 |
| [candidates/spider-coverage.png](candidates/spider-coverage.png) | 蜘蛛女全覆蓋紫色連身衣比較稿，1390×1132 | 舊造型比較保留，現行低伏改採使用者後續確認的外部稿 |
| [蜘蛛女外部候選](candidates/spider/README.md) | 第一批五張圖集及第二批十張補稿，均已本地去背 | normal-01 已獲確認並接三組一般低伏來源；其餘未接 |
| [蜘蛛女低伏來源](characters/spider-low-guard-source.json) | 已確認外部稿、無損鏡像、透明留白裁切與三十鍵來源 | [034 限定接入](../../docs/spec/034-spider-low-guard.md)，一張靜態近似稿，未對應動作原貌回退 |
| [catalog.json](catalog.json) | 每個收錄檔案的 SHA-256、大小、尺寸、原位置與分類 | 核對複製與後續變更；不包含原版圖像資料 |

內建生成 PNG 保留原 bytes。蜘蛛女外部稿先依使用者授權做本地去背，只改背景 alpha，匯入時再逐檔複製去背成品。原始輸入及處理結果的雜湊分開記錄。角色清單沿用目前遊戲可讀的格式，記錄來源檔名、雜湊與座標；`evidence` 中的本機研究路徑不全部隨 Git 提供。`workplace/` 保留生成請求、原始審查與執行收據，不整包提交。

[鬼丸勝利圖集](characters/onimaru-win.png)含四組原姿態的 HD 重繪，正常首勝及 Linux／Wine 切換範圍見[規格 031](../../docs/spec/031-onimaru-victory.md)。此圖已接入，與候選資料夾分開保存。

[金太極](characters/kim-win.png)、[小丑](characters/clown-win.png)及[印第安喬](characters/joe-win.png)新增十五組勝利姿態，正常首勝、Linux 切換與缺件回退範圍見[規格 033](../../docs/spec/033-first-pass-victories.md)。蜘蛛女已接使用者確認的低伏稿，其餘動作仍待補；道場保留候選狀態。

[嵐勝利圖](characters/lan-win.png)新增四組姿態，另兩組與既有一般來源相同，重用已驗圖集；正常 Linux 首勝及切換見 [037](../../docs/spec/037-lan-victory.md)。目前開發版尚未發行，首版 Release 的素材保持原狀。

[鳳凰拳腳光效圖](characters/phoenix-effects.png)保留透明生成原 PNG，兩個第二色盤鍵與正常 Linux 接入見 [039](../../docs/spec/039-phoenix-effects.md)。精確內建 imagegen 提示詞、原檔身分及透明區域登錄保存於[來源清單](characters/phoenix-effects-source.json)。

取得合法原版資料並備妥既有屋頂素材包後，可在專案根目錄指定這份角色包：

```bash
workplace/bin/superfighter-linux-amd64 \
  -data workplace/orig \
  -hd-assets workplace/hd-rooftop-study \
  -hd-characters assets/hd/characters
```

此命令使用另行建置的 Linux 二進位，Windows 與 macOS 使用對應程式。儲存庫未包含二進位、原版資料或屋頂參考色號；只下載儲存庫尚不能直接啟動完整遊戲。建置入口見[主 README](../../README.md)。

上傳授權只改變這批 HD 生成圖的保存位置，不代表取得原作素材的公開散布權。Release 與目前開發版的範圍見[主 README](../../README.md)；原作角色與場景權利仍依原權利人，不能將本專案程式的授權視為原作授權。

[金太極光效圖](characters/kim-effects.png)包含十份第二色盤來源，原 PNG 保持；[來源與精確提示詞](characters/kim-effects-source.json)可回查。普通 Linux 三類光效、切換與舊包回退見 [042](../../docs/spec/042-kim-effects.md)，完整特殊技動畫仍另驗。

[四人特殊技光效](../../docs/spec/044-remaining-special-effects.md)新增鳳凰三鍵、嵐七鍵、小丑八鍵與印第安喬三鍵，六張原 PNG 的來源、精確提示詞及槽位對應見[素材紀錄](characters/remaining-special-effects-source.json)。小丑舊稿中連接失真的三格不註冊，另用分離光影新稿；所有 PNG 保留原 bytes。原版參考、色盤與 CPU 收據只留本機，完整動畫及快捷另驗。
