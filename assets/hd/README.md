# HD 素材

本目錄保存內建圖片工具生成的 HD 原 PNG，以及角色對應清單。使用者於 2026-10-20 明確要求將 HD 素材上傳至現有 GitHub 儲存庫，因此這批生成圖改為版控。原版 EXE、DAT、FIG、背景色號、色盤、原圖與記憶體收據仍留本機。

| 路徑 | 內容 | 接入狀態 |
|---|---|---|
| [characters/manifest.json](characters/manifest.json) | 60 張角色與特效圖集、1093 個登錄鍵 | 現行角色素材；完整動畫及各角色驗收範圍見 [CONTEXT](../../CONTEXT.md) |
| [backgrounds/rooftop.png](backgrounds/rooftop.png) | 屋頂背景，1923×818 | 已接原生；原版參考色號與色盤不隨 Git 提供 |
| [candidates/dojo.png](candidates/dojo.png) | 道場背景，1922×818 | 候選；[多場景格式](../../docs/spec/029-multi-scene-backgrounds.md)尚待確認 |
| [candidates/spider-coverage.png](candidates/spider-coverage.png) | 蜘蛛女全覆蓋紫色連身衣，1390×1132 | 使用者已選定造型；動作圖集尚未生成，遊戲仍用原貌 |
| [catalog.json](catalog.json) | 每個收錄檔案的 SHA-256、大小、尺寸、原位置與分類 | 核對複製與後續變更；不包含原版圖像資料 |

PNG 逐檔複製，未縮放、去背或重新編碼。角色清單沿用目前遊戲可讀的格式，記錄來源檔名、雜湊與座標；`evidence` 中的本機研究路徑不全部隨 Git 提供。`workplace/` 保留生成請求、原始審查與執行收據，不整包提交。

取得合法原版資料並備妥既有屋頂素材包後，可在專案根目錄指定這份角色包：

```bash
workplace/bin/superfighter-linux-amd64 \
  -data workplace/orig \
  -hd-assets workplace/hd-rooftop-study \
  -hd-characters assets/hd/characters
```

此命令使用另行建置的 Linux 二進位，Windows 與 macOS 使用對應程式。儲存庫未包含二進位、原版資料或屋頂參考色號；只下載儲存庫尚不能直接啟動完整遊戲。建置入口見[主 README](../../README.md)。

上傳授權只改變這批 HD 生成圖的保存位置，不代表取得原作素材的公開散布權，也未建立 Release。原作角色與場景權利仍依原權利人，不能將本專案程式的授權視為原作授權。
