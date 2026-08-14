---
trigger_id: trig_01Jo3jNh1ckmveuGTN6V6HZ2
name: daily-book-summaries-3
cron: "0 0 * * *"  # 每天 08:00 台北時間（2026-08-14 由每週四改每天，CC 阿分）
enabled: true
output: Duoli Mailer Worker（siming1221@gmail.com，CC debra.hdf@gmail.com 阿分），每本書獨立區塊（7大分類：相關摘要/重點整理/金句段落/值得筆記/生活與節目運用/可引發討論/出處連結）+ 綜合反思與實踐方向；防重複用 git log（分支 duoli-log-book-summaries，近14天）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer，2026-08-14 切過來）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你要產生並寄出「每日5本書籍摘要」email。請依序完成以下步驟：

## 1. 防止跨天重複（改用 repo git log，不再查 Gmail，不吃 Zapier 額度）
先用 Bash 執行：
```
git fetch origin
git checkout duoli-log-book-summaries 2>/dev/null || git checkout -b duoli-log-book-summaries origin/main
git pull origin duoli-log-book-summaries --ff-only 2>/dev/null || true
```
讀取 `skills/daily-routines-manager/sent-log/book-summaries.md`（若檔案不存在，視為空清單，正常繼續選書，不用備註略過比對）。這份 log 記錄過去約 14 天內已用過的書籍，格式為每次寄送一個 `## YYYY-MM-DD` 區塊，底下列出當次 5 本書（書名＋作者）。整理出「已用過的書籍清單」（書名、作者）。

## 2. 搜尋 5 本書籍的內容摘要
用 WebSearch（必要時 WebFetch 確認連結有效）找出 5 本書籍相關的內容摘要：
- 內容形式不限：書籍段落節錄、章節摘要、書評、讀書筆記、Reading list 推薦、作者訪談中談到書的內容等，只要能讓人了解這本書的核心觀點與精華即可。
- 管道/平台不限：文章、部落格、Podcast 文字稿、YouTube 影片描述/字幕摘要、Goodreads、Medium、豆瓣、方格子、電子報等都可以。
- 語言不限（中、英、日、其他語言皆可），但如果原始內容是外語，必須在報告中完整翻譯成中文呈現，不要留外文原文給收件人自己看。
- 5 本書必須彼此完全不同（不同書名/作者），且必須排除步驟 1 整理出的「已用過清單」中的書籍，撞到就換一本，不能因為找不到新書而重複使用近期已寄過的內容。
- 主題不限（商業、心理、哲學、科技、自我成長、文學等皆可），但優先挑選對收件人有實用啟發性的書籍——收件人是 Podcast 主持人/內容創作者，經營《不標準答案》Podcast 節目、正在做 YouTube 擴張，同時熟悉 n8n 自動化工具鏈。
- 每本書的連結必須直接指向該摘要/書評內容本身（不能是首頁、搜尋結果頁或分類頁），寄信前需確認連結有效。
- 找每本書的內容時要蒐集足夠深度的素材（不能只有一句話的介紹），因為下面步驟3每本書要產出7個項目的完整內容，資料不夠深就換一本或多找幾個來源補齊。

## 3. 產生 email 報告
主旨：「每日5本書籍摘要 - {今天日期，格式 YYYY-MM-DD}」

