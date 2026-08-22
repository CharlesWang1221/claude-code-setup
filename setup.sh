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

# Filesystem MCP 已淘汰。Claude Code 與 Codex 都有內建檔案工具，避免重複權限與設定。

# Playwright
claude mcp add playwright -- npx -y @playwright/mcp
echo -e "${GREEN}      Playwright 加入完成${NC}"

# Cloudflare
claude mcp add cloudflare -- npx mcp-remote https://observability.mcp.cloudflare.com/mcp
echo -e "${GREEN}      Cloudflare MCP 加入完成${NC}"

# Plaud（會議錄音逐字稿/摘要）
claude mcp add plaud -- npx -y @plaud-ai/mcp@latest
echo -e "${GREEN}      Plaud 加入完成（首次使用時需跑一次 OAuth 登入，跳出瀏覽器授權即可）${NC}"

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

# ── 6. Google Workspace MCP ──────────────────────────────────
echo ""
echo -e "${YELLOW}[6/8] Google Workspace MCP（Gmail / Drive / Docs / Sheets / Calendar）${NC}"

SCRIPT_DIR_TMP="$(cd "$(dirname "$0")" && pwd)"
GOOGLE_CREDS_SRC="$SCRIPT_DIR_TMP/google-mcp/credentials.json"
GOOGLE_CREDS_DEST="$HOME/.config/google-mcp/credentials.json"

if [[ -f "$GOOGLE_CREDS_SRC" ]]; then
    # 有 credentials.json（手動放入，gitignored）直接用
    mkdir -p "$(dirname "$GOOGLE_CREDS_DEST")"
    cp "$GOOGLE_CREDS_SRC" "$GOOGLE_CREDS_DEST"
    echo -e "${GREEN}      已從 repo 複製 credentials.json${NC}"
    CLIENT_ID=$(python3 -c "import json; d=json.load(open('$GOOGLE_CREDS_DEST')); print(d['installed']['client_id'])")
    CLIENT_SECRET=$(python3 -c "import json; d=json.load(open('$GOOGLE_CREDS_DEST')); print(d['installed']['client_secret'])")
else
    echo -e "${GRAY}      未找到 google-mcp/credentials.json${NC}"
    echo -e "${GRAY}      GCP 專案：podcast-tools-501708，OAuth client：podcast-uploader${NC}"
    echo -e "${GRAY}      （可在 Claude Code memory 或 mcp-setup.md 查詢憑證）${NC}"
    echo ""
    read -rp "      請貼上 Google OAuth Client ID（直接 Enter 跳過）: " CLIENT_ID
    read -rp "      請貼上 Google OAuth Client Secret（直接 Enter 跳過）: " CLIENT_SECRET
fi

