# Claude Code 執行入口

@AGENTS.md

## 共用規則與專案隔離

- `AGENTS.md` 是共用規則唯一母版；本檔只保留 Claude 相容說明，不再複製一套流程。
- Codex 是主要調度端。Claude Code 可依老查指示獨立執行其他專案；先讀該專案的 `AGENTS.md`、README 與 BRIEF，不把 Podcast 的角色或發布節奏套到其他專案。
- 執行本 repo 任務前，依 `docs/DOCUMENT_GOVERNANCE.md` 判斷權威；調度讀 `docs/CEO_COMMAND_PROTOCOL.md`、`docs/SKILL_ROUTING_MATRIX.md` 與 `docs/AUTHORITY_MATRIX.md`。
- 現有任務先讀 `docs/ACTIVE_TASK_REGISTER.md` 與對應 BRIEF／HANDOFF；平台狀態只認 `docs/RELEASE_EVIDENCE_REGISTER.md` 的讀回證據。
- Skills 唯一母版為 repo 的 `skills/`。本機 `~/.claude/skills` 是部署副本；Mac 執行 `python3 tools/sync-claude.py --apply --global-rules`，Windows 執行 `.\tools\sync-claude.ps1`。不得由 Claude 或 `.agents` 反向同步 Codex。
- 全域規則母版是 `codex/AGENTS.global.md`；Mac／Windows 都從 repo 部署至 `~/.claude/CLAUDE.md`。跨電腦流程見 `docs/CLAUDE_PC_SYNC.md`。
- 總控流程先執行來源檢查並取得 PASS：Mac 用 `tools/check-skill-authority.sh`，Windows 用 `tools/check-skill-authority.ps1`；Claude 副本用 Python 同步工具或 Windows 的 `sync-claude.ps1 -CheckOnly` 驗證。任一必要檢查失敗即停止。
- 每次使用 Skill 先讀完整母版；外部／內建能力先查當前可用清單，不因舊文件提到名稱就假裝能用。
- Auto-memory 只存專案補充與待確認事項，不得覆蓋母版、重建舊觸發詞或把舊任務狀態當成現況。
- 連接器、登入與平台狀態以當次實測為準；不依 2026 年 8 月清單宣稱可用。Codex 專屬插件與電腦操作工具不會因複製 Skills 自動出現在 Claude。
- 共用規則異動只修改母版；本檔透過匯入隨之更新。公開 repo 不保存 token、API key、私人記憶或帳號設定。
