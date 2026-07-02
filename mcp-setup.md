# MCP 工具安裝紀錄

安裝日期：2026-07-02

## 已安裝工具

### 1. Filesystem
- 狀態：✅ Connected
- 用途：讓 AI 存取專案目錄以外的資料夾
- 授權路徑：
  - `C:\Users\siming_wang\Desktop`
  - `C:\Users\siming_wang\Documents`
  - `C:\Users\siming_wang\Downloads`

### 2. Playwright
- 狀態：✅ Connected
- 用途：讓 AI 操作瀏覽器、截圖、填表單、抓需要登入的頁面
- 瀏覽器：Chromium（已下載至 `AppData\Local\ms-playwright`）

### 3. Firecrawl
- 狀態：✅ Connected
- 用途：貼 URL 讓 AI 讀取任何網頁內容，速度快
- 方案：免費 500 次/月
- API Key 已設定於環境變數 `FIRECRAWL_API_KEY`

### 4. Google Workspace
- 狀態：跳過（未安裝）
- 用途：串接 Gmail、行事曆、Drive、Sheets
- 備註：需要 Google Cloud Project + OAuth 設定，約 10-15 分鐘。待日後安裝。

## 前置安裝

- Node.js v24.18.0（透過 winget 安裝）
- npx v11.16.0

## 設定位置

MCP 設定寫入：`C:\Users\siming_wang\.claude.json`

## 驗證指令

```bash
claude mcp list
```

## 使用範例

- **Firecrawl**：「幫我摘要這篇文章 [URL]」
- **Playwright**：「幫我打開 [URL] 並截圖」
- **Filesystem**：「幫我列出桌面上有什麼檔案」
