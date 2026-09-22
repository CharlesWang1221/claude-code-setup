#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "用法：$0 <來源檔> <輸出 Markdown> [--force]" >&2
  exit 2
fi

source_file="$1"
output_file="$2"
force="${3:-}"

if [[ ! -f "$source_file" ]]; then
  echo "找不到來源檔：$source_file" >&2
  exit 1
fi

if [[ -e "$output_file" && "$force" != "--force" ]]; then
  echo "輸出檔已存在：$output_file。確認覆蓋時加上 --force。" >&2
  exit 1
fi

mkdir -p "$(dirname "$output_file")"
python3 -m markitdown "$source_file" -o "$output_file"
echo "已建立 Markdown：$output_file"
