---
name: shorts-pipeline
description: 全自動短影音製作 pipeline：從原始錄影到 YouTube Shorts 上傳。當用戶說「剪短影片」「做 Shorts」「自動剪」「幫我剪一支」「用 XX 集做短影音」時必須使用此 skill。輸入一段原始影片，自動完成：Whisper 字幕、Auto-Editor 去靜音、Pexels B-roll 語意比對、FFmpeg 三區版型合成、YouTube 上傳。
---

# 短影音自動製作 Pipeline

## 概覽

```
01-raw/         原始影片
02-transcript/  Whisper 字幕（SRT）
03-edited/      Auto-Editor 去靜音版本
04-broll/       Pexels B-roll 素材
05-render/      最終合成成品
06-publish/     title.txt / cta.txt
```

**工具目錄**：`D:/hot data/CCoode/tools/video-auto-edit/`
**Python 路徑（Windows）**：`C:/Users/siming_wang/AppData/Local/Programs/Python/Python312/python.exe`
**API Key**：從 `D:/hot data/CCoode/.env` 自動讀取（`PEXELS_API_KEY`）

---

## 執行前確認

1. 原始影片已放入 `video-projects/{名稱}/01-raw/raw.mp4`
2. `06-publish/title.txt` 和 `cta.txt` 已填好標題與 CTA 文字
3. `D:/hot data/CCoode/.env` 中有 `PEXELS_API_KEY`

---

## 步驟 1：Whisper 轉字幕

```powershell
whisper "D:/hot data/CCoode/video-projects/{名稱}/01-raw/raw.mp4" `
  --model medium `
  --language zh `
  --output_format srt `
  --output_dir "D:/hot data/CCoode/video-projects/{名稱}/02-transcript/"
```

輸出：`02-transcript/raw.srt`

---

## 步驟 2：Auto-Editor 去靜音

```powershell
auto-editor "D:/hot data/CCoode/video-projects/{名稱}/01-raw/raw.mp4" `
  --output "D:/hot data/CCoode/video-projects/{名稱}/03-edited/edited.mp4" `
  --margin 0.2sec
```

---

## 步驟 3：抓 Pexels B-roll

**關鍵：用英文語意關鍵字，不要用中文原文**

先看 SRT 字幕找出 3 個關鍵片段，替每個片段想對應的英文關鍵字（描述畫面，不是直譯）：

```powershell
Set-Location "D:/hot data/CCoode"
C:/Users/siming_wang/AppData/Local/Programs/Python/Python312/python.exe `
  tools/video-auto-edit/scripts/fetch_broll.py `
  --srt "video-projects/{名稱}/02-transcript/raw.srt" `
  --output-dir "video-projects/{名稱}/04-broll/" `
  --count 3 `
  --keywords "英文關鍵字1,英文關鍵字2,英文關鍵字3"
```

關鍵字選法範例：
- 字幕說「為什麼同事會偷拍你」→ `security camera office`
- 字幕說「感到焦慮防備」→ `anxiety stressed woman`
- 字幕說「家人擔心害怕」→ `family worried`

輸出：`04-broll/broll_list.json`（包含時間戳 + 檔名）

---

## 步驟 4：建 FFmpeg Filter 腳本

### 4a. 把素材複製到無空格路徑

```powershell
$tmp = "C:/tmp/{名稱}"
New-Item -ItemType Directory -Force $tmp
Copy-Item "D:/hot data/CCoode/video-projects/{名稱}/03-edited/edited.mp4" "$tmp/edited.mp4"
Copy-Item "D:/hot data/CCoode/video-projects/{名稱}/02-transcript/raw.srt" "$tmp/raw.srt"
Copy-Item "D:/hot data/CCoode/video-projects/{名稱}/06-publish/title.txt" "$tmp/title.txt"
Copy-Item "D:/hot data/CCoode/video-projects/{名稱}/06-publish/cta.txt" "$tmp/cta.txt"

# B-roll 複製並重新編號
$brolls = Get-Content "D:/hot data/CCoode/video-projects/{名稱}/04-broll/broll_list.json" | ConvertFrom-Json
for ($i=0; $i -lt $brolls.Count; $i++) {
  Copy-Item "D:/hot data/CCoode/video-projects/{名稱}/04-broll/$($brolls[$i].file)" "$tmp/broll_0$($i+1).mp4"
}
```

### 4b. 建立 build_broll_filter.js

在 `$tmp/build_broll_filter.js` 建立以下腳本（替換 `{名稱}` 和 `{tmp}`）：

```javascript
const fs = require('fs');

