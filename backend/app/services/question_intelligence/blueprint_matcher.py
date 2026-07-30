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
    target_para = int(plan.get("paragraph_length") or style_dna.get("paragraph_length_avg") or 80)
    ratio = word_count / max(target_para, 1)
    if word_count < 5:
        para_score = 0
        sent_score = 20
        time_score = 20
    elif word_count < 10:
        para_score = 55
    elif 0.40 <= ratio <= 1.5:
        para_score = 95
    elif 0.25 <= ratio <= 2.0:
        para_score = 82
    else:
        para_score = 65
    
    # 2. Sentence length — avg words per sentence should be 10-30 for ÖSYM
    if sentences:
        avg_sent_len = word_count / len(sentences)
        if 10 <= avg_sent_len <= 30:
            sent_score = 95
        elif 6 <= avg_sent_len <= 40:
            sent_score = 80
        else:
            sent_score = 65
    else:
        sent_score = 60
    
    # 3. Option length — should be balanced
    opt_words = [len(_words(str(v))) for v in choices.values()]
    if opt_words:
        avg_opt = sum(opt_words) / len(opt_words)
        spread = max(opt_words) - min(opt_words) if opt_words else 0
        if 1 <= avg_opt <= 30 and spread <= 12:
            opt_score = 95
        elif 1 <= avg_opt <= 40 and spread <= 20:
            opt_score = 82
        else:
            opt_score = 65
    else:
        opt_score = 40
    
    # 4. Punctuation style — ÖSYM uses specific patterns
    low = stem.lower()
    punct_score = 85
    if stem.strip().endswith("?") or "hangisi" in low or "nedir" in low or "aşağıdakilerden" in low:
        punct_score = 95
    if stem.count("!") > 2 or stem.count("...") > 3:
        punct_score = max(50, punct_score - 20)
    
    # 5. Reasoning type match
    plan_reasoning = str(plan.get("reasoning_type") or "").lower()
    reasoning_score = 88
    if plan_reasoning in ("inference", "paragraph_inference") and ("çıkarılabilir" in low or "varılabilir" in low or "göre" in low or "söylenebilir" in low or "ulaşılabilir" in low):
        reasoning_score = 95
    elif plan_reasoning == "main_idea" and ("ana düşünce" in low or "ana fikir" in low or "asıl anlatmak" in low or "vurgulanmaktadır" in low):
        reasoning_score = 95
    elif plan_reasoning == "detail" and ("belirtilen" in low or "değinilen" in low or "değinilmemiştir" in low):
        reasoning_score = 95
    
    # 6. Stem style — paragraph-based vs direct question
    plan_stem_type = str(plan.get("stem_type") or "").lower()
    stem_score = 88
    has_paragraph = word_count >= 25
    if plan_stem_type in ("inference", "main_idea", "paragraph_completion") and has_paragraph:
        stem_score = 95
    elif plan_stem_type == "factual" and not has_paragraph:
        stem_score = 90
    
    # 7. Distractor family — check variety
    dist_score = 88
    if len(choices) >= 4:
        choice_texts = [str(v).lower() for v in choices.values()]
        unique_starts = len(set(t[:15] for t in choice_texts))
        if unique_starts >= len(choice_texts) - 1:
            dist_score = 95
        else:
            dist_score = 75
    
    # 8. Cognitive load — appropriate complexity
    cog_score = 88
    plan_difficulty = int(plan.get("difficulty") or 70)
    if plan_difficulty >= 75 and len(sentences) >= 2 and word_count >= 40:
        cog_score = 95
    elif plan_difficulty < 50 and word_count <= 100:
        cog_score = 92
    
    # 9. Reading duration — should match plan
    target_time = int(plan.get("reading_time_sec") or plan.get("target_time_sec") or 60)
    estimated_time = (word_count + sum(opt_words)) / 3.3
    time_ratio = estimated_time / max(target_time, 1)
    if 0.3 <= time_ratio <= 1.8:
        time_score = 92
    else:
        time_score = 75

    if word_count < 5:
        para_score = 0
        sent_score = 20
        time_score = 20
        stem_score = 40
        cog_score = 40
    
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
