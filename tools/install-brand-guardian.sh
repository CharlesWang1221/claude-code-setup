#!/usr/bin/env bash
# 在 macOS 上把 repo 內的「阿維」連結給 Claude Code 與 Codex。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_SOURCE="$REPO_ROOT/skills/brand-guardian"

if [[ ! -f "$SKILL_SOURCE/SKILL.md" ]]; then
  echo "找不到 $SKILL_SOURCE/SKILL.md，請先在 repo 根目錄完成 git pull。" >&2
  exit 1
fi

mkdir -p "$HOME/.claude/skills" "$HOME/.agents/skills"
ln -sfn "$SKILL_SOURCE" "$HOME/.claude/skills/brand-guardian"
ln -sfn "$SKILL_SOURCE" "$HOME/.agents/skills/brand-guardian"

echo "阿維已連結給 Claude Code 與 Codex。請開啟新的對話後使用：阿維，檢查這份內容。"
