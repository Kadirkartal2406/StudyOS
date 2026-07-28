"""Distractor attraction analytics for virtual students."""

from __future__ import annotations

from typing import Any

from app.services.question_virtual_student.types import DistractorAttraction


def _token_set(text: str) -> set[str]:
    return {w for w in (text or "").lower().split() if len(w) >= 3}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(len(a | b), 1)


def rank_distractor_attraction(question: dict[str, Any]) -> list[DistractorAttraction]:
    choices = {str(k).upper(): str(v) for k, v in (question.get("choices") or {}).items()}
    correct = str(question.get("correct_key") or "A").upper()
    stem_toks = _token_set(str(question.get("stem") or ""))
    correct_toks = _token_set(choices.get(correct, ""))

    out: list[DistractorAttraction] = []
    for key, text in choices.items():
        toks = _token_set(text)
        sim = _jaccard(toks, correct_toks)
        stem_overlap = _jaccard(toks, stem_toks)
        length = len(text.split())
        attraction = 0.25 * sim + 0.35 * stem_overlap + min(0.25, length / 40.0)
        trap = "yakin_kavram"
        reason = "lexical_overlap"
        if key == correct:
            attraction = max(attraction, 0.55)
            trap = "correct"
            reason = "correct_option"
        else:
            if sim >= 0.45:
                trap = "yakin_anlam"
                reason = "similar_to_correct"
                attraction += 0.15
            elif stem_overlap >= 0.35:
                trap = "yarim_bilgi"
                reason = "stem_cue_without_full_match"
                attraction += 0.1
            elif length <= 2:
                trap = "dikkat_hatasi"
                reason = "too_short_easy_reject"
                attraction -= 0.1
            attraction = max(0.05, min(0.95, attraction))

        out.append(
            DistractorAttraction(
                option=key,
                attraction_score=round(attraction, 3),
                reason=reason,
                similarity_to_correct=round(sim, 3),
                trap_type=trap,
            )
        )
    out.sort(key=lambda d: d.attraction_score, reverse=True)
    return out
