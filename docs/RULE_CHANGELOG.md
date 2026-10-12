# 規則變更紀錄

本檔只記 A 級母版、Skill 母版與跨專案流程的變更。單次任務進度留在任務卡、`HANDOFF.md` 或專案文件；未驗證的偏好不可升為永久規則。

| 日期（Asia/Taipei） | 變更 | 類型 | 觸發原因 | 權威文件 | 驗證方式 |
| --- | --- | --- | --- | --- | --- |
| 2026-09-01 | 建立 CEO 控制台與內容營運長章程 | 新制度 | 多個 Skill 缺總調度、交接與發布停止線 | `docs/CEO_CONTROL_TOWER.md` | 後續內容任務依任務卡、主管與證據流程回報 |
| 2026-09-01 | 建立文件權威與生命週期規則 | 新制度 | 任務紀錄、Skill、相容文件容易互相覆蓋 | `docs/DOCUMENT_GOVERNANCE.md` | 每月盤點 owner、狀態、衝突與公開風險 |
| 2026-09-01 | Codex 定為主要操作者；Claude 保留輔助執行端 | 治理決策 | 老查尚未決定完全停用 Claude | `AGENTS.md`、`docs/DOCUMENT_GOVERNANCE.md` | 共用規則從 `AGENTS.md` 同步；衝突以 Codex 文件裁決 |
| 2026-09-01 | 建立進行中任務總表與平台發布證據庫 | 新制度 | 已完成素材與已發布狀態被混用 | `docs/ACTIVE_TASK_REGISTER.md`、`docs/RELEASE_EVIDENCE_REGISTER.md` | 每次階段、版本或平台讀回變更後更新總表 |
| 2026-09-01 | 短影片一律先建立產前假設卡，發布後第 7 天用可比基準判定 `KEEP`／`ITERATE`／`STOP`／`UNRESOLVED`；一次只測 1 個內容入口變因 | 新制度 | 老查要求把可重複測試的內容方法納入短影片產出與成效審核 | `skills/short-video-experiment-review/SKILL.md`；接點為 `podcast-publish`、`podcast-performance-review` | 下一支短片有產前卡；7 天後有驗證卡；少於 4 支可比樣本維持 `UNRESOLVED` |
| 2026-09-05 | 修正 Podcast 視覺調度：一般預告固定先做老查、阿分、大寶、小寶四張獨立特寫，再接完整合照與片尾；YouTube 客廳版固定背景母版、主題背景系列、角色座標、專屬縮圖與片尾；移除不存在的 `social-cards` 路由 | 修改 | 連續出現整張圖 Zoom 冒充特寫、角色缺漏、客廳人物越界與 YouTube 包裝漏件 | `AGENTS.md`、`skills/podcast-teaser-video/SKILL.md`、`skills/podcast-publish/SKILL.md`、`docs/SKILL_ROUTING_MATRIX.md`、`docs/CEO_CONTROL_TOWER.md` | 下一個 Podcast 專案必須先通過角色／場景資產表與關鍵畫面 proof；狀態檔記錄 YouTube 資產與 QC flags |
| 2026-09-09 | YouTube 上傳工具遇到多個 MP4 候選時必須中止；正式檔由 `.publish-status.json` 的 `youtube_assets.render_file` 唯一指定，並要求上傳前核對影音規格 | 修改 | S3EP4 誤抓舊版 MP4，造成私人誤上傳 | `tools/youtube-upload.js`、`docs/LEARNING_NOTES.md`、`docs/RELEASE_EVIDENCE_REGISTER.md` | 以 S3EP4 同時存在舊／新版 MP4 實測：未指定時中止，指定後只上傳 `s3ep4-youtube-living-room-v2.mp4` |
| 2026-09-14 | IG 內容固定只留在《不標準答案》Instagram，禁止同步至 Si Ming Wang 個人 Facebook；星期天建立與提交前必須核對 IG 身分及交叉發布設定 | 修改 | S3EP7 發布時發現 IG／Facebook 個人頁連動風險 | `AGENTS.md`、`skills/podcast-publish/SKILL.md` | 下一集 IG 流程需讀回品牌帳號名稱，並確認 Facebook 交叉發布為關閉後才可提交 |
| 2026-09-14 | 預告人物版沿用 S3EP7「全圖風格重製」：從核准全圖延伸一致筆觸與角色設定，逐一重製四張具有獨立情境的個人畫面，禁止裁切或單純 Zoom | 新增 | 老查確認 S3EP7 預告的角色詮釋方式應成為後續固定做法 | `AGENTS.md`、`skills/podcast-teaser-video/SKILL.md` | 下一支預告交付前檢查四張特寫是否各自重製、風格一致且非全圖裁切 |
| 2026-09-14 | 任務交接紀錄不再預設同步 Google Drive；只有老查明確要求時才同步，S3EP7 保留為特例 | 修改 | 老查要求降低每次交接的雲端同步負擔 | `AGENTS.md` | 後續換機以 repo／GitHub 交接；收到明確要求時才建立 Drive 交接副本 |
| 2026-09-23 | Codex 核心 Skill 改為只接受 repo 母版；停止 Claude → Codex 反向同步，隔離 `.agents` 同名副本，總控流程啟動前執行來源檢查；Mac／Windows 使用同一套來源規則 | 修改 | 同名舊 Skill 被同時探索，造成星期天與其他角色誤用舊規則、浪費額度與時間 | `AGENTS.md`、`setup.sh`、`setup.ps1`、`tools/sync-codex.sh`、`tools/sync-codex.ps1`、`tools/check-skill-authority.*`、`tools/isolate-legacy-skills.*` | Mac 執行 `tools/check-skill-authority.sh`、Windows 執行 `tools/check-skill-authority.ps1`，均須回傳 `PASS`；`.agents/skills` 不得存在 repo 核心 Skill 同名目錄 |
| 2026-09-28 | 新增獨立 Skill「實透」，星期天管理核准金句原音、內容拆解、實景照片、動態腳本審閱、角色關鍵畫面與 Flow 動畫；實透改為每週 2 支主力、剪紙每週 1 支；編輯安排為週二 20:30 剪紙、週三 20:30 與週五 12:00 實透，三支採不同原音段落、觀點或切角與動作情境；保留既有外部排程與公開證據 | 新增 | 老查核准流程並命名，要求由星期天管理及與阿維討論發布時機 | `skills/shi-tou/`、`skills/podcast-publish/SKILL.md`、`AGENTS.md`、`docs/SKILL_ROUTING_MATRIX.md`、`docs/CEO_CONTROL_TOWER.md`、`BRAND_CONTEXT.md`、`skills/paper-collage-video/SKILL.md` | Skill 結構檢查、repo → Codex 副本比對及來源檢查；未進行付費生成或平台發布 |
| 2026-09-28 | YouTube 長片移出星期天，建立獨立「油管」Skill，由小查接令管理；沿用核准視覺、縮圖、QC 與上傳規則，獨立狀態與日期；YouTube Shorts 留在星期天 | 新增／修改 | 老查指出長片製作耗時，明確要求拆出獨立人物與流程 | `skills/you-guan/`、`skills/podcast-publish/SKILL.md`、`AGENTS.md`、`BRAND_CONTEXT.md`、`docs/CEO_CONTROL_TOWER.md`、`docs/CEO_COMMAND_PROTOCOL.md`、`docs/SKILL_ROUTING_MATRIX.md` | Skill 結構與 JSON 檢查、角色路由與不阻塞情境檢查、repo → Codex 整樹比對；未生成長片或操作平台 |
| 2026-10-04 | 小渡介入每集 1 剪紙＋2 實透的兩段決策：候選原話後先配置三支任務，原音核准後再逐支交付 `READY` brief；星期天狀態檔記錄配置與各支 brief，剪紙未就緒不得做鏡頭表，實透未就緒不得拆解情境、索取照片或寫腳本 | 修改 | 原本只有總則，實透與剪紙的實作交接沒有小渡停止線，容易在製作後才補策略 | `skills/community-operations/SKILL.md`、`skills/podcast-publish/SKILL.md`、`skills/shi-tou/SKILL.md`、`skills/paper-collage-video/SKILL.md`、`docs/CEO_CONTROL_TOWER.md`、`docs/SKILL_ROUTING_MATRIX.md` | 檢查狀態模板 JSON、3 支不同 item ID 的 brief 欄位、各 Skill 停止線與 repo → Codex 同步後的來源檢查；未操作平台 |
| 2026-10-06 | 角色水墨插圖改為黑白水墨預設、老查明確要求時可使用低飽和彩色水墨；新增家庭桌遊封面的構圖、角色透視、彩墨與 `1400 × 1400` 交付檢查 | 修改 | 實作家庭桌遊封面時，黑白版完成後需要可保留墨線與紙感的彩色變體；小寶坐在斜棋盤邊緣曾出現腳部與棋盤透視不一致 | `skills/chibi-ink-illustrations/SKILL.md`、`skills/chibi-ink-illustrations/references/podcast-cover-workflow.md` | 檢查四角色服裝、斜棋盤接觸面、無文字與無浮水印；交付黑白與彩色水墨各 1 張 `1400 × 1400` PNG |

