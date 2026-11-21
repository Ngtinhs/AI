"""
Đo thời gian từng bước của luồng YouTube -> Gemini (không qua giao diện, không dùng cache).

Cách chạy (ở thư mục gốc project, cần file .env có GEMINI_API_KEY):
    python scripts/benchmark_youtube.py <URL1> <URL2> ... --runs 3

Thử F7 (thinking budget) thì đặt biến môi trường trước khi chạy, ví dụ PowerShell:
    $env:GEMINI_THINKING_BUDGET = "0"; python scripts/benchmark_youtube.py <URL> --runs 3

Kết quả bài học của mỗi lần chạy được lưu trong benchmark_results/ để so sánh chất lượng.
"""

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.stdout.reconfigure(encoding="utf-8")  # để terminal Windows in được tiếng Việt

from config.settings import settings  # noqa: E402
from services.gemini_service import analyze_transcript  # noqa: E402
from services.youtube_service import get_transcript  # noqa: E402
from utils.timing import StageTimer  # noqa: E402
from utils.validators import extract_video_id  # noqa: E402

STAGES = ["URL Validation", "Transcript Retrieval", "Transcript Processing", "Gemini API", "Validation"]
OUTPUT_DIR = PROJECT_ROOT / "benchmark_results"


def run_once(url: str) -> tuple[StageTimer, dict | None, str | None]:
    """Chạy toàn bộ luồng một lần. Trả về (timer, bài học, lỗi)."""
    timer = StageTimer()
    try:
        with timer.measure("URL Validation"):
            video_id = extract_video_id(url)
        if not video_id:
            return timer, None, "URL không hợp lệ"

        transcript = get_transcript(video_id, timer=timer)
        analysis = analyze_transcript(transcript, timer=timer)
        return timer, analysis.model_dump(), None
    except Exception as exc:
        return timer, None, str(exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark luồng YouTube Learning")
    parser.add_argument("urls", nargs="+", help="Các URL YouTube cần đo")
    parser.add_argument("--runs", type=int, default=3, help="Số lần chạy mỗi URL")
    args = parser.parse_args()

    if not settings.gemini_api_key:
        sys.exit("Thiếu GEMINI_API_KEY trong file .env")

    OUTPUT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Model: {settings.gemini_model} | thinking_budget: {settings.gemini_thinking_budget} (None = mặc định)\n")

    for url in args.urls:
        print(f"=== {url}")
        stage_values = {stage: [] for stage in STAGES}
        totals = []
        saved_runs = []

        for run in range(1, args.runs + 1):
            timer, analysis, error = run_once(url)
            status = "OK" if error is None else f"LỖI: {error[:120]}"
            print(f"  Lần {run}: total={timer.total()}s {timer.info} -> {status}")

            for stage in STAGES:
                if stage in timer.stages:
                    stage_values[stage].append(timer.stages[stage])
            if error is None:
                totals.append(timer.total())
            saved_runs.append({"stages": timer.stages, "info": timer.info, "error": error, "analysis": analysis})

        print("\n| Stage | Median (s) | Min (s) | Max (s) |")
        print("|---|---|---|---|")
        for stage in STAGES + ["Total"]:
            values = totals if stage == "Total" else stage_values[stage]
            if values:
                print(f"| {stage} | {statistics.median(values):.3f} | {min(values):.3f} | {max(values):.3f} |")
            else:
                print(f"| {stage} | - | - | - |")
        print()

        video_id = extract_video_id(url) or "invalid"
        out_file = OUTPUT_DIR / f"{stamp}_{video_id}_tb{settings.gemini_thinking_budget}.json"
        out_file.write_text(json.dumps(saved_runs, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Đã lưu chi tiết: {out_file}\n")


if __name__ == "__main__":
    main()
