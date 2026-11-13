# 進行中任務總表

最後盤點：2026-11-05（Asia/Taipei，Claude 管理層依老查指示清理）
主責：內容營運長。  
用途：唯一列出仍需 CEO、主管或老查採取動作的內容任務。它是索引，不取代各專案的 `BRIEF.md`、`HANDOFF.md`、品牌檢查、QC 或平台證據。

## 使用規則

- 只列 `ACTIVE`、`PENDING_APPROVAL`、`BLOCKED` 與 `REVISE`。已結案或純歷史文件不列入。
- 每次任務狀態、最終檔案、平台證據或下一棒改變時，先更新本表，再更新對應專案文件。
- `PENDING_APPROVAL` 代表等老查或品牌放行；`BLOCKED` 代表缺素材、資料或外部狀態。兩者都不是「快完成」。
- 沒有明確日期時填「未設定」，不能擅自編造截止時間。

2026-11-05 盤點：依老查指示，下列逾期或已完成任務標記結束並移出本表（內容保留於 git 歷史）：S4EP2-CAPTION-V9-VERIFY、S3EP12-RELEASE、COVER-HOOK-C1-2026-11-02、KDP-COLORING-TEST、S3EP11-WED-QUOTE、S3EP11-TUE-PAPER、IG-GROWTH-2026Q4、S3EP10-RELEASE、S3EP9-RELEASE、S3EP8-RELEASE、S3EP7-RELEASE、S3EP5-RELEASE、S3EP5-TEASER、S3EP5-YT、S3EP1-YT、S3EP2-YT、S3EP3-YT-TEST、ORG-GODFATHER、MAC-SYNC-2026-10-14、MAC-CODEX-PERMISSION-2026-10-15、PC-SYNC-2026-10-15、RECORDING-COMPASSION。11/02 週句剪老查回報已完成。

