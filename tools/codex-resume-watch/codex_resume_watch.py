#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex 額度自動續跑 watchdog。

背景：Codex CLI 原生沒有「額度用完、恢復後自動續跑」這個功能（官方 issue
openai/codex#21073，2026-05-04 開立，查證時仍是 Open，沒有排進任何 milestone）。
社群已有幾個非官方第三方工具做同樣的事，本腳本是自建、可審查版本，邏輯相同：

  讀最新 session 的 rate_limits.primary.resets_at
  → 等到那個時間（留一點緩衝，避免伺服器端還沒真正刷新）
  → 先記住這個 resets_at 已經處理過（續跑期間排程再觸發也不重複接續）
  → 呼叫一次 `codex exec resume <卡住的 session id> "<prompt>"`
  → 記錄結果；resets_at 已過去超過 6 小時的舊紀錄不接續

資料來源是 `~/.codex/sessions/**/rollout-*.jsonl`，這是 Codex CLI 自己寫的本機逐字記錄，
不是額外的帳戶 API；`docs/SKILL_HEALTH_REGISTER.md` 已經多次確認 Codex 沒有可讀帳戶額度的
官方工具，這支腳本讀的是「上一個 session 最後一次回報的使用率與重置時間」，不是即時帳戶查詢。

用法：
  python tools/codex-resume-watch/codex_resume_watch.py check [--cwd PATH]
  python tools/codex-resume-watch/codex_resume_watch.py watch [--dry-run] [--cwd PATH] [--prompt "..."]
  python tools/codex-resume-watch/codex_resume_watch.py install [--interval-minutes N]
  python tools/codex-resume-watch/codex_resume_watch.py uninstall

跨機器（Mac／Windows）：
- 這支程式碼跟著 repo 走，Mac／Windows 兩邊各自 `git pull` 後就是同一份腳本，不需要另外同步。
- 排程是作業系統層級設定，不會跟著 git 走：`install` 會依平台自動選擇 Mac 用 `launchd`、
  Windows 用工作排程器（`schtasks`），兩台機器都要各自執行一次 `install`。
- 狀態檔與 log（`output/codex-resume-watch/`）刻意不進 git、不跨機器同步：每台機器的
  `~/.codex/sessions` 只記錄「在這台機器上跑的 session」，額度卡住只能由卡住的那台機器自己續跑，
  不是共用帳戶額度就代表哪台機器都能接。兩台機器都要各自裝好 `install`，這個功能才對你兩邊都有效。

未驗證事項（老實寫在這裡，不要假裝測過）：
- 本機目前找不到一次「真的卡在額度」當下留存的 session 檔案可以比對，
  「是否卡在額度」是用 used_percent 門檻與 rate_limit_reached_type 欄位做代理判斷，
  不是官方文件白紙黑字保證的訊號。
- 正式排程前，先用 check 看輸出合不合理，並實際觀察至少一次真實的額度恢復情形，
  確認 watch 判斷正確、`codex exec resume --last` 真的接上對的工作，再完全信任排程。
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Asia/Taipei 固定 UTC+8、無日光節約；跟 tools/duoli/duoli.py 同樣理由，不用 zoneinfo
TZ = dt.timezone(dt.timedelta(hours=8), "Asia/Taipei")
# Codex 有設 CODEX_HOME 時 session 寫在那裡（例如這台 Windows 是 %LOCALAPPDATA%\CodexCLI），沒設才是 ~/.codex
SESSIONS_DIR = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex")) / "sessions"
REPO = Path(__file__).resolve().parents[2]
STATE_DIR = REPO / "output" / "codex-resume-watch"
STATE_FILE = STATE_DIR / "state.json"
LOG_FILE = STATE_DIR / "watch.log"

LAUNCHD_LABEL = "com.beyondans.codex-resume-watch"
LAUNCHD_TEMPLATE = Path(__file__).resolve().parent / "launchd" / "com.beyondans.codex-resume-watch.plist.template"
WINDOWS_TASK_NAME = "CodexResumeWatch"
DEFAULT_INTERVAL_MINUTES = 10

