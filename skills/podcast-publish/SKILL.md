---
name: podcast-publish
description: 《不標準答案》單集上架統一入口（老查取名「星期天」）——自動判斷這一集做到哪一步（逐字稿/文案/IG圖/影片/YouTube/Firstory/Shorts/FB預告），接續執行到底或回報缺什麼輸入。觸發詞「上架」「新集數」「這集上架」「星期天」。
---

# 星期天 — Podcast 上架統一入口

老查一句「星期天」「上架 {slug}」或「新集數 {slug}」，這個 skill 判斷這一集目前做到哪一步、接下去該做什麼，依序執行到底，缺輸入就停下來問，不用老查自己依序喊四條 pipeline。

（內部技術識別名維持 `podcast-publish`——skill 系統規定 name 只能用小寫英文+數字+橫線，中文名只能放在暱稱/觸發詞，不影響喊「星期天」直接叫出這個流程。）

**這不是重寫底下四條 pipeline，是在它們上面加一層排序 + 狀態判斷 + 呼叫。** 每個步驟該用什麼工具、去哪個記憶檔找細節，都在下面列出。

---

## 狀態檔：`.publish-status.json`

每次執行第一步先讀 `output/ep-{slug}/.publish-status.json`；不存在就視為全部 false 並建立：

```json
{
  "transcript": false,
  "content_files": false,
  "ig_images": false,
  "video_rendered": false,
  "youtube": { "uploaded": false, "videoId": null },
  "firstory": { "uploaded": false },
  "shorts": { "applicable": false, "done": false },
  "fb_promo": { "applicable": false, "done": false }
}
```

每完成一步就更新寫回。**YouTube / Firstory 是否上傳過，一律看這個檔案的旗標，不要用「影片檔存在」去猜測**——影片存在不代表已經上傳過。

---

## 執行步驟

### 0. 輸入
需要 `{slug}`（必填）。視情況可能還需要：Plaud 逐字稿連結、Firstory Studio 連結、音檔路徑（Downloads）、封面圖路徑（Google Drive）。老查沒主動給，就在對應步驟卡住時再問，不要一開始就把所有問題一次問完。

### 1. 逐字稿 — `transcript: false` 時
老查有給 Plaud 連結（`https://web.plaud.ai/s/pub_xxxx...`）→ 用 `firecrawl_scrape`（`waitFor: 5000`）抓取，存到 `output/ep-{slug}/transcript/`。
沒給連結 → 停在這一步，回報「需要 Plaud 逐字稿連結才能繼續」。
完成後 `transcript: true`。

### 2. 五個文案檔 — `content_files: false` 時
產出 `fb-post.txt`（800字FB長文）/ `ig-caption.txt`（150字+hashtag）/ `youtube.txt`（標題+說明+章節）/ `show-notes.md`（Firstory Show Notes）。細節格式見記憶 `project_podcast_production`。

寫作時套用記憶 `feedback_interaction_style` 的語氣禁用詞、排版規則。

**產 show-notes 前先自問一次**（不一定要外顯在文案裡，但要確認有想過）：這集體現記憶 `project_podcast_strategy` 三大哲學（金繼/物心分離/慢速野獸）的哪一個？確保底層哲學跟表面內容有連上。

**金句步驟鐵律（不可跳過、不可自動化）**：一律先列 10 句候選金句，讓老查選 5 句，選完才寫進最終文案。這條規則見記憶 `feedback_quote_selection`，統一入口做出來後這一步依然要人工核准。

完成後 `content_files: true`。

### 3. IG 圖 — `content_files: true` 且 `ig_images: false` 時
自動執行：
```powershell
powershell -ExecutionPolicy Bypass -File tools\ig-images\run_ig.ps1 -EpSlug {slug}
```
自動偵測封面圖（規則見記憶 `project_ig_pipeline`）；偵測失敗才問老查要哪張封面，加 `-CoverImage` 參數重跑。
完成後 `ig_images: true`。

