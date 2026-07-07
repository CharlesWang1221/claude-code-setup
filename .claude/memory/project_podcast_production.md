---
name: project-podcast-production
description: 《不標準答案》每集上架完整流程——逐字稿→文案→影片→YouTube 自動上傳，所有工具路徑與指令
metadata: 
  node_type: memory
  type: project
  originSessionId: 81a61a77-0e09-4f11-b6a5-eb1a376cf783
---

## 觸發詞
老查說「上架」「宣傳」「文案」「影片」→ 叫出此記憶繼續執行。

---

## 每集完整 SOP

### 1. 逐字稿來源
- 老查本機用 **Plaud** 錄音並產生逐字稿
- 分享格式：`https://web.plaud.ai/s/pub_xxxx...` 公開連結
- 我用 firecrawl_scrape 抓取（需 waitFor: 5000）

### 2. 素材輸出位置
每集建一個資料夾：`D:\hot data\CCoode\output\ep-{slug}\`

每集產出 5 個檔案：
| 檔案 | 內容 |
|------|------|
| `fb-post.txt` | FB 長文（800字，含故事線、金句、Firstory 連結） |
| `ig-caption.txt` | IG 短文（150字）+ hashtag 組 |
| `youtube.txt` | YouTube 標題 + 說明欄 + 章節時間軸 |
| `show-notes.md` | Firstory Show Notes（案例、金句、重點） |
| `make-video.ps1` | FFmpeg 指令（填入音檔+封面圖路徑後執行） |

### 3. 影片製作（FFmpeg）
FFmpeg 已安裝（winget install Gyan.FFmpeg）

PowerShell 直接執行（不用腳本，避免編碼問題）：
```powershell
$audio  = "C:\Users\siming_wang\Downloads\s2epX_縮混.mp3"
$cover  = "G:\我的雲端硬碟\不標準答案\2026\網誌\節目\S2EPx\S2epX_V2.png"
$output = "D:\hot data\CCoode\output\ep-xxx\s2epX-youtube.mp4"
ffmpeg -y -loop 1 -i $cover -i $audio -c:v libx264 -tune stillimage -crf 18 -c:a aac -b:a 192k -pix_fmt yuv420p -shortest $output
```

封面圖位置規律：
`G:\我的雲端硬碟\不標準答案\2026\網誌\節目\S2EPx\S2epX_V2.png`

### 4. YouTube 自動上傳工具
腳本位置：`D:\hot data\CCoode\tools\youtube-upload.js`
套件：`googleapis`（已安裝在 `D:\hot data\CCoode\node_modules`）

**每集上傳指令：**
```powershell
cd "D:\hot data\CCoode"
node tools/youtube-upload.js --episode ep-{slug}
```

- Token 已快取：`D:\hot data\CCoode\tools\youtube-token.json`（不需要再授權）
- 上傳帳號：`another20251021@gmail.com`
- 上傳後預設為**私人（Private）**，手動改公開
- YouTube Studio 連結：`https://studio.youtube.com/video/{videoId}/edit`

**Google Cloud 憑證：**
- 專案名稱：`podcast-tools`
- 專案 ID：`podcast-tools-501708`
- client_secret.json：`D:\hot data\CCoode\tools\client_secret.json`
- OAuth Client ID：`217493993888-io4msi4ro04gsvvba7uvfp0ghl8flplf.apps.googleusercontent.com`

### 5. Firstory 集數連結格式
`https://open.firstory.me/story/{episodeId}`

episodeId 從 Firstory Studio 網址取得：
`https://studio.firstory.me/episodes/{episodeId}/analytics`

---

## 完整執行順序（新集數）

1. 老查給 Plaud 逐字稿連結 + Firstory Studio 連結
2. 我抓逐字稿、產出 5 個素材檔
3. 老查給音檔路徑（Downloads 裡的 mp3）+ 封面圖路徑（Google Drive）
4. 我用 PowerShell 跑 FFmpeg 合成影片
5. 我用 `node tools/youtube-upload.js --episode ep-xxx` 上傳 YouTube
6. 老查去 YouTube Studio 確認後改公開

---

## 已完成集數紀錄
| 集數 | 主題 | 輸出資料夾 | YouTube ID |
|------|------|-----------|------------|
| S2EP7 | 校園偷拍事件與社會信任退化 | ep-s2ep7 | xlLz8Baai_I（2026-07-07 重新上傳，原 tZLKQ4WiO04 因認證問題被刪） |

**Why:** 老查每週出集需要快速產出全套宣傳素材，這套流程讓一個人可以在 15 分鐘內完成文案 + 影片 + 上傳。  
**How to apply:** 每次老查提到上架、文案、宣傳圖，先叫出此記憶，按 SOP 執行。
