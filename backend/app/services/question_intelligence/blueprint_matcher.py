"""P0 — Real Exam Blueprint Match."""
from __future__ import annotations
import re
from typing import Any
from app.services.question_intelligence.types import BlueprintMatchResult

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+", re.UNICODE)
_SENT_RE = re.compile(r"[.!?…]+")

def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text or "")

def _sentences(text: str) -> list[str]:
    parts = _SENT_RE.split(text.strip())
    return [s.strip() for s in parts if s.strip()]

def match_blueprint(
    question: dict[str, Any],
    plan: dict[str, Any],
    style_dna: dict[str, Any] | None = None,
) -> BlueprintMatchResult:
    """Score a question against real exam blueprint (0-100 per dimension)."""
    style_dna = style_dna or {}
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    
    words = _words(stem)
    word_count = len(words)
    sentences = _sentences(stem)
    
    # 1. Paragraph length — compare to plan target
    target_para = int(plan.get("paragraph_length") or style_dna.get("paragraph_length_avg") or 120)
    ratio = word_count / max(target_para, 1)
    if 0.65 <= ratio <= 1.35:
        para_score = 95
    elif 0.5 <= ratio <= 1.6:
        para_score = 78
    elif 0.35 <= ratio <= 2.0:
        para_score = 60
    else:
        para_score = 35
    
    # 2. Sentence length — avg words per sentence should be 12-25 for ÖSYM
    if sentences:
        avg_sent_len = word_count / len(sentences)
        if 12 <= avg_sent_len <= 25:
            sent_score = 95
        elif 8 <= avg_sent_len <= 35:
            sent_score = 75
        else:
            sent_score = 50
    else:
        sent_score = 40
    
    # 3. Option length — should be balanced
    opt_words = [len(_words(str(v))) for v in choices.values()]
    if opt_words:
        avg_opt = sum(opt_words) / len(opt_words)
        spread = max(opt_words) - min(opt_words) if opt_words else 0
        # ÖSYM options typically 2-15 words each, spread <= 8
        if 2 <= avg_opt <= 15 and spread <= 8:
            opt_score = 95
        elif 1 <= avg_opt <= 25 and spread <= 15:
            opt_score = 72
        else:
            opt_score = 45
    else:
        opt_score = 20
    
    # 4. Punctuation style — ÖSYM uses specific patterns
    low = stem.lower()
    punct_score = 80
    # Questions typically end with "?" or specific patterns
    if stem.strip().endswith("?") or "hangisi" in low or "nedir" in low or "aşağıdakilerden" in low:
        punct_score = 95
    # No excessive punctuation
    if stem.count("!") > 2 or stem.count("...") > 3:
        punct_score = max(40, punct_score - 30)
    
    # 5. Reasoning type match
    plan_reasoning = str(plan.get("reasoning_type") or "").lower()
    reasoning_score = 85  # default
    # Check if question structure matches reasoning type
    if plan_reasoning == "inference" and ("çıkarılabilir" in low or "varılabilir" in low or "göre" in low):
        reasoning_score = 95
    elif plan_reasoning == "main_idea" and ("ana düşünce" in low or "ana fikir" in low or "asıl anlatmak" in low):
        reasoning_score = 95
    elif plan_reasoning == "detail" and ("belirtilen" in low or "değinilen" in low):
        reasoning_score = 95
    elif plan_reasoning in ("inference", "main_idea", "detail"):
        reasoning_score = 75  # didn't match expected keywords
    
    # 6. Stem style — paragraph-based vs direct question
    plan_stem_type = str(plan.get("stem_type") or "").lower()
    stem_score = 85
    has_paragraph = word_count > 60
    if plan_stem_type in ("inference", "main_idea", "paragraph_completion") and has_paragraph:
        stem_score = 95
    elif plan_stem_type == "factual" and not has_paragraph:
        stem_score = 90
    elif plan_stem_type in ("inference", "main_idea") and not has_paragraph:
        stem_score = 55
    
    # 7. Distractor family — check variety
    plan_distractor = str(plan.get("distractor_pattern") or "").lower()
    dist_score = 85
    if len(choices) >= 4:
        # Check if distractors look varied
        choice_texts = [str(v).lower() for v in choices.values()]
        unique_starts = len(set(t[:15] for t in choice_texts))
        if unique_starts >= len(choice_texts) - 1:
            dist_score = 92
        else:
            dist_score = 65
    
    # 8. Cognitive load — appropriate complexity
    cog_score = 85
    plan_difficulty = int(plan.get("difficulty") or 70)
    # High difficulty should have higher cognitive load (more sentences, complex structure)
    if plan_difficulty >= 75 and len(sentences) >= 3 and word_count >= 80:
        cog_score = 95
    elif plan_difficulty < 50 and word_count <= 100:
        cog_score = 92
    elif plan_difficulty >= 75 and word_count < 40:
        cog_score = 55  # too simple for high difficulty
    
    # 9. Reading duration — should match plan
    target_time = int(plan.get("reading_time_sec") or plan.get("target_time_sec") or 75)
    # Estimate reading time: ~200 wpm Turkish = ~3.3 wps
    estimated_time = (word_count + sum(opt_words)) / 3.3
    time_ratio = estimated_time / max(target_time, 1)
    if 0.5 <= time_ratio <= 1.5:
        time_score = 92
    elif 0.3 <= time_ratio <= 2.0:
        time_score = 72
    else:
        time_score = 45
    
    return BlueprintMatchResult(
        paragraph_length=para_score,
        sentence_length=sent_score,
        option_length=opt_score,
        punctuation_style=punct_score,
        reasoning_type=reasoning_score,
        stem_style=stem_score,
        distractor_family=dist_score,
        cognitive_load=cog_score,
        reading_duration=time_score,
    )
