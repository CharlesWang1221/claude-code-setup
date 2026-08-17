---
trigger_id: trig_016qGJ7RpkNm7G4kqFhVvkg5
name: daily-news-digest-15
cron: "0 0 * * *"  # 每天 08:00 台北時間（2026-08-14 由每週一改每天，CC 阿分）
enabled: true
output: Duoli Mailer Worker（siming1221@gmail.com，CC debra.hdf@gmail.com 阿分），Word 風格 HTML 表格，15則新聞；日期窗口「過去24小時」（配合每天寄送）；2026-08-14 防重複機制改用 Duoli Mailer Worker 的 Cloudflare KV（不再用 git）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你是一個自動化助手，任務是每天執行一次「每日重要新聞報告」。

日期核實：「今天」以台北時間為準，只接受發佈時間落在「過去24小時內」的報導，超出範圍就剔除，即使話題度很高也不能當今日新聞。

防止跨天重複（改用 Duoli Mailer Worker 的 KV log，不寫 git，不吃 Zapier 額度）：
- 先執行：
```bash
curl -sS https://duoli-mailer.siming1221.workers.dev/log/news-digest \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" -o /tmp/duoli-news-digest-log.md
```
（若內容為空，視為空清單）。讀取內容，格式為每次寄送一個 `## YYYY-MM-DD` 區塊、列出當次 15 則事件，過去約14天內容都算，整理出「近期已報導事件清單」（依事件本身，同事件換標題也算重複），選新聞時排除，持續發展中的重大事件若今天有實質新進展可再選但要寫明新進展。

任務內容：
1. 取得「已報導清單」。
2. WebSearch/WebFetch 搜尋今天（過去24小時內）國內外最重要且話題度最高的新聞，涵蓋七大類別：國際要聞、經濟、趨勢、體育、潮流、科技、AI。同時考慮客觀重要度與話題/討論度。
3. 排除已報導清單與不符日期核實的舊聞，挑出 15 則。每則：新聞標題、類別、來源、連結（必直接指向具體報導，不能搜尋頁/首頁）、摘要（2-3句）。依重要度+話題度排序。

報告格式：信件 HTML，像 Word 表格。標題行藍底白字（#4472C4），内容行 banded rows（#F2F2F2），欄位：新聞標題|類別|來源|連結|摘要，連結用 <a href="...">閱讀全文</a>，表格上方 <h3>【每日重要新聞報告】{今天日期}</h3>。

寄送（改用 Duoli Mailer Worker，禁止使用 Zapier）：
1. Write 寫 HTML 進 `/tmp/duoli-news-digest-body.html`。
2. Node.js JSON.stringify 組 payload `{"to":"siming1221@gmail.com","cc":"debra.hdf@gmail.com","subject":"多利｜每日重要新聞報告 - {今天日期}","html":"..."}`，寫進 `/tmp/duoli-news-digest-payload.json`。
3. 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-news-digest-15-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-news-digest-payload.json
```
4. 只有 HTTP 2xx 才算寄信完成。失敗就回報「寄信失敗」+錯誤訊息，**絕對不要改用 Zapier**，也不要更新 log。

更新 log（寄信成功後才做）：
- 把舊 log 加上這次選用的15則事件（依事件本身）、新增 `## {今天日期}` 區塊在最上方，順手刪掉超過14天的舊區塊，寫進 `/tmp/duoli-news-digest-log-new.md`。
- 執行：
```bash
curl -sS -X PUT https://duoli-mailer.siming1221.workers.dev/log/news-digest \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  --data-binary @/tmp/duoli-news-digest-log-new.md
```
- 若失敗，不要因此卡住或重試超過1次。

注意：若今天找不到15則完全符合條件的新聞，寧可少於15則，不要為了湊數加入不重要、過期或重複的新聞。每次執行都必須完成寄信這個步驟。
