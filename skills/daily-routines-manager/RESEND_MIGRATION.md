# 多利寄信移除 Zapier：Resend outbox

## 做法

Claude cloud routine 仍負責搜尋與寫報告，但不再呼叫 Zapier。它把報告直接 POST 給 Cloudflare Worker（`duoli-mailer`），Worker 再以 Resend 寄到 Gmail。

這把「內容生成」與「寄送」切開，Zapier 額度歸零後寄信仍可運作。報告內容不寫入這個公開 repo。

**現況（2026-08-14 確認）：已上線且驗證成功**，7 支寄信 routine（不含「影片分析每日推薦」，它直接寫 repo 不寄信）全部改用這條路，Worker 已部署、secrets 已設定、claude.ai 端環境已切好。

## 架構三個關鍵位置（缺一個都會寄不出信）

1. **Cloudflare Worker**（`tools/duoli-mailer-worker/`，worker 名稱 `duoli-mailer`，網址 `https://duoli-mailer.siming1221.workers.dev`）：驗證 Authorization token、收件人白名單（`siming1221@gmail.com`，cc 只能是 `debra.hdf@gmail.com`）、主旨必須以「多利｜」開頭，通過才呼叫 Resend API 寄信。Secrets（`RESEND_API_KEY`、`RESEND_FROM`、`DUOLI_WEBHOOK_TOKEN`）用 `npx wrangler secret put <NAME>` 設定，只能覆寫不能讀出。
2. **claude.ai 上一個叫「Duoli Mailer」的獨立 Cloud environment**：跟系統預設的「Default」環境是分開的兩個東西。這個環境的 Environment variables 裡設了 `DUOLI_WEBHOOK_TOKEN`（明碼可見，claude.ai 環境變數本質上不是保密機制，只是給 routine 執行時用的一般變數），Network access 設成「Custom」，白名單只加了 `duoli-mailer.siming1221.workers.dev` 一個網域。
3. **每支寄信 routine 本身的「Cloud environment」欄位**：必須在 claude.ai 網頁 routine 的 Edit 對話框裡手動選成「Duoli Mailer」，不能停在系統預設的「Default」。這個欄位目前透過 `RemoteTrigger update` API 改不到，只能在網頁上手動切。**新增寄信類排程時最容易漏掉這一步。**

## 一次性設定（給下一次要重建或換帳號時參考）

1. 建立 Resend 帳號，驗證寄件網域或單一寄件地址。**已完成**：`mail.beyond-ans.com`（不標準答案網站網域的子網域）已在 Resend 驗證通過，`RESEND_FROM` 設為 `多利 <duoli@mail.beyond-ans.com>`（`tools/duoli-mailer-worker/wrangler.toml`）。2026-08-14 之前誤用共用測試網域 `onboarding@resend.dev`，這個身分只能寄給 Resend 帳號註冊信箱本人，CC 給非本人地址（例如阿分）會被 Resend 直接 403 拒收整封信——這是造成 5 支有 CC 的排程「遷移後從未真正寄出過」的第二個隱藏根因（第一個是環境沒切、第三個是 to/cc 格式），已改用驗證網域徹底解決，不用再管這個限制。
2. 在 Cloudflare Worker 建立 `duoli-mailer`，部署 `tools/duoli-mailer-worker`（`cd tools/duoli-mailer-worker && npx wrangler deploy`）。設定三個 secret：`RESEND_API_KEY`、`RESEND_FROM`、`DUOLI_WEBHOOK_TOKEN`。
3. 在 claude.ai 建立（或編輯）一個叫「Duoli Mailer」的 Cloud environment：Environment variables 填 `DUOLI_WEBHOOK_TOKEN=<跟 Worker secret 完全一樣的值>`；Network access 選「Custom」，Allowed domains 只填 `duoli-mailer.siming1221.workers.dev`（不用擔心影響 git push/pull，claude.ai 官方文件說 git 憑證走獨立的安全 proxy，不受這層網路政策管）。
4. 每支寄信 routine：Edit → Cloud environment 下拉選單切成「Duoli Mailer」→ Save。同時確認 allowed_tools 有 `Bash`、`Read`、`Write`、`Edit`、`Glob`、`Grep`、`WebSearch`、`WebFetch`，不含任何 `mcp__Zapier__*` 工具。
5. 把原本「寄送」步驟改成下方 outbox 步驟，再用 `RemoteTrigger run` 各測 1 次，**並且真的去 Resend 後台（resend.com/emails）或收件信箱確認收到，不能只看 curl 回應**。

## 每個 routine 的 outbox 步驟

完整 HTML 報告生成後，直接 POST。

```bash
curl --fail-with-body -sS -X POST https://duoli-mailer.siming1221.workers.dev \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: {routine-name}-$(TZ=Asia/Taipei date +%F)" \
  --data @/tmp/{routine-name}-payload.json
```

`{routine-name}-payload.json` 格式為 `{"to":"siming1221@gmail.com","cc":"debra.hdf@gmail.com","subject":"多利｜主旨","html":"完整 HTML"}`（`to`/`cc` 目前 Worker 已改成字串或陣列格式都吃，寫哪種都可以）。有 CC 的 routine 才填入 `cc`。寄送成功後刪除本機暫存檔。

Worker 會在伺服器端拒絕其他收件人、沒有 `多利｜` 開頭的主旨、非 JSON 或超過 500 KB 的報告。即使 routine 被 prompt injection，不能拿這條路寄給第三人。

## 驗收與故障判斷

