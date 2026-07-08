# 短影音自動剪輯環境設定（Windows）
# 執行：.\setup.ps1

Write-Host "=== 短影音自動剪輯 Pipeline 設定 ===" -ForegroundColor Cyan

# 1. FFmpeg
Write-Host "`n[1/4] 檢查 FFmpeg..."
if (Get-Command ffmpeg -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ FFmpeg 已安裝" -ForegroundColor Green
} else {
    Write-Host "  安裝 FFmpeg..."
    winget install Gyan.FFmpeg
    Write-Host "  ✓ FFmpeg 安裝完成" -ForegroundColor Green
}

# 2. Python
Write-Host "`n[2/4] 檢查 Python..."
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyver = python --version
    Write-Host "  ✓ $pyver" -ForegroundColor Green
} else {
    Write-Host "  ✗ 找不到 Python，請先安裝 Python 3.10+" -ForegroundColor Red
    Write-Host "    https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# 3. Python 套件
Write-Host "`n[3/4] 安裝 Python 套件..."
pip install openai-whisper auto-editor requests --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 套件安裝完成" -ForegroundColor Green
} else {
    Write-Host "  ✗ 套件安裝失敗，請手動執行：pip install openai-whisper auto-editor requests" -ForegroundColor Red
}

# 4. Pexels API Key
Write-Host "`n[4/4] Pexels API Key 設定..."
if ($env:PEXELS_API_KEY) {
    Write-Host "  ✓ PEXELS_API_KEY 已設定" -ForegroundColor Green
} else {
    Write-Host "  ⚠ 尚未設定 PEXELS_API_KEY" -ForegroundColor Yellow
    Write-Host "  1. 到 https://www.pexels.com/api/ 申請 API Key" -ForegroundColor Yellow
    Write-Host "  2. 執行以下指令加入永久環境變數：" -ForegroundColor Yellow
    Write-Host '     [Environment]::SetEnvironmentVariable("PEXELS_API_KEY","你的KEY","User")' -ForegroundColor White
}

# 建立專案資料夾
Write-Host "`n建立 video-projects 資料夾..."
$root = Join-Path $PSScriptRoot "..\..\video-projects"
if (-not (Test-Path $root)) {
    New-Item -ItemType Directory $root | Out-Null
    Write-Host "  ✓ 建立 $root" -ForegroundColor Green
} else {
    Write-Host "  ✓ 已存在" -ForegroundColor Green
}

Write-Host "`n=== 設定完成 ===" -ForegroundColor Cyan
Write-Host @"

使用方式：
  1. 把錄影丟進  video-projects/{影片名稱}/01-raw/
  2. 開啟 Claude Code，說「剪這支 {影片名稱}」
  3. Claude Code 會自動執行完整 pipeline

手動執行字幕編輯器：
  用瀏覽器開啟 tools\video-auto-edit\subtitle-editor.html
"@
