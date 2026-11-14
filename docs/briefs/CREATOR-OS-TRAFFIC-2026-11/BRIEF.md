---
task_id: CREATOR-OS-TRAFFIC-2026-11
status: ACTIVE
owner: 廠長（工作站實作，Codex 執行）＋成析（資料口徑）；規則由 Claude Code 管理層維護
created_at: 2026-11-13 Asia/Taipei
last_updated: 2026-11-13 21:00 Asia/Taipei
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

## Mac Claude 查證與改版（2026-11-13 晚，老查核准「按你建議執行」）

**本節取代下方「給 Mac 的 Claude Code」第一件事與「Mac 部署前必看」第 1 至 3 點。** 那兩段的前提（線上有新版主頁原始碼）已查證不成立。

### 查證結果

- 從 Cloudflare 讀回線上 `creator-os` Worker 程式：`GET /` 只回「驗證成功」靜態頁（文字要使用者回本機 `localhost:3000`）；沒有使用 `ASSETS`，非 `/v1/*` 一律 404。**線上從來沒有部署過前端**，沒有 `output: "export"` 是正常的。
- 線上 Worker 與 `main` 的 `worker/src/index.ts` 同版（含 LINE、Mac Worker 佇列、Drive 備份）。重新部署 Worker 不會退版。
- 「讀取雲端」前端從未進 git（全部分支、歷史、stash 都查過），Mac 硬碟與 Drive 也沒有。「核准」是 LINE 指令，不是網頁按鈕。此事不擋本卡，另由老查決定要不要追。

### 改版內容（分支 `feat/creator-os-traffic`，commit `e632af5`）

- `next.config.ts` 加 `output: "export"`，build 產出 `./out`。
- Worker 新增 `isPublicAsset` 白名單：只把 `/traffic`、`/traffic.html`、`/traffic.txt`、`/traffic/*`、`/_next/*`、`/favicon.ico` 交給 `ASSETS`。`/` 仍回驗證頁，另加「開啟總流量」連結。
- `out/index.html` 是 localStorage 舊 MVP，**不得對外**；白名單已擋住，不要放寬。
- `wrangler.jsonc.example` 的 `run_worker_first` 改為 `true`（全部先進 Worker，由白名單決定）。
- Mac 驗證：`npm run lint`、`npx tsc --noEmit`（含 Worker）、`npm run build` 通過，路由 `/`、`/_not-found`、`/traffic`。

### Mac Codex 部署步驟（取代原待辦順序）

1. `git switch feat/creator-os-traffic && git pull --ff-only`，跑來源檢查取得 PASS。
2. `apps/creator-os/wrangler.jsonc`：Mac 沒有，從 Drive 交接包 `wrangler設定_PC副本/` 複製，**只改一處** `assets.run_worker_first` 為 `true`，其餘（database_id、vars）照 PC 副本；不提交。
3. `npm ci` → `npm run lint` → `npm run build`，確認 `out/traffic.html` 存在。
4. `wrangler d1 migrations list` 確認線上已有 0005、0006；套 0007；再讀回一次。
5. `wrangler deploy`。部署前先 `wrangler deploy --dry-run` 確認 assets 目錄是 `./out`。
6. 線上讀回：`/` 是驗證頁且有總流量連結；`/traffic` 有頁面；`/index.html` **必須不是**舊 MVP（應為 404）；無痕視窗被 Access 擋。
7. 匯入 Drive 的 S4EP3、S4EP4 CSV（先預覽再寫入），線上截圖回報。
8. 驗收通過後由 Claude 併入 `main`。

## Mac 交接（2026-11-13 老查指定，今晚在 Mac 執行）

- 交接包放在老查 Google Drive：`我的雲端硬碟/節目-不標準答案/暫存/流量管理/`（Mac 依 Drive 掛載點找，通常在 `~/Library/CloudStorage/GoogleDrive-*/`，不寫死路徑）。
- 先讀 `00_先讀_Mac交接_2026-11-13.md`；給 Codex 的指令是 `01_貼給Mac_Codex的指令.txt`（2026-11-13 下午改版：程式已寫好，Codex 只做確認、部署、填數字、讀回）。
- `wrangler設定_PC副本/` 是 PC 上的 `wrangler.jsonc`、`wrangler.line.jsonc`（含 D1 database_id，不進 repo）。Mac 已有就先比對 database_id，不同即停；沒有才複製。

### 給 Mac 的 Claude Code（已過時，見「Mac Claude 查證與改版」）

