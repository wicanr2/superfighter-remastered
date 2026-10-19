# 005：三平台原生桌面切片

狀態：READY，限定規格 004 的原版輸入與桌面呈現適配。日期：2026-10-19。

## 已確認方向與證據

使用者明確修正「不用 web，就是三平台」。正式玩家入口為 Windows、macOS、Linux 原生桌面程式，直接呼叫 dosgolem public oracle API。既有 HTML、HTTP 工具及收據保留研究用途，不作桌面驗收。

原版 SF.EXE SHA-256 `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`。dosgolem HEAD、IF 補丁、原始輸入與位址空間沿用[規格 004](004-live-input-slice.md)。`input-versus-v2`、`quick-versus-v3` 已證實雙人掃描碼、斬四招及朝向，不增加遊戲規則。Linux GUI 與交叉編譯均在 Docker，交叉編譯不代表其他平台真機通過。

## 最小契約

| 層 | 輸入、狀態與輸出 |
|---|---|
| 原版適配 | 檔案雜湊核對，NOKEY /y → SF.COM → SF.EXE；來源唯讀，可寫資料進使用者資料目錄 |
| 執行 | Ebitengine 2.9.9 原生視窗，每次更新給核心既有 250,000 指令預算；速度仍屬實驗值 |
| 呈現 | 只讀原版 RGB，完整顯示 320×200，工具列在遊戲之外；靜態 HD 不覆蓋對戰 |
| 鍵盤 | 選單用 BIOS／滑鼠，對戰用規格 004 IRQ1 掃描碼；設定攔截事件，恢復前要求放開按鍵 |
| 手把 | 原生標準配置，兩支裝置明確指派不同玩家；拒絕重複指派，非標準配置明示未支援 |
| 快捷 | 各玩家、各角色最多四格，R1／R2／L1／L2 預設 1／2／3／4；可換第五招或留空；實際只啟用已驗斬四招 |
| 所有權 | 鍵盤與手把集合分開，最後來源放開才送 break；新手動變化取消該玩家快捷 |
| 暫停 | Esc／Start 停止核心，不送原版 Esc；設定、失焦釋放來源；斷線只取消該玩家手把、快捷及指派 |
| 設定 | os.UserConfigDir 下的獨立 JSON 原子寫入；兩人角色配置重啟恢復；不保存暫時裝置 index，重啟需重新指派 |
| 結束 | 視窗關閉或測試時限釋放來源、關閉原版執行器；沒有背景伺服器 |

桌面設定格式為版本 1、兩人逐角色四格整數，0 為空。這是未發行的本機切片格式；瀏覽器研究設定不混入桌面資料。未知版本明示錯誤並保留原檔。角色編號及招式順序沿用青衫整理，不冒稱原版內部招式 ID。

## 工具與驗收

- Linux 編譯沿用 `dosgolem-go-ebiten:1.24-r1`，X11／OpenGL 標頭來源為 `/home/anr2/cht/dosgolem/tools/docker/go-ebiten.Dockerfile`。跨平台與 GUI 沿用 `tokugawa-desktop-platforms:go1.24.13-sdk15.5-noble-r1`，已核對 Go 1.24.13、Ebitengine 2.9.9、Clang、Xvfb、xdotool、Wine 及 osxcross。套件複製到專案自有快取後固定版本，避免回寫 image 快取。
- 中間二進位驗 Linux amd64、Windows amd64、macOS amd64／arm64 的實際檔頭與依賴；正式打包另依 dist-all 契約，尚不建立 Release。
- 中文 UI 用 Noto Sans CJK TC 原始 OFL 字型，固定 commit、URL、SHA-256 及授權全文。文字先量測，超出字框用省略號，長裝置名稱不侵入其他按鈕。
- Linux 從正常標題驗雙人選角、兩人拳腳、快捷、暫停、設定保存與重啟、失焦。只從外部送視窗鍵鼠，不注入角色、不載入戰鬥快照。
- 純設定測試、Linux GUI、Windows Wine 啟動及 macOS 真機分開列。合成輸入不等於實體雙手把驗收。

完整回合、其他角色快捷、音訊、正式速度及動態 HD 仍是既有缺口。本規格只授權原生輸入與視窗適配，不猜補原版規則。
