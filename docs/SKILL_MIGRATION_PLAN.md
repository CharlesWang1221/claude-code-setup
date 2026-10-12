# 組織重組遷移計畫

狀態：`ACTIVE`。階段 1 已於 2026-10-12 由老查核准部署；其餘階段待逐一核准。起草：2026-10-12（Asia/Taipei）。
每個階段完成並驗證後，才開始下一個階段。各階段完成後寫入 `docs/RULE_CHANGELOG.md`。

## 階段 1：規則與角色（只改文件與角色設定，不動 Skill）

| 檔案 | 動作 |
| --- | --- |
| `docs/CEO_CONTROL_TOWER.md` | 換成新版公司控制台 |
| `codex/agents/dispatcher.toml` | 新增（阿派） |
| `codex/agents/production_lead.toml` | 新增（廠長） |
| `codex/agents/qa_auditor.toml` | 新增（鐵雄） |
| `codex/agents/quota_officer.toml` | 新增（省長） |
| `docs/QUOTA_LEDGER.md` | 新增（省長帳本） |
| `codex/AGENTS.global.md` | 角色清單加入四個新角色；註明 reviewer 審程式、鐵雄審內容 |
| 各 Skill 的 `description` | 加上員工名稱（預報、剪紙、音剪、真秀、大千、流之呼吸、正風、成析、真短驗析、小簡、師傅）作為觸發詞；不改資料夾名稱 |
| `AGENTS.md`「CEO 控制台與內容營運」段 | 小查改為特助；指向新版控制台 |
| `docs/CEO_COMMAND_PROTOCOL.md`、`docs/AUTHORITY_MATRIX.md`、`docs/SKILL_ROUTING_MATRIX.md` | 角色名稱換成新稱；「主責」欄改成新部門；放行條件加入鐵雄 |
| `docs/ORG_RESTRUCTURE_PROPOSAL.md` | 標示 `SUPERSEDED`，指向新版控制台，不刪除 |
| `tools/sync-codex.sh`、`tools/sync-codex.ps1` | 日常同步也部署 `codex/agents/*.toml`（原本只有新機安裝的 setup 會部署，PC 日常更新會漏掉新角色） |
| `docs/templates/weekly-plan.template.json` | 每個 item 加入 `depends_on`、`lane_dir`、`lane_status`、`budget` 欄位 |

**驗證**
- 四個 toml 用 TOML 解析器檢查通過。
- `setup.sh` 執行後，`~/.codex/agents/` 出現 8 個角色。
- `tools/check-skill-authority.sh` 回傳 `PASS`。
- Codex 實測：子代理能不能再派子代理，結果寫入 `docs/SKILL_HEALTH_REGISTER.md`。
- Codex 實測：能不能讀到額度用量，結果寫入同一份文件。

## 階段 2：Skill 轉職與下架

### 影碩 → 解題（`video-explainer` → `jieti`）

- **新職務**：知識解說動畫師。把節目裡的觀念、數據、因果關係做成動畫，用於 YouTube 長片的圖解段落與知識型短片。
- **觸發詞**：「解題」「這個概念做成動畫」「圖解這段」。
- **移除**：ASUS 題材、ASUS Enterprise Agent Platform 案例、SaaS 產品解說路由、Remotion 流程。
- **改用**：HyperFrames（經 `hyperframes` 入口，必要時接 `faceless-explainer`、`motion-graphics`）。
- **剪紙模組**：`references/paper-cut-effect.md` 先和 `paper-collage-video` 比對。剪紙精華缺少的內容併過去，其餘封存；解題不再接任何剪紙觸發詞。
- **角色素材**：沿用 `DESIGN.md` 與角色水墨規格，維持頻道視覺一致。

### 影華 → 招牌（`video-promo` → `zhaopai`）

- **新職務**：頻道形象動畫師。負責節目片頭、新一季宣傳、頻道預告、活動或課程宣傳片。
- **觸發詞**：「招牌」「做片頭」「新一季宣傳」「頻道預告」。
- **移除**：ASUS 品牌、軟體平台案例、Remotion 主引擎。
- **保留**：「情緒與記憶點優先、必須有明確 CTA」的方法；改成服從 `BRAND_CONTEXT.md` 的品牌界線。
- **改用**：HyperFrames（經 `hyperframes` 入口，必要時接 `general-video`、`motion-graphics`、`music-to-video`）。

### 下架影片頭（`video-shotcraft`）

- 從 `setup.sh`、`setup.ps1` 移除 clone 與部署段落。
- `AGENTS.md` 的影片頭說明段落刪除；`docs/SKILL_HEALTH_REGISTER.md` 標示「已下架」。
- 本機已部署的副本由老查決定要不要刪除，不自動刪。

### 要一起修改的檔案

| 檔案 | 修改位置 |
| --- | --- |
| `AGENTS.md` | 觸發詞表的「影碩」列、「剪紙效果影片」列；影碩、影華、阿諾、影片頭四個說明段落 |
| `skills/animation-director/SKILL.md` | 第 3、10–15 行與影碩、影華的分工說明；阿諾改屬內容企劃部 |
| `docs/SKILL_ROUTING_MATRIX.md` | 「技術解釋型影片」「情緒型品牌宣傳片」兩列 |
| `docs/SKILL_HEALTH_REGISTER.md` | `video-explainer`、`video-promo`、`video-shotcraft` 三列 |
| `skills/video-explainer/agents/openai.yaml` | 隨資料夾改名並更新說明 |
| `tools/sync-claude.py`、`tools/check-skill-authority.*` | 若有寫死的 Skill 名單，一併更新 |

