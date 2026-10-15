---
name: podcast-publish
description: 《不標準答案》單集上架統一入口（老查取名「星期天」）——接收音檔、逐字稿與圖片後，自動完成內容決策、平台文案、社群視覺、Podcast 音檔正片、每週 6 支金句短片（句剪製作，週一為本集預告，每支另做專屬封面），以及 Firstory、IG、FB、Threads、YouTube Shorts 的審核與錯峰排程。自動判斷進度並接續到下一個真正需要老查決定的節點。觸發詞「上架」「新集數」「這集上架」「星期天」。
---

# 星期天 — Podcast 上架統一入口

老查一句「星期天」「上架 {slug}」或「新集數 {slug}」，這個 skill 判斷這一集目前做到哪一步、接下去該做什麼。共用決策關完成後，獨立產線並行推進；只在真正需要老查決定的節點停下來，不用老查自己依序喊四條 pipeline。

（內部技術識別名維持 `podcast-publish`——skill 系統規定 name 只能用小寫英文+數字+橫線，中文名只能放在暱稱/觸發詞，不影響喊「星期天」直接叫出這個流程。）

**這不是重寫底下四條 pipeline，是在它們上面加一層排序 + 狀態判斷 + 呼叫。** 每個步驟該用什麼工具、去哪個記憶檔找細節，都在下面列出。

### 並行調度與接續

- 啟動時先通過 `tools/check-skill-authority.sh`，讀既有 `.publish-status.json`、週計畫、任務交接及平台證據；一次登錄當次素材。已完成、已核准及已排程項目不得因新一輪調度重做或重傳。
- 逐字稿、品牌基準、內容決策及週計畫來源配置是共用前置。前置未核准時，可並行做唯讀盤點、素材分類、音訊技術檢查與選段候選；不能把候選直接送入對外稿或短片製作。
- 前置完成後，依可用代理席位同時推進互不依賴的工作：音檔與 Firstory 準備、IG 輪播與文案、各個已 READY 的短片 item。缺圖、缺原音或一支 QC 失敗，只阻塞該項；其他就緒項目繼續。
- 每個代理只擁有明確檔案或 item ID，禁止兩個可寫入代理改同一狀態檔、週計畫或平台草稿。總控統一合併結果、執行品牌與版本檢查、序列化寫回狀態；並行任務完成不等於獲得發布授權。
- 對外提交依第 6 節：預檢帳號、交叉發布、時間與成品版本，整理成一份上架授權包；老查回「可以上架」後一次跑完並讀回平台證據，中途不再逐項詢問。若平台不支援替換舊排程，須避免新舊兩份同時上線。跨工作階段依狀態檔與證據接續；單次對話不宣稱背景任務會持續運轉。

2026-09-28 起 YouTube 長片獨立交由教父管理的 `you-guan`（油管）。星期天不自動啟動油管、不製作或等待長片、不執行長片上傳；既有長片旗標只保留歷史，不作完成或阻塞條件。精華到 YouTube Shorts 的發布仍由星期天管理。

### 社群營運前置閘門

星期天開始製作任何金句短片（含週一預告），或老查另外點名的剪紙、實透特別企劃前，必須先呼叫 `community-operations`。若有留言或討論資料，先交 `voc-jtbd-demand-map` 做 VOC 採證；沒有原始觀眾資料時，標示為內容推論。

依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md) 建立跨集週計畫。小渡先配置六支任務與來源，再由老查以原音包一次核准原音，各支 READY brief 同時產出；六支並行製作，老查每週只審原音包、鏡頭表包、小樣包三次，細節依短片母版「六支並行與整批審」。每份 brief 需有 item ID、主要平台、單一任務、觀眾入口、核心摩擦、完整原話與時間碼、畫面／字幕方向及結尾導向。

任一項未 READY，或原話／時間碼／版本不一致，不得開始該支的鏡頭表、素材生成或動畫；只阻塞該支。歷史 paper-1、shitou-1、shitou-2 為舊識別，不固定限制新週數量。

原音候選以原音包一次交齊六段（缺段標明原因先交其他段），每段各一個可直接播放的私人連結，並標明週槽、時長和待確認的句首／句尾；不要用本機 `file://` 試聽頁代替。交付前先對照逐字稿和原音，確保指定說話者把完整句子講完、不殘留下一位的半句。若切點仍帶入下一位的接話，可在指定說話者完成後做短淡出；淡出不能吃掉最後一個字。每週各槽必須使用不同的原音時間段和不同內容角度；核對週配置、候選清單與已核准片，發現重複就保留一槽並另找新段補缺，不能把同段改畫風算新內容。老查逐段回覆後，記下核准段的版本、時間碼和原話並立即開工；退件段單獨重找補交，不擋已核准段。核准原音不等於 brief READY、畫面核准或發布授權。

