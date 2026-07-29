"""P6 — Question Scorecard: complete internal score for each question."""
from __future__ import annotations
from typing import Any
from app.services.question_intelligence.types import QuestionScorecard
from app.services.question_intelligence.blueprint_matcher import match_blueprint
from app.services.question_intelligence.exam_feel_v2 import detect_exam_feel_v2
from app.services.question_intelligence.option_balance import analyze_option_balance
from app.services.question_intelligence.distractor_quality_v2 import analyze_distractor_quality_v2
from app.services.question_intelligence.multi_stage_review import (
    _stage_language,
    _stage_fairness,
    _stage_human_examiner,
)


def build_scorecard(
    question: dict[str, Any],
    plan: dict[str, Any] | None = None,
    style_dna: dict[str, Any] | None = None,
    *,
    author_scores: dict[str, Any] | None = None,
    review_scores: dict[str, Any] | None = None,
    vsse_scores: dict[str, Any] | None = None,
) -> QuestionScorecard:
    """Build complete scorecard from all available signals."""
    plan = plan or {}
    author_scores = author_scores or {}
    review_scores = review_scores or {}
    vsse_scores = vsse_scores or {}
    
    # Blueprint
    bp = match_blueprint(question, plan, style_dna)
    
    # Exam feel V2
    ef = detect_exam_feel_v2(question)
    
    # Option balance
    ob = analyze_option_balance(question, question.get("correct_key"))
    
    # Distractor quality
    dq = analyze_distractor_quality_v2(question, question.get("correct_key"))
    
    # Language
    lang = _stage_language(question)
    
    # Fairness
    fair = _stage_fairness(question)
    
    # Use author/review scores where available, else estimate
    style = int(author_scores.get("style_score") or author_scores.get("style") or ob.score)
    difficulty = int(author_scores.get("difficulty_score") or author_scores.get("difficulty") or plan.get("difficulty") or 70)
    naturalness = int(author_scores.get("naturalness") or max(0, ef.score - 5))
    reasoning = int(author_scores.get("reasoning_score") or author_scores.get("reasoning") or bp.reasoning_type)
    virtual_student = int(vsse_scores.get("score") or vsse_scores.get("overall") or 80)
    
    return QuestionScorecard(
        style=style,
        difficulty=difficulty,
        exam_feel=ef.score,
        naturalness=naturalness,
        reasoning=reasoning,
        distractors=dq.score,
        blueprint=bp.score,
        language=lang,
        fairness=fair,
        virtual_student=virtual_student,
    )
