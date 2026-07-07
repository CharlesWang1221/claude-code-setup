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

### 4. Cloudflare
- 狀態：✅ 已安裝並登入
- 用途：部署靜態網頁到 Cloudflare Pages（完全免費）、管理 DNS、Cloudflare Workers
- 適合：純前端網頁、Landing Page、個人網站
- 元件：Wrangler CLI + Cloudflare MCP Server

### 5. Google Workspace
- 狀態：✅ Connected
- 用途：串接 Gmail、Drive、Docs、Sheets、Calendar
- GCP 專案：`podcast-tools-501708`，OAuth client：`podcast-uploader`（Desktop 類型）
- 授權帳號：siming1221@gmail.com
- credentials.json 位置：`~/.config/google-mcp/credentials.json`
- token 位置：`~/.config/google-docs-mcp/token.json`
- 換電腦時：執行 `setup.sh`，步驟 6 會自動授權（瀏覽器開啟，用 siming1221@gmail.com 登入按「繼續」即可）

### 6. Zeabur Agent Skills
- 狀態：⚠️ 被 ASUS 企業政策封鎖（macOS 個人電腦可安裝）
- 用途：有後端的專案、Bot、資料庫應用部署（Node.js / Python / Go 都支援）
- macOS 安裝指令：
  ```bash
  claude plugin marketplace add zeabur/agent-skills
  claude plugin install zeabur@zeabur
  ```
- 需要 Zeabur 帳號（用 GitHub 登入）：https://zeabur.com

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
