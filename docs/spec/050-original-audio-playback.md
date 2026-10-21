# 050：原版音樂、語音與音效播放

狀態：限定 CONFORMED。來源、播放接線、Linux 虛擬音訊與以下驗證完成；真機／人耳及音樂／語音 HD 美化不在完成聲明。使用者於 2026-10-21 明確選擇同輪加入原版音訊播放。沿已確認的 dosgolem 核心，只讀音訊請求，播放原 MIDI 與原 Compact PCM；不改遊戲規則、亂數、音效卡偵測或硬體 driver。已完成切歌、停止、循環與 PCM 解碼的最小充分來源審查。

## 原始證據

SF.EXE SHA `24b23d41c5fe6015d211b601e44b4e030677363f7232adcf9999c9ddd80d8300`，唯讀正式 sf-hd-draw-v2.i64 SHA `5a122f625e659633f1e29ea1cb024fb4b1c31405031bf90d92dfe115ac00e2ca`。工具為專案既有 IDA 9.4／292 函式、Go 1.24.13 與固定 TiMidity++ 2.14.0／FFmpeg 5.1.9。新增證據保存在 `workplace/hd-batch-integration-v1/audio-research-v1/` 與 `audio-cues-v1/`，原 DB、名稱及 bytes 不改。

| 等級 | 原始定位與證據 |
|---|---|
| 已證實 | SF000.MUS 為十五段完整 SMF，原讀取 sub_10181 由 SI 選原始偏移／長度表，再呼叫 sub_18318。正常標題／選角／對戰讀到檔內偏移 18779／26918／59025，對應 MIDI 1／2／5。不能據此推定其餘場景的固定表 |
| 已證實 | sub_18318 先呼叫 sub_18381 停音，再由原參數 DS:SI 呼叫 INT 61h AH=1；停止入口為 sub_18381。觀測點在內部停音之後，避免新曲立即被舊停止事件蓋掉 |
| 已證實 | sub_18945 的 18949h..1895Ch 對 FF 2F 00 恢復該軌保存的起點，為原 MIDI 循環；新播放器依 SMF tempo／division／end tick 重播循環，交界採 5ms 收尾以免點擊聲，為軟體演奏近似 |
| 已證實 | sub_1981E 由 AX 高位選四個已載音效 bank、低六位選偏移表；BX 為原播放控制、CX 為次數。sub_19873 直接使用 ES:DI。普通選單、回合與拳擊已觀察到完整 Compact PCM 標記與有效來源指標 |
| 已證實 | Compact PCM 記錄有 32-byte 表頭，檔內 +1Bh 的 word 為 packed payload 長度。原 ISR 的 IDA MZ linear 198F2h..1990Dh／198DDh..198ECh 交替取高半位元組與低半位元組左移四位，為 unsigned 四位元線性 PCM，沒有差分累加。普通播放包裝固定要求 8000 Hz |
| 硬體規格近似 | 新播放器以 8000 Hz 請求率解碼，輸出 48 kHz 雙聲道 OGG。PIT divisor 量化、初始 seed byte 與尾端閘門不宣稱逐週期或逐波形相同；不展開硬體 ISR timing RE |

以上皆為 IDA MZ 線性位址。主程式可用等價 `01B9:IP` 觀測；driver 的實際 CS 由執行期暫存器取得，不能把 CS 相對 operand 誤套主段。

## 載入與播放契約

- 正式音訊資產採 Ogg Vorbis，來源、轉換命令、取樣率、聲道、時長與 SHA 分開記錄。原音不加入 Git、引擎公開包或 Release；本機完整版可包含已核對原音。
- 音樂沿既有本機影片已用的 TiMidity++／FluidR3_GM 演奏原 MIDI，不重寫旋律、不稱原機 OPL 音色或已完成音樂 HD。語音／音效沿原四位元 PCM，不新配音、不聲音複製。
- 只在原播放入口及停止入口產生事件；按完整來源雜湊選音訊，不按畫面、角色檔名或計時猜 cue。未知來源不播放，不能沿用上一段語音。
- 暫停、失焦、關閉設定與結束要能停止／恢復音訊，不改原版狀態。保持既有鍵位，另提供可見原音開關。
- 資料匯入／音訊轉換與原版來源保持唯讀。公開引擎的原音匯入流程須明列工具需求；未匯入時明示，不要求玩家取得本專案私有音訊。
- 原音 registry 在 `internal/originalaudio/sources.json`，只含十八個來源檔及五十五段音訊的檔內偏移、長度與 SHA。轉換工具為 `tools/prepare_original_audio.py`；播放器沿 Ebitengine 2.9.9 既有 OGG／Oto API。原音開關只影響前端播放，本次不改既有設定格式。

## 最後集中驗證

十五 MIDI／四十 PCM 的來源、完整解碼、非靜音、峰值及 OGG 完整性；原播放事件與新事件同序；音訊觀測不改正常核心狀態；正常標題→選角→對戰切歌、語音／拳腳、暫停／恢復／靜音、返回與缺件。Linux 音訊裝置實際輸出另錄 loopback，Wine 取代表樣本；真機與人耳確認分開記錄。
## 驗收收據與限制

本機 original-audio-ogg-v2 的 55 段全部完整解碼、非靜音且 clipping ratio 0；首輪音源增益造成削波的輸出保留為失敗，降低實際增益後重新轉換，沒有放寬標準。音源 SHA 與每段命令、時長、OGG SHA 保留。完整載入、未知鍵／損壞整組拒絕、安全匯入與 CLI 拒絕覆寫通過。

原音觀測開／關的 188 次固定測試時鐘成對記憶體／暫存器比較通過。audio-final-v4 的正常標題→選角→對戰讀到 music-01／02／08、三次音樂與八次語音請求、未知拒絕 0，普通拳腳後語音計數增加。Oto→ALSA pulse→私有 PulseAudio monitor 的 167.18 秒實錄，以 parec 48 kHz 樣本計數對時；暫停／靜音 RMS 0、恢復及跨循環非靜音、峰值 17581、削波 0。收據為 receipt.json／audio-comparison.json，實錄只留本機。原貌／HD 切換不重啟或改 cue。

四架構編譯與本機 55 OGG 封包完整性通過；Wine 驗普通視覺與本機音訊 bank 載入／啟動，沒有驗 Wine 的音訊裝置輸出。Windows／macOS 真機、喇叭與人耳仍待人工；原 MIDI 軟體音色、5ms 接縫與名義 PCM 時長均為近似。沒有原機逐波形或逐週期聲稱，也沒有新作 HD 配樂／配音。
