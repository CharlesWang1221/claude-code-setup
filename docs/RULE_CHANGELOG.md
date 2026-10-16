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

| 2026-10-14 | 星期天發布階段改為「上架授權包」：建包前預檢登入、帳號身分與時間；老查回「可以上架」即授權包內全部列，授權後自動完成 Firstory 預約、IG／FB 與短片排程並讀回；異常只停該列、跑完一次回報；取消 IG 草稿二次確認與 Firstory 人工按發布 | 修改 | 老查指出每次上架都被逐項詢問，必須守在電腦前才能完成 | `skills/podcast-publish/SKILL.md`、`docs/AUTHORITY_MATRIX.md`、`docs/CEO_COMMAND_PROTOCOL.md` | 下一集上架時檢查：授權前只有 1 次詢問、授權後無逐列詢問、每列有平台讀回或 FAILED 原因；Firstory 預約由瀏覽器工具完成尚待首次實測 |

| 2026-10-14 | 油管長片比照上架授權包：老查回「可以上架」後，`youtube-upload.js --publish-at` 一次完成上傳、縮圖與預約公開，工具核對平台回傳的預約時間；不再另進 Studio 手動排程 | 修改 | 老查要求 YouTube 上架也不必守在電腦前 | `skills/you-guan/SKILL.md`、`skills/you-guan/references/state-and-upload.md`、`tools/youtube-upload.js`、`docs/CEO_COMMAND_PROTOCOL.md` | 時間格式與已過時間的拒絕邏輯已本機測試；實際上傳與 `publishAt` 回傳尚待下一支長片首次實測 |

| 2026-10-14 | YouTube Shorts 納入上架授權包的自動執行：`youtube-upload.js` 新增 `--video`／`--meta`／`--thumbnail`／`--qa-report` 直接指定週計畫單支檔案，搭配 `--publish-at` 一次上傳、套封面並預約公開；已有 videoId 即跳過 | 修改 | 老查要求 YouTube 短影片也不必逐支確認 | `skills/podcast-publish/SKILL.md`、`tools/youtube-upload.js` | 參數缺漏、檔案不存在、時間已過三種錯誤路徑已本機測試；實際 Shorts 上傳、預約與封面生效尚待首次實測 |