### 4. 集數影片 — `video_rendered: false` 時
問老查「音檔路徑（Downloads 裡的 mp3）+ 封面圖路徑（Google Drive）」。拿到後直接執行 FFmpeg（不產生 `make-video.ps1` 中間檔，直接跑）：
```powershell
$audio  = "<老查給的音檔路徑>"
$cover  = "<老查給的封面圖路徑>"
$output = "D:\hot data\CCoode\output\ep-{slug}\{slug}-youtube.mp4"
ffmpeg -y -loop 1 -i $cover -i $audio -c:v libx264 -tune stillimage -crf 18 -c:a aac -b:a 192k -pix_fmt yuv420p -shortest $output
```
完成後 `video_rendered: true`。

### 5. YouTube 上傳 — `video_rendered: true` 且 `youtube.uploaded: false` 時
```powershell
node tools/youtube-upload.js --episode ep-{slug}
```
上傳後把回傳的 videoId 寫入 `.publish-status.json`（`youtube.uploaded: true`, `youtube.videoId: "<id>"`），回報 YouTube Studio 連結（`https://studio.youtube.com/video/{videoId}/edit`）。預設私人，老查自行確認後改公開。

### 6. Firstory 上傳 — 有音檔路徑且 `firstory.uploaded: false` 時
```
node tools/firstory-upload/upload.mjs --episode {slug} --audio "<音檔路徑>"
```
這是半自動：開瀏覽器、自動填標題+說明+上傳音檔，停在發布頁讓老查手動確認發布。老查確認發布後才把 `firstory.uploaded` 設為 `true`（不要在腳本跑完就設定，因為它本來就不會自動按發布）。

### 7. Shorts + FB 預告（條件式）
檢查 `video-projects/{slug}-short/01-raw/raw.mp4` 是否存在：
- **不存在** → `shorts.applicable: false`，跳過。這是正常狀態，不是卡住——不是每集都會另外錄短影音素材。
- **存在** → 依 `shorts-pipeline` skill（`~/.claude/skills/shorts-pipeline/SKILL.md`）的 6 個步驟執行完，`shorts.done: true`。接著跑 FB 預告（細節見記憶 `project_fb_promo_pipeline`）：
  ```powershell
  cd tools\fb-promo; npm install   # 首次需要
  tools\fb-promo\run.bat video-projects\{slug}-short
  ```
  完成後 `fb_promo.done: true`。

### 8. 結尾報告
每次執行完，列出這集 8 個項目的狀態表：

| 項目 | 狀態 |
|------|------|
| 逐字稿 | ✅/❌/⏸️缺輸入 |
| 文案4檔 | ... |
| IG圖 | ... |
| 集數影片 | ... |
| YouTube | ... |
| Firstory | ... |
| Shorts | ✅/❌/➖不適用 |
| FB預告 | ... |

清楚標示完成、缺什麼輸入、還是不適用，讓老查一眼看出下一步要給什麼。

### 9. SEO 文章（選配，不算在上面 8 項狀態表內）
若老查想把這集也轉成SEO文章補網站流量，可另外呼叫 `seo-article-writer` skill（老查取名「居易」，模式A，帶入同一個 `{slug}`）。這不是必經步驟，星期天流程本身不會主動觸發它。

---

## 涉及但不修改的既有工具
原樣呼叫，不動內部邏輯：
- `tools/ig-images/run_ig.ps1`
- `tools/youtube-upload.js`
- `tools/firstory-upload/upload.mjs`
- `tools/fb-promo/run.bat` / `run.sh`
- `shorts-pipeline` skill（步驟 7 直接引用其步驟，不要複製貼上整份內容）
- `seo-article-writer` skill（居易，選配步驟 9 引用，不要複製貼上整份內容）

## 相關記憶
`project_podcast_production`、`project_ig_pipeline`、`project_shorts_pipeline`、`project_fb_promo_pipeline`、`feedback_interaction_style`、`feedback_quote_selection`、`project_podcast_strategy`、`project_marketing_team_upgrade`
