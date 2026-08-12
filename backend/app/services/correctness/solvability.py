"""Stem solvability / sufficient information — conservative sympy + patterns."""

from __future__ import annotations

import re
from typing import Any

from app.services.correctness.constants import is_numeric_subject
from app.services.correctness.math_parser import parse_math
from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
)

_UNIT_PRICE_RE = re.compile(
    r"tanesi ka[cç]|birim fiyat|ka[cç] TL.?den satar",
    re.IGNORECASE,
)
_CONTAINER_RE = re.compile(r"\bkoli\b|\bpaket\b|\bkutu\b", re.IGNORECASE)
_ITEM_COUNT_RE = re.compile(
    r"\d+\s*(?:adet|tane|defter|kalem|ki[sş]i)|"
    r"kolide\s+\d+|\d+\s*'?l[ıi]k\s+koli",
    re.IGNORECASE,
)
_DESTINATION_RE = re.compile(
    r"gidece[gğ]i yer|var[ıi][sş] noktas[ıi]|hedefe ula[sş]",
    re.IGNORECASE,
)
_SPEED_KM_RE = re.compile(
    r"(?:saatte|h[ıi]z(?:la|ı)?)\s+\d+\s*(?:km|kilometre)|"
    r"\d+\s*(?:km|kilometre)\s+h[ıi]z",
    re.IGNORECASE,
)
_DISTANCE_KM_RE = re.compile(
    r"\d+\s*(?:km|kilometre)\s+"
    r"(?:uzak|mesafe|yol|uzunlu[gğ]|aral[ıi][kğ])|"
    r"(?:uzakl[ıi]k|mesafe|yol)\s+\d+\s*(?:km|kilometre)",
    re.IGNORECASE,
)
_SIMPLE_ARITH_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*([+\-×x*])\s*(\d+(?:[.,]\d+)?)",
)
_EQ_LINE_RE = re.compile(r"([^.\n]{2,60}=\s*[^.\n]{1,40})")

# Narrow template: given ∫ f = number, ask an integral involving f' without f values.
_INT_F_GIVEN_RE = re.compile(
    r"(\\int\s*(?:_\{[^}]+\}\s*(?:\^\{[^}]+\})?|\_{[^}]+}\s*\^{[^}]+})\s*"
    r"f\s*\(\s*[^)]+\s*\)[^={}]*|\\int\s*f\s*\([^)]*\)[^={}]*)"
    r"\s*=\s*-?\d+",
    re.IGNORECASE,
)
_INT_F_GIVEN_LOOSE_RE = re.compile(
    r"\\int[^=\n]{0,80}f\s*\([^)]*\)[^=\n]{0,40}=\s*-?\d+",
    re.IGNORECASE,
)
_ASKS_F_PRIME_INT_RE = re.compile(
    r"\\int[^=\n]{0,100}f'\s*\(|\\int[^=\n]{0,100}f\\'\s*\(",
    re.IGNORECASE,
)
_HAS_F_POINT_VALUE_RE = re.compile(
    r"f\s*\(\s*-?\d+\s*\)\s*=\s*-?\d+|f\s*\(\s*[a-zA-Z]\s*\)\s*=\s*-?\d+",
    re.IGNORECASE,
)


def _insufficient_integral_fprime(stem: str) -> bool:
    """True when ∫f is given numerically but the question asks ∫…f'… without f(a)."""
    given = _INT_F_GIVEN_RE.search(stem) or _INT_F_GIVEN_LOOSE_RE.search(stem)
    if not given:
        return False
    if not _ASKS_F_PRIME_INT_RE.search(stem):
        return False
    if _HAS_F_POINT_VALUE_RE.search(stem):
        return False
    return True