| 2026-10-14 | Threads 納入排程：每集主題文（週一 12:15）、6 支金句短片（同各支時段）、週四網誌導流短文（12:15）；一律另寫 Threads 版文案並過品牌閘門；IG「分享到 Threads」關閉；授權後以 threads.com 原生排程完成並讀回 | 新增 | 老查要求 Threads 也加入排程，選定主題文、金句短片與網誌導流三類，文案另寫 | `skills/podcast-publish/SKILL.md`、`skills/seo-article-writer/SKILL.md`、`docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`AGENTS.md` | 規則與同步檢查；Threads 帳號登入、網頁版原生排程與讀回尚待首次實測；週四 12:15 為編輯預設，無流量實證 |

| 2026-10-14 | 影片上架 AI 標示預設選「否」（YouTube 變造或合成內容、Meta AI 標籤、Threads）；授權包每列記 `ai_label`；`youtube-upload.js` 預設送出 `containsSyntheticMedia: false`，`--synthetic-media` 改為是。例外僅 AI 複製聲音、擬真 AI 人物／場景，須選「是」；不得去除 AI 中繼資料 | 新增 | 老查要求影片上架不標注 AI | `skills/podcast-publish/SKILL.md`、`skills/you-guan/SKILL.md`、`tools/youtube-upload.js` | 欄位對照 YouTube Data API 官方文件；實際上傳後於 Studio 讀回「變造或合成內容＝否」尚待首次實測 |

| 2026-10-15 | 新增「教材復盤」Skill（`process-curriculum-retro`）：每週記錄製作流程改了什麼、為什麼改、有沒有證據，並把每項方法改變整理成 8 類教材卡（草稿／已驗證／可教三級），落檔老查 Drive「不標準答案/復盤內容」；每週日製作復盤後由教父提醒；與製作復盤、成析分工不重疊 | 新增 | 老查準備日後開工作坊，要求每週復盤時記錄製作過程變化並整理成分類教材 | `skills/process-curriculum-retro/SKILL.md`、`AGENTS.md`、`docs/SKILL_ROUTING_MATRIX.md`、`docs/CEO_CONTROL_TOWER.md` | 已在 Drive 建立資料夾、README、索引、2026-W42 週紀錄與 10 張教材卡；Skill 同步與 Codex 端首次實跑待驗證 |

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

| 2026-10-12 | 多利例行巡檢改由小查每天第一次回報前執行 `tools/duoli/duoli.py auto`，不使用 launchd 背景排程、不寄信；報告存於 `output/weekly-shorts/duoli-reports/`，當天已跑過就印出已存報告 | 修改 | launchd 讀取 `~/Documents` 需授權 Python 完整取用磁碟，老查選擇不開放此權限 | `tools/duoli/duoli.py`、`skills/daily-routines-manager/SKILL.md`、`docs/CEO_COMMAND_PROTOCOL.md`、`docs/CEO_CONTROL_TOWER.md` | 實跑 `auto` 兩次：第一次產出並存檔、第二次印出已存報告；報告目錄被 git 忽略；launchd 已移除 |

| 2026-10-12 | 階段 2：影碩（`video-explainer`）改名重寫為解題（`jieti`，知識解說動畫），影華（`video-promo`）改名重寫為招牌（`zhaopai`，頻道形象動畫），移除 ASUS 內容並改用 HyperFrames；剪紙觸發詞只歸剪紙，舊剪紙模組封存；影片頭（`video-shotcraft`）自 setup 下架；10 個 Skill 說明加上員工名稱；選題情報週報改由 Codex 每週手動執行，多利每週提醒 | 修改／廢止 | 公司不再承接 ASUS 內容，老查要求轉成自媒體動畫公司的員工並全員命名 | `skills/jieti/`、`skills/zhaopai/`、`skills/paper-collage-video/`、`skills/animation-director/SKILL.md`、`AGENTS.md`、`docs/SKILL_ROUTING_MATRIX.md`、`setup.sh`、`setup.ps1`、`tools/duoli/duoli.py` | 全 repo 不再有派工到舊名稱的引用；`jieti`／`zhaopai` 除一句「已移除 ASUS 內容」的轉職註記外，無 ASUS 內容；同步後 Codex 不殘留舊資料夾且來源檢查 PASS；小樣於第一個真實任務驗證 |

| 2026-10-12 | 階段 3：上傳硬閘門。新增 `tools/qa-gate/qa-gate.cjs`，確認最終檔有鐵雄 PASS 報告且 SHA-256 一致；YouTube、Firstory 上傳工具在程式內強制檢查，IG／FB 由星期天上傳前執行並貼入證據庫；緊急放行需老查決定，以 `QA_OVERRIDE_REASON` 記錄，多利每日回報 | 新增 | 規則只寫在文件時，可能被忘記或跳過；需要程式擋住 | `tools/qa-gate/`、`tools/youtube-upload.js`、`tools/firstory-upload/upload.mjs`、`tools/duoli/duoli.py`、`docs/CEO_CONTROL_TOWER.md` | 8 種情況測試通過；Firstory 實測在開瀏覽器前擋下；YouTube 僅語法檢查，首次正式上傳時讀回驗證 |

| 2026-10-12 | 省長額度讀數：Codex 讀不到帳戶額度，改由老查每週一在 Codex 輸入 `/status` 貼回原文，小查第一次回報時提醒，省長記帳後才開本週預算卡；沒有讀數時以代理指標開卡並在結算註明 | 修改 | Codex 實測確認無工具可讀帳戶用量，老查同意以每週手動讀數補上 | `docs/CEO_CONTROL_TOWER.md`、`codex/agents/quota_officer.toml` | 下週一小查有提醒、帳本有 `/status` 讀數或「本週無讀數」註記 |

| 2026-10-13 | 製作流程改為看板拉動制：T1–T4 明定為看板欄位（待辦／`READY`／製作中／稽核中／待放行／已排程），WIP 上限＝預算卡並行數（S=1、M=2–4、L>4）；逾時判準綁上架時間，阿派從週計畫或單集狀態檔讀取每支 item 的 `target_at`（上架時間）回推截止時間，停留超過 48 小時或距上架時間不足 24 小時仍未進「待放行」就標記 `overdue`，優先處理距上架時間最近者，由阿派當天回報與重排，不新增時間官；鐵雄 FAIL 拆分「可自行修正」（技術格式類，廠長自行修正、重送鐵雄複審，不經小查老查，同一條二度 FAIL 自動升級）與「需升級」（品牌／合規／授權／預算，維持原停止線、只有老查能推翻）；小查日報新增「看板逾時數量、原因與距上架時間」「退件可自行修正／需升級」欄位 | 修改 | 老查反映製作常拖過上架時間、省長發現錯誤後整個硬停要等人工重啟浪費時間；依老查提供的 PMI／敏捷聯盟《敏捷實踐指南》(AgilePG_CHI.pdf) 導入看板與分級處理，同時保留對外內容必要的品牌合規否決權不變；老查進一步要求逾時判準要配合阿派掌握的實際上架時間與排程，不是單純固定計時器；5 小時額度自動恢復續跑仍卡在既有「Codex 讀不到帳戶額度」限制，本次未解決，待另行技術調研 | `docs/CEO_CONTROL_TOWER.md` | 下一週計畫或單集狀態 JSON 需能標記 `lane_status: overdue` 且能對照 `target_at`；下一次鐵雄報告需能看到「可自行修正」與「需升級」兩類分別走對應流程；下一份小查日報含逾時數量與距上架時間欄位 |

| 2026-10-13 | 5 小時額度自動續跑：新增 `tools/codex-resume-watch/`，排程（Mac launchd／Windows 工作排程器，每 10 分鐘）讀本機 Codex 工作階段紀錄的 `rate_limits` 與 `resets_at`，額度卡住且已過恢復時間才對卡住的工作階段呼叫一次 `codex exec resume <session id>`，同一 `resets_at` 不重複、超過 6 小時的舊紀錄不接續；兩台電腦各自 `install` | 新增 | Codex 原生不支援額度恢復續跑（openai/codex Issue #21073 未處理）；不採用第三方 watchdog，改自建可審查的最小腳本 | `tools/codex-resume-watch/`、`.gitignore`、`docs/CEO_CONTROL_TOWER.md` | 已用 176 份歷史紀錄 dry-run 驗證三種判斷；尚未遇過真實卡額度情境，第一次實際卡住後要讀 log 確認有正確接續 |

| 2026-10-13 | 製作復盤與精進迴路：收集鐵雄 FAIL、阿維 REVISE／REJECTED、老查改稿三種退回，阿派每日記入 `docs/PRODUCTION_RETRO_LOG.md`；鐵雄獨立歸因為沒寫／寫不清／沒遵守；每週日 21:00 前交週復盤；「沒寫」「寫不清」由師傅改 Skill 母版，「沒遵守」改加進鐵雄必查項；同一缺失出現 2 次才改 SOP（老查明說長期適用則 1 次就改）；改後再犯列「改了沒用」升級老查。同步把 FAIL 分級與缺失歸因欄寫進鐵雄子代理設定（補上同日 FAIL 分級漏改 `qa_auditor.toml` 的缺口），每月回報改看「改了沒用」項目 | 新增 | 老查要求製作團隊越做越符合要求；原本只有每月檢討鐵雄 FAIL，漏掉退件大宗的老查改稿與阿維 REVISE，且頻率太慢 | `docs/CEO_CONTROL_TOWER.md`、`docs/PRODUCTION_RETRO_LOG.md`、`codex/agents/qa_auditor.toml`、`docs/ACTIVE_TASK_REGISTER.md`、`docs/DOCUMENT_GOVERNANCE.md` | 下一份鐵雄報告含 FAIL 分級與缺失歸因欄；2026-10-18 週日有第一份製作復盤 |

| 2026-10-14 | 短片改版：週一至六 6 支全部改為「金句短片」，週一那支為本集預告；預報改名「句剪」（Skill 代號 `podcast-teaser-video` 不變，「預報」觸發詞保留）；每支另行製作專屬封面並獨立送審；重點卡字級放大 40%（主句 42.9→60 px、副句 35.2→49 px），放不下就換行或精簡濃縮文字，逐字原話只換行不刪字，整張卡須在安全框內（`bottom` ≥ 400 px）；剪紙、實透改為老查點名＋省長 L 級預算卡才啟動的特別企劃，替換槽位維持總數 6；「節目精選」改由句剪處理，不再觸發剪紙；真短驗析每支出產前假設卡與 D7 驗證卡，試行 2 週後彙整；週計畫 item ID 改為 `*-quote`，舊週計畫不回溯 | 修改 | 老查 2026-10-13 實測剪紙與實透耗時、耗額度過多，與阿分討論後決定；6 天都叫「預告」不合邏輯故改名；老查反映預報字幕太小 | `docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`docs/templates/weekly-plan.template.json`、`AGENTS.md`、`BRAND_CONTEXT.md`、`docs/SKILL_ROUTING_MATRIX.md`、`docs/CEO_CONTROL_TOWER.md`、`skills/podcast-teaser-video`、`skills/podcast-publish`、`skills/paper-collage-video`、`skills/shi-tou`、`skills/community-operations`、`skills/short-video-experiment-review` | 下一份週計畫六項皆為 `*-quote` 且各有假設卡與專屬封面；第一支新片重點卡實測字級與安全框；試行 2 週後真短驗析交 12 支彙整 |

