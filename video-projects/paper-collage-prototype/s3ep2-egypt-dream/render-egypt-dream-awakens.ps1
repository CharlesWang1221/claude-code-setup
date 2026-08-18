param(
  [string]$OutputFile = 's3ep2-dream-awakens.mp4',
  [Parameter(Mandatory = $true)]
  [string]$AudioFile
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$asset = Join-Path $root 'assets'
$output = Join-Path $root $OutputFile
$captions = 's3ep2-dream-awakens.ass'

$nightSky = Join-Path $asset 'egypt-window-night-v1.png'
$room = Join-Path $asset 'egypt-room-window-v1.png'

# The night sky stays outside the large central window. The dream book rises inside the room.
$filter = "[0:v]scale=1080:1920,format=rgba[night];[1:v]scale=1080:1920,format=rgba[room];[2:v]scale=720:-1,format=rgba[book];[3:v]format=rgba[panelOne];[4:v]format=rgba[panelTwo];[night][room]overlay=shortest=1[v1];[v1][book]overlay=x='(W-w)/2+9*sin(0.6*t)':y='if(lt(t,1.8),2050,if(lt(t,3.2),2050-1250*(t-1.8),300+10*sin(14*(t-3.2))*exp(-2*(t-3.2))))':shortest=1[v2];[v2][panelOne]overlay=x=80:y=90:enable='between(t,0.7,4.4)'[v3];[v3][panelTwo]overlay=x=80:y=1640:enable='between(t,4.4,10.8)'[v4];[v4]subtitles='$captions',format=yuv420p[v]"

& ffmpeg -y `
  -loop 1 -framerate 30 -i $nightSky `
  -loop 1 -framerate 30 -i $room `
  -loop 1 -framerate 30 -i (Join-Path $asset 'egypt-dream-book-v1.png') `
  -loop 1 -framerate 30 -i (Join-Path $asset 'subtitle-panel-single.png') `
  -loop 1 -framerate 30 -i (Join-Path $asset 'subtitle-panel-double.png') `
  -ss 00:48:48.0 -t 10.8 -i $AudioFile `
  -filter_complex $filter `
  -map '[v]' -map 5:a -t 10.8 -r 30 `
  -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k `
  -movflags +faststart $output

Write-Host "Rendered: $output"
