---
trigger_id: trig_01Jo3jNh1ckmveuGTN6V6HZ2
name: daily-book-summaries-3
cron: "0 0 * * *"  # 每天 08:00 台北時間（2026-08-14 由每週四改每天，CC 阿分）
enabled: true
output: Duoli Mailer Worker（siming1221@gmail.com，CC debra.hdf@gmail.com 阿分），每本書獨立區塊（7大分類）+ 綜合反思與實踐方向；2026-08-14 防重複機制改用 Duoli Mailer Worker 的 Cloudflare KV（不再用 git）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你要產生並寄出「每日5本書籍摘要」email。

## 1. 防止跨天重複（改用 Duoli Mailer Worker 的 KV log，不寫 git，不吃 Zapier 額度）
先執行：
```bash
curl -sS https://duoli-mailer.siming1221.workers.dev/log/book-summaries \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" -o /tmp/duoli-book-summaries-log.md
```
（若內容為空，視為空清單）。讀取內容，格式為每次寄送一個 `## YYYY-MM-DD` 區塊、列出的5本書（書名＋作者），過去約14天内容都算，整理出「已用過清單」。

## 2. 搜尋 5 本書籍的內容摘要
用 WebSearch（必要時 WebFetch 確認連結有效）找出 5 本書籍相關內容摘要（段落節錄、章節摘要、書評、讀書筆記、訪談提到的內容等），管道不限。外語內容必須完整翻譯成中文。5 本彼此完全不同，排除已用過清單。優先挑對收件人有實用啟發性的（收件人是 Podcast 主持人/內容創作者，經營《不標準答案》，正做 YouTube 擴張，熟悉 n8n）。連結必直接指向摘要本身。每本要足夠深度的素材（因為下面每本需產出7個項目）。

## 3. 產生 email 報告
主旨：「每日5本書籍摘要 - {今天日期}」。**不要用一行一本書的簡表**，改用每本書一個獨立區塊：
- 信件最上方：<h2 style="color:#4472C4;">【每日5本書籍摘要】{今天日期}</h2>
- 每本書：書名標題 <h3 style="color:#4472C4;border-bottom:2px solid #4472C4;">{序號}. {書名}　—　{作者}</h3>，下接一個兩欄表格（左欄分類名稱藍底白字、右欄內容、右欄banded rows），分類固定7列：1.相關摘要（5-8句） 2.重點整理（條列、方法/框架） 3.金句或段落推薦（條列引用原文，外語需中譯） 4.值得筆記地方 5.如何生活運用及節目製作 6.可引發討論地方 7.出處連結（<a href="...">查看原文</a>）。每本之間加 <hr>。
- 信件最下方加「📝 每日反思與實踐方向」：(a) 3-5句，從5本書一起看的洞察 (b) 1-2個「今天就能做」的實踐方向（條列），連結到節目製作/內容策略/個人成長。

## 4. 寄送（改用 Duoli Mailer Worker，禁止使用 Zapier）
1. Write 寫 HTML 進 `/tmp/duoli-book-summaries-body.html`。
2. Node.js JSON.stringify 組 payload `{"to":"siming1221@gmail.com","cc":"debra.hdf@gmail.com","subject":"多利｜每日5本書籍摘要 - {今天日期}","html":"..."}`，寫進 `/tmp/duoli-book-summaries-payload.json`。
3. 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-book-summaries-3-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-book-summaries-payload.json
```
4. 只有 HTTP 2xx 才算寄信完成。失敗就回報「寄信失敗」+錯誤訊息，**絕對不要改用 Zapier**，也不要更新 log。

## 5. 更新 log（寄信成功後才做）
把舊 log 加上這次選用的5本書（書名＋作者）、新增 `## {今天日期}` 區塊在最上方，順手刪掉超過14天的舊區塊，寫進 `/tmp/duoli-book-summaries-log-new.md`。執行：
```bash
curl -sS -X PUT https://duoli-mailer.siming1221.workers.dev/log/book-summaries \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  --data-binary @/tmp/duoli-book-summaries-log-new.md
```
若失敗，不要因此卡住或重試超過1次。

注意：找不到 5 本完全符合條件的書就找最接近的並註明原因。每次執行都必須完成寄信這個步驟。
