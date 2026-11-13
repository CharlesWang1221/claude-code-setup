---
task_id: CREATOR-OS-TRAFFIC-2026-11
status: ACTIVE
owner: 廠長（工作站實作，Codex 執行）＋成析（資料口徑）；規則由 Claude Code 管理層維護
created_at: 2026-11-13 Asia/Taipei
last_updated: 2026-11-13 Asia/Taipei
source: 老查 2026-11-13 與 Claude Code 討論：「能把這個改成總流量管理嗎」→「好 開始」
---

# 工作站加「總流量」：第一階段（手填＋CSV 匯入）

## 背景與定案

- 老查問 GA 能不能管全部流量。Claude 判斷不能：GA 只看得到 beyond-ans.com，Podcast 收聽、YouTube、IG、FB、Threads 的數字都在各平台後台。
- 定案：總帳放在工作站 Creator OS（`apps/creator-os`，線上為 `creator-os.siming1221.workers.dev`），GA 或 Cloudflare Web Analytics 只算其中「網站」一欄。
- 分兩階段。**本卡只做第一階段**：手填＋CSV 匯入，先跑 2 至 4 週，確認老查與阿分真的會看哪些數字。第二階段（各平台 API 自動抓）另開卡，本卡不得提前做。

## 完成定義

1. 工作站新增一頁「總流量」，以「集數 × 平台 × 觀察窗」為一列。
2. 每列可手填，也可匯入 CSV；資料寫入 D1，換電腦、換瀏覽器都看得到同一份資料。
3. 用 S4EP3、S4EP4 的真實數字各填一輪，線上讀回正確。
4. `npm run lint`、`npm run build` 通過，部署後線上網址看得到新頁，Cloudflare Access 仍只放行老查與阿分。

## 資料口徑（成析定義，Codex 照做）

- 平台固定 9 個：Firstory、Spotify、Apple Podcasts、YouTube 正片、YouTube Shorts、FB、IG、Threads、網站（beyond-ans.com）。
- 觀察窗固定 3 種：D1、D7、D30（從該平台公開時間起算，Asia/Taipei）。
- 每列欄位：主要數字（播放／下載／觀看，依平台原名）、觸及或曝光、互動數、導流點擊（有才填）、追蹤數變化、來源（手填／CSV）、填寫人、備註。
- **不同平台的主要數字不得相加成單一「總流量」大數字**。Firstory 下載和 IG 觀看不是同一種東西，加起來沒有意義。頁面頂端改為每平台一張小卡，各自顯示 D7 數字與上一集比較。
- 單一內容（某一支句剪）可掛在集數底下，沿用既有 `content_items.parent_id` 與 `publications` 對應，不另建一套 ID。

## Codex 待辦（依序）

0. **前置已解除**：老查 2026-11-13 決定保留 LINE 遠端控制，已由 Claude 提交（`908b3d0`，含 `0005_remote_control.sql`、`0006_line_authorized_users.sql`）。新功能疊在其上，新 migration 一律編號 `0007` 起跳。部署前先確認線上 D1 已套用 0005、0006；沒套用就一起套，套完讀回 `wrangler d1 migrations list`。`wrangler.jsonc` 含 database_id，維持不提交。
1. `git pull --ff-only`，跑來源檢查取得 PASS。實作與部署在 Mac 執行；Windows 是公司電腦，不在上面跑 `npm install` 或 `wrangler`。
2. 讀 `apps/creator-os/AGENTS.md`：這版 Next.js 有破壞性變更，先讀 `node_modules/next/dist/docs/` 對應段落再寫。
3. 新增 D1 migration：成效數據表，外鍵接 `workspaces`，可選接 `content_items`／`publications`；同一內容、同一平台、同一觀察窗不得重複（UNIQUE）。
4. Worker 加 API：列出、新增或更新單列、CSV 批次匯入（匯入前先回傳預覽與錯誤列，確認後才寫入）。沿用現有 Access 身分檢查，viewer 只能讀。
5. 前端加「總流量」頁：平台小卡＋明細表＋手填表單＋CSV 上傳。版面與色碼依根目錄 `DESIGN.md`。現有「復盤沉澱」頁的假數字（27,700 等）不要動，本卡不處理。
6. CSV 範本：放一份 `apps/creator-os/docs/traffic-csv-template.csv`（只放欄位與一列假資料）。Firstory 後台能不能匯出、匯出什麼欄位，先實際登入看，結果寫回本卡「實測結果」；不能匯出就手填，不要硬寫爬蟲。
7. 部署後填入 S4EP3、S4EP4 已有的數字，從線上網址讀回截圖，回報老查。