社群 brief 是製作方向，不是品牌放行。星期天依 brief 製作後，仍須送 `brand-guardian` 取得 `ALLOW`，由教父驗收版本與證據，最後依授權矩陣等待老查發布授權。畫面與內容走向衝突時，退回小渡與小查裁決，不得自行改成另一個觀點。

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
- 社群主題文維持週一 12:15，FB、IG、Threads 同時段；週一至週六各 1 支短片，共 6 支（含一般預告），形式、時間與網誌碰撞處理依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md)。每支的 IG Reels 與 FB Reels 在 Meta Business Suite 以同一則 Reel 一次排程（2026-10-15），YouTube Shorts、Threads 另排；無平台成功讀回不得標為已排程。
- IG 金句圖與 IG 輪播（靜態圖）只發 IG，「分享至 Facebook」一律關閉，FB 不另發同一組圖（2026-10-15）。網站的 FB→IG 同步只轉居易網誌長文，不會替 Reels 或主題文發 IG，這兩類仍由本流程各平台原生發布。
- Threads 只發布／排程在《不標準答案》的 Threads 帳號。IG 發文時「分享到 Threads」一律關閉，Threads 版另以專屬文案排程，避免同一內容出現兩次。
- IG 發布隔離：IG 圖文與 IG Reels 只發布／排程至《不標準答案》Instagram 品牌帳號；禁止同步至 Si Ming Wang 個人 Facebook 頁面。建立 IG 貼文與提交前，星期天必須逐項核對「目前 IG 身分＝不標準答案」及「分享至 Facebook／交叉發布＝關閉」；任一項不符即停止並修正，不得發布。
- Podcast target_at 與短片週計畫分開。每項短片寫完整 +08:00 target_at，週計畫引用來源集數；不從正片日期自動追加舊三支精華。
- 第 6 集發布滿 7 天後，回報應進行時段復盤；比較上線後 24 小時播放量、7 天完播率、首日播放占比、實際收聽尖峰與社群導流，再由老查決定是否調整。

總控優先追蹤一般預告、IG 圖文、Firstory 與週計畫其他短片；符合前置條件的內部製作可並行，對外動作仍在當次核准後逐項提交。前段可先配置週計畫原音與素材需求，但不插入 YouTube 長片工作。

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

小渡依週計畫提供各支差異與逐支 brief，教父核對 item ID、原話、時間碼及版本後才設 READY。核准寫回單集與週計畫；同段原音換畫風不能算兩支不同發布內容。

### 2.1 平台文案 — `content_decision.approved: true` 且 `content_files: false` 時
以核准母稿產出 fb-post.txt、ig-caption.txt、threads-post.txt、show-notes.md，並依週計畫逐 item ID 產出 caption 與 Threads 版文案。每支只服務該段觀點，不共用泛用摘要；用 AGENTS.md 與 BRAND_CONTEXT.md 的寫作規則，不依賴不可讀的舊記憶。

寫作時套用記憶 `feedback_interaction_style` 的語氣禁用詞、排版規則，以及以下平台硬規則與發布前品牌關（取自 `social-media-assistant` 技能包，2026-08-06 併入）：

**FB 長文排版硬規則**
- 手機一行約 20-21 個全形字，抓 17-19 字最安全；話題轉換/重要觀點/情緒轉折處分段，同一論點延續不要硬拆
- 長短句交錯，全短句版面右側會空一片，全長句手機會亂斷
- 不用粗體、斜體、標題層級、編號清單——FB 不支援，寫下去只會變成一堆符號
- 開頭三段內要讓人知道在講什麼，不要自我介紹

**IG 短文規則**
- 挑素材裡最有張力、最有記憶點的切角，不是整集摘要
- 第一行就是全部，後面會被折起來

**Threads 文案規則**
- 另寫，不照貼 FB 長文或 IG caption；單篇 500 字元以內，像老查當下想到的一句話，不像公告
- 拋一個觀點或問題讓人想回，結尾不用「點連結收聽」式 CTA；hashtag 最多 1 個
- 短片的 Threads 文案只服務該支觀點，跟同支 IG caption 不得是同一段文字

