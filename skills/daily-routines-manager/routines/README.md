# 每日排程清單（多利管理）

這份清單是 [claude.ai routines](https://claude.ai/code/routines)（cloud agent 排程）的 git 備份存檔，方便版本追蹤、換電腦還原、審閱異動。**即時狀態一律以 `RemoteTrigger list` 查到的線上結果為準**，這裡的檔案在每次異動後由「多利」skill 同步更新。

最後同步時間：2026-07-24

| 檔案 | routine 名稱 | trigger_id | 時間 | 輸出方式 |
|---|---|---|---|---|
| video-analysis-daily.md | 影片分析每日推薦 | trig_01WoF3zy2i2AVHdhBSHhtQa6 | 08:00 台北 | 寫入 repo「影片分析」分支 |
| daily-ae-motion-graphics-report.md | daily-ae-motion-graphics-report | trig_016PteoSby2GRxyvYXEHSk3j | 08:00 台北 | Gmail（siming1221@gmail.com） |
| daily-news-digest-15.md | daily-news-digest-15 | trig_016qGJ7RpkNm7G4kqFhVvkg5 | 08:00 台北 | Gmail（siming1221@gmail.com） |
| daily-uiux-articles-report.md | daily-uiux-articles-report | trig_01TANUyyqAknfU5sX4kiMNaZ | 08:00 台北 | Gmail（siming1221@gmail.com） |
| daily-ai-startup-cases-report.md | daily-ai-startup-cases-report | trig_01ER4FFu49McBY8zC9gaRqUU | 08:00 台北 | Gmail（siming1221@gmail.com） |
| daily-book-summaries-3.md | daily-book-summaries-3 | trig_01Jo3jNh1ckmveuGTN6V6HZ2 | 08:00 台北 | Gmail（siming1221@gmail.com） |
| daily-podcast-direction-inspiration-report.md | daily-podcast-direction-inspiration-report | trig_01Xz9H5H9AZm2RD4bYCNAB3v | 08:00 台北 | Gmail（siming1221@gmail.com） |

## 共用設定（新增 routine 時套用）

- environment_id: `env_012PXqxpqYN4yzPvZoiGdmLf`
- model: `claude-sonnet-5`
- 08:00 台北時間 = cron `0 0 * * *`（UTC）
- 寄信類 routine 一律走 Zapier MCP：`mcp_connections: [{connector_uuid: "4a34f6a9-553f-4645-939f-708b21535f24", name: "Zapier", url: "https://mcp.zapier.com/api/v1/connect"}]`
- 預設收件人：siming1221@gmail.com
- 樣板規則見「多利」skill 本體（`../SKILL.md`）
