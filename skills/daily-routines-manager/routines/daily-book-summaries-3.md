---
trigger_id: trig_01Jo3jNh1ckmveuGTN6V6HZ2
name: daily-book-summaries-3
cron: "0 0 * * *"  # 08:00 台北時間
enabled: true
output: Gmail（siming1221@gmail.com），Word 風格 HTML 表格 + 3題反思問題
mcp_connections: [Zapier]
model: claude-sonnet-5
allowed_tools: [WebSearch, WebFetch, mcp__Zapier__list_enabled_zapier_actions, mcp__Zapier__execute_zapier_write_action, mcp__Zapier__execute_zapier_read_action, mcp__Zapier__discover_zapier_actions]
---

## Prompt

你要產生並寄出「每日3本書籍摘要」email。請依序完成以下步驟：

## 1. 防重複檢查
先用 mcp__Zapier__execute_zapier_read_action（selected_api: GoogleMailV2CLIAPI, action: message, tool_name: gmail_find_email, params: {query: "subject:每日3本書籍摘要"}）查詢過去約 7 天已寄送的報告內容，整理出「已用過的書籍清單」（書名、作者）。只有查詢失敗或完全查不到歷史紀錄時才可略過比對，並在報告最後備註說明「本次未執行防重複比對」。

## 2. 搜尋 3 本書籍的內容摘要
用 WebSearch（必要時 WebFetch 確認連結有效）找出 3 本書籍相關的摘要內容：
- 內容形式不限：書籍段落節錄、章節摘要、書評、讀書筆記、Reading list 推薦、作者訪談中談到書的內容等，只要能讓人了解這本書的核心觀點與精華即可
- 管道/平台不限：文章、部落格、Podcast 文字稿、YouTube 影片描述/字幕摘要、Goodreads、Medium、豆瓣、方格子、電子報等都可以
- 語言不限（中、英、日、其他語言皆可），但如果原始內容是外語，必須在報告中完整翻譯成中文呈現，不要留外文原文給收件人自己看
- 3 本書必須彼此完全不同（不同書名/作者），且必須排除步驟 1 整理出的「已用過清單」中的書籍，撞到就換一本，不能因為找不到新書而重複使用近期已寄過的內容
- 主題不限（商業、心理、哲學、科技、自我成長、文學等皆可），但優先挑選對收件人有實用啟發性的書籍——收件人是 Podcast 主持人/內容創作者，經營《不標準答案》Podcast 節目、正在做 YouTube 擴張，同時熟悉 n8n 自動化工具鏈
- 每本書的連結必須直接指向該摘要/書評內容本身（不能是首頁、搜尋結果頁或分類頁），寄信前需確認連結有效

## 3. 產生 email 報告
主旨：「每日3本書籍摘要 - {今天日期，格式 YYYY-MM-DD}」

內容用 HTML email（body_type "html"），呈現形式要像 Microsoft Word 裡面插入的表格一樣整齊、專業、有商務感：
- 用一個 HTML <table style="border-collapse:collapse;width:100%;font-family:Calibri,Arial,sans-serif;font-size:14px;">，每個 <th> 和 <td> 都設 style="border:1px solid #999;padding:8px 10px;text-align:left;vertical-align:top;"
- 標題行（<th>）背景色 style="background-color:#4472C4;color:#ffffff;font-weight:bold;"（Word 預設藍色表格樣式）
- 內容行（<tr>）一行白一行淡灰（background-color:#F2F2F2）交替，像 Word 的 banded rows
- 欄位依序為：書名 | 作者 | 出處/管道（含可點擊連結，例如 <a href="..." style="color:#4472C4;">查看原文</a>） | 摘要重點（3-5句中文，若原文為外語需已翻譯成中文） | 可學到什麼（1-2句，該書對收件人的啟發或應用點）
- 表格上方加一行標題文字，例如 <h3>【每日3本書籍摘要】{今天日期}</h3>
- 共 3 本書，每本一行（<tr>）

表格下方加一個「📝 每日反思」區塊，針對當天這 3 本書，設計 3 個反思問題（條列式呈現），引導收件人思考：
(a) 我可以從這幾本書中學到什麼（知識、心態、方法層面的啟發）
(b) 以我目前的狀態/處境可以如何應用——收件人是 Podcast 主持人/內容創作者，經營《不標準答案》Podcast 節目、正在做 YouTube 擴張，同時熟悉 n8n 自動化工具鏈，反思問題要盡量貼近這個身分脈絡去設計，不要泛用空泛的問題

## 4. 寄送
用 mcp__Zapier__execute_zapier_write_action（selected_api: GoogleMailV2CLIAPI, action: message, tool_name: gmail_send_email）寄給收件人 siming1221@gmail.com。

寄送前務必先用 mcp__Zapier__list_enabled_zapier_actions 確認 Gmail 動作已啟用，若未啟用則用 mcp__Zapier__discover_zapier_actions 尋找並啟用。

注意：如果找不到 3 本完全符合條件（有可用摘要內容+連結有效+不在已用過清單）的書，盡量找最接近的，並在表格下方註明實際找到的數量、原因。每次執行都必須完成寄信這個步驟，不要只做搜尋不寄信。