| 2026-10-10 | Claude 共用入口改為匯入 Codex 的 AGENTS 母版，子專案亦引用同層 AGENTS；停用過期鏡像、記憶路由與舊 git pull 同步 hook，新增 repo → Claude 單向部署及整樹驗證；其他專案不自動套入 Podcast 產線 | 修改 | 老查要求兩個月未更新的 Claude 與 Codex 現行工作方式同步，並清除舊規則 | `AGENTS.md`、`CLAUDE.md`、`tools/sync-claude.py` | 驗證 23 個 repo Skills 整樹一致、入口引用有效、工作區記憶索引重建；MCP 共用 5 項設定相同，Claude CLI 讀回全部 Connected |

| 2026-10-10 | 品牌憲法版本引用由 v3 改為已讀回的 v5（2026-09-04 增修）；原文只保存在私人聊遇所工作區，母品牌摘要不納入私密原文，也不覆蓋後續已核准的操作規則 | 修改 | 老查提供總部 Drive；實際 Word 內文已是 Version 5.0，但 repo 引用與雲端索引仍落後 | `BRAND_CONTEXT.md`；私人專案來源索引 | 讀回 Word 版本頁；雲端索引未改動，標示待校正 |

| 2026-10-10 | 新增 Windows 的 Codex＋Claude 單向同步入口、全域規則部署、可選舊 Skills／指定記憶清理，UTF-8 BOM 編碼相容，以及公開 repo 外的私人專案 ZIP 驗證匯入；公開方法走 repo，私人內容走老查指定的 Drive | 新增 | 老查要求本次 Claude 更新與聊遇所交接可同步到 PC | `codex/AGENTS.global.md`、`tools/sync-claude.ps1`、`tools/sync-claude.py`、`tools/import-private-project.py`、`docs/CLAUDE_PC_SYNC.md` | Mac 上驗證 Python 共用引擎、資料雜湊、重跑與漂移偵測；Windows PowerShell 包裝尚待 PC 實機執行 |

