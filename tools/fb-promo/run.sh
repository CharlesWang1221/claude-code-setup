#!/usr/bin/env bash
# FB 預告影片完整 Pipeline
# 用法: bash tools/fb-promo/run.sh <episode_dir>
# 範例: bash tools/fb-promo/run.sh video-projects/s2ep7-short

set -e

EP_DIR="${1:?Usage: bash tools/fb-promo/run.sh <episode_dir>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EP_ABS="$(cd "$EP_DIR" && pwd)"
EP_NAME="$(basename "$EP_DIR" | sed 's/-short//')"

echo "=== FB 預告 Pipeline: $EP_NAME ==="
echo "Episode dir: $EP_ABS"
echo ""

# Step 1 — 確認素材
if [ ! -f "$EP_ABS/03-edited/edited.mp4" ]; then
  echo "ERROR: $EP_ABS/03-edited/edited.mp4 not found"
  exit 1
fi

# Step 2 — 取得音訊時長
echo "[1/4] 讀取音訊時長..."
DURATION=$(python3 -c "
import subprocess, json, sys
r = subprocess.run(['ffprobe','-v','quiet','-show_format','-print_format','json','$EP_ABS/03-edited/edited.mp4'], capture_output=True, text=True)
print(json.loads(r.stdout)['format']['duration'])
")
echo "Duration: ${DURATION}s"

# Step 3 — 產生 HTML
TMP_DIR="${TMPDIR:-/tmp}"
TMP_HTML="$TMP_DIR/fb_promo_${EP_NAME}.html"
echo "[2/4] 產生 HTML ($TMP_HTML)..."
python3 "$SCRIPT_DIR/build_html.py" "$EP_ABS" "$TMP_HTML"

# Step 4 — Puppeteer 截圖抓幀
FRAMES_DIR="$TMP_DIR/fb_promo_frames_${EP_NAME}"
echo "[3/4] Puppeteer 抓幀 ($FRAMES_DIR)..."
cd "$SCRIPT_DIR"
node capture_frames.mjs "$TMP_HTML" "$FRAMES_DIR" "$DURATION"
cd - > /dev/null

# Step 5 — FFmpeg 合成
mkdir -p "$EP_ABS/06-publish"
OUTPUT="$EP_ABS/06-publish/${EP_NAME}_reels_vertical.mp4"
echo "[4/4] FFmpeg 合成 → $OUTPUT"
ffmpeg -y \
  -framerate 24 -i "$FRAMES_DIR/frame_%05d.png" \
  -i "$EP_ABS/03-edited/edited.mp4" \
  -map 0:v -map 1:a \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 128k -shortest \
  "$OUTPUT"

SIZE=$(du -sh "$OUTPUT" | cut -f1)
echo ""
echo "=== 完成 ==="
echo "輸出: $OUTPUT ($SIZE)"
echo ""
echo "清理暫存..."
rm -rf "$FRAMES_DIR"
echo "Done!"
