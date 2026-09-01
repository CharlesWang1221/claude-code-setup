# 文件治理規則

本文件定義 repo 內 Markdown 的權威、主責與生命週期。目的不是把所有檔案集中管理，而是防止舊任務紀錄、重複 Skill 或相容性文件，偷偷變成新的規則來源。

## 1. 衝突時的權威順序

同一問題有多份文件時，依下列順序裁決。低層文件不得覆蓋高層文件；若高層規則不夠具體，才由低層補足執行細節。

1. `AGENTS.md`：全域工作、發布、安全與代理行為規則。
2. `BRAND_CONTEXT.md`：心維空間、《不標準答案》與 We I 的品牌判斷。
3. `DESIGN.md`：視覺色彩、字體與元件的實際規格。
4. `docs/CEO_CONTROL_TOWER.md`：任務調度、主管權責與內容營運閘門。
5. 對應 `skills/*/SKILL.md`：專業流程與工具使用法。
6. 專案目錄內的 `AGENTS.md`、`BRIEF.md`、`STORYBOARD.md`：單一專案的限制與目標。
7. 任務產物、QC、日記、發布內容與技術說明：紀錄或證據，不具有規則覆蓋權。

品牌紅線、公開範圍、安全與最終發布決定，仍由老查保留最終裁決權。任何文件都不能授權 AI 自動對外發布。

## 2. 文件類別與主責

| 類別 | 目前範圍 | 權威與主責 | 更新觸發 | 管理規則 |
| --- | --- | --- | --- | --- |
| A. 憲法母版 | 根目錄 `AGENTS.md`、`BRAND_CONTEXT.md`、`DESIGN.md`；`docs/CEO_CONTROL_TOWER.md`、`CEO_COMMAND_PROTOCOL.md`、`SKILL_ROUTING_MATRIX.md`、`AUTHORITY_MATRIX.md`、本檔、`docs/RULE_CHANGELOG.md` | CEO 主責；品牌總監共同把關品牌文件 | 規則重複出錯、跨電腦失效、品牌決策改變 | 改前寫明觸發事件、影響範圍、例外與驗證；不可放私人資料 |
| B. 產線規則 | `skills/*/SKILL.md`、`skills/*/references/*.md`、`tools/*/SKILL.md`、`docs/SKILL_HEALTH_REGISTER.md` | 對應主管擁有內容；系統與資產總監管版本 | SOP 已驗證改善、工具 API／流程變動、A 級規則調整 | 每次執行先讀完整主 Skill；references 只補細節，不得另立最高規則 |
| C. 任務控制文件 | `docs/ACTIVE_TASK_REGISTER.md`、`docs/RELEASE_EVIDENCE_REGISTER.md`、`docs/PROJECT_CONTROL_TEMPLATE.md`、`docs/CEO_PILOT_LOG_*.md`、`video-projects/*/AGENTS.md`、`BRIEF.md`、`STORYBOARD.md`、`frame.md`、`HANDOFF.md`；`output/ep-*/content-decision.md`、`brand-review.md`、`asset-manifest.md`、`*-qc.md` | 內容營運長主責；製作總監管成片；品牌總監管放行 | 任務建立、階段移轉、版本變更、交接或結案 | 必須標示狀態、最終版本、主責與下一步；只對該任務有效 |
| D. 成果與知識資產 | `output/*/show-notes.md`、`performance-review-*.md`、`output/podcast-performance-patterns.md`、`site/src/content/blog/*.md` | 成長與知識總監；已發布內容由品牌總監協作 | 發布、修訂、更正、7／30 天復盤 | 保留來源、發布狀態與可驗證數據；不以後見之明改寫當時紀錄 |
| E. 技術與系統文件 | 各 `README.md`、`mcp-setup.md`、`apps/creator-os/docs/*.md`、`tools/*/README.md`、`blender-projects/*/README.md` | 系統與資產總監；子專案 owner 負責細節 | 安裝、部署、環境、資料結構或工具介面改變 | 記錄可重現步驟與非機敏設定；帳密、token、私人路徑禁止入庫 |
| F. 私人與歷史紀錄 | `journals/*.md`、`s2ep12-snapshot.md`、已結案專案日誌 | 老查擁有；CEO 僅索引與引用 | 老查要求整理、結案或需要提煉規則 | 不列入日常待辦；僅在有明確用途時提煉去識別規則 |
| G. 輔助執行端文件 | 根目錄與子專案的 `CLAUDE.md` | 系統與資產總監 | Codex 母版規則或 Claude 專屬操作改變 | 可保留 Claude 的相容、記憶與工具說明；共用規則須與 Codex 同步，衝突時以 A 級 Codex 文件為準 |

