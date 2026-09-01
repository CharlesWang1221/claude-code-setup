# 文件治理盤點｜2026-09-01

盤點時間：2026-09-01 10:41（Asia/Taipei）  
範圍：repo 內 Markdown 文件。  
執行方式：只讀分類與風險標記。本次沒有搬移、刪除、改名或封存任何既有文件。

## 結論

目前可辨識 162 份 Markdown。制度母版已具備基本骨架；Claude 保留為輔助執行端，Codex 是主要操作者與衝突裁決來源。S3EP5、S3EP1、S3EP3 的內容任務仍有未完成的發布或確認關卡，不能被標為完成。

本次判定為 `ACTIVE` 的任務不代表正在背景自動執行，只表示下次接續工作時仍應先讀、更新與處理。`ARCHIVED` 是建議狀態，不是已封存動作。

## A. 憲法母版

| 文件 | 建議狀態 | owner | 盤點結果與下一步 |
| --- | --- | --- | --- |
| `AGENTS.md` | `ACTIVE` | CEO | Codex 全域工作母版。已連結 CEO 控制台與文件治理規則。 |
| `BRAND_CONTEXT.md` | `ACTIVE` | 品牌總監＋CEO | 品牌母版。對外內容任務必讀。 |
| `DESIGN.md` | `ACTIVE` | 品牌總監＋製作總監 | 視覺規格母版。視覺任務必讀。 |
| `docs/CEO_CONTROL_TOWER.md` | `ACTIVE` | CEO | 已定義主管、任務卡、停止線與內容營運長。 |
| `docs/DOCUMENT_GOVERNANCE.md` | `ACTIVE` | 系統與資產總監 | 已定義文件權威、生命週期與盤點格式。 |
| `codex/AGENTS.global.md` | `ACTIVE` | CEO | Codex 跨專案全域摘要。它已明確指向根目錄 `AGENTS.md`，不應重複擴寫。 |

## B. 需處理的規則與相容性風險

| 文件或群組 | 建議狀態 | 問題 | 所需決策或動作 |
| --- | --- | --- | --- |
| `CLAUDE.md` | `ACTIVE` | Claude 保留為輔助執行端。現有共用規則可繼續同步，但權威衝突不得由 Claude 文件裁決。 | 保留 Claude 專屬 auto-memory、工具與相容說明；共用規則變更時，以 `AGENTS.md` 為源頭同步。 |
| `apps/creator-os/CLAUDE.md` | `ACTIVE` | Claude 可支援 Creator OS，但不是產品規則母版。 | 下次 Creator OS 變更前做逐條比對；保留必要框架限制與 Claude 專屬說明，共用規則以子專案 `AGENTS.md` 為準。 |
| `video-projects/*/AGENTS.md`、`CLAUDE.md` | `ACTIVE`，但降權 | 多為 HyperFrames 產生的專案技術規則，內容大幅重複，且不可覆蓋 repo 的品牌與發布規則。 | 只在該專案執行 HyperFrames 時引用；不要合併進全域規則，也不要因重複而現在刪除。 |
| `skills/*/SKILL.md` 與 `references/*.md` | `ACTIVE` | 已有 repo 版母版，但本機安裝版與外部 `tools/video-use` 可能版本漂移。 | 每次啟動流程先讀 repo 對應 Skill；重大改版或換機時再做 repo／安裝版同步盤點。 |

## C. 進行中或待確認的內容任務

