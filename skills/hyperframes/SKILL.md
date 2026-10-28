---
name: hyperframes
description: 必須入口。任何使用 HyperFrames 製作、修改、檢查、預覽或渲染影片、動畫、動態圖卡、字幕疊圖與簡報式動態內容時先讀；也適用於接手既有 HyperFrames 專案、排查錯誤或批次製作。依專案狀態恢復工作、選擇 repo 內的專責流程、核對預算與品質閘門，再使用 HyperFrames CLI。
---

# HyperFrames｜影片製作入口

HyperFrames 將 HTML 組合渲染成影片。它是本 repo 的預設影片框架；老查明確指定其他框架，或任務只要求錄製瀏覽器畫面時，才改走指定路徑。先恢復專案狀態和核准範圍，再碰時間軸或 render。

## 啟動順序

1. 如果這是 Podcast 總控或會呼叫其他 Skill 的流程，先在 repo 根目錄執行 `tools/check-skill-authority.sh`，必須看到 `PASS`。失敗就停止，不用安裝副本替代 repo 母版。
2. 讀 repo 根目錄 `AGENTS.md` 和任務所屬 Skill。Podcast 短片先讀 `skills/podcast-teaser-video/SKILL.md`；YouTube 長片讀 `skills/you-guan/SKILL.md`；知識動畫讀 `skills/jieti/SKILL.md`；頻道形象動畫讀 `skills/zhaopai/SKILL.md`；老查點名剪紙時讀 `skills/paper-collage-video/SKILL.md`。
3. 先判斷既有工程或新工程。既有工程先讀 `BRIEF.md`、`HANDOFF.md`、`STATUS.md`（若存在）、`AGENTS.md` 及最近的 render／QA 證據；看工作樹與版本差異，不覆蓋未交接的改動。新工程先確認交付目的、素材、比例、時長、目標平台和核准額度；已能從本集文件取得答案時，不重複問老查。
4. 按「路由」選一條主要製作流程，再讀該流程列出的必要 Skill。這份入口 Skill 不取代內容、品牌、素材授權或平台發布審查。

## 路由

| 交付需求 | 主要流程 |
| --- | --- |
| Podcast 音檔金句短片、直式預告 | `podcast-teaser-video` |
| YouTube 長片及其製作交接 | `you-guan` |
| 知識概念、數據或因果解說動畫 | `jieti` |
| 頻道片頭、新季宣傳、活動或形象片 | `zhaopai` |
| 老查明確點名的剪紙精華／剪紙風影片 | `paper-collage-video` |
| 以上皆不符合的自訂影片或 HTML 動態作品 | 本 Skill 配合 `hyperframes` 專案流程；若 repo 沒有對應專責 Skill，先把工作範圍寫入 brief，不憑關鍵字硬派 |

## 專案與素材

- 新工程先讀 CLI 的實際版本和本機說明，再用 `hyperframes init` 建立專案。CLI 已安裝時使用該安裝版本；若只有 `npx` 會觸發下載，先停止並取得安裝／網路授權，不暗中下載依賴或瀏覽器。
- 工程放在 repo 已核准的影片目錄或使用者指定的私人工作區。家庭素材、未公開逐字稿、原音、封面及工程輸出不可加入公開 Git；先檢查 `.gitignore`，不要只因目錄名像 `video-projects` 就假設已忽略。
- 建立或補齊 `BRIEF.md`：目的、觀眾、原音／來源區段、平台、畫幅、時長、影像方向、素材來源與核准狀態。鏡頭表、字幕、首尾接點和輸出規格由所屬製作 Skill 定義。
- 預算卡決定可用工具、最多試片數、正式 render 數、並行數、重做停止線與對外範圍。工具額度、使用者核准、平台發布授權是三件不同的事；不得互相推定。

## 組合與動態

- 以時間可定位、可重複 seek 的時間軸組成場景。播放、動態與音訊位置必須能在任意時間點重現；不可依賴牆鐘計時、非同步載入完成順序或使用者點擊才能進入正確畫面。
- 先用簡單、可讀的 HTML 結構和正式素材建立場景，再依所屬 Skill 加入 GSAP、CSS 或其他 runtime。需要指定效果、轉場或元件時先查官方 registry，不憑名稱猜不存在的元件。
- 畫幅、fps、字幕安全框、音樂、旁白、片尾與循環規則以所屬 Skill 和核准 brief 為準。不要把一個專案的比例或版型套到另一個專案。
- 影片裡的逐字字幕、濃縮重點卡、封面文案要分清楚。沒有核准的逐字稿或字詞不得假裝是原話；畫面生成工具不得負責拼中文字。

## 檢查、預覽與 render

依目前安裝的 CLI `--help` 或 `npx hyperframes docs <topic>` 確認命令與旗標；CLI 會更新，不能複製舊專案裡過時的命令當現行規格。

1. 先跑 `hyperframes lint` 檢查組合結構，再跑 `hyperframes check --json` 檢查瀏覽器執行、版面、動態、對比及專案 assertions。將錯誤修到可解釋、可複查；不要為了讓檢查變綠而刪除必要敘事或放寬已核准條件。
2. 依故事節點執行 `hyperframes snapshot --at <seconds>`，查看開頭、各段中間、轉場與結尾。確認畫面沒有溢出、遮擋、凍結、字卡碰撞或首尾斷裂。截圖只證明取樣時刻，不代表整支影片已驗收。
3. 依所屬 Skill 開啟 preview；讓老查看到可播放的 sample，並記錄版本、檔案路徑和審查狀態。老查核准 sample 後才可正式 render。
4. Render 只使用核准額度內的本機方式。Cloud render、付費服務、升級 CLI、下載瀏覽器／套件、重做、上傳、發布或排程都要各自有明確授權。核准一個 sample 不等於核准正式版或平台發布。
5. 正式輸出後用 `ffprobe` 讀回檔案、時長、畫幅、fps、影像／音訊 codec；再抽樣檢查畫面、音訊同步、片尾和循環。將檢查證據存於私人專案，獨立 QA 與品牌審查未完成前，不標成 READY 或 ALLOW。

## 交付紀錄

回報工程與輸出路徑、版本、已執行的檢查、樣片／成片狀態、剩餘阻塞和發布狀態。清楚區分「工程建立」「影片 render 完成」「審查通過」「平台發布成功」；沒有平台讀回證據時不得稱為已上架。

## 官方技術參考

- [HyperFrames 官方 CLI 文件](https://hyperframes.app/docs/5-packages/cli)：命令、`lint`、`check`、`snapshot`、`preview` 和 `render`。實際旗標以本機已安裝版本為準。
- [HyperFrames 官方渲染指南](https://hyperframes.app/docs/3-guides/4-rendering)：環境檢查、預覽及本機 render 流程。
- [HyperFrames 官方入口 Skill](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/SKILL.md)：能力路由、專案狀態恢復與官方工作流程。此 repo 的本檔是 Codex 母版；外部安裝版不可回寫或裁決本 repo 規則。

以上官方參考於 2026-10-27 核對。CLI 或官方文件更新時，先比較目前版本和本檔涉及的流程，再由 repo 維護者修訂本母版。
