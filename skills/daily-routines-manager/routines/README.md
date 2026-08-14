# 每日排程清單（多利管理）

這份清單是 [claude.ai routines](https://claude.ai/code/routines)（cloud agent 排程）的 git 備份存檔，方便版本追蹤、換電腦還原、審閱異動。**即時狀態一律以 `RemoteTrigger list` 查到的線上結果為準**，這裡的檔案在每次異動後由「多利」skill 同步更新。

最後同步時間：2026-08-14（多利：找出並修完 Duoli Mailer 寄信全掛的四層根因，7 支寄信 routine 全部改切到獨立的「Duoli Mailer」Cloud environment，`daily-ae-motion-graphics-report` 已實測收到真實報告信。完整故障排除步驟見 `../RESEND_MIGRATION.md`。次要已知問題：寄信成功後 log 分支 `git push` 回 403，懷疑是 claude.ai 連接 GitHub 的 App 在這個 repo 權限被裝成唯讀，待老查去 GitHub 網頁確認。）

| 檔案 | routine 名稱 | trigger_id | 頻率 | 輸出方式 |
|---|---|---|---|---|
| video-analysis-daily.md | 影片分析每日推薦 | trig_01WoF3zy2i2AVHdhBSHhtQa6 | 每天 08:00 台北 | 寫入 repo「影片分析」分支（不寄信，Default 環境） |
| daily-ae-motion-graphics-report.md | daily-ae-motion-graphics-report | trig_016PteoSby2GRxyvYXEHSk3j | 每天 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；防重複用 git log；Cloud environment: Duoli Mailer |
| daily-news-digest-15.md | daily-news-digest-15（每週重要新聞報告） | trig_016qGJ7RpkNm7G4kqFhVvkg5 | 每週一 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；Cloud environment: Duoli Mailer |
| daily-uiux-articles-report.md | daily-uiux-articles-report | trig_01TANUyyqAknfU5sX4kiMNaZ | 每月 1、15 日 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；防重複用 git log；Cloud environment: Duoli Mailer |
| daily-ai-startup-cases-report.md | daily-ai-startup-cases-report（每週AI創業案例報告） | trig_01ER4FFu49McBY8zC9gaRqUU | 每週三 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；Cloud environment: Duoli Mailer |
| daily-book-summaries-3.md | daily-book-summaries-3（每週5本書籍摘要） | trig_01Jo3jNh1ckmveuGTN6V6HZ2 | 每週四 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；Cloud environment: Duoli Mailer |
| daily-podcast-direction-inspiration-report.md | daily-podcast-direction-inspiration-report | trig_01Xz9H5H9AZm2RD4bYCNAB3v | 每週一 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；Cloud environment: Duoli Mailer |
| daily-competitor-monitor-7.md | daily-competitor-monitor-7（雙週競品動態監控） | trig_01HaRbUMGiddyezfGpoq1FFS | 雙週週五 08:00 台北（每月第1、3週的週五，cron無雙週語法，非精準隔14天） | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；Cloud environment: Duoli Mailer |

## 共用設定（新增 routine 時套用）

- environment_id: `env_012PXqxpqYN4yzPvZoiGdmLf`（系統預設「Default」環境，不寄信的排程用這個）
- **會寄信的排程必須改用「Duoli Mailer」環境**（`env_012GK45Z6sL8waNgSho7rmSd`），在 claude.ai 網頁 routine 的 Edit 對話框手動選，`RemoteTrigger update` API 目前改不到這個欄位。漏了這一步 `$DUOLI_WEBHOOK_TOKEN` 會是空的，寄信一定失敗。完整說明見 `../RESEND_MIGRATION.md`。
- model: `claude-sonnet-5`
- 08:00 台北時間 = cron `0 0 * * *`（UTC）
- 寄信類 routine 一律走 Cloudflare Worker（`duoli-mailer`）+ Resend，不用 Zapier。完整設定與故障排除見 `../RESEND_MIGRATION.md`。
- 預設收件人：siming1221@gmail.com
- 樣板規則見「多利」skill 本體（`../SKILL.md`）
