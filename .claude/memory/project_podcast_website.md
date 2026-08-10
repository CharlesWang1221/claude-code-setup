---
name: project-podcast-website
description: 《不標準答案》Podcast 網站專案——技術架構、部署指令、設計狀態、待辦清單
metadata: 
  node_type: memory
  type: project
  originSessionId: 272bf243-fe65-4c8e-add5-f9840da310d3
  modified: 2026-08-10T11:13:56.626Z
---

## 觸發詞
老查說「做網頁」→ 叫出此記憶繼續執行。

## 專案位置
`D:\hot data\CCoode\site\`（子目錄，Git repo 根目錄在 `D:\hot data\CCoode\`）  
Git remote: `https://github.com/CharlesWang1221/claude-code-setup.git`（注意：repo 名稱是 `claude-code-setup`，不是 `CCoode`）

## 線上網址
- 正式：https://beyond-ans.com（Cloudflare Registrar + Pages 自訂域名，2026-07-03 啟用）
- 備用：https://podcast-site-9hr.pages.dev（Cloudflare Pages 原始網址）

## 技術棧
- Astro 4.16（靜態輸出 `output: 'static'`）
- `fast-xml-parser` — build time 從 Firstory RSS 拉取集數資料
- `@astrojs/sitemap` — 自動生成 sitemap-index.xml
- Wrangler 4 — Cloudflare Pages 部署

## RSS 來源
`https://feed.firstory.me/rss/user/cmi76pcj000h7010chgezh8bs`

## 部署指令
```bash
cd "D:/hot data/CCoode/site"
npm run build
npx wrangler pages deploy dist --project-name podcast-site --commit-dirty=true --branch main
```

## 頁面結構
```
/                    → 首頁（Hero + 3欄集數卡片 + 主持人卡片 + Feature + 引言 + 集數列表）
/episodes            → 所有集數列表（20 集）
/episodes/[slug]     → 單集頁（音頻播放器 + Show Notes + 上下集導航）
/blog/[slug]         → Blog 文章頁（Content Collections，支援 FB 貼文同步）
```

## 設計 Token
- `--bg: #15083A`（深紫黑）
- `--surface: #0F0235`（更深紫，卡片背景）
- `--rule: #2A1A5E`（紫色邊框）
- `--accent: #EE359E`（粉紅）
- `--accent2: #815BDB`（紫色）
- `--body: #CAC0E4`（淡紫白，內文）
- `--muted: #AAA8BD`（灰紫，次要文字）
- Serif 標題（Georgia）× mono 標籤（SF Mono）× **黑體內文（Noto Sans TC → PingFang TC → Heiti TC → Microsoft JhengHei）**
- 字型 import：`Noto Sans TC` from Google Fonts（已加入 Base.astro `<head>`）

## Blog Content Collections schema
位置：`site/src/content/config.ts`
```ts
const blog = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string(),
    description: z.string().optional(),
    image: z.string().optional(),
    fbPostId: z.string().optional(),
  }),
});
export const collections = { blog };
```

## Facebook 自動同步架構（已完成，2026-07-03）
**目標：** Facebook 粉專貼文自動同步成 Blog Markdown 文章  
**方式：** GitHub Actions（非 n8n，因為環境沒裝 n8n）

### 涉及檔案
- `.github/workflows/sync-fb-posts.yml` — 每天 UTC 14:00（台北 22:00）自動執行，可手動觸發
- `.github/scripts/sync-fb-posts.js` — Node.js 腳本，呼叫 Graph API → 寫 Markdown

### Facebook App 資訊
- App 名稱：Beyond Ans Blog
- App ID：`1512554099972439`
- 粉專 Page ID：`beyond.ans`（《不標準答案》FB 粉絲專頁）

### GitHub Secret
- Secret 名稱：`FB_PAGE_ACCESS_TOKEN`
- 儲存位置：GitHub repo Settings → Secrets and variables → Actions
- ⚠️ 這個 token 是從 Graph API Explorer 取得的**短效 token**，可能 60 天後過期
  - 若自動同步失敗，先去 https://developers.facebook.com/tools/explorer/ 重新取得 Page Access Token
  - 取得步驟：選 App → 加 `pages_show_list` 權限 → 取得 User Token → 選「取得粉絲專頁存取權杖」→ 選 不標準答案 → 複製 token
  - 然後：`echo "新token" | gh secret set FB_PAGE_ACCESS_TOKEN`

### 同步邏輯
1. 呼叫 `GET https://graph.facebook.com/v25.0/beyond.ans/posts?fields=id,message,created_time,full_picture&limit=10`
2. 每篇貼文轉成 `site/src/content/blog/fb-{postId後半段}.md`
3. 已存在的檔案跳過（不覆蓋）
4. 新文章 commit `自動同步：Facebook 貼文 YYYY-MM-DD` 並 push

### 測試方式
去 GitHub → Actions → Sync Facebook Posts to Blog → Run workflow（手動觸發）

## 已完成
- [x] 首頁 Hero（家庭插畫背景 `/public/hero.png`）
- [x] 音頻播放條（可點擊跳轉、顯示時間）
- [x] 3 欄集數卡片（自動拉 Firstory 封面圖）
- [x] 主持人卡片（老查 / 阿分，從插畫裁切左右側）
- [x] Feature Section + 引言 + 集數列表 + About
- [x] PodcastSeries / PodcastEpisode JSON-LD Schema
- [x] sitemap-index.xml + robots.txt
- [x] 部署至 Cloudflare Pages
- [x] 自訂網域（beyond-ans.com，2026-07-03 Active）
- [x] 自動部署（.github/workflows/deploy.yml：push site/ 觸發 + 每週一 6am 台北時間定時 rebuild）
- [x] Google Search Console 提交 sitemap
- [x] 集數標題清理（cleanTitle() in feed.ts）
- [x] Blog Content Collections schema（config.ts）
- [x] Facebook 貼文自動同步 GitHub Action（sync-fb-posts.yml + sync-fb-posts.js）

## 待辦
- [x] 測試 Facebook 同步：已成功（2026-07-11），FB Page Token 需每 60 天更新一次；透過 `/me/accounts` 或直接呼叫 page endpoint 換 Page Token
- [x] Blog 前端頁面：`/blog` 列表頁 + `/blog/[slug]` 文章頁已完成並部署
- [x] Blog 卡片 RWD 修正：加半透明底色 + 紫色左邊框（rgba(255,255,255,0.04) + border-left: 3px solid var(--accent2)）
- [x] 全站字型換黑體：--serif / --sans / --heading 全改為 Noto Sans TC 系列（已加 Google Fonts import 至 Base.astro）
- [x] 影音頁（`/videos`）骨架已完成（空陣列 + empty state），2026-08-10 確認：卡在內容層，不是程式——YouTube 頻道正確 handle 是 `@不標準答案`（channelId `UCE-QusSupACm0Lk7D0ThHLQ`，注意不是 `@beyondanswersTW`，那個 404），頻道目前 0 支影片。等老查上傳第一支影片後，回來把資料填進 `src/pages/videos.astro` 的 `videos` 陣列（格式：`{ id, title, date, description }`）。
- [x] 2026-08-10 修正全站 YouTube 死連結：header/footer/影音頁 CTA 原本都指向不存在的 `@beyondanswersTW`，已全部改成 `@不標準答案`，並部署上線。

**Why:** 老查想要有 SEO 複利效果的 Podcast 內容資料庫，長期累積有機搜尋流量。  
**How to apply:** 每次繼續前先 `npm run dev` 確認本地環境，改動後 `npm run build` 確認無誤再部署。
