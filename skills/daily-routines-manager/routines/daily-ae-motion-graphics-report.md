---
trigger_id: trig_016PteoSby2GRxyvYXEHSk3j
name: daily-ae-motion-graphics-report
cron: "0 0 * * *"  # 08:00 台北時間（維持每天，2026-08-12 確認不變）
enabled: true
output: Gmail（siming1221@gmail.com），Word 風格 HTML 表格；來源平台限縮為不需登入公開平台（2026-07-26修復連結打不開問題）；2026-08-12 防重複機制由查 Gmail 改為 git log（分支 duoli-log-ae）；2026-08-12 寄送改用 Duoli Mailer Worker（curl POST，不再用 Zapier）
environment_id: env_012PXqxpqYN4yzPvZoiGdmLf（共用 env，2026-08-14 確認 $DUOLI_WEBHOOK_TOKEN 已在此環境設好，不需切到獨立 Duoli Mailer 環境）
mcp_connections: [Zapier]（僅為 API 限制殘留，見下方「已知限制」，allowed_tools 已不含任何 mcp__Zapier__ 工具，功能上無法被呼叫）
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch]
sources: [{git_repository: {url: "https://github.com/CharlesWang1221/claude-code-setup"}}]
---

## Prompt

你是一個自動化助手，任務是每天執行一次「AE Motion Graphics 影片分析報告」。這是雲端獨立執行的任務，需要存取 git repo（讀寫防重複 log 檔用），但不修改 repo 裡除了指定 log 檔以外的任何檔案。

影片選項條件（重要，必須遵守）：
- 內容主題限定在：科技、AI、UI/UX、雲端（Cloud）這四大方向。
- 影片類型必須是「廣告宣傳影片」（例如品牌/產品發佈宣傳、企業形象宣傳、產品功能宣傳短片等，以商業宣傳為目的使用 After Effects Motion Graphics 製作的影片）。
- 絕對不要選「教學影片」（包含 AE 教學、How-to、Tutorial、Course 等教學性質內容），若搜尋結果看起來像教學影片就跳過。
- 影片來源限定在「不需登入、公開即可直接觀看」的平台，只用以下來源：YouTube、Vimeo、Bilibili、Behance、Dribbble、品牌/代理商官網發佈的宣傳影片頁面。**明確排除**：Facebook、Instagram/Reels、TikTok、LinkedIn、Twitter(X)——這些平台常規定需要登入才能完整觀看、或有地區鎖/流量限制，這是之前連結打不開的主要原因，不要再選這些平台的內容。

影片連結要求（重要）：
- 每一支影片的連結都必須是可以直接點進去觀看那支具體影片的網址（例如 YouTube 影片頁面、Vimeo 具體影片頁、Behance 專案頁面等），不能是搜尋結果頁、頻道首頁、標題頁面或任何不能直接播放/觀看該影片的連結。
- 寄信前要確認這 3 個連結都是有效且不需登入即可點擊直接觀看的，不要放失效、不確定、或需登入/有地區限制提示的連結。
- 3 支影片必須是彼此完全不同的內容（不同品牌/產品/創作者），不能是同一支影片的不同版本/剪輯版本，也不能是同一創作者/同一作品集系列裡非常相似的作品，要確定 3 支在內容與主題上有明確差別。

防止跨天重複（改用 repo log，不再查 Gmail，不吃 Zapier 額度）：
- 先用 Bash 執行：
```
git fetch origin
git checkout duoli-log-ae 2>/dev/null || git checkout -b duoli-log-ae origin/main
git pull origin duoli-log-ae --ff-only 2>/dev/null || true
```
- 讀取 `skills/daily-routines-manager/sent-log/ae-motion-graphics.md`（若檔案不存在，視為空清單，正常繼續選片，不用備註略過比對）。這份 log 記錄過去約 14 天內已推薦過的影片，格式為每天一個 `## YYYY-MM-DD` 區塊，底下列出當天已用過的影片（標題＋連結）。整理出「已用過清單」。
- 本次選片時必須排除「已用過清單」裡的所有影片：不能選同一支影片，也不能選同一創作者/同一系列的極相似作品。
- 如果搜尋到的候選影片與「已用過清單」撞了，必須換一支，不能因為找不到新影片就照樣選用近期已經推薦過的內容。

執行步驟：
1. 依上方「防止跨天重複」的做法，先取得「已用過清單」。
2. 用網路搜尋工具（WebSearch/WebFetch）在上述限定的公開平台中，找出符合選項條件、且不在「已用過清單」裡的、近期最新、最熱門的 3 支廣告宣傳影片。優先挑選近期發佈、話題度高、技術含量高、主題符合科技/AI/UIUX/雲端的作品，並跨越單一平台。
3. 針對這 3 支影片，整理以下資訊：影片標題、影片連結（需可直接觀看，見上方連結要求）、來源平台、所屬主題、特色分析、技術分析。

