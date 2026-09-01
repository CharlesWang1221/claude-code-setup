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
