"""Read validation artifacts from data/style_validation/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ValidationRepository:
    def __init__(self, data_root: Path | str) -> None:
        self.data_root = Path(data_root)
        self.root = self.data_root / "style_validation"

    def _read(self, name: str) -> dict[str, Any] | list[Any] | None:
        path = self.root / name
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def get_validation(self) -> dict[str, Any] | None:
        data = self._read("summary.json")
        return data if isinstance(data, dict) else None

    def get_exam_validation(self, exam_code: str) -> dict[str, Any] | None:
        summary = self.get_validation() or {}
        by_exam = ((summary.get("quality_scores") or {}).get("by_exam")) or {}
        return by_exam.get(exam_code.lower())

    def get_quality_score(self, topic_code: str | None = None) -> Any:
        scores = self._read("quality_scores.json")
        if not isinstance(scores, dict):
            return None
        if topic_code is None:
            return scores
        for row in scores.get("contracts") or []:
            if row.get("topic_code") == topic_code:
                return row
        return None

    def get_warnings(self) -> list[Any]:
        data = self._read("warnings.json")
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return list(data.get("warnings") or [])
        return []

    def get_similarity_report(self) -> dict[str, Any] | None:
        data = self._read("similarity_report.json")
        return data if isinstance(data, dict) else None
