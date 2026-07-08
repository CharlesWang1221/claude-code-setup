# 短影音自動剪輯 Pipeline

當用戶說「剪這支」、「自動剪」或提供影片路徑時，依照以下流程執行。

---

## 前置需求

```powershell
# Windows 安裝
winget install Gyan.FFmpeg
pip install openai-whisper auto-editor requests
```

環境變數需設定：
- `PEXELS_API_KEY` — 到 https://www.pexels.com/api/ 申請

---

## 專案資料夾結構

每支影片建立獨立資料夾：

```
video-projects/
  {影片名稱}/
    01-raw/          ← 放原始錄影檔在這
    02-transcript/   ← Whisper 輸出 SRT
    03-edited/       ← Auto-Editor 輸出
    04-broll/        ← Pexels 下載的 B-roll
    05-render/       ← 最終合成成品
    06-publish/      ← 封面圖、文案等
```

建立指令：
```powershell
$name = "影片名稱"
mkdir "video-projects/$name/01-raw","video-projects/$name/02-transcript","video-projects/$name/03-edited","video-projects/$name/04-broll","video-projects/$name/05-render","video-projects/$name/06-publish"
```

---

## 步驟 1：Whisper 轉字幕

```powershell
whisper "video-projects/{名稱}/01-raw/input.mp4" `
  --model medium `
  --language zh `
  --output_format srt `
  --output_dir "video-projects/{名稱}/02-transcript/"
```

輸出：`02-transcript/input.srt`

---

## 步驟 2：Auto-Editor 剪靜音 + 推鏡頭

```powershell
auto-editor "video-projects/{名稱}/01-raw/input.mp4" `
  --output "video-projects/{名稱}/03-edited/edited.mp4" `
  --margin 0.2sec `
  --zoom-in-factor 0.05
```

參數說明：
- `--margin 0.2sec` — 靜音前後各保留 0.2 秒
- `--zoom-in-factor 0.05` — 每次剪切有輕微推鏡效果

---

## 步驟 3：Pexels 自動抓 B-roll

執行 Python 腳本，傳入 SRT 路徑：

```powershell
python scripts/fetch_broll.py `
  --srt "video-projects/{名稱}/02-transcript/input.srt" `
  --output-dir "video-projects/{名稱}/04-broll/" `
  --api-key $env:PEXELS_API_KEY `
  --count 5
```

腳本會：
1. 解析 SRT 擷取關鍵字
2. 呼叫 Pexels Videos API
3. 下載最佳匹配的 B-roll 短片（720p MP4）
4. 輸出 `04-broll/broll_list.json`（時間戳 + 檔案對應）

---

## 步驟 4：字幕微調（可選）

用瀏覽器開啟 `subtitle-editor.html`，載入 `02-transcript/input.srt`：
- 修改字幕文字
- 標記「大字」（重要句子會放大顯示）
- 匯出修改後的 SRT

---

## 步驟 5：燒字幕 + 三區式版型合成

```powershell
python scripts/compose.py `
  --video "video-projects/{名稱}/03-edited/edited.mp4" `
  --srt "video-projects/{名稱}/02-transcript/input.srt" `
  --broll-list "video-projects/{名稱}/04-broll/broll_list.json" `
  --title "這裡放標題文字" `
  --cta "追蹤更多 → @帳號名稱" `
  --output "video-projects/{名稱}/05-render/final.mp4" `
  --layout three-zone
```

版型選項：
- `three-zone` — 上標題 + 中影片 + 下 CTA（1080×1920 垂直）
- `selfie` — 全螢幕自拍風，封面遮罩壓字

---

## 步驟 6：確認成品

成品在 `05-render/final.mp4`，確認後用 YouTube 上傳工具或手動上傳 IG/YouTube Shorts。

**只保留 SRT 檔案在本機，影片上傳到社群平台當雲端備份。**

---

## 常見 FFmpeg 指令備查

### Windows 字幕燒錄方案（用 drawtext，繞過 libass）
`subtitles=` filter 在 Windows 需要 fontconfig，容易報錯。改用 drawtext + enable 時間條件：

```bash
# 步驟1：SRT → drawtext filter chain
node scripts/srt_to_drawtext.js input.srt "C:/Windows/Fonts/NotoSansTC-VF.ttf" sub_filters.txt

# 步驟2：把 sub_filters.txt 接在 layout filter 後面，用 -filter_complex_script 跑
ffmpeg -y -i video.mp4 -filter_complex_script filter_full.txt \
  -map "[with_subs]" -map "0:a" -c:v libx264 -crf 22 output.mp4
```

字幕會出現在影片底部（`y=h-120`），黑色半透明底框。

### Windows 路徑有空格的解法
FFmpeg filter_complex 不支援含空格的路徑。把素材先複製到無空格的 temp：
```powershell
$tmp = "C:\tmp\myproject"
mkdir $tmp
Copy-Item "D:\hot data\...\edited.mp4" "$tmp\input.mp4"
Copy-Item "D:\hot data\...\raw.srt" "$tmp\raw.srt"
# 在 $tmp 跑 FFmpeg，完成後複製回來
```

字型必須用 `fontfile=` 直接指定（Windows 沒有 fontconfig）：
```
fontfile='C\:/Windows/Fonts/NotoSansTC-VF.ttf'
```

### 燒入 SRT 字幕
```bash
ffmpeg -i input.mp4 -vf "subtitles=input.srt:force_style='FontName=Noto Sans TC,FontSize=22,PrimaryColour=&Hffffff,OutlineColour=&H000000,Outline=2'" output.mp4
```

### 三區版型（純 FFmpeg，不用 Python）
```bash
ffmpeg -i edited.mp4 \
  -filter_complex "
    color=black:size=1080x1920:d=999[bg];
    [0:v]scale=1080:607:force_original_aspect_ratio=decrease,pad=1080:607:(ow-iw)/2:(oh-ih)/2[vid];
    [bg][vid]overlay=0:330[comp];
    [comp]drawtext=text='標題文字':fontcolor=white:fontsize=52:x=(w-text_w)/2:y=120:font='Noto Sans TC':box=1:boxcolor=black@0.0[with_title];
    [with_title]drawtext=text='CTA 文字':fontcolor=white@0.8:fontsize=32:x=(w-text_w)/2:y=1600:font='Noto Sans TC'[final]
  " \
  -map "[final]" -map 0:a output_three_zone.mp4
```
