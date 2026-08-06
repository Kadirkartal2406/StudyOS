"""M34 Pipeline — orchestrates all quality layers as a post-processing pass.

Does NOT modify existing QIE/Author/Review engines. Runs AFTER their output.
"""
from __future__ import annotations
import logging
from typing import Any

from app.services.question_intelligence.types import (
    MIN_BLUEPRINT_SCORE,
    MIN_SCORECARD_OVERALL,
    QuestionScorecard,
    BatchQualityReport,
)
from app.services.question_intelligence.blueprint_matcher import match_blueprint
from app.services.question_intelligence.exam_feel_v2 import detect_exam_feel_v2
from app.services.question_intelligence.option_balance import analyze_option_balance
from app.services.question_intelligence.distractor_quality_v2 import analyze_distractor_quality_v2
from app.services.question_intelligence.uniqueness_checker import check_uniqueness
from app.services.question_intelligence.multi_stage_review import run_multi_stage_review
from app.services.question_intelligence.scorecard import build_scorecard
from app.services.question_intelligence.auto_repair import auto_repair
from app.services.question_intelligence.batch_report import generate_batch_report
# EAE Sprint 4+1 — Node ID hallucination guard (P_EAE quality gate)
from app.services.question_intelligence.eae_node_verifier import EAENodeVerifier

logger = logging.getLogger("studyos.m34")


def evaluate_question(
    question: dict[str, Any],
    plan: dict[str, Any] | None = None,
    style_dna: dict[str, Any] | None = None,
    existing_stems: list[str] | None = None,
    *,
    author_scores: dict[str, Any] | None = None,
    review_scores: dict[str, Any] | None = None,
    vsse_scores: dict[str, Any] | None = None,
    allow_repair: bool = True,
    eae_asset_node_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Run full M34 evaluation on a single question.
    
    Returns dict with:
      - accepted: bool
      - scorecard: QuestionScorecard
      - blueprint: BlueprintMatchResult
      - exam_feel: ExamFeelV2Result
      - option_balance: OptionBalanceResult
      - distractor_quality: DistractorQualityV2Result
      - uniqueness: UniquenessResult
      - multi_stage: MultiStageReviewResult
      - repair: AutoRepairResult | None
      - reject_reason: str | None
      - question: dict (possibly repaired)
      - eae_node_verification: NodeVerificationResult | None
    """
    plan = plan or {}
    existing_stems = existing_stems or []
    
    # P0: Blueprint match
    bp = match_blueprint(question, plan, style_dna)
    
    # P1: Exam feel V2
    ef = detect_exam_feel_v2(question)
    
    # P2: Option balance
    ob = analyze_option_balance(question, question.get("correct_key"))
    
    # P3: Distractor quality
    dq = analyze_distractor_quality_v2(question, question.get("correct_key"))
    
    # P4: Uniqueness
    uq = check_uniqueness(str(question.get("stem") or ""), existing_stems)
    
    # P5: Multi-stage review
    ms = run_multi_stage_review(question, plan)
    
    # P9: Auto repair if failing on repairable dimensions
    repair_result = None
    repaired_question = question
    if allow_repair and not ms.passed and ms.failed_stage in ("language", "exam_feeling"):
        repaired_question, repair_result = auto_repair(question)
        if repair_result.repaired:
            # Re-evaluate after repair
            ef = detect_exam_feel_v2(repaired_question)
            ms = run_multi_stage_review(repaired_question, plan)
            bp = match_blueprint(repaired_question, plan, style_dna)
    
    # P6: Scorecard
    sc = build_scorecard(
        repaired_question, plan, style_dna,
        author_scores=author_scores,
        review_scores=review_scores,
        vsse_scores=vsse_scores,
    )
    
    # P_EAE: EAE Visual Node ID Hallucination Guard
    # Only runs when a visual EAE asset is attached to the question (eae_asset_node_ids supplied).
    eae_node_verification = None
    if eae_asset_node_ids is not None:
        eae_node_verification = EAENodeVerifier().verify_question_grounding(
            question_payload=repaired_question,
            available_node_ids=eae_asset_node_ids,
        )

    # Decision
    reject_reason = None
    accepted = True

    # P_EAE runs first — hallucinated node IDs are an immediate hard reject
    if eae_node_verification is not None and not eae_node_verification.is_valid:
        accepted = False
        reject_reason = f"eae_node_hallucination:{eae_node_verification.missing_node_ids}"
    elif bp.score < MIN_BLUEPRINT_SCORE:
        accepted = False
        reject_reason = f"blueprint_low:{bp.score}"
    elif not ef.passed:
        accepted = False
        reject_reason = f"exam_feel_v2:{ef.score}"
    elif not uq.is_unique:
        accepted = False
        reject_reason = f"not_unique:{uq.similarity_score:.2f}"
    elif not ms.passed:
        accepted = False
        reject_reason = f"multi_stage:{ms.failed_stage}"
    elif sc.overall < MIN_SCORECARD_OVERALL:
        accepted = False
        reject_reason = f"scorecard_low:{sc.overall}"

    logger.info(
        "[PIPELINE] M34 evaluate_question | accepted=%s reject_reason=%s bp=%s ef=%s uq=%s ms=%s sc=%s eae_ok=%s",
        accepted, reject_reason, bp.score, ef.score, uq.is_unique, ms.passed, sc.overall,
        eae_node_verification.is_valid if eae_node_verification else "n/a",
    )

    return {
        "accepted": accepted,
        "scorecard": sc,
        "blueprint": bp,
        "exam_feel": ef,
        "option_balance": ob,
        "distractor_quality": dq,
        "uniqueness": uq,
        "multi_stage": ms,
        "repair": repair_result,
        "reject_reason": reject_reason,
        "question": repaired_question,
        "eae_node_verification": eae_node_verification,
    }


def evaluate_batch(
    questions: list[dict[str, Any]],
    plans: list[dict[str, Any]] | None = None,
    style_dna: dict[str, Any] | None = None,
    existing_stems: list[str] | None = None,
) -> tuple[list[dict[str, Any]], BatchQualityReport]:
    """Evaluate a batch of questions, returning results and a batch report."""
    plans = plans or [{} for _ in range(len(questions))]
    existing = list(existing_stems or [])
    
    results: list[dict[str, Any]] = []
    accepted_scorecards: list[QuestionScorecard] = []
    rejected_count = 0
    rewritten_count = 0
    reject_reasons: dict[str, int] = {}
    
    for i, q in enumerate(questions):
        plan = plans[i] if i < len(plans) else {}
        result = evaluate_question(q, plan, style_dna, existing)
        results.append(result)
        
        if result["accepted"]:
            accepted_scorecards.append(result["scorecard"])
            existing.append(str(q.get("stem") or ""))
        else:
            rejected_count += 1
            reason = result["reject_reason"] or "unknown"
            category = reason.split(":")[0]
            reject_reasons[category] = reject_reasons.get(category, 0) + 1
        
        if result.get("repair") and result["repair"].repaired:
            rewritten_count += 1
    
    report = generate_batch_report(
        accepted_scorecards,
        total_attempted=len(questions),
        rejected_count=rejected_count,
        rewritten_count=rewritten_count,
        reject_reasons=reject_reasons,
    )
    
    return results, report