| 任務與控制文件 | 建議狀態 | 證據 | 下一個明確動作 |
| --- | --- | --- | --- |
| `output/ep-s3ep5/content-decision.md`、`episode-metadata.md`、`asset-manifest.md`、`brand-review.md` | `ACTIVE` | 品牌複檢為 `ALLOW`，但 `brand-review.md` 明示發布日期、平台回讀網址與排程證據尚未取得。 | 內容營運長先確認正片、主題文、一般預告的各平台實際狀態，補回讀證據。 |
| `output/ep-s3ep5/s3ep5-highlight-1-v2-qc.md` | `PENDING_APPROVAL` | 最終 QC 4 項 `PASS`，但文件只有「完整節目已上線／Firstory 收聽」的片尾描述，未有平台草稿或排程證據。 | 確認最終檔沒有再變動後，重核平台文案與片尾宣稱，再建立草稿或排程。 |
| `output/ep-s3ep5/s3ep5-highlight-2-qc.md` | `PENDING_APPROVAL` | 文件明載「待老查看完整動態後確認。未上傳、未排程。」 | 老查確認動態成片；確認後才補最終檔 QC 與跨平台排程證據。 |
| `video-projects/s3ep5-hyperframes-teaser/BRIEF.md` | `PENDING_APPROVAL` | 明載成品先供老查確認，未確認不得高畫質渲染、建貼文或排程。 | 取得老查確認或改稿方向。 |
| `video-projects/youtube-window-s3ep5/` | `ACTIVE`，控制文件不足 | 目錄有素材索引與 HyperFrames 規則，但本次未發現該專案自己的 `BRIEF.md`、`STORYBOARD.md` 或 `HANDOFF.md`。 | 在任何製作或上傳前補建任務卡與 `BRIEF.md`，否則不能判斷目標、時長、版本與下一棒。 |
| `video-projects/youtube-window-s3ep1/HANDOFF.md` | `PENDING_APPROVAL` | 試作完成；正式 high quality render 與 YouTube 上傳都必須老查明確確認。 | 老查預覽後決定「確認渲染」或提出修訂。 |
| `video-projects/youtube-window-s3ep3-test/BRIEF.md`、`STORYBOARD.md`、`character-layout-notes.md` | `BLOCKED` | 2026-08-28 檢查點要求取得含講者與起訖時間碼的逐字稿，現有特寫尚未校準。 | 取得逐字稿後，才可依講者與轉折重新排特寫。 |
| `video-projects/s3ep3-paper-collage/BRIEF.md` | `PENDING_APPROVAL` | 僅能製作無聲構圖 proof，且最終音訊裁切與構圖仍待確認。 | 確認構圖與主音檔時間碼；未確認前禁止輸出交付 MP4。 |
| `output/錄音前審核_慈悲的傲慢與同行的溫度.md` | `PENDING_APPROVAL` | 阿維判定 `REVISE`，涉及未核實真人刑案與其他事實風險。 | 先用原始報導、警方或法院公開資料查證；無法查證就撤下相關事件。 |

## D. 知識資產與已結案候選

| 文件或群組 | 建議狀態 | owner | 管理方式 |
| --- | --- | --- | --- |
| `output/podcast-performance-patterns.md` | `ACTIVE` | 成長與知識總監 | 是跨集基準表。下一集第 7 天依相同口徑補資料，不以單集升級規則。 |
| `output/ep-s3ep3/performance-review-7d.md` | `LOCKED` | 成長與知識總監 | 2026-08-25 的觀察證據。若補數據，建立新版本或補充段落，不改寫原結論。 |
| `output/ep-s2ep1/show-notes.md`、`output/ep-s2ep2/show-notes.md`、`output/ep-s2ep12/show-notes.md`、`output/ep-s3ep1/show-notes.md` | `ARCHIVED` 候選 | 內容營運長 | 視為已發布／歷史內容資產。除非平台更正或重製，不納入日常待辦。 |
| `site/src/content/blog/*.md` | `LOCKED` | 成長與知識總監＋品牌總監 | 已發布網站內容。修訂必須記錄更正原因與公開影響。 |
| `journals/*.md`、`s2ep12-snapshot.md` | `ARCHIVED` | 老查 | 私人或歷史紀錄，只在老查要求提煉時處理。 |
| `docs/youtube-window-production-log-2026-08-27.md`、`docs/youtube-window-session-checkpoint-2026-08-28.md` | `ARCHIVED` 候選 | 製作總監 | 歷史經驗仍可參考；可提煉的長期規則已部分進入 `AGENTS.md`。 |

## E. 技術與系統文件

| 文件或群組 | 建議狀態 | owner | 盤點結果 |
| --- | --- | --- | --- |
| `apps/creator-os/README.md`、`apps/creator-os/AGENTS.md`、`apps/creator-os/docs/*.md` | `ACTIVE` | 系統與資產總監 | 產品與跨電腦備份規則。程式或部署改動時更新，不列入 Podcast 日常流轉。 |
| `tools/README.md`、`tools/*/README.md`、`mcp-setup.md` | `ACTIVE` | 系統與資產總監 | 安裝與工具操作文件。必須避免 token、帳密、私人路徑。 |
| `blender-projects/*/README.md`、`ae/export-notes.md` | `ARCHIVED` 候選 | 製作總監 | 除非重啟 Blender 專案，否則不進日常控制台。 |

## F. 本月處理順序

1. 不要先整理歷史檔。先釐清 S3EP5 各平台的實際發布與排程證據，避免 `ALLOW` 被誤讀成已發布。
2. 替 `video-projects/youtube-window-s3ep5/` 補最小控制文件，否則這個專案沒有可管理的終點。
3. 老查確認 S3EP5 精華 2 與一般預告的動態成片，或明確退回修訂。
4. 保留根目錄 `CLAUDE.md` 作為 Claude 輔助執行端文件；共用規則從 `AGENTS.md` 同步，避免雙向漂移。
5. 上述進行中任務結案後，再由老查決定是否將歷史文件真正搬入封存結構。

## 需要老查裁決

- S3EP5 的正片、主題文、一般預告、精華 1，各平台目前究竟是草稿、已排程、已上傳，還是已公開？沒有平台讀回證據時，控制台一律視為 `待驗證`。
- 是否繼續製作 `youtube-window-s3ep5`？若是，需補充影片目標、時長、輸出平台與素材版本。