if [[ -n "$CLIENT_ID" && -n "$CLIENT_SECRET" ]]; then
    mkdir -p "$(dirname "$GOOGLE_CREDS_DEST")"
    cat > "$GOOGLE_CREDS_DEST" << GCREDS
{
  "installed": {
    "client_id": "$CLIENT_ID",
    "project_id": "podcast-tools-501708",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "$CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
GCREDS
    # 跑 OAuth 授權（瀏覽器會自動開啟，用 siming1221@gmail.com 登入並按「繼續」）
    echo -e "${YELLOW}      開始 Google OAuth 授權（瀏覽器會開啟，用 siming1221@gmail.com 登入）...${NC}"
    GOOGLE_CLIENT_ID="$CLIENT_ID" GOOGLE_CLIENT_SECRET="$CLIENT_SECRET" \
        npx -y @a-bonus/google-docs-mcp auth

    # 註冊到 Claude Code（全域 -s user）
    claude mcp add -s user google-workspace \
        -e "GOOGLE_CLIENT_ID=$CLIENT_ID" \
        -e "GOOGLE_CLIENT_SECRET=$CLIENT_SECRET" \
        -- npx -y @a-bonus/google-docs-mcp

    echo -e "${GREEN}      Google Workspace MCP 加入完成（Gmail / Drive / Docs / Sheets / Calendar）${NC}"
else
    echo -e "${GRAY}      已跳過 Google Workspace MCP${NC}"
    echo -e "${GRAY}      之後可手動執行 google-mcp/setup-google-mcp.sh${NC}"
fi

# ── 7. Claude Code Skills ────────────────────────────────────
echo ""
echo -e "${YELLOW}[7/8] 安裝 Claude Code Skills...${NC}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"
SKILLS_DEST="$HOME/.claude/skills"

if [[ -d "$SKILLS_SRC" ]]; then
    mkdir -p "$SKILLS_DEST"
    cp -r "$SKILLS_SRC"/. "$SKILLS_DEST/"
    COUNT=$(ls -d "$SKILLS_SRC"/*/ 2>/dev/null | wc -l | tr -d ' ')
    echo -e "${GREEN}      已安裝 $COUNT 個 skill 到 $SKILLS_DEST${NC}"
else
    echo -e "${GRAY}      找不到 skills/ 目錄，跳過${NC}"
fi

# 外部 Skill：video-shotcraft（影片頭，第三方 Remotion 鏡頭庫，只 clone 不 commit 進 repo）
mkdir -p "$SKILLS_DEST"
VIDEO_SHOTCRAFT_DEST="$SKILLS_DEST/video-shotcraft"
if [[ -d "$VIDEO_SHOTCRAFT_DEST/.git" ]]; then
    echo -e "${GRAY}      video-shotcraft 已存在，git pull 更新...${NC}"
    git -C "$VIDEO_SHOTCRAFT_DEST" pull --ff-only
else
    git clone --depth 1 https://github.com/Vincentwei1021/video-shotcraft.git "$VIDEO_SHOTCRAFT_DEST"
fi
echo -e "${GREEN}      已安裝 video-shotcraft（影片頭）${NC}"

# Codex 是主要工作代理。直接從 repo 安裝 Skills，不再以 Claude 設定反向覆蓋 Codex。
CODEX_SKILLS_DEST="$HOME/.codex/skills"
mkdir -p "$CODEX_SKILLS_DEST"
for dir in "$SKILLS_SRC"/*/; do
    [[ -d "$dir" ]] || continue
    name=$(basename "$dir")
    [[ "$name" == "skill-creator" ]] && continue
    mkdir -p "$CODEX_SKILLS_DEST/$name"
    cp -R "$dir"/. "$CODEX_SKILLS_DEST/$name/"
done
mkdir -p "$CODEX_SKILLS_DEST/video-shotcraft"
cp -R "$VIDEO_SHOTCRAFT_DEST"/. "$CODEX_SKILLS_DEST/video-shotcraft/"
echo -e "${GREEN}      已直接安裝 Skills 到 Codex（Codex 主、Claude 輔）${NC}"

CODEX_AGENTS_SRC="$SCRIPT_DIR/codex/AGENTS.global.md"
CODEX_HOME_DIR="$HOME/.codex"
if [[ -f "$CODEX_AGENTS_SRC" ]]; then
    mkdir -p "$CODEX_HOME_DIR"
    cp "$CODEX_AGENTS_SRC" "$CODEX_HOME_DIR/AGENTS.md"
    echo -e "${GREEN}      已安裝 Codex 全域規則 ~/.codex/AGENTS.md${NC}"
fi

# ── 8. 網站專案依賴 ──────────────────────────────────────────
echo ""
echo -e "${YELLOW}[8/8] 安裝《不標準答案》網站依賴...${NC}"

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

# ── 8. Status Line ───────────────────────────────────────────
echo ""
echo -e "${YELLOW}[9/9] 安裝 Claude Code 狀態列（雷蒙完整版）...${NC}"

# 安裝 jq（腳本依賴）
if ! command -v jq &>/dev/null; then
    echo -e "${YELLOW}      安裝 jq...${NC}"
    brew install jq
fi

# 備份舊腳本
test -f ~/.claude/statusline-command.sh && \
    cp ~/.claude/statusline-command.sh ~/.claude/statusline-command.sh.backup.$(date +%Y%m%d-%H%M%S)

# 複製腳本
mkdir -p ~/.claude/hooks
cp "$SCRIPT_DIR/statusline/statusline-command.sh" ~/.claude/statusline-command.sh
cp "$SCRIPT_DIR/statusline/hooks/session-time.sh" ~/.claude/hooks/session-time.sh
chmod +x ~/.claude/statusline-command.sh ~/.claude/hooks/session-time.sh

# 初始化時間戳
bash ~/.claude/hooks/session-time.sh

# 更新 settings.json
test -f ~/.claude/settings.json || echo '{}' > ~/.claude/settings.json

# 加入 statusLine + UserPromptSubmit hook（bash 版，macOS 原生支援）
python3 - <<'PYEOF'
import json, os, sys
path = os.path.expanduser("~/.claude/settings.json")
with open(path) as f:
    cfg = json.load(f)

cfg["statusLine"] = {"type": "command", "command": "bash ~/.claude/statusline-command.sh"}

hooks = cfg.setdefault("hooks", {})
submit = hooks.setdefault("UserPromptSubmit", [])
already = any("session-time.sh" in str(h) for h in submit)
if not already:
    submit.append({"hooks": [{"type": "command", "command": "~/.claude/hooks/session-time.sh", "timeout": 5}]})

with open(path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
print("      settings.json 更新完成")
PYEOF

echo -e "${GREEN}      狀態列安裝完成${NC}"
echo -e "${GRAY}      第一行：模型 │ Context 進度條 │ 5h 額度 │ 7d 額度${NC}"
echo -e "${GRAY}      第二行：Git 分支 │ +N/-N │ 專案名 │ 📝 最後訊息時間${NC}"
echo -e "${GRAY}      調整顯示：編輯 ~/.claude/statusline-command.sh 頂部的 true/false${NC}"

# ── 完成 ──────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}=== 安裝完成 ===${NC}"
echo ""
echo -e "請重新啟動 Claude Code 讓 MCP 工具、Skills 與狀態列生效。"
echo -e "${GRAY}驗證指令：claude mcp list${NC}"
echo ""

# ── API Keys 提示 ─────────────────────────────────────────────
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}⚠ 找不到 .env 檔（API Keys）${NC}"
  echo -e "${GRAY}  請從舊電腦複製 .env，或手動建立：${NC}"
  echo -e "${GRAY}  echo 'PEXELS_API_KEY=你的Key' >> .env${NC}"
  echo ""
else
  echo -e "${GREEN}✓ .env 已存在（API Keys 載入中）${NC}"
  echo ""
fi
