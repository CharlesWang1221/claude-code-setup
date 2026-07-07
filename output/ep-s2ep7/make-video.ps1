# S2EP7 YouTube 影片產生腳本
# 需要先安裝 FFmpeg：winget install Gyan.FFmpeg

$AUDIO  = "C:\Users\siming_wang\Downloads\s2ep7_缩混.mp3"
$COVER  = "G:\我的雲端硬碟\不標準答案\2026\網誌\節目\S2EP8\S2ep8_V2.png"
$OUTPUT = "$PSScriptRoot\s2ep7-youtube.mp4"

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "找不到 FFmpeg，請先執行：winget install Gyan.FFmpeg"
    exit 1
}

if (-not (Test-Path $AUDIO)) {
    Write-Host "找不到音檔：$AUDIO"
    exit 1
}

if (-not (Test-Path $COVER)) {
    Write-Host "找不到封面圖：$COVER（請先填入正確路徑）"
    exit 1
}

Write-Host "開始轉檔，音檔：$AUDIO"
ffmpeg -loop 1 -i $COVER -i $AUDIO `
    -c:v libx264 -tune stillimage -crf 18 `
    -c:a aac -b:a 192k `
    -pix_fmt yuv420p `
    -shortest `
    $OUTPUT

Write-Host "完成：$OUTPUT"
