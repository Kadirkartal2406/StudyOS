"""CLI: M27.6 Style Validation & Benchmark."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.services.exam_intelligence.style_validation import (  # noqa: E402
    BenchmarkRunner,
    ValidationRepository,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="StudyOS M27.6 Style Validation")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Path to data/ (default: repo/data)",
    )
    args = parser.parse_args()
    data_root = args.data_root or (_BACKEND.parent / "data")

    result = BenchmarkRunner(data_root).run()
    summary = result["summary"]
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"M28 ready: {result.get('m28_ready')}")
    print(f"Report: {summary.get('artifacts', {}).get('validation_md')}")

    repo = ValidationRepository(data_root)
    print(f"Warnings loaded via repository: {len(repo.get_warnings())}")
    return 0 if result.get("m28_ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
