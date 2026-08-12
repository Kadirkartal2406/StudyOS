"""Explanation self-consistency — derived relation vs claimed answer."""

from __future__ import annotations

import re
from typing import Any

from app.services.correctness.math_parser import parse_math, values_equal
from app.services.correctness.numeric_extract import extract_numeric_answer
from app.services.correctness.relation_parse import (
    RelationForm,
    extract_relations_from_text,
    parse_linear_relation,
    parse_option_value,
    relations_equal,
)
from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
)

# Explicit "derived value is not among the options" language.
_ABSENCE_RE = re.compile(
    r"(?:"
    r"seçeneklerde\s+(?:[^\n.]{0,80}?\s+)?(?:yok(?:tur)?|bulunmuyor)|"
    r"şıklarda\s+(?:[^\n.]{0,80}?\s+)?(?:yok(?:tur)?|bulunmuyor)|"
    r"seçeneklerde\s+yok|"
    r"şıklarda\s+yok|"
    r"not among the choices|"
    r"not in the (?:options|choices)|"
    r"\bno option\b"
    r")",
    re.IGNORECASE,
)

_EQ_NUMBER_RE = re.compile(
    r"=\s*(-?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?)",
)
_NUMBER_BEFORE_ABSENCE_RE = re.compile(
    r"(-?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?)\s+"
    r"(?:seçeneklerde|şıklarda|yok|yoktur|bulunmuyor|not among|not in the)",
    re.IGNORECASE,
)


def _claimed_relation(inp: CorrectnessInput) -> RelationForm | None:
    key = str(inp.correct_key or "").upper()
    for k, v in (inp.choices or {}).items():
        if str(k).upper() == key:
            rel = parse_linear_relation(str(v))
            if rel is not None:
                return rel
    rels = extract_relations_from_text(inp.explanation or "")
    if rels:
        return rels[-1]
    return None


def _has_valid_correct_key(inp: CorrectnessInput) -> bool:
    key = str(inp.correct_key or "").upper()
    if not key or not inp.choices:
        return False
    return any(str(k).upper() == key for k in inp.choices)


def _extract_confessed_derived_value(expl: str) -> tuple[Any, str] | None:
    """Return (sympy_value, display) only when absence language + nearby number."""
    absence = _ABSENCE_RE.search(expl)
    if not absence:
        return None

    window_start = max(0, absence.start() - 100)
    window = expl[window_start : absence.end() + 10]

    token: str | None = None
    eq_hits = list(_EQ_NUMBER_RE.finditer(window))
    if eq_hits:
        token = eq_hits[-1].group(1)
    else:
        before = _NUMBER_BEFORE_ABSENCE_RE.search(window)
        if before:
            token = before.group(1)

    if token is None:
        # Fallback: existing conservative extractor, only with absence present.
        extracted = extract_numeric_answer(expl)
        if extracted.ok and extracted.value is not None:
            return extracted.value, extracted.display or str(extracted.value)
        return None

    parsed = parse_math(token.replace(",", "."))
    if not parsed.ok:
        return None
    return parsed.expr, token


def _matches_any_option(value: Any, choices: dict[str, str]) -> bool:
    for text in (choices or {}).values():
        parsed = parse_option_value(str(text))
        if not parsed.ok:
            continue
        if isinstance(parsed.expr, RelationForm):
            continue
        if values_equal(value, parsed.expr) is True:
            return True
    return False


def _check_confessed_value_missing_from_options(
    inp: CorrectnessInput,
    evidence: dict[str, Any],
) -> CorrectnessCheck | None:
    """HARD FAIL when explanation derives N, admits N∉options, yet claims a key."""
    expl = inp.explanation or ""
    if not _ABSENCE_RE.search(expl):
        return None
    if not _has_valid_correct_key(inp):
        return None

    derived = _extract_confessed_derived_value(expl)
    if derived is None:
        # Absence without a reliable numeric — do not FAIL.
        return None

    value, display = derived
    evidence["confessed_derived_value"] = display
    evidence["absence_language"] = True

    if _matches_any_option(value, inp.choices or {}):
        # Confession is wrong / value is present — do not FAIL on this signal.
        evidence["confessed_value_in_options"] = True
        return None

    evidence["confessed_value_in_options"] = False
    return CorrectnessCheck(
        name="explanation_consistency",
        status="fail",
        error_code=CorrectnessErrorCode.NO_CORRECT_OPTION.value,
        message=f"explanation_confessed_no_option:derived={display}",
        evidence=evidence,
    )


def check_explanation_consistency(inp: CorrectnessInput) -> CorrectnessCheck:
    """FAIL only on clear derived-vs-claimed contradictions."""
    evidence: dict[str, Any] = {
        "derived_relations": [],
        "claimed_relation": None,
        "contradiction": None,
    }
    expl = inp.explanation or ""
    if not expl.strip():
        return CorrectnessCheck(
            name="explanation_consistency",
            status="pass",
            evidence=evidence,
        )

    confessed = _check_confessed_value_missing_from_options(inp, evidence)
    if confessed is not None:
        return confessed

    derived_all = extract_relations_from_text(expl)
    evidence["derived_relations"] = [r.raw for r in derived_all]
    claimed = _claimed_relation(inp)
    if claimed is not None:
        evidence["claimed_relation"] = claimed.raw

    if claimed is None or not derived_all:
        return CorrectnessCheck(
            name="explanation_consistency",
            status="pass",
            evidence=evidence,
        )

    contradictions: list[dict[str, str]] = []
    for rel in derived_all:
        eq = relations_equal(rel, claimed)
        if eq is False:
            contradictions.append({"derived": rel.raw, "claimed": claimed.raw})

    if contradictions and claimed is not None:
        claimed_from_choice = False
        key = str(inp.correct_key or "").upper()
        for k, v in (inp.choices or {}).items():
            if str(k).upper() == key and parse_linear_relation(str(v)) is not None:
                claimed_from_choice = True
                break

        usable: list[dict[str, str]] = []
        for item in contradictions:
            der = item["derived"]
            if claimed_from_choice:
                usable.append(item)
                continue
            idx_der = expl.find(der)
            idx_cl = expl.rfind(claimed.raw)
            if idx_der >= 0 and (idx_cl < 0 or idx_der < idx_cl):
                usable.append(item)

        if usable:
            evidence["contradiction"] = usable[0]
            return CorrectnessCheck(
                name="explanation_consistency",
                status="fail",
                error_code=CorrectnessErrorCode.ANSWER_KEY_MISMATCH.value,
                message=(
                    "explanation_self_inconsistency:"
                    f"{usable[0]['derived']}!={usable[0]['claimed']}"
                ),
                evidence=evidence,
            )

    return CorrectnessCheck(
        name="explanation_consistency",
        status="pass",
        evidence=evidence,
    )