DEFAULT_PROMPT = (
    "剛才的工作因為 Codex 額度用完中斷了，額度已經恢復，"
    "請接續未完成的部分繼續做，不要重做已經完成的步驟。"
)
LIMIT_THRESHOLD = 99.0  # primary.used_percent 達到這個門檻，視為「很可能卡在額度」
RESUME_BUFFER_SECONDS = 90  # resets_at 之後再等一下，避免伺服器端額度還沒真正刷新
RESUME_TIMEOUT_SECONDS = 4 * 60 * 60  # 續跑工作本身可能很長，只防真的卡死
MAX_STALE_SECONDS = 6 * 60 * 60  # resets_at 已過去超過這麼久，視為老查已經不在等這個工作，不接續


def now():
    return dt.datetime.now(TZ)


def fmt_ts(epoch_seconds):
    if epoch_seconds is None:
        return "未知"
    return dt.datetime.fromtimestamp(epoch_seconds, TZ).strftime("%Y-%m-%d %H:%M:%S (Asia/Taipei)")


def log(msg):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{now().isoformat()}] {msg}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def norm_path(path_str):
    try:
        return str(Path(path_str)).replace("/", "\\").lower()
    except Exception:
        return str(path_str).lower()


def read_first_json(path):
    with path.open("r", encoding="utf-8") as f:
        first = f.readline()
    return json.loads(first) if first.strip() else None


