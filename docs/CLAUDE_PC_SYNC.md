# Claude Code 與 Codex 跨電腦同步

共用規則與核心 Skills 從這個 repo 單向部署。私人專案資料透過老查指定的私人 Drive 交接，不能放進這個公開 repo。

## PC 更新

在 PC 現有的 repo 目錄開 PowerShell。不要把 Mac 路徑貼進去，也不要為日常更新重跑包含安裝與帳號設定的 `setup.ps1`。

```powershell
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "git pull failed; resolve it before syncing" }
.\tools\sync-claude.ps1
```

這個入口先跑 repo → Codex 的既有同步及來源檢查，再同步 Claude 的 23 個核心 Skills 與全域工作規則。
Python 3.9 以上需已安裝；入口依序偵測 `py -3`、`python3`、`python`。同步後開新的工作階段。既有中文 PowerShell 同步與來源檢查腳本使用 UTF-8 BOM，兼容 Windows PowerShell 5.1。
中文腳本的編碼處理依 [Microsoft 官方文件](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_character_encoding?view=powershell-5.1)。

第一次淘汰舊 Claude Skills 與記憶，可明確加入清理參數：

```powershell
.\tools\sync-claude.ps1 -CleanLegacy -ResetMemory
```

- `-CleanLegacy` 刪除 Claude Skills 目錄中不屬於 repo 的非隱藏資料夾，包括其他外部 Skills；並移除會到 `.claude/skills` 跑 `git pull` 的舊 hook。時間 hook、狀態列與其他設定保留。
- `-ResetMemory` 只清除指定工作區的 Markdown 記憶，預設為 repo 路徑與其上一層；若舊工作區在另一位置，使用 `-MemoryWorkspace "實際舊工作區路徑"`。找不到對應記憶目錄時回報 SKIP，不假裝完成。
- 原始影片、聊天紀錄、MCP、OAuth token 與其他專案不在清理範圍。只讀驗證使用 `.\tools\sync-claude.ps1 -CheckOnly`。

## 聊遇所私人交接包

從老查指定的 Drive「03_AI團隊工作流」取得私人交接 ZIP，下載到 PC。不要上傳或 commit 到這個 repo。

```powershell
.\tools\sync-claude.ps1 -ProjectBundle "$env:USERPROFILE\Downloads\liaoyu-private-handoff-20261010.zip"
```

預設安裝到 repo 上一層的 `projects\liaoyu`。自訂位置使用 `-ProjectDirectory "想使用的專案路徑"`。
安裝工具驗證每個檔案 SHA-256，阻擋路徑穿越與 symlink；遇到已有不同內容的檔案即停止，避免覆蓋 PC 既有進度。
私人專案必須放在這個公開 repo 外；自訂目的地落在 repo 裡時，工具會拒絕匯入。
匯入後在專案目錄啟動 Claude Code，新對話先讀 `HANDOFF.md`、`AGENTS.md` 與 `SOURCES.md`。

交接包記錄的是 Mac 的驗證狀態，不能當成 PC 的成功證據。PC 接手後讀回雲端來源，並更新自己的環境驗證與任務進度。

## 憑證與工具

同步工具不讀取或複製 MCP 憑證，尤其不能搬移 Mac 的 `/opt/homebrew` 執行路徑到 PC。
PC 的 Codex 與 Claude 連線分開檢查；登入與 OAuth 需在 PC 完成：

```powershell
codex mcp list
claude mcp list
```

模型與平台插件不會因同步規則而變成相同能力；先確認 PC 工作階段的實際可用工具。

## Mac 更新

```bash
git pull --ff-only
./tools/sync-codex.sh
python3 tools/sync-claude.py --apply --global-rules
```

完整私人品牌文件、客戶紀錄、個人雲端連結與 token 不加入共用同步包。本 repo 只保存通用方法與不含私人來源的工具。

## 每週六支短片更新（2026-10-10）

Codex 接手先執行 `git pull --ff-only`，成功後執行 `.\tools\sync-codex.ps1`，再開新工作階段。只需 Codex 時不必跑 Claude 同步入口。

先讀 [短片週母版](SHORT_VIDEO_WEEKLY_POLICY.md) 與 [夥伴更新盤點摘要](PARTNER_UPDATE_AUDIT_2026-10-10.md)。新週計畫為六支、包含預告；Flow 只作特別企劃。私人來源與樣片不進公開 repo，PC 需另從私人交接位置取得。
