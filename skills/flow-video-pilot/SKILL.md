---
name: flow-video-pilot
description: 用既有 Google Flow 訂閱點數製作實景照片與固定插畫角色的短動作試片，並回收、驗收及接入核准音檔。當老查要求 Flow 圖生影片、實景加動畫或延續已核准的角色影片試作時使用。
---

# Flow 實景角色試片

本 Skill 的母版是 repo 的 `skills/flow-video-pilot/`。優先測試本機已登入的 `gflow-cli`；遇到新版 Flow 編輯器不相容時，改用已登入的 Flow 網頁。登入由老查在 Chrome 親自完成。不要讀取、複製、列印或上傳 Google cookies／Chrome profile。`gflow-cli` 是非官方瀏覽器自動化工具，介面可能變動；它不是 Google 官方 API。

## 工作順序

1. 讀當次專案的 `AGENTS.md`、`BRIEF.md`、核准構圖與音檔。角色／場景資產表及完整起始構圖須先獲核准；現成分層圖不能用整張位移假裝自然走路。
2. 依 [連線與安裝](references/connection.md) 檢查 `gflow`、Chrome、FFmpeg 與 Flow 登入。尚未登入時，只請老查在本機完成 `gflow auth login --browser chrome`；Codex 不代輸入帳密。點數餘額要讀 Flow 網頁的帳戶選單，不能依賴 `gflow credits user`。
3. 先用已核准的完整 9:16 合成圖做一段 4–8 秒圖生影片。腳本上傳前會轉成無 EXIF 的暫存 PNG。每次只生成 1 支，先看腳步接地、人物身份、筆觸、背景與影子。首段未過，不展開全長。
4. 生成前執行 `flow_video.py plan`，看輸入、模型、預估點數及輸出位置，並在 Flow 網頁核對當下的點數與模型價格。只有當次任務已授權消耗 Flow 點數時，才用 `generate --spend`。失敗後不得自動重送；先回 Flow 專案回收已提交的成品。
5. 以 `verify` 產生可讀的影片技術資訊與接觸表；逐格看角色互換、肢體變形、地面接觸與背景漂移。技術通過不代表創意核可。
6. 當所有片段都核可，才用 `assemble` 接入核准原音。丟棄生成片的音軌，不改寫 Podcast 台詞；輸出 1080 × 1920、H.264／AAC 並再次驗收。任何正式發布仍走原專案的品牌與發布閘門。

## 指令

腳本位於本 Skill 的 `scripts/flow_video.py`，使用 Python 3.9 以上標準函式庫。以下指令從 repo 根目錄執行。腳本會先找 repo 的 `.flow-tools/gflow-venv`；也可用 `GFLOW_BIN` 指定其他位置。

```bash
python3 skills/flow-video-pilot/scripts/flow_video.py doctor
python3 skills/flow-video-pilot/scripts/flow_video.py plan --start-frame /absolute/start.png --prompt-file /absolute/motion.txt --out /absolute/proof.mp4 --model omni-flash --duration 4
python3 skills/flow-video-pilot/scripts/flow_video.py generate --start-frame /absolute/start.png --prompt-file /absolute/motion.txt --out /absolute/proof.mp4 --model omni-flash --duration 4 --spend
python3 skills/flow-video-pilot/scripts/flow_video.py verify --video /absolute/proof.mp4
python3 skills/flow-video-pilot/scripts/flow_video.py assemble --clips /absolute/a.mp4 /absolute/b.mp4 --audio /absolute/approved.m4a --out /absolute/final.mp4
```

`plan` 和 `doctor` 不消耗生成點數。`generate` 每次固定 `--count 1`，建立提交紀錄；若狀態變成 `needs_review`，先人工檢查 Flow 成品，不可再跑同一命令。模型扣點以 Flow 當下畫面為準。

`gflow-cli` 目前以 Flow 的 classic 影片編輯器為操作目標。若它回報 exit 25（agentic 編輯器）或 exit 28（classic 編輯器不可達），先到 Flow 專案核對成品與點數；確認沒有提交後，才改用已登入的 Flow 網頁做單支試片。不要自動切換模型或反覆提交。CLI 登入成功只證明連線，實際影片生成仍須首支試片驗證。

2026-09-27 的 S3EP8 試片實測：這個帳戶的 Veo 3.1 Lite 僅提供 8 秒；Omni 1.1 Flash 可做 4 秒，Flow 確認畫面顯示單支 7 點。當次 `gflow-cli` 因 agentic 編輯器 exit 25，確認沒有提交後才在 Flow 網頁完成。模型長度及點數之後仍需以當次確認畫面為準。

## S3EP8 專案界線

沿用 `video-projects/s3ep8-live-action-animation-pilot/` 的核准條件：山谷照片原色、四人核准比例與中段草皮、接觸影、核准精華 2 原音。當次起始構圖與角色參考圖保留在私有工作區；不要將照片、家庭角色參考原件、生成憑證或私人路徑提交公開 repo。