| 2026-10-14 | 修正 Windows 同步路徑：`tools/sync-codex.ps1` 與 `tools/check-skill-authority.ps1` 原本寫死 `~/.codex`，但這台 Codex 設有 `CODEX_HOME`（`%LOCALAPPDATA%\CodexCLI`），導致 9/29 後的 Skill、全域規則與角色都沒部署到 Codex 實際讀取的位置，檢查也比對錯資料夾而顯示 PASS；改為有 `CODEX_HOME` 就用它 | 修正 | 實測 Codex 讀取位置的 23 個核心 Skill 中 18 個 DIFF／MISSING（含 jieti、zhaopai、community-operations） | `tools/sync-codex.ps1`、`tools/check-skill-authority.ps1` | 部署後 `check-skill-authority.ps1` 對 `CODEX_HOME` 回 PASS；Mac 未設 `CODEX_HOME`，行為不變 |

| 2026-10-14 | 取消所有未發布的剪紙／實透舊內容，不再發布：移除 `S3EP5-H1`、`S3EP5-H2`、`S3EP3-COLLAGE`；`S3EP7-RELEASE` 兩支剪紙正式檔、`S3EP8-RELEASE` 兩支剪紙、`S3EP9-RELEASE` 實透 1 與剪紙、`S3EP10-RELEASE` 兩支實透一併取消；原音可轉金句短片候選，需重新 READY brief。已發布的 S3EP10 剪紙、S3EP9 實透 2、S3EP11 週二剪紙不撤下。同步把 `setup.sh`、`tools/sync-codex.sh`、`tools/check-skill-authority.sh` 改為尊重 `CODEX_HOME` | 修改 | 老查決定舊剪紙／實透全部取消、改成金句短片；Mac 腳本與 Windows 同樣寫死 `~/.codex` | `docs/ACTIVE_TASK_REGISTER.md`、`setup.sh`、`tools/sync-codex.sh`、`tools/check-skill-authority.sh` | 星期天下次調度不再出現這些剪紙／實透 item；Mac 執行 `./setup.sh` 後 `check-skill-authority.sh` 回 PASS |

