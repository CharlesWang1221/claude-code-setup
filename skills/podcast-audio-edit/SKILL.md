---
name: podcast-audio-edit
description: 《不標準答案》Podcast 音檔全自動剪輯流程。當用戶說「剪音檔」「幫我剪這集」「處理音檔」「podcast 剪輯」「剪 ep」「剪輯音檔」「出這集」時，立即執行此 skill。輸入 Adobe Audition .sesx 專案資料夾，自動完成：分軌合併、降噪、normalize、加片頭片尾、壓縮停頓、Whisper 逐字稿，輸出成品 MP3。
---

# Podcast 音檔自動剪輯

## 概覽

這個 skill 處理《不標準答案》Podcast 每集的音檔後製流程，從 Adobe Audition 的原始錄音檔，一路輸出到可上線的 MP3 成品，並附上逐字稿供人工標記刪除點。

---

## 固定設定

```
片頭片尾音樂：/Volumes/AS1000 Plus/片頭片尾/0202mp3.mp3
  - 片頭：0–13 秒
  - 片尾鋼琴：24:25（1465 秒）起到結尾

Whisper 路徑：/Users/ming/Library/Python/3.9/bin/whisper
暫存目錄：session scratchpad

輸出格式：MP3 192kbps 48000Hz
Normalize 標準：-16 LUFS（Podcast 國際標準）
```

---

## 執行流程

### Step 0：確認輸入

用戶給的路徑可能是 `.sesx` 專案檔或資料夾。從路徑找到 `_Recorded/` 資料夾，列出所有 `.wav` 檔確認軌道數量與時長：

```bash
ls "<專案路徑>/_Recorded/"
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "<file>" | awk '{printf "%02d:%02d:%02d", $1/3600, ($1%3600)/60, $1%60}'
```

確認軌道命名（通常「轨道 1」= 老查、「轨道 2」= 來賓），詢問來賓姓名後繼續。

---

### Step 1：合併分段 WAV

每集錄音通常被切成多段（因中途暫停），分別為每條軌道建立 concat 清單並合併：

```bash
# 建立清單
printf "file '%s'\n" "<_Recorded>/轨道 1_001.wav" "轨道 1_002.wav" ... > "$SCRATCH/track1_list.txt"
printf "file '%s'\n" "<_Recorded>/轨道 2_001.wav" "轨道 2_002.wav" ... > "$SCRATCH/track2_list.txt"

# 合併
ffmpeg -y -f concat -safe 0 -i "$SCRATCH/track1_list.txt" -c copy "$SCRATCH/track1_merged.wav"
ffmpeg -y -f concat -safe 0 -i "$SCRATCH/track2_list.txt" -c copy "$SCRATCH/track2_merged.wav"
```

---

### Step 2：每軌個別降噪 + Normalize（不去靜音）

**重要：靜音只能在 mix 之後統一刪除。** 若分軌各自去靜音，兩軌移除的靜音位置不同，mix 後聲音對點會跑掉。

```bash
ffmpeg -y -i "$SCRATCH/track1_merged.wav" \
  -af "afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11" \
  "$SCRATCH/track1_norm.wav"

ffmpeg -y -i "$SCRATCH/track2_merged.wav" \
  -af "afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11" \
  "$SCRATCH/track2_norm.wav"
```

---

### Step 3：兩軌 Mix 合一，再統一去靜音

先 mix，再對 mix 後的整軌去靜音，確保兩人聲音對點不跑：

```bash
# Mix
ffmpeg -y \
  -i "$SCRATCH/track1_norm.wav" \
  -i "$SCRATCH/track2_norm.wav" \
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=longest:weights=1 1[out]" \
  -map "[out]" \
  "$SCRATCH/mixed_sync.wav"

# 統一去靜音 + 最終 normalize
ffmpeg -y -i "$SCRATCH/mixed_sync.wav" \
  -af "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-50dB:stop_periods=-1:stop_duration=2:stop_threshold=-50dB,loudnorm=I=-16:TP=-1.5:LRA=11" \
  "$SCRATCH/mixed.wav"
```

---

### Step 4：重新採樣（重要）

`loudnorm` filter 會將輸出提升至 192kHz，串接前必須降回 48kHz，否則 MP3 時長會出錯：

```bash
ffmpeg -y -i "$SCRATCH/mixed.wav" -ar 48000 "$SCRATCH/mixed_48k.wav"
```

---

### Step 5：截取片頭片尾

