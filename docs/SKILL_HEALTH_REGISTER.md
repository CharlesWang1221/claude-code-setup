# Skill 健康檢查表

檢查時間：2026-09-20 15:54（Asia/Taipei）
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
| podcast-publish | `skills/podcast-publish` | `MATCH`（2026-09-20 SHA-256 複核） | `DIFF` | `DIFF` | Codex 可用；輔助端待下次同步確認。 |
| podcast-teaser-video | `skills/podcast-teaser-video` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| short-video-experiment-review | `skills/short-video-experiment-review` | `MATCH`（2026-09-01 手動同步） | `MISSING` | `MISSING` | 新增短片產前／7 天驗證閘門。Mac 端下次執行 `./setup.sh` 後要重新比對。 |
| presentation-architect | `skills/presentation-architect` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| seo-article-writer | `skills/seo-article-writer` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| shorts-pipeline | `skills/shorts-pipeline` | `MATCH` | `MATCH` | `MATCH` | 健康。 |
| skill-creator | `skills/skill-creator` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |
| jieti | `skills/jieti` | `MATCH` | `待同步` | `待同步` | 2026-10-12 由 `video-explainer`（影碩）改名重寫為解題；Codex 已部署，輔助端待同步。 |
| zhaopai | `skills/zhaopai` | `MATCH` | `待同步` | `待同步` | 2026-10-12 由 `video-promo`（影華）改名重寫為招牌；Codex 已部署，輔助端待同步。 |
| voc-jtbd-demand-map | `skills/voc-jtbd-demand-map` | `MATCH` | `DIFF` | `DIFF` | Codex 可用；輔助端待確認。 |

## 外部與內建 Skill

| Skill 群組 | Codex | Claude／Agents | 母版與處理方式 |
| --- | --- | --- | --- |
| `video-shotcraft` | `MISSING` | `PRESENT` | 2026-10-12 已下架，setup 不再安裝；以下為下架前紀錄。第三方外部 Git Skill。目前不是 Codex 可直接啟動的本機部署；若要用，先以外部來源同步到 Codex，不以 Claude 版當母版。 |
| HyperFrames、`media-use`、`general-video`、`talking-head-recut`、`motion-graphics`、`ui-ux-pro-max` | `PRESENT` | 多數 `PRESENT` | 屬安裝或系統提供能力，不在 repo 核心 Skill 比對範圍；使用時仍依當前完整 `SKILL.md`。 |
| `social-cards`、`landing`、`brainstorm`、`learning-journal` 等 | 本次 session 可用，但本機 repo 無母版 | Agents 路徑可見部分項目 | 需另立外部／個人 Skill 來源清冊；未確認母版前，不將本機副本回寫 repo。 |

## 健康門檻與處理順序

- `GREEN`：Codex `MATCH`，可依 repo 母版啟動。
- `YELLOW`：Codex `MATCH`，但輔助端 `DIFF` 或 `MISSING`。不阻擋 Codex，Claude 任務前先同步或確認。
- `RED`：Codex `DIFF` 或 `MISSING`。目前為 `paper-collage-video` 與 `video-shotcraft`；啟動前必須先比對或部署。`podcast-publish` 已於 2026-09-20 複核為 `MATCH`。

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

## 2026-10-12 15:06（Asia/Taipei）公司控制台能力實測

本次只測兩項執行能力，未啟動內容產線、生成、渲染、寄信、平台操作或外部排程變更。上方 Skill 同步結果仍保留原檢查日期，本次沒有重驗部署。

### 子代理能否再派子代理：PASS

- 小查實際呼叫 `collaboration.spawn_agent`，指定 `agent_type=dispatcher`、`task_name=dispatcher_probe`；原始回應為 `{"task_name":"/root/dispatcher_probe"}`。
- Dispatcher 再實際呼叫同一工具，指定 `agent_type=explorer`、`task_name=readonly_probe`；原始回應為 `{"task_name":"/root/dispatcher_probe/readonly_probe"}`。
- Explorer 唯讀查詢 `docs/CEO_CONTROL_TOWER.md`，讀回第 3 行 `狀態：ACTIVE`（原文以反引號標示 ACTIVE，並載明階段 1 核准日期）與第 99 行 `## 5. 並行製作流程`。

