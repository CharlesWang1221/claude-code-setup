---
trigger_id: trig_01HaRbUMGiddyezfGpoq1FFS
name: daily-competitor-monitor-7
display_name: 雙週競品動態監控
cron: "0 0 1-7,15-21 * 5"  # 每月第1、3週的週五 08:00 台北時間（cron無雙週語法，非精準隔14天）
enabled: true
output: Duoli Mailer Worker（siming1221@gmail.com，CC debra.hdf@gmail.com 阿分），監控 7 個同賽道創作者（4台灣+3國際）；2026-08-14 防重複機制改用 Duoli Mailer Worker 的 Cloudflare KV（不再用 git）
environment_id: env_012GK45Z6sL8waNgSho7rmSd（Duoli Mailer）
mcp_connections: [Zapier]（僅為 API 限制殘留，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你要產生並寄出「雙週競品動態監控」email。監控對象固定 7 個同賽道 Podcast/創作者（4 個台灣＋3 個國際）：①只能嗝酒的圖書館（Otherwise Library，Ting & Hank 夫妻檔，哲學類）②大人的 Small Talk（姚詩豪+張國洋）③本子在隔壁 Benzi（心理學/腦科學科普）④FarHugs 遠距抱抱（心理健康/個人成長/關係議題）⑤We Can Do Hard Things（Glennon Doyle+Abby Wambach+Amanda Doyle，脆弱揭露+接受不完美人生）⑥Unlocking Us（Brené Brown，shame/vulnerability 研究，「裂縫值得被看見」是金繼哲學的西方學術版）⑦On Purpose with Jay Shetty（心理學背書的生活建議，Netflix/Spotify 獨家約）。

收件人背景：老查與阿分共同主持《不標準答案》Podcast，核心哲學是金繼（裂縫不必被磨平）、物心分離、慢速野獸（反效率文化），三大內容支柱是社會議題深度集、金繼時刻、書喔吾聊。老查正在做 YouTube 擴張。

## 1. 防止跨兩週重複（改用 Duoli Mailer Worker 的 KV log，不寫 git，不吃 Zapier 額度）
先執行：
```bash
curl -sS https://duoli-mailer.siming1221.workers.dev/log/competitor-monitor \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" -o /tmp/duoli-competitor-monitor-log.md
```
（若內容為空，視為空清單）。讀取內容，格式為每次寄送一個 `## YYYY-MM-DD` 區塊、依創作者列出當次已提過的標題，過去約30天內容都算，整理出「近期已提過的集數/內容標題清單」（依創作者分類）。

## 2. 搜尋 7 個對象的最新動態
用 WebSearch（必要時 WebFetch 確認連結有效）查每個創作者最近1-2週內有沒有新集數/新影片/新貼文：有新內容則抓標題、平台連結、內容摘要（3-5句），3個國際對象用英文搜尋但摘要翻成繁體中文，金句可保留一句英文原文附中文翻譯；若近期無新內容或跟已提過清單重複，該創作者欄寫「近期無新動態」。連結必須直接指向該集/貼文本身。額外留意這集/貼文有沒有蹭到近期熱門話題。

## 3. 產生 email 報告
主旨：「雙週競品動態監控 - {今天日期}」。信件最上方 <h2 style="color:#4472C4;">【雙週競品動態監控】{今天日期}</h2>，一個表格（藍底白字標題行 #4472C4，banded rows #F2F2F2），欄位：創作者｜最新動態(標題+連結)｜內容摘要｜跟《不標準答案》的重疊/差異/可借鏡點｜是否蹭熱點。7個創作者各一列，用「🇹🇼」「🌍」區分台灣/國際。「跟不標準答案的重疊/差異/可借鏡點」欄必須具體，不要泛用空話。信件最下方加「🎯 本次觀察」區塊（3-5句），從這7個對象裡挑一個最有參考價值的信號，具體說明為何值得注意、可以怎麼回應；若7個都無新動態就寫「本次7個監控對象皆無新動態」。

## 4. 寄送（改用 Duoli Mailer Worker，禁止使用 Zapier 或任何其他管道）
1. Write 寫 HTML 進 `/tmp/duoli-competitor-monitor-body.html`。
2. Node.js JSON.stringify 組 payload `{"to":"siming1221@gmail.com","cc":"debra.hdf@gmail.com","subject":"多利｜雙週競品動態監控 - {今天日期}","html":"..."}`，寫進 `/tmp/duoli-competitor-monitor-payload.json`。
3. 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-competitor-monitor-7-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-competitor-monitor-payload.json
```
4. 只有 HTTP 2xx 才算寄信完成。失敗就回報「寄信失敗」+錯誤訊息，**絕對不要改用 Zapier**，也不要更新 log。

## 5. 更新 log（寄信成功後才做，只寫這一個 log，跳過「近期無新動態」的創作者不用記錄）
把舊 log 加上這次實際整理出有新動態的創作者與標題、新增 `## {今天日期}` 區塊在最上方（依創作者列每則一行 `- {創作者} — {標題}`），順手刪掉超過30天的舊區塊，寫進 `/tmp/duoli-competitor-monitor-log-new.md`。執行：
```bash
curl -sS -X PUT https://duoli-mailer.siming1221.workers.dev/log/competitor-monitor \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  --data-binary @/tmp/duoli-competitor-monitor-log-new.md
```
若失敗，不要因此卡住或重試超過1次，寄信才是主要任務。
