"""節目素材庫：把逐字稿切成候選片段（STORY-BANK-PILOT）。

用法：
  python -I tools/story-bank/build_index.py split  --episode S4EP1 --transcript <逐字稿.txt|.docx> --out <dir> [--timemap <timemap.json>]
  python -I tools/story-bank/build_index.py merge  --passages <dir>/S4EP1.passages.jsonl --tags <dir>/S4EP1.tags.json --out <index.jsonl>
  python -I tools/story-bank/build_index.py search --index <index.jsonl> 關鍵詞 [關鍵詞...]

split：解析兩種格式（txt：時間碼＋講者一行、內容一行；docx：時間碼＋講者＋內容同一行），
       依講者輪替與停頓切成 40–120 秒的候選片段，輸出 passages.jsonl，供人工或 Codex 標註。
merge：把標註檔（topics、story_type、quote、child_quote、drop）併回片段，寫進索引。
search：在索引的原文、主題、原話中找關鍵詞，列出集數、時間碼與原話。

索引與逐字稿內容都屬私人資料，只能輸出到老查指定的私人位置，不得寫進 repo。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

SPEAKERS = ("老查", "阿分", "大寶", "小寶")
TS = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\s*(.*)$")
NON_ZH_NOISE = re.compile(r"[぀-ヿ]")  # 日文假名：Whisper 幻覺的常見訊號

MIN_SEC, MAX_SEC, GAP_SEC = 40, 120, 6


def to_sec(h: str, m: str, s: str) -> int:
    return int(h) * 3600 + int(m) * 60 + int(s)


def fmt(sec: int) -> str:
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def parse_txt(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    segs, i = [], 0
    while i < len(lines):
        m = TS.match(lines[i].strip())
        if m and m.group(4).strip():
            text = lines[i + 1].strip() if i + 1 < len(lines) else ""
            segs.append({"t": to_sec(*m.group(1, 2, 3)), "speaker": m.group(4).strip(), "text": text})
            i += 2
        else:
            i += 1
    return segs


def parse_docx(path: Path) -> list[dict]:
    xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    paras = [re.sub(r"<[^>]+>", "", p).strip() for p in re.findall(r"<w:p[ >].*?</w:p>", xml)]
    segs = []
    for p in paras:
        m = TS.match(p)
        if not m:
            continue
        rest = m.group(4).strip()
        speaker = next((s for s in SPEAKERS if rest.startswith(s)), "?")
        text = rest[len(speaker):].strip() if speaker != "?" else rest
        segs.append({"t": to_sec(*m.group(1, 2, 3)), "speaker": speaker, "text": text})
    return segs


def clean(segs: list[dict]) -> tuple[list[dict], list[dict]]:
    kept, dropped = [], []
    for s in segs:
        if not s["text"] or NON_ZH_NOISE.search(s["text"]):
            dropped.append(s)
        else:
            kept.append(s)
    return kept, dropped


def split_passages(episode: str, segs: list[dict]) -> list[dict]:
    passages, cur = [], []

    def flush(end_t: int) -> None:
        if not cur:
            return
        start = cur[0]["t"]
        speakers = sorted({s["speaker"] for s in cur}, key=lambda x: (x not in SPEAKERS, x))
        passages.append({
            "id": f"{episode}-{len(passages) + 1:03d}",
            "episode": episode,
            "start": fmt(start),
            "end": fmt(end_t),
            "speakers": speakers,
            "text": "\n".join(f"{s['speaker']}：{s['text']}" for s in cur),
        })
        cur.clear()

    for i, s in enumerate(segs):
        nxt_t = segs[i + 1]["t"] if i + 1 < len(segs) else s["t"] + 5
        cur.append(s)
        dur = nxt_t - cur[0]["t"]
        gap = nxt_t - s["t"]
        if dur >= MAX_SEC or (dur >= MIN_SEC and gap >= GAP_SEC):
            flush(nxt_t)
    if cur:
        flush(cur[-1]["t"] + 5)
    return passages


def apply_timemap(segs: list[dict], path: str) -> tuple[list[dict], list[dict]]:
    """套用 align_public.py 的結果：公開版已剪的句子剔除，其餘改用公開版時間碼。"""
    tm = json.loads(Path(path).read_text(encoding="utf-8"))
    if len(tm) != len(segs) or any(r["local"] != s["t"] for r, s in zip(tm, segs)):
        sys.exit("timemap 與逐字稿句數或時間碼對不上，請用同一份逐字稿重跑 align_public.py")
    kept, cut = [], []
    for r, s in zip(tm, segs):
        if r["status"] == "cut":
            cut.append(s)
        else:
            kept.append({**s, "t": r["pub_t"], "local_t": s["t"]})
    return kept, cut


def cmd_split(a: argparse.Namespace) -> None:
    src = Path(a.transcript)
    segs = parse_docx(src) if src.suffix.lower() == ".docx" else parse_txt(src)
    cut: list[dict] = []
    if a.timemap:
        segs, cut = apply_timemap(segs, a.timemap)
        print(f"{a.episode}: 公開版已剪 {len(cut)} 句，不入庫；時間碼改用公開版")
    kept, dropped = clean(segs)
    passages = split_passages(a.episode, kept)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    pf = out / f"{a.episode}.passages.jsonl"
    with pf.open("w", encoding="utf-8") as fh:
        for p in passages:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{a.episode}: {len(segs)} 段 → 保留 {len(kept)}、剔除 {len(dropped)}、片段 {len(passages)} → {pf}")
    for d in dropped:
        print(f"  剔除 {fmt(d['t'])} {d['speaker']}：{d['text'][:40]}")
    unknown = sorted({s["speaker"] for s in kept} - set(SPEAKERS))
    if unknown:
        print(f"  注意：有未命名講者 {unknown}，入庫前要老查確認")


def cmd_merge(a: argparse.Namespace) -> None:
    tags = json.loads(Path(a.tags).read_text(encoding="utf-8"))
    passages = [json.loads(l) for l in Path(a.passages).read_text(encoding="utf-8").splitlines() if l.strip()]
    out = Path(a.out)
    existing = []
    if out.exists():
        existing = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
    episodes = {p["episode"] for p in passages}
    existing = [r for r in existing if r["episode"] not in episodes]
    merged, missing = [], []
    for p in passages:
        t = tags.get(p["id"])
        if t is None:
            missing.append(p["id"])
            continue
        if t.get("drop"):
            continue
        quote = t.get("quote", "")
        if quote and quote.replace("…", "") not in p["text"].replace("\n", ""):
            # 原話必須逐字取自片段（允許用 … 省略），否則不收
            parts = [x for x in quote.split("…") if x]
            if not all(x in p["text"] for x in parts):
                sys.exit(f"{p['id']} 的 quote 不是片段原文：{quote}")
        merged.append({**p, "topics": t.get("topics", []), "story_type": t.get("story_type", ""),
                       "quote": quote, "quote_speaker": t.get("quote_speaker", ""),
                       "child_quote": bool(t.get("child_quote")), "note": t.get("note", ""), "public": True})
    if missing:
        sys.exit(f"缺標註：{missing[:10]}（共 {len(missing)} 筆）")
    with out.open("w", encoding="utf-8") as fh:
        for r in existing + merged:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"併入 {len(merged)} 筆（{', '.join(sorted(episodes))}），索引共 {len(existing) + len(merged)} 筆 → {out}")


def cmd_search(a: argparse.Namespace) -> None:
    rows = [json.loads(l) for l in Path(a.index).read_text(encoding="utf-8").splitlines() if l.strip()]
    hits = []
    for r in rows:
        hay = " ".join([r["text"], " ".join(r["topics"]), r["quote"]])
        score = sum(hay.count(k) for k in a.keywords) + 3 * sum(k in " ".join(r["topics"]) for k in a.keywords)
        if score:
            hits.append((score, r))
    hits.sort(key=lambda x: -x[0])
    for score, r in hits[: a.limit]:
        flag = "［孩子原話，對外前交阿維］" if r["child_quote"] else ""
        print(f"{r['episode']} {r['start']}–{r['end']} {r['story_type']} {'/'.join(r['topics'])} {flag}")
        print(f"  {r['quote_speaker']}：「{r['quote']}」")
        if r.get("note"):
            print(f"  ⚠ {r['note']}")
    print(f"共 {len(hits)} 筆命中，顯示 {min(len(hits), a.limit)} 筆")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split"); s.add_argument("--episode", required=True); s.add_argument("--transcript", required=True); s.add_argument("--out", required=True)
    s.add_argument("--timemap", help="align_public.py 輸出；公開版與逐字稿音檔不同時必填")
    m = sub.add_parser("merge"); m.add_argument("--passages", required=True); m.add_argument("--tags", required=True); m.add_argument("--out", required=True)
    q = sub.add_parser("search"); q.add_argument("--index", required=True); q.add_argument("--limit", type=int, default=10); q.add_argument("keywords", nargs="+")
    a = ap.parse_args()
    {"split": cmd_split, "merge": cmd_merge, "search": cmd_search}[a.cmd](a)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
