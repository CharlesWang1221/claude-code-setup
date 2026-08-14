# 每日排程清單（多利管理）

這份清單是 [claude.ai routines](https://claude.ai/code/routines)（cloud agent 排程）的 git 備份存檔，方便版本追蹤、換電腦還原、審閱異動。**即時狀態一律以 `RemoteTrigger list` 查到的線上結果為準**，這裡的檔案在每次異動後由「多利」skill 同步更新。

最後同步時間：2026-08-14（多利：找出並修完 Duoli Mailer 寄信全掛的五層根因（to/cc 格式、Cloud environment 沒切、網路白名單、token 不同步、CC 被 Resend 拒收），7 支寄信 routine 全部改切到獨立的「Duoli Mailer」Cloud environment，改用驗證網域 `mail.beyond-ans.com` 寄信，已實測寄信+CC 都成功。同一天把新聞報告、AI創業案例報告、書籍摘要三支從每週改成每天，補上 CC 阿分，新聞報告日期窗口改抓「過去24小時」。**接著發現防重複 log 的 `git push` 一律 403，根因是 claude.ai 平台規定「cloud session 的 git push 只能推回 session 自己的 working branch」，跟 GitHub 權限無關**，於是把 7 支寄信 routine 的防重複 log 機制整個從 git 改成呼叫 Duoli Mailer Worker 新增的 KV 端點（`/log/{key}`，GET 讀、PUT 寫），完全不再用 git，7 支 routine 的 prompt 已同步更新，`sources.git_repository` 保留但不再被防重複這一步用到。「影片分析每日推薦」不寄信、寫入 git 分支才是它的主任務本體，目前仍受同一個 push 限制，還沒處理，見下方待辦。完整設定見 `../RESEND_MIGRATION.md`。

| 檔案 | routine 名稱 | trigger_id | 頻率 | 輸出方式 |
|---|---|---|---|---|
| video-analysis-daily.md | 影片分析每日推薦 | trig_01WoF3zy2i2AVHdhBSHhtQa6 | 每天 08:00 台北 | 寫入 repo「影片分析」分支（不寄信，Default 環境；⚠️ 同樣會撞到 git push 只能推 session working branch 的限制，待處理） |
| daily-ae-motion-graphics-report.md | daily-ae-motion-graphics-report | trig_016PteoSby2GRxyvYXEHSk3j | 每天 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；防重複用 Duoli Mailer 的 KV（`/log/ae-motion-graphics`）；Cloud environment: Duoli Mailer |
| daily-news-digest-15.md | daily-news-digest-15（每日重要新聞報告） | trig_016qGJ7RpkNm7G4kqFhVvkg5 | 每天 08:00 台北（2026-08-14 由每週一改每天） | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；日期窗口過去24小時；防重複用 KV（`/log/news-digest`）；Cloud environment: Duoli Mailer |
| daily-uiux-articles-report.md | daily-uiux-articles-report | trig_01TANUyyqAknfU5sX4kiMNaZ | 每月 1、15 日 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com）；防重複用 KV（`/log/uiux-articles`）；Cloud environment: Duoli Mailer |
| daily-ai-startup-cases-report.md | daily-ai-startup-cases-report（每日AI創業案例報告） | trig_01ER4FFu49McBY8zC9gaRqUU | 每天 08:00 台北（2026-08-14 由每週三改每天） | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；防重複用 KV（`/log/ai-startup-cases`）；Cloud environment: Duoli Mailer |
| daily-book-summaries-3.md | daily-book-summaries-3（每日5本書籍摘要） | trig_01Jo3jNh1ckmveuGTN6V6HZ2 | 每天 08:00 台北（2026-08-14 由每週四改每天） | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；防重複用 KV（`/log/book-summaries`）；Cloud environment: Duoli Mailer |
| daily-podcast-direction-inspiration-report.md | daily-podcast-direction-inspiration-report（每次創作靈感） | trig_01Xz9H5H9AZm2RD4bYCNAB3v | 每天 08:00 台北 | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；防重複用 KV（`/log/podcast-direction`）；Cloud environment: Duoli Mailer |
| daily-competitor-monitor-7.md | daily-competitor-monitor-7（雙週競品動態監控） | trig_01HaRbUMGiddyezfGpoq1FFS | 雙週週五 08:00 台北（每月第1、3週的週五，cron無雙週語法，非精準隔14天） | Duoli Mailer Worker（siming1221@gmail.com，CC 阿分）；防重複用 KV（`/log/competitor-monitor`）；Cloud environment: Duoli Mailer |

## 共用設定（新增 routine 時套用）

- environment_id: `env_012PXqxpqYN4yzPvZoiGdmLf`（系統預設「Default」環境，不寄信的排程用這個）
- **會寄信的排程必須改用「Duoli Mailer」環境**（`env_012GK45Z6sL8waNgSho7rmSd`），在 claude.ai 網頁 routine 的 Edit 對話框手動選，`RemoteTrigger update` API 目前改不到這個欄位。漏了這一步 `$DUOLI_WEBHOOK_TOKEN` 會是空的，寄信一定失敗。
- **防重複 log 一律用 Duoli Mailer Worker 的 KV 端點，不要用 git**：`GET /log/{key}` 讀既有清單、`PUT /log/{key}` 寫回去，`{key}` 只能是 Worker 白名單裡的固定字串（見 `tools/duoli-mailer-worker/src/index.js` 的 `LOG_KEYS`），新增排程要新增 key 就要先加進這個陣列並重新部署 Worker。claude.ai cloud session 的 `git push` 只能推回 session 自己的 working branch，用 git 存防重複 log 一定會 403，這是平台限制，不是能修的 bug。
- model: `claude-sonnet-5`
- 08:00 台北時間 = cron `0 0 * * *`（UTC）
- 寄信類 routine 一律走 Cloudflare Worker（`duoli-mailer`）+ Resend（已用驗證網域 `mail.beyond-ans.com`），不用 Zapier。完整設定與故障排除見 `../RESEND_MIGRATION.md`。
- 預設收件人：siming1221@gmail.com
- 樣板規則見「多利」skill 本體（`../SKILL.md`）

## 待辦

- [ ] 「影片分析每日推薦」寄不寄信無關，但它寫進 repo「影片分析」分支的每日報告本體，一樣會被 cloud session 的 git push 限制擋住，需要想辦法改成別的持久化方式（例如也走 KV，或改成寄信）。
