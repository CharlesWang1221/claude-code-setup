#!/bin/bash
# 從 repo 母版同步核心 Skills 到 Codex。
# 不讀取 ~/.claude/skills、~/.claude.json 或 Claude MCP 設定。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
CODEX_SKILLS="$HOME/.codex/skills"

GREEN='\033[0;32m'
GRAY='\033[0;90m'
NC='\033[0m'

echo "=== 同步 Skills（repo → Codex）==="
mkdir -p "$CODEX_SKILLS"

for dir in "$SKILLS_SRC"/*/; do
    [[ -d "$dir" ]] || continue
    name=$(basename "$dir")

    if [[ "$name" == "skill-creator" ]]; then
        echo -e "${GRAY}  跳過 skill-creator：Codex 固定使用內建版${NC}"
        continue
    fi

    mkdir -p "$CODEX_SKILLS/$name"
    rsync -a --delete "$dir"/ "$CODEX_SKILLS/$name/"
    echo -e "${GREEN}  已同步: $name${NC}"
done

echo ""
"$SCRIPT_DIR/isolate-legacy-skills.sh"
"$SCRIPT_DIR/check-skill-authority.sh"
echo -e "${GREEN}=== 完成：Claude Skills 與 Claude MCP 未讀取、未同步 ===${NC}"
