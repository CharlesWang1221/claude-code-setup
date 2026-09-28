---
name: podcast-publish
description: 《不標準答案》單集上架統一入口（老查取名「星期天」）——接收音檔、逐字稿與圖片後，自動完成內容決策、平台文案、社群視覺、Podcast 音檔正片、一般預告、每週兩支實透實景角色精華與一支剪紙精華，以及 Firstory、IG、FB、YouTube Shorts 的審核與錯峰排程。自動判斷進度並接續到下一個真正需要老查決定的節點。觸發詞「上架」「新集數」「這集上架」「星期天」。
---

# 星期天 — Podcast 上架統一入口

老查一句「星期天」「上架 {slug}」或「新集數 {slug}」，這個 skill 判斷這一集目前做到哪一步、接下去該做什麼，依序執行到底，缺輸入就停下來問，不用老查自己依序喊四條 pipeline。

（內部技術識別名維持 `podcast-publish`——skill 系統規定 name 只能用小寫英文+數字+橫線，中文名只能放在暱稱/觸發詞，不影響喊「星期天」直接叫出這個流程。）

**這不是重寫底下四條 pipeline，是在它們上面加一層排序 + 狀態判斷 + 呼叫。** 每個步驟該用什麼工具、去哪個記憶檔找細節，都在下面列出。

2026-09-28 起 YouTube 長片獨立交由小查管理的 `you-guan`（油管）。星期天不自動啟動油管、不製作或等待長片、不執行長片上傳；既有長片旗標只保留歷史，不作完成或阻塞條件。精華到 YouTube Shorts 的發布仍由星期天管理。

---

## 狀態檔：`.publish-status.json`

每次執行第一步先讀 `output/ep-{slug}/.publish-status.json`；不存在就視為全部 false 並建立：

```json
{
  "transcript": false,
  "content_decision": {
    "approved": false,
    "core_claim": null,
    "brand_anchor": null,
    "audience": null,
    "listener_problem": null,
    "episode_promise": null,
    "title": null,
    "thumbnail_text": null
  },
  "brand_review": {
    "passed": false,
    "rejected_reasons": []
  },
  "content_files": false,
  "inputs": {
    "audio": null,
    "transcript": null,
    "images_dir": null,
    "assets_classified": false
  },
  "teaser_video": {
    "quote_selected": false,
    "rendered": false,
    "approved": false,
    "quote": null,
    "start": null,
    "end": null
  },
  "paper_highlights": [
    {
      "slot": 1,
      "quote_selected": false,
      "rendered": false,
      "approved": false,
      "quote": null,
      "start": null,
      "end": null,
      "render": null
    }
  ],
  "real_scene_highlights": [
    {
      "id": "shitou-1",
      "stage": "QUOTE_ANALYSIS",
      "quote": null,
      "start": null,
      "end": null,
      "script_approved": false,
      "keyframes_approved": false,
      "render": null,
      "qc_passed": false,
      "brand_review": null,
      "approved": false,
      "platforms": {}
    },
    {
      "id": "shitou-2",
      "stage": "QUOTE_ANALYSIS",
      "quote": null,
      "start": null,
      "end": null,
      "script_approved": false,
      "keyframes_approved": false,
      "render": null,
      "qc_passed": false,
      "brand_review": null,
      "approved": false,
      "platforms": {}
    }
  ],
  "highlight_plan": {
    "policy": "shitou-2-paper-1",
    "items": [
      {
        "id": "paper-1",
        "format": "paper",
        "slot": 1,
        "target_at": null
      },
      {
        "id": "shitou-1",
        "format": "shitou",
        "target_at": null
      },
      {
        "id": "shitou-2",
        "format": "shitou",
        "target_at": null
      }
    ]
  },
  "ig_images": false,
  "instagram": {
    "approved": false,
    "published": false,
    "postId": null,
    "url": null
  },
  "firstory": {
    "uploaded": false
  },
  "release_schedule": {
    "target_at": null,
    "timezone": "Asia/Taipei",
    "experiment_episode": null,
    "firstory_scheduled": false,
    "ig_topic_at": null,
    "fb_topic_at": null,
    "teaser_at": null,
    "paper_highlight_1_at": null,
    "real_scene_highlight_1_at": null,
    "real_scene_highlight_2_at": null
  },
  "shorts": {
    "applicable": false,
    "done": false
  },
  "fb_promo": {
    "applicable": false,
    "done": false,
    "scheduled": false,
    "postId": null,
    "url": null
  },
  "paper_highlight_publish": [
    {
      "slot": 1,
      "scheduled": false,
      "instagram": null,
      "facebook": null,
      "youtubeShorts": null
    }
  ]
}
```

