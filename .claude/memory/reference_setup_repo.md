---
name: reference_setup_repo
description: GitHub repo for Claude Code environment setup on a new Mac
metadata: 
  node_type: memory
  type: reference
  originSessionId: 27405260-e3d6-4b19-8765-9e94f082e77b
---

Claude Code 換電腦設定 repo：https://github.com/CharlesWang1221/claude-code-setup

包含：
- `setup.sh`：一鍵安裝 MCP 工具（Node.js、Playwright、Cloudflare、Firecrawl、Wrangler）+ Skills
- `skills/skill-creator`：自訂 skill
- `site/`：「不標準答案」Astro 網站（Cloudflare Pages 部署）
- `.claude/settings.local.json`：Claude Code 權限設定

**安裝注意事項：**
- Homebrew 安裝需要在 Terminal.app 執行（Claude Code 無 TTY，無法輸入 sudo 密碼）
- Wrangler 安裝需加 `--allow-scripts=esbuild,workerd,sharp`
- 安裝後需執行 `wrangler login` 登入 Cloudflare
- 重啟 Claude Code 讓 MCP 生效
