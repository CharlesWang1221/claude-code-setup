#!/usr/bin/env python3
"""Small, credit-aware wrapper around a local gflow-cli installation."""

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MODELS = {"omni-flash", "veo-lite", "veo-fast", "veo-quality"}
MODEL_ESTIMATES = {"veo-lite": 10, "veo-fast": 20, "veo-quality": 100}


def fail(message):
    raise SystemExit(message)


def which_gflow():
    configured = os.environ.get("GFLOW_BIN")
    repo_root = Path(__file__).resolve().parents[3]
    local = repo_root / ".flow-tools" / "gflow-venv" / ("Scripts/gflow.exe" if os.name == "nt" else "bin/gflow")
    result = configured or (str(local) if local.is_file() else None) or shutil.which("gflow")
    if not result or not Path(result).is_file():
        fail("找不到 gflow。先讀 Skill 的 references/connection.md 完成隔離安裝。")
    return str(Path(result).resolve())


def run_checked(command, timeout=60):
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)


def now_taipei():
    zone = dt.timezone(dt.timedelta(hours=8))
    return dt.datetime.now(zone).isoformat(timespec="seconds")


def require_file(value, label):
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        fail("{} 不存在：{}".format(label, path))
    return path


def require_start_frame(value):
    path = require_file(value, "起始畫面")
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        fail("起始畫面必須是 PNG、JPEG 或 WebP 圖檔")
    info = probe(path)
    streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not streams:
        fail("起始畫面不是可讀取的圖檔")
    width, height = streams[0].get("width"), streams[0].get("height")
    if not width or not height or abs(width / height - 9 / 16) > 0.02:
        fail("起始畫面應為 9:16 直式構圖，實際 {} × {}".format(width, height))
    return path


def probe(path):
    result = run_checked([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
        "-of", "json", str(path),
    ])
    if result.returncode:
        fail("ffprobe 無法讀取：{}".format(path))
    return json.loads(result.stdout)


