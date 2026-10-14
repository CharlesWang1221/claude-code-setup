# Voicebox 本機聲音複製：安裝與使用邊界

狀態：試用中（2026-10-14 老查核准安裝測試）。盲聽未通過前，不得用於任何對外成品。

## 是什麼

開源本機語音工作室 [jamiepine/voicebox](https://github.com/jamiepine/voicebox)，MIT 授權，不需訂閱。幾秒原音即可複製聲音，內建 Qwen3-TTS、Chatterbox、Kokoro 等引擎與 Whisper 聽寫，所有運算留在本機。

## 安裝（只限 Mac）

Windows PC 是公司電腦，禁止安裝外部軟體，不得安裝 Voicebox。Windows 端只能編輯本文件與相關 Skill。

Mac 在 repo 執行 `git pull` 後，再執行 `./tools/install-voicebox.sh`。Apple Silicon 用 MLX 加速，首次開啟會下載語音模型；被 Gatekeeper 擋下時，到「隱私權與安全性」按「仍要打開」。

換版本時加參數，例如 `./tools/install-voicebox.sh 0.6.0`。

## 聲音檔的保存

- 聲音樣本、聲音檔、生成音檔一律不得放進本 repo（公開）
- 備份用 App 的匯出功能，存到私人 Drive
- 用來複製的原音只取老查本人的錄音

## 使用邊界

| 用途 | 狀態 |
| --- | --- |
| Podcast 正片念錯 1～2 個詞的補錄 | 盲聽通過後才可用 |
| 解題、油管長片的圖解旁白 | 盲聽通過後才可用；YouTube 上架須勾選合成內容標示 |
| 句剪金句短片、任何標示為原話的內容 | 禁用，必須用核准原音 |
| 阿分的聲音 | 須取得阿分書面同意並寫明用途後才可建立 |
| 大寶、小寶的聲音 | 禁止建立 |

## 盲聽驗收

1. 選一句正片原話，以同一句文字生成 AI 版
2. 兩版隨機順序給老查與阿分各聽一次
3. 兩人都分辨不出，且沒有大陸腔，才算通過；結果記入 `docs/RULE_CHANGELOG.md`
