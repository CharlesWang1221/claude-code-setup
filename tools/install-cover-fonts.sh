#!/usr/bin/env bash
# 安裝短影片封面主標字體到 Mac 使用者字型夾（~/Library/Fonts），不需管理員權限。
# 清單以 DESIGN.md「短影片封面主標字體」為準；全部為 OFL 1.1，可免費商用。
# 重跑安全：已存在的檔案會跳過。只給 Mac 用，Windows 公司電腦不安裝字型。
set -euo pipefail

if [[ "$(uname)" != "Darwin" ]]; then
  echo "只支援 macOS。Windows 製作封面請用 DESIGN.md 的網頁字型載入方式。" >&2
  exit 1
fi

DEST="$HOME/Library/Fonts"
GF="https://raw.githubusercontent.com/google/fonts/main/ofl"
BAKUDAI="https://cdn.jsdelivr.net/gh/max32002/bakudaifont@1.49/tw"

FONTS=(
  "NotoSansTC-Variable.ttf|$GF/notosanstc/NotoSansTC%5Bwght%5D.ttf"
  "NotoSerifTC-Variable.ttf|$GF/notoseriftc/NotoSerifTC%5Bwght%5D.ttf"
  "Huninn-Regular.ttf|$GF/huninn/Huninn-Regular.ttf"
  "LXGWWenKaiTC-Regular.ttf|$GF/lxgwwenkaitc/LXGWWenKaiTC-Regular.ttf"
  "LXGWWenKaiTC-Bold.ttf|$GF/lxgwwenkaitc/LXGWWenKaiTC-Bold.ttf"
  "Bakudai-Regular.ttf|$BAKUDAI/Bakudai-Regular.ttf"
  "Bakudai-Bold.ttf|$BAKUDAI/Bakudai-Bold.ttf"
)

mkdir -p "$DEST"
fail=0
for entry in "${FONTS[@]}"; do
  name="${entry%%|*}"
  url="${entry#*|}"
  if [[ -f "$DEST/$name" ]]; then
    echo "SKIP  $name（已安裝）"
    continue
  fi
  tmp="$(mktemp)"
  if curl -fsSL "$url" -o "$tmp" && [[ -s "$tmp" ]]; then
    mv "$tmp" "$DEST/$name"
    echo "OK    $name"
  else
    rm -f "$tmp"
    echo "FAIL  $name ← $url" >&2
    fail=1
  fi
done

if [[ $fail -ne 0 ]]; then
  echo "有字型下載失敗，請檢查網路或來源網址後重跑。" >&2
  exit 1
fi
echo "完成。已開啟的 App（Keynote、Canva 桌面版等）需重新啟動才會看到新字型。"