| 2026-10-14 | 新增執行長「教父」：在老查之下、其他人之上，接老查發布的案件、管理整個後製流程並向老查回報與送最終批准；阿派留在教父之下負責任務卡與派工；鐵雄、阿維、省長行政歸教父，但判定獨立，教父不能推翻。小查改為獨立特助：只聽老查命令、處理老查個人交辦與監察全公司，不屬教父、不向教父回報；發現違反停止線可寫 `lane_status: FROZEN` 凍結該 item，只有老查能解除。小查日報改為教父日報，另加小查監察報告；新增 `codex/agents/inspector.toml` | 新增／修改 | 阿分提議：老查只需發布案件、洽談業務與最終批准；原本小查兼接令、回報與監督，自己監督自己轄下的流程 | `docs/CEO_CONTROL_TOWER.md`、`docs/CEO_COMMAND_PROTOCOL.md`、`docs/AUTHORITY_MATRIX.md`、`docs/SKILL_ROUTING_MATRIX.md`、`AGENTS.md`、`codex/AGENTS.global.md`、`codex/agents/`（dispatcher、qa_auditor、quota_officer、新增 inspector）、`docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`docs/ACTIVE_TASK_REGISTER.md`、`skills/community-operations`、`skills/daily-routines-manager`、`skills/podcast-publish`、`skills/you-guan` | TOML 解析通過；待驗：下一份日報以【教父日報】出現且附【小查監察】原文；第一次 FROZEN 時星期天確實停下；`tools/qa-gate/qa-gate.cjs` 已改為讀取 `lane_dir/FROZEN.md` 與週計畫 `lane_status: FROZEN*` 硬擋上傳，且緊急放行無效（暫存目錄 5 情境測試通過）；Mac 需 `git pull` 後執行 `./setup.sh` 部署新角色與規則 |
| 2026-10-14 | 所有句剪改為核准原音帶劇情：先按原話因果寫鏡頭表，再決定角色、場景與視覺；不預設三張字卡或四人出場。S3EP11 週三字卡版退件，老查核准 L 級新繪角色水墨劇情版 | 修改 | 老查以既有 Reel 指出字卡版方法錯誤，明確指定往後所有句剪遵守原音敘事 | `docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`skills/podcast-teaser-video/SKILL.md`、`docs/QUOTA_LEDGER.md` | 週三小樣能逐鏡對回原音，人物／動作／因果成立；獨立關鍵畫面審核後才渲染，首尾連播無片尾卡 |

