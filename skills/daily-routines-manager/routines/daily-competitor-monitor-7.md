---
trigger_id: trig_01HaRbUMGiddyezfGpoq1FFS
name: daily-competitor-monitor-7
cron: "0 0 1-7,15-21 * 5"  # 雙週週五 08:00 台北時間（2026-08-12 由每月1、15日改為每月第1、3週的週五；cron無「雙週」語法，用此慣用寫法逼近，不保證每次精準隔14天）
enabled: true
output: Gmail（siming1221@gmail.com，CC debra.hdf@gmail.com），監控7個同賽道創作者(4台灣+3國際)的最新動態，每列含重疊/差異/可借鑑點分析；2026-08-12 改名「雙週競品動態監控」，搜尋窗從1-3天拉長到1-2週
mcp_connections: [Zapier]
model: claude-sonnet-5
allowed_tools: [WebSearch, WebFetch, mcp__Zapier__list_enabled_zapier_actions, mcp__Zapier__execute_zapier_write_action, mcp__Zapier__execute_zapier_read_action, mcp__Zapier__discover_zapier_actions]
---

## 監控對象（固定 7 個，4 台灣＋3 國際，2026-08-05 定案）

台灣：
1. **只能喝酒的圖書館**（Otherwise Library，Ting & Hank 夫妻檔，哲學類）——對標性最高：夫妻檔主持結構跟老查+阿分同構，核心哲學（疑惑是生命的本質/擁抱不確定）跟金繼/物心分離高度重疊。
2. **大人的 Small Talk**（姚詩豪+張國洋）——雙人搭檔把抽象邏輯講成可執行內容，理性/管理顧問視角，可借鑑「如何把抽象講清楚」。
3. **本子在隔壁 Benzi**（心理學/腦科學科普，單人主持）。
4. **FarHugs 遠距抱抱**（心理健康/個人成長/關係議題）。

國際（2026-08-05 新增）：
5. **We Can Do Hard Things**（Glennon Doyle+Abby Wambach+Amanda Doyle，配偶+姊妹三人組）——核心是脆弱揭露+接受不完美人生，全球最大同類 podcast 之一，累積超5億次播放，每週二四更新。對標「規模化後還能不能保持真實」。
6. **Unlocking Us**（Brené Brown，shame/vulnerability 研究學者主持）——核心命題「裂縫值得被看見、不用被磨平」幾乎是金繼哲學的西方學術版，2026年2月剛回歸更新。對標「個人哲學怎麼包裝成有學術背書的內容產品」。
7. **On Purpose with Jay Shetty**（心理學背書的生活建議）——2026年簽下 Netflix/Spotify 獨家約（上億美元），商業化路徑可借鑑，但內容偏勵志語錄，真實裂縫揭露較少（跟劉軒的差異點類似，借鑑價值有限）。

## Prompt

你要產生並寄出「雙週競品動態監控」email。監控對象固定 7 個同賽道 Podcast/創作者（4 個台灣＋3 個國際）：①只能喝酒的圖書館（Otherwise Library，Ting & Hank 夫妻檔，哲學類）②大人的 Small Talk（姚詩豪+張國洋）③本子在隔壁 Benzi（心理學/腦科學科普，單人主持）④FarHugs 遠距抱抱（心理健康/個人成長/關係議題）⑤We Can Do Hard Things（Glennon Doyle+Abby Wambach+Amanda Doyle，配偶+姊妹三人組，核心是脆弱揭露+接受不完美人生，全球最大同類 podcast 之一，累積超5億次播放）⑥Unlocking Us（Brené Brown，shame/vulnerability 研究學者主持，核心命題「裂縫值得被看見、不用被磨平」是金繼哲學的西方學術版，2026年2月剛回歸更新）⑦On Purpose with Jay Shetty（心理學背書的生活建議，2026年簽下 Netflix/Spotify 獨家約，商業化路徑可借鑑但真實裂縫揭露較少）。請依序完成：

