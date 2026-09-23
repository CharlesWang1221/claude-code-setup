#!/bin/bash
# 驗證 Codex 與 .agents 相容鏡像沒有偏離 repo Skill 母版。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
CODEX_SKILLS="$HOME/.codex/skills"
AGENTS_SKILLS="$HOME/.agents/skills"

failures=0
checked=0

hash_tree() {
    local root="$1"
    find "$root" -type f ! -name '.DS_Store' -print0 \
        | LC_ALL=C sort -z \
        | xargs -0 shasum -a 256 \
        | sed "s#  $root/#  #" \
        | shasum -a 256 \
        | awk '{print $1}'
}

check_copy() {
    local name="$1"
    local label="$2"
    local deployed="$3"
    local source="$SKILLS_SRC/$name"

    if [[ ! -f "$deployed/SKILL.md" ]]; then
        printf 'MISSING\t%s\t%s\n' "$label" "$name"
        failures=$((failures + 1))
        return
    fi

    if [[ "$(hash_tree "$source")" != "$(hash_tree "$deployed")" ]]; then
        printf 'DIFF\t%s\t%s\n' "$label" "$name"
        failures=$((failures + 1))
        return
    fi

    printf 'MATCH\t%s\t%s\n' "$label" "$name"
}

for dir in "$SKILLS_SRC"/*/; do
    [[ -d "$dir" ]] || continue
    name=$(basename "$dir")
    [[ "$name" == "skill-creator" ]] && continue
    checked=$((checked + 1))
    check_copy "$name" Codex "$CODEX_SKILLS/$name"
    if [[ -e "$AGENTS_SKILLS/$name" ]]; then
        printf 'DUPLICATE\tAgents\t%s\n' "$name"
        failures=$((failures + 1))
    fi
done

if [[ -d "$CODEX_SKILLS/skill-creator" ]]; then
    printf 'WARN\tCodex\tskill-creator 使用者副本存在；應停用並改用 .system 內建版\n'
    failures=$((failures + 1))
fi

if (( failures > 0 )); then
    printf 'FAIL\t檢查 %d 個核心 Skill，發現 %d 個來源問題。停止總控流程。\n' "$checked" "$failures" >&2
    exit 1
fi

printf 'PASS\t%d 個核心 Skill 只由 repo 母版部署至 Codex；Claude／.agents 來源未參與。\n' "$checked"