| 2026-10-14 | 新增 Voicebox 本機聲音複製工具（試用）：只在 Mac 安裝（Windows 為公司電腦，禁止安裝外部軟體）；聲音檔不進公開 repo；句剪與原話內容禁用 AI 聲音，阿分須書面同意，大寶小寶禁止；盲聽通過前不得用於對外成品 | 新增 | 老查評估 FB 影片介紹的開源 ElevenLabs 替代方案後核准安裝 | `docs/VOICEBOX_SETUP.md`、`tools/install-voicebox.sh` | Mac 待 `git pull` 後執行腳本；盲聽結果回填本表 |

| 2026-10-15 | PC 更新流程：「未提交修改」只看已追蹤檔（`git status --short --untracked-files=no`），未追蹤檔不擋 pull；有修改時逐檔確認後只 commit 指名檔案，兩邊分岔改 `git pull --rebase`，表格衝突兩邊新列全保留；push 需老查當次同意 | 修改 | PC Codex 因未追蹤的 `video-projects/` 停工，且 `--ff-only` 在 PC／Mac 都有新 commit 時必定失敗 | `docs/CLAUDE_PC_SYNC.md`、`AGENTS.md`、`docs/SHORT_VIDEO_WEEKLY_POLICY.md` | 下次 PC 更新遇未追蹤檔不再停工；有修改時能 rebase 後同步並 `check-skill-authority.ps1` PASS |

