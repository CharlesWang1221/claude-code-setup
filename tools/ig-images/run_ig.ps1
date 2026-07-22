param(
    [Parameter(Mandatory=$true)][string]$EpSlug,
    [string]$CoverImage = "--auto"
)

$ROOT   = "D:\hot data\CCoode"
$NOTES  = "$ROOT\output\ep-$EpSlug\show-notes.md"
$OUTDIR = "$ROOT\output\ep-$EpSlug\ig"
$TOOLS  = "$ROOT\tools\ig-images"

if (-not (Test-Path $NOTES)) { Write-Error "show-notes.md not found: $NOTES"; exit 1 }

Write-Host "=== IG Image Pipeline: ep-$EpSlug ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "$TOOLS\node_modules")) {
    Write-Host "[0/2] Installing puppeteer..." -ForegroundColor Yellow
    Push-Location $TOOLS; npm install; Pop-Location
    if ($LASTEXITCODE -ne 0) { exit 1 }
}

Write-Host "[1/2] Generating HTML..." -ForegroundColor Yellow
python "$TOOLS\build_ig.py" $NOTES $CoverImage $OUTDIR
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
Write-Host "[2/2] Capturing screenshots (8 images)..." -ForegroundColor Yellow
foreach ($html in (Get-ChildItem "$OUTDIR\html\*.html" | Sort-Object Name)) {
    $name = [IO.Path]::GetFileNameWithoutExtension($html.Name)
    node "$TOOLS\capture_ig.mjs" $html.FullName "$OUTDIR\$name.png" 1080 1080
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed: $($html.Name)"; exit 1 }
}

Write-Host ""
Write-Host "=== Done! ===" -ForegroundColor Green
Write-Host "Output: $OUTDIR"
Write-Host "Quote cards (pick 1): quote_1.png  quote_2.png  quote_3.png" -ForegroundColor Yellow
Write-Host "Carousel (all 5):     carousel_1.png ~ carousel_5.png" -ForegroundColor Yellow