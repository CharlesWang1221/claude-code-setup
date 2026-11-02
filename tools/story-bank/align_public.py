"""把逐字稿時間碼對到公開版音檔（STORY-BANK-PILOT）。

本機逐字稿是對「剪輯前或某一版」音檔做的；公開版若又剪過，時間碼會偏移，被剪掉的句子也不能入庫。
本工具用音量包絡做逐句比對，輸出每句的狀態（kept／cut）與公開版時間碼。

用法：
  python -I tools/story-bank/align_public.py --public <公開版.mp3> --local <逐字稿對應的本機音檔> \
      --transcript <逐字稿.txt|.docx> --out <timemap.json>

需要 ffmpeg 與 numpy。公開版音檔可從 Firstory RSS 的 enclosure 下載（只放暫存區，不進 repo）。
判讀：
  - 每句取 6 秒窗，在公開版往前 320 秒內找最相似位置，相關係數 corr ≥ 0.85 且與鄰近句偏移一致者當錨點。
  - 錨點之間偏移相同 → 中間的句子保留；偏移跳動處相關不足 → 判為公開版已剪掉（cut）。
  - 兩版完全相同時（例如 S4EP2），全部 kept、偏移 0。
"""
from __future__ import annotations

import argparse
import bisect
import importlib.util
import json
import statistics
import subprocess
import sys
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("story_bank_build", HERE / "build_index.py")
bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bi)  # type: ignore[union-attr]

FPS, WIN, SEARCH_BACK = 10, 60, 3200  # 10 幀／秒、6 秒窗、往前找 320 秒


def envelope(path: str) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "4000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    hop = 4000 // FPS
    n = len(a) // hop
    return np.log1p(np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--public", required=True)
    ap.add_argument("--local", required=True)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    src = Path(a.transcript)
    segs = bi.parse_docx(src) if src.suffix.lower() == ".docx" else bi.parse_txt(src)
    pub, loc = envelope(a.public), envelope(a.local)
    pw = sliding_window_view(pub, WIN)
    pn = (pw - pw.mean(1, keepdims=True)) / (pw.std(1, keepdims=True) + 1e-6)

    rows = []
    for s in segs:
        i = min(s["t"] * FPS, len(loc) - WIN)
        w = loc[i : i + WIN]
        w = (w - w.mean()) / (w.std() + 1e-6)
        lo, hi = max(0, i - SEARCH_BACK), min(len(pn), i + 50)
        c = pn[lo:hi] @ w / WIN
        k = int(c.argmax())
        p = (lo + k) / FPS
        rows.append({"local": s["t"], "speaker": s["speaker"], "corr": round(float(c[k]), 2), "off": s["t"] - p})

    good = [i for i, r in enumerate(rows) if r["corr"] >= 0.85 and -2 <= r["off"] <= SEARCH_BACK / FPS]
    offs = [rows[i]["off"] for i in good]
    med = [statistics.median(offs[max(0, k - 4) : k + 5]) for k in range(len(offs))]
    anchors, vals = [], []
    for i, m, raw in zip(good, med, offs):
        if abs(raw - m) <= 1.5 and not (vals and m < vals[-1] - 1.5):
            anchors.append(i)
            vals.append(raw)
    aset = set(anchors)
    total_cut = (len(loc) - len(pub)) / FPS

    for i, r in enumerate(rows):
        k = bisect.bisect_left(anchors, i)
        prev = vals[k - 1] if k > 0 else 0.0
        nxt = vals[k] if k < len(vals) else total_cut
        if i in aset:
            off = r["off"]
        elif abs(prev - nxt) <= 1.5:
            off = prev
        elif r["corr"] >= 0.7 and (abs(r["off"] - prev) <= 1.5 or abs(r["off"] - nxt) <= 1.5):
            off = r["off"]
        else:
            off = None
        r["status"] = "kept" if off is not None else "cut"
        r["pub_t"] = None if off is None else max(0, round(r["local"] - off))
        del r["off"]

    Path(a.out).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    cut = [r for r in rows if r["status"] == "cut"]
    print(f"本機 {len(loc) / FPS:.0f}s／公開 {len(pub) / FPS:.0f}s；{len(rows)} 句 → 保留 {len(rows) - len(cut)}、公開版已剪 {len(cut)} → {a.out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
