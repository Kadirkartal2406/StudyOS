"""P1 — Exam Feel Detector V2: AI language & prompt-smell detection."""
from __future__ import annotations
import re
from typing import Any
from app.services.question_intelligence.types import ExamFeelV2Result

# Phrases that betray AI generation — must never appear in ÖSYM-level questions
_BANNED_PHRASES: list[tuple[str, str]] = [
    ("bu metne göre", "ai_opener"),
    ("bloom düzeyi", "meta_leak"),
    ("ölçülen kazanım", "meta_leak"),
    ("aşağıdaki seçeneklerden", "ai_directive"),
    ("doğru cevap", "answer_leak"),
    ("çeldirici", "meta_leak"),
    ("mantıksal çıkarım", "meta_leak"),
    ("yapay zeka", "ai_reference"),
    ("chatgpt", "ai_reference"),
    ("as an ai", "ai_reference"),
    ("language model", "ai_reference"),
    ("geçici stub", "stub_marker"),
    ("lorem ipsum", "stub_marker"),
    ("test sorusu", "meta_leak"),
    ("bu soru", "self_reference"),
    ("soruyu yanıtlayınız", "ai_directive"),
    ("aşağıdaki bilgilere göre", "ai_opener"),
    ("verilen bilgilere dayanarak", "ai_opener"),
    ("dikkatli okuyunuz", "ai_directive"),
    ("kelimelik resmi bir üslup", "prompt_leak"),
    ("günlük yaşamdan bir durumu anlatan kısa bir metin düşününüz", "prompt_leak"),
    ("bilişsel", "meta_leak"),
    ("taksonomisi", "meta_leak"),
    ("kazanım ölçme", "meta_leak"),
    ("soru kökü", "meta_leak"),
    ("çoktan seçmeli", "meta_leak"),
    ("distractor", "english_meta"),
    ("correct answer", "english_meta"),
    ("multiple choice", "english_meta"),
    ("stem:", "english_meta"),
    ("option quality", "english_meta"),
]

# Regex patterns for subtler AI smell
_AI_SMELL_PATTERNS: list[tuple[re.Pattern, str, int]] = [
    (re.compile(r"(?:I\.|II\.|III\.|IV\.)\s*Yalnız", re.IGNORECASE), "roman_numeral_only", 5),
    (re.compile(r"Buna göre,?\s+aşağıdaki", re.IGNORECASE), "formulaic_transition", 8),
    (re.compile(r"(?:Yukarıdaki|Verilen)\s+(?:paragraf|metin|bilgi)(?:a|e|da|de|dan|den)\s+göre", re.IGNORECASE), "reference_pattern", 3),
    (re.compile(r"hangi(?:si|leri)\s+(?:doğrudur|yanlıştır|söylenebilir)\s*\?", re.IGNORECASE), "generic_question_ending", 3),
]

# Positive signals — real ÖSYM patterns
_POSITIVE_PATTERNS: list[tuple[str, int]] = [
    ("aşağıdakilerden hangisi", 3),
    ("hangisinde verilmiştir", 3),
    ("hangisi söylenemez", 3),
    ("çıkarılamaz", 2),
    ("değildir", 2),
    ("uygundur", 2),
    ("verilemez", 2),
]


def detect_exam_feel_v2(question: dict[str, Any]) -> ExamFeelV2Result:
    """Analyze question for AI-generated language patterns."""
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    all_text = stem + " " + " ".join(str(v) for v in choices.values())
    low = all_text.lower()
    
    score = 90  # start high
    detected: list[str] = []
    
    # Check banned phrases
    for phrase, category in _BANNED_PHRASES:
        if phrase in low:
            detected.append(f"{category}:{phrase}")
            if category in ("meta_leak", "prompt_leak", "english_meta", "stub_marker"):
                score -= 30  # severe
            elif category in ("ai_reference", "answer_leak"):
                score -= 25
            elif category in ("ai_opener", "ai_directive"):
                score -= 15
            elif category == "self_reference":
                score -= 10
    
    # Check subtle patterns
    for pattern, name, penalty in _AI_SMELL_PATTERNS:
        if pattern.search(all_text):
            detected.append(f"pattern:{name}")
            score -= penalty
    
    # Positive signals boost
    for phrase, bonus in _POSITIVE_PATTERNS:
        if phrase in low:
            score += bonus
    
    # Check for overly uniform option structure (AI tendency)
    choice_vals = list(choices.values())
    if len(choice_vals) >= 4:
        starts = [str(v).split()[0].lower() if str(v).split() else "" for v in choice_vals]
        if len(set(starts)) == 1 and starts[0]:
            detected.append("uniform_option_start")
            score -= 8
    
    # Check for unnatural formality markers
    formal_count = sum(1 for w in ("dolayısıyla", "binaenaleyh", "maamafih", "nitekim") if w in low)
    if formal_count >= 3:
        detected.append("over_formal")
        score -= 5
    
    score = max(0, min(100, score))
    
    return ExamFeelV2Result(
        score=score,
        detected_phrases=detected,
        passed=score >= 70,
    )