const BROLL_LIST = "D:/hot data/CCoode/video-projects/{名稱}/04-broll/broll_list.json";
const SRT_FILE   = "C:/tmp/{名稱}/raw.srt";
const TITLE_FILE = "C:/tmp/{名稱}/title.txt";
const CTA_FILE   = "C:/tmp/{名稱}/cta.txt";
const FONT       = "C\\:/Windows/Fonts/NotoSansTC-VF.ttf";
const BROLL_DUR  = 4;

const brolls = JSON.parse(fs.readFileSync(BROLL_LIST, 'utf8'));
const srt    = fs.readFileSync(SRT_FILE, 'utf8').replace(/\r\n/g, '\n').replace(/\r/g, '\n');

function parseSRT(text) {
  return text.trim().split(/\n{2,}/).map(b => {
    const lines = b.trim().split('\n');
    if (lines.length < 3) return null;
    const [start, end] = lines[1].split(' --> ');
    return { start: toSec(start), end: toSec(end), text: lines.slice(2).join(' ') };
  }).filter(Boolean);
}
function toSec(t) {
  const [hms, ms] = t.replace(',','.').split('.');
  const [h,m,s] = hms.split(':').map(Number);
  return h*3600 + m*60 + s + parseFloat('0.'+ms);
}
function escText(s) {
  return s.replace(/\\/g,'\\\\').replace(/:/g,'\\:').replace(/\n/g,' ');
}

const subtitles = parseSRT(srt);
const lines = [];

lines.push(`[0:v]scale=1080:810[main_vid]`);

let prev = 'main_vid';
brolls.forEach((b, i) => {
  const idx   = i + 1;
  const start = b.insert_at_seconds.toFixed(3);
  const end   = (b.insert_at_seconds + BROLL_DUR).toFixed(3);
  const cur   = i < brolls.length - 1 ? `vid_b${i}` : 'vid_with_broll';
  lines.push(`[${idx}:v]scale=1080:810:force_original_aspect_ratio=increase,crop=1080:810[bscaled${i}]`);
  lines.push(`[${prev}][bscaled${i}]overlay=0:0:enable='between(t,${start},${end})'[${cur}]`);
  prev = cur;
});

const vidSrc = brolls.length > 0 ? 'vid_with_broll' : 'main_vid';
lines.push(`color=black:size=1080x1920:d=999[bg]`);
lines.push(`[bg][${vidSrc}]overlay=0:230[base]`);
lines.push(`[base]drawbox=x=0:y=0:w=1080:h=230:color=0x111111:t=fill[topbar]`);
lines.push(`[topbar]drawbox=x=0:y=1040:w=1080:h=880:color=0x0a0a0a:t=fill[btmbar]`);
lines.push(`[btmbar]drawtext=fontfile='${FONT}':textfile='C\\:/tmp/{名稱}/title.txt':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=75[t]`);
lines.push(`[t]drawtext=fontfile='${FONT}':textfile='C\\:/tmp/{名稱}/cta.txt':fontcolor=0xaaaaaa:fontsize=28:x=(w-text_w)/2:y=1660[comp]`);

let subPrev = 'comp';
subtitles.forEach((s, i) => {
  const labelOut = i === subtitles.length - 1 ? '[with_subs]' : `[sub${i}]`;
  const labelIn  = i === 0 ? '[comp]' : `[sub${i-1}]`;
  lines.push(
    `${labelIn}drawtext=fontfile='${FONT}':text='${escText(s.text)}':fontcolor=white:fontsize=36:` +
    `x=(w-text_w)/2:y=h-120:box=1:boxcolor=black@0.55:boxborderw=10:` +
    `enable='between(t,${s.start.toFixed(3)},${s.end.toFixed(3)})'${labelOut}`
  );
});

const filterStr = lines.join(';\n');
fs.writeFileSync('C:/tmp/{名稱}/filter_broll.txt', filterStr, 'utf8');

const inputs = [
  `-i C:/tmp/{名稱}/edited.mp4`,
  ...brolls.map((b, i) => `-i C:/tmp/{名稱}/broll_0${i+1}.mp4`),
].join(' ');

