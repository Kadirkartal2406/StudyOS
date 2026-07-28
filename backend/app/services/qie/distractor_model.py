"""Distractor Intelligence — planner selects; LLM only writes."""

from __future__ import annotations

from enum import StrEnum


class DistractorPattern(StrEnum):
    MEANING_SHIFT = "meaning_shift"
    HALF_CORRECT = "half_correct"
    OPPOSITE_LOGIC = "opposite_logic"
    OVER_GENERALIZATION = "over_generalization"
    UNDER_GENERALIZATION = "under_generalization"
    TERMINOLOGY_CONFUSION = "terminology_confusion"
    CAUSE_EFFECT_SWAP = "cause_effect_swap"
    SCOPE_SHIFT = "scope_shift"
    PRONOUN_TRAP = "pronoun_trap"
    TIME_TRAP = "time_trap"


DISTRACTOR_PROMPTS: dict[str, str] = {
    DistractorPattern.MEANING_SHIFT: (
        "Meaning Shift: options that flip a key nuance while looking close to the correct answer."
    ),
    DistractorPattern.HALF_CORRECT: (
        "Half Correct: partially true statements that miss a critical condition."
    ),
    DistractorPattern.OPPOSITE_LOGIC: (
        "Opposite Logic: reverse the causal or logical direction."
    ),
    DistractorPattern.OVER_GENERALIZATION: (
        "Over-Generalization: stretch a local claim into an absolute."
    ),
    DistractorPattern.UNDER_GENERALIZATION: (
        "Under-Generalization: narrow a valid claim so it no longer fits."
    ),
    DistractorPattern.TERMINOLOGY_CONFUSION: (
        "Terminology Confusion: swap near-synonyms or exam jargon."
    ),
    DistractorPattern.CAUSE_EFFECT_SWAP: (
        "Cause-Effect Swap: invert cause and effect."
    ),
    DistractorPattern.SCOPE_SHIFT: (
        "Scope Shift: change who/what the claim applies to."
    ),
    DistractorPattern.PRONOUN_TRAP: (
        "Pronoun Trap: ambiguous reference that looks coherent."
    ),
    DistractorPattern.TIME_TRAP: (
        "Time Trap: wrong tense / sequence / temporal scope."
    ),
}


_CYCLE = list(DistractorPattern)


def pick_distractor(
    *,
    index: int = 0,
    forbidden: list[str] | None = None,
    preferred: list[str] | None = None,
) -> str:
    """Deterministic distractor selection — never random LLM choice."""
    forbidden_set = {f.lower().replace("-", "_") for f in (forbidden or [])}
    preferred_list = [p.lower().replace("-", "_") for p in (preferred or [])]

    for p in preferred_list:
        if p not in forbidden_set and p in DISTRACTOR_PROMPTS:
            return p

    for offset in range(len(_CYCLE)):
        cand = _CYCLE[(index + offset) % len(_CYCLE)].value
        if cand not in forbidden_set:
            return cand
    return DistractorPattern.MEANING_SHIFT.value


def distractor_contract(pattern: str) -> str:
    key = (pattern or "").lower().replace("-", "_")
    return DISTRACTOR_PROMPTS.get(
        key,
        DISTRACTOR_PROMPTS[DistractorPattern.MEANING_SHIFT],
    )
