"""M31 VSSE orchestrator — simulate students; never generate questions."""

from __future__ import annotations

from typing import Any

from app.services.question_virtual_student.cognitive_load import analyze_cognitive_load
from app.services.question_virtual_student.confusion_detector import analyze_confusion
from app.services.question_virtual_student.difficulty_reality import difficulty_reality_check
from app.services.question_virtual_student.distractor_attraction import (
    rank_distractor_attraction,
)
from app.services.question_virtual_student.fairness_bias import check_fairness_bias
from app.services.question_virtual_student.profiles import all_profiles
from app.services.question_virtual_student.reading_analytics import reading_analytics
from app.services.question_virtual_student.reject_policy import evaluate_rejects
from app.services.question_virtual_student.student_simulator import simulate_all
from app.services.question_virtual_student.types import MIN_VSSE_SCORE, VSSEResult


def _as_question(question: Any) -> dict[str, Any]:
    if isinstance(question, dict):
        return {
            "stem": str(question.get("stem") or ""),
            "choices": {
                str(k).upper(): str(v) for k, v in (question.get("choices") or {}).items()
            },
            "correct_key": str(question.get("correct_key") or "A").upper(),
            "explanation": question.get("explanation"),
        }
    return {
        "stem": str(getattr(question, "stem", "") or ""),
        "choices": {
            str(k).upper(): str(v)
            for k, v in (getattr(question, "choices", {}) or {}).items()
        },
        "correct_key": str(getattr(question, "correct_key", "A") or "A").upper(),
        "explanation": getattr(question, "explanation", None),
    }


def _author_difficulty(question: Any) -> int | None:
    plan = getattr(question, "author_plan", None)
    if plan is not None and getattr(plan, "difficulty_target", None) is not None:
        return int(plan.difficulty_target)
    if isinstance(question, dict) and question.get("author_difficulty") is not None:
        return int(question["author_difficulty"])
    meta = getattr(question, "internal_metadata", None)
    if callable(meta):
        data = meta()
        plan = (data or {}).get("author_plan") or {}
        if plan.get("difficulty_target") is not None:
            return int(plan["difficulty_target"])
    return None


class VirtualStudentEngine:
    """Solve-as-student quality layer. Does not write stems/choices."""

    def simulate(
        self,
        question: Any,
        *,
        review_bounce_used: int = 0,
    ) -> VSSEResult:
        q = _as_question(question)
        profiles = all_profiles()
        attempts = simulate_all(q, profiles)
        confusion = analyze_confusion(
            attempts, correct_key=q["correct_key"], question=q
        )
        reading = reading_analytics(q, attempts)
        cognitive = analyze_cognitive_load(q)
        fairness = check_fairness_bias(q)
        attractions = rank_distractor_attraction(q)
        difficulty = difficulty_reality_check(
            attempts, author_difficulty=_author_difficulty(question)
        )
        rejects = evaluate_rejects(
            confusion=confusion,
            reading=reading,
            cognitive=cognitive,
            fairness=fairness,
            distractors=attractions,
            question=q,
            difficulty=difficulty,
        )

        # Score: start 100, subtract for rejects / confusion
        score = 100
        score -= 12 * len(rejects)
        score -= int(40 * float(confusion.get("confusion_score") or 0))
        if difficulty.get("warning"):
            score -= 8
        score = max(0, min(100, score))
        passed = score >= MIN_VSSE_SCORE and not rejects

        return VSSEResult(
            passed=passed,
            virtual_student_score=score,
            attempts=attempts,
            solve_distribution=dict(confusion.get("solve_distribution") or {}),
            confusion_score=float(confusion.get("confusion_score") or 0),
            ambiguity_probability=float(confusion.get("ambiguity_probability") or 0),
            reading_time_prediction=float(reading.get("reading_time_prediction") or 0),
            thinking_time_prediction=float(reading.get("thinking_time_prediction") or 0),
            distractor_attraction=attractions,
            cognitive_load=cognitive,
            fairness=fairness,
            difficulty_reality=difficulty,
            reject_reasons=rejects,
            review_bounce_used=review_bounce_used,
        )
