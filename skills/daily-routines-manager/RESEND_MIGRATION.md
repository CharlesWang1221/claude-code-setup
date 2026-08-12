# 多利寄信移除 Zapier：Resend outbox

## 做法

Claude cloud routine 仍負責搜尋與寫報告，但不再呼叫 Zapier。它把報告直接 POST 給 Cloudflare Worker，Worker 再以 Resend 寄到 Gmail。

這把「內容生成」與「寄送」切開，Zapier 額度歸零後寄信仍可運作。報告內容不寫入這個公開 repo。

## 一次性設定

1. 建立 Resend 帳號，驗證寄件網域或單一寄件地址。
2. 在 Cloudflare Worker 建立 `duoli-mailer`，部署 `tools/duoli-mailer-worker`。設定三個 secret：`RESEND_API_KEY`、`RESEND_FROM`、`DUOLI_WEBHOOK_TOKEN`。`RESEND_FROM` 例如 `多利 <reports@你的網域>`。
3. 將 Worker 網址與 webhook token 只填入 Claude.ai routine 的私密設定；不可寫進 repo、routine Markdown 或公開 commit。
4. 在 Claude.ai 每個寄信 routine 移除 Zapier MCP connection 與 Zapier tools，改加入 `Bash`、`Read`、`Write`、`Edit`、`Glob`、`Grep`。
5. 把原本「寄送」步驟改成下方 outbox 步驟，再用 `RemoteTrigger run` 各測 1 次。

## 每個 routine 的 outbox 步驟

完整 HTML 報告生成後，直接 POST。以下的收件人、主旨、Worker URL、token 均換成當次實際值；URL 與 token 只存在 Claude.ai routine 私密設定。

```bash
curl --fail-with-body --retry 2 --retry-all-errors \\
  -X POST "$DUOLI_MAILER_URL" \\
  -H "Authorization: Bearer $DUOLI_WEBHOOK_TOKEN" \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: {routine-name}-{YYYY-MM-DD}" \\
  --data-binary @report.json
```

`report.json` 格式為 `{"to":["siming1221@gmail.com"],"cc":[],"subject":"主旨","html":"完整 HTML"}`。有 CC 的 routine 才填入 `cc`，例如 `["debra.hdf@gmail.com"]`。寄送成功後立即刪除本機暫存檔。

## 驗收與故障判斷

- Worker 回傳 HTTP 200，才算寄送成功。
- Worker 回傳 401，代表 webhook token 不一致；回傳 5xx 或 Resend 的驗證錯誤，去 Cloudflare／Resend 後台修正 secret 或網域驗證。
- Resend 回傳收件人或網域驗證錯誤，去 Resend 後台完成驗證。
- 不要把報告、token 或 Resend key 寫入 repo。這個 repo 是公開的。

## 目前限制

本機 Claude CLI 已失去登入，無法列出或更新 Claude.ai 的 RemoteTrigger。因此線上 7 個 routine 還要在重新登入 Claude 後依本文件套用並測試。Worker 原始碼已寫入 repo，但尚未部署或設定秘密。
