---
name: daily-routines-manager
description: 每日 cloud routine 排程總管（老查取名「多利」）——列出/新增/修改/暫停/測試所有每日寄送/寫入的排程內容（AE影片分析、每日新聞、UIUX報告、AI創業案例、書籍摘要、節目方向靈感、影片分析寫入repo等）。觸發詞「多利」。
---

# 多利 — 每日排程總管

老查一句「多利」或「多利，幫我 XXX」，就叫出這個 skill 來管理所有每天自動執行的 cloud routine（用 `RemoteTrigger` 操作 claude.ai routines API）。老查不用自己去記每個 routine 的 trigger_id、cron 語法或既有樣板，多利負責把要求翻譯成正確的 API 呼叫，並把異動同步寫回這個 repo。

（內部技術識別名維持 `daily-routines-manager`——skill 系統規定 name 只能用小寫英文+數字+橫線，中文名只能放在暱稱/觸發詞，不影響喊「多利」直接叫出這個流程。）

---

## 備份清單：`routines/`

`routines/README.md` 是目前所有 routine 的索引表，每個 routine 各有一份 `.md` 備份檔（trigger_id、cron、收件方式、完整 prompt）。**這是 git 版本追蹤用的備份，不是即時狀態**——每次被叫出來，第一步一定是用 `RemoteTrigger {action:"list"}` 拉即時清單，跟本地檔案核對，若有落差（老查在別的地方新增/改過、或本地缺記錄）先同步好再繼續。

---

## 執行步驟

### 0. 先同步狀態
呼叫 `RemoteTrigger {action:"list"}`，比對 `routines/README.md` 的表格：
- 線上有、本地沒有 → 補建一份 `.md` 備份檔 + 補進 README 表格
- 線上內容跟本地不一致（cron、prompt 改過）→ 更新本地檔案
- 本地有、線上已被刪除（`ended_reason` 顯示異常或查不到）→ 在 README 標記「已刪除」，檔案可以留著當歷史記錄，不用刪

### 1. 依老查的指令分流

**查狀態 / 列清單**（「多利，現在有哪些」「多利，列一下」）
直接呼叫 `RemoteTrigger list`，整理成表格回報：名稱、時間、輸出方式、下次執行時間、啟用狀態。不用先問，直接執行。

**新增一個新的每日報告**（「多利，我要多加一個 XXX」）
1. 先問清楚：主題/搜尋範圍、輸出方式（寄信 vs 寫入 repo）、收件人（沒說就預設 siming1221@gmail.com）、寄送時間（沒說就預設 08:00 台北 = cron `0 0 * * *`）、要不要防重複機制（預設要）。
2. 若是寄信類報告，套用既有樣板結構（可直接參考 `routines/daily-book-summaries-3.md` 或 `routines/daily-ai-startup-cases-report.md` 當範本複製修改）：
   - 防重複：先用 `mcp__Zapier__execute_zapier_read_action`（`gmail_find_email`，query 用 `subject:{報告標題}`）查近 7 天已寄送內容，整理「已用過清單」，撞到就換一個
   - 內容：用 WebSearch/WebFetch 搜尋，管道與語言不限但外語內容要翻中文，連結必須直接指向內容本身（不能是首頁/搜尋頁）
   - 格式：Word 風格 HTML 表格（`border-collapse`、標題列 `background-color:#4472C4;color:#ffffff`、內容列 banded rows `#F2F2F2` 交替）
   - 若老查要求要反思問題，表格下方加「📝 每日反思」區塊，3 個問題要緊扣老查身分脈絡（Podcast主持人/內容創作者，經營《不標準答案》、YouTube擴張、熟悉n8n自動化，見記憶 `user_profile`），不要泛用空泛的問題
   - 寄送：`mcp__Zapier__list_enabled_zapier_actions` 確認 Gmail 動作可用 →`mcp__Zapier__execute_zapier_write_action`（`gmail_send_email`）寄出
   - `mcp_connections` 用 Zapier：`{connector_uuid: "4a34f6a9-553f-4645-939f-708b21535f24", name: "Zapier", url: "https://mcp.zapier.com/api/v1/connect"}`
   - `environment_id`: `env_012PXqxpqYN4yzPvZoiGdmLf`，`model`: `claude-sonnet-5`
3. 若是寫入 repo 類任務（像「影片分析每日推薦」），套用 `routines/video-analysis-daily.md` 的樣板：獨立分支、檢查歷史避免重複、只在指定資料夾寫檔、commit+push。
4. 確認內容後用 `RemoteTrigger {action:"create"}` 建立，成功後：在 `routines/` 新增對應 `.md` 檔、更新 `routines/README.md` 表格，並用 git commit（訊息格式：「多利：新增每日排程 {名稱}」）。不要自動 push，除非老查明確要求。
5. 回報 routine 名稱、trigger_id、下次執行時間、claude.ai 管理連結。

**修改現有 routine**（改時間、改收件人、改搜尋條件、暫停/啟用）
1. 從 `routines/README.md` 或 `RemoteTrigger list` 找到對應 trigger_id，跟老查確認要改的內容（給出「目前 vs 改成」對照）。
2. 呼叫 `RemoteTrigger {action:"update", trigger_id, body:{...}}`（partial update，只送要改的欄位）。
3. 同步更新本地對應 `.md` 檔與 README 表格，git commit（訊息：「多利：更新排程 {名稱}」）。

**暫停 / 重新啟用**
`RemoteTrigger update`，`body: {enabled: false}` 或 `{enabled: true}`。同步更新本地檔案的 `enabled` 欄位。

**立即測試一次**
`RemoteTrigger {action:"run", trigger_id}`，回報 session_id，提醒老查等幾分鐘去信箱/repo 確認結果。

**刪除**
`RemoteTrigger` 的 API 不支援刪除。導去 https://claude.ai/code/routines 讓老查手動刪，刪除後把 `routines/` 對應檔案標記「已刪除」（不用真的移除檔案，留歷史），git commit。

### 2. 結尾報告
每次異動完，用一個簡短表格列出「異動前 → 異動後」，並提醒是否已 commit（有沒有 push）。

---

## 安全邊界
- 只在 `skills/daily-routines-manager/routines/` 這個路徑下新增/修改檔案，不要動其他 skill 或 output 資料夾。
- git 只 commit，不主動 push，除非老查明確說要 push。
- 建立/修改 routine 前，涉及寄送對象、時間、內容範圍的變動一定要跟老查確認過才送出 API 呼叫，不要自己猜著就建立。

## 相關記憶
`user_profile`、`project_daily_ae_video_report`、`project_daily_news_digest`、`project_daily_uiux_report`、`project_daily_ai_startup_cases_report`、`project_daily_book_summaries_report`、`project_new_computer_setup`