**發布前品牌閘門（五個文案檔、Threads 版文案與所有對外字卡都要檢查）**

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

IG 輪播視覺固定使用 1:1；金句短片（含週一預告）與剪紙、實透特別企劃短影片固定使用 9:16。所有短影片不製作片尾卡，最後畫面需回接開場形成循環；細則見 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md)。YouTube 長影片封面、正片與片尾由油管另行製作，不套用短影片版型。

完成後 `ig_images: true`。列出輪播順序與 `ig-caption.txt` 讓老查審核；核准後列入第 6 節上架授權包，授權後直接建立草稿並排程，不另做二次確認。成功讀回後才寫回 `instagram.approved`、`published`、`postId`、`url`。

### 4. Firstory 上傳 — 有音檔路徑且 `firstory.uploaded: false` 時
```
node tools/firstory-upload/upload.mjs --episode {slug} --audio "<音檔路徑>"
```
腳本開瀏覽器、自動填標題+說明+上傳音檔，停在發布頁，本身不會按發布。音檔與標題列入第 6 節上架授權包；授權後由星期天用瀏覽器工具在同一頁設定 `release_schedule.target_at` 的預約時間並按預約，不再請老查到電腦前操作。若 Firstory 當下介面或方案不支援預約，該列標 `FAILED` 並停在確認頁，不得改成提前公開。在 Firstory 單集列表讀回「已預約＋正確時間」後，才把 `firstory.uploaded` 與 `release_schedule.firstory_scheduled` 設為 `true`（不要在腳本跑完就設定）。

### 5. 依週計畫製作短片

逐項讀 weekly-plan.json 的 format、role、核准來源、READY brief 與 target_at；不硬派舊 paper-1／shitou-1／shitou-2。

- quote（2026-10-14 起六支預設）：呼叫 podcast-teaser-video（句剪），原話分句、字幕對齊與畫面動作均有聲音依據；每支同時交專屬封面，重點卡字級依句剪 SKILL.md。開工前先有真短驗析的產前假設卡。
- paper／scene：只在老查另外點名剪紙或實透、省長開出 L 級預算卡時才出現，替換一個 quote 槽位；分別呼叫 paper-collage-video 與 shi-tou。星期天不得自行把槽位改成 paper 或 scene。

各支腳本、關鍵畫面、小樣與最終版按適用流程核准；缺原音或 QC 只阻塞該支。Flow 只在明確特別企劃及點數授權後使用，不替六支日常扣點。

### 6. 上架授權包與自動排程

老查只在內容階段核准；發布階段只問一次。把要上架的全部內容整理成一份「上架授權包」，老查回「可以上架」後，星期天自行跑完所有平台的草稿、排程與讀回，中途不再逐項詢問。

**建包前的預檢（可逆，不對外寫入）**

- 只收齊件的列：最終檔、專屬封面、caption、鐵雄 PASS、阿維 `ALLOW`、人工核准、完整 +08:00 時間都具備。缺件的列標 `BLOCKED` 留在包外，不擋其他列。
- 逐平台確認登入有效、帳號身分正確（IG＝不標準答案、分享至 Facebook＝關閉、分享到 Threads＝關閉；Threads＝不標準答案）、時間未過、平台支援預約。登入失效在預檢一次列給老查補登，不得等授權後才中途叫人。

**授權包**：寫入 `output/ep-{slug}/release-package.json`（週計畫短片寫 `output/weekly-shorts/{week-start}/release-package.json`），每列記 item ID、平台、帳號、成品路徑與 SHA-256、封面、caption 檔與 SHA-256、公開範圍、target_at、`ai_label`。給老查的摘要一次列完全部列，不分批問。

**授權**：老查回「可以上架」「照包上架」或同義明確回覆，即授權包內全部列。寫入 `release_authorization`：包路徑、包的 SHA-256、授權時間與老查原話。只回部分列（例如「IG 先不要」）就把其餘列移出包後再執行。

**AI 標示**：所有影片在 YouTube（「變造或合成內容」）、IG／FB Reels 與 Threads（「AI 標籤／AI 資訊」）上架時，AI 選項一律選「否」，授權包每列記 `ai_label: false`。水墨、剪紙、字卡動畫與節目真實原音不屬平台要求揭露的擬真合成內容。例外只有兩種，該列必須選「是」並在授權包標明：用 AI 複製的聲音（例如 Voicebox）讓真人說出沒說過的話；或 AI 生成／改造、看起來像真實拍攝的人物或場景（例如 Flow 擬真動態）。不得為了選「否」去除檔案的 AI 中繼資料；平台若自動加上 AI 標籤，保留並在結束回報註明。

