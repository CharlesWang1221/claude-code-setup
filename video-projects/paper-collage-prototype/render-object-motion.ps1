param(
  [string]$Caption = 'caption',
  [string]$OutputFile = 'object-motion-render.mp4'
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$asset = Join-Path $root 'assets'
$output = Join-Path $root $OutputFile
$font = 'C\:/Windows/Fonts/msjhbd.ttc'

# Satellite drifts, a route appears in three beats, landmarks land, then newspapers settle.
$filter = @"
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=rgba[bg];
[1:v]colorkey=0x00FF00:0.40:0.08,despill=green:mix=0.9,scale=390:-1,format=rgba[sat];
[2:v]colorkey=0x00FF00:0.40:0.08,despill=green:mix=0.9,scale=820:-1,format=rgba[land];
[3:v]colorkey=0x00FF00:0.40:0.08,despill=green:mix=0.9,scale=820:-1,format=rgba[news];
[bg][sat]overlay=x='620+25*sin(1.8*t)':y='340+10*sin(2.1*t)':shortest=1[v1];
[v1][land]overlay=x='(W-w)/2':y='if(lt(t,2.2),2100,if(lt(t,3),2100-1188*(t-2.2),1150+20*sin(20*(t-3))*exp(-2*(t-3))))':shortest=1[v2];
[v2][news]overlay=x='(W-w)/2':y='if(lt(t,3.3),1920,if(lt(t,4.2),1920-522*(t-3.3),1450))':shortest=1[v3];
[v3]drawbox=x=110:y=900:w=260:h=12:color=0xA84A3B@0.95:t=fill:enable='gte(t,0.4)',
drawbox=x=370:y=900:w=260:h=12:color=0xA84A3B@0.95:t=fill:enable='gte(t,1.0)',
drawbox=x=630:y=900:w=210:h=12:color=0xA84A3B@0.95:t=fill:enable='gte(t,1.6)',
drawbox=x=108:y=888:w=34:h=34:color=0xA84A3B@0.98:t=fill:enable='gte(t,0.4)',
drawbox=x=610:y=888:w=34:h=34:color=0xA84A3B@0.98:t=fill:enable='gte(t,1.0)',
drawbox=x=830:y=888:w=34:h=34:color=0xA84A3B@0.98:t=fill:enable='gte(t,1.6)',
drawbox=x=70:y=1710:w=940:h=130:color=0x201A15@0.76:t=fill,
drawtext=fontfile='$font':text='$Caption':fontcolor=0xF2E7D2:fontsize=42:x=(w-text_w)/2:y=1755
"@ -replace "`r?`n", ''

& ffmpeg -y `
  -loop 1 -framerate 30 -i (Join-Path $asset 'map-background.png') `
  -loop 1 -framerate 30 -i (Join-Path $asset 'satellite-green.png') `
  -loop 1 -framerate 30 -i (Join-Path $asset 'landmarks-green.png') `
  -loop 1 -framerate 30 -i (Join-Path $asset 'newspapers-green.png') `
  -filter_complex $filter -t 8 -r 30 -c:v libx264 -pix_fmt yuv420p -movflags +faststart $output

Write-Host "Rendered: $output"
