#!/usr/bin/env bash
# Voicebox（本機聲音複製）Mac 安裝
# 用法：./tools/install-voicebox.sh [版本，預設 0.5.0]
# 聲音樣本與聲音檔只存在本機 App 資料夾，不得放進本 repo（公開）。
set -euo pipefail
VERSION="${1:-0.5.0}"

if [ -d "/Applications/Voicebox.app" ]; then
  echo "已安裝：/Applications/Voicebox.app"; exit 0
fi

case "$(uname -m)" in
  arm64) ARCH="aarch64" ;;
  *)     ARCH="x64" ;;
esac
NAME="Voicebox_${VERSION}_${ARCH}.dmg"
URL="https://github.com/jamiepine/voicebox/releases/download/v${VERSION}/${NAME}"
DEST="${TMPDIR:-/tmp}/${NAME}"

[ -f "$DEST" ] || { echo "下載 $URL（約 520 MB）"; curl -L --fail -o "$DEST" "$URL"; }

MNT="$(mktemp -d)"
hdiutil attach "$DEST" -nobrowse -quiet -mountpoint "$MNT"
cp -R "$MNT/Voicebox.app" /Applications/
hdiutil detach "$MNT" -quiet
echo "完成：/Applications/Voicebox.app"
echo "首次開啟若被 Gatekeeper 擋下：系統設定 → 隱私權與安全性 → 仍要打開。"
echo "Apple Silicon 走 MLX，不需 CUDA；首次開啟會下載語音模型。"
