param(
    [Parameter(Mandatory=$true)][string]$EpSlug,
    [string]$Audio = ""
)

$ROOT  = "D:\hot data\CCoode"
$TOOLS = "$ROOT\tools\firstory-upload"

if (-not (Test-Path "$TOOLS\node_modules")) {
    Write-Host "Installing playwright..." -ForegroundColor Yellow
    Push-Location $TOOLS
    npm install
    npx playwright install chromium
    Pop-Location
}

$audioArg = if ($Audio -ne "") { "--audio `"$Audio`"" } else { "" }
node "$TOOLS\upload.mjs" --episode $EpSlug $audioArg