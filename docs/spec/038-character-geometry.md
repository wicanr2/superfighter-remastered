# 038：角色雙向翻轉與頂部裁切

狀態：CONFORMED，僅限本規格的來源／幾何核對及 Linux 正常取樣。延續 008 的原版定位與同格回退契約，處理現有 HD 因 C0h 或 TopClip 而整格回退的正常擊倒畫面。沿既有版本 1／2／3 素材與 UI，不改背景格式、規則、動畫速度或出招。

## 來源與範圍

固定 SF.EXE SHA-256 為 24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300。SFMAN05.DAT 為 b5b77d590420b92db2d265aa89483de70d58193caf442fd41eba338eb111d653。Go 1.24.13、固定 dosgolem 副本與 Pillow 11.3.0；原檔唯讀。

沿 008 已驗四支 blit 契約。IDA MZ 線性 sub_14665／sub_146E8／sub_1477E／sub_1480A 的原 bytes 在 ida-hd-draw-v2.json，runtime 另由 01B9:42A5／4446 讀繪製後快照，不混用位址。矩形定位保留鏡像的加一像素與成對裁切。

- 正常 native-lan-victory-v2 的 transition-0，法蘭克一般槽 28、105×41、X123／Y80、flags C2h、TopClip 0，來源 SHA 為 341748422e3d562e73ed987ae7c701627ec8f2a3d0cd4360e4794a08410b34a2。它是普通選角與拳擊的擊倒過場。
- 正常 native-kim-v1 的 knockout-0，法蘭克一般槽 27、103×68、X88／Y-9、flags 43h、TopClip 9，來源 SHA 為 3e7e581f067d13967cb0e9d17bc7323f1c3318ac200870c102c9ddd7822e1213。沒有練習模式或狀態注入。
- 兩份原圖層已可重組完整原貌，但舊 Characters.Select 對以上旗標／裁切直接回退。獨立來源重組及 HD 定位等價審查通過後，才可升 READY。

## 擬定資料流與驗證邊界

LoadCharacters 保留已核對來源的私有 packed bytes 供記憶體內核對，不加入 manifest、一般 JSON 或公開遊戲資料。當主角色出現雙向翻轉或 TopClip 時，以既有 Placement 與完整來源像素推算可見覆蓋及色號，逐點對照同格 CPU 原始角色層。只有覆蓋與全部寫入色號一致才允許 HD，來源不符、缺件、壞遮罩或非法裁切仍整格原貌。一般已驗幾何不新增逐幀成本；特效保留既有幾何限制。

HD 繪圖繼續使用同一 Placement、既有兩次 GeoM 翻轉與實際原版 clip，不猜新座標或裁切補畫。資料鏈為原檔 → 受驗姿態與私有來源 → 原版角色層幾何核對 → 既有 HD 合成 → 同狀態切換。設定、存檔、玩家控制與原版狀態不改。

驗收須有原檔／CPU 覆蓋與色號的獨立重組、真實 fixture Go 測試及篡改拒絕、正常原生兩類幾何與同狀態切換、恢復後繼續執行、完整可用測試與四平台精確編譯。其他未知色盤、未對應姿態與全部動畫不因本項完成。

## READY 審查

`workplace/character-geometry-evidence-v1/review.json` 已由原檔及已保存 CPU 層獨立驗證。C0h 案例實檔偏移 76824，2,298 個寫入點；TopClip 9 案例偏移 73286，2,168 個寫入點，全部色號及覆蓋相同。完整影像翻轉／裁切與原 blit 的逐點結果亦相同。前者 origin (124,81)、clip (123,81,229,122)，後者 origin (89,-9)、clip (88,0,192,59)。可沿既有定位進實作，不修改 Placement 或原版繪圖。

新幾何每格均須再次核對原始 CPU 層，不能只因審查的兩張通過就盲目放行。TopClip／左右裁切拒絕負值、超過來源範圍或超過成對寬度；完全裁掉的合法空矩形只在原始覆蓋也空時接受。特效仍限既有翻轉及零裁切。原版 packed bytes 僅在使用者執行期記憶體保留，不外洩至清單或一般觀測檔。

## 實作與限定驗收

已證實：`character-geometry-evidence-v1/review.json` 的兩份原檔／CPU 層逐點重組通過。`geometry_test.go` 以真實素材及完整 CPU 遮罩驗完整群組選擇，並拒絕覆蓋、色號、位置、負裁切、過高裁切與缺層篡改；合法空裁切另為受控單元測試，不外推正常玩家樣本。可用 internal／cmd 測試與 vet 均通過，記錄為 `character-geometry-build-v1/tests.log`。

Linux 原生 `character-geometry-native-c0-v1` 與 `character-geometry-native-top-v2` 均從普通標題、雙打選角、移動及拳擊走至首勝。每案七張既有流程擷取及三張新幾何切換，分別由 `verify_victory_animation.py`、`verify_native_character_geometry.py` 獨立重組原檔、CPU 圖層、HUD、陰影與 CRTC。新幾何的 HD／原貌／恢復維持原狀態，恢復 HD 逐點相同；解除暫停後進下一回合、勝負快照清除。沒有練習鎖血、強制勝利或座標注入。

| 正常原生取樣 | 原始寫入點 | HD 改變的可見角色像素 | 實際定位 |
|---|---:|---:|---|
| C2h／槽 28 | 2,298 | 16,317 | X125／Y80，origin (126,81)，clip (125,81,231,122) |
| 43h／槽 27／TopClip 9 | 2,168 | 14,121 | X88／Y−9，origin (89,−9)，clip (88,0,192,59) |

變動點以三倍呈現的可見原始角色覆蓋計數，只證明畫面實際替換；美術符合完整動畫仍須另驗。

首個 top-v1 已擷取裁切，但自動抓圖在滑鼠按住期間重入 click，後續 mouse_left 等待逾時，沒有完整通過收據。失敗檔原樣保存；僅修正測試腳本的輸入互斥，在相同 image／相同二進位重跑 top-v2，不能把失敗檔改成成功。c0-v1 的成功收據仍綁定當時腳本副本。

三平台四架構的 44 份實際編譯輸入及二進位標頭已核對，候選與晉升記錄在 `character-geometry-build-v1`；開發版仍為未發行的 v.0.1.1-20261020。1483 鍵／66 PNG 角色清單及全部素材 bytes 保持，已發布 v.0.1.0 封包、影片與 tag 不變。

未知／未驗：所有裁切組合、全部動畫、替代色盤、Wine／Windows／macOS 真機及實體手把。本規格不改多場景格式 029，其確認仍待回答。每格核對及整格回退繼續有效，不以兩份成功樣本放行未吻合幾何。完整 HD 目標持續進行。