def find_latest_session_for_cwd(cwd):
    """回傳 cwd 底下最新一個 rollout 檔的 Path；找不到回傳 None。只讀每個檔案的第一行（session_meta）。"""
    if not SESSIONS_DIR.exists():
        return None
    target = norm_path(cwd)
    candidates = sorted(
        SESSIONS_DIR.rglob("rollout-*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for p in candidates:
        try:
            meta = read_first_json(p)
        except Exception:
            continue
        if not meta or meta.get("type") != "session_meta":
            continue
        session_cwd = meta.get("payload", {}).get("cwd")
        if session_cwd and norm_path(session_cwd) == target:
            return p
    return None


def get_latest_rate_limits(path):
    """回傳檔案內最後一筆 token_count 事件的 rate_limits dict；沒有回傳 None。"""
    last = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") == "event_msg" and obj.get("payload", {}).get("type") == "token_count":
                rl = obj["payload"].get("rate_limits")
                if rl:
                    last = rl
    return last


def describe_rate_limits(rl):
    primary = (rl or {}).get("primary") or {}
    secondary = (rl or {}).get("secondary") or {}
    reached = (rl or {}).get("rate_limit_reached_type")
    return (
        f"primary: used_percent={primary.get('used_percent')} "
        f"window_minutes={primary.get('window_minutes')} resets_at={fmt_ts(primary.get('resets_at'))} | "
        f"secondary: used_percent={secondary.get('used_percent')} resets_at={fmt_ts(secondary.get('resets_at'))} | "
        f"rate_limit_reached_type={reached}"
    )


def cmd_check(args):
    cwd = args.cwd or str(REPO)
    session_path = find_latest_session_for_cwd(cwd)
    if not session_path:
        print(f"check: 找不到 cwd={cwd} 的 session 檔案")
        return
    rl = get_latest_rate_limits(session_path)
    print(f"check: 最新 session 檔 = {session_path}")
    if not rl:
        print("check: 這個 session 檔沒有 rate_limits 紀錄")
        return
    print("check: " + describe_rate_limits(rl))


def cmd_watch(args):
    cwd = args.cwd or str(REPO)
    session_path = find_latest_session_for_cwd(cwd)
    if not session_path:
        log(f"watch: 找不到 cwd={cwd} 的 session 檔案，不處理")
        return

    rl = get_latest_rate_limits(session_path)
    if not rl:
        log(f"watch: {session_path.name} 沒有 rate_limits 紀錄，不處理")
        return

    primary = rl.get("primary") or {}
    used = primary.get("used_percent")
    resets_at = primary.get("resets_at")
    reached_type = rl.get("rate_limit_reached_type")

    likely_limited = (reached_type is not None) or (
        used is not None and used >= args.threshold
    )

    if not likely_limited:
        log(
            f"watch: {session_path.name} used_percent={used} 未達門檻（{args.threshold}），"
            f"rate_limit_reached_type={reached_type}，視為沒卡住，不處理"
        )
        return

    if resets_at is None:
        log(f"watch: {session_path.name} 判斷為卡住但沒有 resets_at，無法排程，請人工處理")
        return

    state = load_state()
    if state.get("last_resumed_resets_at") == resets_at:
        log(f"watch: resets_at={fmt_ts(resets_at)} 已經處理過一次，不重複接續")
        return

    now_ts = now().timestamp()
    if now_ts < resets_at + RESUME_BUFFER_SECONDS:
        remain = int(resets_at + RESUME_BUFFER_SECONDS - now_ts)
        log(
            f"watch: 判斷卡在額度，但還沒到恢復時間，還要等 {remain} 秒"
            f"（resets_at={fmt_ts(resets_at)}）"
        )
        return

    if now_ts > resets_at + MAX_STALE_SECONDS:
        log(
            f"watch: resets_at={fmt_ts(resets_at)} 已過去超過 {MAX_STALE_SECONDS // 3600} 小時，"
            f"視為舊紀錄，不接續"
        )
        return

    prompt = args.prompt or DEFAULT_PROMPT
    # 指定卡住的那個 session id，不用 --last，避免接到之後另開的其他工作
    session_id = (read_first_json(session_path) or {}).get("payload", {}).get("id")
    target = [session_id] if session_id else ["--last"]

    if args.dry_run:
        log(
            f"watch: [dry-run] 會對 cwd={cwd} 執行「codex exec resume {target[0]} <prompt>」，"
            f"prompt={prompt!r}，本次不會真的呼叫，也不會更新 state"
        )
        return

    # 先寫 state 再呼叫：續跑可能跑好幾小時，期間排程再觸發也不會重複接續同一個 resets_at
    state["last_resumed_resets_at"] = resets_at
    state["last_resumed_at"] = now().isoformat()
    state["last_resumed_session"] = session_id
    save_state(state)

    log(f"watch: 額度已恢復（resets_at={fmt_ts(resets_at)}），開始接續 session={target[0]} cwd={cwd}")
    try:
        result = subprocess.run(
            ["codex", "exec", "resume", *target, prompt],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=RESUME_TIMEOUT_SECONDS,
        )
        log(f"watch: codex exec resume 結束，exit_code={result.returncode}")
        if result.stdout:
            log("watch stdout（截斷前 2000 字）: " + result.stdout[:2000])
        if result.stderr:
            log("watch stderr（截斷前 2000 字）: " + result.stderr[:2000])
    except Exception as e:
        log(f"watch: 呼叫 codex exec resume 失敗：{e}（此 resets_at 已標記處理過，不自動重試，請人工確認）")


def install(interval_minutes):
    if sys.platform == "darwin":
        _install_launchd(interval_minutes)
    elif sys.platform == "win32":
        _install_schtasks(interval_minutes)
    else:
        print(f"install: 不支援的平台 {sys.platform}，請手動設定排程定期呼叫 `watch` 指令")


def _install_launchd(interval_minutes):
    target = Path.home() / "Library" / "LaunchAgents" / (LAUNCHD_LABEL + ".plist")
    plist = LAUNCHD_TEMPLATE.read_text(encoding="utf-8")
    python_bin = shutil.which("python3") or "/usr/bin/python3"
    plist = plist.replace("{{PYTHON}}", python_bin)
    plist = plist.replace("{{SCRIPT}}", str(Path(__file__).resolve()))
    plist = plist.replace("{{INTERVAL_SECONDS}}", str(interval_minutes * 60))
    plist = plist.replace("{{LOG}}", str(STATE_DIR / "launchd.log"))
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    uid = str(os.getuid())
    subprocess.run(["launchctl", "bootout", f"gui/{uid}/{LAUNCHD_LABEL}"], capture_output=True)
    target.write_text(plist, encoding="utf-8")
    p = subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(target)], capture_output=True, text=True)
    status = "OK" if p.returncode == 0 else p.stderr.strip()
    print(f"install: 已安裝 launchd：{target}（{status}），每 {interval_minutes} 分鐘檢查一次")