- 現況：程式在分支 `feat/creator-os-traffic`（`f0a5bc9`），PC 已過 lint、tsc、build；尚未套 0007、未部署、未填數字。
- Claude 的角色：管理與驗收，不重寫功能。部署、填數字由 Mac Codex 依 Drive 的 `01` 指令執行。
- Claude 第一件事：在 Mac repo 跑 `git status`，確認 `apps/creator-os/src/app/page.tsx`、`next.config.ts` 有沒有未提交的線上版（有「讀取雲端」「核准」、`output: "export"`）。這是部署成敗的關鍵，結果先告訴老查。
  - 有：請 Codex 先 commit 到分支再部署。
  - 沒有：停下來，跟老查確認線上版原始碼在哪；不得用 repo 的舊 MVP 部署。
- 驗收 Codex 回報時看四件事：線上 `/traffic` 有 S4EP3、S4EP4 數字；主頁沒退回舊版；無痕視窗仍被 Access 擋；沒有跨平台加總的大數字。通過後確認分支已併入 main、任務卡「實測結果」與總表已更新。

## PC／Mac 拆工（2026-11-13 老查要求白天先在 PC 推進）

PC 已有 `node_modules`（含 `next/dist/docs`），寫程式不需要安裝。拆法如下，取代待辦 1「實作在 Mac」的限制；`npm install`、`wrangler` 仍只在 Mac 跑。

- **PC 現在做**（Codex，單一執行線，不開子代理；唯讀盤點卡住兩次就是並行探查拖垮的，直接開工）：
  - 待辦 2 至 6 的程式：`0007` migration、Worker API、「總流量」頁、CSV 範本。
  - 可跑 `npm run lint`、`npm run build`（只用既有 `node_modules`，不得 `npm install`／`npm ci`）。缺套件就停，留給 Mac。
  - 開分支 `feat/creator-os-traffic` commit 並 push，不併入 main。
  - Firstory 匯出實測：瀏覽器登入後台只看不改，結果寫回本卡「實測結果」。
  - S4EP3、S4EP4 各平台 D1／D7／D30 數字：後台唯讀抄錄，存到 Drive 交接包 `流量管理/` 的 CSV（照範本欄位），不進 repo。
- **Mac 今晚做**：拉分支 → `npm ci` → lint／build → 確認線上 D1 已有 0005、0006 → 套 0007 並讀回 `migrations list` → 部署 → 匯入 Drive 那份 CSV → 線上讀回截圖 → 併入 main。

## PC 實作結果（2026-11-13，Claude 依老查「換你寫」代寫）

PC Codex 的寫檔工具壞了（`TextEncoder is not defined`），老查改指派 Claude 寫程式，已記 `docs/RULE_CHANGELOG.md`。程式在分支 `feat/creator-os-traffic`，未併 main。

- 新增：`database/migrations/0007_traffic_metrics.sql`、`src/lib/traffic.ts`（平台、觀察窗、CSV 解析與驗證，Worker 與前端共用）、`src/lib/traffic-api.ts`、`src/app/traffic/`（頁面）、`docs/traffic-csv-template.csv`；修改 `worker/src/index.ts`（`GET /v1/traffic`、`POST /v1/traffic`、`POST /v1/traffic/import` 帶 `mode=preview|commit`）。
- PC 驗證：`npm run lint`、`npx tsc --noEmit`（含 Worker）、`npm run build` 都通過，路由出現 `/traffic`；CSV 解析用 6 種情況實測；migration 與覆寫語句用 Node 內建 SQLite 實跑通過。
- 與待辦的兩個差異（Claude 裁定）：
  - **不設外鍵接 `content_items`／`publications`**。`POST /v1/state` 每次儲存都整批刪除再重建 `content_items`，設外鍵會讓成效資料跟著被刪或斷開。改用 `episode`（例 S4EP3）＋`content_label`（空白代表集數本身）當識別，`content_item_id` 只留欄位、不設約束。
  - **總流量做成獨立網址 `/traffic`，沒改主頁 `page.tsx`**。原因見下。

### Mac 部署前必看（停止線；第 1 至 3 點已由「Mac Claude 查證與改版」取代）

1. **PC 的 repo 裡沒有線上工作站的前端原始碼。** repo 的 `src/app/page.tsx` 還是 localStorage 版 MVP，沒有「讀取雲端」「核准」；`next.config.ts` 也沒有 `output: "export"`，但線上是從 `./out` 部署。線上版原始碼推測只在 Mac 本機、沒有 commit。
2. Mac 先跑 `git status` 看 `apps/creator-os` 有沒有未提交的 `page.tsx`、`next.config.ts`。有的話，先 commit 到這個分支再 build；**用 repo 現在的 `page.tsx` 直接部署，會把線上工作站退回舊版**，這種情況要停下來回報老查。
3. 確認線上版原始碼後，在主頁側欄加一個連到 `/traffic` 的入口（一行 `<Link href="/traffic">`），這步由 Mac 做，因為主頁原始碼只在 Mac 上。
4. D1：先 `wrangler d1 migrations list` 確認線上已有 0005、0006，再套 0007，套完再讀回一次。

## 實測結果