| 任務 ID | 任務與範圍 | 狀態 | 主責主管 | 最終依據／證據 | 阻塞或待放行 | 下一個明確動作 | 時點 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRE-PACKAGE-CUT-2026-11 | 上架包之前的流程：Codex 接第 2 步「未剪逐字稿」與第 6 步「照阿分修剪清單定稿剪輯」，固定回報剪後總長，剪後逐字稿對成品 MP3 重跑 Whisper | `ACTIVE` | 星期天＋音剪 | `docs/briefs/PRE-PACKAGE-CUT-2026-11/BRIEF.md` | Codex 能否讀寫阿分的共用 Drive 資料夾未實測；Speaker 對應需老查確認 | Codex 先實測 Drive 讀寫，S4E05 錄完後照待辦 A、B 執行 | S4E05 錄音後 |
| MAC-SYNC-2026-11-12 | Mac 同步 2026-11-12 規則：上架順序＋IG 輪播＋Threads 輪播鉤子文（`4abeee5`）、封面四人輪值與大寶小寶 v2 造型（`7922ea8`、`c5c0612`）、上架包前逐字稿與剪輯交 Codex（`2797f8a`，改 `podcast-publish`）；另有新任務卡 FB 限動試點（`b9570c2`，不動 Skill） | `ACTIVE` | Codex（Mac 執行） | Windows 2026-11-13 已同步到 `2797f8a`：`sync-claude.ps1 -CheckOnly` 回報 Codex 24、Claude 25 個 Skill MATCH／PASS | 無 | Mac 在 repo 執行 `git pull --ff-only`、`./tools/sync-codex.sh`、`python3 tools/sync-claude.py --apply --global-rules`，看到 PASS 後重開 Codex 與 Claude Code，回寫本列並移除 | 2026-11-16 週開工前 |
| KIDS-OUTFIT-COVER-ROTATION-2026-11 | 大寶改短 T＋長褲、小寶改短 T＋短褲（大千重繪三視圖）；句剪封面改四人輪值（老查 2、阿分 2、大寶 1、小寶 1） | `ACTIVE` | 大千＋星期天 | `docs/briefs/KIDS-OUTFIT-COVER-ROTATION-2026-11/BRIEF.md` | 需省長 S 級 ImageGen 卡（≤6 次）；新三視圖待老查核准 | 大千出兩張新三視圖交老查審 | 未設定 |
| THREADS-CAROUSEL-HOOK-2026-11 | IG 輪播復工（每集必做，週一 12:15）＋Threads 週一至週三 12:15 輪播鉤子文；上架順序改為 Firstory → FB → IG 輪播 → Threads → 短片 | `ACTIVE` | 星期天（執行）＋阿派 | `docs/briefs/THREADS-CAROUSEL-HOOK-2026-11/BRIEF.md` | Threads 排程能否附圖、能否預排第一則回覆未實測；IG 工具配色可能與 `DESIGN.md` 不一致 | Codex 依 BRIEF 待辦 1 至 4，下一集試行 | 下一集上架前 |
| FB-STORY-SHORTS-2026-11 | 每週 6 支句剪同片同時段上 FB 粉專限動（原檔預排，不轉發 Reel）；週四加網誌連結格；試點 S4EP4、S4EP5 兩週 | `ACTIVE` | 星期天（執行）＋阿派；真短驗析記數據 | `docs/briefs/FB-STORY-SHORTS-2026-11/BRIEF.md` | Business Suite 能否預排粉專影片限動、是否切段、介面是否蓋字幕、連結貼紙能否預排，皆未實測 | Codex 依 BRIEF 待辦 2 用 S4EP3 舊片實測並回報老查；全過才列入 S4EP4 授權包 | S4EP4 句剪開排前 |
| MAC-SITE-NPM-VULN | 網站 `site/` npm 套件 19 個漏洞（含 1 critical），2026-10-14 Mac 同步時發現未修 | `ACTIVE` | Codex（執行） | 原 MAC-SYNC-2026-10-14 紀錄 | Windows 公司電腦不裝軟體，只能在 Mac 處理 | 下次用 Mac：`site/` 跑 `npm audit`，先修 critical；`npm audit fix` 後本機 build 通過才 commit，不用 `--force`，有破壞性升級先回報 | 下次使用 Mac 時 |
| RELEASE-FLOW-FIX-2026-11 | 老查 2026-11-05 交辦：①上架流程兩種起始狀態（有／無阿分上架包）②句剪字幕框圓角 30＋行內重點字換色 ③beyond-ans.com 每週一連動更新（網誌／影音分類）。**先做①②，完成後才做③** | `ACTIVE` | 教父＋阿派＋星期天；網站段廠長 | `docs/briefs/RELEASE-FLOW-FIX-2026-11/BRIEF.md` | 無；老查 2026-11-05 已回覆全部衝突（主題文維持原排程、週四 Threads 改長文、網誌圖維持啊問、照常審查、網站週一批次），並新增上架順序 Firstory → FB／Threads 排程 → 短影音 | A 母版已由 Claude 寫回（2026-11-05）；Codex 拉新版後以 S4EP3 驗證 A，並出 B 字幕樣張（B 的母版待樣張核准後由 Claude 改） | 下一集上架前（Asia/Taipei） |
| STORY-BANK-PILOT | 歷集逐字稿切成「案例／原話」索引，供居易、句剪選句、開講選段跨集取材；索引放私人位置，repo 只放腳本與規格 | `ACTIVE` | 廠長＋居易 | `tools/story-bank/BRIEF.md` | S4EP1＋EP2 已入庫 105 筆（EP1 已對齊公開版剪輯）；待老查用公開版抽查 10 筆 | 抽查通過後改居易 SKILL.md 接素材庫；EP3、EP4 公開讀回後補入 | 未設定 |
| PERFORMANCE-BASELINE | Podcast 跨集第 7／30 天成效基準累積 | `ACTIVE` | 成長與知識總監 | `output/podcast-performance-patterns.md` | 樣本尚不足以升級為規則 | 下一集按同一口徑補第 7 天資料 | 下次符合觀察日的單集 |
| PRODUCTION-RETRO | 動畫製作缺失復盤與精進迴路（2026-10-13 老查提出）：把每支成品被退回的原因收集起來，歸因到 Skill 母版的哪一條沒寫清楚或沒被遵守，再改進 SOP，讓製作團隊越做越符合要求。範圍只限製作品質，不含播放成效（成效仍歸成析 T6） | `ACTIVE` | 阿派（記錄）＋鐵雄（歸因）＋師傅（改 SOP）；廠長提供說明 | `docs/CEO_CONTROL_TOWER.md` 第 6 節「製作復盤與精進迴路」、`docs/PRODUCTION_RETRO_LOG.md`、`codex/agents/qa_auditor.toml`（FAIL 分級與缺失歸因欄） | 2026-10-13 老查核准：三種來源都收（鐵雄 FAIL＋阿維 REVISE／REJECTED＋老查改稿）、每週日 21:00 前交週復盤、只有師傅能改 SOP。紀錄表目前沒有任何資料，第一次週復盤要等有退回才有內容 | 阿派從下一次退回開始記錄；鐵雄下一份報告起填 FAIL 分級與缺失歸因 | 2026-10-18（週日）21:00 第一次週復盤 |
| RELEASE-AUTO-FIRST-RUN | 上架授權包與自動排程的首次實測（規則與工具 2026-10-14 完成，平台端皆未實跑） | `PENDING_APPROVAL` | 星期天（短片／Firstory／Threads）＋油管（長片） | `skills/podcast-publish/SKILL.md` 第 6 節；`tools/youtube-upload.js` 錯誤路徑已本機測試 | Firstory 由瀏覽器按預約、YouTube `publishAt` 回傳、Shorts 自訂封面生效、Threads 網頁版原生排程、Studio「變造或合成內容＝否」，五項都未經平台讀回 | 下一集上架時老查在旁確認：授權前只問 1 次、授權後無逐列詢問；逐項讀回上列五項並寫入 `RELEASE_EVIDENCE_REGISTER.md`；任一項失敗回報後再修工具 | 下一集上架時 |
| S4EP2-YOUTUBE-B | S4EP2 油管 B 兩支（B1 請看護是不是不孝、B2 長照資源怎麼找），B 常態規則首跑 | `ACTIVE` | 教父（油管）＋廠長；解題、大千、正風 | `video-projects/s4ep2-youtube-b/BRIEF.md`、`OPENING_B1.md`；預算卡 `S4EP2-YOUTUBE-B`（ImageGen 合計 ≤30） | 老查審 B1 開場稿並錄音；B2 須先決定 37:15 長照費用句剪掉或加更正字卡 | 老查審稿錄音 → 對原音確認 B1 切點 → B1 鏡頭表文字版與正風查證清單 | 未設定 |
| YOUTUBE-SCENE-LIBRARY | 油管長片 16:9 水墨空景庫 6 張（家中餐桌、餐廳小店、露營、稻田小路大樹下、三合院古宅、博物館），供故事段漫畫覆蓋重複使用 | `ACTIVE` | 教父（油管）＋廠長；大千出圖 | `video-projects/youtube-scene-library/BRIEF.md`；規則 `skills/you-guan/references/growth-stage.md` | 場景清單 2026-10-28 已確認；預算卡 2026-11-03 已開（ImageGen ≤20 次） | 大千先出 B1 要用的「家中餐桌」，再出其餘 5 張 → 聯絡表整批審 | 未設定 |
| KAIJIANG-PILOT | 「開講」直式講者知識短片試點與共用嘴型元件（油管角落小頭像也用） | `PENDING_APPROVAL` | 教父＋廠長；解題、大千 | `video-projects/kaijiang-pilot/BRIEF.md`、`HANDOFF.md`；引擎 `tools/kaijiang/`；試片在私有 Drive「暫存/對嘴試作」 | 2026-11-03 老查審 v13：6 種嘴型核准；5 張姿勢肩膀破面退件。已授權以垂手原圖為底重畫「攤手」1 次驗證肩線，過了才放行其餘 4 張各 1 次（ImageGen 由 Codex 執行） | 老查審 v13 試片 → 頭身分層合成；阿分姿勢圖另開卡 | 未設定 |
| YT-AGENT-SKILL-EVAL-2026-11 | 外部 Skill 評估落地：①競品爆款雷達腳本（`yt-dlp`，Mac／Windows 皆可，倍數＝播放數÷頻道中位數）②句剪開頭檢查卡回測 | `ACTIVE` | 多利＋小渡／小市；真短驗析回測；教父督導 | `docs/briefs/YT-AGENT-SKILL-EVAL-2026-11/BRIEF.md`、`EVALUATION.md`；母版 2026-11-06 已寫回 | 需省長 S 級預算卡；新增競品頻道待老查勾選 | Codex 建 `tools/yt-outlier/` 首跑並提 5 個候選頻道；真短驗析回測 12 支已發布句剪 | 未設定 |
| SLOT-COVER-RULES-2026-11-12 | Claude 2026-11-12 交辦（`514c50e`、`11e1e12`、`fa925b2`）：①星期天每週跑 `tools/weekly-shorts/check_slots.py` 排程對帳（建包前、`--package` 建包後、`--readback` 讀回後與週日收週），結束回報附 24 格對帳表 ②句剪封面期別標籤只放 `S{季}EP{集}`、主標字距 `0.07em`、第一行最多 6 字，一律用 `render_cover.py` 產出 | `ACTIVE` | 星期天＋句剪；Codex 執行（PC／Mac 皆同） | `skills/podcast-publish/SKILL.md` 第 6 節「週排程對帳表」；`skills/podcast-teaser-video/SKILL.md`「專屬封面」；`docs/RULE_CHANGELOG.md` 2026-11-12 兩列；樣式預覽 `output/cover-preview-2026-11-12/fri-cover-PREVIEW.png`（PC 本機，老查已核准字距） | 無。Mac 需先同步：`git pull` → `./setup.sh` → 重開 Codex；PC 已於 2026-11-12 跑 `sync-claude.ps1` PASS | S4EP3 週 6 張封面以新樣板產出（7 字第一行改寫成 6 字內）；建授權包前先跑 `check_slots.py` 取得 PASS | S4EP3 週授權包建包前 |
| CREATOR-OS-TRAFFIC-2026-11 | 工作站加「總流量」頁第一階段：9 個平台 × D1／D7／D30，手填＋CSV 匯入寫進 D1；不跨平台相加，不接 API（第二階段另開卡） | `ACTIVE` | 廠長（Codex 執行）＋成析（口徑） | `docs/briefs/CREATOR-OS-TRAFFIC-2026-11/BRIEF.md` | LINE 改動已保留並提交（`908b3d0`）；需省長 S 級卡 | PC 白天：Codex 在分支 `feat/creator-os-traffic` 寫程式＋lint／build、Firstory 匯出實測、S4EP3／S4EP4 數字抄進 Drive CSV；Mac 今晚：npm ci、套 0007、部署、匯入、讀回（見 BRIEF「PC／Mac 拆工」） | 2026-11-13 晚（Asia/Taipei） |