既有狀態檔若沒有 `content_decision` 或 `brand_review`，只補上缺少欄位並視為未核准／未通過；不得重設其他已完成旗標。

2026-09-28 起新集數採每週 2 支實透＋1 支剪紙，`highlight_plan.items` 是當集必做／必排的唯一清單；不可因歷史 `paper_highlights` 中另有未完成項目就追加製作。舊檔保留所有成品、核准與平台證據，補上新清單並明確列出既有內容如何承接；已公開或已排程項目不得自動改動，需單集明確授權。缺 `real_scene_highlights` 時只補缺欄位，不重設既有核准。

每完成一步就更新寫回。**Firstory 是否上傳過，一律看這個檔案的旗標，不要用「影片檔存在」去猜測**——影片存在不代表已經上傳過。

---

## 執行步驟

### 0. 輸入與素材分類
需要 `{slug}`（必填）。接受本機音檔、Plaud 連結或本機逐字稿（`.txt`／`.md`／`.docx`），以及圖片檔或圖片資料夾。老查已一次提供的素材先全部登錄到 `inputs`，不要在後段重問同一路徑。

收到圖片資料夾後先建立素材清單，依實際比例與內容分成：IG 1:1、FB／Reels 9:16、YouTube 16:9、角色／場景來源圖。不能拿錯比例的圖片硬裁來補缺口；缺少必要比例時，在真正使用前回報。

### 0.5 品牌基準

任何內容生成前，完整讀取專案根目錄的 `AGENTS.md` 與 `BRAND_CONTEXT.md`。找不到任一檔案就停止內容生成並回報缺少品牌基準，不得憑印象補寫。

以心維空間為母品牌、《不標準答案》為旗下產品。所有單集標題、Show Notes、社群文案、預告字卡與 CTA 都必須服從 `BRAND_CONTEXT.md`；不可把兩者寫成並列品牌。

### 0.6 發布時段與 6 集實驗

- 2026-08-24 起，Podcast 音檔正片固定排程於每週一 07:00（Asia/Taipei, UTC+8）公開，連續執行 6 集；不得因單集波動自行改時段。
- 啟動單集流程時，先確認該集預定發布日期，將完整 ISO 8601 時間（含 `+08:00`）寫入 `release_schedule.target_at`，並標記這是實驗第幾集。若日期無法由現有資料判斷，只問老查「這集排哪個週一」，不可自行猜日期。
- 製作目標：前一週五 18:00 前完成內容決策與品牌審查；週日 18:00 前完成星期天範圍內的成品、平台文案與上傳；週一 07:00 正片公開。時間不足時要回報風險，不可默默改成即時發布。
- 社群錯峰：週一 12:15 發 FB／IG 主題文，週一 20:30 發一般預告，週二 20:30 發剪紙精華，週三 20:30 發實透 1，週五 12:00 發實透 2。三支精華各自使用自己的 9:16 成品，分別排到 IG Reels、FB Reels、YouTube Shorts；若任一平台不支援預約或當下無法完成，保留草稿並明確回報，不得假裝已排程。
- IG 發布隔離：IG 圖文與 IG Reels 只發布／排程至《不標準答案》Instagram 品牌帳號；禁止同步至 Si Ming Wang 個人 Facebook 頁面。建立 IG 貼文與提交前，星期天必須逐項核對「目前 IG 身分＝不標準答案」及「分享至 Facebook／交叉發布＝關閉」；任一項不符即停止並修正，不得發布。
- 從 `target_at` 自動計算同週的 `ig_topic_at`、`fb_topic_at`、`teaser_at`、`paper_highlight_1_at`、`real_scene_highlight_1_at`、`real_scene_highlight_2_at`，全部寫完整 ISO 8601 與 `+08:00`，並同步到 `highlight_plan.items[].target_at`。除非老查明確要求單次改為立即發布，否則沿用上述時段。
- 第 6 集發布滿 7 天後，回報應進行時段復盤；比較上線後 24 小時播放量、7 天完播率、首日播放占比、實際收聽尖峰與社群導流，再由老查決定是否調整。

