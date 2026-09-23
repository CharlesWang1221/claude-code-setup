#!/bin/bash
# 將會與 Codex 母版撞名的舊 Skill 移出自動探索路徑；保留可復原備份。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
RUN_STAMP="$(date '+%Y%m%d-%H%M%S')"
AGENTS_SKILLS="$HOME/.agents/skills"
AGENTS_BACKUP="$HOME/.agents/codex-disabled-skills/$RUN_STAMP"
CODEX_SKILLS="$HOME/.codex/skills"
CODEX_BACKUP="$HOME/.codex/codex-disabled-skills/$RUN_STAMP"

for dir in "$SKILLS_SRC"/*/; do
    [[ -d "$dir" ]] || continue
    name=$(basename "$dir")
    [[ "$name" == "skill-creator" ]] && continue

    if [[ -e "$AGENTS_SKILLS/$name" ]]; then
        mkdir -p "$AGENTS_BACKUP"
        mv "$AGENTS_SKILLS/$name" "$AGENTS_BACKUP/$name"
        printf 'ISOLATED\tAgents\t%s\t%s\n' "$name" "$AGENTS_BACKUP/$name"
    fi
done

if [[ -d "$CODEX_SKILLS/skill-creator" ]]; then
    mkdir -p "$CODEX_BACKUP"
    mv "$CODEX_SKILLS/skill-creator" "$CODEX_BACKUP/skill-creator"
    printf 'ISOLATED\tCodex\tskill-creator\t%s\n' "$CODEX_BACKUP/skill-creator"
fi
