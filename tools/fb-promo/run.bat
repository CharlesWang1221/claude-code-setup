@echo off
REM FB 預告影片完整 Pipeline (Windows)
REM 用法: tools\fb-promo\run.bat <episode_dir>
REM 範例: tools\fb-promo\run.bat video-projects\s2ep7-short

setlocal enabledelayedexpansion

set EP_DIR=%~1
if "%EP_DIR%"=="" (
  echo Usage: tools\fb-promo\run.bat ^<episode_dir^>
  exit /b 1
)

set SCRIPT_DIR=%~dp0
for %%i in ("%EP_DIR%") do set EP_ABS=%%~fi
for %%i in ("%EP_DIR%") do set EP_BASENAME=%%~ni

REM Remove -short suffix for output naming
set EP_NAME=%EP_BASENAME:-short=%

echo === FB 預告 Pipeline: %EP_NAME% ===
echo Episode dir: %EP_ABS%
echo.

REM Check source file
if not exist "%EP_ABS%\03-edited\edited.mp4" (
  echo ERROR: %EP_ABS%\03-edited\edited.mp4 not found
  exit /b 1
)

REM Step 1 — Get duration
echo [1/4] 讀取音訊時長...
for /f "delims=" %%d in ('python -c "import subprocess,json;r=subprocess.run(['ffprobe','-v','quiet','-show_format','-print_format','json',r'%EP_ABS%\03-edited\edited.mp4'],capture_output=True,text=True);print(json.loads(r.stdout)['format']['duration'])"') do set DURATION=%%d
echo Duration: %DURATION%s

REM Step 2 — Build HTML
set TMP_HTML=%TEMP%\fb_promo_%EP_NAME%.html
echo [2/4] 產生 HTML (%TMP_HTML%)...
python "%SCRIPT_DIR%build_html.py" "%EP_ABS%" "%TMP_HTML%"

REM Step 3 — Capture frames
set FRAMES_DIR=%TEMP%\fb_promo_frames_%EP_NAME%
echo [3/4] Puppeteer 抓幀 (%FRAMES_DIR%)...
pushd "%SCRIPT_DIR%"
node capture_frames.mjs "%TMP_HTML%" "%FRAMES_DIR%" %DURATION%
popd

REM Step 4 — FFmpeg compile
if not exist "%EP_ABS%\06-publish" mkdir "%EP_ABS%\06-publish"
set OUTPUT=%EP_ABS%\06-publish\%EP_NAME%_reels_vertical.mp4
echo [4/4] FFmpeg 合成 → %OUTPUT%
ffmpeg -y ^
  -framerate 24 -i "%FRAMES_DIR%\frame_%%05d.png" ^
  -i "%EP_ABS%\03-edited\edited.mp4" ^
  -map 0:v -map 1:a ^
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p ^
  -c:a aac -b:a 128k -shortest ^
  "%OUTPUT%"

echo.
echo === 完成 ===
echo 輸出: %OUTPUT%
echo.
echo 清理暫存...
rmdir /s /q "%FRAMES_DIR%"
echo Done!
