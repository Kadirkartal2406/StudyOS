"""P9 — Auto Repair: fix minor issues without full regeneration."""
from __future__ import annotations
import re
from typing import Any
from app.services.question_intelligence.types import AutoRepairResult
from app.services.question_intelligence.exam_feel_v2 import detect_exam_feel_v2, _BANNED_PHRASES


def auto_repair(question: dict[str, Any]) -> tuple[dict[str, Any], AutoRepairResult]:
    """Attempt to repair minor language/exam-feel/naturalness issues.
    
    Only repairs if the failures are in Language, Exam Feel, or Naturalness.
    Returns (repaired_question, result).
    """
    stem = str(question.get("stem") or "")
    choices = dict(question.get("choices") or {})
    original_feel = detect_exam_feel_v2(question)
    
    repaired = False
    fields_fixed: list[str] = []
    original_scores: dict[str, int] = {"exam_feel": original_feel.score}
    
    new_stem = stem
    new_choices = dict(choices)
    
    # Fix 1: Remove banned AI phrases from stem
    low = new_stem.lower()
    for phrase, category in _BANNED_PHRASES:
        if phrase in low:
            # Case-insensitive removal
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            new_stem = pattern.sub("", new_stem)
            repaired = True
            if "exam_feel" not in fields_fixed:
                fields_fixed.append("exam_feel")
    
    # Fix 2: Clean up whitespace artifacts
    new_stem = re.sub(r"\s{2,}", " ", new_stem).strip()
    new_stem = re.sub(r"\s+([.,;:?!])", r"\1", new_stem)
    
    # Fix 3: Remove AI phrases from choices
    for key, text in new_choices.items():
        original_text = text
        for phrase, category in _BANNED_PHRASES:
            if phrase in text.lower():
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                text = pattern.sub("", text)
        text = re.sub(r"\s{2,}", " ", text).strip()
        if text != original_text:
            new_choices[key] = text
            repaired = True
            if "naturalness" not in fields_fixed:
                fields_fixed.append("naturalness")
    
    # Fix 4: Remove self-referential openers
    openers_to_remove = [
        r"^Bu metinde\s+",
        r"^Verilen paragrafta\s+",
        r"^Yukarıdaki metne göre\s+",
        r"^Aşağıdaki metne göre\s+",
    ]
    for pattern_str in openers_to_remove:
        match = re.match(pattern_str, new_stem, re.IGNORECASE)
        if match:
            new_stem = new_stem[match.end():]
            new_stem = new_stem[0].upper() + new_stem[1:] if new_stem else new_stem
            repaired = True
            if "language" not in fields_fixed:
                fields_fixed.append("language")
    
    repaired_question = {
        **question,
        "stem": new_stem,
        "choices": new_choices,
    }
    
    new_feel = detect_exam_feel_v2(repaired_question)
    
    return repaired_question, AutoRepairResult(
        repaired=repaired,
        fields_fixed=fields_fixed,
        original_scores=original_scores,
        new_scores={"exam_feel": new_feel.score},
    )