| 2026-10-15 | 句剪六支並行：老查審核改為每週原音包、鏡頭表包、小樣包三次；包在未阻塞 item 到齊時交出，退件只退單支；正式渲染同時最多 2 支。新增「句剪常態卡」：WIP 6、Terra、ImageGen 每支 ≤10 次／每週 ≤60 次，省長每週一直接開卡不必重批 | 新增／修改 | 老查實測句剪一支做完才開下一支、進度太慢；原因是原音一次只交一段、每支兩道關卡逐支等待、M 卡並行 2 | `docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`docs/CEO_CONTROL_TOWER.md`、`skills/podcast-publish/SKILL.md`、`skills/podcast-teaser-video/SKILL.md`、`skills/community-operations/SKILL.md`、`AGENTS.md`、`docs/QUOTA_LEDGER.md` | 下一週句剪：六支 brief 同日產出、鏡頭表與小樣各以一包交老查；記錄六支總工時與 2026-10-14 週對照；ImageGen 用量未超常態卡上限 |

| 2026-10-15 | 句剪鏡頭表每一鏡必附示意圖：9:16、用預定畫風與角色，每支一張聯絡表＋單張圖並標鏡號、原音起訖、原話與畫面事件；先重用核准素材本機合成，不足才用 ImageGen 並計入常態卡每支 10 次；核准示意圖即為關鍵畫面母版 | 新增 | 老查要求審鏡頭表時就看到圖像實際呈現 | `skills/podcast-teaser-video/SKILL.md`、`docs/SHORT_VIDEO_WEEKLY_POLICY.md` | 下一個鏡頭表包六支都附聯絡表，鏡數與鏡頭表列數一致；核准後關鍵畫面不再整支重畫 |

| 2026-10-15 | 句剪專屬封面新增「封面鉤子手法」：衝突句／半句懸念／角色反應三選一並記 `cover_hook`，全週套固定系列框架；禁用假引號、震驚臉與紅箭頭；角色反應畫面交大千出圖並計入句剪常態卡；封面鉤子列為真短驗析可測的入口變因，同週至少輪替 2 種 | 新增 | 老查要求挑選適合的短影音封面手法作為點閱鉤子 | `skills/podcast-teaser-video/SKILL.md`、`skills/short-video-experiment-review/SKILL.md`、`docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`docs/SKILL_ROUTING_MATRIX.md` | 下一週 6 支封面皆有 `cover_hook`、至少 2 種類型、系列框架母版經阿維核准；第 7 天驗證卡檢查封面點閱資料是否可取得 |

| 2026-10-15 | 居易改為每週四固定一篇「本週那集主題」的 GEO＋SEO 文章：網站 10:00、Threads 12:15、FB 20:30，不發 IG；新增 GEO 寫法（答案先行、實體明確、問句 H2、常見問題）、三平台標籤分工、啊問 1200 × 630 水墨主圖；金句沿用星期天已選定的；週三一包審；獨立品牌網誌改為點名才寫 | 修改 | 老查要求每週針對節目主題寫 GEO／SEO 文章，讓各平台搜尋讀到並發到 FB、Threads 與網站 | `skills/seo-article-writer/SKILL.md`、`skills/blog-image-director/SKILL.md`、`AGENTS.md`、`BRAND_CONTEXT.md`、`docs/SHORT_VIDEO_WEEKLY_POLICY.md`、`docs/SKILL_ROUTING_MATRIX.md` | 第一篇週四文章檢查：答案段、FAQ、實體、tags、主圖規格、三平台讀回；網站 FB 自動同步與 robots sitemap 兩項技術問題待處理 |

| 2026-10-15 | 網站 FB→IG 同步改為只轉含 `beyond-ans.com/blog/` 連結的居易長文（IG 圖文，過長補全文連結），網站不重複列出；Reels 與主題文不再被轉成 IG 靜態截圖；IG 金句圖與輪播只發 IG、不分享到 FB；週四文章帶 `publishAt` 由週四 10:00 排程部署上線，文章可輸出 FAQPage | 修改 | 老查要求 FB 文章一次發布讓 IG 也讀到，IG 金句圖不得上 FB；盤點發現同步把 Reels 截圖重複發到 IG | `.github/scripts/sync-fb-posts.js`、`.github/workflows/deploy.yml`、`site/src/`、`skills/seo-article-writer/SKILL.md`、`skills/podcast-publish/SKILL.md`、`AGENTS.md`、`BRAND_CONTEXT.md` | 本機 build、publishAt／FAQ 假文章測試、同步函式樣本測試；首篇週四長文當晚 22:00 同步需讀回 IG 貼文與網站未重複 |

| 2026-10-15 | 六支短片的 IG／FB Reels 改在 Meta Business Suite 以同一則 Reel 一次排程兩平台，共用 caption，分別讀回 | 修改 | 老查要求發一次讓兩平台都有，省額度與流程 | `skills/podcast-publish/SKILL.md` | 下一週第一支短片在 Business Suite 排程清單讀回 FB、IG 兩列與封面 |

