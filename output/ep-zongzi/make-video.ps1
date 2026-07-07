# 用法：把音檔路徑和封面圖路徑填進來，然後在 PowerShell 執行這個腳本
# 需要先安裝 FFmpeg：winget install Gyan.FFmpeg

$AUDIO = "C:\path\to\your\audio.mp3"       # <-- 改成你的音檔路徑
$COVER = "C:\path\to\your\cover.jpg"        # <-- 改成你的封面圖路徑
$OUTPUT = "$PSScriptRoot\youtube-video.mp4" # 輸出在同一個資料夾

# 確認 FFmpeg 存在
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "找不到 FFmpeg，請先執行：winget install Gyan.FFmpeg"
    exit 1
}

Write-Host "開始轉檔..."
ffmpeg -loop 1 -i $COVER -i $AUDIO `
    -c:v libx264 -tune stillimage -crf 18 `
    -c:a aac -b:a 192k `
    -pix_fmt yuv420p `
    -shortest `
    $OUTPUT

Write-Host "完成：$OUTPUT"
