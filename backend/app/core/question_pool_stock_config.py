"""M33 — minimum/target stok hedefleri.

Hedefler bir JSON dosyasından okunur (kod motorları değiştirmez).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QuestionPoolStockTarget:
    exam: str
    difficulty_band: str
    minimum: int
    target: int

    subject_code: str | None = None
    topic_code: str | None = None

    subject_name: str | None = None
    topic_name: str | None = None


def _normalize_exam(s: str) -> str:
    return (s or "").strip().lower()


def load_question_pool_stock_targets() -> list[QuestionPoolStockTarget]:
    root = Path(__file__).resolve().parent
    path = root / "question_pool_stock_targets.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: list[QuestionPoolStockTarget] = []
    for i, e in enumerate(raw):
        subject_code = e.get("subject_code")
        topic_code = e.get("topic_code")
        subject_name = e.get("subject_name")
        topic_name = e.get("topic_name")

        out.append(
            QuestionPoolStockTarget(
                exam=_normalize_exam(e.get("exam")),
                subject_code=subject_code,
                topic_code=topic_code,
                subject_name=subject_name,
                topic_name=topic_name,
                difficulty_band=str(e.get("difficulty_band") or "medium"),
                minimum=int(e.get("minimum") or 0),
                target=int(e.get("target") or 0),
            )
        )
    return out

