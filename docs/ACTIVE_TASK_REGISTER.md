# 進行中任務總表

最後盤點：2026-09-01 10:41（Asia/Taipei）  
主責：內容營運長。  
用途：唯一列出仍需 CEO、主管或老查採取動作的內容任務。它是索引，不取代各專案的 `BRIEF.md`、`HANDOFF.md`、品牌檢查、QC 或平台證據。

## 使用規則

- 只列 `ACTIVE`、`PENDING_APPROVAL`、`BLOCKED` 與 `REVISE`。已結案或純歷史文件不列入。
- 每次任務狀態、最終檔案、平台證據或下一棒改變時，先更新本表，再更新對應專案文件。
- `PENDING_APPROVAL` 代表等老查或品牌放行；`BLOCKED` 代表缺素材、資料或外部狀態。兩者都不是「快完成」。
- 沒有明確日期時填「未設定」，不能擅自編造截止時間。

| 任務 ID | 任務與範圍 | 狀態 | 主責主管 | 最終依據／證據 | 阻塞或待放行 | 下一個明確動作 | 時點 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S3EP5-RELEASE | S3EP5 正片、主題文與一般預告的發布流轉 | `PENDING_APPROVAL` | 內容營運長 | `output/ep-s3ep5/content-decision.md`、`brand-review.md`、`episode-metadata.md` | 品牌複檢 `ALLOW`，但沒有 Firstory、YouTube、FB、IG 的平台讀回證據 | 逐一讀回各平台草稿／排程／公開狀態，填入發布證據庫 | 未設定 |
| S3EP5-H1 | S3EP5 剪紙精華 1 v2 跨平台發布 | `PENDING_APPROVAL` | 內容營運長＋製作總監 | `output/ep-s3ep5/s3ep5-highlight-1-v2-qc.md`，最終 QC 4 項 `PASS` | 未記錄最終檔是否再改、品牌複核與平台草稿／排程證據 | 鎖定最終檔，確認片尾宣稱與文案，完成品牌與平台證據 | 未設定 |
| S3EP5-H2 | S3EP5 剪紙精華 2 動態確認與發布 | `PENDING_APPROVAL` | 內容營運長＋製作總監 | `output/ep-s3ep5/s3ep5-highlight-2-qc.md` | 文件明載待老查確認完整動態，未上傳、未排程 | 老查確認成片或退回修訂；確認後重做最終檔 QC 與排程 | 未設定 |
| S3EP5-TEASER | S3EP5 一般預告動態成片 | `PENDING_APPROVAL` | 內容營運長＋製作總監 | `video-projects/s3ep5-hyperframes-teaser/BRIEF.md` | 成品尚待老查確認；未確認不得高畫質渲染或建貼文 | 取得老查確認或改稿方向 | 未設定 |
| S3EP5-YT | S3EP5 YouTube 對話版 | `BLOCKED` | 內容營運長＋製作總監 | `video-projects/youtube-window-s3ep5/.media/index.md` | 缺 `BRIEF.md`、`STORYBOARD.md`、`HANDOFF.md`，無法判斷範圍與完成定義 | 補任務卡與 `BRIEF.md`，再決定是否進入製作 | 未設定 |
| S3EP1-YT | S3EP1 YouTube 對話版正式渲染 | `PENDING_APPROVAL` | 製作總監 | `video-projects/youtube-window-s3ep1/HANDOFF.md` | 試作已完成；正式 high quality render 須老查確認 | 老查看試作後回覆「確認渲染」或提出修訂 | 未設定 |
| S3EP3-YT-TEST | S3EP3 YouTube 客廳對話版講者特寫校準 | `BLOCKED` | 製作總監 | `docs/youtube-window-session-checkpoint-2026-08-28.md` | 缺含起訖時間、講者與台詞的逐字稿 | 取得逐字稿，依講者與觀點轉折重排特寫 | 未設定 |
| S3EP3-COLLAGE | S3EP3 剪紙精華構圖 proof 與最終音訊裁切 | `PENDING_APPROVAL` | 內容營運長＋製作總監 | `video-projects/s3ep3-paper-collage/BRIEF.md` | 只允許無聲構圖 proof；構圖與最終音訊時間碼未確認 | 確認構圖與音訊裁切，才可進交付 MP4 | 未設定 |
| RECORDING-COMPASSION | 「慈悲的傲慢與同行的溫度」錄音前審核 | `REVISE` | 品牌總監＋成長與知識總監 | `output/錄音前審核_慈悲的傲慢與同行的溫度.md` | 真人刑案與其他具體事實尚未查證 | 查證原始來源；無法查證就撤下相關段落 | 未設定 |
| PERFORMANCE-BASELINE | Podcast 跨集第 7／30 天成效基準累積 | `ACTIVE` | 成長與知識總監 | `output/podcast-performance-patterns.md` | 樣本尚不足以升級為規則 | 下一集按同一口徑補第 7 天資料 | 下次符合觀察日的單集 |

## 新任務列入模板

```text
| TASK-ID | 範圍 | ACTIVE／PENDING_APPROVAL／BLOCKED／REVISE | 主責主管 | 文件／版本／平台證據 | 缺口 | 下一個動作＋主責 | Asia/Taipei 時點或未設定 |
```
