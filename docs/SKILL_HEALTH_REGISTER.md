# Skill 健康檢查表

檢查時間：2026-09-01 10:41（Asia/Taipei）  
repo Skill 母版：`skills/<skill-name>/SKILL.md`。  
比較方式：比對 `SKILL.md` 的 SHA-256；`MATCH` 代表與 repo 母版一致，`DIFF` 代表內容不同，`MISSING` 代表路徑不存在。

`Codex` 是主要執行端，`Claude` 與 `.agents` 是輔助／相容端。`DIFF` 不自動表示錯誤，但在啟動該 Skill 前，必須先確認是本機修補還是版本漂移；不得反向以本機版覆蓋 repo 母版。

## repo 核心 Skill 同步狀態

| Skill | repo 母版 | Codex | Claude | Agents mirror | 判定與下一步 |
| --- | --- | --- | --- | --- | --- |
| animation-director | `skills/animation-director` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待下次同步確認。 |
| blog-image-director | `skills/blog-image-director` | `MATCH` | `MISSING` | `MISSING` | Codex 可用；若 Claude 要做網誌圖，先跑同步。 |
| brand-guardian | `skills/brand-guardian` | `MATCH` | `DIFF` | `MATCH` | Codex 可用；Claude 版待確認。 |
| chibi-ink-illustrations | `skills/chibi-ink-illustrations` | `MATCH` | `MISSING` | `MISSING` | Codex 可用；輔助端未部署。 |
| daily-routines-manager | `skills/daily-routines-manager` | `MATCH` | `MATCH` | `MATCH` | 健康。 |
| fact-checker | `skills/fact-checker` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| paper-collage-video | `skills/paper-collage-video` | `DIFF` | `DIFF` | `DIFF` | 高風險漂移。下次剪紙任務前先比較差異，再決定是否同步。 |
| podcast-audio-edit | `skills/podcast-audio-edit` | `MATCH` | `MISSING` | `MISSING` | Codex 可用；輔助端未部署。 |
| podcast-performance-review | `skills/podcast-performance-review` | `MATCH` | `MISSING` | `MISSING` | Codex 可用；輔助端未部署。 |
| podcast-publish | `skills/podcast-publish` | `DIFF` | `DIFF` | `DIFF` | 高風險漂移。下次上架前先比較差異，再決定是否同步。 |
| podcast-teaser-video | `skills/podcast-teaser-video` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| short-video-experiment-review | `skills/short-video-experiment-review` | `MATCH`（2026-09-01 手動同步） | `MISSING` | `MISSING` | 新增短片產前／7 天驗證閘門。Mac 端下次執行 `./setup.sh` 後要重新比對。 |
| presentation-architect | `skills/presentation-architect` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| seo-article-writer | `skills/seo-article-writer` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| shorts-pipeline | `skills/shorts-pipeline` | `MATCH` | `MATCH` | `MATCH` | 健康。 |
| skill-creator | `skills/skill-creator` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| video-explainer | `skills/video-explainer` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| video-promo | `skills/video-promo` | `MATCH` | `MATCH` | `MATCH` | 健康。 |
| voc-jtbd-demand-map | `skills/voc-jtbd-demand-map` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |

## 外部與內建 Skill

| Skill 群組 | Codex | Claude／Agents | 母版與處理方式 |
| --- | --- | --- | --- |
| `video-shotcraft` | `MISSING` | `PRESENT` | 第三方外部 Git Skill。目前不是 Codex 可直接啟動的本機部署；若要用，先以外部來源同步到 Codex，不以 Claude 版當母版。 |
| HyperFrames、`media-use`、`general-video`、`talking-head-recut`、`motion-graphics`、`ui-ux-pro-max` | `PRESENT` | 多數 `PRESENT` | 屬安裝或系統提供能力，不在 repo 核心 Skill 比對範圍；使用時仍依當前完整 `SKILL.md`。 |
| `social-cards`、`landing`、`brainstorm`、`learning-journal` 等 | 本次 session 可用，但本機 repo 無母版 | Agents 路徑可見部分項目 | 需另立外部／個人 Skill 來源清冊；未確認母版前，不將本機副本回寫 repo。 |

## 健康門檻與處理順序

- `GREEN`：Codex `MATCH`，可依 repo 母版啟動。
- `YELLOW`：Codex `MATCH`，但輔助端 `DIFF` 或 `MISSING`。不阻擋 Codex，Claude 任務前先同步或確認。
- `RED`：Codex `DIFF` 或 `MISSING`。本次為 `paper-collage-video`、`podcast-publish` 與 `video-shotcraft`；啟動前必須先比對或部署。

每月、換機、執行 `setup.ps1`／`setup.sh` 後，以及任何 `RED` Skill 的任務前，都要重新檢查。本表記錄結果，不授權直接覆蓋本機 Skill；同步動作需由 CEO 確認來源與影響後執行。

## 2026-09-01 同步事故

