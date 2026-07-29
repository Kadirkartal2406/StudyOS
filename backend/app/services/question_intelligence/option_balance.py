"""P2 — Real Option Balance analysis."""
from __future__ import annotations
import re
from typing import Any
from app.services.question_intelligence.types import OptionBalanceResult

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+", re.UNICODE)

def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text or "")


def analyze_option_balance(
    question: dict[str, Any],
    correct_key: str | None = None,
) -> OptionBalanceResult:
    """Analyze choice option balance for real-exam quality."""
    choices = question.get("choices") or {}
    correct_key = correct_key or question.get("correct_key") or "A"
    
    if len(choices) < 2:
        return OptionBalanceResult()
    
    texts = {k: str(v) for k, v in choices.items()}
    word_counts = {k: len(_words(v)) for k, v in texts.items()}
    char_counts = {k: len(v.strip()) for k, v in texts.items()}
    
    wc_values = list(word_counts.values())
    avg_wc = sum(wc_values) / len(wc_values)
    spread = max(wc_values) - min(wc_values) if wc_values else 0
    
    # 1. Length balance — options should be similar length
    if avg_wc > 0:
        cv = (max(wc_values) - min(wc_values)) / max(avg_wc, 1)
        if cv <= 0.5:
            length_balance = 95
        elif cv <= 1.0:
            length_balance = 80
        elif cv <= 2.0:
            length_balance = 60
        else:
            length_balance = 35
    else:
        length_balance = 20
    
    # 2. Language balance — similar complexity/register
    has_numbers = {k: bool(re.search(r"\d", v)) for k, v in texts.items()}
    numeric_count = sum(has_numbers.values())
    if numeric_count in (0, len(texts)):
        lang_balance = 92  # all same type
    elif numeric_count == 1:
        lang_balance = 70
    else:
        lang_balance = 80
    
    # 3. Obvious correct — correct answer shouldn't be notably different
    if correct_key in word_counts:
        correct_wc = word_counts[correct_key]
        others_wc = [v for k, v in word_counts.items() if k != correct_key]
        avg_others = sum(others_wc) / len(others_wc) if others_wc else 0
        # If correct is much longer (common AI pattern: more detail = correct)
        if avg_others > 0 and correct_wc > avg_others * 1.8:
            obvious_correct = 40  # obvious because longest
        elif avg_others > 0 and correct_wc < avg_others * 0.4:
            obvious_correct = 50  # obvious because shortest
        else:
            obvious_correct = 92
    else:
        obvious_correct = 85
    
    # 4. Obvious short — one option much shorter than others
    if wc_values and min(wc_values) <= 1 and avg_wc >= 4:
        obvious_short = 40
    elif wc_values and min(wc_values) <= max(1, avg_wc * 0.25):
        obvious_short = 60
    else:
        obvious_short = 92
    
    # 5. Structural variety — not all starting with same word
    starts = [str(v).split()[0].lower() if str(v).split() else "" for v in texts.values()]
    unique_starts = len(set(s for s in starts if s))
    if unique_starts >= len(texts) - 1:
        structural_variety = 92
    elif unique_starts >= len(texts) // 2:
        structural_variety = 72
    else:
        structural_variety = 45
    
    # 6. Repetition — check for repeated words across options
    all_words_per_opt = [set(_words(v.lower())) for v in texts.values()]
    if len(all_words_per_opt) >= 2:
        common = set.intersection(*all_words_per_opt)
        # Exclude common Turkish function words
        stop_words = {"ve", "ile", "bir", "bu", "da", "de", "için", "olan", "olarak", "gibi", "en", "çok"}
        meaningful_common = common - stop_words
        if len(meaningful_common) <= 1:
            repetition = 92
        elif len(meaningful_common) <= 3:
            repetition = 75
        else:
            repetition = 50
    else:
        repetition = 85
    
    return OptionBalanceResult(
        length_balance=length_balance,
        language_balance=lang_balance,
        obvious_correct=obvious_correct,
        obvious_short=obvious_short,
        structural_variety=structural_variety,
        repetition_score=repetition,
    )
