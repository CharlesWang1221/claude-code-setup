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

## 新增變更模板

```text
| YYYY-MM-DD | 規則文字與影響 | 新增／修改／廢止 | 觸發事件 | 唯一母版 | 如何驗證、何時回看 |
```

廢止規則時，保留原列並新增一列說明取代文件與日期。不得刪除歷史變更來假裝規則從未存在。
