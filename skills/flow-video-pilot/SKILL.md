---
name: flow-video-pilot
description: 「流之呼吸」——《不標準答案》動畫製作部的 Flow 特別企劃產線，需明確付費授權。用既有 Google Flow 訂閱點數製作實景照片與固定插畫角色的短動作試片，並回收、驗收及接入核准音檔。當老查要求 Flow 圖生影片、實景加動畫或延續已核准的角色影片試作時使用。
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

## 專屬封面（2026-10-15 起，每支影片必做）

依 `AGENTS.md`「影片封面硬規則」：本產線做出的每支要對外發布的影片，都由本產線另做一張專屬封面，跟成片一起交件、送鐵雄技術審與阿維品牌放行。直式（9:16）沿用句剪 SKILL.md「專屬封面」的規格與「封面鉤子手法」；橫式（16:9）做 1280 × 720 縮圖。不得抓影片其中一格或沿用單集封面圖冒充。只供內部看的試片不必做；試片一旦要發布，就先補封面再交星期天。

## 排程與本機檔案選擇器

Flow 網頁若需要 Chrome 原生檔案選擇器，排程執行時不得假設能操作本機視窗或沿用互動工作階段的 Computer Use 權限。工具回報無權限、選擇器未開啟或無法選取檔案時，停在上傳前，記錄待上傳檔案、Flow 專案、提示詞、模型／長度／點數設定與最後核對狀態，交由老查在互動工作階段附加素材後再續作。

不要把權限錯誤直接歸因於排程；只有排程環境與互動環境的實測才能確認原因。未確認 Flow 專案提交狀態及點數前，不重送生成，也不把畫面預覽當成已生成或已扣點的證據。

2026-09-27 的 S3EP8 試片實測：這個帳戶的 Veo 3.1 Lite 僅提供 8 秒；Omni 1.1 Flash 可做 4 秒，Flow 確認畫面顯示單支 7 點。當次 `gflow-cli` 因 agentic 編輯器 exit 25，確認沒有提交後才在 Flow 網頁完成。模型長度及點數之後仍需以當次確認畫面為準。

## Seedance 備援（經 Monica 網頁）

老查有 Monica 年訂閱，可用 Seedance 2.5 圖生影片，作為 Flow 以外的第二條產線。Monica API 另外收費，不使用；只由 Codex 操作已登入的 Monica 網頁。開工前先查 Monica 使用條款是否允許瀏覽器自動化；有疑慮就改半自動：Codex 填提示詞與上傳參考圖，生成鍵由老查按。

- 登入由老查在 Chrome 親自完成。不讀取、複製或上傳 Monica cookies 與 Chrome profile，不代輸入帳密。瀏覽器操作先在 Mac 實測；公司 Windows 能否讓 Codex 控制瀏覽器尚未驗證。
- 生成規則比照 Flow：開工前在 Monica 網頁讀當下剩餘額度與單支扣點，並確認額度是每月重置或整年一池；每次只生成 1 支；失敗不自動重送，先到 Monica 歷史紀錄確認有沒有提交。檔案選擇器無法操作時，停在上傳前，依上節記錄待上傳檔案、提示詞、模型與設定，交老查續作。
- 分工測試：前兩個鏡頭（大千水墨角色圖生影片、實景照片加角色各一），用同一張起始構圖與同一段提示詞，Flow 與 Seedance 各做 1 支，以 `verify` 接觸表比較角色走樣、筆觸、腳步接地與背景漂移。結果寫回本節，之後依鏡頭類型固定指派，不再每次兩邊比。
- 每支 Seedance 片段記下模型、提示詞、參考圖檔名、扣點與下載時間，供鐵雄追溯。下載後的 `verify`、`assemble`、專屬封面與發布閘門與 Flow 相同。
- 上傳前圖片一律轉成無 EXIF 的暫存 PNG。私人實景照片與家庭角色參考圖會經過 Monica 與 Seedance 兩家第三方，需老查當次同意；不把照片、帳號資訊或私人路徑提交公開 repo。

## S3EP8 專案界線

沿用 `video-projects/s3ep8-live-action-animation-pilot/` 的核准條件：山谷照片原色、四人核准比例與中段草皮、接觸影、核准精華 2 原音。當次起始構圖與角色參考圖保留在私有工作區；不要將照片、家庭角色參考原件、生成憑證或私人路徑提交公開 repo。
