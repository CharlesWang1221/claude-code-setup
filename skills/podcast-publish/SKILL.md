---
name: podcast-publish
description: 《不標準答案》單集上架統一入口（老查取名「星期天」）——接收音檔、逐字稿與圖片後，自動完成內容決策、平台文案、社群視覺、Podcast 音檔正片、每週 6 支短影片（含一般預告），以及 Firstory、IG、FB、YouTube Shorts 的審核與錯峰排程。自動判斷進度並接續到下一個真正需要老查決定的節點。觸發詞「上架」「新集數」「這集上架」「星期天」。
---

# 星期天 — Podcast 上架統一入口

老查一句「星期天」「上架 {slug}」或「新集數 {slug}」，這個 skill 判斷這一集目前做到哪一步、接下去該做什麼，依序執行到底，缺輸入就停下來問，不用老查自己依序喊四條 pipeline。

（內部技術識別名維持 `podcast-publish`——skill 系統規定 name 只能用小寫英文+數字+橫線，中文名只能放在暱稱/觸發詞，不影響喊「星期天」直接叫出這個流程。）

**這不是重寫底下四條 pipeline，是在它們上面加一層排序 + 狀態判斷 + 呼叫。** 每個步驟該用什麼工具、去哪個記憶檔找細節，都在下面列出。

2026-09-28 起 YouTube 長片獨立交由小查管理的 `you-guan`（油管）。星期天不自動啟動油管、不製作或等待長片、不執行長片上傳；既有長片旗標只保留歷史，不作完成或阻塞條件。精華到 YouTube Shorts 的發布仍由星期天管理。

### 社群營運前置閘門

星期天開始製作任何一般預告、實透、剪紙精華或其他短影音前，必須先呼叫 `community-operations`。若有留言或討論資料，先交 `voc-jtbd-demand-map` 做 VOC 採證；沒有原始觀眾資料時，標示為內容推論。

依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md) 建立跨集週計畫。小渡先配置六支任務與來源，再由老查核准原音，逐支交付 READY brief。每份 brief 需有 item ID、主要平台、單一任務、觀眾入口、核心摩擦、完整原話與時間碼、畫面／字幕方向及結尾導向。

任一項未 READY，或原話／時間碼／版本不一致，不得開始該支的鏡頭表、素材生成或動畫；只阻塞該支。歷史 paper-1、shitou-1、shitou-2 為舊識別，不固定限制新週數量。

社群 brief 是製作方向，不是品牌放行。星期天依 brief 製作後，仍須送 `brand-guardian` 取得 `ALLOW`，由小查驗收版本與證據，最後依授權矩陣等待老查發布授權。畫面與內容走向衝突時，退回小渡與小查裁決，不得自行改成另一個觀點。

### 直式短影片安全框（所有 9:16 成品）

每週六支短片交付 IG Reels、FB Reels、YouTube Shorts 前，一律以 1080 × 1920 畫布套用同一保守安全框：`x = 76 至 1004 px`（左右各 7%），`y = 250 至 1520 px`（上方 250 px、下方 400 px）。所有字幕、CTA、平台資訊、人物名稱、數字與不可被遮住的關鍵畫面元素都必須完整落在框內；不要只把文字基線塞進框內。

