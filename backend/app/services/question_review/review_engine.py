"""M30 Question Review Engine — chief editor orchestrator (no generation)."""

from __future__ import annotations

import hashlib
from typing import Any

from app.services.question_review.ambiguity_detector import detect_ambiguity
from app.services.question_review.answer_verifier import verify_answer
from app.services.question_review.cognitive_load import measure_cognitive_load
from app.services.question_review.distractor_balance import analyze_distractor_balance
from app.services.question_review.exam_feeling_editor import score_exam_feeling
from app.services.question_review.fairness_checker import check_fairness
from app.services.question_review.language_editor import edit_language
from app.services.question_review.review_report import format_review_comments
from app.services.question_review.review_score import build_review_breakdown, passes_review
from app.services.question_review.types import ReviewResult


def _as_question_dict(question: Any) -> dict[str, Any]:
    if isinstance(question, dict):
        return {
            "stem": str(question.get("stem") or ""),
            "choices": dict(question.get("choices") or {}),
            "correct_key": str(question.get("correct_key") or "A").upper(),
            "explanation": question.get("explanation"),
        }
    # AuthoredQuestion-like
    return {
        "stem": str(getattr(question, "stem", "") or ""),
        "choices": dict(getattr(question, "choices", {}) or {}),
        "correct_key": str(getattr(question, "correct_key", "A") or "A").upper(),
        "explanation": getattr(question, "explanation", None),
    }


def _uniqueness_score(question: dict[str, Any], recent_stems: list[str] | None) -> int:
    stem = str(question.get("stem") or "").strip().lower()
    if not stem:
        return 40
    if not recent_stems:
        return 92
    h = hashlib.sha1(stem[:160].encode("utf-8")).hexdigest()
    for prev in recent_stems[-200:]:
        ph = hashlib.sha1(str(prev).strip().lower()[:160].encode("utf-8")).hexdigest()
        if h == ph:
            return 35
        # opening overlap
        a = stem.split()[:8]
        b = str(prev).lower().split()[:8]
        if a and a == b:
            return 50
    return 90


class QuestionReviewEngine:
    """Chief editor: inspect only — never writes stems/choices."""

    def review(
        self,
        question: Any,
        *,
        recent_stems: list[str] | None = None,
        recent_correct_keys: list[str] | None = None,
        rewrite_used: int = 0,
    ) -> ReviewResult:
        q = _as_question_dict(question)
        ambiguity = detect_ambiguity(q)
        distractors = analyze_distractor_balance(q)
        language = edit_language(q)
        feeling = score_exam_feeling(q)
        load = measure_cognitive_load(q)
        validity = verify_answer(q)
        fairness = check_fairness(q, recent_correct_keys=recent_correct_keys)
        uniq = _uniqueness_score(q, recent_stems)

        breakdown = build_review_breakdown(
            clarity=ambiguity,
            fairness=fairness,
            language=language,
            exam_feeling=feeling,
            distractors=distractors,
            cognitive_load=load,
            answer_validity=validity,
            uniqueness=uniq,
        )
        comments = format_review_comments(
            ambiguity, distractors, language, feeling, load, validity, fairness
        )
        return ReviewResult(
            passed=passes_review(breakdown),
            breakdown=breakdown,
            comments=comments,
            rewrite_used=rewrite_used,
        )
