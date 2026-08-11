// build-ribbon-loop.jsx
//
// 用途：自動搭出「絲綢流動背景」loop 的圖層結構（原生 AE，無外掛）
// 對照：RAN DESIGN 品牌迴圈背景素材（含版權浮水印，不可直接使用）的重製版
// 技術路徑：Fractal Noise 拉成長條 → Turbulent Displace 扭動 → Glow 收邊 → Screen 疊加
//
// 用法：After Effects → File > Scripts > Run Script File... → 選這個檔案
//
// 注意：Fractal Noise / Turbulent Displace 的下拉選單型屬性（Fractal Type、Displacement）
// 刻意維持 AE 預設值，不用猜測的索引去設定，避免跑出看起來對但實際錨錯選項的結果。
// 數值型屬性（Contrast、Scale、Amount、Evolution…）才用腳本直接設定。
// 每個效果屬性都包了 try/catch，就算某個屬性名稱在你的 AE 版本對不上，
// 腳本仍會把其他部分建完，並在最後跳出的視窗列出哪些地方要你自己手動補。

(function () {

  var warnings = [];

  function trySet(effect, propName, value, isExpr) {
    try {
      var p = effect.property(propName);
      if (isExpr) { p.expression = value; } else { p.setValue(value); }
    } catch (err) {
      warnings.push("[" + effect.name + "] " + propName + " 設定失敗：" + err.toString());
    }
  }

  app.beginUndoGroup("Build Ribbon Loop BG");

  try {

    var W = 1920, H = 1080, FPS = 30, DUR = 8; // 8 秒 loop，長度可自行改

    var comp = app.project.items.addComp("RibbonLoop_BG", W, H, 1, DUR, FPS);
    comp.bgColor = [0.02, 0.03, 0.06];

    // ── 01 背景四色漸層 ──────────────────────────────
    var bg = comp.layers.addSolid([0, 0, 0], "01_BG_Gradient", W, H, 1, DUR);
    var grad = null;
    try {
      grad = bg.property("Effects").addProperty("ADBE 4ColorGradient");
    } catch (err) {
      warnings.push("4-Color Gradient 加不上去（matchName 對不上這台 AE），改用單一 Gradient Ramp 手動上色：" + err.toString());
    }
    if (grad) {
      trySet(grad, "Point 1", [0, H]);
      trySet(grad, "Color 1", [0.10, 0.65, 0.45, 1]);  // 左下：綠
      trySet(grad, "Point 2", [W, 0]);
      trySet(grad, "Color 2", [0.05, 0.15, 0.45, 1]);  // 右上：深藍
      trySet(grad, "Point 3", [0, 0]);
      trySet(grad, "Color 3", [0.08, 0.35, 0.60, 1]);  // 左上：青藍
      trySet(grad, "Point 4", [W, H]);
      trySet(grad, "Color 4", [0.02, 0.08, 0.30, 1]);  // 右下：深藏青
      trySet(grad, "Blend", 55);
    }

    // ── 02-04 三條絲帶 ──────────────────────────────
    // evoSpeed(度/秒) * DUR 必須是 360 的倍數，Evolution 才能在 loop 起訖點完全對齊
    var ribbonSpecs = [
      { name: "02_Ribbon_A", rot: 15,  scaleW: 420, scaleH: 35, complexity: 3, evoSpeed: 45,   tdAmount: 80,  tdSize: 250, opacity: 85 },
      { name: "03_Ribbon_B", rot: -10, scaleW: 380, scaleH: 45, complexity: 4, evoSpeed: 90,   tdAmount: 60,  tdSize: 180, opacity: 75 },
      { name: "04_Ribbon_C", rot: 5,   scaleW: 300, scaleH: 55, complexity: 3, evoSpeed: 22.5, tdAmount: 100, tdSize: 320, opacity: 60 }
    ];

    var ribbonIndices = [];

    for (var i = 0; i < ribbonSpecs.length; i++) {
      var spec = ribbonSpecs[i];
      var solid = comp.layers.addSolid([1, 1, 1], spec.name, W, H, 1, DUR);
      solid.blendingMode = BlendingMode.SCREEN;
      solid.opacity.setValue(spec.opacity);

      var fn = null;
      try {
        fn = solid.property("Effects").addProperty("ADBE Fractal Noise");
      } catch (err) {
        warnings.push("[" + spec.name + "] Fractal Noise 加不上去：" + err.toString());
      }

      if (fn) {
        trySet(fn, "Contrast", 190);
        trySet(fn, "Brightness", -15);
        trySet(fn, "Complexity", spec.complexity);
        trySet(fn, "Evolution", "time*" + spec.evoSpeed, true);

        try {
          var xf = fn.property("Transform");
          trySet(xf, "Uniform Scaling", 0);       // 關掉等比縮放，才能把噪點拉成長條絲帶
          trySet(xf, "Scale Width", spec.scaleW);
          trySet(xf, "Scale Height", spec.scaleH);
          trySet(xf, "Rotation", spec.rot);
        } catch (err) {
          warnings.push("[" + spec.name + "] Transform 子屬性設定失敗：" + err.toString());
        }
      }

      var td = null;
      try {
        td = solid.property("Effects").addProperty("ADBE Turbulent Displace");
      } catch (err) {
        warnings.push("[" + spec.name + "] Turbulent Displace 加不上去：" + err.toString());
      }

      if (td) {
        trySet(td, "Amount", spec.tdAmount);
        trySet(td, "Size", spec.tdSize);
        trySet(td, "Complexity", spec.complexity);
        trySet(td, "Evolution", "time*" + spec.evoSpeed, true);
      }

      ribbonIndices.push(solid.index);
    }

    // 把三條絲帶收進一個 precomp，統一上 Glow
    comp.layers.precompose(ribbonIndices, "05_Ribbons_Precomp", true);
    var ribbonsPreLayer = comp.layer("05_Ribbons_Precomp");
    try {
      var glow = ribbonsPreLayer.property("Effects").addProperty("ADBE Glo2");
      trySet(glow, "Glow Threshold", 65);
      trySet(glow, "Glow Radius", 45);
      trySet(glow, "Glow Intensity", 1.3);
    } catch (err) {
      warnings.push("Glow 加不上去：" + err.toString());
    }

    // ── 06 文字（demo 用 placeholder，記得換成你自己的品牌字）──
    function addCenteredText(str, size, posY, opacity) {
      var t = comp.layers.addText(str);
      try {
        var textProp = t.property("Source Text");
        var doc = textProp.value;
        doc.fontSize = size;
        doc.fillColor = [1, 1, 1];
        doc.font = "ArialMT";
        doc.justification = ParagraphJustification.CENTER_JUSTIFY;
        textProp.setValue(doc);
      } catch (err) {
        warnings.push("[" + str + "] 文字樣式設定失敗（可能是字體找不到）：" + err.toString());
      }
      t.position.setValue([W / 2, posY]);
      t.opacity.setValue(opacity);
      t.name = "06_Text_" + str.replace(/\s+/g, "_");
      return t;
    }

    addCenteredText("YOUR BRAND", 90, H / 2, 100);
    addCenteredText("YOUR TAGLINE HERE", 26, H / 2 + 130, 70);

    var msg = "已建立 RibbonLoop_BG。\n\n手動確認/微調：\n" +
      "1. 把 06_Text 圖層文字換成你自己的品牌名／tagline（現在是 placeholder）\n" +
      "2. 想要更接近絲綢流線質感：在 05_Ribbons_Precomp 上加 CC Vector Blur，" +
      "Type 手動切成 Vector Map、Property 指向任一條 Ribbon 圖層、Amount 抓 200-300\n" +
      "3. 輸出無縫 loop：Work Area 設 0 到少一個 frame（例如 8 秒 30fps 設 0:00-7:29），不要整整 8 秒都輸出\n" +
      "4. Fractal Noise 的 Fractal Type 若想要更滑順，手動切成 Turbulent Smooth（腳本沒動這個下拉選單）";

    if (warnings.length > 0) {
      msg += "\n\n⚠ 以下屬性腳本設定失敗，需要手動補：\n- " + warnings.join("\n- ");
    }

    alert(msg);

  } catch (e) {
    alert("腳本執行中斷：" + e.toString() + "（行號 " + e.line + "）");
  }

  app.endUndoGroup();

})();