平台介面、瀏海／前鏡頭區、底部互動列與不同 App 的裁切都會吃掉邊緣。字幕若跨多行，整個字幕底板與陰影範圍也要在框內；沒有必要時不在安全框外放任何關鍵內容。視覺 proof 與最終 QC 都要抽檢至少 1 張中段字幕畫面，逐項確認沒有越界，未通過不得標示為 QC 完成或排程。

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
  "community_allocation": {
    "status": "PENDING",
    "path": null,
    "version": null,
    "reviewed_by_ceo": false
  },
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
  "paper_highlights": [],
  "real_scene_highlights": [],
  "highlight_plan": {
    "policy": "weekly-six-v1",
    "items": [],
    "legacy_only": true
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
    "short_video_policy": "weekly-six-v1"
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
  "paper_highlight_publish": [],
  "weekly_plan_refs": []
}
```

既有狀態檔若沒有 `content_decision`、`brand_review`、`community_allocation` 或逐支 `community_brief`，只補上缺少欄位並視為未核准／未就緒；不得重設其他已完成旗標。

2026-10-10 起依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md)，每週一至六共 6 支，含一般預告。以跨集 weekly-plan.json 為短片必做／必排清單，單集只保留來源及週計畫引用，不預設一集切六段。既有成品、核准、平台證據與歷史狀態保留；舊 false 項不得觸發追加製作。

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
- 社群主題文維持週一 12:15；週一至週六各 1 支短片，共 6 支（含一般預告），形式、時間與網誌碰撞處理依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md)。每支分別排 IG Reels、FB Reels、YouTube Shorts，無平台成功讀回不得標為已排程。
- IG 發布隔離：IG 圖文與 IG Reels 只發布／排程至《不標準答案》Instagram 品牌帳號；禁止同步至 Si Ming Wang 個人 Facebook 頁面。建立 IG 貼文與提交前，星期天必須逐項核對「目前 IG 身分＝不標準答案」及「分享至 Facebook／交叉發布＝關閉」；任一項不符即停止並修正，不得發布。
- Podcast target_at 與短片週計畫分開。每項短片寫完整 +08:00 target_at，週計畫引用來源集數；不從正片日期自動追加舊三支精華。
- 第 6 集發布滿 7 天後，回報應進行時段復盤；比較上線後 24 小時播放量、7 天完播率、首日播放占比、實際收聽尖峰與社群導流，再由老查決定是否調整。

實際製作與對外操作順序依總控章程：一般預告 → IG 圖文 → Firstory → 週計畫其他短片。前段可先配置週計畫原音與素材需求，但不插入 YouTube 長片工作。每一項對外動作仍在當次核准後提交。

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

同時列出 10 句逐字稿原話金句，附講者與可靠時間碼。不可把改寫句冒充原話；找不到可靠時間碼就標示待確認。將這 10 句及可用素材交給小渡，產出 `community-briefs/highlight-allocation.md`，再由小查核對其沒有改寫原話或越過品牌放行。

讓老查核准最終標題、縮圖文字、原話金句與週計畫中本集承接的選段。一般預告含在六支內，可由核准歷史素材補足其他槽位，不強迫本集切六段。完整語意優先，不為秒數截斷句子。

小渡依週計畫提供各支差異與逐支 brief，小查核對 item ID、原話、時間碼及版本後才設 READY。核准寫回單集與週計畫；同段原音換畫風不能算兩支不同發布內容。

### 2.1 平台文案 — `content_decision.approved: true` 且 `content_files: false` 時
以核准母稿產出 fb-post.txt、ig-caption.txt、show-notes.md，並依週計畫逐 item ID 產出 caption。每支只服務該段觀點，不共用泛用摘要；用 AGENTS.md 與 BRAND_CONTEXT.md 的寫作規則，不依賴不可讀的舊記憶。

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

只有在老查指定核准主句、可靠切點及週一預告 item 後才製作。一般預告是六支中的動態字卡／物件 1，呼叫 podcast-teaser-video 的預設字卡版，使用核准原音與字幕；依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md) 的輕量路線及逐支 brief 製作。

老查明確選擇「人物版」時才呼叫 podcast-teaser-video 的四張獨立特寫／合照流程。不要將四角色生成當作每週字卡預告的前置條件。小樣與最終成片分開核准，QC、品牌 ALLOW 與發布證據照常適用。

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

### 5. 依週計畫製作短片

逐項讀 weekly-plan.json 的 format、role、核准來源、READY brief 與 target_at；不硬派舊 paper-1／shitou-1／shitou-2。

- paper：呼叫 paper-collage-video，完整鏡頭表、分層物件、小樣與 QC。
- scene：呼叫 shi-tou 的實景紙片模式，先重用透明角色與實景，再做可控圖層動作；不預設 Flow。
- type：依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md) 做原音動態字卡／物件，原話分句、字幕對齊與物件動作均有聲音依據。

各支腳本、關鍵畫面、小樣與最終版按適用流程核准；缺照片、原音或 QC 只阻塞該支。Flow 只在明確特別企劃及點數授權後使用，不替六支日常扣點。

### 6. 對外草稿與排程

所有對外發布都先把成品、文案、身分、公開範圍與時間設定到最後一步，再向老查做動作確認。收到明確確認後才正式發布或建立平台排程；成功訊息、內容編號與網址讀回後，才可標成完成。

#### 6.1 一般預告

只要 `teaser_video.rendered: true` 且 `approved: true`，`fb_promo.applicable` 就是 `true`，與真人 Shorts 是否存在無關。使用 9:16 成品與核准文案建立 FB Reel，預設排程週一 20:30；單集若由老查指定立即發布，就只覆寫該集。

#### 6.2 六支週計畫跨平台排程

以 weekly-plan.json 為唯一短片發布清單（包含第 6.1 節的一般預告，不能重算）。逐支核對最終檔、caption、品牌 ALLOW、QC、人工核准、帳號及 target_at；時段依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md)。

各平台讀回寫入該 item.platforms 與發布證據庫，單集保留引用。三平台任一失敗保留其他成功結果，不重複上傳，也不把整支標為跨平台完成。

#### 6.3 真人或 Flow 特別短片

存在真人 raw.mp4 不自動追加影片。收到明確製作指示時，依對應 Skill 先判素材，再替換核准週計畫槽位；維持總數六支。額外第七支需另行指示。

### 7. 結尾報告
回報單集文字／音檔／IG 狀態，以及當週六個 item 的來源、形式、素材、原音、brief、render、QC、品牌、核准與各平台狀態。清楚區分樣片、成片、草稿、排程與公開；標示下一棒及缺件，不再硬列舊三支精華為必做。

### 8. SEO 文章（選配，獨立追蹤）
若老查想把這集也轉成SEO文章補網站流量，可另外呼叫 `seo-article-writer` skill（老查取名「居易」，模式A，帶入同一個 `{slug}`）。這不是必經步驟，星期天流程本身不會主動觸發它。

---

## 涉及但不修改的既有工具
原樣呼叫，不動內部邏輯：
- `tools/ig-images/run_ig.ps1`
- `tools/firstory-upload/upload.mjs`
- `tools/fb-promo/run.bat` / `run.sh`
- `shorts-pipeline` skill（步驟 6 直接引用其步驟，不要複製貼上整份內容）
- `podcast-teaser-video` skill（步驟 2.5 預設字卡版，人物版僅明確指定時使用）
- `paper-collage-video` skill（步驟 5 每週一支剪紙精華，不與真人 Shorts 綁定）
- `shi-tou` skill（實透，步驟 5 實景紙片預設、Flow 特別企劃；星期天管理選段、製作交接與發布槽位）
- `seo-article-writer` skill（居易，選配步驟 8 引用，不要複製貼上整份內容）

## 相關記憶
`project_podcast_production`、`project_ig_pipeline`、`project_shorts_pipeline`、`project_fb_promo_pipeline`、`feedback_interaction_style`、`feedback_quote_selection`、`project_podcast_strategy`、`project_marketing_team_upgrade`
