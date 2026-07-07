# Podcast 工具說明

## youtube-upload.js — YouTube 自動上傳

### 換電腦後的設定步驟

1. **安裝依賴套件**
   ```bash
   npm install
   ```

2. **放入 OAuth 憑證**  
   從 Google Cloud Console 下載 `client_secret.json`，放到這個資料夾：
   ```
   tools/client_secret.json
   ```
   - 專案名稱：`podcast-tools`
   - 專案 ID：`podcast-tools-501708`
   - 下載位置：https://console.cloud.google.com/apis/credentials?project=podcast-tools-501708
   - 點既有的 OAuth 用戶端 ID → 下載 JSON → 改名為 `client_secret.json`

3. **第一次執行會要求授權**（之後 token 快取，不用再授權）
   ```bash
   node tools/youtube-upload.js --episode ep-s2ep7
   ```

---

### 每集上傳指令

```bash
node tools/youtube-upload.js --episode ep-{集數資料夾名稱}
```

例：
```bash
node tools/youtube-upload.js --episode ep-s2ep7
```

- 自動讀取 `output/ep-xxx/youtube.txt` 裡的標題與說明欄
- 自動找 `output/ep-xxx/*.mp4` 作為影片檔
- 上傳帳號：`another20251021@gmail.com`
- 上傳後預設為**私人（Private）**，請到 YouTube Studio 確認後改公開

---

### 影片製作（FFmpeg）

**Mac：**
```bash
# 安裝 FFmpeg
brew install ffmpeg

# 合成影片
ffmpeg -y -loop 1 -i /path/to/cover.png -i /path/to/audio.mp3 \
  -c:v libx264 -tune stillimage -crf 18 \
  -c:a aac -b:a 192k -pix_fmt yuv420p -shortest \
  output/ep-xxx/youtube.mp4
```

**Windows（PowerShell）：**
```powershell
# 安裝 FFmpeg
winget install Gyan.FFmpeg

$audio  = "C:\Users\...\audio.mp3"
$cover  = "G:\...\cover.png"
$output = "D:\hot data\CCoode\output\ep-xxx\youtube.mp4"
ffmpeg -y -loop 1 -i $cover -i $audio -c:v libx264 -tune stillimage -crf 18 -c:a aac -b:a 192k -pix_fmt yuv420p -shortest $output
```