def _install_schtasks(interval_minutes):
    # pythonw 不開主控台視窗，避免每 10 分鐘閃一個黑視窗
    python_bin = shutil.which("pythonw") or shutil.which("python") or shutil.which("python3") or "python"
    script = str(Path(__file__).resolve())
    cmd = f'"{python_bin}" "{script}" watch'
    result = subprocess.run(
        [
            "schtasks", "/Create", "/TN", WINDOWS_TASK_NAME, "/TR", cmd,
            "/SC", "MINUTE", "/MO", str(interval_minutes), "/F",
        ],
        capture_output=True,
        text=True,
    )
    output = (result.stdout or result.stderr).strip()
    if result.returncode == 0:
        print(f"install: 已安裝工作排程器工作「{WINDOWS_TASK_NAME}」，每 {interval_minutes} 分鐘檢查一次")
    else:
        print(f"install: 安裝失敗，請確認是否有權限建立排程工作：{output}")


def uninstall():
    if sys.platform == "darwin":
        target = Path.home() / "Library" / "LaunchAgents" / (LAUNCHD_LABEL + ".plist")
        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{LAUNCHD_LABEL}"], capture_output=True)
        if target.exists():
            target.unlink()
        print("uninstall: 已移除 launchd 排程")
    elif sys.platform == "win32":
        result = subprocess.run(
            ["schtasks", "/Delete", "/TN", WINDOWS_TASK_NAME, "/F"], capture_output=True, text=True
        )
        print("uninstall: " + (result.stdout or result.stderr).strip())
    else:
        print(f"uninstall: 不支援的平台 {sys.platform}")


def main():
    # Windows 終端機預設不是 UTF-8，不重設就會把中文訊息印成亂碼
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass

    parser = argparse.ArgumentParser(description="Codex 額度自動續跑 watchdog")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="只印出目前判斷到的額度狀態，不做任何動作")
    p_check.add_argument("--cwd", default=None, help="要檢查哪個專案目錄的 session，預設這個 repo")

    p_watch = sub.add_parser("watch", help="判斷是否該續跑，額度恢復時呼叫一次 codex exec resume --last")
    p_watch.add_argument("--cwd", default=None, help="要接續哪個專案目錄的 session，預設這個 repo")
    p_watch.add_argument("--prompt", default=None, help="接續時要送出的提示詞，預設用標準續跑提示")
    p_watch.add_argument("--threshold", type=float, default=LIMIT_THRESHOLD, help="used_percent 判斷門檻")
    p_watch.add_argument(
        "--dry-run", action="store_true", help="只印出會做什麼，不實際呼叫 codex exec resume"
    )

    p_install = sub.add_parser(
        "install", help="安裝排程（Mac 用 launchd、Windows 用工作排程器），定期呼叫 watch"
    )
    p_install.add_argument(
        "--interval-minutes", type=int, default=DEFAULT_INTERVAL_MINUTES, help="每隔幾分鐘檢查一次"
    )

    sub.add_parser("uninstall", help="移除排程")

    args = parser.parse_args()
    if args.command == "check":
        cmd_check(args)
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "install":
        install(args.interval_minutes)
    elif args.command == "uninstall":
        uninstall()


if __name__ == "__main__":
    main()
