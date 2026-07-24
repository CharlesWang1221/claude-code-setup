---
trigger_id: trig_01Jo3jNh1ckmveuGTN6V6HZ2
name: daily-book-summaries-3
cron: "0 0 * * *"  # 08:00 台北時間
enabled: true
output: Gmail（siming1221@gmail.com），每本書獨立區塊（7大分類：相關摘要/重點整理/金句段落/值得筆記/生活與節目運用/可引發討論/出處連結）+ 綜合反思與實踐方向
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
- 找每本書的內容時要蒐集足夠深度的素材（不能只有一句話的介紹），因為下面步驟3每本書要產出7個項目的完整內容，資料不夠深就換一本或多找幾個來源補齊

## 3. 產生 email 報告
主旨：「每日3本書籍摘要 - {今天日期，格式 YYYY-MM-DD}」

內容用 HTML email（body_type "html"）。**不要用「一行一本書」的簡表**，一本書不可能用幾句話講完，改採「每本書一個獨立區塊」的呈現方式，維持 Word 風格的整齊、專業、商務感：

- 信件最上方：<h2 style="color:#4472C4;">【每日3本書籍摘要】{今天日期}</h2>
- 每本書一個區塊，依序包含：
  - 書名標題：<h3 style="color:#4472C4;border-bottom:2px solid #4472C4;padding-bottom:4px;">{序號}. {書名}　—　{作者}</h3>
  - 一個兩欄表格 <table style="border-collapse:collapse;width:100%;font-family:Calibri,Arial,sans-serif;font-size:14px;margin-bottom:28px;">，每一列 <tr> 代表一個分類：左欄 <td style="width:160px;background-color:#4472C4;color:#ffffff;font-weight:bold;padding:8px 10px;vertical-align:top;"> 放分類名稱，右欄 <td style="padding:8px 10px;border:1px solid #ccc;vertical-align:top;"> 放內容，各列右欄背景色白/淡灰（#F2F2F2）交替，像 Word 的 banded rows
  - 表格分類固定 7 列，依序：
    1. 相關摘要：5-8 句話說明這本書在講什麼、核心論點與架構
    2. 重點整理：條列（<ul><li>）4-6 點，拆解本書的核心論點/方法/框架
    3. 金句或段落推薦：條列 2-3 段直接引用原文的金句或精彩段落，若原文外語需附中文翻譯並標註原文語言，盡量附出處（章節/頁數，若查得到）
    4. 值得筆記的地方：條列 3-4 點，反直覺、容易被忽略、特別值得記下來的細節或案例
    5. 如何生活運用及節目製作：條列 3-4 點，具體說明怎麼運用在日常生活中，以及具體怎麼用在《不標準答案》節目製作上（例如可連結到哪個內容支柱——社會議題深度集／金繼時刻／書喔吾聊、可當開場故事、可發展成哪種選題角度）
    6. 可引發討論的地方：條列 2-3 點，這本書有沒有爭議性、反直覺、值得挑戰的觀點，適合拿出來討論辯論的角度
    7. 出處連結：<a href="..." style="color:#4472C4;">查看原文</a>，必須直接指向該摘要/書評內容本身
  - 每本書區塊之間加分隔線 <hr style="border:none;border-top:1px solid #ddd;margin:24px 0;">

信件最下方（3 本書都寫完之後）加一個「📝 每日反思與實踐方向」區塊——**不是條列反思問題，是直接給出綜合性的反思內容與具體行動建議**：
(a) 一段文字（3-5句），從今天這 3 本書放在一起看，點出彼此呼應或矛盾張力之處，帶出對收件人最值得思考的一個洞察——收件人是 Podcast 主持人/內容創作者，經營《不標準答案》Podcast 節目、正在做 YouTube 擴張，同時熟悉 n8n 自動化工具鏈，內容要貼近這個身分脈絡
(b) 條列（<ul><li>）1-2 個「今天/這週就能做」的具體實踐方向，明確連結到節目製作、內容策略或個人成長，不要泛用空泛的建議

## 4. 寄送
用 mcp__Zapier__execute_zapier_write_action（selected_api: GoogleMailV2CLIAPI, action: message, tool_name: gmail_send_email）寄給收件人 siming1221@gmail.com。

寄送前務必先用 mcp__Zapier__list_enabled_zapier_actions 確認 Gmail 動作已啟用，若未啟用則用 mcp__Zapier__discover_zapier_actions 尋找並啟用。

注意：如果找不到 3 本完全符合條件（有足夠深度的摘要內容+連結有效+不在已用過清單）的書，盡量找最接近的，並在信件最下方註明實際找到的數量、原因。每次執行都必須完成寄信這個步驟，不要只做搜尋不寄信。
