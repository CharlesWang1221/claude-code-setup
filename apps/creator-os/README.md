# Creator OS

《不標準答案》的私人內容營運工作站 MVP。

目前包含：今日推進、內容流轉、節奏日曆、復盤沉澱與規則庫。資料暫存在使用者瀏覽器的 `localStorage`，尚未接 Supabase、n8n、Google Calendar 或平台成效 API。

## 在新電腦啟動

```bash
cd apps/creator-os
npm install
npm run dev
```

開啟 `http://localhost:3000`。正式建置驗證使用 `npm run lint` 與 `npm run build`。

## 注意

- 這是獨立私有工具，不併入 `site/` 的公開 Podcast 官網。
- 將來改接雲端資料庫前，先確認目前欄位與節奏至少使用滿 2 至 4 週。
- 本 repo 為公開 repo，絕不提交 API key、OAuth token 或私人內容素材。