- Windows `setup.ps1` 在第 62、106、155 行出現 `Unexpected token '}'`，本次未完成整包同步。此錯誤仍待修復，不得宣稱 Windows 換機可直接靠該腳本恢復環境。
- 為讓本次制度先可用，已手動同步 `short-video-experiment-review`、`podcast-publish`、`podcast-performance-review` 到 Codex 本機 Skill 目錄。
- repo `skills/` 仍是唯一母版。Mac 端必須先驗證 `./setup.sh` 是否包含並成功複製新 Skill；成功後以 SHA-256 重新更新本表。

## 2026-09-28 11:52（Asia/Taipei）實透與週節奏部署複核

本次僅更新 `shi-tou`、`podcast-publish`、`paper-collage-video` 的部署；保留上方歷史盤點，不以舊表判斷本次狀態。

| Skill | repo → Codex | 驗證 |
| --- | --- | --- |
| shi-tou（實透） | `MATCH` | 新建母版、UI 名稱與腳本交接模板；結構驗證通過 |
| podcast-publish（星期天） | `MATCH` | 新狀態模板 JSON 可解析：2 支實透＋1 支剪紙；獨立流程檢查無重大矛盾 |
| paper-collage-video | `MATCH` | 每週 1 支；保留原有素材庫與動畫規則 |

`tools/check-skill-authority.sh` 回傳 `PASS`，19 個核心 Skill repo 母版與 Codex 整棵目錄一致，未參與 `.agents`／Claude 反向同步。新流程尚未完成完整音檔至發布的實作驗證；本次未消耗 Flow 點數或改動平台排程。

## 2026-09-28 12:02（Asia/Taipei）油管獨立部署複核

`you-guan`（油管）新建、`podcast-publish`（星期天）拆除長片工作，兩者 repo → Codex 整樹 `MATCH`。結構驗證與兩份狀態模板 JSON 檢查通過；星期天報告維持 16 項，長片不列為完成或阻塞條件，YouTube Shorts 仍保留。

`tools/check-skill-authority.sh` 回傳 `PASS`，20 個核心 Skill 母版與 Codex 一致。既有媒體、任務 ID、平台排程與發布證據未改動；本次未生成、渲染或上傳長片。油管完整實作驗證留待下一次長片交辦。

## 2026-10-04（Asia/Taipei）小渡逐支 brief 停止線部署複核

已同步 `community-operations`、`podcast-publish`、`shi-tou` 與 `paper-collage-video`。`pwsh -File tools/sync-codex.ps1` 後，`pwsh -File tools/check-skill-authority.ps1` 回傳 `PASS`，22 個核心 Skill 均與 repo 母版 `MATCH`，未使用 Claude 或 `.agents` 同名副本。

星期天狀態模板 JSON 已解析。新規則尚未以新單集跑完整製作驗證；本次未生成、渲染、扣 Flow 點數或操作平台。

## 2026-10-10（Asia/Taipei）Claude 接手前複核

老查授權將 Claude 舊 Skills 與工作規則更新至 Codex 母版，並指定由 Claude 接手另一專案。

- Claude：23 個 repo Skills 整樹 `MATCH`；Codex：22 個核心 Skill 整樹 `MATCH`，`check-skill-authority.sh` 回傳 `PASS`。Codex 的 `skill-creator` 使用內建版，Claude 保留 repo 相容版。
- 新增 `tools/sync-claude.py`；預設只讀，`--apply` 單向部署。暫存目錄實測完成部署並能偵測內容漂移。
- Claude 的全域規則、工作區入口與子專案引用已更新；清除工作區的 21 份舊記憶，移除舊 Skills 目錄 `git pull` 的錯誤同步 hook。私人資料沒有進本 repo。
- 5 個共用 MCP 的 command／args／env 與 Codex 相同，Claude CLI 讀回 Playwright、Cloudflare、Firecrawl、Google Workspace、Plaud 均 `Connected`。此結果只表示連線，未代表外部平台動作或 bot 端到端測試完成。
- 本機 CLI 為 Claude Code 2.1.224；本次未升級程式。已移除的 22 個非母版舊 Skills 不列為 Claude 可用能力，未從 `.agents` 或 Claude 回寫 Codex。

本段是目前部署狀態；上方歷史表只供追溯，不得用舊版 `DIFF`／`MISSING` 作為現況。

## 2026-10-10（Asia/Taipei）PC 同步交付

- 新增 Windows PowerShell 同步入口，共用 Python 引擎可部署全域規則、核心 Skills、可選舊副本清理與指定工作區記憶重建。
- 私人 ZIP 匯入逐檔驗 SHA-256；已實測重跑、已有工作保護、危險路徑與損壞資料拒絕。
- Mac 的來源檢查與 Claude 整樹檢查 PASS；Windows PowerShell 包裝尚未在 PC 實機執行，PC 的 MCP 登入狀態亦待各機驗證。
- 公開 repo 不包含私人 ZIP、品牌原文、雲端個案或 OAuth token。
