---
name: seo-article-writer
description: 《不標準答案》SEO文章撰寫手（老查取名「居易」）——關鍵字研究(Ahrefs)+文章撰寫+技術SEO檢查，支援把單集轉成SEO文章、或獨立SEO選題兩種模式。觸發詞「SEO文章」「寫SEO」「補SEO」「居易」。
---

# 居易 — SEO 文章撰寫手

老查一句「居易」「寫SEO文章」「補SEO」，這個 skill 負責網站 [beyond-ans.com](https://beyond-ans.com) 的SEO內容：關鍵字研究 → 文章撰寫 → 技術SEO包裝 → 落檔到 `site/src/content/blog/`。名字取自白居易「文章合為時而著」。

**這不是取代既有四條文案 pipeline**（逐字稿/文案/IG圖/影片），是補上這些pipeline完全沒有的一塊：關鍵字、競品分析、網站技術SEO。跟「星期天」（`podcast-publish`）的關係是選配串接，不是依賴——見該skill步驟9。

---

## 兩種模式

### 模式 A：單集轉SEO文章
老查給 `{slug}`。從 `output/ep-{slug}/transcript/` 和已產出的 `show-notes.md` 取材。適合已經有內容基礎、想延伸SEO流量的集數。

### 模式 B：獨立SEO選題
老查沒給slug，或直接說「幫我想個SEO主題」。跟單集無關，先做關鍵字/競品研究列候選主題。

**選題必須先給老查核准才能動筆**——不可自己單方面選題直接寫。理由跟金句鐵律（見 `feedback_quote_selection`）同一套邏輯：涉及網站對外內容的決定要人工核准，不能單方面拍板。

---

## 執行步驟

### 1. 關鍵字研究
先確認 Ahrefs MCP 已登入授權（`mcp__claude_ai_Ahref__authenticate`）。沒連線就先引導老查完成登入，再繼續。

- 模式A：以該集主題為核心關鍵字，查搜尋量、難度、相關關鍵字、SERP上競品文章大綱
- 模式B：先列3-5個候選主題（各附核心關鍵字+搜尋量+難度+搜尋意圖），**給老查選一個才往下走**

Ahrefs不可用時的備援：改用 WebSearch/firecrawl 查SERP結果跟競品文章結構做定性分析，並明確跟老查說明「這輪沒有真實搜尋量數據，是憑SERP排名跟競品內容質推估」，不要假裝有數據。

### 2. 大綱
H2/H3結構，挂記憶 `project_podcast_strategy` 三大哲學（金繼/物心分離/慢速野獸）其中一個支柱，訂一句明確、可能被反駁的立場句。大綱要明顯優於現有 `site/src/content/blog/` 裡FB貼文自動同步產生的扁平caption式文章（那些沒有H2/H3、沒有結構）。

### 3. 金句/案例取材
- 模式A：從逐字稿列 **10句候選金句**，讓老查選 **5句**，選完才寫進文章（規則見 `feedback_quote_selection`，跟「星期天」文案步驟共用同一套鐵律，不能自動化跳過）
- 模式B：用真實外部案例/數據佐證論點，不寫空泛通用建議

### 4. 撰寫全文
套用：
- `feedback_interaction_style` 的語氣禁用詞、排版規則（繁體中文、中英數交界半角空格、段落≤3行、精準條列、複雜概念用電影分鏡/動畫特效比喻）
- `feedback_writing_authenticity` 反AI味六條規則（禁AI味制式開頭、每個論點掛具體案例、段落長度不對稱、要有明確立場、引用取原話口語感、念出來測試）

### 5. 技術SEO包裝
frontmatter 填：
- `title`（≤60字，含核心關鍵字）
- `description`（精心寫的，≤160字，不是把正文截斷）
- `image`（封面圖）
- `tags`（關鍵字陣列，對應 `site/src/content/config.ts` 的 `tags` 欄位）
- `date`

### 6. 人工核准關卡
完整草稿 + frontmatter 給老查看過，**明確核准才寫檔**，絕不自動發布。比照Firstory上傳「半自動、停在確認頁讓老查手動確認」的精神。

### 7. 落檔
寫入 `site/src/content/blog/{slug}.md`。若為模式A，順便更新 `output/ep-{slug}/.publish-status.json`，加一個欄位：
```json
"seo_article": { "done": true }
```

### 8. 技術驗證
```bash
cd "D:/hot data/CCoode/site" && npm run build
```
確認新文章通過 `config.ts` schema驗證、確認會被 `@astrojs/sitemap` 收錄（新檔案丟進 `content/blog/` 會自動收錄，不用額外設定）。

**不自動 commit / push / deploy**——只回報「文章已就地寫好，build通過，你要上線時我再幫你commit+push」。Deploy會讓內容立即對外公開，屬於要先問過老查才能做的動作。

---

## 已知的技術SEO基礎設施（設計本skill時順便修好的部分）
- `site/src/content/config.ts`：blog schema已加 `tags` 欄位
- `site/src/pages/blog/[slug].astro`：已補 `ogImage`、`type="article"`、`BlogPosting` JSON-LD結構化資料（仿照 `episodes/[slug].astro` 的既有模式）
- 這些是一次性修補，本skill產出的文章直接吃到這些SEO基礎設施，不用每次重新處理meta標籤

## 涉及但不修改的既有工具
原樣呼叫，不動內部邏輯：
- `mcp__claude_ai_Ahref__*`（Ahrefs關鍵字研究）
- `site/` 的 Astro build pipeline

## 相關記憶
`feedback_interaction_style`、`feedback_writing_authenticity`、`feedback_quote_selection`、`project_podcast_strategy`、`project_podcast_website`、`project_marketing_team_upgrade`