片頭長度：**5 秒**（不是 13 秒）。

```bash
MUSIC="/Volumes/AS1000 Plus/片頭片尾/0202mp3.mp3"
ffmpeg -y -i "$MUSIC" -t 5 -ar 48000 "$SCRATCH/intro.wav"
ffmpeg -y -i "$MUSIC" -ss 1465 -ar 48000 "$SCRATCH/outro.wav"
```

主體音檔也需要從「回來啦」開始切，去掉前面的測試音（「好了」「可以囉」等收音前雜音）。用戶通常會告知「回來啦」在某個參考檔案的時間點，用以下公式反推切點：

```
主音檔切點 = 用戶說的時間點 - 參考檔片頭長度
例：v3 的「回來啦」在 0:20，v3 片頭 13 秒 → 主音檔從 0:07 開始切
```

```bash
ffmpeg -y -i "$SCRATCH/mixed_sync_48k.wav" -ss <切點秒數> "$SCRATCH/main_trimmed.wav"
```

---

### Step 6：串接輸出 MP3

**必須用 `filter_complex concat`，不能用 `-f concat` demuxer**（後者會導致 MP3 header 時長計算錯誤，檔案看起來只有一半長度）：

```bash
OUTPUT="<專案資料夾>/sXepXX_final.mp3"
ffmpeg -y \
  -i "$SCRATCH/intro.wav" \
  -i "$SCRATCH/mixed_48k.wav" \
  -i "$SCRATCH/outro.wav" \
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]" \
  -map "[out]" \
  -c:a libmp3lame -b:a 192k -ar 48000 \
  "$OUTPUT"
```

驗證時長：
```bash
ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT" | awk '{printf "%02d:%02d:%02d\n", $1/3600, ($1%3600)/60, $1%60}'
```

---

### Step 7：壓縮停頓（選用）

把對話間過長的停頓壓短，讓節奏更緊湊：

```bash
ffmpeg -y -i "$OUTPUT" \
  -af "silenceremove=start_periods=1:start_duration=0.3:start_threshold=-45dB:stop_periods=-1:stop_duration=0.8:stop_threshold=-45dB" \
  -c:a libmp3lame -b:a 192k \
  "<專案資料夾>/sXepXX_v2.mp3"
```

---

### Step 8：Whisper 逐字稿

以背景行程跑，完成後告知用戶：

```bash
WHISPER="/Users/ming/Library/Python/3.9/bin/whisper"
"$WHISPER" "<v2.mp3路徑>" \
  --model medium \
  --language zh \
  --output_format srt \
  --output_dir "$SCRATCH" \
  --word_timestamps True &
```

Whisper 完成後，把 `.srt` 複製到專案資料夾：
```bash
cp "$SCRATCH/sXepXX_v2.srt" "<專案資料夾>/sXepXX_逐字稿.srt"
```

- 40 分鐘音檔約需 60–90 分鐘 CPU 時間
- 等進程結束再通知用戶（用 `while kill -0 <PID>` 監控）

---

### Step 9：等用戶標記刪除點

逐字稿出來後，告訴用戶：

> 逐字稿在 `sXepXX_逐字稿.srt`，用任何文字編輯器打開。
> 找到要刪的段落，提供時間點格式：
> `HH:MM:SS – HH:MM:SS 說明`
> 丟給我，我幫你切掉。

---

### Step 10：依時間點切除（用戶提供後執行）

把保留的段落截出來再重新串接：

```bash
# 例如刪除 00:05:23–00:05:41，保留其他段落
# 截出 Part 1：0 到 5:23
ffmpeg -y -i "$INPUT" -t 323 -c:a libmp3lame -b:a 192k "$SCRATCH/part1.mp3"
# 截出 Part 2：5:41 到結尾
ffmpeg -y -i "$INPUT" -ss 341 -c:a libmp3lame -b:a 192k "$SCRATCH/part2.mp3"
# 串接
ffmpeg -y -i "$SCRATCH/part1.mp3" -i "$SCRATCH/part2.mp3" \
  -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1[out]" \
  -map "[out]" -c:a libmp3lame -b:a 192k "$FINAL_OUTPUT"
```

多段刪除就多截幾段再一次串接。

---

## 環境需求

- `ffmpeg`：`brew install ffmpeg`
- `openai-whisper`：`pip3 install openai-whisper`
- 硬碟空間：每集約需 2–3GB 暫存空間（WAV 中間檔）
