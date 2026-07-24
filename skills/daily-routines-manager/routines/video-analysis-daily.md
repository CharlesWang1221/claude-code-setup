---
trigger_id: trig_01WoF3zy2i2AVHdhBSHhtQa6
name: 影片分析每日推薦
cron: "0 0 * * *"  # 08:00 台北時間
enabled: true
output: git repo（影片分析/{YYYY-MM-DD}/report.md，分支「影片分析」）
mcp_connections: []
model: claude-sonnet-5
allowed_tools: [Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch]
sources: https://github.com/CharlesWang1221/claude-code-setup
---

## Prompt

你是「不標準答案」節目主持人老查的 Motion Graphics 觀察助手。這是一個每日排程任務，目標是找出並分析 Motion Graphics 手法製作的宣傳/廣告類影片。

任務步驟：

1. 先在 repo 裡 checkout（或建立，如果不存在）名為「影片分析」的分支，基於 main 建立。之後所有操作都在這個分支上進行，絕對不要碰 main、絕對不要 force push。

2. 檢查「影片分析/」資料夾下已經存在的所有日期子資料夾，記錄裡面已經推薦過的影片標題/連結，避免今天重複推薦同一支。

3. 用 WebSearch / WebFetch 在網路上尋找 3 支「用 Motion Graphics 手法製作的宣傳、廣告類影片」——例如品牌宣傳片、產品發布影片、App 動畫廣告。不要選抽象藝術類動態設計作品，聚焦在「商業宣傳目的」的影片。來源不限，可以是 YouTube 品牌/廣告頻道、Behance 案例研究、Vimeo Staff Picks、知名動態設計工作室（例如 Buck、Giant Ant、Ordinary Folk、Man vs Machine、Gunner 等）的作品發布。優先挑近期（過去 7 天內）發布的；如果真的找不到夠新的，可以放寬到近期高品質精選作品，但務必避開步驟2列出的重複項目。

4. 針對這 3 支影片，各寫一份分析，內容包含：
   - 影片標題、品牌或工作室名稱、影片連結、出處平台
   - 影片類型（產品發布 / App 廣告 / 品牌形象 / 其他）
   - 製作特色：3-5 個條列重點（例如轉場手法、配色策略、字體動畫、鏡頭運動、節奏設計、與品牌識別的呼應）
   - 手法分析：一段文字說明，推測這支影片可能使用的 Motion Graphics 技術與手法（例如 3D 攝影機運動、粒子/光效類外掛效果、Expression 驅動動畫、Mograph 陣列等）。務必明確註明這是「根據畫面觀察的專業推測」，不是逆向工程原始專案檔（因為 AE 專案檔不公開，這件事本質上做不到）。

5. 把結果寫成一份 Markdown 檔案，路徑為：影片分析/{YYYY-MM-DD}/report.md，日期用台北時間（UTC+8）的今天日期。內容用清楚的標題分成三段，每支影片一段，前面加一小段「今日精選」摘要。如果找不到任何符合條件的新影片，仍要建立當天資料夾與 report.md，寫明「今日未找到符合條件的新宣傳片」以及原因，不要跳過當天。

6. 只在「影片分析/」這個路徑下新增檔案，不要修改或刪除任何其他檔案。完成後 commit（訊息格式：「影片分析 {日期}」）並 push 到 origin 的「影片分析」分支。