實際製作與對外操作順序依總控章程：一般預告 → IG 圖文 → Firstory → 三支精華。前段內容決策可先完成三支選段與素材需求，但不插入 YouTube 長片工作。每一項對外動作仍在當次核准後提交。

### 1. 逐字稿 — `transcript: false` 時
老查有給 Plaud 連結（`https://web.plaud.ai/s/pub_xxxx...`）→ 用 `firecrawl_scrape`（`waitFor: 5000`）抓取；有給本機 `.txt`／`.md`／`.docx` → 直接讀取並複製到 `output/ep-{slug}/transcript/`。兩者都有時以本機修訂版為準，Plaud 只用來補時間碼。
完全沒有逐字稿來源才停在這一步，回報「需要 Plaud 逐字稿連結或逐字稿檔案才能繼續」。
完成後 `transcript: true`。

### 2. 內容決策關 — `content_decision.approved: false` 時

先讀完整逐字稿，只能使用逐字稿與老查明確提供的事實。產出 `content-decision.md`：

- 核心主張 1 句：聽完後應改變的看法或行動。
- 品牌錨點 1 個：指出這集如何連回 Beyond Answers、靈魂金繼、情感物理學或對抗爆買帝國；只選真正吻合者，不硬塞品牌術語。
- 主要受眾 1 種：不要同時討好多群人。
- 聽眾問題 1 個：用受眾會說的口語描述。
- 節目承諾 1 個：這集實際能交付什麼，不誇大。
- 標題 6 案：搜尋型 2 案、觀點型 2 案、衝突型 2 案。
- 每案標示主題清楚度、具體程度、好奇缺口、搜尋辨識度，各 1 至 5 分，並寫 1 句風險。
- 推薦標題 1 案與推薦理由。人名沒有自帶搜尋量時，不放標題最前面。
- 縮圖文字 3 案，每案 6 至 10 個中文字，不照抄標題。
- 品牌風險：逐案檢查是否藏有標準答案、販賣焦慮、強迫正向、鼓動比較，或把裂痕／修復當裝飾口號。

同時列出 10 句逐字稿原話金句，附講者與可靠時間碼。不可把改寫句冒充原話；找不到可靠時間碼就標示待確認。

停下來讓老查核准：最終標題、縮圖文字、5 句金句、其中 1 句一般預告主句，以及 2 段實透精華與 1 段剪紙精華。三支精華應各自表達一個完整觀點，優先使用不同段落，長度以 25 至 45 秒為目標，但不能為湊秒數切斷完整語意。未核准不得產生平台文案，也不得把 `content_decision.approved` 設為 `true`。

核准後把結果寫入 `.publish-status.json`，再進入下一步。三支必須使用不同原音段落、主要觀點或切角、動作情境；可共用角色與實景，但不能只換字幕、畫風或運鏡。選段時附三支差異對照，重複就先重選，不等製作後才改。三支選段可按「週二提出問題、週三情境轉折、週五另一個觀點或收束」分工，但依本集內容調整，不固定套模板；不可把同一段原音換三種畫面重播。

### 2.1 平台文案 — `content_decision.approved: true` 且 `content_files: false` 時
以核准的核心主張、品牌錨點、標題與金句為唯一母稿，產出 `fb-post.txt`（800 字 FB 長文）／`ig-caption.txt`（150 字＋hashtag）／`show-notes.md`（Firstory Show Notes）／`paper-highlight-1-caption.txt`／`shitou-highlight-1-caption.txt`／`shitou-highlight-2-caption.txt`。三支精華文案各自只服務該段觀點，不能貼同一篇通用摘要。細節格式見記憶 `project_podcast_production`。

寫作時套用記憶 `feedback_interaction_style` 的語氣禁用詞、排版規則，以及以下平台硬規則與發布前品牌關（取自 `social-media-assistant` 技能包，2026-08-06 併入）：

