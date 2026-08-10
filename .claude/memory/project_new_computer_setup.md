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

---

## 2026-07-11 macOS 安裝狀態（ming 這台）

`setup.sh` 已跑完，MCP 已全部用 `-s user` 重新加入（.claude.json）：

- [x] **Filesystem / Playwright / Cloudflare MCP** — 已加入，✔ Connected
- [x] **Firecrawl** — 已加入（fc-eaf8...），✔ Connected
- [x] **Cloudflare 登入** — wrangler 已登入（siming1221@gmail.com）
- [x] **Google Workspace MCP** — OAuth 完成，token 存於 ~/.config/google-docs-mcp/token.json，✔ Connected
- [x] **.env 檔** — PEXELS_API_KEY 已寫入 tools/video-auto-edit/.env
- [ ] **重啟 Claude Code** — 讓新加的 MCP 在 UI 層生效

## 2026-07-27 複查（同一台 Mac：MingdeMacBook-Pro.local）

老查說「換電腦到 mac」，實際檢查發現 repo 路徑是 `/Users/ming/Documents/CCoode/claude-code-setup`（不是筆記裡的 `~/Code/`），且環境早已是完整狀態：

- [x] gh auth 已登入（CharlesWang1221）
- [x] wrangler 已登入（siming1221@gmail.com）
- [x] repo 已 clone，`git status` clean，跟 origin/main 同步
- [x] 所有 MCP（filesystem/playwright/cloudflare/firecrawl/google-workspace + claude.ai 整合的 Zapier/VidIQ/Figma/Canva/Asana/Ahref/Semrush/Adobe 等）✔ Connected
- [x] 補跑 `npm install`（claude-code-setup 根目錄的 node_modules 原本缺失，已裝好 90 個套件）

**Why:** repo 路徑跟舊筆記不一致，之後若再「換電腦」要優先用 `find ~ -maxdepth 3 -iname claude-code-setup` 或直接檢查 `/Users/ming/Documents/CCoode` 確認實際路徑，不要照搬 `~/Code/` 假設。
**How to apply:** 下次老查說換電腦時，先跑 gh/wrangler/git status/claude mcp list 診斷，而不是直接整套重跑安裝腳本——很可能已經同步過了。

## 2026-07-27 新增：Codex CLI 同步

老查這天也在同一台 Mac 裝了 OpenAI Codex CLI（`curl -fsSL https://chatgpt.com/install.sh | sh`），並要求跟 Claude Code 同步 MCP 工具跟 skills。

**關鍵發現：**
- Codex CLI 讀取 skills 的實際路徑是 `~/.codex/skills/`（直接放資料夾進去，SKILL.md 格式跟 Claude 幾乎相容），**不是** `~/.agents/skills`——舊版 `setup.sh` 裡鏡射到 `~/.agents/skills` 那段其實從未生效，已經移除替換掉。
- Codex 的 MCP 設定在 `~/.codex/config.toml`，格式是 `[mcp_servers.NAME]` + `command`/`args`/`[mcp_servers.NAME.env]`，跟 Claude 的 `~/.claude.json` 的 `mcpServers` 概念一致，可以直接轉換。
- 用 `curl ... | sh` 安裝時腳本結尾會嘗試自動啟動 `codex`，但因為整條指令是透過 pipe 執行、stdin 不是 TTY，自動啟動一定會失敗（`Error: stdin is not a terminal`）且不會顯示錯誤，畫面只會不斷跳回空 prompt。**解法：另開一個全新終端機視窗，直接打 `codex`。**
- Codex 的 MCP 工具呼叫在非互動模式（`codex exec`）下，若該工具被歸類為「會碰網路/外部帳號」（如 firecrawl），即使加 `-a never` 也會被 approval 機制擋下並靜默取消（`user cancelled MCP tool call`），模型會自己編答案頂替，容易誤判成「工具能用」。真正用 `codex`（互動 TUI）操作時會正常跳出確認框，不受影響。純本機唯讀工具（如 filesystem）不受此限制。

**已建立同步工具：** `claude-code-setup/tools/sync-codex.sh`（idempotent，可重複執行）：
1. 把 `~/.claude/skills/*`（排除 `skill-creator`，Codex 內建同款）鏡射到 `~/.codex/skills/`，用 manifest 檔追蹤刪除掉的 skill
2. 把 `~/.claude.json` 的 `mcpServers` 轉成 TOML，用註解標記包住寫入 `~/.codex/config.toml`（重跑不會產生重複區塊）

已接進 `setup.sh` 步驟 7（裝完 Claude skills 後，偵測到 `codex` 指令就自動跑這支腳本）。

**How to apply:** 之後老查說「同步 codex」「codex 跟 claude 同步」，直接跑 `tools/sync-codex.sh` 或提示已經接在 `setup.sh` 裡，不用重新研究路徑。若要新增其他 MCP 或 skill，改 Claude 那邊（`~/.claude.json` / `~/.claude/skills`）後重跑這支腳本即可。