**授權後執行**：依 Firstory → IG／FB／Threads 主題文 → 週一預告 → 其他短片的順序，逐列建立草稿、設定、排程並讀回平台證據。不做 IG 草稿二次確認，也不在每列之間回頭問。

**只停該列、不中途詢問**：成品或 caption 雜湊與包不符、帳號身分不符或交叉發布關不掉、登入失效、時間已過或平台不支援預約、平台報錯或讀回不符、需要付費或新增權限。遇到就把該列標 `FAILED` 並寫原因，不重試上傳、不改時間、不換檔、不換平台、不改成立即公開，繼續下一列。

**授權邊界**：只涵蓋包內的列與當時的雜湊。包外新增、換版、改時間、修改或刪除既有排程，都要另開新包或老查另行明確授權；授權不延續到下一包。

**結束回報**：全部列跑完才回報一次：每列是「排程成功（平台 ID／網址／讀回時間）」「FAILED（原因）」或「未執行」，同步寫入 `docs/RELEASE_EVIDENCE_REGISTER.md`。失敗列另開只含失敗列的補件包。成功訊息、內容編號與網址讀回後，才可標成完成。

#### 6.1 週一預告（mon-quote）

只要 `teaser_video.rendered: true` 且 `approved: true`，`fb_promo.applicable` 就是 `true`，與真人 Shorts 是否存在無關。使用 9:16 成品與核准文案建立 FB Reel，預設排程週一 20:30；單集若由老查指定立即發布，就只覆寫該集。

#### 6.2 六支週計畫跨平台排程

以 weekly-plan.json 為唯一短片發布清單（包含第 6.1 節的一般預告，不能重算）。逐支核對最終檔、專屬封面、caption、品牌 ALLOW、QC、人工核准、帳號及 target_at；三平台都要套用專屬封面並讀回封面已生效；時段依 [每週 6 支短片母版](../../docs/SHORT_VIDEO_WEEKLY_POLICY.md)。

IG／FB Reels 列在授權後到 Meta Business Suite 建立一則 Reel，發布位置同時勾選《不標準答案》Facebook 粉專與《不標準答案》Instagram（不得出現 Si Ming Wang 個人頁），上傳該支成品與專屬封面、貼上同一段 caption、AI 標示選「否」、以原生排程設定 target_at。兩個平台共用一段 caption；排程後分別在 Business Suite 排程清單讀回 FB 與 IG 兩列的時間、帳號與封面，任一邊未出現或封面未生效，就只把該平台記 `FAILED`，不重建另一邊。授權包仍分 IG、FB 兩列記錄證據。

YouTube Shorts 列在授權後用 `node tools/youtube-upload.js --video <item.render> --meta <該支 youtube.txt> --thumbnail <專屬封面> --qa-report <鐵雄報告> --publish-at <item.target_at>` 一次完成上傳、封面與預約公開；工具核對平台回傳的預約時間，不符就停下且不重傳。上傳前先讀 `item.platforms.youtube`，已有 id 就跳過。封面另到 Studio 讀回；若 Shorts 封面沒生效，該列記「封面未生效」，不為此重傳影片。

Threads 列（主題文與每支短片）在授權後用瀏覽器工具到 threads.com，以《不標準答案》帳號建立貼文、附上該支成品（主題文附 IG 輪播第一張或純文字）、貼上 Threads 版文案，用原生「排程」設定 target_at；到排程清單讀回時間與內容後才算成功。介面找不到排程功能就標 `FAILED`，不得改成立即發布。

各平台讀回寫入該 item.platforms 與發布證據庫，單集保留引用。三平台任一失敗保留其他成功結果，不重複上傳，也不把整支標為跨平台完成。

##### 已排程短片換版

收到換版指示時，先從 `.publish-status.json`、發布證據庫與平台清單逐一讀回舊版 ID、帳號、排程時間及版本，不能只靠標題判斷。先以核准的新檔、封面與文案建立新版；確認三平台各自讀回新版檔案／內容、封面、帳號與 Asia/Taipei 排程時間後，才清除舊版，避免新版失敗時沒有可用排程。