**FB 長文排版硬規則**
- 手機一行約 20-21 個全形字，抓 17-19 字最安全；話題轉換/重要觀點/情緒轉折處分段，同一論點延續不要硬拆
- 長短句交錯，全短句版面右側會空一片，全長句手機會亂斷
- 不用粗體、斜體、標題層級、編號清單——FB 不支援，寫下去只會變成一堆符號
- 開頭三段內要讓人知道在講什麼，不要自我介紹

**IG 短文規則**
- 挑素材裡最有張力、最有記憶點的切角，不是整集摘要
- 第一行就是全部，後面會被折起來

**發布前品牌閘門（四個文案檔與所有對外字卡都要檢查）**

逐項記錄 PASS／REJECTED 與具體問題句：

1. 架構關：心維空間是母品牌，《不標準答案》是旗下產品，沒有混用或錯置。
2. 北極星關：內容鼓勵受眾做自己的不標準選擇，不把單一做法包裝成唯一正解。
3. 焦慮關：不暗示受眾不夠好、不販賣恐懼、不鼓動比較競爭、不強迫正向。
4. 語氣關：有生活細節、明確立場與老查的煙火氣，不是「賦能」「全方位整合」等報告腔。
5. 事實關：沒在逐字稿或老查原話出現的數字、案例、經驗與成效，一個字不能補。
6. 隱私關：不過度揭露孩子、家庭、私密對話與未經同意的當事人資訊。
7. 商業關：不做農場標題、焦慮行銷、未揭露業配、絕對承諾或拉低品牌定位的廉售導向。

任一項命中即設為 `REJECTED`，把具體問題句與原因寫入 `brand-review.md`，完成改寫後重新檢查。全部通過才設定 `brand_review.passed: true` 與 `content_files: true`；不得為了接續上架硬放行。

**下游硬條件**：無論 `content_files`、`ig_images`  的既有旗標為何，只要 `brand_review.passed` 不是 `true`，就不得執行節目預告、IG 圖生成、Firstory 填寫、Shorts 或 FB 預告。先審查既有對外內容；通過後才能接續。

**目的衝突當場擋下**：如果這集文案同時要衝觸及、要導流訂閱、又要帶貨/招募，先問老查排順序，不要假裝一組文案能通吃三個目的。

**產 show-notes 前先自問一次**（不一定要外顯在文案裡，但要確認有想過）：這集體現記憶 `project_podcast_strategy` 三大哲學（金繼/物心分離/慢速野獸）的哪一個？確保底層哲學跟表面內容有連上。

**金句步驟鐵律（不可跳過、不可自動化）**：沿用內容決策關核准的 5 句原話金句，不得重新生成或自行替換。這條規則見記憶 `feedback_quote_selection`。

**節目預告選段**：選完 5 句後，將每句的原話、講者（若可知）與起訖時間碼列出，讓老查指定其中 1 句作為「節目預告主句」。沒有明確主句或可靠時間碼，就停在這裡，不自己猜要剪哪段。

完成後 `content_files: true`。

### 2.5 節目預告 — `teaser_video.rendered: false` 時

只有在老查從已選 5 句金句中指定 1 句主句後才執行。把主句與時間碼寫入 `teaser_video.quote`、`start`、`end`，再呼叫 `podcast-teaser-video` skill。

它以主句為剪輯錨點，從原始音檔取 12 至 18 秒，製作 9:16 一般預告。人物版依序使用老查、阿分、大寶、小寶特寫，每張必須有肉眼可辨的景別差異；場景之間用漫畫翻頁，最後翻到完整全圖與 9:16 片尾。片尾固定列 YouTube、Firstory、Spotify、Apple Podcast。

必須先讓老查確認四角色特寫、完整合照與片尾關鍵畫面才渲染，成品驗證後集中讓老查核准。只交一張完整圖的縮放 proof，不算關鍵畫面確認。核准後設定 `teaser_video.rendered: true`、`approved: true`，並立即銜接 FB Reel 草稿與排程，不再等老查另外提醒。

### 3. IG 圖 — `content_files: true` 且 `ig_images: false` 時
先讀專案根目錄 `DESIGN.md`，讓封面、輪播與金句圖服從品牌色、字體與視覺規則；找不到就停止視覺生成並回報。

