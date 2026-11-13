# LINE 遠端控制設定

這是 Creator OS 的「遙控台」，不是任意遠端 shell。LINE 只建立受限命令；Mac 只執行 `worker-config.json` 中明確列出的 workflow。

## 部署前

先套用 D1 migration：

```powershell
npx wrangler d1 migrations apply creator-os --remote
```

Cloudflare Worker 必須設定以下 Secret。所有值都不可寫入 `.env.local`、README 或 Git。

```powershell
npx wrangler secret put LINE_CHANNEL_SECRET
npx wrangler secret put LINE_CHANNEL_ACCESS_TOKEN
npx wrangler secret put LINE_ALLOWED_USER_IDS
npx wrangler secret put LINE_PAIRING_CODE
npx wrangler secret put CREATOR_OS_WORKER_TOKEN
```

- `LINE_ALLOWED_USER_IDS`：只填老查自己的 LINE user ID。多個帳號才用逗號分隔。
- `LINE_PAIRING_CODE`：首次綁定自己的 LINE 帳號用。請用至少 20 碼的隨機字串；成功配對後可保留或撤銷。
- `CREATOR_OS_WORKER_TOKEN`：隨機長字串。它只放在 Cloudflare Secret 與 Mac 的 `worker-config.json`。

部署 Worker 後，把 LINE Developers Console 的 Webhook URL 設為：

```text
https://creator-os-line.siming1221.workers.dev/line/webhook
```

Webhook 使用獨立的 `creator-os-line` Worker，不套 Cloudflare Access。LINE 無法登入 Access；保護靠 LINE 簽章驗證與 `LINE_ALLOWED_USER_IDS` 雙層控管。既有 Creator OS 工作站仍維持 Access 保護。

## 第一期可用指令

```text
進度
待我核准
執行 每日檢查
```

首次傳訊前，先傳 `配對 <LINE_PAIRING_CODE>`。Bot 只會把送出正確配對碼的 LINE user ID 寫入 D1 白名單。

`執行 每日檢查` 只會呼叫 Mac 設定檔裡的 `daily-check`。其他自由文字不會被轉成 shell 指令。

「核准／退件／暫停」的完整工作流仍要先把 Creator OS 既有 task 資料由瀏覽器 `localStorage` 遷移成 D1 的單一資料源，否則 LINE 操作的是雲端、工作站卻仍可能讀本機舊資料，會製造兩份真相。

## Mac 上線後

依 `../mac-worker/README.md` 建立私有 `worker-config.json`，只列出已審核 workflow，再透過 `launchd` 常駐。Mac 離線時，LINE 命令保持 `queued`；不會偽稱工作已完成。