| 2026-10-15 | 所有要對外發布的影片都必須有專屬封面，由製作產線一起交件：直式沿用句剪封面規格與鉤子，橫式 1280 × 720；缺封面的列在授權包一律 BLOCKED | 新增 | 老查要求「只要做影片就要有封面」，盤點發現真秀、剪紙、實透、解題、招牌、Flow 都沒寫 | `AGENTS.md`、`skills/shorts-pipeline`、`skills/paper-collage-video`、`skills/shi-tou`、`skills/jieti`、`skills/zhaopai`、`skills/flow-video-pilot` | 下一支非句剪影片交件時檢查是否附封面與審核紀錄 |

| 2026-10-15 | 網站新增「單集重點」：每集寫 `site/src/content/highlights/s{季}ep{集}.md`（摘要、章節時間碼、原話、FAQ、相關文章），單集頁顯示並輸出 Clip／FAQPage；不放完整逐字稿；首頁加 `sameAs` 串起各平台帳號；星期天授權包新增一列，Firstory 公開後才推送 | 新增 | 老查想讓《不標準答案》被 AI 搜尋看見，但完整逐字稿太繁瑣、畫面不好呈現 | `skills/podcast-publish/SKILL.md`、`skills/seo-article-writer/SKILL.md`、`site/src/` | 本機 build、手機寬 390 px 截圖無橫向捲動、章節點擊跳到 750 秒；第一集實際上線待讀回 |

| 2026-10-15 | 內容決策新增「核心搜尋問題＋核心關鍵字」（居易查搜尋量），Firstory 標題、Show Notes、網站單集重點、週四 GEO 文章全部沿用；最終標題必含關鍵字；Show Notes 前 150 字先答問題、含 `00:00` 起的章節時間碼並連回網站 | 修改 | 老查確認要讓 Firstory 標題與介紹配合 GEO，AI 讀 Apple／Spotify 頁面時看到的就是這兩項 | `skills/podcast-publish/SKILL.md`、`skills/seo-article-writer/SKILL.md` | 下一集內容決策有核心問題與關鍵字；Firstory 讀回標題含關鍵字、說明欄前 150 字與章節；Spotify 顯示可點章節 |

| 2026-10-15 | `flow-video-pilot` 新增 Seedance 備援：經 Monica 網頁由 Codex 瀏覽器操作（不用另付費的 API），登入、扣點、單支生成、不自動重送與檔案選擇器停止線比照 Flow；前兩個鏡頭與 Flow 對照測試後依鏡頭類型固定指派；私人照片經第三方需老查當次同意 | 新增 | 老查有 Monica 年訂閱，想善用 Seedance 2.5 不浪費 | `skills/flow-video-pilot/SKILL.md` | Monica 使用條款、Mac 瀏覽器操作、額度計算方式與 Flow／Seedance 對照測試均待首次實測 |

| 2026-10-16 | 新增標題公式實驗 T1：整理 10 句候選金句時加標 `T1 適配`，每週從入選且標「可」的支挑 1 支只改標題測試 | 新增（實驗，未成規則） | S3EP11 剪紙「為了讓別人好探聽，卻離自己越來越遠」YouTube 觀看 724，同形式 S3EP10 僅 58；老查要求交 Codex 整理金句時套用 | `output/short-video-experiments/2026-10-title-formula.md`、`skills/podcast-teaser-video/SKILL.md`、`skills/podcast-publish/SKILL.md`、`docs/SHORT_VIDEO_WEEKLY_POLICY.md` | 下一次候選金句表有 `T1 適配` 欄；週計畫有 1 支 `title_formula_T1` 或寫明本週無適配；累積 4 支才判定 |

| 2026-10-16 | 星期天預檢的帳號身分加入 YouTube：Studio 網址頻道 ID 必須是品牌頻道 `UCE-QusSupACm0Lk7D0ThHLQ`，不是個人頻道 Charles Wang | 修改 | S3EP7 剪紙精華 YouTube 版誤發在個人頻道，10/16 重發至品牌頻道並刪除舊片 | `skills/podcast-publish/SKILL.md`、`docs/RELEASE_EVIDENCE_REGISTER.md` | 下一次上架授權包的 YouTube 列記錄讀回的頻道 ID |