**驗證**
- `grep -ri asus skills/jieti skills/zhaopai` 沒有結果。
- 全 repo 找不到舊名稱 `video-explainer`、`video-promo` 的現行引用（歷史日誌與 changelog 除外）。
- Repo → Codex 同步後，`check-skill-authority.sh` 回傳 `PASS`，Codex 端沒有殘留舊名稱資料夾。
- 用一個真實節目概念各試做一支小樣，確認觸發與產線正確；小樣不發布。

## 階段 2B：多利轉職為後勤管家

**狀態（2026-10-12）**：已部署。舊 routine 讀回確認早已刪除，不需外部操作；腳本整合為 `tools/duoli/duoli.py` 加三支 `.sh` 入口。老查選擇不用背景排程（launchd 需授權 Python 完整取用磁碟），改由小查每天第一次回報前執行 `duoli.py auto`，Mac 與 PC 都適用，報告不寄信。launchd 範本保留為選用。尚待：選題情報週報的執行端。

可以和階段 2 同時進行，兩者不改同一批檔案。

### 停掉舊排程（外部操作，執行前逐支向老查確認）

| routine | 處理 |
| --- | --- |
| daily-podcast-direction-inspiration-report | 併入「選題情報週報」 |
| daily-competitor-monitor-7 | 併入「選題情報週報」 |
| daily-ae-motion-graphics-report | 停用，改為按需 |
| daily-news-digest-15 | 停用，改為按需 |
| daily-uiux-articles-report | 停用，改為按需 |
| daily-ai-startup-cases-report | 停用，改為按需 |
| daily-book-summaries-3 | 停用，改為按需 |
| video-analysis-daily | 取消 |

- 先用 `RemoteTrigger list` 讀回 8 支的實際狀態，再動手；已經停用的就只更新備份紀錄。
- API 不支援刪除，要刪除由老查在 claude.ai 手動操作；備份檔標示「已停用」或「已刪除」，不移除檔案。
- 「選題情報週報」的執行端待老查決定：claude.ai routine（用 Claude 額度）或 Codex 每週手動跑一次（用 Codex 額度）。兩者都要先有省長的預算卡。

### 新增後勤腳本

| 檔案 | 用途 |
| --- | --- |
| `tools/duoli/daily-check.sh` | 每日 07:30：排程看門、Skill 健康、檔案巡邏，彙整成一封信 |
| `tools/duoli/weekly-open.sh` | 每週一 07:30：建立週計畫空殼、列出到期的復盤 |
| `tools/duoli/ledger-tally.sh` | 每週日 20:00：統計交件包的重做次數與付費點數，產出給省長的原始數字 |
| `tools/duoli/launchd/*.plist.template` | macOS 排程範本；安裝時才填入本機路徑，repo 不存放絕對路徑 |

- 寄信沿用 Duoli Mailer Worker；token 只放本機環境變數，不進 repo。
- 腳本只讀檔、不改任何產線檔案；唯一的寫入是建立週計畫空殼（已存在就跳過，絕不覆蓋）。
- 全程不呼叫任何 AI 模型。
- Windows 版本等 Mac 版試跑穩定後再做。

### 更新多利的 Skill

- `skills/daily-routines-manager/SKILL.md` 改成後勤管家版（草稿見 `repo草稿/skills/daily-routines-manager/SKILL.md`）。
- 資料夾名稱維持 `daily-routines-manager`，避免觸發詞與部署路徑變動。

**驗證**
- 8 支 routine 的讀回狀態和備份紀錄一致。
- 每支腳本先用 `--dry-run` 印出內容，不寄信、不寫檔；確認後再實寄一次給老查。
- 故意放兩個 MP4 在測試資料夾，確認檔案巡邏會發出警告。
- 連續跑 3 天，確認沒有遺漏，也沒有呼叫 AI。

## 階段 3：硬閘門（要改程式碼，另開任務）

- `tools/youtube-upload.js`、`tools/firstory-upload/upload.mjs`，以及 IG／FB 發布工具，在上傳前讀取 `{lane_dir}/qa/report.md`：
  - 總結必須是 PASS。
  - 報告裡的 SHA-256 必須等於要上傳的檔案。
  - 任一項不符就中止，並印出原因。
- 先在測試檔上驗證中止與放行兩種情況，再套用到正式流程。

## 階段 4：試運行一週

用一週 6 支短片加上一集 Podcast 實跑新流程。

| 指標 | 怎麼量 |
| --- | --- |
| 從 T0 到 6 支全部進 T5 的時間 | 和上一週的實際時間比較 |
| 鐵雄退件率與原因 | 稽核報告統計 |
| 阿維終審退件率 | 預期因為 T1 預審而下降 |
| 額度 | 省長週結算，與試運行前一週比較 |
| 規則被跳過的次數 | 小查監督紀錄 |

試運行結束後，由小查交一份檢討給老查，決定繼續、調整或回退。
