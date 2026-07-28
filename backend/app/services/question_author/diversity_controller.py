"""M29.8 Diversity Controller — compare against recent authored stems."""

from __future__ import annotations

import hashlib
import re
from collections import deque
from typing import Any


def _norm(text: str) -> str:
    t = (text or "").lower()
    t = re.sub(r"[^\w\s]", " ", t, flags=re.UNICODE)
    return re.sub(r"\s+", " ", t).strip()


def _opening(stem: str, n: int = 8) -> str:
    words = _norm(stem).split()
    return " ".join(words[:n])


def structure_signature(stem: str, *, stem_type: str, outcome: str) -> str:
    opening = _opening(stem)
    return hashlib.sha1(f"{opening}|{stem_type}|{outcome}".encode("utf-8")).hexdigest()[:16]


class DiversityController:
    """In-memory ring of last N signatures (caller may persist externally)."""

    def __init__(self, capacity: int = 500) -> None:
        self.capacity = capacity
        self._recent: deque[str] = deque(maxlen=capacity)
        self._openings: deque[str] = deque(maxlen=capacity)
        self._types: deque[str] = deque(maxlen=capacity)
        self._outcomes: deque[str] = deque(maxlen=capacity)

    def remember_many(self, items: list[dict[str, Any]]) -> None:
        for it in items:
            self.remember(
                stem=str(it.get("stem") or ""),
                stem_type=str(it.get("stem_type") or ""),
                outcome=str(it.get("outcome") or ""),
            )

    def remember(self, *, stem: str, stem_type: str = "", outcome: str = "") -> None:
        sig = structure_signature(stem, stem_type=stem_type, outcome=outcome)
        self._recent.append(sig)
        self._openings.append(_opening(stem))
        if stem_type:
            self._types.append(stem_type)
        if outcome:
            self._outcomes.append(outcome)

    def is_too_similar(
        self,
        *,
        stem: str,
        stem_type: str = "",
        outcome: str = "",
    ) -> bool:
        sig = structure_signature(stem, stem_type=stem_type, outcome=outcome)
        if sig in self._recent:
            return True
        op = _opening(stem)
        if not op:
            return False
        for prev in self._openings:
            if not prev:
                continue
            if op == prev or op.startswith(prev) or prev.startswith(op):
                return True
        return False

    def accept(
        self,
        *,
        stem: str,
        stem_type: str = "",
        outcome: str = "",
    ) -> bool:
        """Return True if accepted into buffer; False if rejected as duplicate."""
        if self.is_too_similar(stem=stem, stem_type=stem_type, outcome=outcome):
            return False
        self.remember(stem=stem, stem_type=stem_type, outcome=outcome)
        return True