報告格式（重要）：
- 信件必須用 body_type: "html"，呈現形式要像 Microsoft Word 裡面插入的表格一樣整齊、專業、有商務感，不要簡陋的黑白邊框。
- 結構上用一個 HTML <table style="border-collapse:collapse;width:100%;font-family:Calibri,Arial,sans-serif;font-size:14px;">，每個 <th> 和 <td> 都設 style="border:1px solid #999;padding:8px 10px;text-align:left;vertical-align:top;"。
- 標題行（<th>）背景要有題色區分，例如 style="background-color:#4472C4;color:#ffffff;font-weight:bold;"（像 Word 預設藍色表格樣式），標題列依序為：影片標題 | 來源平台 | 主題 | 連結 | 特色分析 | 技術分析。
- 內容行（<tr>）可以一行白一行淡灰（例如 background-color:#F2F2F2）交替，像 Word 的 banded rows。
- 連結那一格用 <a href="..." style="color:#4472C4;">觀看影片</a> 做成可點擊連結，必須是上面要求的可直接觀看連結，不能是搜尋頁或頻道頁。
- 共 3 支內容彼此不同、且不在「已用過清單」裡的影片，每支一行（<tr>）。
- 表格上方加一行標題文字，例如 <h3>【AE Motion Graphics 廣告影片分析報告】{今天日期}</h3>。

4. 寄送（改用 Duoli Mailer Worker，禁止使用 Zapier 或任何其他管道）
   1. 用 Write 工具把步驟3產生的完整 HTML 表格內容，原封不動寫進暫存檔 `/tmp/duoli-ae-motion-graphics-body.html`。
   2. 用 Bash/Node.js 讀出暫存檔內容，組成 JSON payload：`{"to":"siming1221@gmail.com","subject":"多利｜每日 AE Motion Graphics 廣告影片分析報告 - {今天日期}","html":"..."}`（html 欄位放暫存檔的完整內容），寫進 `/tmp/duoli-ae-motion-graphics-payload.json`。組 JSON 務必用程式（例如 Node.js `JSON.stringify`）處理，不要手動拼字串，避免 HTML 裡的引號/換行破壞 JSON 格式。subject 必須以「多利｜」開頭。
   3. 用 Bash 執行：
```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: daily-ae-motion-graphics-report-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/duoli-ae-motion-graphics-payload.json
```
   4. 只有 curl 回應成功（HTTP 2xx）才算寄信完成，才能繼續下一步的 log 更新。若失敗（非 2xx、連線錯誤、或環境變數 `$DUOLI_WEBHOOK_TOKEN` 未設定）：直接回報「寄信失敗」＋實際錯誤訊息，**絕對不要改用 Zapier、Gmail 或任何其他方式寄送**，也不要繼續執行下一步的 log 更新（避免沒寄出卻誤標記已寄送）。

5. 更新 log 並 commit（寄信成功後才做這一步，這一步只寫這一個 log 檔，不要動 repo 裡其他任何檔案，也不要碰 main 分支）：
   - 用 Bash 把這次實際選用的 3 支影片（標題＋連結）append 進 `skills/daily-routines-manager/sent-log/ae-motion-graphics.md`：在檔案最上方新增一個 `## {今天日期 YYYY-MM-DD}` 區塊，列出這 3 支影片（每支一行 `- {標題} — {連結}`）。順手刪掉超過 30 天以前的舊區塊，避免檔案無限長大。
   - 完成後執行：
```
git add skills/daily-routines-manager/sent-log/ae-motion-graphics.md
git commit -m "多利日誌 daily-ae-motion-graphics-report {今天日期}"
git push origin duoli-log-ae
```

注意：
- 如果找不到 3 支完全符合條件（主題+廣告性質+非教學+公開不需登入可直接觀看連結+彼此內容不同+不在已用過清單）的影片，盡量找最接近的，並在表格下方註明實際找到的數量、原因，以及是否有因為避免重複而放寬標準。
- 必須確定找到的影片不是教學/教學性質影片，若不確定就換一支。
- 只從 YouTube、Vimeo、Bilibili、Behance、Dribbble、品牌官網這些公開不需登入的平台尋找，盡量跨平台，不一定都來自同一平台。絕對不要因為找不到合適影片就放寬到 Facebook/Instagram/TikTok 這些需登入的平台。
- 每次執行都必須完成寄信這個步驟，不要只做分析不寄信。整個執行過程應該很快，若發現自己在重試某個失敗的操作超過 2-3 次，直接放棄並繼續下一步，不要卡住。步驟5的log更新若失敗（例如push衝突），不要因此卡住或重試超過1次，寄信才是主要任務，log更新失敗只需在下次執行時自然補上。
