# MCP 一鍵安裝腳本
# 執行方式：在 PowerShell 輸入  .\setup.ps1

Write-Host ""
Write-Host "=== MCP 工具安裝腳本 ===" -ForegroundColor Cyan
Write-Host ""

# ── 1. Node.js ──────────────────────────────────────────────
Write-Host "[1/5] 檢查 Node.js..." -ForegroundColor Yellow

$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCmd) {
    Write-Host "      已安裝：$(node --version)" -ForegroundColor Green
} else {
    Write-Host "      未偵測到 Node.js，開始安裝..." -ForegroundColor Yellow
    winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    Write-Host "      Node.js 安裝完成：$(node --version)" -ForegroundColor Green
}

# 確保 PATH 包含 Node.js
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

# ── 2. Playwright 瀏覽器 ─────────────────────────────────────
Write-Host ""
Write-Host "[2/5] 安裝 Playwright Chromium 瀏覽器..." -ForegroundColor Yellow
npx -y playwright install chromium
Write-Host "      Playwright 瀏覽器安裝完成" -ForegroundColor Green

# ── 3. MCP 工具 ──────────────────────────────────────────────
Write-Host ""
Write-Host "[3/5] 加入 MCP 工具..." -ForegroundColor Yellow

# Filesystem（桌面 / Documents / Downloads）
$username = $env:USERNAME
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem `
    "C:\Users\$username\Desktop" `
    "C:\Users\$username\Documents" `
    "C:\Users\$username\Downloads"
Write-Host "      Filesystem 加入完成" -ForegroundColor Green

# Playwright
claude mcp add playwright -- npx -y @playwright/mcp
Write-Host "      Playwright 加入完成" -ForegroundColor Green

# Cloudflare
claude mcp add cloudflare -- npx mcp-remote https://observability.mcp.cloudflare.com/mcp
Write-Host "      Cloudflare MCP 加入完成" -ForegroundColor Green

# ── 4. Firecrawl ─────────────────────────────────────────────
Write-Host ""
Write-Host "[4/5] Firecrawl API Key 設定" -ForegroundColor Yellow
Write-Host "      申請網址：https://www.firecrawl.dev/" -ForegroundColor Gray
Write-Host "      （免費方案 500 次/月，用 Google 帳號登入即可）" -ForegroundColor Gray
Write-Host ""
$firecrawlKey = Read-Host "      請貼上你的 Firecrawl API Key（直接 Enter 跳過）"

if ($firecrawlKey -ne "") {
    claude mcp add firecrawl -e "FIRECRAWL_API_KEY=$firecrawlKey" -- npx -y firecrawl-mcp
    Write-Host "      Firecrawl 加入完成" -ForegroundColor Green
} else {
    Write-Host "      已跳過 Firecrawl（之後可手動執行）" -ForegroundColor Gray
    Write-Host "      指令：claude mcp add firecrawl -e FIRECRAWL_API_KEY=你的Key -- npx -y firecrawl-mcp" -ForegroundColor Gray
}

# ── 5. Cloudflare Wrangler 登入提示 ──────────────────────────
Write-Host ""
Write-Host "[5/5] Cloudflare Wrangler CLI" -ForegroundColor Yellow

$wranglerCmd = Get-Command wrangler -ErrorAction SilentlyContinue
if (-not $wranglerCmd) {
    Write-Host "      安裝 Wrangler CLI..." -ForegroundColor Yellow
    npm install -g wrangler
}

Write-Host "      Wrangler 安裝完成" -ForegroundColor Green
Write-Host ""
Write-Host "      *** 重要：請在安裝完成後手動執行以下指令登入 Cloudflare ***" -ForegroundColor Yellow
Write-Host "      wrangler login" -ForegroundColor Cyan
Write-Host "      （會開啟瀏覽器，點 Allow 完成授權）" -ForegroundColor Gray

# ── 6. 網站專案依賴 ──────────────────────────────────────────
Write-Host ""
Write-Host "[6/6] 安裝《不標準答案》網站依賴..." -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$siteDir = Join-Path $scriptDir "site"

if (Test-Path $siteDir) {
    Set-Location $siteDir
    npm install
    Write-Host "      網站依賴安裝完成（Astro + fast-xml-parser）" -ForegroundColor Green
    Write-Host ""
    Write-Host "      網站開發指令（在 site/ 目錄執行）：" -ForegroundColor Gray
    Write-Host "      npm run dev     → 本地預覽 http://localhost:4321" -ForegroundColor Gray
    Write-Host "      npm run build   → 產生靜態檔案" -ForegroundColor Gray
    Write-Host "      npx wrangler pages deploy dist --project-name podcast-site --commit-dirty=true --branch main" -ForegroundColor Gray
    Set-Location $scriptDir
} else {
    Write-Host "      找不到 site/ 目錄，請確認 repo 已正確 clone" -ForegroundColor Red
}

# ── 完成 ──────────────────────────────────────────────────────
Write-Host ""
Write-Host "=== 安裝完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "請重新啟動 Claude Code 讓 MCP 工具生效。" -ForegroundColor White
Write-Host "驗證指令：claude mcp list" -ForegroundColor Gray
Write-Host ""
