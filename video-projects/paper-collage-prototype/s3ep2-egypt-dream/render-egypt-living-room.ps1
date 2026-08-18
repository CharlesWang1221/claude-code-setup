param(
  [string]$OutputFile = 's3ep2-history-in-picture-book.mp4',
  [Parameter(Mandatory = $true)]
  [string]$AudioFile
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$asset = Join-Path $root 'assets'
$daySky = Join-Path $asset 'egypt-window-day-v1.png'
$nightSky = Join-Path $asset 'egypt-window-night-v1.png'
$room = Join-Path $asset 'egypt-room-window-v1.png'
$storybook = Join-Path $asset 'egypt-storybook-v1.png'
$anubis = Join-Path $asset 'egypt-anubis-v1.png'
$captions = 's3ep2-history-in-picture-book.ass'
$output = Join-Path $root $OutputFile
$font = 'C\:/Windows/Fonts/msjhbd.ttc'

$filter = "[0:v]scale=1080:1920,format=rgba[day];[1:v]scale=1080:1920,format=rgba,fade=t=in:st=0.8:d=2.2:alpha=1[night];[2:v]scale=1080:1920,format=rgba[room];[3:v]scale=780:-1,format=rgba[book];[4:v]scale=650:-1,format=rgba[god];[5:v]format=rgba[panelA];[6:v]format=rgba[panelB];[day][night]overlay=shortest=1[sky];[sky][room]overlay=shortest=1[v1];[v1][book]overlay=x='(W-w)/2':y='if(lt(t,1.2),2050,if(lt(t,2.2),2050-850*(t-1.2),1200+12*sin(18*(t-2.2))*exp(-2*(t-2.2))))':shortest=1[v2];[v2][god]overlay=x='(W-w)/2+25*sin(0.8*t)':y='if(lt(t,3.0),1950,if(lt(t,4.2),1950-1210*(t-3.0),740+5*sin(1.7*t)))':shortest=1[v3];[v3][panelA]overlay=x=80:y=1660:enable='between(t,0.8,5.0)'[v4];[v4][panelB]overlay=x=80:y=1660:enable='between(t,5.0,10.6)'[v5];[v5]subtitles='$captions',format=yuv420p[v]"

& ffmpeg -y `
  -loop 1 -framerate 30 -i $daySky `
  -loop 1 -framerate 30 -i $nightSky `
  -loop 1 -framerate 30 -i $room `
  -loop 1 -framerate 30 -i $storybook `
  -loop 1 -framerate 30 -i $anubis `
  -loop 1 -framerate 30 -i (Join-Path $asset 'subtitle-panel-single.png') `
  -loop 1 -framerate 30 -i (Join-Path $asset 'subtitle-panel-single.png') `
  -ss 00:48:37.8 -t 10.6 -i $AudioFile `
  -filter_complex $filter `
  -map '[v]' -map 7:a -t 10.6 -r 30 `
  -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k `
  -movflags +faststart $output

Write-Host "Rendered: $output"
