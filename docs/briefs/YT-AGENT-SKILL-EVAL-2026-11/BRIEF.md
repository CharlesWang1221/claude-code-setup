---
task_id: YT-AGENT-SKILL-EVAL-2026-11
status: ACTIVE
owner: 多利（腳本）＋小渡／小市（歸類）＋真短驗析（回測）；教父督導
created_at: 2026-11-06 Asia/Taipei
last_updated: 2026-11-06 Asia/Taipei
source: Claude Code 管理層評估外部 Skill，老查 2026-11-06 回覆「以你建議執行」
---

# 競品爆款雷達＋開頭檢查卡回測

評估全文：同資料夾 `EVALUATION.md`。母版已由 Claude 寫好，Codex 只執行，不改規則：

- `skills/daily-routines-manager/SKILL.md`「選題情報週報」的競品爆款雷達
- `skills/podcast-teaser-video/SKILL.md`「開頭檢查卡」
- `skills/podcast-performance-review/SKILL.md` 第 2 節「倍數」

## 開工前

- `git pull` → Mac 跑 `./setup.sh`（或 `tools/check-skill-authority.sh` 取得 PASS）。
- 先向省長申請 S 級預算卡，兩項任務共用。沒有預算卡不得開工。
- **不得安裝或複製外部 repo 的 Skill**（`Jakeschincariol/youtube-agent-skill`）到任何 skills 目錄。演算法自己寫，不搬原檔。

## T1：競品爆款雷達腳本（Mac 或 Windows）

2026-11-06 老查在 Windows 公司電腦實測不擋，`yt-dlp` 列為 Windows 例外，兩台都能跑。安裝一律用使用者層級：`python -m pip install --user yt-dlp`（Mac 用 `python3`），不用管理員權限、不裝 deno 等 JS 執行環境。

Claude 實測紀錄（2026-11-06，yt-dlp 2026.10.26）：

- `--flat-playlist` **拿不到播放數**，只有標題、長度、網址。播放數要逐支讀：`--skip-download --print "%(view_count)s..."`，約每支 2.5 秒。
- 每支會跳「No supported JavaScript runtime」警告，只影響下載格式，讀資料不受影響，過濾掉即可。
- 頻道沒有某個分頁時（例：我們頻道沒有 `/videos`），yt-dlp 會報 `does not have a videos tab`，腳本要當成「該格式 0 支」處理，不要整個中止。
- 頻道網址優先用 `https://www.youtube.com/channel/UC...`，比 `@代號` 穩；中文代號可用，但要 URL 編碼正確。

1. 建 `tools/yt-outlier/outlier.py`，Python 標準函式庫＋以 `python -m yt_dlp` 呼叫（不依賴 PATH）。
   - 輸入 `tools/yt-outlier/channels.txt`：一行一個頻道，格式 `頻道名稱<TAB>YouTube 頻道網址<TAB>tw／intl／self`。
   - 每個頻道逐支讀最近 20 支長片與最近 20 支 Shorts（`--limit` 可調）。12 個頻道約 20 分鐘，跑在背景。不登入、不帶 cookies、不用老查帳號。
   - 長片、Shorts **分開**算各自的播放數中位數；同一格式少於 4 支就跳過，在報告列出跳過原因。
   - 倍數＝播放數 ÷ 該頻道該格式中位數；預設門檻 2.0，可用 `--min` 調整。
   - 我方頻道也放進清單、標 `self`，只當參照，不列入爆款。
   - 輸出 `output/weekly-shorts/{週一日期}/outlier-radar.json` 與 `.md`（倍數、播放數、中位數、頻道、標題、網址、格式）。
2. `channels.txt` 初版：
   - 現有雙週競品監控 7 個對象中有 YouTube 頻道的（名單見 `skills/daily-routines-manager/routines/daily-competitor-monitor-7.md`），網址由 Luna 唯讀查找，查不到就標 `N/A`，不猜。
   - 《不標準答案》自己的頻道 `https://www.youtube.com/channel/UCE-QusSupACm0Lk7D0ThHLQ`（代號 `@不標準答案`），標 `self`。
   - **另提 5 個台灣中型 Podcast 的 YouTube 頻道作為候選**，各附訂閱數與一句為何同賽道。這 5 個先不寫進 `channels.txt`，交老查勾選。
3. 首跑一次，回報：2 倍以上清單前 10、跳過的頻道與原因、執行時間。腳本與 `channels.txt` commit 進 repo；輸出在 `output/`，不 commit。
4. 小渡／小市讀首跑結果，依 SKILL.md 歸類鉤子並寫「能不能做」。歸類用中文判斷，不用英文 regex。

完成定義：腳本在 Mac 跑完無錯；`outlier-radar.md` 存在；候選頻道清單已交老查。

## T2：開頭檢查卡回測（真短驗析）

製作者不得評自己做的那支。

1. 樣本：`docs/RELEASE_EVIDENCE_REGISTER.md` 有平台讀回證據的已發布句剪，至少 12 支；不足 12 支就全收，結論標 `UNRESOLVED`。
2. 每支依 SKILL.md 五面向標高／中／低（只看開頭第一句與封面主標）。**先評分，再看數據**，避免看了數字回頭調分。
3. 對照平台數據：YouTube Shorts「觀看 vs 滑走」比例與平均觀看百分比；IG／FB 有就附。
4. 輸出 `output/short-video-experiments/hook-check-backtest-2026-11.md`：每支一列（評分、最低項、數據）＋一段結論，三選一：
   - 最低項有 `低` 的那批，數據明顯較差 → 建議升為硬規則
   - 看不出差別但最低項提醒仍有用 → 維持只記錄
   - 完全無關 → 建議撤除
5. 結論交老查，由 Claude 管理層改母版。Codex 不自行改 SKILL.md。

## 停止線

- 任何會登入、留言、追蹤或寫入平台的操作都不做，這個任務只讀公開資料。
- `channels.txt` 只放公開頻道名稱與網址，不放帳號、token、私人筆記。
- 雷達的鉤子歸類不得寫成「它爆是因為⋯」。

## 目前狀態

- 2026-11-06：母版已寫回（見 `docs/RULE_CHANGELOG.md` 同日）。
- 2026-11-06：Windows 實測可用（已 `pip --user` 安裝），T1、T2 都可在任一台開工。
