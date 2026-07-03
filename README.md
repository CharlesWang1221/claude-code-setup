# Claude Code 環境設定

Claude Code MCP 工具一鍵安裝腳本，支援 Windows 與 macOS。

## 換電腦還原步驟

### Step 1 — 安裝 Git + GitHub CLI

**Windows**
```powershell
winget install Git.Git --accept-source-agreements --accept-package-agreements
winget install GitHub.cli --accept-source-agreements --accept-package-agreements
```

**macOS**
```bash
# 先安裝 Homebrew（setup.sh 也會自動裝，這步可跳過）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git gh
```

### Step 2 — 登入 GitHub

```bash
gh auth login
```

### Step 3 — Clone repo

```bash
# 兩台機器都 clone 到 ~/Code/（統一慣例）
git clone https://github.com/CharlesWang1221/claude-code-setup ~/Code/claude-code-setup
cd ~/Code/claude-code-setup
```

> Windows 的 `~` 對應 `C:\Users\你的帳號`，效果相同。

### Step 4 — 執行一鍵安裝腳本

**Windows（PowerShell）**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

**macOS（Terminal）**
```bash
chmod +x setup.sh
./setup.sh
```

腳本會自動安裝：
- Node.js
- Playwright Chromium
- Filesystem MCP（Desktop / Documents / Downloads）
- Playwright MCP
- Cloudflare MCP
- Firecrawl MCP（輸入 API Key）
- Wrangler CLI
- 《不標準答案》網站 npm 依賴

### Step 5 — Cloudflare 登入（手動，會開瀏覽器）

```bash
wrangler login
```

---

## 已安裝的工具

| 工具 | 用途 |
|------|------|
| Filesystem MCP | 存取 Desktop / Documents / Downloads |
| Playwright MCP | 操作瀏覽器、截圖、填表單 |
| Firecrawl MCP | 讀取任何網頁內容（免費 500 次/月） |
| Cloudflare MCP | 查詢 Cloudflare Workers 日誌 |
| Wrangler CLI | 部署靜態網頁到 Cloudflare Pages |

## Firecrawl API Key

申請網址：https://www.firecrawl.dev/（Google 帳號登入即可）

事後補設定指令：
```bash
claude mcp add firecrawl -e FIRECRAWL_API_KEY=你的Key -- npx -y firecrawl-mcp
```