## 新增變更模板

```text
| YYYY-MM-DD | 規則文字與影響 | 新增／修改／廢止 | 觸發事件 | 唯一母版 | 如何驗證、何時回看 |
```

廢止規則時，保留原列並新增一列說明取代文件與日期。不得刪除歷史變更來假裝規則從未存在。

| 2026-10-10 | 短片改為週一至六共 6 支、預告包含其中；3 實景紙片＋2 原音字卡／物件＋1 完整剪紙，Flow 改為特別企劃；以跨集週計畫追蹤、保留歷史發布證據 | 修改 | 老查要求降低實透製作時間並核准六支與兩種樣片比較 | `docs/SHORT_VIDEO_WEEKLY_POLICY.md`、星期天／小渡／實透／剪紙／預告／短片實驗 Skills | 六個槽位與預告計數檢查、Skill 結構與狀態模板 JSON、同步來源比對；樣片不計為正式成品或已發布 |

| 2026-10-10 | 所有短影片取消片尾卡，結尾需設計接回開場形成循環；QC 必須連播檢查尾段與開場，完整原話與自然音訊優先 | 新增 | 老查檢視 S3EP11 預告後明確要求短影片不留片尾並循環播放 | `docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`AGENTS.md`、`skills/podcast-publish/SKILL.md` | S3EP11 循環版 33.5 秒成片檢查通過，尾格回到開場；10/11 三平台新版已讀回排程，舊版已清除 |

| 2026-10-11 | 新增已排程短片換版 SOP：先核對新舊平台 ID，逐平台建立並讀回新版的檔案／內容、帳號、封面與排程，再依明確授權刪除舊版，最後確認沒有重複並更新狀態與證據 | 修改 | S3EP11 循環版替換過程需要同時保住排程、清除舊片並跨平台留證 | `skills/podcast-publish/SKILL.md`；案例見 `docs/LEARNING_NOTES.md` 與 S3EP11 QC | 新版三平台排程 ID／時間讀回；三筆舊版清除；Meta 排程清單無重複；私有狀態 JSON 可解析 |

| 2026-10-12 | Codex 改組為影音動畫公司（階段 1）：小查改為特助與唯一窗口，不產製不放行；新增阿派（營運總監，依賴圖並行派工）、廠長（製作總監）、鐵雄（品管合規，獨立稽核、逐條附出處、FAIL 只有老查能推翻）、省長（額度管理，S／M／L 預算卡）四個角色；製作改為並行，固定順序只約束排程；全員命名；多利、解題、招牌與上傳硬閘門列為後續階段 | 新增／修改 | 老查指出品管常脫離規則、產線串行拖慢進度、小查一人兼多職自己驗自己，並要求控管額度 | `docs/CEO_CONTROL_TOWER.md`、`docs/SKILL_MIGRATION_PLAN.md`、`docs/QUOTA_LEDGER.md`、`codex/agents/` 四個新角色、`codex/AGENTS.global.md`、`AGENTS.md`、`docs/SKILL_ROUTING_MATRIX.md`、`docs/CEO_COMMAND_PROTOCOL.md`、`docs/AUTHORITY_MATRIX.md`、`docs/templates/weekly-plan.template.json`、`tools/sync-codex.sh`、`tools/sync-codex.ps1`（日常同步改為一併部署角色檔，PC 才讀得到） | TOML／JSON 解析、Codex 部署比對、來源檢查 PASS；待 Codex 實測子代理巢狀派工與額度讀取；試運行一週後回看工時、退件率與額度 |

| 2026-10-12 | 多利轉職為後勤管家（階段 2B）：每日排程看門、Skill 健康、檔案巡邏，每週開週計畫與復盤提醒、整理交件包數字給省長，全部改用腳本、不耗 AI 額度；8 支舊 claude.ai routine 讀回確認已刪除，備份保留作按需查詢樣板；廠長交件包新增固定的「重做次數」「付費點數」兩行 | 修改 | 老查指出多利因額度停擺，要求轉成適合的後勤工作 | `skills/daily-routines-manager/`、`tools/duoli/`、`codex/agents/production_lead.toml` | 三支腳本 dry-run、暫存資料夾測試（開檔不覆蓋、帳本加總、多 MP4 警告）、launchd 安裝後首次執行紀錄；連跑 3 天確認無遺漏、無 AI 呼叫 |
