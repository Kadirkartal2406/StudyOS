"""Read Style Contracts and exam profiles from data/ (telif-safe)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.exam_intelligence.style_learning.style_similarity import (
    style_similarity,
)


class StyleRepository:
    """Filesystem repository over exam_style_contracts / profiles."""

    def __init__(self, data_root: Path | str) -> None:
        self.data_root = Path(data_root)
        self.contracts_root = self.data_root / "exam_style_contracts"
        self.profiles_root = self.data_root / "exam_style_profiles_learned"

    def _read_json(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list_contracts(self) -> list[Path]:
        if not self.contracts_root.exists():
            return []
        return sorted(self.contracts_root.rglob("style_contract.json"))

    def get_topic_style(
        self,
        exam_code: str,
        subject_slug: str,
        topic_slug: str,
    ) -> dict[str, Any] | None:
        path = (
            self.contracts_root
            / exam_code.lower()
            / subject_slug.lower()
            / topic_slug.lower()
            / "style_contract.json"
        )
        return self._read_json(path)

    def get_style(self, topic_code: str) -> dict[str, Any] | None:
        """Resolve topic_code like kpss_turkce__paragraf."""
        topic_code = (topic_code or "").strip()
        if "__" not in topic_code:
            return None
        left, topic_slug = topic_code.split("__", 1)
        exam = left.split("_", 1)[0] if "_" in left else left
        subject_slug = left.split("_", 1)[-1] if "_" in left else left
        return self.get_topic_style(exam, subject_slug, topic_slug)

    def get_exam_style(self, exam_code: str) -> dict[str, Any] | None:
        path = self.profiles_root / f"{exam_code.upper()}.json"
        alt = self.profiles_root / f"{exam_code.lower()}.json"
        return self._read_json(path) or self._read_json(alt)

    def get_reasoning(self, topic_code: str) -> dict[str, Any] | None:
        c = self.get_style(topic_code)
        return None if c is None else dict(c.get("reasoning") or {})

    def get_trap_pattern(self, topic_code: str) -> dict[str, Any] | None:
        c = self.get_style(topic_code)
        return None if c is None else dict(c.get("trap") or {})

    def get_bloom(self, topic_code: str) -> dict[str, float] | None:
        c = self.get_style(topic_code)
        if c is None:
            return None
        bloom = c.get("bloom") or {}
        return {str(k): float(v) for k, v in bloom.items()}

    def get_difficulty_curve(self, topic_code: str) -> list[dict[str, Any]] | None:
        c = self.get_style(topic_code)
        return None if c is None else list(c.get("difficulty_curve") or [])

    def get_reading_profile(self, topic_code: str) -> dict[str, Any] | None:
        c = self.get_style(topic_code)
        return None if c is None else dict(c.get("reading_load") or {})

    def similarity(self, topic_a: str, topic_b: str) -> float | None:
        a = self.get_style(topic_a)
        b = self.get_style(topic_b)
        if not a or not b:
            return None
        return style_similarity(a, b)
