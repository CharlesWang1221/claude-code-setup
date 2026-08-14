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

1. 建立 Resend 帳號，驗證寄件網域或單一寄件地址（目前用 Resend 的共用測試網域 `onboarding@resend.dev`，這個身分**只能寄給 Resend 帳號註冊信箱本人**，如果之後要 CC 給非帳號本人的地址，必須先在 Resend 完成自訂網域驗證，否則 Resend API 會拒收）。
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
- **診斷順序建議**：先去 `resend.com/emails` 看有沒有寄送嘗試記錄（這個帳號的 Cloudflare Workers Logs 功能沒開，過去查全部回空，別浪費時間查那邊）；再去 claude.ai/code/routines/{trigger_id} 點最新一次 run 的 session，看 agent 自己回報的錯誤訊息，通常會直接講清楚卡在哪一層。
- 不要把報告、token 或 Resend key 寫入 repo。這個 repo 是公開的。

## 已知次要問題（2026-08-14 發現，不影響寄信本身）

寄信成功後，routine 的第 5 步（把選用內容寫進 `sent-log/*.md` 並 `git push` 到 `duoli-log-*` 分支）在 cloud session 裡會被 GitHub 拒絕，回 403（`git push` 對 `https://github.com/CharlesWang1221/claude-code-setup/` 存取被拒）。本機用個人帳號 push 完全正常（`push:true`、`admin:true`），代表這不是 repo 權限問題，比較像是 claude.ai 連接 GitHub 的那個 App（Settings → Applications → Installed GitHub Apps → Claude）在這個 repo 上被裝成唯讀權限。待確認：去 GitHub 網頁檢查該 App 對這個 repo 的權限設定，改成允許寫入。這個問題不影響寄信這個主任務，只影響防重複 log 沒被記錄，下次執行會自然重試。
