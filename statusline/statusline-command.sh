#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Claude Code Status Line · Starter Kit #06
# ═══════════════════════════════════════════════════════════════
# Designed by 雷蒙（Raymond Hou）
# Source: https://github.com/Raymondhou0917/claude-code-resources
# Docs: https://cc.lifehacker.tw
# License: CC BY-NC-SA 4.0 · 個人使用自由；禁止商業用途
# ═══════════════════════════════════════════════════════════════
# 想改顯示什麼？下面這幾行 true/false 切換就好。

# ── 顯示開關（把 true 改 false 就能關閉對應欄位） ──
EMOJI_STR=""
SHOW_MODEL=true
SHOW_CONTEXT_BAR=true
SHOW_RATE_5H=true
SHOW_RATE_7D=true
SHOW_GIT_BRANCH=true
SHOW_GIT_DIFF=true
SHOW_PROJECT=true
SHOW_LAST_MSG=true # 顯示「最後一則訊息的時間」（需要 hooks/session-time.sh 或 PowerShell hook 支援）
LAST_MSG_FILE="$HOME/.claude/last-session-msg"

# ── 確保 jq 可被找到（跨平台）──
if ! command -v jq &>/dev/null; then
  # macOS Homebrew（Apple Silicon: /opt/homebrew/bin、Intel: /usr/local/bin）
  for d in "/opt/homebrew/bin" "/usr/local/bin"; do
    [ -x "$d/jq" ] && export PATH="$PATH:$d" && break
  done
  # Windows WinGet（Git Bash 路徑格式）
  if ! command -v jq &>/dev/null; then
    for d in /c/Users/*/AppData/Local/Microsoft/WinGet/Links; do
      [ -x "$d/jq.exe" ] && export PATH="$PATH:$d" && break
    done
  fi
fi

# ── 顏色定義（依 Claude Code 主題自動切換） ──
_THEME=$(jq -r '.theme // empty' ~/.claude.json 2>/dev/null)
[ -z "$_THEME" ] && _THEME=$(jq -r '.theme // "dark"' ~/.claude/settings.json 2>/dev/null)
if [[ "$_THEME" == *"light"* ]]; then
  WH=$'\033[38;2;40;40;40m'
  GR=$'\033[38;2;20;120;20m'
  YL=$'\033[38;2;160;100;0m'
  OG=$'\033[38;2;180;80;0m'
  RD=$'\033[38;2;160;20;10m'
  MD=$'\033[38;2;140;80;10m'
  DM=$'\033[38;2;110;110;110m'
else
  WH=$'\033[97m'
  GR=$'\033[38;2;80;200;81m'
  YL=$'\033[38;2;255;235;59m'
  OG=$'\033[38;2;255;152;0m'
  RD=$'\033[38;2;244;67;54m'
  MD=$'\033[38;2;246;184;90m'
  DM=$'\033[90m'
fi
RS=$'\033[0m'
SEP="${DM} │ ${RS}"

input=$(cat)

# ── 解析 Claude Code 傳來的 JSON ──
model=$(echo "$input" | jq -r '.model.display_name // ""')
remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
rl_5h=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
rl_5h_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
rl_7d=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
rl_7d_reset=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

# ══════ LINE 1 ══════
L1=""
[ -n "$EMOJI_STR" ] && L1="${EMOJI_STR} "

# 模型名稱
if $SHOW_MODEL && [ -n "$model" ]; then
  L1="${L1}${SEP}${MD}${model}${RS}"
fi

# Context 漸層進度條
if $SHOW_CONTEXT_BAR && [ -n "$remaining" ]; then
  pct=$(printf '%.0f' "$remaining")
  used=$((100 - pct))
  BAR_W=12
  filled=$(( used * BAR_W / 100 ))
  z1=$(( BAR_W / 4 )); z2=$(( BAR_W / 2 )); z3=$(( BAR_W * 3 / 4 ))
  bar=""
  for ((n=0; n<BAR_W; n++)); do
    if (( n < filled )); then
      if   (( n < z1 )); then bar="${bar}${GR}█${RS}"
      elif (( n < z2 )); then bar="${bar}${YL}█${RS}"
      elif (( n < z3 )); then bar="${bar}${OG}█${RS}"
      else                    bar="${bar}${RD}█${RS}"
      fi
    else
      bar="${bar}${DM}░${RS}"
    fi
  done
  L1="${L1}${SEP}${bar} ${WH}${pct}%${RS}"
fi

# 5 小時額度
if $SHOW_RATE_5H && [ -n "$rl_5h" ]; then
  used_pct=$(printf '%.0f' "$rl_5h")
  left_pct=$(( 100 - used_pct ))
  countdown=""
  if [ -n "$rl_5h_reset" ]; then
    now=$(date +%s)
    diff=$(( rl_5h_reset - now ))
    if (( diff > 0 )); then
      h=$(( diff / 3600 ))
      m=$(( (diff % 3600) / 60 ))
      countdown="${h}H${m}m"
    else
      countdown="soon"
    fi
  fi
  label="${countdown:+${countdown} }${left_pct}%"
  L1="${L1}${SEP}${DM}5h:${RS}${WH}${label}${RS}"
fi

# 7 天額度
if $SHOW_RATE_7D && [ -n "$rl_7d" ]; then
  used_pct=$(printf '%.0f' "$rl_7d")
  left_pct=$(( 100 - used_pct ))
  countdown=""
  if [ -n "$rl_7d_reset" ]; then
    now=$(date +%s)
    diff=$(( rl_7d_reset - now ))
    if (( diff > 0 )); then
      d=$(( diff / 86400 ))
      h=$(( (diff % 86400) / 3600 ))
      countdown="${d}D${h}H"
    else
      countdown="soon"
    fi
  fi
  label="${countdown:+${countdown} }${left_pct}%"
  L1="${L1}${SEP}${DM}7d:${RS}${WH}${label}${RS}"
fi

# ══════ LINE 2 ══════
L2=""
git_top=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -n "$git_top" ] && git -C "$git_top" rev-parse HEAD >/dev/null 2>&1; then
  if $SHOW_GIT_BRANCH; then
    br=$(git branch --show-current 2>/dev/null)
    if [ -n "$br" ]; then
      dirty=""
      git diff-index --quiet HEAD -- 2>/dev/null || dirty="*"
      [ -z "$dirty" ] && [ -n "$(git ls-files --others --exclude-standard 2>/dev/null | head -1)" ] && dirty="*"
      L2="${WH}${br}${dirty}${RS}"
    fi
  fi

  if $SHOW_GIT_DIFF; then
    stat=$(git diff --shortstat HEAD 2>/dev/null)
    ins=$(echo "$stat" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
    del=$(echo "$stat" | grep -oE '[0-9]+ deletion' | grep -oE '[0-9]+')
    if [ -n "$ins" ] || [ -n "$del" ]; then
      ds=""
      [ -n "$ins" ] && ds="${GR}+${ins}${RS}"
      [ -n "$ins" ] && [ -n "$del" ] && ds="${ds}${DM}/${RS}"
      [ -n "$del" ] && ds="${ds}${RD}-${del}${RS}"
      [ -n "$L2" ] && L2="${L2}${SEP}${ds}" || L2="${ds}"
    fi
  fi

  if $SHOW_PROJECT; then
    pname=$(basename "$git_top")
    if [ -n "$pname" ]; then
      [ -n "$L2" ] && L2="${L2}${SEP}${WH}${pname}${RS}" || L2="${WH}${pname}${RS}"
    fi
  fi
fi

# 最後訊息時間（從 hook 寫入的檔案讀取）
if $SHOW_LAST_MSG && [ -f "$LAST_MSG_FILE" ]; then
  last_msg=$(cat "$LAST_MSG_FILE" 2>/dev/null)
  if [ -n "$last_msg" ]; then
    [ -n "$L2" ] && L2="${L2}${SEP}${DM}📝 ${last_msg}${RS}" || L2="${DM}📝 ${last_msg}${RS}"
  fi
fi

# ══════ 輸出 ══════
printf '%s\n' "$L1"
[ -n "$L2" ] && printf '%s\n' "$L2"