Explorer 使用 `rg -n` 與 `nl -ba`／`sed -n` 查詢；小查另以 `collaboration.list_agents` 讀回三層代理樹，dispatcher 與 explorer 均為 `completed`，explorer 完成訊息包含上述行號與原文。兩個子代理皆未寫檔。

結論：本工作階段已證實 dispatcher 可再派一層 explorer。後續可由阿派直接依派工單開出 worker；仍須遵守預算卡、並行上限與單一寫入者。此次共 3 個代理，未測更深層級、廠長實作或最大並行數；本工作階段工具宣告共 4 個並行槽位，不能外推到所有環境。

### 目前額度／用量可見性：未取得帳戶數值

| 實測入口 | 可讀欄位／實際結果 | 判定 |
| --- | --- | --- |
| 當前工具清單 | 未提供 Codex 帳戶用量、rate-limit 或 `/status` 呼叫工具 | 無法經現有工具直接讀取 |
| `get_goal({})` | `goal=null`、`remainingTokens=null`、`completionBudgetReport=null` | 只有 goal 工具的欄位，沒有有效數值；不代表訂閱剩餘額度 |
| `codex --help`、`codex app-server --help`、`codex debug --help` | 可讀 CLI 指令與選項；未列出獨立的 `status` 或 `usage` 子命令 | help 不提供帳戶用量；未另開模型工作階段 |
| Computer Use 讀取 Codex App | `cua.getApp('com.openai.codex')` 回覆 `Computer Use is not allowed to use the app 'com.openai.codex' for safety reasons.` | 工具安全限制，未讀到 UI；未繞過限制 |
| 工具執行回應 | Shell 執行有 `original_token_count`、`wall_time_seconds`、`exit_code` 等欄位；代理清單有 `agent_name`、`agent_status` | 屬工具輸出估算／執行狀態，不是模型總用量或帳戶扣款 |

