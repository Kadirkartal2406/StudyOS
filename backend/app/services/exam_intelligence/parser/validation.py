"""Validate parse consistency — no AI."""

from __future__ import annotations

from typing import Any

from app.services.exam_intelligence.parser.types import ParseResult


def validate_result(result: ParseResult) -> dict[str, Any]:
    issues: list[str] = []
    ok: list[str] = []

    if result.page_count <= 0:
        issues.append("page_count_zero")
    else:
        ok.append("page_count")

    if result.question_count <= 0:
        issues.append("no_questions_located")
    else:
        ok.append("questions_located")

    ak = len(result.answer_key)
    if ak == 0:
        issues.append("answer_key_missing")
    else:
        ok.append("answer_key")
        if result.question_count and abs(ak - result.question_count) > max(
            5, result.question_count // 5
        ):
            issues.append(
                f"answer_key_mismatch_q={result.question_count}_key={ak}"
            )
        else:
            ok.append("answer_key_count_aligned")

    if not result.subject_distribution and not result.subject_order:
        issues.append("subjects_weak")
    else:
        ok.append("subjects")

    if not result.topic_distribution:
        issues.append("topics_weak")
    else:
        ok.append("topics")

    # Ensure no accidental text fields on QuestionMeta
    for q in result.questions:
        d = q.to_dict()
        for bad in ("stem", "choices", "explanation", "_transient_text"):
            if bad in d:
                issues.append(f"forbidden_field_{bad}")

    return {
        "ok": ok,
        "issues": issues,
        "passed": len(issues) == 0
        or (
            "no_questions_located" not in issues
            and "page_count_zero" not in issues
        ),
    }
