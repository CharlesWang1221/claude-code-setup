---
name: project-statusline-setup
description: Claude Code 狀態列（雷蒙完整版）已安裝的設定檔位置與功能說明，換電腦時需要一起還原
metadata: 
  node_type: memory
  type: project
  originSessionId: 3276c960-ebc6-4694-9965-6a3aaeb54cde
---

## 已安裝的狀態列（雷蒙 Starter Kit #06）

來源：https://raw.githubusercontent.com/Raymondhou0917/claude-code-resources/refs/heads/master/starter-kit/06-statusline.md

**Why:** 老查希望 Claude Code 底部常駐顯示模型、Context 用量、Git 狀態、最後對話時間，不用每次打指令查。

**How to apply:** 換電腦或重裝環境時，這幾個檔案需要一起還原。老查說「狀態列跑掉了」「status line 沒了」時，直接重跑安裝流程。

---

## 安裝的檔案

| 檔案路徑 | 用途 |
|---|---|
| `~/.claude/statusline-command.sh` | 主腳本，Claude Code 每次重繪狀態列時執行 |
| `~/.claude/hooks/session-time.sh` | 備用 bash hook（實際用 PowerShell hook） |

## settings.json 加了什麼

- `statusLine.command` → `bash ~/.claude/statusline-command.sh`
- `hooks.UserPromptSubmit` → PowerShell 指令，每次送訊息時把台灣時間寫入 `~/.claude/last-session-msg`

## 顯示內容（雷蒙完整版 + 無 Emoji）

**第一行**：模型名稱 │ Context 漸層進度條 │ 5h 額度剩餘 │ 7d 額度剩餘

**第二行**：Git 分支（有改動顯示 `*`）│ +N/-N 行數 │ 專案名稱 │ 📝 最後訊息時間（Asia/Taipei）

## Windows 特殊處理

- `jq` 透過 winget 安裝，路徑 `C:\Users\siming_wang\AppData\Local\Microsoft\WinGet\Links\jq.exe`
- statusline 腳本頂部有 PATH 補丁讓 Git Bash 找到 jq
- 時間戳用 PowerShell hook 寫入（避免 Git Bash TZ 問題），`-Encoding UTF8NoBOM` 避免 BOM 字元

## 想調整顯示

打開 `~/.claude/statusline-command.sh`，最上面的 `true`/`false` 切換：
```bash
SHOW_MODEL=true
SHOW_RATE_7D=false  # 不看週額度就關
EMOJI_STR="🎯🔥"   # 加 emoji 改這行
```