## 預算與停止線

- 需要省長 S 級卡：Terra，單一 worker，付費點數 0。不得接任何付費 API 或第三方數據服務。
- 本卡不碰平台 API、不存任何平台 token。公開 repo 只放程式、schema 與假資料，真實成效數字只進 D1。
- 部署失敗或 Access 設定被改動，立即停止並回報，不得暫時關掉 Access 來測試。
- 規則問題（口徑、平台清單）回報老查交 Claude 修，不自行改。

## 之後（不在本卡範圍）

- 第一階段跑滿 2 至 4 週，老查確認欄位後，Claude 另開第二階段卡：YouTube Analytics API、Meta Graph API（FB＋IG）、Threads insights、Cloudflare Web Analytics 掛到每日排程自動抓；Podcast 收聽保留手動。
- 屆時一併評估要不要改 `podcast-performance-review`（成析）讓復盤數字直接寫進工作站。

## Mac 交接（2026-11-13 老查指定，今晚在 Mac 執行）

- 交接包放在老查 Google Drive：`我的雲端硬碟/節目-不標準答案/暫存/流量管理/`（Mac 依 Drive 掛載點找，不寫死路徑）。
- 先讀 `00_先讀_Mac交接_2026-11-13.md`；給 Codex 的指令是 `01_貼給Mac_Codex的指令.txt`。
- `wrangler設定_PC副本/` 是 PC 上的 `wrangler.jsonc`、`wrangler.line.jsonc`（含 D1 database_id，不進 repo）。Mac 已有就先比對 database_id，不同即停；沒有才複製。
- Mac 的 Claude Code 接手時：只負責確認上述前置與驗收，實作交 Codex，不自己改 `apps/creator-os` 程式。

## PC／Mac 拆工（2026-11-13 老查要求白天先在 PC 推進）

PC 已有 `node_modules`（含 `next/dist/docs`），寫程式不需要安裝。拆法如下，取代待辦 1「實作在 Mac」的限制；`npm install`、`wrangler` 仍只在 Mac 跑。

- **PC 現在做**（Codex，單一執行線，不開子代理；唯讀盤點卡住兩次就是並行探查拖垮的，直接開工）：
  - 待辦 2 至 6 的程式：`0007` migration、Worker API、「總流量」頁、CSV 範本。
  - 可跑 `npm run lint`、`npm run build`（只用既有 `node_modules`，不得 `npm install`／`npm ci`）。缺套件就停，留給 Mac。
  - 開分支 `feat/creator-os-traffic` commit 並 push，不併入 main。
  - Firstory 匯出實測：瀏覽器登入後台只看不改，結果寫回本卡「實測結果」。
  - S4EP3、S4EP4 各平台 D1／D7／D30 數字：後台唯讀抄錄，存到 Drive 交接包 `流量管理/` 的 CSV（照範本欄位），不進 repo。
- **Mac 今晚做**：拉分支 → `npm ci` → lint／build → 確認線上 D1 已有 0005、0006 → 套 0007 並讀回 `migrations list` → 部署 → 匯入 Drive 那份 CSV → 線上讀回截圖 → 併入 main。

## 實測結果

- 2026-11-13 PC Codex 實測 Firstory：「成效總覽」可下載 CSV，欄位為 `date, uniqueStarts, videoUniqueStarts, spotifyStreams, starts, videoStarts, spotifyPlays, spotifyListeners, spotifyFollowers`；頁面標示時區 UTC+0。
- Claude 裁定（口徑，Codex 照做）：
  - 這份匯出是**頻道每日總量，不是單集**，不得拿來填單集的 D1／D7／D30 列。
  - 單集列一律從 Firstory 單集頁手填，CSV 匯入只吃本卡自己的範本格式；本階段不寫 Firstory 專用解析器。
  - 時區：Firstory 的日界是 UTC+0（台北早上 08:00 換日）。手填 D7 時取最接近的完整日，在「備註」寫 `Firstory UTC+0`，不另做換算。
  - 原始匯出檔留在 Drive 當佐證，不進 repo、不進 D1。