def duration_of(info):
    try:
        return float(info["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        fail("找不到媒體長度")


def doctor(_args):
    required = ["ffmpeg", "ffprobe"]
    for command in required:
        if not shutil.which(command):
            fail("找不到 {}".format(command))
    gflow = which_gflow()
    version = run_checked([gflow, "--version"])
    auth = run_checked([gflow, "auth", "status"], timeout=45)
    print(json.dumps({
        "gflow": gflow,
        "version": version.stdout.strip() if version.returncode == 0 else "unknown",
        "chrome": Path("/Applications/Google Chrome.app").exists() if sys.platform == "darwin" else bool(shutil.which("chrome") or shutil.which("chromium")),
        "ffmpeg": True,
        "flow_login_status": "verified" if auth.returncode == 0 else "unverified",
    }, ensure_ascii=False, indent=2))
    if auth.returncode:
        print("無法驗證 Flow 登入；可能是未登入或本機權限／網路受限。請在正常本機環境執行 gflow auth status。")


def plan_data(args):
    start = require_start_frame(args.start_frame)
    prompt = require_file(args.prompt_file, "動作提示詞")
    if not prompt.read_text(encoding="utf-8").strip():
        fail("動作提示詞是空的")
    out = Path(args.out).expanduser().resolve()
    if out.suffix.lower() != ".mp4":
        fail("輸出路徑必須是 .mp4")
    if args.model not in MODELS:
        fail("不支援模型：{}".format(args.model))
    if args.duration == 10 and args.model != "omni-flash":
        fail("10 秒只適用 omni-flash")
    record = out.with_suffix(".flow-run.json")
    return {
        "start_frame": str(start),
        "prompt_file": str(prompt),
        "out": str(out),
        "record": str(record),
        "model": args.model,
        "duration": args.duration,
        "count": 1,
        "estimated_credits": MODEL_ESTIMATES.get(args.model, "請以 Flow 頁面當下價格為準"),
        "credit_note": "官方點數可能調整，生成前以 Flow 頁面為準；一次只送 1 支。",
    }


def plan(args):
    print(json.dumps(plan_data(args), ensure_ascii=False, indent=2))


def generate(args):
    data = plan_data(args)
    if not args.spend:
        fail("本命令可能消耗 Google Flow 點數。確認當次已授權後，才加 --spend。")
    output = Path(data["out"])
    record = Path(data["record"])
    if output.exists() or record.exists():
        fail("輸出或提交紀錄已存在；先檢查 Flow 專案及本機檔案，不要重送。")
    gflow = which_gflow()
    auth = run_checked([gflow, "auth", "status"], timeout=45)
    if auth.returncode:
        fail("Flow 登入未通過。請老查在本機完成 gflow auth login --browser chrome。")
    output.parent.mkdir(parents=True, exist_ok=True)
    record_data = {**data, "status": "pending", "created_at": now_taipei()}
    try:
        with record.open("x", encoding="utf-8") as handle:
            json.dump(record_data, handle, ensure_ascii=False, indent=2)
    except FileExistsError:
        fail("提交紀錄剛被建立；已取消，避免重複扣點。")
    prompt = Path(data["prompt_file"]).read_text(encoding="utf-8").strip()
    try:
        with tempfile.TemporaryDirectory(prefix="flow-upload-") as temp_dir:
            clean_frame = Path(temp_dir) / "start.png"
            clean = run_checked([
                "ffmpeg", "-v", "error", "-y", "-i", data["start_frame"],
                "-map_metadata", "-1", "-frames:v", "1", str(clean_frame),
            ], timeout=120)
            if clean.returncode or not clean_frame.is_file():
                fail("起始圖去除中繼資料失敗；未提交 Flow。")
            command = [gflow, "video", "i2v", "--initial-frame", str(clean_frame),
                       prompt, "--aspect", "9:16", "--model", data["model"],
                       "--duration", str(data["duration"]), "--count", "1",
                       "--output", data["out"], "--json"]
            if args.project:
                command.extend(["--project", args.project])
            result = run_checked(command, timeout=1800)
        if result.returncode or not output.is_file() or output.stat().st_size == 0:
            record_data["status"] = "needs_review"
            record_data["error"] = "gflow_exit_{}; check original Flow project before retry".format(result.returncode)
            fail("生成未能確認完成。先到 Flow 專案找原任務，勿直接重送。")
        record_data["status"] = "downloaded"
        record_data["completed_at"] = now_taipei()
        print("已下載：{}".format(output))
        try:
            verify_video(output)
        except SystemExit:
            record_data["status"] = "needs_review"
            record_data["error"] = "downloaded file failed verification"
            raise
    except subprocess.TimeoutExpired:
        record_data["status"] = "needs_review"
        record_data["error"] = "timeout; check original Flow project before retry"
        fail("等待逾時。先到 Flow 專案找原任務，勿直接重送。")
    finally:
        record.write_text(json.dumps(record_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_video(video):
    info = probe(video)
    video_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not video_streams:
        fail("檔案沒有影片軌：{}".format(video))
    stream = video_streams[0]
    duration = duration_of(info)
    decode = run_checked(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"], timeout=600)
    if decode.returncode:
        fail("影片完整解碼失敗：{}".format(video))
    contact = video.with_name(video.stem + "-contact.jpg")
    frame_rate = max(0.25, 4.0 / duration)
    contact_result = run_checked([
        "ffmpeg", "-v", "error", "-i", str(video),
        "-vf", "fps={:.5f},scale=270:480,tile=4x1".format(frame_rate),
        "-frames:v", "1", "-y", str(contact),
    ], timeout=120)
    qc = {
        "video": str(video), "duration": duration,
        "width": stream.get("width"), "height": stream.get("height"),
        "codec": stream.get("codec_name"), "decode_ok": True,
        "contact_sheet": str(contact) if contact_result.returncode == 0 and contact.is_file() else None,
        "visual_review": "pending: inspect character identity, feet, shadows, background, and continuity",
        "checked_at": now_taipei(),
    }
    qc_path = video.with_name(video.stem + "-qc.json")
    qc_path.write_text(json.dumps(qc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qc, ensure_ascii=False, indent=2))
    return qc


def verify(args):
    verify_video(require_file(args.video, "影片"))


def assemble(args):
    clips = [require_file(value, "片段") for value in args.clips]
    audio = require_file(args.audio, "核准音檔")
    out = Path(args.out).expanduser().resolve()
    if out.exists():
        fail("輸出已存在，不覆蓋：{}".format(out))
    if out.suffix.lower() != ".mp4":
        fail("輸出路徑必須是 .mp4")
    audio_info = probe(audio)
    if not any(s.get("codec_type") == "audio" for s in audio_info.get("streams", [])):
        fail("核准音檔沒有音軌")
    target = duration_of(audio_info)
    total = sum(duration_of(probe(clip)) for clip in clips)
    if total + 0.05 < target:
        fail("影片片段總長 {:.2f} 秒，短於音檔 {:.2f} 秒。".format(total, target))
    out.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-v", "error", "-n"]
    for clip in clips:
        command.extend(["-i", str(clip)])
    command.extend(["-i", str(audio)])
    parts = []
    for index in range(len(clips)):
        parts.append("[{}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{}]".format(index, index))
    parts.append("{}concat=n={}:v=1:a=0[outv]".format("".join("[v{}]".format(i) for i in range(len(clips))), len(clips)))
    command.extend(["-filter_complex", ";".join(parts), "-map", "[outv]",
                    "-map", "{}:a:0".format(len(clips)), "-t", "{:.3f}".format(target),
                    "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    result = run_checked(command, timeout=1800)
    if result.returncode:
        fail("FFmpeg 合成失敗：{}".format(result.stderr[-800:]))
    verify_video(out)


def main():
    parser = argparse.ArgumentParser(description="Google Flow 短片生成與驗收")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor").set_defaults(func=doctor)
    for name, handler in (("plan", plan), ("generate", generate)):
        part = commands.add_parser(name)
        part.add_argument("--start-frame", required=True)
        part.add_argument("--prompt-file", required=True)
        part.add_argument("--out", required=True)
        part.add_argument("--model", choices=sorted(MODELS), default="veo-lite")
        part.add_argument("--duration", type=int, choices=[4, 6, 8, 10], default=4)
        if name == "generate":
            part.add_argument("--project", help="既有 Flow project ID")
            part.add_argument("--spend", action="store_true", help="允許提交 1 支可能扣點的生成")
        part.set_defaults(func=handler)
    part = commands.add_parser("verify")
    part.add_argument("--video", required=True)
    part.set_defaults(func=verify)
    part = commands.add_parser("assemble")
    part.add_argument("--clips", nargs="+", required=True)
    part.add_argument("--audio", required=True)
    part.add_argument("--out", required=True)
    part.set_defaults(func=assemble)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
