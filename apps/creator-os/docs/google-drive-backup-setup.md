# Creator OS Google Drive 備份授權

這份設定只做一次。目標是讓 Cloudflare Worker 將 JSON 快照寫入老查擁有的 Google Drive 資料夾，不讓阿分或瀏覽器持有 Google OAuth 憑證。

## 1. Google Cloud

1. 用老查的 Google 帳號建立專案 `Creator OS Backup`。
2. 在「APIs & Services」啟用 Google Drive API。
3. 建立 OAuth consent screen，測試使用者只加入老查帳號。
4. 建立 OAuth Client（Desktop app），scope 使用 `https://www.googleapis.com/auth/drive.file`。

## 2. 取得 refresh token

使用剛建立的 Client ID 與 Client Secret 完成一次老查帳號授權，取得 refresh token。它等同可持續寫入指定 Drive 資料夾的鑰匙，不可貼到聊天、文件或 GitHub。

## 3. 設定 Cloudflare Secret

在 `apps/creator-os` 依序執行以下指令。每一個值在提示時貼入，終端機不會顯示內容：

```powershell
npx wrangler secret put GOOGLE_DRIVE_CLIENT_ID
npx wrangler secret put GOOGLE_DRIVE_CLIENT_SECRET
npx wrangler secret put GOOGLE_DRIVE_REFRESH_TOKEN
npx wrangler secret put GOOGLE_DRIVE_BACKUP_FOLDER_ID
```

最後一項填入 `不標準答案/Creator OS/備份` 的 Drive folder ID，不是網址。

## 4. 驗證

以 owner 登入正式工作站，按「立即備份」。成功後到 Drive 的 `不標準答案/Creator OS/備份/`，應看到 `creator-os_YYYYMMDDHHMMSS.json`。

每日備份排程是台北時間 03:30。若備份失敗，D1 的 `backup_runs` 會留下失敗原因；未成功前不能視為已有備份。