- 2026-11-13 PC Codex 實測 Firstory：「成效總覽」可下載 CSV，欄位為 `date, uniqueStarts, videoUniqueStarts, spotifyStreams, starts, videoStarts, spotifyPlays, spotifyListeners, spotifyFollowers`；頁面標示時區 UTC+0。
- Claude 裁定（口徑，Codex 照做）：
  - 這份匯出是**頻道每日總量，不是單集**，不得拿來填單集的 D1／D7／D30 列。
  - 單集列一律從 Firstory 單集頁手填，CSV 匯入只吃本卡自己的範本格式；本階段不寫 Firstory 專用解析器。
  - 時區：Firstory 的日界是 UTC+0（台北早上 08:00 換日）。手填 D7 時取最接近的完整日，在「備註」寫 `Firstory UTC+0`，不另做換算。
  - 原始匯出檔留在 Drive 當佐證，不進 repo、不進 D1。

## 上線結果（2026-11-13 晚，Mac）

- 已部署：Worker 版本 `7f66de14`（程式），之後老查重設 secret，目前線上是 `f3259fdf`（Secret Change，程式不變）。分支已併入 `main`（`f06bfc0`）。
- D1：0005、0006 原本已套用；0007 已套用，讀回「No migrations to apply」。
- Access：未登入時 `/`、`/traffic`、`/index.html`、`/v1/traffic` 全部 302 轉 Access 登入頁（Claude curl 實測）。`/index.html` 登入後回 Worker 的 404「找不到路徑」，舊 MVP 未對外。
- **既有問題已修**：`OWNER_EMAIL` secret 存在但值為空，雲端工作站自 8 月起從未啟用（D1 工作區 0、成員 0、備份 0）。老查重設 `OWNER_EMAIL`／`EDITOR_EMAIL` 後親自開 `/traffic`，D1 讀回工作區 1、成員 owner＋editor。每日 Drive 備份從今晚起才有機會成功，明早（19:30 UTC 排程）須讀 `backup_runs` 確認。
- Mac Wrangler OAuth 9/4 過期，老查 11-13 重新 `wrangler login`。
- 部署用的 `wrangler.jsonc`（`run_worker_first: true`）在 `~/creator-os-deploy/apps/creator-os/`，保留作為 Mac 部署目錄；`apps/creator-os/.gitignore` 已加入 `wrangler.jsonc`、`wrangler.line.jsonc`。
- `package-lock.json` 已進版控（根目錄 `.gitignore` 例外）。

### 首次 Drive 自動備份（2026-11-14 08:47 查）

- `backup_runs` 只有 1 筆：`failed`，`creator-os_20261114033053.json`，錯誤「Google Drive 授權更新失敗。」（2026-11-14 03:30:53 台北時間）。工作區啟用後的第一次排程，**Creator OS 目前仍沒有任何異地備份**。
- 判斷（高信心，未取得 Google 原始錯誤碼）：refresh token 已失效。依據：`docs/google-drive-backup-setup.md` 要求 consent screen 用「測試使用者」，Google 對 Testing 狀態 App 的 refresh token 只給 7 天；secret 最晚 10-21 設定，早已超過。Worker 丟掉了 Google 回傳的錯誤內容，無法直接證實是 `invalid_grant`。
- 修法（待老查決定，Claude 未改 secret）：
  1. Google Cloud 專案 `Creator OS Backup` 的 OAuth consent screen 改為「In production」。`drive.file` 是非敏感 scope，不需 Google 審查；之後 refresh token 不會 7 天到期。
  2. 用 `tools/google-drive-oauth.mjs` 重新授權取得新 refresh token，老查本人 `npx wrangler secret put GOOGLE_DRIVE_REFRESH_TOKEN`。
  3. 立即驗證：老查登入 `/traffic` 後在瀏覽器主控台跑 `fetch('/v1/backups',{method:'POST'}).then(r=>r.json()).then(console.log)`，或等下一次 03:30 排程；讀回 `backup_runs` 為 `succeeded` 並在 Drive `不標準答案/Creator OS/備份/` 看到檔案才算數。
  4. 建議另修 Worker：把 Google 回傳的 `error` 欄位（如 `invalid_grant`）寫進 `error_message`，下次失敗能直接判斷。

### 完成定義第 3 項：延後

- 今晚無可填數據：S4EP3 於 11-09 公開，D7 要 11-16 才滿；S4EP4 尚未發布。Firstory 頻道 CSV 依裁定不得填單集。
- Codex 用 Chrome 抄數字時多次遇到畫面切換，D1 也沒抄到。
- 新期限：**11-16（一）晚**抄 S4EP3 D1／D7，存成 Drive `流量管理/S4EP3_traffic.csv`（範本格式）後從 `/traffic` 匯入；S4EP4 等發布後第 8 天補 D7。匯入成功並截圖後，本卡才結案。
