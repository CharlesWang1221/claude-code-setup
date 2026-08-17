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
  "content_decision": { "approved": false, "core_claim": null, "brand_anchor": null, "audience": null, "listener_problem": null, "episode_promise": null, "title": null, "thumbnail_text": null },
  "brand_review": { "passed": false, "rejected_reasons": [] },
  "content_files": false,
  "teaser_video": { "quote_selected": false, "rendered": false, "quote": null, "start": null, "end": null },
  "ig_images": false,
  "video_rendered": false,
  "youtube": { "uploaded": false, "videoId": null },
  "firstory": { "uploaded": false },
  "shorts": { "applicable": false, "done": false },
  "fb_promo": { "applicable": false, "done": false }
}
```

既有狀態檔若沒有 `content_decision` 或 `brand_review`，只補上缺少欄位並視為未核准／未通過；不得重設其他已完成旗標。

每完成一步就更新寫回。**YouTube / Firstory 是否上傳過，一律看這個檔案的旗標，不要用「影片檔存在」去猜測**——影片存在不代表已經上傳過。

---

## 執行步驟

### 0. 輸入
需要 `{slug}`（必填）。視情況可能還需要：Plaud 逐字稿連結、Firstory Studio 連結、音檔路徑（Downloads）、封面圖路徑（Google Drive）。老查沒主動給，就在對應步驟卡住時再問，不要一開始就把所有問題一次問完。

### 0.5 品牌基準

任何內容生成前，完整讀取專案根目錄的 `AGENTS.md` 與 `BRAND_CONTEXT.md`。找不到任一檔案就停止內容生成並回報缺少品牌基準，不得憑印象補寫。

以心維空間為母品牌、《不標準答案》為旗下產品。所有標題、縮圖、Show Notes、社群文案、預告字卡與 CTA 都必須服從 `BRAND_CONTEXT.md`；不可把兩者寫成並列品牌。

### 1. 逐字稿 — `transcript: false` 時
老查有給 Plaud 連結（`https://web.plaud.ai/s/pub_xxxx...`）→ 用 `firecrawl_scrape`（`waitFor: 5000`）抓取，存到 `output/ep-{slug}/transcript/`。
沒給連結 → 停在這一步，回報「需要 Plaud 逐字稿連結才能繼續」。
完成後 `transcript: true`。

### 2. 內容決策關 — `content_decision.approved: false` 時

先讀完整逐字稿，只能使用逐字稿與老查明確提供的事實。產出 `content-decision.md`：

- 核心主張 1 句：聽完後應改變的看法或行動。
- 品牌錨點 1 個：指出這集如何連回 Beyond Answers、靈魂金繼、情感物理學或對抗爆買帝國；只選真正吻合者，不硬塞品牌術語。
- 主要受眾 1 種：不要同時討好多群人。
- 聽眾問題 1 個：用受眾會說的口語描述。
- 節目承諾 1 個：這集實際能交付什麼，不誇大。
- 標題 6 案：搜尋型 2 案、觀點型 2 案、衝突型 2 案。
- 每案標示主題清楚度、具體程度、好奇缺口、搜尋辨識度，各 1 至 5 分，並寫 1 句風險。
- 推薦標題 1 案與推薦理由。人名沒有自帶搜尋量時，不放標題最前面。
- 縮圖文字 3 案，每案 6 至 10 個中文字，不照抄標題。
- 品牌風險：逐案檢查是否藏有標準答案、販賣焦慮、強迫正向、鼓動比較，或把裂痕／修復當裝飾口號。

同時列出 10 句逐字稿原話金句，附講者與可靠時間碼。不可把改寫句冒充原話；找不到可靠時間碼就標示待確認。

停下來讓老查核准：最終標題、縮圖文字、5 句金句，以及其中 1 句節目預告主句。未核准不得產生平台文案，也不得把 `content_decision.approved` 設為 `true`。

核准後把結果寫入 `.publish-status.json`，再進入下一步。

### 2.1 四個文案檔 — `content_decision.approved: true` 且 `content_files: false` 時
以核准的核心主張、品牌錨點、標題與金句為唯一母稿，產出 `fb-post.txt`（800 字 FB 長文）／`ig-caption.txt`（150 字＋hashtag）／`youtube.txt`（標題＋說明＋章節）／`show-notes.md`（Firstory Show Notes）。細節格式見記憶 `project_podcast_production`。

寫作時套用記憶 `feedback_interaction_style` 的語氣禁用詞、排版規則，以及以下平台硬規則與發布前品牌關（取自 `social-media-assistant` 技能包，2026-08-06 併入）：

**FB 長文排版硬規則**
- 手機一行約 20-21 個全形字，抓 17-19 字最安全；話題轉換/重要觀點/情緒轉折處分段，同一論點延續不要硬拆
- 長短句交錯，全短句版面右側會空一片，全長句手機會亂斷
- 不用粗體、斜體、標題層級、編號清單——FB 不支援，寫下去只會變成一堆符號
- 開頭三段內要讓人知道在講什麼，不要自我介紹

**IG 短文規則**
- 挑素材裡最有張力、最有記憶點的切角，不是整集摘要
- 第一行就是全部，後面會被折起來

**發布前品牌閘門（四個文案檔與所有對外字卡都要檢查）**

逐項記錄 PASS／REJECTED 與具體問題句：

