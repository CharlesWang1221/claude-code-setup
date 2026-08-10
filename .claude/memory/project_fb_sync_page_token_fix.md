---
name: project_fb_sync_page_token_fix
description: GitHub Actions「Sync Facebook Posts to Blog」token失效修復記錄與根因(新版粉專需換Page Token,不能直接用System User token)
metadata:
  type: project
  originSessionId: c0303cd7-7a04-4a1d-a3ed-0bc2def5d358
---

## 背景
`CharlesWang1221/claude-code-setup` repo 的 GitHub Actions「Sync Facebook Posts to Blog」（cron `0 14 * * *`，跑 `.github/scripts/sync-fb-posts.js`，抓「不標準答案」粉專貼文同步到 blog + Instagram）從約 8/5 起持續失敗，因為 `FB_PAGE_ACCESS_TOKEN` secret 存的舊 token 過期。

## 修復過程
1. 在 Meta Business Suite（`business.facebook.com/latest/settings/system_users`）用既有 System User「GitHub Actions Bot」（ID `61593252775688`）產生新權杖，App 選「Beyond Ans Blog」，勾選 `pages_read_engagement`、`instagram_basic`、`instagram_content_publish` 三個 scope。
2. **關鍵根因（非顯而易見）**：即使 System User token 本身有效且 scope 正確（`debug_token` 驗證 `is_valid:true`），直接拿去打 `/{page_id}/posts` 仍會報 `(#190) Invalid OAuth 2.0 Access Token`，`error_subcode 2069032`，訊息「不支援用戶存取權杖，若要存取新版粉絲專頁體驗，必須提供粉絲專頁存取權杖」。**原因：Facebook 新版粉專體驗（New Pages Experience）要求真正的 Page Access Token，System User/User token 不算，即使該 System User 已被指派這個粉專資產。**
3. **解法**：拿 System User token 再打一次 `GET /{page_id}?fields=access_token&access_token={system_user_token}`，這會換回一個真正的 Page-scoped access token（前綴一樣是 `EAA...`，但 `type` 不同、長度也不同，這次是198字元）。把**這個換出來的 page token**存進 `FB_PAGE_ACCESS_TOKEN` secret，`/posts` 呼叫才成功。
4. 修復完成，workflow 重跑成功（run id 31384674790，sync 1m27s）。

**Why:** Meta 對「新版粉絲專頁」的 Graph API 存取權限模型改了，`/page_id/posts` 這類 edge 現在只認 Page Access Token，不接受 System User 直接呼叫，即使權限指派正確。這不是 token 過期/scope 錯誤/剪貼簿傳輸corruption的問題（這三種都排查過並排除），是 API 存取模型本身的限制。
**How to apply:** 之後這個 token 過期要重新產生時，記得**多一步**：System User token 產生後，不要直接拿去用，要先用它去換 `/{page_id}?fields=access_token` 拿到真正的 Page Token，再存進 GitHub secret。System User token 60天到期（這次選的到期時間），到期前應該要重複這個流程。

## 診斷排查方向（下次出狀況時的優先順序）
1. 先跑 `gh run list --workflow="Sync Facebook Posts to Blog" --repo CharlesWang1221/claude-code-setup --limit 5` 看**實際執行紀錄的時間/耗時/結果**，不要只看老查手機收到的 GitHub 失敗通知信就判斷現狀——通知信可能延遲送達或是舊信，跟最新一次真正的執行結果對不上（2026-08-10 曾發生：老查看到一封「Failed in 8 seconds」的信，但當時最新一筆執行紀錄其實已經成功且耗時1m36s，是舊信造成誤判）。
2. 若確認是真的新失敗，用 `gh run view <run_id> --repo CharlesWang1221/claude-code-setup --log-failed` 看錯誤訊息：
   - 若是 `Cannot parse access token` / 明顯格式錯誤 → 大概是 secret 存值時傳輸出錯（剪貼簿污染之類），重新設一次 secret。
   - 若是 `(#190) Invalid OAuth 2.0 Access Token` 且 `error_subcode 2069032`／訊息提到「新版粉絲專頁」「粉絲專頁存取權杖」→ 就是本篇記錄的根因，直接跳到上面「解法」步驟重新換 Page Token。
   - 若是提示缺少某個 permission（如 `pages_read_engagement`）→ 回 Meta 重新產生 System User token 時把該 scope 勾上。

## 傳輸經驗（技術細節，供下次參考）
- 剪貼簿在瀏覽器「複製」按鈕點擊後立刻用 `pbpaste` 讀取是可行的，之前懷疑的「剪貼簿被其他活動覆蓋」問題本次沒重現（可能是巧合或環境因素，不是穩定必然發生）。
- `navigator.clipboard.writeText()` 透過 `javascript_tool` 在頁面內執行容易 timeout（45秒逾時過），不可靠，之後優先用點擊真實「複製」按鈕 + 立即 `pbpaste` 的方式。
- 用 `javascript_tool` 直接把 token 值當作回傳結果讀出來，會被系統安全機制擋掉（回報「[BLOCKED: Base64 encoded data]」），這是設計上的防護，不要嘗試繞過。
- 全程驗證 token 是否有效，優先用 `curl .../debug_token` 或直接打真正要用的 API，只印診斷用 JSON（不含原始token），絕不在 bash 輸出或聊天訊息印出完整 token 值。

相關：無（獨立事件，跟每日排程 Zapier 額度問題[[project_daily_mail_routines_zapier_quota]]無關）
