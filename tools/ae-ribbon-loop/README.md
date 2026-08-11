# AE 絲綢流動背景 Loop — build-ribbon-loop.jsx

參考來源：一支帶版權浮水印的「RAN DESIGN」品牌迴圈背景素材（`然.DESIGN`），不能直接拿來用，
所以用原生 AE 效果重製同款質感：深藍→青綠漸層底 + 半透明絲帶波浪流動。

## 用法

1. 打開 After Effects
2. `File > Scripts > Run Script File...` → 選 `build-ribbon-loop.jsx`
3. 跑完會自動建立一個叫 `RibbonLoop_BG` 的 comp，跳出視窗列出需要手動補的地方

## 圖層結構

```
RibbonLoop_BG (1920×1080, 30fps, 8s)
├── 06_Text_YOUR_TAGLINE_HERE
├── 06_Text_YOUR_BRAND
├── 05_Ribbons_Precomp（Glow）
│   ├── 02_Ribbon_A（Fractal Noise 拉長條 + Turbulent Displace）
│   ├── 03_Ribbon_B
│   └── 04_Ribbon_C
└── 01_BG_Gradient（4-Color Gradient）
```

## 跑完一定要手動做的事

1. **換文字** — `06_Text_*` 現在是 placeholder（YOUR BRAND / YOUR TAGLINE HERE），改成自己的
2. **無縫 loop 輸出** — Work Area 設 0 到少一個 frame（8 秒 30fps → 設 `0:00` 到 `0:07:29`），
   整整 8 秒輸出會在接點多一個重複 frame，卡頓感就是這裡來的
3. 如果視窗跳出「⚠ 以下屬性腳本設定失敗」，代表某個效果的屬性名稱在你那個 AE 版本對不上，
   照清單去 Effect Controls 面板手動補那幾個數值即可，其他部分都已經建好

## 想要更接近原片的絲滑質感（進階，選用）

原片用的手法八成是 `CC Vector Blur`（Streamline 模式），腳本刻意沒有自動加這個效果，
因為它的下拉選單（Type / Property）用腳本猜索引風險太高，容易做出「看起來加了但選錯選項」的結果。
自己動手比較穩：

1. 在 `05_Ribbons_Precomp` 上加 `CC Vector Blur`
2. `Type` 切成 `Vector Map`
3. `Property` 指到任一條 `Ribbon` 圖層
4. `Amount` 抓 200–300，`Map Softness` 抓 8–10
