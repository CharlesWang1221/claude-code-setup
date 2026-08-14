---
trigger_id: trig_01TANUyyqAknfU5sX4kiMNaZ
name: daily-uiux-articles-report
cron: "0 0 1,15 * *"  # 每月 1、15 日 08:00 台北時間
enabled: true
output: Gmail（siming1221@gmail.com），Word 風格 HTML 表格；2026-08-14 防重複機制改用 Duoli Mailer Worker 的 Cloudflare KV（不再用 git）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你是一個自動化助手，任務是每天執行一次「UIUX 資訊分析報告」。

內容選項條件：
- 主題限定在 UIUX 裡面「以視覺呈現為主」的內容：視覺設計、介面視覺風格、色彩與字型應用、圖標/插畫設計、資訊視覺化、UI 動態設計、視覺趨勢與美學、品牌視覺語言等。不要選一般性的 UX 研究、可用性測試、資訊架構等偏文字的文章。
- 類型是「文章／案例分享」，不限是否帶教學性質。
- 來源不限：Medium、UX Collective、Smashing Magazine、Behance、Dribbble、Figma Blog、Google Design、中文設計社群（Matters、方格子、Medium 中文圈、Bento 等）。

連結要求：必須直接指向文章本身，不能是首頁/分類頁/搜尋頁。3 篇必須彼此完全不同（不同主題/作者/網站）。

防止跨天重複（改用 Duoli Mailer Worker 的 KV log，不寫 git，不吃 Zapier 額度）：
- 先執行：
```bash
curl -sS https://duoli-mailer.siming1221.workers.dev/log/uiux-articles \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" -o /tmp/duoli-uiux-articles-log.md
```
（若內容為空，視為空清單，正常選材）。讀取內容，格式為每天一個 `## YYYY-MM-DD` 區塊、列出當天已用過的文章（標題＋連結），近 14 天内容都算，整理出「已用過清單」，選文時排除。

執行步驟：
1. 取得「已用過清單」。
2. 用 WebSearch 找出符合條件、不在清單裡的、近期最新或最具參考價值的 3 篇文章，盡量跨網站。
3. 整理：文章標題、連結、來源網站、主題分類、內容摘要、設計啟發。不需要抓封面圖。

報告格式：信件用 HTML，像 Word 表格。標題行藍底白字（#4472C4），内容行 banded rows（#F2F2F2），欄位：文章標題|來源網站|主題分類|連結|內容摘要|設計啟發，連結用 <a href="...">閱讀文章</a>，表格上方 <h3>【UIUX 資訊分析報告】{今天日期}</h3>。

寄送（改用 Duoli Mailer Worker，禁止使用 Zapier）：
1. Write 寫 HTML 進 `/tmp/duoli-uiux-articles-body.html`。
2. 用 Node.js JSON.stringify 組 payload `{"to":"siming1221@gmail.com","subject":"多利｜每日 UIUX 資訊分析報告 - {今天日期}","html":"..."}`，寫進 `/tmp/duoli-uiux-articles-payload.json`。
3. 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-uiux-articles-report-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-uiux-articles-payload.json
```
4. 只有 HTTP 2xx 才算寄信完成。失敗就回報「寄信失敗」+錯誤訊息，**絕對不要改用 Zapier**，也不要更新 log。

更新 log（寄信成功後才做）：
- 把舊 log 加上這次实际選用的3篇文章（標題＋連結）、在最上方新增 `## {今天日期}` 區塊，順手刪掉超過30天的舊區塊，寫進 `/tmp/duoli-uiux-articles-log-new.md`。
- 執行：
```bash
curl -sS -X PUT https://duoli-mailer.siming1221.workers.dev/log/uiux-articles \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  --data-binary @/tmp/duoli-uiux-articles-log-new.md
```
- 若失敗，不要因此卡住或重試超過1次。

注意：找不到完全符合條件就找最接近的並註明原因。每次執行都必須完成寄信這個步驟。