def check_solvability(inp: CorrectnessInput) -> CorrectnessCheck:
    evidence: dict[str, Any] = {
        "pattern": None,
        "unknowns": [],
        "equations": [],
        "solution_kind": None,
    }
    if not is_numeric_subject(inp.subject_code, inp.exam):
        return CorrectnessCheck(
            name="solvability",
            status="unsupported",
            error_code=CorrectnessErrorCode.UNSOLVABLE.value,
            message="non_numeric_subject",
            evidence=evidence,
        )

    stem = inp.stem or ""

    if _insufficient_integral_fprime(stem):
        evidence["pattern"] = "integral_f_given_asks_fprime"
        evidence["solution_kind"] = "insufficient"
        return CorrectnessCheck(
            name="solvability",
            status="fail",
            error_code=CorrectnessErrorCode.UNSOLVABLE.value,
            message="unsolvable:insufficient_information",
            evidence=evidence,
        )

    if _UNIT_PRICE_RE.search(stem) and _CONTAINER_RE.search(stem) and not _ITEM_COUNT_RE.search(stem):
        evidence["pattern"] = "unit_price_unknown_count"
        evidence["solution_kind"] = "insufficient"
        return CorrectnessCheck(
            name="solvability",
            status="fail",
            error_code=CorrectnessErrorCode.UNSOLVABLE.value,
            message="unsolvable:insufficient_information",
            evidence=evidence,
        )

    if _DESTINATION_RE.search(stem) and not _DISTANCE_KM_RE.search(stem):
        # Speeds like "saatte 70 km" do not count as a destination distance.
        evidence["pattern"] = "motion_missing_destination"
        evidence["solution_kind"] = "insufficient"
        return CorrectnessCheck(
            name="solvability",
            status="fail",
            error_code=CorrectnessErrorCode.UNSOLVABLE.value,
            message="unsolvable:insufficient_information",
            evidence=evidence,
        )

    arith = _SIMPLE_ARITH_RE.search(stem)
    if arith:
        op = arith.group(2)
        op_map = {"+": "+", "-": "-", "*": "*", "×": "*", "x": "*"}
        expr = f"{arith.group(1).replace(',', '.')}{op_map.get(op, '+')}{arith.group(3).replace(',', '.')}"
        parsed = parse_math(expr)
        if parsed.ok:
            try:
                symbols = list(parsed.expr.free_symbols)
            except Exception:
                symbols = ["?"]
            if not symbols:
                evidence["pattern"] = "closed_arithmetic"
                evidence["solution_kind"] = "unique"
                evidence["equations"] = [expr]
                return CorrectnessCheck(
                    name="solvability",
                    status="pass",
                    evidence=evidence,
                )

    eq_lines = [m.group(1).strip() for m in _EQ_LINE_RE.finditer(stem)]
    parsed_eqs = []
    for line in eq_lines[:4]:
        if line.count("=") != 1:
            continue
        left, right = line.split("=", 1)
        lp, rp = parse_math(left), parse_math(right)
        if lp.ok and rp.ok:
            parsed_eqs.append((lp.expr, rp.expr, line))
    if parsed_eqs:
        try:
            import sympy

            diffs = [sympy.Eq(a, b) for a, b, _ in parsed_eqs]
            syms = sorted({s for eq in diffs for s in eq.free_symbols}, key=str)
            evidence["equations"] = [t for _, _, t in parsed_eqs]
            evidence["unknowns"] = [str(s) for s in syms]
            if not syms:
                evidence["solution_kind"] = "unique"
                return CorrectnessCheck(name="solvability", status="pass", evidence=evidence)
            sols = sympy.solve(diffs, syms, dict=True)
            if sols is None:
                evidence["solution_kind"] = "unsupported"
            elif len(sols) == 1:
                evidence["solution_kind"] = "unique"
                return CorrectnessCheck(name="solvability", status="pass", evidence=evidence)
            elif len(sols) == 0:
                evidence["solution_kind"] = "zero"
                return CorrectnessCheck(
                    name="solvability",
                    status="fail",
                    error_code=CorrectnessErrorCode.UNSOLVABLE.value,
                    message="unsolvable:zero_solutions",
                    evidence=evidence,
                )
            else:
                evidence["solution_kind"] = "multiple"
                return CorrectnessCheck(
                    name="solvability",
                    status="fail",
                    error_code=CorrectnessErrorCode.UNSOLVABLE.value,
                    message="unsolvable:non_unique",
                    evidence=evidence,
                )
        except Exception:
            evidence["solution_kind"] = "unsupported"

    evidence["solution_kind"] = "unsupported"
    return CorrectnessCheck(
        name="solvability",
        status="unsupported",
        error_code=CorrectnessErrorCode.UNSOLVABLE.value,
        message="unsolvable:unsupported_parse",
        evidence=evidence,
    )
