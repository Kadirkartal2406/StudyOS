#!/usr/bin/env python3
"""CLI: parse data/official_exams → metadata / style stats / Style DNA.

Usage (from backend/):
  python -m scripts.parse_official_exams
  python -m scripts.parse_official_exams --limit 3
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure backend root on path
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.exam_intelligence.parser.pipeline import ExamIntelligencePipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="M27 Official Exam Intelligence Parser")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=BACKEND_ROOT.parent / "data",
        help="StudyOS data/ directory",
    )
    parser.add_argument("--limit", type=int, default=None, help="Parse only first N PDFs")
    args = parser.parse_args()

    data_root = args.data_root.resolve()
    if not (data_root / "official_exams").exists():
        print(f"official_exams not found under {data_root}", file=sys.stderr)
        return 1

    pipe = ExamIntelligencePipeline(data_root)
    summary = pipe.run_all(limit=args.limit)
    out = data_root / "parsed_metadata" / "_reports" / "run_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nSummary: parsed={summary['parsed']} failed={summary['failed']}")
    print(f"Wrote {out}")
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