1. 架構關：心維空間是母品牌，《不標準答案》是旗下產品，沒有混用或錯置。
2. 北極星關：內容鼓勵受眾做自己的不標準選擇，不把單一做法包裝成唯一正解。
3. 焦慮關：不暗示受眾不夠好、不販賣恐懼、不鼓動比較競爭、不強迫正向。
4. 語氣關：有生活細節、明確立場與老查的煙火氣，不是「賦能」「全方位整合」等報告腔。
5. 事實關：沒在逐字稿或老查原話出現的數字、案例、經驗與成效，一個字不能補。
6. 隱私關：不過度揭露孩子、家庭、私密對話與未經同意的當事人資訊。
7. 商業關：不做農場標題、焦慮行銷、未揭露業配、絕對承諾或拉低品牌定位的廉售導向。

任一項命中即設為 `REJECTED`，把具體問題句與原因寫入 `brand-review.md`，完成改寫後重新檢查。全部通過才設定 `brand_review.passed: true` 與 `content_files: true`；不得為了接續上架硬放行。

**下游硬條件**：無論 `content_files`、`ig_images` 或 `video_rendered` 的既有旗標為何，只要 `brand_review.passed` 不是 `true`，就不得執行節目預告、IG 圖生成、YouTube 上傳、Firstory 填寫、Shorts 或 FB 預告。先審查既有對外內容；通過後才能接續。

**目的衝突當場擋下**：如果這集文案同時要衝觸及、要導流訂閱、又要帶貨/招募，先問老查排順序，不要假裝一組文案能通吃三個目的。

**產 show-notes 前先自問一次**（不一定要外顯在文案裡，但要確認有想過）：這集體現記憶 `project_podcast_strategy` 三大哲學（金繼/物心分離/慢速野獸）的哪一個？確保底層哲學跟表面內容有連上。

**金句步驟鐵律（不可跳過、不可自動化）**：沿用內容決策關核准的 5 句原話金句，不得重新生成或自行替換。這條規則見記憶 `feedback_quote_selection`。

**節目預告選段**：選完 5 句後，將每句的原話、講者（若可知）與起訖時間碼列出，讓老查指定其中 1 句作為「節目預告主句」。沒有明確主句或可靠時間碼，就停在這裡，不自己猜要剪哪段。

完成後 `content_files: true`。

### 2.5 節目預告 — `teaser_video.rendered: false` 時

只有在老查從已選 5 句金句中指定 1 句主句後才執行。把主句與時間碼寫入 `teaser_video.quote`、`start`、`end`，再呼叫 `podcast-teaser-video` skill。

它以主句為剪輯錨點，從原始音檔取 12 至 18 秒，製作 9:16、15 秒、3 段重點卡的節目預告。必須先讓老查確認關鍵畫面才渲染；成品驗證完畢後才設 `teaser_video.rendered: true`。不在這個流程自行上傳。

### 3. IG 圖 — `content_files: true` 且 `ig_images: false` 時
先讀專案根目錄 `DESIGN.md`，讓封面、輪播與金句圖服從品牌色、字體與視覺規則；找不到就停止視覺生成並回報。

自動執行：
```powershell
powershell -ExecutionPolicy Bypass -File tools\ig-images\run_ig.ps1 -EpSlug {slug}
```
自動偵測封面圖（規則見記憶 `project_ig_pipeline`）；偵測失敗才問老查要哪張封面，加 `-CoverImage` 參數重跑。

產完後，把整個 `output/ep-{slug}/ig/` 資料夾內容（carousel + quote 圖）連同 `ig-caption.txt` 一起複製到 Google Drive：`G:\我的雲端硬碟\不標準答案\2026\IG\{slug}\`（老查要求2026-07-26，方便他之後直接去這裡貼文，不用回頭找 repo 路徑）。

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
每次執行完，列出這集 11 個項目的狀態表：

| 項目 | 狀態 |
|------|------|
| 逐字稿 | ✅/❌/⏸️缺輸入 |
| 內容決策 | ✅/❌/⏸️待核准 |
| 品牌審查 | ✅/❌ REJECTED/⏸️待修正 |
| 文案4檔 | ... |
| 節目預告 | ✅/❌/⏸️待選金句 |
| IG圖 | ... |
| 集數影片 | ... |
| YouTube | ... |
| Firstory | ... |
| Shorts | ✅/❌/➖不適用 |
| FB預告 | ... |

清楚標示完成、缺什麼輸入、還是不適用，讓老查一眼看出下一步要給什麼。

### 9. SEO 文章（選配，不算在上面 11 項狀態表內）
若老查想把這集也轉成SEO文章補網站流量，可另外呼叫 `seo-article-writer` skill（老查取名「居易」，模式A，帶入同一個 `{slug}`）。這不是必經步驟，星期天流程本身不會主動觸發它。

---

## 涉及但不修改的既有工具
原樣呼叫，不動內部邏輯：
- `tools/ig-images/run_ig.ps1`
- `tools/youtube-upload.js`
- `tools/firstory-upload/upload.mjs`
- `tools/fb-promo/run.bat` / `run.sh`
- `shorts-pipeline` skill（步驟 7 直接引用其步驟，不要複製貼上整份內容）
- `podcast-teaser-video` skill（步驟 2.5 只在老查選定預告主句後呼叫）
- `seo-article-writer` skill（居易，選配步驟 9 引用，不要複製貼上整份內容）

## 相關記憶
`project_podcast_production`、`project_ig_pipeline`、`project_shorts_pipeline`、`project_fb_promo_pipeline`、`feedback_interaction_style`、`feedback_quote_selection`、`project_podcast_strategy`、`project_marketing_team_upgrade`