自動執行：
```powershell
powershell -ExecutionPolicy Bypass -File tools\ig-images\run_ig.ps1 -EpSlug {slug}
```
自動偵測封面圖（規則見記憶 `project_ig_pipeline`）；偵測失敗才問老查要哪張封面，加 `-CoverImage` 參數重跑。

產完後，把整個 `output/ep-{slug}/ig/` 資料夾內容（carousel + quote 圖）連同 `ig-caption.txt` 一起複製到 Google Drive：`G:\我的雲端硬碟\不標準答案\2026\IG\{slug}\`（老查要求2026-07-26，方便他之後直接去這裡貼文，不用回頭找 repo 路徑）。

IG 輪播與片尾固定使用 1:1；一般預告、剪紙與實透精華固定使用 9:16；YouTube 長片封面、正片與片尾由油管另行製作。方形與直式片尾不得共用一張圖硬裁，分別輸出 `end-card-square.png`、`end-card-vertical.png`，並列出 YouTube、Firstory、Spotify、Apple Podcast。

完成後 `ig_images: true`。列出輪播順序與 `ig-caption.txt` 讓老查審核；核准後建立 IG 草稿，正式分享或排程前再確認一次。成功後才寫回 `instagram.approved`、`published`、`postId`、`url`。

### 4. Firstory 上傳 — 有音檔路徑且 `firstory.uploaded: false` 時
```
node tools/firstory-upload/upload.mjs --episode {slug} --audio "<音檔路徑>"
```
這是半自動：開瀏覽器、自動填標題+說明+上傳音檔，停在發布頁。依 `release_schedule.target_at` 設定預約發布；若 Firstory 當下介面或方案不支援預約，停止在確認頁並明確回報，不得改成提前公開。老查確認預約成功後，才把 `firstory.uploaded` 與 `release_schedule.firstory_scheduled` 設為 `true`（不要在腳本跑完就設定，因為它本來就不會自動按發布）。

### 5. 每週一支剪紙節目精華

只處理 `highlight_plan.items` 中 `format: paper` 的項目，呼叫 `paper-collage-video`。使用內容決策關核准的原話、講者、起訖時間碼與來源音檔，不另寫旁白。先鏡頭表與分層物件清單，再做代表鏡頭 proof，風格核准後完成 1080 × 1920、30 fps 成品。

交付預覽、原話、時間碼、長度與 caption，經核准才更新該項 `rendered`、`approved`。預設對應週二 20:30，交回第 6.2 節處理跨平台排程。歷史第二支剪紙未完成不再是新週節奏的必做項，也不刪除舊成品或證據。

### 5.1 每週兩支實透實景角色精華

呼叫 repo `skills/shi-tou/SKILL.md`，星期天管理每支進度。交接核准金句、上下文、講者、可靠時間碼與來源音檔；實透先擷取精華原音與拆解情境，等老查提供實景照片後完成動態腳本。腳本及關鍵畫面分別獲確認後，才串接角色插圖與 Flow。

兩支使用不同觀點或情緒轉折，動作由金句與當次場景決定，不固定入場或四人同台。先讓老查看兩支內容拆解與素材需求，可以同批提供照片；每支腳本、關鍵畫面與試片各自核准，不能用一支的放行套另一支。

依實透 `references/handoff-and-script.md` 更新 `real_scene_highlights`，並以 `highlight_plan.items` 對應星期三 20:30、星期五 12:00。缺照片、腳本待審或 QC 未過時回報缺口與時程風險，繼續其他可做工作；不為湊每週兩支降低驗收、不自動改成剪紙或增加扣點。

### 6. 對外草稿與排程

所有對外發布都先把成品、文案、身分、公開範圍與時間設定到最後一步，再向老查做動作確認。收到明確確認後才正式發布或建立平台排程；成功訊息、內容編號與網址讀回後，才可標成完成。

#### 6.1 一般預告

只要 `teaser_video.rendered: true` 且 `approved: true`，`fb_promo.applicable` 就是 `true`，與真人 Shorts 是否存在無關。使用 9:16 成品與核准文案建立 FB Reel，預設排程週一 20:30；單集若由老查指定立即發布，就只覆寫該集。

#### 6.2 每週三支精華跨平台排程

以 `highlight_plan.items` 為唯一排程清單，逐支核准即可準備該支草稿，不必等另一支照片。每支依自己的最終成片、caption、品牌 `ALLOW`、QC 與老查核准處理。

| 成品 | 發布時間（Asia/Taipei） | 平台 |
| --- | --- | --- |
| 剪紙精華 | 週二 20:30 | IG Reels、FB Reels、YouTube Shorts |
| 實透精華 1 | 週三 20:30 | IG Reels、FB Reels、YouTube Shorts |
| 實透精華 2 | 週五 12:00 | IG Reels、FB Reels、YouTube Shorts |

這是沿既有節奏安排的編輯方案，不是已驗證的最佳流量時間。週五預留實透 2，網誌不再擠入；老查單集明確覆寫時才改。已排程或公開的舊內容保留，重新安排需另有明確指示。

剪紙平台讀回寫入 `paper_highlight_publish`，實透平台讀回寫入該 `real_scene_highlights` 項目的 `platforms`，並更新發布證據庫。同一支在三個平台中有一個失敗，不能把整支標成完成；保留已成功結果，避免重複上傳。第 6 節的發布確認與 IG 身分／交叉發布隔離規則照常適用。

#### 6.3 額外真人 Shorts（條件式）

檢查 `video-projects/{slug}-short/01-raw/raw.mp4` 是否存在。不存在就把 `shorts.applicable: false`，這只代表沒有額外真人短片，不影響一般預告與三支精華。存在才依 `shorts-pipeline` skill 執行並安排額外發布槽位；不得擠掉週二剪紙、週三及週五實透的固定槽位。

### 7. 結尾報告
每次執行完，列出這集 16 個項目的狀態表：

| 項目 | 狀態 |
|------|------|
| 逐字稿 | ✅/❌/⏸️缺輸入 |
| 內容決策 | ✅/❌/⏸️待核准 |
| 品牌審查 | ✅/❌ REJECTED/⏸️待修正 |
| 平台文案 | ... |
| 節目預告 | ✅/❌/⏸️待選金句 |
| 剪紙精華 | ✅/❌/⏸️待選段或待審核 |
| 實透精華 1 | ✅/❌/⏸️待照片、腳本或成片核准 |
| 實透精華 2 | ✅/❌/⏸️待照片、腳本或成片核准 |
| IG圖 | ... |
| IG上架 | ... |
| Firstory | ... |
| Shorts | ✅/❌/➖不適用 |
| FB預告 | ... |
| 剪紙跨平台排程 | ✅/❌/⏸️待確認 |
| 實透 1 跨平台排程 | ✅/❌/⏸️待確認 |
| 實透 2 跨平台排程 | ✅/❌/⏸️待確認 |

清楚標示完成、缺什麼輸入、還是不適用，讓老查一眼看出下一步要給什麼。

### 8. SEO 文章（選配，不算在上面 16 項狀態表內）
若老查想把這集也轉成SEO文章補網站流量，可另外呼叫 `seo-article-writer` skill（老查取名「居易」，模式A，帶入同一個 `{slug}`）。這不是必經步驟，星期天流程本身不會主動觸發它。

---

## 涉及但不修改的既有工具
原樣呼叫，不動內部邏輯：
- `tools/ig-images/run_ig.ps1`
- `tools/firstory-upload/upload.mjs`
- `tools/fb-promo/run.bat` / `run.sh`
- `shorts-pipeline` skill（步驟 6 直接引用其步驟，不要複製貼上整份內容）
- `podcast-teaser-video` skill（步驟 2.5 只在老查選定預告主句後呼叫）
- `paper-collage-video` skill（步驟 5 每週一支剪紙精華，不與真人 Shorts 綁定）
- `shi-tou` skill（實透，步驟 5.1 每週兩支；星期天管理選段、製作交接與發布槽位）
- `seo-article-writer` skill（居易，選配步驟 8 引用，不要複製貼上整份內容）

## 相關記憶
`project_podcast_production`、`project_ig_pipeline`、`project_shorts_pipeline`、`project_fb_promo_pipeline`、`feedback_interaction_style`、`feedback_quote_selection`、`project_podcast_strategy`、`project_marketing_team_upgrade`
