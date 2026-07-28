"""CLI: M27.5 Exam Style Learning over data/ M27 outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure backend root on path when run as script
_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from app.services.exam_intelligence.style_learning import (  # noqa: E402
    StyleLearningEngine,
    StyleRepository,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="StudyOS M27.5 Style Learning")
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="Path to data/ (default: repo/data)",
    )
    args = parser.parse_args()
    data_root = args.data_root or (_BACKEND.parent / "data")
    engine = StyleLearningEngine(data_root)
    summary = engine.learn_all()
    print(json.dumps({k: summary[k] for k in summary if k != "validation_issues"}, ensure_ascii=False, indent=2))
    if summary.get("validation_failures"):
        print(f"Validation failures: {summary['validation_failures']}")
    repo = StyleRepository(data_root)
    sample = repo.get_topic_style("kpss", "turkce", "paragraf")
    if sample:
        print("Sample KPSS Türkçe Paragraf intents:", (sample.get("intent") or {}).get("intents"))
        print("Cluster:", sample.get("cluster"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
