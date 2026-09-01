# 平台發布證據庫

最後盤點：2026-09-01 10:41（Asia/Taipei）  
主責：內容營運長。  
用途：將「素材已做完」與「平台已處理」切開。未填入平台讀回證據的列，一律視為 `待驗證`，不得對外或對老查宣稱已上傳、已排程或已公開。

## 證據規則

- `草稿已建立`：平台草稿畫面或可讀回草稿 ID。
- `已排程`：平台顯示的 Asia/Taipei 發布時間與貼文／影片 ID。
- `已上傳`：平台成功回應與可讀回網址或 ID。
- `已公開`：公開網址可開啟，並核對標題、封面、文案與成片版本。
- 同一素材更新檔案、字幕、音訊、片尾或文案後，先前證據失效，必須建立新列或明確標示新版本。

## 現況

| 資產 ID | 平台與用途 | 最終版本／依據 | 目前狀態 | 已有平台證據 | 預定／實際時間 | 公開網址／平台 ID | 下一個驗證動作 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S3EP5-FULL-FIRSTORY | Firstory 正片 | `output/ep-s3ep5/episode-metadata.md` | `待驗證` | 無 | 未記錄 | 未記錄 | 讀回草稿、排程或公開狀態；填入 ID 與時間 |
| S3EP5-FULL-YOUTUBE | YouTube 正片 | S3EP5 metadata 已有；成片版本未在本庫確認 | `待驗證` | 無 | 未記錄 | 未記錄 | 確認最終成片、Studio 狀態與網址／影片 ID |
| S3EP5-TOPIC-FB | Facebook 本集主題文 | `content-decision.md`、`brand-review.md` | `待驗證` | 品牌 `ALLOW` 不等於平台證據 | 未記錄 | 未記錄 | 讀回 FB 草稿、排程或公開貼文 ID |
| S3EP5-TOPIC-IG | Instagram 本集主題文 | `content-decision.md`、`brand-review.md` | `待驗證` | 品牌 `ALLOW` 不等於平台證據 | 未記錄 | 未記錄 | 讀回 IG 草稿、排程或公開貼文 ID |
| S3EP5-TEASER | FB／IG 一般預告 | `video-projects/s3ep5-hyperframes-teaser/BRIEF.md` | `待老查確認` | 無。未確認不得渲染或建貼文 | 未設定 | 未記錄 | 先取得成片確認；再依平台分列建立證據 |
| S3EP5-H1-IG | Instagram Reels 剪紙精華 1 v2 | `s3ep5-highlight-1-v2-qc.md` | `待驗證` | QC `PASS`，無平台證據 | 目標週三 20:30，實際未記錄 | 未記錄 | 鎖版本、品牌複核後讀回 IG 草稿或排程 |
| S3EP5-H1-FB | Facebook Reels 剪紙精華 1 v2 | `s3ep5-highlight-1-v2-qc.md` | `待驗證` | QC `PASS`，無平台證據 | 目標週三 20:30，實際未記錄 | 未記錄 | 鎖版本、品牌複核後讀回 FB 草稿或排程 |
| S3EP5-H1-SHORTS | YouTube Shorts 剪紙精華 1 v2 | `s3ep5-highlight-1-v2-qc.md` | `待驗證` | QC `PASS`，無平台證據 | 目標週三 20:30，實際未記錄 | 未記錄 | 鎖版本、品牌複核後讀回 YouTube 草稿或排程 |
| S3EP5-H2-IG | Instagram Reels 剪紙精華 2 | `s3ep5-highlight-2-qc.md` | `待老查確認` | 文件明載未上傳、未排程 | 目標週五 12:00，實際未記錄 | 未記錄 | 先確認完整動態與最終檔 QC，再建草稿 |
| S3EP5-H2-FB | Facebook Reels 剪紙精華 2 | `s3ep5-highlight-2-qc.md` | `待老查確認` | 文件明載未上傳、未排程 | 目標週五 12:00，實際未記錄 | 未記錄 | 先確認完整動態與最終檔 QC，再建草稿 |
| S3EP5-H2-SHORTS | YouTube Shorts 剪紙精華 2 | `s3ep5-highlight-2-qc.md` | `待老查確認` | 文件明載未上傳、未排程 | 目標週五 12:00，實際未記錄 | 未記錄 | 先確認完整動態與最終檔 QC，再建草稿 |
| S3EP1-YT | S3EP1 YouTube 對話版 | `video-projects/youtube-window-s3ep1/HANDOFF.md` | `待老查確認` | 試作通過格式檢查；正式 high quality 未渲染 | 未設定 | 未記錄 | 老查確認渲染後，驗證正式檔並建立 YouTube 證據 |

## 新發布資產列入模板

```text
| ASSET-ID | 平台與用途 | 最終檔名／文案版本／QC | 草稿已建立／已排程／已上傳／已公開／待驗證 | 畫面、ID 或讀回資訊 | Asia/Taipei 時間 | 網址或平台 ID | 下一個驗證動作 |
```
