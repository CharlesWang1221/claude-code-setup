# 每日排程清單（多利管理）

這份清單是 [claude.ai routines](https://claude.ai/code/routines)（cloud agent 排程）的 git 備份存檔，方便版本追蹤、換電腦還原、審閱異動。**即時狀態一律以 `RemoteTrigger list` 查到的線上結果為準**，這裡的檔案在每次異動後由「多利」skill 同步更新。

最後同步時間：2026-08-12（多利：daily-ae-motion-graphics-report、daily-uiux-articles-report 兩支已改用 Duoli Mailer Worker 寄信、environment 換成 Duoli Mailer、allowed_tools 移除 Zapier；其餘 routine 尚待套用，遷移步驟見 `../RESEND_MIGRATION.md`。已知限制：RemoteTrigger update 對 mcp_connections 傳空陣列/null 不會清空既有連結，只能整批替換成非空陣列，這兩支目前 mcp_connections 仍列著 Zapier，但因 allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上不可能被呼叫。）

| 檔案 | routine 名稱 | trigger_id | 頻率 | 輸出方式 |
|---|---|---|---|---|
| video-analysis-daily.md | 影片分析每日推薦 | trig_01WoF3zy2i2AVHdhBSHhtQa6 | 每天 08:00 台北 | 寫入 repo「影片分析」分支（不吃 Zapier） |
| daily-ae-motion-graphics-report.md | daily-ae-motion-graphics-report | trig_016PteoSby2GRxyvYXEHSk3j | 每天 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；防重複用 git log；2026-08-12 已移除 Zapier |
| daily-news-digest-15.md | daily-news-digest-15（每週重要新聞報告） | trig_016qGJ7RpkNm7G4kqFhVvkg5 | 每週一 08:00 台北 | Gmail（siming1221@gmail.com） |
| daily-uiux-articles-report.md | daily-uiux-articles-report | trig_01TANUyyqAknfU5sX4kiMNaZ | 每月 1、15 日 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；防重複用 git log；2026-08-12 已移除 Zapier |
| daily-ai-startup-cases-report.md | daily-ai-startup-cases-report（每週AI創業案例報告） | trig_01ER4FFu49McBY8zC9gaRqUU | 每週三 08:00 台北 | Gmail（siming1221@gmail.com，CC 阿分） |
| daily-book-summaries-3.md | daily-book-summaries-3（每週5本書籍摘要） | trig_01Jo3jNh1ckmveuGTN6V6HZ2 | 每週四 08:00 台北 | Gmail（siming1221@gmail.com） |
| daily-podcast-direction-inspiration-report.md | daily-podcast-direction-inspiration-report | trig_01Xz9H5H9AZm2RD4bYCNAB3v | 每週一 08:00 台北 | Gmail（siming1221@gmail.com，CC 阿分） |
| daily-competitor-monitor-7.md | daily-competitor-monitor-7（雙週競品動態監控） | trig_01HaRbUMGiddyezfGpoq1FFS | 雙週週五 08:00 台北（每月第1、3週的週五，cron無雙週語法，非精準隔14天） | Gmail（siming1221@gmail.com，CC 阿分） |

## 共用設定（新增 routine 時套用）

- environment_id: `env_012PXqxpqYN4yzPvZoiGdmLf`
- model: `claude-sonnet-5`
- 08:00 台北時間 = cron `0 0 * * *`（UTC）
- Zapier 已無額度時，寄信類 routine 改走 Cloudflare Worker + Resend。完整設定與 prompt 替換內容見 `../RESEND_MIGRATION.md`。
- 預設收件人：siming1221@gmail.com
- 樣板規則見「多利」skill 本體（`../SKILL.md`）
