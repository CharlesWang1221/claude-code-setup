# n8n Workflow — YouTube 自動化

兩支 workflow，都是「YouTube RSS 偵測到新公開影片 → 自動處理」，觸發頻率 30 分鐘一次。

## youtube-to-threads.json — 新影片自動發 Threads

新影片一上架（YouTube RSS 只會顯示公開影片，私人影片不會出現），自動用兩步驟（建立 container → 發布）發一篇 Threads 貼文。

## youtube-to-videos-pr.json — 新影片自動開 PR 補網站

新影片出現後，自動：開新分支 → 更新 `site/src/pages/videos.astro` 的 `videos` 陣列 → 開 Pull Request。
**不會自動 merge**，要老查自己去 GitHub 看過內容、確認沒問題再按合併。

---

## 匯入步驟（兩支都一樣）

1. n8n 左側選單 → Workflows → 右上角 `Import from File`，選這個資料夾裡的 `.json` 檔
2. 匯入後會看到一張「設定說明」便利貼卡片，照上面寫的填東西
3. 兩件共同要填的：
   - **YouTube Channel ID**：去 YouTube Studio → 設定 → 頻道 → 進階設定，複製 Channel ID（`UC` 開頭 24 字元），貼到「YouTube RSS」節點的 url 裡取代 `REPLACE_WITH_CHANNEL_ID`
4. 測試：先手動點右上角 `Execute Workflow` 跑一次看有沒有噴錯，確認沒問題才把 Active 打開

## Threads 版額外要做

- 去 Meta for Developers 申請 Threads API，拿到長期 access token
- 呼叫一次 `GET https://graph.threads.net/v1.0/me?fields=id&access_token=你的token` 拿到你的 Threads User ID
- 把「Create Threads Container」「Publish Threads Post」兩個節點裡的 `REPLACE_WITH_THREADS_USER_ID` 換成這個 ID
- 在 n8n 建一個 Credential：類型選 **Query Auth**，Name 填 `access_token`，Value 填你的 Threads token，套用到上面那兩個節點

## GitHub PR 版額外要做

- 去 GitHub → Settings → Developer settings → Fine-grained personal access tokens，新建一個
  - Repository access：只勾 `claude-code-setup` 這一個 repo，不要給全帳號權限
  - Permissions：`Contents` 給 Read and write、`Pull requests` 給 Read and write，其他都不用給
- 在 n8n 建一個 Credential：類型選 **GitHub API**，貼上剛申請的 token，套用到裡面 4 個 HTTP Request 節點
- repo 目前預設寫死 `CharlesWang1221/claude-code-setup`，如果之後改 repo 名稱，要手動改這 4 個節點的 URL

## 安全注意

- Threads token、GitHub PAT 都只存在 n8n 的 Credential 裡（加密存放，前提是你已經設定 `N8N_ENCRYPTION_KEY`），不要把 token 直接寫進節點參數
- 兩支 workflow 匯入後預設是關閉的（`active: false`），手動測過一次沒問題才打開
