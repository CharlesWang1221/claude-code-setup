# 油管獨立狀態與上傳交接

## 狀態唯一母版

在當次 `output/{project-folder}/.youtube-status.json` 保存油管狀態，Podcast 通常沿用 `output/ep-{slug}/`。非 Podcast 使用當次核准工作名稱；不為管理拆分搬動既有媒體。此檔由油管維護，星期天不將它納入完成條件。

```json
{
  "owner": "you-guan",
  "manager": "小查",
  "task_id": null,
  "stage": "INPUT_REVIEW",
  "inputs": { "audio": null, "transcript": null, "source_video": null },
  "format": null,
  "script_approved": false,
  "keyframes_approved": false,
  "preview_approved": false,
  "assets": { "thumbnail_ready": false, "end_card_ready": false },
  "render_file": null,
  "thumbnail": null,
  "metadata_file": null,
  "qc_passed": false,
  "brand_review": null,
  "final_approved": false,
  "uploaded": false,
  "videoId": null,
  "target_at": null,
  "scheduled": false,
  "published": false,
  "evidence": []
}
```

階段可用 `INPUT_REVIEW`、`PLAN_REVIEW`、`KEYFRAMES_REVIEW`、`PREVIEW_REVIEW`、`RENDERING`、`REVISION_REQUIRED`、`FINAL_REVIEW`、`READY_FOR_UPLOAD`、`UPLOADED_PRIVATE`、`SCHEDULED`、`PUBLISHED`。核准與證據須對應版本。

接手舊集時，先讀 `.publish-status.json` 的 `video_rendered`、`youtube_assets`、`youtube`、`inputs.thumbnail`、`release_schedule.youtube_scheduled` 與已有平台證據，按真實證據承接到新檔。未知欄位與舊旗標保留，不刪除、不重設；缺證據標待驗證，不猜已完成。若新舊資料不一致，讀回檔案／平台再決定，不盲目覆蓋。

## 沿用既有上傳工具

`tools/youtube-upload.js` 目前讀取 `output/{project-folder}/youtube.txt` 和舊 `.publish-status.json`，尚未讀取油管新狀態。新 `.youtube-status.json` 是長片進度唯一母版，舊檔相關欄位只作工具相容鏡像與歷史保留。

獲上傳授權後，先將核准文案寫成 `youtube.txt`，並局部合併 `.publish-status.json` 的 `youtube_assets.render_file` 與 `inputs.thumbnail`，指定唯一核准長片與縮圖。路徑需能由工具的 repo 根目錄解析，私人素材不因此提交 Git。保留舊檔其他欄位，不將油管狀態同步成星期天待辦。

```bash
node tools/youtube-upload.js --episode <project-folder>
```

呼叫前用 `ffprobe` 核對正確 16:9 長片、影音軌與時長，不能讓工具自行在多個 MP4 中挑選。若工具報錯或縮圖上傳失敗，先到平台確認影片是否已成功建立，保存 videoId，避免整支再次上傳。

上傳成功只設 `uploaded` 與 `videoId`，視讀回結果標 `UPLOADED_PRIVATE`；核准並完成 Studio 排程後才設 `scheduled`。`target_at` 必須是當次明確長片日期，含 `+08:00`，不能從 Podcast 發布日自動推定。將平台證據寫回新檔及 `docs/RELEASE_EVIDENCE_REGISTER.md`；必要時局部更新舊長片旗標相容鏡像，但不更新星期天其他完成狀態。
