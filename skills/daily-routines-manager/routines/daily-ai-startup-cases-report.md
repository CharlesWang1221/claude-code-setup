---
trigger_id: trig_01ER4FFu49McBY8zC9gaRqUU
name: daily-ai-startup-cases-report
cron: "0 0 * * *"  # 每天 08:00 台北時間（2026-08-14 由每週三改每天）
enabled: true
output: Duoli Mailer Worker（主收件人 siming1221@gmail.com，CC debra.hdf@gmail.com 阿分），Word 風格 HTML 表格 + 3題反思問題，5個案例；2026-08-14 防重複機制改用 Duoli Mailer Worker 的 Cloudflare KV（不再用 git）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你要產生並寄出「每日AI創業案例報告」email。

## 1. 防重複檢查（改用 Duoli Mailer Worker 的 KV log，不寫 git，不吃 Zapier 額度）
先執行：
```bash
curl -sS https://duoli-mailer.siming1221.workers.dev/log/ai-startup-cases \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" -o /tmp/duoli-ai-startup-cases-log.md
```
（若內容為空，視為空清單）。讀取內容，格式為每次寄送一個 `## YYYY-MM-DD` 區塊、列出的5個案例（名稱＋創辦人/公司），過去約14天内容都算，整理出「已用過清單」。

## 2. 搜尋 5 個 AI 創業真實案例
用 WebSearch（必要時 WebFetch 確認連結有效）找出 5 個「AI創業相關的真實案例」：創辦人故事、產品從0到1、融資/收購/退場、工具幫助效率或營收、失敗教訓等，只要真實發生過。管道不限（文章、影片、Podcast、訪談、新聞、社群貼文）。5個案例彼此完全不同，排除已用過清單。連結必直接指向案例本身。

## 3. 產生 email 報告
主旨：「每日AI創業案例報告 - {今天日期}」。內容用 HTML，像 Word 表格，標題行藍底白字（#4472C4），内容行 banded rows（#F2F2F2），欄位：案例標題|來源管道|案例類型|連結（<a href="...">查看案例</a>）|案例摘要|關鍵啟示。表格下方加「📝 每日反思」區塊，針對這 5 個案例設計 3 個反思問題（條列式），引導思考：(a) 學到什麼（模式/心態/策略）(b) 如何應用——收件人是 Podcast 主持人/內容創作者，經營《不標準答案》，正做 YouTube 擴張，熟悉 n8n，問題要貼近這個身份。

## 4. 寄送（改用 Duoli Mailer Worker，禁止使用 Zapier）
1. Write 寫 HTML 進 `/tmp/duoli-ai-startup-cases-body.html`。
2. Node.js JSON.stringify 組 payload `{"to":"siming1221@gmail.com","cc":"debra.hdf@gmail.com","subject":"多利｜每日AI創業案例報告 - {今天日期}","html":"..."}`，寫進 `/tmp/duoli-ai-startup-cases-payload.json`。
3. 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-ai-startup-cases-report-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-ai-startup-cases-payload.json
```
4. 只有 HTTP 2xx 才算寄信完成。失敗就回報「寄信失敗」+錯誤訊息，**絕對不要改用 Zapier**，也不要更新 log。

## 5. 更新 log（寄信成功後才做）
把舊 log 加上這次实际選用的5個案例（標題＋創辦人/公司）、新增 `## {今天日期}` 區塊在最上方，順手刪掉超過14天的舊區塊，寫進 `/tmp/duoli-ai-startup-cases-log-new.md`。執行：
```bash
curl -sS -X PUT https://duoli-mailer.siming1221.workers.dev/log/ai-startup-cases \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  --data-binary @/tmp/duoli-ai-startup-cases-log-new.md
```
若失敗，不要因此卡住或重試超過1次。
