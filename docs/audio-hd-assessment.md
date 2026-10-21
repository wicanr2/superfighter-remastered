# 音樂與語音 HD 評估

原版播放已依 [050](spec/050-original-audio-playback.md)接入。它保留原 MIDI 與 PCM，尚未製作重新編曲、降噪或新配音。來源檔與轉換音訊只留本機，不加入 Git 或引擎包。

## 音樂

`SF000.MUS` 為 172,513 bytes，SHA-256 `78af89020939bc7f2013f3869332aae1a67a2600c14ec7820146599e31cdaeda`。十五段完整 SMF 均為 format 0、一軌、division 240。原播放入口、停止與 end-of-track 循環已由 IDA 9.4 查證，播放器依實際請求的完整 MIDI 雜湊切歌，沒有用場景猜曲目。

正式本機 OGG 用固定 TiMidity++ 2.14.0／FluidR3_GM 演奏，48 kHz 雙聲道、Vorbis q5。保留旋律、節奏與配器指令，音色是軟體音源近似，沒有聲稱原機 OPL 錄音或已完成 HD 配樂。循環時長由 MIDI tempo／end tick 計算，交界有 5ms 收尾。

未來若重編，可保留曲目主題並先做對照樣本，再決定音色與編制。本輪沒有替使用者選擇新配樂風格。

## 語音與音效

十七個 `FIV-*.PPM` 共四十筆 Compact PCM。原 ISR 的高／低半位元組讀法已證實是 unsigned 四位元線性 PCM，沒有差分累加；原播放包裝要求 8000 Hz。前版「解碼／取樣率未知」的假說已由 050 的位址、bytes 與資料流取代。

現在以原請求播放原 PCM，轉為 48 kHz OGG 不會補回原錄音缺失細節。PIT 量化、seed byte 與尾端閘門為硬體規格近似，沒有逐週期或逐波形對拍聲明。降噪、音量修復及重配音尚未實作，需要先聽樣本並確認表演取捨。

## 本機準備與使用

[來源清單](../internal/originalaudio/sources.json)只含十八原檔、55 段資料的偏移與雜湊。[轉換工具](../tools/prepare_original_audio.py)核對原檔後輸出十五首音樂與四十段語音／音效；每段保留命令、時長、峰值與 SHA。使用既有 `kol-music:timidity2.14-fluid3.1-r1` Docker image，原版目錄唯讀掛載，輸出父目錄須已存在且屬 UID 1000。

```sh
python3 tools/prepare_original_audio.py --original-root /orig --output /project/workplace/original-audio-ogg
```

以上命令在容器內執行。音源固定為 `/usr/share/sounds/sf2/FluidR3_GM.sf2`，工具會核對 SHA，不接受未鎖版音源。正常玩家可用已準備的本機音訊包匯入：

```sh
superfighter-linux-amd64 -data game-data -import-audio 原音OGG目錄
```

匯入完整驗證 55 段後才建立使用者目錄，拒絕覆寫。也可用 `-audio-assets` 指定完整音訊目錄；本機完整版從 `assets/audio/original/` 自動載入。公開引擎包沒有原音，未匯入會顯示「原音未匯入」。右下角開關控制靜音，`-mute` 可預設靜音；靜音保持播放位置，暫停／失焦／設定頁暫停音訊。開關只保留本次執行。

技術驗證包含 55 段非靜音與無削波、來源拒絕、原音觀測不改核心，以及 Linux 虛擬裝置實錄。真機、全部曲目人耳抽聽與 HD 聲音美化另見 [工作清單](../WORKLIST.md#人工驗證)。前版含原曲推廣片只留本機，沒有隨 Release 提供。
