"""P5 — Multi-Stage Exam Review (6 stages)."""
from __future__ import annotations
from typing import Any
from app.services.question_intelligence.types import MultiStageReviewResult
from app.services.question_intelligence.exam_feel_v2 import detect_exam_feel_v2
from app.services.question_intelligence.option_balance import analyze_option_balance
from app.services.question_intelligence.distractor_quality_v2 import analyze_distractor_quality_v2


def _stage_language(question: dict[str, Any]) -> int:
    """Stage 1: Language quality check."""
    import re
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    all_text = stem + " " + " ".join(str(v) for v in choices.values())
    
    score = 90
    
    # Grammar issues
    if re.search(r"\s{2,}", stem):
        score -= 5
    if re.search(r"[a-z]\.[A-Z]", stem):  # missing space after period
        score -= 8
    
    # Mixed language
    english_words = re.findall(r"\b[a-zA-Z]{4,}\b", stem)
    turkish_words = re.findall(r"[A-Za-zĞğİıÖöŞşÜüÇç]{3,}", stem)
    if turkish_words and english_words:
        ratio = len(english_words) / max(len(turkish_words), 1)
        if ratio > 0.3:
            score -= 15
    
    # Too short
    if len(stem.strip()) < 30:
        score -= 20
    
    # Check options have content
    empty_opts = sum(1 for v in choices.values() if len(str(v).strip()) < 2)
    score -= empty_opts * 15
    
    return max(0, min(100, score))


def _stage_difficulty(question: dict[str, Any], plan: dict[str, Any]) -> int:
    """Stage 3: Difficulty appropriateness."""
    import re
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    target = int(plan.get("difficulty") or 70)
    
    word_count = len(re.findall(r"\w+", stem))
    choice_count = len(choices)
    
    score = 85
    
    # High difficulty should have complex questions
    if target >= 80:
        if word_count < 50:
            score -= 15
        if choice_count < 5:
            score -= 5
    elif target <= 40:
        if word_count > 200:
            score -= 10
    
    return max(0, min(100, score))


def _stage_fairness(question: dict[str, Any]) -> int:
    """Stage 5: Fairness check."""
    stem = str(question.get("stem") or "").lower()
    choices = question.get("choices") or {}
    
    score = 95
    
    # Gender bias markers
    gender_heavy = sum(1 for w in ("erkek", "kadın", "kız", "oğlan", "anne", "baba") if w in stem)
    if gender_heavy >= 3:
        score -= 10
    
    # Cultural bias — checking for region-specific references
    # Allowed: general Turkish culture
    # Flag: specific city/region stereotypes
    
    # Check if correct answer is always in same position pattern
    correct_key = str(question.get("correct_key") or "A")
    keys_sorted = sorted(choices.keys())
    if correct_key == keys_sorted[0]:
        score -= 3  # slight concern if always first
    
    # "Hepsi" / "Hiçbiri" as catch-all
    for v in choices.values():
        low_v = str(v).lower()
        if low_v in ("hepsi", "hiçbiri", "hepsi doğrudur", "hiçbiri doğru değildir"):
            score -= 5
    
    return max(0, min(100, score))


def _stage_human_examiner(question: dict[str, Any]) -> int:
    """Stage 6: Human examiner simulation."""
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    
    score = 85
    
    # Real exam presence signals
    word_count = len(stem.split())
    if 60 <= word_count <= 200:
        score += 5
    
    if len(choices) >= 5:
        score += 3
    
    # Self-contained question
    if "?" in stem or "hangisi" in stem.lower():
        score += 3
    
    # No meta language
    low = stem.lower()
    meta_words = ("soru", "test", "ölçme", "değerlendirme", "kazanım")
    meta_count = sum(1 for w in meta_words if w in low)
    score -= meta_count * 5
    
    return max(0, min(100, score))


MIN_STAGE_SCORE = 65


def run_multi_stage_review(
    question: dict[str, Any],
    plan: dict[str, Any] | None = None,
) -> MultiStageReviewResult:
    """Run all 6 review stages. Fail fast on any stage below threshold."""
    plan = plan or {}
    
    # Stage 1: Language
    lang = _stage_language(question)
    if lang < MIN_STAGE_SCORE:
        return MultiStageReviewResult(language=lang, passed=False, failed_stage="language")
    
    # Stage 2: Exam Feeling
    feel = detect_exam_feel_v2(question)
    if feel.score < MIN_STAGE_SCORE:
        return MultiStageReviewResult(language=lang, exam_feeling=feel.score,
                                       passed=False, failed_stage="exam_feeling")
    
    # Stage 3: Difficulty
    diff = _stage_difficulty(question, plan)
    if diff < MIN_STAGE_SCORE:
        return MultiStageReviewResult(language=lang, exam_feeling=feel.score,
                                       difficulty=diff, passed=False, failed_stage="difficulty")
    
    # Stage 4: Distractor
    dist_result = analyze_distractor_quality_v2(question, question.get("correct_key"))
    dist_score = dist_result.score
    if dist_score < MIN_STAGE_SCORE:
        return MultiStageReviewResult(language=lang, exam_feeling=feel.score,
                                       difficulty=diff, distractor=dist_score,
                                       passed=False, failed_stage="distractor")
    
    # Stage 5: Fairness
    fair = _stage_fairness(question)
    if fair < MIN_STAGE_SCORE:
        return MultiStageReviewResult(language=lang, exam_feeling=feel.score,
                                       difficulty=diff, distractor=dist_score,
                                       fairness=fair, passed=False, failed_stage="fairness")
    
    # Stage 6: Human Examiner
    examiner = _stage_human_examiner(question)
    if examiner < MIN_STAGE_SCORE:
        return MultiStageReviewResult(language=lang, exam_feeling=feel.score,
                                       difficulty=diff, distractor=dist_score,
                                       fairness=fair, human_examiner=examiner,
                                       passed=False, failed_stage="human_examiner")
    
    return MultiStageReviewResult(
        language=lang,
        exam_feeling=feel.score,
        difficulty=diff,
        distractor=dist_score,
        fairness=fair,
        human_examiner=examiner,
        passed=True,
        failed_stage=None,
    )
