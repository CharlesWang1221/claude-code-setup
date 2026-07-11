---
name: project-fb-promo-pipeline
description: FB 預告動畫影片 Pipeline：從 Podcast 音訊生成 CSS 動畫解說影片，輸出 9:16 MP4 供 Facebook Reels / Instagram 上傳
metadata: 
  node_type: memory
  type: project
  originSessionId: d80eeff0-d9a1-4d7c-83a6-ead8f6dec26e
---

# FB 預告動畫影片 Pipeline

觸發詞：「做FB預告」「做預告」「做動畫影片」「做宣傳影片」

## 完整流程（共 5 步）

### Step 1 — 讀取素材
從該集的 `video-projects/sXepY-short/` 取得：
- `03-edited/edited.mp4` — 剪輯後的影片（含音訊）
- `02-transcript/edited.srt` — 字幕（抓字幕時間點和台詞）
- `06-publish/title.txt` — 標題（了解集數主題）

### Step 2 — 規劃場景
- 根據 SRT 內容將 42 秒切成 6 個場景（每場 7 秒）
- 每個場景對應一個 3D CSS 動畫視覺元素：
  - Scene 0：旋轉攝影機 Cube（開場 + 節目資訊）
  - Scene 1：Flip Card（問題/懸念）
  - Scene 2：Parallax 分層（職場/情境）
  - Scene 3：Orbit 軌道環（公共/多元）
  - Scene 4：Before/After 傾斜面板（對比）
  - Scene 5：浮動手機（結尾 CTA）
- 字幕時間點直接對應 SRT 原始秒數

### Step 3 — 產生 HTML
執行：`python tools/fb-promo/build_html.py <episode_dir> /tmp/output.html`

關鍵設計規格：
- 尺寸：1080×1920（9:16）
- 色彩：`--navy:#112D4E` / `--teal:#3F72AF` / `--coral:#E07A5F`
- 字型：PMingLiU（標題）/ Microsoft JhengHei（內文）/ Consolas（mono）
- 音訊：從 `edited.mp4` 抽取 64kbps mono MP3，base64 嵌入 HTML
- 驅動：`audio.currentTime` 驅動場景切換和 data-at reveals（非 rAF timestamp）
- 開場：點擊 overlay 才播放（瀏覽器政策）

### Step 4 — 截圖抓幀
執行：`node tools/fb-promo/capture_frames.mjs <html_path> <frames_dir> <duration_sec>`

- 工具：Puppeteer headless
- 解析度：1080×1920，24fps
- 幀數：~1008 幀（42 秒）
- 技巧：override `audio.currentTime` getter + 手動推進時間，不依賴真實音訊播放
- 每幀等兩次 rAF 確保 DOM 更新

### Step 5 — FFmpeg 合成
```bash
ffmpeg -y \
  -framerate 24 -i "frames_dir/frame_%05d.png" \
  -i "video-projects/sXepY-short/03-edited/edited.mp4" \
  -map 0:v -map 1:a \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -shortest \
  "video-projects/sXepY-short/06-publish/sXepY_reels_vertical.mp4"
```

輸出：`06-publish/sXepY_reels_vertical.mp4`，約 2-3MB，1080×1920

## 一鍵執行（跨平台）

**Mac/Linux:**
```bash
cd <repo_root>
cd tools/fb-promo && npm install   # 首次需要
bash tools/fb-promo/run.sh video-projects/s2ep7-short
```

**Windows (PowerShell):**
```powershell
cd tools\fb-promo; npm install     # 首次需要
tools\fb-promo\run.bat video-projects\s2ep7-short
```

## 工具路徑（Git Repo）
`tools/fb-promo/` — 跨平台版本，無硬編碼路徑，接受命令列參數
- `build_html.py` — Python，接受 `<episode_dir> <output_html>`
- `capture_frames.mjs` — Node.js Puppeteer，接受 `<html_path> <frames_dir> <duration>`
- `run.sh` — Mac/Linux 一鍵執行
- `run.bat` — Windows 一鍵執行
- `package.json` — puppeteer 依賴

**Why:** 老查希望 Podcast 每集都有視覺動畫預告影片，用於 Facebook Reels 宣傳。
**How to apply:** 說「做FB預告」時，問集數，然後跑上面五步流程。
