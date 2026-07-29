"""P3 — Distractor Quality V2 with type classification."""
from __future__ import annotations
import re
from typing import Any
from app.services.question_intelligence.types import (
    DISTRACTOR_TYPES,
    DistractorQualityV2Result,
)

_WORD_RE = re.compile(r"[A-Za-zÀ-ÿĞğİıÖöŞşÜüÇç0-9]+", re.UNICODE)


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text or "")


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _classify_distractor(
    distractor_text: str,
    correct_text: str,
    stem: str,
) -> str:
    """Heuristic distractor type classification."""
    d_words = set(_words(distractor_text.lower()))
    c_words = set(_words(correct_text.lower()))
    s_words = set(_words(stem.lower()))
    
    similarity = _jaccard(d_words, c_words)
    stem_overlap = _jaccard(d_words, s_words)
    
    # High similarity to correct → close meaning (yakın anlam)
    if similarity >= 0.6:
        return "yakin_anlam"
    
    # Shares words with stem but misses key parts → incomplete inference
    if stem_overlap >= 0.3 and similarity < 0.3:
        return "eksik_cikarim"
    
    # Very different from both → scope shift
    if similarity < 0.15 and stem_overlap < 0.15:
        return "kapsam_kaymasi"
    
    # Contains negation or opposite markers → cause-effect error
    neg_markers = {"değil", "olmaz", "yapamaz", "edemez", "karşı", "aksine", "tersine"}
    if d_words & neg_markers:
        return "sebep_sonuc_hatasi"
    
    # Moderate similarity → could be overgeneralization
    if 0.3 <= similarity < 0.6:
        return "asiri_genelleme"
    
    # Default
    return "kavram_karisikligi"


def analyze_distractor_quality_v2(
    question: dict[str, Any],
    correct_key: str | None = None,
) -> DistractorQualityV2Result:
    """Analyze distractor quality with type classification."""
    choices = question.get("choices") or {}
    correct_key = correct_key or question.get("correct_key") or "A"
    stem = str(question.get("stem") or "")
    correct_text = str(choices.get(correct_key) or "")
    
    types_detected: dict[str, str] = {}
    
    for key, text in choices.items():
        if key == correct_key:
            continue
        dtype = _classify_distractor(str(text), correct_text, stem)
        types_detected[key] = dtype
    
    # Type variety — how many distinct types
    unique_types = set(types_detected.values())
    num_distractors = len(types_detected)
    
    if num_distractors == 0:
        return DistractorQualityV2Result()
    
    variety_ratio = len(unique_types) / max(num_distractors, 1)
    if variety_ratio >= 0.75:
        type_variety = 95
    elif variety_ratio >= 0.5:
        type_variety = 80
    else:
        type_variety = 55
    
    # Plausibility — distractors should be similar length/style to correct
    correct_wc = len(_words(correct_text))
    dist_wcs = [len(_words(str(choices[k]))) for k in types_detected]
    if dist_wcs and correct_wc > 0:
        ratios = [wc / max(correct_wc, 1) for wc in dist_wcs]
        avg_ratio = sum(ratios) / len(ratios)
        if 0.5 <= avg_ratio <= 1.8:
            plausibility = 92
        elif 0.3 <= avg_ratio <= 2.5:
            plausibility = 72
        else:
            plausibility = 45
    else:
        plausibility = 70
    
    # Trap effectiveness — distractors should share enough with correct to be tempting
    trap_scores = []
    for key in types_detected:
        d_words = set(_words(str(choices[key]).lower()))
        c_words = set(_words(correct_text.lower()))
        sim = _jaccard(d_words, c_words)
        # Sweet spot: 0.15-0.5 similarity
        if 0.15 <= sim <= 0.5:
            trap_scores.append(92)
        elif 0.05 <= sim <= 0.65:
            trap_scores.append(72)
        else:
            trap_scores.append(45)
    
    trap_effectiveness = int(sum(trap_scores) / len(trap_scores)) if trap_scores else 70
    
    return DistractorQualityV2Result(
        types_detected=types_detected,
        type_variety=type_variety,
        plausibility=plausibility,
        trap_effectiveness=trap_effectiveness,
    )