[OpenAI 官方文件](https://developers.openai.com/blog/mastering-codex-remote-for-engineering) 說明 `/status` 可顯示工作階段、工作區、context 用量及可用的 rate-limit 資訊。本次已開啟核對該頁，但未能在當前工作階段呼叫 `/status`，因此這些只列為官方描述，不能列為本次讀回的欄位。

結論：本工作階段沒有取得實際 token 用量、剩餘額度百分比、限額重置時間、credits 或金額。省長繼續使用預算卡等級、重做次數與可驗證的付費點數，不得把輸出 token 估算當成精確帳戶用量；本結果也不等於 Codex 所有介面都不支援查用量。

### 後續順序與週報執行端

小查決定選題情報週報由 Codex 每週執行一次：阿派派工、小渡主責、小市提供需求採證，開工前取得省長的 S 預算卡。本次只記錄分工決定，未建立或變更任何排程。

建議下一步先處理階段 2B 的後勤腳本與多利 Skill，再處理階段 2 的解題／招牌。現行每日排程的停用須逐支核對授權；此次尚未實作階段 2 或 2B，也未以小樣驗證產線。

## 2026-10-12 16:35（Asia/Taipei）公司控制台能力複測

本次依老查交辦重新實測兩項能力；只做唯讀查詢與本登記表紀錄，沒有啟動任何產線工作。

### Dispatcher 是否能派 Explorer：PASS

- 小查派出 `dispatcher` `/root/dispatcher_probe2`；Dispatcher 成功再派 `explorer` `/root/dispatcher_probe2/explorer_phase2b`。
- Explorer 唯讀查詢 `docs/CEO_CONTROL_TOWER.md`，確認第 5 行記載階段 2B 已於 2026-10-12 完成，多利轉職為後勤管家，由小查每日第一次回報前觸發、不使用背景排程；第 60–64 行載明 `python3 -I tools/duoli/duoli.py auto` 本機入口。
- Dispatcher 與 Explorer 均完成；沒有派第三層，沒有修改其他檔案。

結論：本次再次證實 Dispatcher 可派一層 Explorer 執行唯讀查詢。這只驗證一層巢狀派工，不代表更深層派工或產線並行已驗證。

### 當前工作階段能否讀取額度／用量：未取得帳戶數值

| 實測入口 | 本次讀到的欄位／結果 | 判定 |
| --- | --- | --- |
| `get_goal({})` | `goal=null`、`remainingTokens=null`、`completionBudgetReport=null` | 有欄位名稱，沒有本次用量或訂閱額度數值 |
| 可用工具清單 | 沒有 Codex 帳戶用量、rate-limit、credits 或 `/status` 查詢工具 | 此工作階段無直接帳戶讀取入口 |
| `codex --help` | 列出 `agents`、`exec`、`login`、`doctor` 等子命令；沒有 `status`／`usage` 子命令 | CLI help 不能讀出帳戶額度；當前 shell 也不是互動式 Codex CLI 工作階段，故不能在此輸入 `/status` |
| Shell 執行回應 | 可見 `original_token_count`、`wall_time_seconds`、`exit_code` | 僅為工具執行輸出與耗時，不是模型總用量或帳戶扣款 |
| 代理清單 | 可見 `agent_name`、`agent_status` | 只反映代理執行狀態 |

[OpenAI 官方文件](https://developers.openai.com/blog/mastering-codex-remote-for-engineering) 說明 `/status` 能顯示工作階段、工作區、context 用量與可用的 rate-limit 資訊；這些是官方描述，不是本次成功讀回的欄位。

結論：本次不能讀取帳戶剩餘額度、實際 token 總用量、限額重置時間、credits 或費用。省長應繼續以預算卡、重做次數與可驗證的付費點數作管理依據，不把工具輸出 token 估算當成帳戶用量。

### 決策與範圍

選題情報週報由 Codex 每週執行一次，阿派派工、小渡主責、小市提供需求採證，開工前取得省長的 S 預算卡。本次只確認分工，沒有建立或更改排程。

本次沒有開始階段 2 或 2B 的產線工作。另，控制台文件目前已記載階段 2、2B 與階段 3 均完成；若要把它們當成待啟動階段，需先修正兩處說法不一致的文件狀態。

## 2026-10-12（Asia/Taipei）多利階段 2B dry-run 驗證

實跑每日、每週及帳本三個入口的 `--dry-run`。三個指令皆 exit 0；輸出均明確標示不存檔、不寄信、不通知。沒有執行實際寄信、安裝排程或寫入週計畫。

| 入口 | 驗證結果 |
| --- | --- |
| `bash tools/duoli/daily-check.sh --dry-run` | `PASS`；巡檢正常輸出，並提出需人工確認的警示。 |
| `bash tools/duoli/weekly-open.sh --dry-run` | `PASS`；週計畫狀態與提醒輸出正常。 |
| `bash tools/duoli/ledger-tally.sh --dry-run` | `PASS`；缺少來源資料時明確回報無法統計。 |

判定：三個例行入口的 dry-run 驗證通過；整體階段 2B 尚未完成 3 天連跑、測試資料夾警告驗證或實際寄信，因此不標記為完整驗收。涉及目前排程、素材路徑與數量的警示明細保存在私人工作區盤點清冊。

## 2026-10-12 15:27（Asia/Taipei）控制台能力實測

本次依 `docs/CEO_CONTROL_TOWER.md` 做控制面驗證，未啟動任何 Skill、內容產線、生成、渲染、上傳或平台操作。

| 實測項目 | 結果 | 可讀回證據／限制 |
| --- | --- | --- |
| 子代理遞迴派工 | `PASS` | 主代理建立 dispatcher `/root/dispatcher_probe`；dispatcher 成功建立 explorer `/root/dispatcher_probe/repo_read_probe`，並唯讀查詢 `docs/CEO_CONTROL_TOWER.md` 前 20 行，讀到 `## 1. 決策與責任邊界`。表示子代理可再派子代理。 |
| Codex 額度／用量可見性 | `LIMITED` | 此工作階段無 `/status` 或等價的額度 API。`get_goal` 只回傳 `goal`、`remainingTokens`、`completionBudgetReport`，本次三者均為 `null`；`codex login status` 只顯示「Logged in using ChatGPT」。可確認登入身分，不能讀取方案額度、已用 token、剩餘 token、重置時間、費用或併發額度。 |

結論：階層式派工可作為階段 2／2B 的控制面能力；額度治理目前只能以任務級工作量與子代理數量作營運估算，不能宣稱有即時用量讀回。若要讓額度成為可驗收欄位，需由產品端提供可授權讀取的 usage／quota 端點或 UI 證據。
