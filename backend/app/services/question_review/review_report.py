"""Internal review report metadata (not user-facing)."""

from __future__ import annotations

from typing import Any

from app.services.question_review.types import ReviewResult


def build_review_report(result: ReviewResult) -> dict[str, Any]:
    """Compact internal metadata blob."""
    return result.internal_metadata()


def format_review_comments(*flag_groups: dict[str, Any]) -> list[str]:
    comments: list[str] = []
    for g in flag_groups:
        for flag in g.get("flags") or []:
            comments.append(str(flag))
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for c in comments:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out