## 2026-09-28 管理分工更新

YouTube 長片相關任務由教父管理油管，沿用既有 Task ID、素材與核准證據。上表舊單集若仍列 YouTube 缺件，只代表獨立長片尚未完成，不再構成星期天音檔與社群流程阻塞。不得因移交擅自重做影片、取消排程或變更平台狀態。


## 2026-10-14 退役紀錄

`auto-resume-work`（Codex Goal＋同一聊天每 15 分鐘續工排程）未進 git 即退役：與 `tools/codex-resume-watch/` 功能重疊、可能重複接續，且未檢查任務卡、預算卡與 `FROZEN`。老查選擇只留 `codex-resume-watch`。Skill 本體移至 `output/retired-skills/auto-resume-work/`（未進 git），全域規則對應那行已刪除，Windows Codex 部署副本已移除；Mac 從未取得。要恢復需先補上述三項檢查並與 `codex-resume-watch` 分工。

## 新任務列入模板

```text
| TASK-ID | 範圍 | ACTIVE／PENDING_APPROVAL／BLOCKED／REVISE | 主責主管 | 文件／版本／平台證據 | 缺口 | 下一個動作＋主責 | Asia/Taipei 時點或未設定 |
```

| S4EP3-SHORTS-V4 | S4EP3 六支句剪依開頭檢查卡重切（週一、二、三、五）、換 6 張封面主標與鉤子、週一主角改阿分 | `ACTIVE` | 廠長（句剪）；鐵雄、阿維 | `docs/briefs/S4EP3-SHORTS-V4-2026-11/BRIEF.md`；本機字幕 v4、`weekly-plan.json` `revision_v4` | 新切四支待老查核聽 | Codex 重切音檔、重算字幕時間碼、出封面，交老查核聽原音包 | 週一片 2026-11-09 20:30 前（Asia/Taipei） |
| S4EP3-RELEASE | S4EP3 上架包 v0.6 執行 | `ACTIVE` | 星期天 | `output/ep-s4ep3/HANDOFF.md`、`.publish-status.json`；鐵雄 PASS、阿維 ALLOW | Firstory、FB 已排程並讀回；Threads 等 GEO 公開網址 | 老查 11/6 明確啟動短片：六段候選已切、待核聽；11/12 GEO 公開後補 Threads 授權包 | Firstory：2026-11-09 07:00（Asia/Taipei） |
| S4EP4-RELEASE | Firstory＋Threads 三篇已排程；其餘等上架包 | `BLOCKED` | 星期天 | `docs/briefs/S4EP4-RELEASE-2026-11/HANDOFF.md`、`release-summary.json`、發布證據庫 | 缺阿分上架包；短影片未啟動 | Mac 同步後先核對已排程項目，收到包才續作，禁止重傳／重排 | Firstory 2026-11-16 07:00；Threads 11/16–18 12:15 Asia/Taipei |
