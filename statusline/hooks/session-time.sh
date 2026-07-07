#!/bin/bash
# ─────────────────────────────────────────────────────────
# Session Time Hook · Claude Code Starter Kit #06
# by 雷蒙（Raymond Hou）· https://cc.lifehacker.tw
# License: CC BY-NC-SA 4.0
# ─────────────────────────────────────────────────────────
# 記錄本次 session 最後一則訊息的時間戳（Asia/Taipei）
# macOS 用這個 bash hook；Windows 改用 settings.json 裡的 PowerShell hook
TZ="Asia/Taipei" date '+%Y-%m-%d %H:%M' > ~/.claude/last-session-msg
