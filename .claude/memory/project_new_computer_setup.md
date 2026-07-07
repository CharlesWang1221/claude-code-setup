---
name: project_new_computer_setup
description: 換電腦時的 Claude Code + MCP 環境還原流程，支援 Windows 和 macOS，含 GitHub repo 和一鍵安裝腳本
metadata: 
  node_type: memory
  type: project
  originSessionId: 70c5e1d5-4c1b-4e87-a519-d304700f6082
---

已建立 GitHub repo 存放 MCP 設定與一鍵安裝腳本：
**https://github.com/CharlesWang1221/claude-code-setup**

**Why:** 老查有兩台電腦（ASUS Windows + MacBook），需要快速在新機器上還原 Claude Code MCP 工具環境。

**How to apply:** 每當老查提到「換電腦」「新電腦」「第二台電腦」「重裝環境」，立刻直接執行以下還原流程，不用再問。

---

## 統一慣例

兩台機器都 clone 到 `~/Code/`：
- Windows：`C:\Users\siming_wang\Code\claude-code-setup`
- macOS：`/Users/siming_wang/Code/claude-code-setup`

---

## Windows 還原步驟

**Step 1** — 安裝 Git + GitHub CLI
```powershell
winget install Git.Git --accept-source-agreements --accept-package-agreements
winget install GitHub.cli --accept-source-agreements --accept-package-agreements
```

**Step 2** — 登入 GitHub
```powershell
gh auth login
```

**Step 3** — Clone repo
```powershell
git clone https://github.com/CharlesWang1221/claude-code-setup ~/Code/claude-code-setup
cd ~/Code/claude-code-setup
```

**Step 4** — 執行一鍵安裝腳本
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

**Step 5（手動）** — Cloudflare 登入
```powershell
wrangler login
```

---

## macOS 還原步驟

**Step 1** — 安裝 Git + GitHub CLI（setup.sh 會裝 Homebrew，但 gh 要先裝才能 clone private repo）
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git gh
```

**Step 2** — 登入 GitHub
```bash
gh auth login
```

**Step 3** — Clone repo
```bash
git clone https://github.com/CharlesWang1221/claude-code-setup ~/Code/claude-code-setup
cd ~/Code/claude-code-setup
```

**Step 4** — 執行一鍵安裝腳本
```bash
chmod +x setup.sh
./setup.sh
```

**Step 5（手動）** — Cloudflare 登入
```bash
wrangler login
```

---

## 腳本會自動安裝的工具

| 工具 | 類型 | 用途 |
|------|------|------|
| Filesystem | MCP | 存取 Desktop / Documents / Downloads |
| Playwright | MCP | 操作瀏覽器、截圖、填表單 |
| Firecrawl | MCP | 讀取任何網頁內容（免費 500 次/月） |
| Cloudflare MCP | MCP | 查詢 Cloudflare Workers 日誌 |
| Wrangler CLI | CLI | 部署靜態網頁到 Cloudflare Pages |
| 《不標準答案》網站依賴 | npm | Astro + fast-xml-parser |

Firecrawl API Key 由老查自行保管，安裝時腳本會詢問輸入。
Cloudflare 登入需要跑 `wrangler login`（瀏覽器授權），腳本跑完後手動執行一次。