永久刪除舊版須有老查明確授權。YouTube 舊片在 Studio「永久刪除」並確認；Meta 舊 Reel 先讀回內容 ID，再從貼文詳情「操作」刪除並確認。不能以設私人或移到草稿冒充刪除。若平台新版還在「處理中」，保留該狀態，等待處理完成再核對一次排程清單；不可因舊版刪掉就宣稱新片完成。

替換完成後更新 `.publish-status.json`、單集 `production-status.md`、QC／交接紀錄與 `docs/RELEASE_EVIDENCE_REGISTER.md`：記錄新版檔名、平台 ID／網址、帳號、封面狀態、排程時間與讀回證據；另列舊版 ID 及刪除結果。平台成功讀回前不得把本機成片狀態改成已排程。

#### 6.3 真人或 Flow 特別短片

存在真人 raw.mp4 不自動追加影片。收到明確製作指示時，依對應 Skill 先判素材，再替換核准週計畫槽位；維持總數六支。額外第七支需另行指示。

#### 6.4 網站單集重點（每集必做，2026-10-15 起）

讓讀者與 AI 搜尋讀懂這集講了什麼。不放完整逐字稿，只放約 800 至 1,200 字的重點，寫成 `site/src/content/highlights/s{季}ep{集}.md`（例 `s3ep11.md`），網站單集頁依季／集自動顯示「本集重點」並輸出結構化資料。

```yaml
---
summary: "2 至 3 句：這集在回答什麼問題、結論是什麼"
chapters:            # 4 至 8 個，時間碼取自逐字稿，點了會跳到音檔該秒
  - time: "12:30"
    title: "用聽眾會問的話命名，不寫『第二段』"
quotes:              # 3 至 5 句，用老查已選定的金句，逐字原話
  - text: "情緒會流動，也會往安全的地方找出口。"
    speaker: "阿分"
faq:                 # 3 題，答案 2 至 4 句、可單獨閱讀
  - q: "..."
    a: "..."
related:             # 選填：週四 GEO 文章上線後回填網址
  - "https://beyond-ans.com/blog/{slug}/"
---
```

- 素材：show-notes、已選定金句與逐字稿時間碼，屬於重新整理，不另寫新觀點。
- 審核：跟主題文同一關過阿維；家人私事、未成年人的可辨識細節不放。章節標題與摘要由鐵雄核對時間碼與原話。
- 上線：列入上架授權包的一列「網站單集重點」。Firstory 正片公開並讀回後才 commit＋push（單集頁要等 RSS 有這集才會產生），推送後讀回單集頁出現「本集重點」。
- 週四 GEO 文章上線後，把文章網址補進 `related`，讓單集頁與文章互相連結。

### 7. 結尾報告
回報單集文字／音檔／IG 狀態，以及當週六個 item 的來源、形式、素材、原音、brief、render、QC、品牌、核准與各平台狀態。清楚區分樣片、成片、草稿、排程與公開；標示下一棒及缺件，不再硬列舊三支精華為必做。

### 8. 週四 GEO 文章（居易，獨立追蹤）
每集上架後，居易依 `seo-article-writer` 的「週四 GEO／SEO 文章」節奏寫本集主題文章（模式 A，帶入同一個 `{slug}`），由居易自己的週節奏管理，不阻塞星期天的其他項目。

---

## 涉及但不修改的既有工具
原樣呼叫，不動內部邏輯：
- `tools/ig-images/run_ig.ps1`
- `tools/firstory-upload/upload.mjs`
- `tools/fb-promo/run.bat` / `run.sh`
- `shorts-pipeline` skill（步驟 6 直接引用其步驟，不要複製貼上整份內容）
- `podcast-teaser-video` skill（句剪，原名預報；步驟 5 每週六支金句短片與專屬封面，人物版僅明確指定時使用）
- `paper-collage-video` skill（剪紙，2026-10-14 起只在老查點名時作特別企劃，不占固定槽位）
- `shi-tou` skill（實透，2026-10-14 起只在老查點名時作特別企劃；被點名時星期天管理選段、製作交接與發布槽位）
- `seo-article-writer` skill（居易，選配步驟 8 引用，不要複製貼上整份內容）

## 相關記憶
`project_podcast_production`、`project_ig_pipeline`、`project_shorts_pipeline`、`project_fb_promo_pipeline`、`feedback_interaction_style`、`feedback_quote_selection`、`project_podcast_strategy`、`project_marketing_team_upgrade`
