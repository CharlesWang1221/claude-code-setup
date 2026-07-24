---
trigger_id: trig_01ER4FFu49McBY8zC9gaRqUU
name: daily-ai-startup-cases-report
cron: "0 0 * * *"  # 08:00 台北時間
enabled: true
output: Gmail（siming1221@gmail.com），Word 風格 HTML 表格 + 3題反思問題
mcp_connections: [Zapier]
model: claude-sonnet-5
allowed_tools: [WebSearch, WebFetch, mcp__Zapier__list_enabled_zapier_actions, mcp__Zapier__execute_zapier_write_action, mcp__Zapier__execute_zapier_read_action, mcp__Zapier__discover_zapier_actions]
---

## Prompt

你要產生並寄出「每日AI創業案例報告」email。請依序完成以下步驟：

## 1. 防重複檢查
先用 mcp__Zapier__execute_zapier_read_action（selected_api: GoogleMailV2CLIAPI, tool_name: gmail_find_email, query: "subject:每日AI創業案例報告"）查詢近 7 天已寄送的報告內容，整理出「已用過的案例清單」（案例名稱、創辦人、公司）。只有查詢失敗或完全查不到歷史紀錄時才可略過比對，並在報告最後備註說明「本次未執行防重複比對」。

## 2. 搜尋 5 個 AI 創業真實案例
用 WebSearch（必要時 WebFetch 確認連結有效）找出 5 個「AI創業相關的真實案例」：
- 內容類型不限：創辦人故事、AI 產品從 0 到 1 的過程、AI 創業公司融資/收購/退場、AI 工具如何實際幫助創業者提升效率或營收、AI 創業失敗教訓等，只要是「真實發生過」的案例即可，不要用假設性或泛論性內容
- 管道/形式不限：文章、影片、Podcast、訪談、新聞報導、社群貼文（X/LinkedIn/Reddit 等）皆可，不必侵限單一平台
- 5 個案例必須彼此完全不同（不同公司/創辦人/事件），且必須排除步驟 1 整理出的「已用過清單」中的案例，撞到就換一個，不能因為找不到新案例而重複使用近期已寄過的內容
- 每個案例的連結必須直接指向該案例內容本身（不能是首頁、搜尋結果頁或分類頁），寄信前需確認連結有效

## 3. 產生 email 報告
主旨：「每日AI創業案例報告 - {今天日期，格式 YYYY-MM-DD}」

內容用 HTML email（body_type "html"），格式沿用「Word 風格表格」：
- 表格用 border-collapse
- 標題列藍底白字（背景色 #4472C4）
- 內容列 banded rows（淡灰交替底色）
- 欄位依序：案例標題｜來源管道｜案例類型｜連結（可點擊文字「查看案例」）｜案例摘要（2-3句）｜關鍵啟示

表格下方加一個「📝 每日反思」區塊，針對當天這 5 個案例，設計 3 個反思問題（條列式呈現），引導收件人思考：
(a) 我可以從這些案例中學到什麼（模式、心態、策略層面的啟發）
(b) 以我目前的狀態可以如何應用——收件人是 Podcast 主持人/內容創作者，經營《不標準答案》Podcast 節目、正在做 YouTube 擴張，同時熟悉 n8n 自動化工具鏈，反思問題要盡量貼近這個身分脈絡去設計，不要泛用空泛的問題

## 4. 寄送
用 mcp__Zapier__execute_zapier_write_action（selected_api: GoogleMailV2CLIAPI, action: message, tool_name: gmail_send_email）寄給收件人 siming1221@gmail.com。

寄送前務必先用 mcp__Zapier__list_enabled_zapier_actions 確認 Gmail 動作已啟用，若未啟用則用 mcp__Zapier__discover_zapier_actions 尋找並啟用。
