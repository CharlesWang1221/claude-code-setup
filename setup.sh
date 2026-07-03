#!/bin/bash
# MCP 一鍵安裝腳本（macOS）
# 執行方式：chmod +x setup.sh && ./setup.sh

CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
GRAY='\033[0;37m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${CYAN}=== MCP 工具安裝腳本（macOS）===${NC}"
echo ""

# ── 0. Homebrew ──────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
    echo -e "${YELLOW}[前置] 未偵測到 Homebrew，開始安裝...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Apple Silicon 需加入 PATH
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    fi
    echo -e "${GREEN}      Homebrew 安裝完成${NC}"
else
    echo -e "${GREEN}[前置] Homebrew 已安裝${NC}"
fi

# ── 1. Node.js ──────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[1/5] 檢查 Node.js...${NC}"

if command -v node &>/dev/null; then
    echo -e "${GREEN}      已安裝：$(node --version)${NC}"
else
    echo -e "${YELLOW}      未偵測到 Node.js，開始安裝...${NC}"
    brew install node
    echo -e "${GREEN}      Node.js 安裝完成：$(node --version)${NC}"
fi

# ── 2. Playwright 瀏覽器 ─────────────────────────────────────
echo ""
echo -e "${YELLOW}[2/5] 安裝 Playwright Chromium 瀏覽器...${NC}"
npx -y playwright install chromium
echo -e "${GREEN}      Playwright 瀏覽器安裝完成${NC}"

# ── 3. MCP 工具 ──────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[3/5] 加入 MCP 工具...${NC}"

USERNAME_HOME="$HOME"

# Filesystem（桌面 / Documents / Downloads）
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem \
    "$USERNAME_HOME/Desktop" \
    "$USERNAME_HOME/Documents" \
    "$USERNAME_HOME/Downloads"
echo -e "${GREEN}      Filesystem 加入完成${NC}"

# Playwright
claude mcp add playwright -- npx -y @playwright/mcp
echo -e "${GREEN}      Playwright 加入完成${NC}"

# Cloudflare
claude mcp add cloudflare -- npx mcp-remote https://observability.mcp.cloudflare.com/mcp
echo -e "${GREEN}      Cloudflare MCP 加入完成${NC}"

# ── 4. Firecrawl ─────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[4/5] Firecrawl API Key 設定${NC}"
echo -e "${GRAY}      申請網址：https://www.firecrawl.dev/${NC}"
echo -e "${GRAY}      （免費方案 500 次/月，用 Google 帳號登入即可）${NC}"
echo ""
read -rp "      請貼上你的 Firecrawl API Key（直接 Enter 跳過）: " FIRECRAWL_KEY

if [[ -n "$FIRECRAWL_KEY" ]]; then
    claude mcp add firecrawl -e "FIRECRAWL_API_KEY=$FIRECRAWL_KEY" -- npx -y firecrawl-mcp
    echo -e "${GREEN}      Firecrawl 加入完成${NC}"
else
    echo -e "${GRAY}      已跳過 Firecrawl（之後可手動執行）${NC}"
    echo -e "${GRAY}      指令：claude mcp add firecrawl -e FIRECRAWL_API_KEY=你的Key -- npx -y firecrawl-mcp${NC}"
fi

# ── 5. Cloudflare Wrangler ───────────────────────────────────
echo ""
echo -e "${YELLOW}[5/5] Cloudflare Wrangler CLI${NC}"

if ! command -v wrangler &>/dev/null; then
    echo -e "${YELLOW}      安裝 Wrangler CLI...${NC}"
    npm install -g wrangler
fi

echo -e "${GREEN}      Wrangler 安裝完成${NC}"
echo ""
echo -e "${YELLOW}      *** 重要：請在安裝完成後手動執行以下指令登入 Cloudflare ***${NC}"
echo -e "${CYAN}      wrangler login${NC}"
echo -e "${GRAY}      （會開啟瀏覽器，點 Allow 完成授權）${NC}"

# ── 6. 網站專案依賴 ──────────────────────────────────────────
echo ""
echo -e "${YELLOW}[6/6] 安裝《不標準答案》網站依賴...${NC}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SITE_DIR="$SCRIPT_DIR/site"

if [[ -d "$SITE_DIR" ]]; then
    cd "$SITE_DIR" && npm install
    echo -e "${GREEN}      網站依賴安裝完成（Astro + fast-xml-parser）${NC}"
    echo ""
    echo -e "${GRAY}      網站開發指令（在 site/ 目錄執行）：${NC}"
    echo -e "${GRAY}      npm run dev     → 本地預覽 http://localhost:4321${NC}"
    echo -e "${GRAY}      npm run build   → 產生靜態檔案${NC}"
    echo -e "${GRAY}      npx wrangler pages deploy dist --project-name podcast-site --commit-dirty=true --branch main${NC}"
    cd "$SCRIPT_DIR"
else
    echo -e "${RED}      找不到 site/ 目錄，請確認 repo 已正確 clone${NC}"
fi

# ── 完成 ──────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}=== 安裝完成 ===${NC}"
echo ""
echo -e "請重新啟動 Claude Code 讓 MCP 工具生效。"
echo -e "${GRAY}驗證指令：claude mcp list${NC}"
echo ""
