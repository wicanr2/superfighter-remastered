# 019：薩爾可夫勝利姿態與文字

狀態：READY。日期：2026-10-20。六個正常來源畫格、五組 WIN 原圖、透明 PNG 與 445 鍵候選已完成來源審查。承接[一般姿態](018-sarkov-hd.md)、[勝負文字](016-hd-victory-messages.md)與[獨立 WIN 來源](017-victory-pose-banks.md)，本輪限定薩爾可夫第一人正常勝利；完整動畫、第二人與其他分支另驗。

## 原版來源與正常證據

- 原檔 `BBWIN.FIG` 共 17,657 bytes，SHA-256 `bf9aaca05512785be194558ee45b5e4dcba2b122583d83f9f63e3d577c5cac3d`。沿用固定 SF.EXE `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`、NAME.XBB `60c0bbe367e44ab9fda512df2ba93ad62d70147df90079d07ff15818f21bad82` 與既有 1719 檔 dosgolem 副本。完整輸入身分見 `workplace/sarkov-victory-evidence-review.json`。
- 已證實於原檔：表在檔案偏移 60h，圖像基底 180h，72 個有效入口對應五組不同 bytes。首 96 bytes 與 SFMAN02.DAT 的 AC8h 正常色盤相同。這是檔案偏移，不能當成 runtime segment:offset。
- 已證實於正常樣本：`sarkov-victory-core-diagnostic-v1` 從正常標題選角進入 1／4 雙打，普通方向與拳鍵取得第一人勝利。winner word 為 0001h，生命 124／0、計時 21。未注入生命、座標、勝負或亂數。這是單核心來源診斷，不稱觀測不改狀態的成對驗證。
- 原始 72-entry RAM 表辨識及來源 bytes 沿用 017。勝利取樣取得槽 0、2、3、4，對應 BBWIN.FIG；槽 1 只有原檔及靜態登錄證據。六個保存畫格須由原檔、背景、陰影、介面、文字與顯示尾端獨立重組。
- 已證實於字圖 consumer：勝利文字依次使用 NAME 槽 1 與 17。槽 1 為 `SARORKOV`，矩形 (96,54) 至 (184,65)，runtime caller IP 39DCh、source SI 01FEh；WIN 為 (193,54) 至 (224,65)，caller IP 39F9h、source SI 368Ch。定位、完整來源 bytes 與 SHA-256 均保留在凍結快照，不以新名稱替代原定位。下一回合勝利快照清空，顯示勝場為 1／0。

## 呈現與資料契約

- 沿用版本 3，正常圖像與 `source_bank=victory` 分開，色盤群組仍為 0。不改原槽、角色座標、碰撞、輸入、動畫時序或設定格式。未知來源、替代色盤、未支援幾何與缺件沿用整格原貌回退。
- 五張勝利稿按原像素姿勢順序生成，沿用已確認的街機手繪風格與薩爾可夫造型。2172×724 透明 PNG 及精確內建 imagegen 提示詞在 `workplace/sarkov-victory-art-v1`，保留原 PNG bytes。透明分隔、外緣、五個姿態矩形及完整 72 入口須通過嚴格讀取。
- `hd-characters-sarkov-victory-v1` 保留舊 373 鍵及十九張 PNG，加入 72 個 WIN 入口與一張 PNG，共 445 鍵、二十張 PNG、六份原來源。登錄齊全不代表每個動作或逐格動畫已驗。
- 高解析勝負文字只補角色 1 的 `SARORKOV` 標籤，位置、尺寸、caller、完整來源與最後圖層均繼續由既有選擇器驗證。一般戰鬥姓名沿用 018；其他角色白名單不擴充。
- 原始資料 → 來源表辨識 → typed Sprite／VictoryState → 嚴格資產與字圖選擇 → 原生 GPU → 原貌／HD 切換的鏈必須完整。這次只改呈現，存檔與兩人快捷設定不變，並由切換快照核對。

## 驗收閘門

1. 審核診斷的六個原版畫格及五組 BBWIN 原圖。未知字圖與缺 WIN 的既有素材在診斷中明示拒絕，不把拒絕當成資料缺陷。
2. Go 讀取全部新入口，核對舊資料與 PNG 不變；以真實勝利快照驗 SARORKOV／WIN 的字圖來源及矩形，錯來源、角色與位置仍拒絕。
3. 正常核心及 Linux／Wine 視窗取得第一人薩爾可夫勝利，獨立重組原版，驗人物／文字同格 HD、原貌切換、恢復逐點一致及下一回合清除。原生流程不由單核心診斷取代。
4. 使用缺薩爾可夫 WIN 的 373 鍵舊群組，驗正常一般對戰可 HD、勝利整張原貌、下一回合恢復 HD。核對四個編譯產物及精確輸入；不以交叉編譯代替真機。

研究及素材工具為 [來源參考](../../tools/victory_pose_reference.py)、[WIN 登錄](../../tools/prepare_victory_characters.py)與[正常核心](../../tools/victory_core_receipt.go)。原版、衍生美術與收據只留本機，不加入 Git 或公開產物。來源與驗收不足的部分保留 unknown，不藉 HD 能顯示升級為原版 parity。