## 3. 文件生命週期

| 狀態 | 適用文件 | 必填欄位或訊號 | 可做的事 |
| --- | --- | --- | --- |
| `ACTIVE` | A、B、進行中的 C、E | owner、最後確認日、適用範圍 | 可作為目前工作依據 |
| `PENDING_APPROVAL` | 對外內容、品牌審查、發布或重大規則改動 | 待誰核准、阻塞原因、下一步 | 可修訂，不得宣稱完成 |
| `LOCKED` | 最終成片 QC、已發布內容、已排程資產 | 最終檔名／網址／排程證據 | 任何改動都產生新版本並重驗收 |
| `ARCHIVED` | 結案的 C、舊版本與歷史紀錄 | 結案日、後續參考價值 | 只讀參考，不得當現行規則 |
| `DEPRECATED` | 被母版取代的 Skill、文件或工具說明 | 取代文件與日期 | 不再引用；保留至確認無相依後再處理 |

Markdown 不必全部新增 frontmatter。只有 C 級任務控制文件，必須在文件開頭或同目錄 `HANDOFF.md` 清楚留下狀態、owner、最後更新日、最終版本與下一步。

## 4. 單一母版與重複控制

- Codex 的全域規則唯一母版是根目錄 `AGENTS.md`。`CLAUDE.md` 可保留並記錄 Claude 專屬的相容、記憶與工具說明；共用規則必須同步，若兩者衝突，以 `AGENTS.md` 為準。
- 品牌規則唯一母版是 `BRAND_CONTEXT.md`。Skill 只能引用或落地，不可重寫品牌憲法。
- 視覺實際規格唯一母版是 `DESIGN.md`。單一專案可以加本次畫面限制，但不得私改品牌色碼與字體規則。
- 每個 Skill 的 repo 版 `skills/<skill-name>/SKILL.md` 是可同步的母版；使用者家目錄的安裝版是部署產物，不是修改來源。
- `tools/video-use` 與其內嵌 Skill 是外部工具文件。除非 CEO 明確決定接管，不能與 repo 的同名 Skill 互相覆蓋。

發現重複規則時，CEO 不直接刪除。先判斷哪份是母版、哪些是引用、哪些是歷史版本；更新引用後，將被取代文件標記為 `DEPRECATED`，再由老查決定是否清理。

## 5. 內容營運長的文件責任

每一集 Podcast 或跨平台內容至少建立或確認下列控制文件：

| 文件 | 用途 | 最低完成條件 |
| --- | --- | --- |
| `content-decision.md` | 金句、標題、平台內容決策 | 原話時間碼、選擇理由、已知風險 |
| `brand-review.md` | 對外素材的品牌放行 | 明確 `ALLOW`／`REVISE`／`REJECTED` 與版本 |
| `asset-manifest.md` | 素材、成片與平台資產清單 | 最終檔名、位置、用途、版本狀態 |
| `*-qc.md` | 影片／圖像的驗收證據 | 對應最終檔名、驗收項目、抽格或畫面證據 |
| `show-notes.md` | Podcast 平台文案 | 已放行版本、平台狀態與公開範圍 |
| `HANDOFF.md` | 跨日或跨工作階段交接 | 目標、已完成、狀態、阻塞、下一步、驗證與避坑 |

不是每集都必須新建所有檔案。沒有使用剪紙精華，就不需要 QC 文件；沒有跨日交接，就不需要 `HANDOFF.md`。但已有的文件必須被更新，不能讓舊版假裝仍是最後版本。

## 6. 每月文件盤點

系統與資產總監每月或重大流程變更後，回報一次：

```text
【文件治理盤點｜YYYY-MM-DD Asia/Taipei】
新增的 A／B 級母版：
需要同步的 Skill：
ACTIVE 任務控制文件：
可 ARCHIVE 的結案文件：
疑似重複或衝突文件：
機敏資訊與公開 repo 風險：
需要老查裁決：
```

盤點是索引與風險報告，不是自動清理授權。涉及刪除、搬移、合併歷史文件或改公開內容時，必須先取得老查明確指示。
