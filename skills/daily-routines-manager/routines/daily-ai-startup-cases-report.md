---
trigger_id: trig_01ER4FFu49McBY8zC9gaRqUU
name: daily-ai-startup-cases-report
cron: "0 0 * * *"  # 每天 08:00 台北時間（2026-08-14 由每週三改每天）
enabled: true
output: Duoli Mailer Worker（主收件人 siming1221@gmail.com，CC debra.hdf@gmail.com 阿分），Word 風格 HTML 表格 + 3題反思問題，5個案例；防重複用 git log（分支 duoli-log-ai-startup-cases，近14天）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer，2026-08-14 切過來）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你要產生並寄出「每日AI創業案例報告」email。請依序完成以下步驟：

## 1. 防重複檢查（改用 repo git log，不再查 Gmail，不吃 Zapier 額度）
先用 Bash 執行：
```
git fetch origin
git checkout duoli-log-ai-startup-cases 2>/dev/null || git checkout -b duoli-log-ai-startup-cases origin/main
git pull origin duoli-log-ai-startup-cases --ff-only 2>/dev/null || true
```
讀取 `skills/daily-routines-manager/sent-log/ai-startup-cases.md`（若檔案不存在，視為空清單，正常繼續選案例，不用備註略過比對）。這份 log 記錄過去約 14 天內已用過的案例，格式為每次寄送一個 `## YYYY-MM-DD` 區塊，底下列出當次 5 個案例（案例名稱＋創辦人/公司）。整理出「已用過的案例清單」（案例名稱、創辦人、公司）。

## 2. 搜尋 5 個 AI 創業真實案例
用 WebSearch（必要時 WebFetch 確認連結有效）找出 5 個「AI創業相關的真實案例」：
- 內容類型不限：創辦人故事、AI 產品從 0 到 1 的過程、AI 創業公司融資/收購/退場、AI 工具如何實際幫助創業者提升效率或營收、AI 創業失敗教訓等，只要是「真實發生過」的案例即可，不要用假設性或泛論性內容。
- 管道/形式不限：文章、影片、Podcast、訪談、新聞報導、社群貼文（X/LinkedIn/Reddit 等）皆可，不必侵限單一平台。
- 5 個案例必須彼此完全不同（不同公司/創辦人/事件），且必須排除步驟 1 整理出的「已用過清單」中的案例，撞到就換一個，不能因為找不到新案例而重複使用近期已寄過的內容。
- 每個案例的連結必須直接指向該案例內容本身（不能是首頁、搜尋結果頁或分類頁），寄信前需確認連結有效。

## 3. 產生 email 報告
主旨：「每日AI創業案例報告 - {今天日期，格式 YYYY-MM-DD}」

內容用 HTML email，格式沿用「Word 風格表格」：
- 表格用 border-collapse
- 標題列藍底白字（背景色 #4472C4）
- 內容列 banded rows（淡灰交替底色）
- 欄位依序：案例標題｜來源管道｜案例類型｜連結（可點擊文字「查看案例」）｜案例摘要（2-3句）｜關鍵啟示

表格下方加一個「📝 每日反思」區塊，針對當天這 5 個案例，設計 3 個反思問題（條列式呈現），引導收件人思考：
(a) 我可以從這些案例中學到什麼（模式、心態、策略層面的啟發）
(b) 以我目前的狀態可以如何應用——收件人是 Podcast 主持人/內容創作者，經營《不標準答案》Podcast 節目、正在做 YouTube 擴張，同時熟悉 n8n 自動化工具鏈，反思問題要盡量貼近這個身份脈絡去設計，不要泛用空泛的問題。

## 4. 寄送（改用 Duoli Mailer Worker，禁止使用 Zapier）
1. 用 Write 工具把上面產生的完整 HTML email 內容寫進暫存檔 `/tmp/duoli-ai-startup-cases-body.html`。
2. 用 Bash/Node.js 讀出暫存檔內容，組成 JSON payload：`{"to":"siming1221@gmail.com","cc":"debra.hdf@gmail.com","subject":"多利｜每日AI創業案例報告 - {今天日期}","html":"..."}`（html 欄位放暫存檔完整內容），寫進 `/tmp/duoli-ai-startup-cases-payload.json`。組 JSON 務必用程式（例如 Node.js `JSON.stringify`）處理，不要手動拼字串。subject 必須以「多利｜」開頭。
3. 用 Bash 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-ai-startup-cases-report-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-ai-startup-cases-payload.json
```
4. 只有 curl 回應成功（HTTP 2xx）才算寄信完成。若失敗（非 2xx、連線錯誤、或環境變數 `$DUOLI_WEBHOOK_TOKEN` 未設定）：直接回報「寄信失敗」＋實際錯誤訊息，**絕對不要改用 Zapier**，也不要進行下一步的 log 更新。

## 5. 更新 log 並 commit（寄信成功後才做，只寫這一個 log 檔，不要動 repo 裡其他任何檔案，也不要碰 main 分支）
用 Bash 把這次實際選用的5 個案例（案例名稱＋創辦人/公司）append 進 `skills/daily-routines-manager/sent-log/ai-startup-cases.md`：在檔案最上方新增一個 `## {今天日期 YYYY-MM-DD}` 區塊，列出這 5 個（每個一行 `- {案例名稱} — {創辦人/公司}`）。順手刪掉超過 14 天以前的舊區塊。
完成後執行：
```
git add skills/daily-routines-manager/sent-log/ai-startup-cases.md
git commit -m "多利日誌 daily-ai-startup-cases-report {今天日期}"
git push origin duoli-log-ai-startup-cases
```
若 push 失敗，不要因此卡住或重試超過1次。
