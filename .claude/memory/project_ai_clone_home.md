---
name: project-ai-clone-home
description: /Users/ming/Agent/my-agent 是老查的獨立「AI 分身」母資料夾，2026-07-27 由付費迷你課工具生成，跟 CCoode 工作目錄並存
metadata: 
  node_type: memory
  type: project
  originSessionId: 59a451d0-fa8c-4b9a-b612-77c7f2e5d9ab
---

`/Users/ming/Agent/my-agent`（symlink 常見寫法 `~/Agent/my-agent`）是老查在 2026-07-27 用「AI 分身起始助手 by 阿雷」（雷蒙侯的付費迷你課工具，v1.5）生成的個人知識管理/AI 分身骨架，跟目前的主工作目錄 [[project_working_directory]]（`~/Documents/CCoode`）是**兩套並存、不互通**的系統。

結構：
- `CLAUDE.md` / `AGENTS.md`（同源）：老查的 AI 分身核心規則 — 繁中對話、先給答案再解釋、行動前先給簡要計畫、模糊需求用互動選項澄清（Claude Code 用 AskUserQuestion）
- `000_Agent/memory/MEMORY.md`：跨 session 記憶（截至建立時仍是空模板，尚無偏好/踩坑）
- `000_Agent/knowledge/REPOS.md`：專案路徑索引表，列出 CCoode 底下的三個 repo（claude-code-setup / claude-code-mini-course / claude-code-resources）
- `000_Agent/skills/`：獨立 git repo（`github.com/CharlesWang1221/claude-skills.git`），透過 symlink 接到 `~/.claude/skills` 和專案內 `.agents/skills`；README 明確說明**現有 6 個 skill 仍留在 `CCoode/claude-code-setup/skills/` 原地不動**，這個資料夾只放「未來新建」的 skill
- `100_Todo/`（drafts/projects/archive）、`200_Reference/`（writing-samples/past-work/templates）、`300_Journal/2026-07/`：草稿、寫作範例、每月反思日誌

**Why:** 老查上了雷蒙侯的 Claude Code 迷你課，用課程附的起始助手產生了這套「第二大腦」骨架，目的是要有一個跨專案、跨 session 都能用的個人 AI 分身入口，而不是每次都在特定專案目錄裡重新建立記憶。

**How to apply:** 這套資料夾內容多是剛建立的空模板，實質記憶/偏好還沒長出來，暫不能當作可信資料來源引用。如果老查在其他工作目錄（如 CCoode）提到「AI 分身」「母資料夾」「新對話從哪開始」，指的通常是這個資料夾。若未來這裡的 MEMORY.md 或 REPOS.md 長出實質內容，且跟 CCoode 這邊的記憶系統重複或衝突，要留意兩套記憶尚未整併，需要人工判斷寫哪邊。

## 2026-07-31 補充：claude-skills repo 同步狀況

`000_Agent/skills`（`github.com/CharlesWang1221/claude-skills.git`）當初「搬入既有 skills」時，只有 `analyze-video`、`skill-creator` 兩個真正被 commit + push 過；其餘 5 個（`daily-routines-manager`、`podcast-audio-edit`、`podcast-publish`、`seo-article-writer`、`shorts-pipeline`）+ README.md 只是複製進資料夾、從未進 git，一直是 untracked 狀態，只存在本機。2026-07-31 已補 commit + push（commit `77cf521`），現在 GitHub 上跟本機一致，7 個 skill 都完整。

**Why:** 老查說「換電腦到 mac、同步一下、看 git 有什麼同步的」時發現的落差——這台 Mac 其實不是新機器（`MingdeMacBook-Pro.local`，2026-07-27 已完整設過環境），只是 `claude-code-setup`/`claude-code-mini-course`/`claude-code-resources` 三個 repo 落後遠端（分別落後 6/1/2 個 commit），已直接 fast-forward pull 同步。

**How to apply:** 之後老查說「同步」「換電腦」時：先跑 `gh auth status` / `wrangler whoami` / 逐個 repo `git fetch && git status -sb` 診斷，別假設是全新環境就整套重裝；也順手檢查 `000_Agent/skills` 有沒有 untracked 檔案（代表本機新增的 skill 還沒推上 claude-skills repo）。
