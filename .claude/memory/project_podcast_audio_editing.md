---
name: podcast-audio-editing
description: 《不標準答案》Podcast 音檔剪輯流程，從 Adobe Audition 原始錄音到成品 MP3
metadata: 
  node_type: memory
  type: project
  originSessionId: 04b96cc0-eb46-4273-bc7b-596919328038
---

# Podcast 音檔剪輯流程

**Why:** 老查每集用 Adobe Audition 分軌錄音（老查軌道1、來賓軌道2），需要自動化處理出成品 MP3。

**How to apply:** 每次有新一集要剪時，照這個流程執行。

---

## 檔案結構

- 原始錄音：`.sesx` 專案檔 + `_Recorded/` 資料夾內的 WAV 分段檔
- 片頭片尾音樂：`/Volumes/AS1000 Plus/片頭片尾/0202mp3.mp3`
  - 片頭：0–13 秒
  - 片尾鋼琴：24:25（1465秒）起到結尾
- 參考成品：`/Volumes/AS1000 Plus/2026/已上線/s1ep7.mp3`
- 輸出目錄：`/Volumes/AS1000 Plus/2026/未上線/SXepXX/sXepXX/`

---

## 完整流程

### 1. 合併分段 WAV
```bash
# 建立 concat 清單，分別合併軌道1（老查）和軌道2（來賓）
ffmpeg -f concat -safe 0 -i track1_list.txt -c copy track1_merged.wav
ffmpeg -f concat -safe 0 -i track2_list.txt -c copy track2_merged.wav
```

### 2. 每軌個別處理
```bash
# 降噪 + 去靜音（>3秒）+ 音量 normalize（-16 LUFS，Podcast 標準）
ffmpeg -i track1_merged.wav \
  -af "afftdn=nf=-25,silenceremove=start_periods=1:start_duration=0.5:start_threshold=-45dB:stop_periods=-1:stop_duration=3:stop_threshold=-45dB,loudnorm=I=-16:TP=-1.5:LRA=11" \
  track1_processed.wav
```

### 3. 兩軌 Mix 合一
```bash
ffmpeg -i track1_processed.wav -i track2_processed.wav \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=longest:weights=1 1,loudnorm=I=-16:TP=-1.5:LRA=11[out]" \
  -map "[out]" mixed.wav
```

### 4. 重新採樣（重要：loudnorm 會產生 192kHz，需降回 48kHz）
```bash
ffmpeg -i mixed.wav -ar 48000 mixed_48k.wav
```

### 5. 截取片頭片尾
```bash
ffmpeg -i "0202mp3.mp3" -t 13 -ar 48000 intro.wav
ffmpeg -i "0202mp3.mp3" -ss 1465 -ar 48000 outro.wav
```

### 6. 串接輸出 MP3（用 filter_complex，不用 concat demuxer 避免 header 寫壞）
```bash
ffmpeg -i intro.wav -i mixed_48k.wav -i outro.wav \
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]" \
  -map "[out]" -c:a libmp3lame -b:a 192k -ar 48000 \
  sXepXX_final.mp3
```

### 7. 壓縮停頓（可選）
```bash
# 把 >0.8 秒的靜音壓掉，讓對話節奏更緊
ffmpeg -i sXepXX_final.mp3 \
  -af "silenceremove=start_periods=1:start_duration=0.3:start_threshold=-45dB:stop_periods=-1:stop_duration=0.8:stop_threshold=-45dB" \
  -c:a libmp3lame -b:a 192k sXepXX_v2.mp3
```

### 8. Whisper 逐字稿
```bash
/Users/ming/Library/Python/3.9/bin/whisper sXepXX_v2.mp3 \
  --model medium --language zh \
  --output_format srt --output_dir <scratch_dir> \
  --word_timestamps True
```
- 40 分鐘音檔約需 60–90 分鐘 CPU 時間
- 輸出 SRT 複製到專案資料夾供老查標記刪除點

### 9. 依時間點切除（老查標記後執行）
老查用 SRT 逐字稿標記要刪除的時間段，提供格式：
`HH:MM:SS – HH:MM:SS 說明`
然後用 ffmpeg 分段截取再重新串接。

---

## 注意事項
- `loudnorm` filter 輸出會變成 192kHz，串接前**必須重新採樣到 48kHz**
- 串接三段時用 `filter_complex concat`，不要用 `-f concat` demuxer（會導致 MP3 header 時長錯誤）
- 片頭片尾要同樣 `-ar 48000` 才能正確串接
