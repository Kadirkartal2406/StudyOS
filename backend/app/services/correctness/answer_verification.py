"""Match an extracted / template numeric answer against options and claimed key."""

from __future__ import annotations

from typing import Any

from app.services.correctness.area_template import try_poly_abs_area
from app.services.correctness.math_parser import values_equal
from app.services.correctness.numeric_extract import extract_numeric_answer
from app.services.correctness.relation_parse import (
    RelationForm,
    parse_option_value,
    relations_equal,
)
from app.services.correctness.types import CorrectnessErrorCode, CorrectnessInput


def _empty_evidence(claimed_key: str) -> dict[str, Any]:
    return {
        "claimed_key": claimed_key,
        "solved_value": None,
        "matching_keys": [],
        "equivalent_pairs": [],
    }


def _match_options(solved: Any, choices: dict[str, str]) -> tuple[list[str], int]:
    matching: list[str] = []
    parseable = 0
    for key, text in (choices or {}).items():
        parsed = parse_option_value(str(text))
        if not parsed.ok:
            continue
        parseable += 1
        if isinstance(solved, RelationForm) and isinstance(parsed.expr, RelationForm):
            eq = relations_equal(solved, parsed.expr)
        elif isinstance(parsed.expr, RelationForm) or isinstance(solved, RelationForm):
            eq = False
        else:
            eq = values_equal(solved, parsed.expr)
        if eq is True:
            matching.append(str(key).upper())
    return sorted(set(matching)), parseable


def verify_answer_key(inp: CorrectnessInput) -> dict[str, Any]:
    """Return a check dict: status, error_code, message, evidence.

    UNSUPPORTED when the explanation cannot be parsed reliably.
    Confession language without a matching option is FAIL (no_correct_option).
    Narrow stem area template may supply the solved value when applicable.
    """
    claimed = str(inp.correct_key or "").upper()
    evidence = _empty_evidence(claimed)

    solved: Any = None
    display: str | None = None
    source: str | None = None
    confession = False

    area = try_poly_abs_area(inp.stem or "")
    if area.ok:
        solved = area.expr
        display = str(area.expr)
        source = "poly_abs_area_template"
        evidence["area_template"] = area.raw
    else:
        extracted = extract_numeric_answer(inp.explanation)
        confession = extracted.confession
        if not extracted.ok:
            if extracted.confession:
                evidence["solved_value"] = None
                evidence["confession"] = True
                return {
                    "status": "fail",
                    "error_code": CorrectnessErrorCode.NO_CORRECT_OPTION.value,
                    "message": "explanation admits a non-option result",
                    "evidence": evidence,
                }
            return {
                "status": "unsupported",
                "error_code": CorrectnessErrorCode.UNSUPPORTED_CORRECTNESS.value,
                "message": extracted.reason or "no_reliable_value",
                "evidence": evidence,
            }
        solved = extracted.value
        display = extracted.display or str(extracted.value)
        source = extracted.source

    evidence["solved_value"] = display
    evidence["extract_source"] = source
    if confession:
        evidence["confession"] = True

    matching, parseable = _match_options(solved, inp.choices or {})
    evidence["matching_keys"] = matching

    if parseable == 0:
        return {
            "status": "unsupported",
            "error_code": CorrectnessErrorCode.UNSUPPORTED_CORRECTNESS.value,
            "message": "options_unparsed",
            "evidence": evidence,
        }

    if len(matching) == 0:
        return {
            "status": "fail",
            "error_code": CorrectnessErrorCode.NO_CORRECT_OPTION.value,
            "message": f"solved={evidence['solved_value']} matches no option",
            "evidence": evidence,
        }
    if len(matching) > 1:
        return {
            "status": "fail",
            "error_code": CorrectnessErrorCode.MULTIPLE_CORRECT_OPTIONS.value,
            "message": f"solved={evidence['solved_value']} matches {matching}",
            "evidence": evidence,
        }

    only = matching[0]
    if claimed and only != claimed:
        return {
            "status": "fail",
            "error_code": CorrectnessErrorCode.ANSWER_KEY_MISMATCH.value,
            "message": f"claimed={claimed},solved={evidence['solved_value']},matching={only}",
            "evidence": evidence,
        }
    return {
        "status": "pass",
        "error_code": None,
        "message": None,
        "evidence": evidence,
    }
