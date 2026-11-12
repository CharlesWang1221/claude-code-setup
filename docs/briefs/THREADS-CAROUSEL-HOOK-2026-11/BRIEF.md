---
task_id: THREADS-CAROUSEL-HOOK-2026-11
status: ACTIVE
owner: 星期天（執行）＋阿派（派工）；規則由 Claude Code 管理層維護
created_at: 2026-11-12 Asia/Taipei
last_updated: 2026-11-12 Asia/Taipei
source: 老查 2026-11-12 與 Claude Code 討論定案
---

# IG 輪播復工＋Threads 輪播鉤子文

## 老查定案（2026-11-12）

- 上架順序：Firstory 全部內容 → FB 主題文 → IG 輪播 → Threads 輪播鉤子文 → 短片＋封面。前四步讀回前不做短片。
- IG 輪播 5 張＋金句圖 5 張恢復每集必做；輪播週一 12:15 與 FB 主題文同時段。
- Threads 週一至週三 12:15 各 1 則，依序配 `carousel_2`、`carousel_3`、`carousel_4`，看圖寫鉤子，導流回 Podcast；週四 Threads 12:15 居易長文＋大千圖不變。
- 規則母版已改：`skills/podcast-publish/SKILL.md`（上架順序、第 3 步 IG 圖、Threads 輪播鉤子文、對帳表圖文 4 格）、`AGENTS.md` 每週節奏。

## 為什麼要做

輪播自 S3EP11 起連續 5 集沒做（S4EP1 `.publish-status.json` 為 `ig_images: false`），S3EP7、S3EP10 做好的輪播在證據庫仍是「待發布」。它被歸成「並行、只阻塞自己」，又不在對帳表內，所以漏了沒人發現。

## Codex 待辦（依序）

1. `git pull --ff-only`，Windows 跑 `.\tools\sync-codex.ps1`；開工前跑來源檢查取得 PASS。
2. **IG 工具健檢**：用 S4EP3 素材試跑 `tools\ig-images\run_ig.ps1 -EpSlug s4ep3 -CoverImage <S4EP3 Firstory 1400 圖>`，只產圖不發布。核對：5 張輪播＋金句圖皆 1080 × 1080；第 2 至 4 張重點不是空白；配色與字體符合現行 `DESIGN.md`（工具內寫死的是舊色 navy／teal／coral，跟 `DESIGN.md` 不一致就回報老查決定改不改，不自行改品牌色）。結果交鐵雄技術審。
3. **Threads 排程實測**（不得立即發布，用 2 天後的時段再刪除，或用老查同意的測試貼文）：
   - 網頁版排程能否附 1 張圖片，公開後圖是否在。
   - 排程貼文能否預先加「第一則回覆」。**若做不到**，改用備案：Firstory 連結放主文最後一行，回報老查確認是否接受，不得叫人每天 12:15 手動回覆。
4. **對帳工具**：`tools/weekly-shorts/check_slots.py` 加入圖文 4 格（IG 輪播週一 12:15、Threads 輪播鉤子文週一至週三 12:15），缺一格判 `BLOCKED`；完成前依 SKILL 在授權包人工核對。改完交 reviewer。
5. **下一集試行**：依新順序完整走一次，4 格圖文都要有平台讀回證據，寫入 `docs/RELEASE_EVIDENCE_REGISTER.md`。

## 驗收

- 下一集證據庫有 IG 輪播 1 則＋Threads 輪播鉤子文 3 則的公開頁讀回（帳號、圖、文案、主題、連結）。
- 三則鉤子文與 FB 主題文、IG caption、同日短片 Threads 文案都不重複，已過阿維。
- 第 3 步實測結果寫回本 BRIEF；若改用備案，Claude 依老查決定修 SKILL。

## 停止線

- 不得為了趕排程把 Threads 改成立即發布。
- IG 輪播不得勾「分享至 Facebook」或「分享到 Threads」。
- 規則有問題回報老查交 Claude 修，不自行改 SKILL。