- Worker 回傳 HTTP 200，才算寄送成功。
- Worker 回傳 401：`DUOLI_WEBHOOK_TOKEN` 不一致。先確認 claude.ai「Duoli Mailer」環境變數裡的值跟 Worker secret 是不是同一組，不一致就用 `npx wrangler secret put DUOLI_WEBHOOK_TOKEN` 把 Worker 端改成跟 claude.ai 環境變數一樣（claude.ai 環境變數是明碼可查，Worker secret 是唯寫，只能改 Worker 端去對齊 claude.ai，不能反過來）。
- curl 回傳 `403 CONNECT tunnel failed`（不是 Worker 回的，是連線本身被擋）：這支 routine 的 Cloud environment 沒切到「Duoli Mailer」，或「Duoli Mailer」環境的 Network access 白名單裡沒有 `duoli-mailer.siming1221.workers.dev`。
- 環境變數 `$DUOLI_WEBHOOK_TOKEN` 展開後是空字串：這支 routine 的 Cloud environment 還停在「Default」，沒切過去。
- Worker 回傳 400「Missing to, subject, or html」：檢查 `to`/`subject`/`html` 格式，`to`/`cc` 只能是白名單裡的信箱（`siming1221@gmail.com` / `debra.hdf@gmail.com`），subject 必須以「多利｜」開頭。
- Worker 回傳 5xx 或 Resend 的驗證錯誤：去 Cloudflare／Resend 後台確認 `RESEND_API_KEY`、`RESEND_FROM`、網域驗證狀態。
- Resend 回傳 403「You can only send testing emails to your own email address」：`RESEND_FROM` 還在用共用測試網域（`onboarding@resend.dev`），這個身分只能寄給 Resend 帳號註冊信箱本人，一旦 payload 有 `cc` 給非本人地址就會整封被拒收。目前已改用已驗證網域 `mail.beyond-ans.com`（`多利 <duoli@mail.beyond-ans.com>`），CC 已可正常寄送；若之後又改回或換掉 `RESEND_FROM`，記得確認寄件網域仍是已驗證狀態。
- **診斷順序建議**：先去 `resend.com/emails` 看有沒有寄送嘗試記錄（這個帳號的 Cloudflare Workers Logs 功能沒開，過去查全部回空，別浪費時間查那邊）；再去 claude.ai/code/routines/{trigger_id} 點最新一次 run 的 session，看 agent 自己回報的錯誤訊息，通常會直接講清楚卡在哪一層。
- 不要把報告、token 或 Resend key 寫入 repo。這個 repo 是公開的。

## 防重複 log 已改用 Cloudflare KV，不再用 git（2026-08-14 實作完成）

**背景**：寄信成功後 routine 原本要把選用內容 `git commit` + `git push` 到 `duoli-log-*` 分支，但 cloud session 的 `git push` 一律回 403。**根因不是 GitHub 權限**（這個帳號的 `github.com/settings/installations` 裡沒有裝任何 Claude/Anthropic 的 GitHub App，本機用個人帳號 push 也完全正常），而是 claude.ai 平台本身的限制，寫在官方文件 `code.claude.com/docs/en/cloud-environments`「GitHub proxy」段落：「Push protection: git push works only against the session's current working branch」——cloud session 的 git push 只能推回這個 session 自己當初被指派的分支（例如自動產生的 `claude/xxx`），routine 裡 `git checkout -b duoli-log-ae` 之後想推這個自訂分支，一定會被 proxy 擋掉，跟 GitHub 端任何權限設定無關。這是所有 8 支排程共同的結構性限制，不是能修的 bug，只能換掉存法。

**做法**：`tools/duoli-mailer-worker/src/index.js` 加了 `/log/{key}` 端點，掛在同一個 Duoli Mailer Worker 上（同網址、同 `DUOLI_WEBHOOK_TOKEN` 驗證），用 Cloudflare KV（namespace `duoli-log`，binding `DUOLI_LOG`）存防重複清單，完全不碰 git：

- `GET /log/{key}` — 讀出既有 log 全文（純文字，找不到回空字串，不是 404）
- `PUT` 或 `POST /log/{key}` — 用 request body 整份覆寫 log 全文（上限 200KB）

`{key}` 只能是 `LOG_KEYS` 陣列裡的固定字串（防止任意 KV 寫入），目前有：`ae-motion-graphics`、`uiux-articles`、`news-digest`、`ai-startup-cases`、`book-summaries`、`podcast-direction`、`competitor-monitor`。新增寄信排程時要先把新 key 加進這個陣列並 `npx wrangler deploy`，否則會回 404「Unknown log key」。

**routine 端的新流程**（取代原本的 git fetch/checkout/pull + Read，以及 git add/commit/push）：
```bash
# 讀「已用過清單」（寄信前）
curl -sS https://duoli-mailer.siming1221.workers.dev/log/{key} \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" -o /tmp/duoli-{key}-log.md

# 寫回更新後的 log（寄信成功後）
curl -sS -X PUT https://duoli-mailer.siming1221.workers.dev/log/{key} \
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \
  --data-binary @/tmp/duoli-{key}-log-new.md
```
log 檔案格式維持原本的 `## YYYY-MM-DD` 區塊＋條列，routine 自己負責在寫回前砍掉過舊的區塊（14 或 30 天，各 routine 不同）。7 支寄信 routine 的 prompt 已於 2026-08-14 全部改成這個流程，`sources.git_repository` 保留但這一步已經不會再用到 git。

**已知殘留**：「影片分析每日推薦」的每日報告本體（不是防重複 log，是主要產出）仍是寫進 git 的「影片分析」分支，同樣會撞到這個 push 限制，還沒處理——它跟 KV 的關係不大，因為它的內容本來就要被看到（不是防重複用的內部清單），改法可能是也走 KV 存內容、或改成也用 Duoli Mailer 寄信，待評估。