## 1. 防重複檢查
先用 mcp__Zapier__execute_zapier_read_action（selected_api: GoogleMailV2CLIAPI, action: message, tool_name: gmail_find_email, params: {query: "subject:雙週競品動態監控"}）查詢過去約 14 天已寄送的報告，整理出「近期已提過的集數/內容標題」（依創作者分類）。只有查詢失敗或查不到歷史紀錄才可略過，並在報告最後備註「本次未執行防重複比對」。

## 2. 搜尋 7 個對象的最新動態
用 WebSearch（必要時 WebFetch 確認連結有效）查每個創作者最近 1-2 週內有沒有新集數/新影片/新貼文：
- 若有新內容：抓標題、平台連結、內容摘要（3-5句說明這集在講什麼）。3 個國際對象（We Can Do Hard Things / Unlocking Us / On Purpose）用英文搜尋，但摘要一律翻成繁體中文給老查看，若有適合的原話金句可保留一句英文原文附中文翻譯
- 若近期沒有新內容，或搜到的內容跟步驟1「已提過清單」重複：該創作者這欄寫「近期無新動態」，不要硬掰內容
- 連結必須直接指向該集/該貼文本身，不能是節目首頁
- 額外留意：這集/這則貼文有沒有蹭到近期熱門話題（例如暢銷書、時事、社群熱議事件，國際對象則看英語圈熱點），如果有要指出蹭的是什麼

收件人背景：老查與阿分共同主持《不標準答案》Podcast，核心哲學是金繼（裂縫不必被磨平）、物心分離、慢速野獸（反效率文化），三大內容支柱是社會議題深度集、金繼時刻（個人脆弱裂縫）、書喔吾聊。老查正在做 YouTube 擴張、熟悉 n8n 自動化工具鏈。

## 3. 產生 email 報告
主旨：「雙週競品動態監控 - {今天日期，格式 YYYY-MM-DD}」

內容用 HTML email（body_type "html"），Word 風格 HTML 表格：
- 信件最上方：<h2 style="color:#4472C4;">【雙週競品動態監控】{今天日期}</h2>
- 一個表格 <table style="border-collapse:collapse;width:100%;font-family:Calibri,Arial,sans-serif;font-size:14px;">，標題列 <tr><td style="background-color:#4472C4;color:#ffffff;font-weight:bold;padding:8px 10px;">，欄位依序：創作者｜最新動態(標題+連結)｜內容摘要｜跟《不標準答案》的重疊/差異/可借鑑點｜是否蹭熱點
- 內容列 banded rows，背景色白/淡灰（#F2F2F2）交替，每列 <td style="padding:8px 10px;border:1px solid #ccc;vertical-align:top;">，7 個創作者各一列，建議用一個較淺的分隔列或在創作者名稱前標註「🇹🇼」「🌍」區分台灣/國際對象
- 「跟《不標準答案》的重疊/差異/可借鑑點」這欄必須具體，不要泛用空話，要點出這次的動態跟收件人自己節目的哲學/題材/格式有什麼可以直接拿來用或該警惕的地方

信件最下方加「🎯 本次觀察」區塊：一段文字（3-5句），從這 7 個創作者這次的動態裡挑一個對收件人最有參考價值的信號，具體說明為什麼值得注意、可以怎麼回應。如果 7 個都無新動態，這裡就寫「本次 7 個監控對象皆無新動態，建議之後可觀察～」。

## 4. 寄送
用 mcp__Zapier__execute_zapier_write_action（selected_api: GoogleMailV2CLIAPI, action: message, tool_name: gmail_send_email）寄送。主收件人（to）：siming1221@gmail.com，同時加上 CC（cc）給 debra.hdf@gmail.com（阿分）——讓這封信看起來是老查寄出並 CC 給阿分，不是兩人平行主收件人。呼叫 gmail_send_email 時記得帶上 cc 參數。

寄送前務必先用 mcp__Zapier__list_enabled_zapier_actions 確認 Gmail 動作已啟用，若未啟用則用 mcp__Zapier__discover_zapier_actions 尋找並啟用。每次執行都必須完成寄信這個步驟，不要只做搜尋不寄信。