內容用 HTML email。**不要用「一行一本書」的簡表**，一本書不可能用幾句話講完，改採「每本書一個獨立區塊」的呈現方式，維持 Word 風格的整齊、專業、商務感：
- 信件最上方：<h2 style="color:#4472C4;">【每日5本書籍摘要】{今天日期}</h2>
- 每本書一個區塊，依序包含：
  - 書名標題：<h3 style="color:#4472C4;border-bottom:2px solid #4472C4;padding-bottom:4px;">{序號}. {書名}　—　{作者}</h3>
  - 一個兩欄表格 <table style="border-collapse:collapse;width:100%;font-family:Calibri,Arial,sans-serif;font-size:14px;margin-bottom:28px;">，每一列 <tr> 代表一個分類：左欄 <td style="width:160px;background-color:#4472C4;color:#ffffff;font-weight:bold;padding:8px 10px;vertical-align:top;"> 放分類名稱，右欄 <td style="padding:8px 10px;border:1px solid #ccc;vertical-align:top;"> 放內容，各列右欄背景色白/淡灰（#F2F2F2）交替，像 Word 的 banded rows
  - 表格分類固定 7 列，依序：
    1. 相關摘要：5-8 句話說明這本書在講什麼、核心論點與架構
    2. 重點整理：條列（<ul><li>）4-6 點，拆解本書的核心論點/方法/框架
    3. 金句或段落推薦：條列 2-3 段直接引用原文的金句或精彩段落，若原文外語需附中文翻譯並標註原文語言，盡量附出處（章節/頁數，若查得到）
    4. 值得筆記的地方：條列 3-4 點，反直覺、容易被忽略、特別值得記下來的細節或案例
    5. 如何生活運用及節目製作：條列 3-4 點，具體說明怎麼運用在日常生活中，以及具體怎麼用在《不標準答案》節目製作上
    6. 可引發討論的地方：條列 2-3 點，這本書有沒有爭議性、反直覺、值得挑戰的觀點，適合拿出來討論辯論的角度
    7. 出處連結：<a href="..." style="color:#4472C4;">查看原文</a>，必須直接指向該摘要/書評內容本身
  - 每本書區塊之間加分隔線 <hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">

信件最下方（5 本書都寫完之後）加一個「📝 每日反思與實踐方向」區塊：
(a) 一段文字（3-5句），從這 5 本書放在一起看，點出彼此呼應或矛盾張力之處，帶出對收件人最值得思考的一個洞察
(b) 條列（<ul><li>）1-2 個「今天就能做」的具體實踐方向，明確連結到節目製作、內容策略或個人成長

## 4. 寄送（改用 Duoli Mailer Worker，禁止使用 Zapier 或任何其他管道）
1. 用 Write 工具把上面產生的完整 HTML email 內容寫進暫存檔 `/tmp/duoli-book-summaries-body.html`。
2. 用 Bash/Node.js 讀出暫存檔內容，組成 JSON payload：`{"to":"siming1221@gmail.com","cc":"debra.hdf@gmail.com","subject":"多利｜每日5本書籍摘要 - {今天日期}","html":"..."}`（html 欄位放暫存檔完整內容），寫進 `/tmp/duoli-book-summaries-payload.json`。組 JSON 務必用程式（例如 Node.js `JSON.stringify`）處理，不要手動拼字串。subject 必須以「多利｜」開頭。
3. 用 Bash 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-book-summaries-3-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-book-summaries-payload.json
```
4. 只有 curl 回應成功（HTTP 2xx）才算寄信完成。若失敗（非 2xx、連線錯誤、或環境變數 `$DUOLI_WEBHOOK_TOKEN` 未設定）：直接回報「寄信失敗」＋實際錯誤訊息，**絕對不要改用 Zapier，也不要進行下一步的 log 更新**。

## 5. 更新 log 並 commit（寄信成功後才做，只寫這一個 log 檔，不要動 repo 裡其他任何檔案，也不要碰 main 分支）
用 Bash 把這次實際選用的5 本書（書名＋作者）append 進 `skills/daily-routines-manager/sent-log/book-summaries.md`：在檔案最上方新增一個 `## {今天日期 YYYY-MM-DD}` 區塊，列出這 5 本（每本一行 `- {書名} — {作者}`）。順手刪掉超過 14 天以前的舊區塊。
完成後執行：
```
git add skills/daily-routines-manager/sent-log/book-summaries.md
git commit -m "多利日誌 daily-book-summaries-3 {今天日期}"
git push origin duoli-log-book-summaries
```
若 push 失敗，不要因此卡住或重試超過1次。

注意：如果找不到 5 本完全符合條件（有足夠深度的摘要內容+連結有效+不在已用過清單）的書，盡量找最接近的，並在信件最下方註明實際找到的數量、原因。每次執行都必須完成寄信這個步驟，不要只做搜尋不寄信。