const cmd = `ffmpeg -y ${inputs} -filter_complex_script C:/tmp/{名稱}/filter_broll.txt ` +
  `-map "[with_subs]" -map "0:a" ` +
  `-c:v libx264 -crf 22 -preset fast -c:a aac -b:a 192k -pix_fmt yuv420p ` +
  `C:/tmp/{名稱}/final_broll.mp4`;

fs.writeFileSync('C:/tmp/{名稱}/ffmpeg_broll_cmd.txt', cmd, 'utf8');
console.log(`filter: ${lines.length} lines, brolls: ${brolls.length}, subtitles: ${subtitles.length}`);
```

---

## 步驟 5：執行 FFmpeg 渲染

```powershell
node C:/tmp/{名稱}/build_broll_filter.js
# 確認輸出後執行渲染指令：
$cmd = Get-Content C:/tmp/{名稱}/ffmpeg_broll_cmd.txt
Invoke-Expression $cmd
```

渲染完成後複製回專案：

```powershell
Copy-Item "C:/tmp/{名稱}/final_broll.mp4" `
  "D:/hot data/CCoode/video-projects/{名稱}/05-render/final.mp4" -Force
```

---

## 步驟 6：YouTube 上傳（私人）

建立上傳腳本 `C:/tmp/{名稱}/upload_short.js`：

```javascript
const { google } = require('D:/hot data/CCoode/node_modules/googleapis');
const fs = require('fs');

const TOKEN_PATH = 'D:/hot data/CCoode/tools/youtube-token.json';
const CREDS_PATH = 'D:/hot data/CCoode/tools/client_secret.json';
const VIDEO_PATH = 'D:/hot data/CCoode/video-projects/{名稱}/05-render/final.mp4';
const TITLE      = fs.readFileSync('D:/hot data/CCoode/video-projects/{名稱}/06-publish/title.txt', 'utf8').trim() + ' #Shorts';
const DESCRIPTION = `${TITLE}\n\n追蹤《不標準答案》Podcast 獲取更多內容\n\n#不標準答案 #Podcast #Shorts`;
const TAGS = ['不標準答案', 'Podcast', 'Shorts'];

(async () => {
  const creds = JSON.parse(fs.readFileSync(CREDS_PATH));
  const { client_secret, client_id, redirect_uris } = creds.installed || creds.web;
  const oauth2 = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
  oauth2.setCredentials(JSON.parse(fs.readFileSync(TOKEN_PATH)));
  const youtube  = google.youtube({ version: 'v3', auth: oauth2 });
  const fileSize = fs.statSync(VIDEO_PATH).size;
  console.log(`上傳：${(fileSize/1024/1024).toFixed(1)} MB\n標題：${TITLE}\n`);
  const res = await youtube.videos.insert(
    {
      part: ['snippet', 'status'],
      requestBody: {
        snippet: { title: TITLE, description: DESCRIPTION, tags: TAGS, categoryId: '22', defaultLanguage: 'zh-TW' },
        status: { privacyStatus: 'private' },
      },
      media: { body: fs.createReadStream(VIDEO_PATH) },
    },
    { onUploadProgress: evt => process.stdout.write(`\r進度：${((evt.bytesRead/fileSize)*100).toFixed(1)}%`) }
  );
  console.log(`\n上傳完成！`);
  console.log(`影片 ID：${res.data.id}`);
  console.log(`YouTube Studio：https://studio.youtube.com/video/${res.data.id}/edit`);
})().catch(err => { console.error('錯誤：', err.message); process.exit(1); });
```

```powershell
node C:/tmp/{名稱}/upload_short.js
```

---

## 常見問題排查

| 問題 | 原因 | 解法 |
|------|------|------|
| FFmpeg filter 路徑錯誤 | 路徑含空格 | 複製到 `C:/tmp/` |
| 字幕不顯示 | fontconfig 找不到字型 | 用 `fontfile='C\\:/Windows/Fonts/NotoSansTC-VF.ttf'` |
| B-roll 全一樣 | scale2ref 的 bug | 改用 `scale=1080:810:force_original_aspect_ratio=increase,crop=1080:810` |
| Pexels 找不到結果 | 中文關鍵字 | 一律用英文語意關鍵字 |
| Python 找不到 | Windows Store stub | 用完整路徑 `C:/Users/siming_wang/AppData/...` |
| CP950 編碼錯誤 | Windows 終端機 | fetch_broll.py 開頭已有 `sys.stdout.reconfigure` |
