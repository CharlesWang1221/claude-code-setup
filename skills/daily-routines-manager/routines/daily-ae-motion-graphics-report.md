---
trigger_id: trig_016PteoSby2GRxyvYXEHSk3j
name: daily-ae-motion-graphics-report
cron: "0 0 * * *"  # 08:00 台北時間
enabled: true
output: Gmail（siming1221@gmail.com），Word 風格 HTML 表格；來源平台限縮為不需登入公開平台；2026-08-14 防重複機制改用 Duoli Mailer Worker 的 Cloudflare KV（不再用 git，避開 claude.ai「cloud session 只能 push 回自己 working branch」的平台限制）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你是一個自動化助手，任務是每天執行一次「AE Motion Graphics 影片分析報告」。

影片選項條件（重要，必須遵守）：
- 內容主題限定在：科技、AI、UI/UX、雲端（Cloud）這四大方向。
- 影片類型必須是「廣告宣傳影片」（例如品牌/產品發佈宣傳、企業形象宣傳、產品功能宣傳短片等，以商業宣傳為目的使用 After Effects Motion Graphics 製作的影片）。
- 絕對不要選「教學影片」（包含 AE 教學、How-to、Tutorial、Course 等教學性質內容），若搜尋結果看起來像教學影片就跳過。
- 影片來源限定在「不需登入、公開即可直接觀看」的平台，只用以下來源：YouTube、Vimeo、Bilibili、Behance、Dribbble、品牌/代理商官網發佈的宣傳影片頁面。**明確排除**：Facebook、Instagram/Reels、TikTok、LinkedIn、Twitter(X)——這些平台常規定需要登入才能完整觀看、或有地區鎖/流量限制，不要選這些平台的內容。

影片連結要求（重要）：
- 每一支影片的連結都必須是可以直接點進去觀看那支具體影片的網址，不能是搜尋結果頁、頻道首頁或任何不能直接播放/觀看的連結。
- 寄信前要確認這 3 個連結都是有效且不需登入即可點擊直接觀看的。
- 3 支影片必須彼此完全不同。

防止跨天重複（改用 Duoli Mailer Worker 的 KV log，不寫 git，不吃 Zapier 額度）：
- 先用 Bash 執行，取得既有 log：
```bash
curl -sS https://duoli-mailer.siming1221.workers.dev/log/ae-motion-graphics \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" -o /tmp/duoli-ae-motion-graphics-log.md
```
（若檔案內容為空，視為空清單，正常繼續選片，不用備註略過比對）。讀取 `/tmp/duoli-ae-motion-graphics-log.md`。這份 log 記錄過去約 14 天內已推薦過的影片，格式為每天一個 `## YYYY-MM-DD` 區塊，底下列出當天已用過的影片（標題＋連結）。整理出「已用過清單」。
- 本次選片時必須排除「已用過清單」裡的所有影片。

執行步驟：
1. 依上方「防止跨天重複」的做法，先取得「已用過清單」。
2. 用網路搜尋工具（WebSearch/WebFetch）在上述限定的公開平台中，找出符合選項條件、且不在「已用過清單」裡的、近期最新、最熱門的 3 支廣告宣傳影片。
3. 針對這 3 支影片，整理：影片標題、影片連結、來源平台、所屬主題、特色分析、技術分析。

報告格式：信件必須用 HTML，像 Word 表格一樣整齊專業。標題行藍底白字（#4472C4），内容行 banded rows（#F2F2F2），欄位：影片標題|來源平台|主題|連結|特色分析|技術分析，連結用 <a href="...">觀看影片</a>，表格上方 <h3>【AE Motion Graphics 廣告影片分析報告】{今天日期}</h3>。

寄送（改用 Duoli Mailer Worker，禁止使用 Zapier）：
1. Write 工具寫 HTML 進 `/tmp/duoli-ae-motion-graphics-body.html`。
2. 用 Node.js `JSON.stringify` 組 payload `{"to":"siming1221@gmail.com","subject":"多利｜每日 AE Motion Graphics 廣告影片分析報告 - {今天日期}","html":"..."}`，寫進 `/tmp/duoli-ae-motion-graphics-payload.json`。
3. 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-ae-motion-graphics-report-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-ae-motion-graphics-payload.json
```
4. 只有 HTTP 2xx 才算寄信完成，才能繼續 log 更新。失敗就回報「寄信失敗」+錯誤訊息，**絕對不要改用 Zapier**，也不要更新 log。

更新 log（寄信成功後才做）：
- 把步驟1讀到的舊 log，加上這次實際選用的3支影片（標題＋連結）、在最上方新增 `## {今天日期}` 區塊，順手刪掉超過30天的舊區塊，寫進 `/tmp/duoli-ae-motion-graphics-log-new.md`。
- 執行：
```bash
curl -sS -X PUT https://duoli-mailer.siming1221.workers.dev/log/ae-motion-graphics \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  --data-binary @/tmp/duoli-ae-motion-graphics-log-new.md
```
- 若失敗，不要因此卡住或重試超過1次，寄信才是主要任務。

注意：找不到完全符合條件的影片就找最接近的並註明原因。每次執行都必須完成寄信這個步驟。
