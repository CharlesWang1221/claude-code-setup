---
name: feedback-what-i-can-do
description: 老查已確認我能做的事情清單，包含安裝 Claude Code Starter Kit、設定自動化工具等
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 3276c960-ebc6-4694-9965-6a3aaeb54cde
---

## 我能做的事（老查親測確認）

**Why:** 老查希望我在未來對話開始時知道我們合作過什麼，能主動提供相關服務，不要每次都問「你要我做什麼」。

**How to apply:** 當老查提到相關需求時，主動說「我之前幫你裝過 X，需要的話可以繼續」。

---

### 1. 安裝 Claude Code Starter Kit（任何 GitHub 原始連結）

給我一個 `.md` 檔案的 raw GitHub URL，我會：
- 用 firecrawl_scrape 抓取完整內容
- 解讀 AI 指引區的 Section 流程
- 用 `AskUserQuestion` 跑互動式選單（版本、emoji、時區等）
- 依序執行環境檢查 → 寫入腳本 → 設定 hooks → 驗證

**觸發詞：** 「幫我安裝這裡面的內容」+ GitHub raw URL

---

### 2. 設定 Claude Code 狀態列

已安裝雷蒙完整版 statusline（見 [[project-statusline-setup]]）。
如果跑掉或換電腦，提供同一個 URL 讓我重裝，或我可以直接修改 `~/.claude/statusline-command.sh`。

---

### 3. 建立與管理 settings.json hooks

我能讀取並修改 `~/.claude/settings.json`，包括：
- 新增/移除 `PreToolUse`、`UserPromptSubmit` hooks
- 設定 `statusLine`、`permissions`、`theme` 等

---

### 4. 安裝 Windows 工具（winget）

需要像 `jq` 這類 CLI 工具，我可以用 `winget install` 安裝，並處理 Git Bash PATH 不同步的問題。
