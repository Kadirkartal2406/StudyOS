"""Solution vs stem consistency — conservative, high-precision signals only."""

from __future__ import annotations

import re
from typing import Any

from app.services.correctness.math_parser import parse_math, values_equal
from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
)

_ASSUME_PHRASE_RE = re.compile(
    r"(varsayal[ıi]m|kabul edelim|oldu[gğ]unu varsayal[ıi]m|"
    r"varsay[ıi]l[ıi]rsa|oldu[gğ]u varsay[ıi]l[ıi]r)",
    re.IGNORECASE,
)
_ASSUME_NUMBER_BEFORE_RE = re.compile(
    r"(\d+(?:[.,]\d+)?)\s+(?:\w+\s+){0,4}(?:oldu[gğ]u\s+)?varsay",
    re.IGNORECASE,
)
_ASSUME_NUMBER_AFTER_RE = re.compile(
    r"(?:varsayal[ıi]m|kabul edelim|alal[ıi]m)\s*[:,]?\s*"
    r".{0,40}?(\d+(?:[.,]\d+)?)",
    re.IGNORECASE | re.DOTALL,
)
_LHS_HEAD_RE = re.compile(
    r"(f'\s*\(\s*[^)]+\s*\)|f\s*\(\s*[^)]+\s*\)|[A-Za-z]'?\s*\(\s*[^)]+\s*\))"
    r"\s*=\s*",
    re.IGNORECASE,
)
_RHS_STOP_RE = re.compile(
    r"\s*=\s*0\b|"
    r"\s+(?:denklemi|alındığında|olmalıdır|olur|ilişkisi|olduğuna|verilmekte|kök)|"
    r"[.;]|"
    r"(?=\s*[A-Za-z]'?\s*\([^)]*\)\s*=)",
    re.IGNORECASE,
)
_NUMBER_RE = re.compile(r"(?<![A-Za-z])(\d+(?:[.,]\d+)?)")

# Operator / formula rewrite: a_n = n^2 - spf(...) rewritten as n^2 + spf(...)
_SPF_LIKE = (
    r"(?:en\s*küçük\s*asal\s*bölen|enk[uü][cç][uü]k\s*asal|"
    r"\\text\{\s*en\s*küçük\s*asal\s*bölen\s*\}|spf)"
)
_STEM_SQ_MINUS_SPF = re.compile(
    rf"(?:a_n\s*=\s*)?(?:n\^2|n\*\*2)\s*-\s*.{{0,60}}{_SPF_LIKE}",
    re.IGNORECASE,
)
_SOL_SQ_PLUS_SPF = re.compile(
    rf"(?:(?:\d+|n)\^2|(?:\d+|n)\*\*2)\s*\+\s*.{{0,60}}{_SPF_LIKE}",
    re.IGNORECASE,
)
_SIGN_FLIP_NOTE = re.compile(
    r"(?:eksi\s+işareti\s+art[ıi]|art[ıi]\s+olarak\s+değerlendir|"
    r"eksiyi\s+art[ıi]|işareti\s+değiştir)",
    re.IGNORECASE,
)


def _norm_num(token: str) -> str:
    t = token.replace(",", ".")
    try:
        f = float(t)
        if f.is_integer():
            return str(int(f))
        return t
    except ValueError:
        return t


def _numbers_in(text: str) -> set[str]:
    return {_norm_num(m.group(1)) for m in _NUMBER_RE.finditer(text or "")}


def _extract_lhs_equations(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    blob = text or ""
    for m in _LHS_HEAD_RE.finditer(blob):
        lhs = re.sub(r"\s+", "", m.group(1).lower())
        rest = blob[m.end() :]
        stop = _RHS_STOP_RE.search(rest)
        rhs = rest[: stop.start() if stop else len(rest)]
        rhs = rhs.replace("$", "").strip().rstrip(".")
        rhs = re.sub(r"\s+", " ", rhs)
        if not rhs or len(rhs) > 80:
            continue
        found.setdefault(lhs, []).append(rhs)
    return found


def _rhs_equivalent(a: str, b: str) -> bool | None:
    pa, pb = parse_math(a), parse_math(b)
    if not pa.ok or not pb.ok:
        return None
    try:
        import sympy

        diff = sympy.simplify(sympy.expand(pa.expr - pb.expr))
        if diff == 0:
            return True
        if getattr(diff, "is_zero", None) is True:
            return True
        if diff.free_symbols or diff != 0:
            return False
        return True
    except Exception:
        eq = values_equal(pa.expr, pb.expr)
        return eq


def _operator_rewrite(stem: str, expl: str) -> dict[str, Any] | None:
    """Detect stem n^2 - spf rewritten as n^2 + spf in the solution."""
    if not _STEM_SQ_MINUS_SPF.search(stem or ""):
        return None
    sol_plus = bool(_SOL_SQ_PLUS_SPF.search(expl or ""))
    if not sol_plus:
        return None
    return {
        "kind": "sign_flip_spf",
        "stem_op": "-",
        "solution_op": "+",
        "flip_note": bool(_SIGN_FLIP_NOTE.search(expl or "")),
    }


def check_solution_consistency(inp: CorrectnessInput) -> CorrectnessCheck:
    stem = inp.stem or ""
    expl = inp.explanation or ""
    evidence: dict[str, Any] = {
        "stem_constraints": [],
        "solution_constraints": [],
        "unexpected_literals": [],
        "changed_equations": [],
        "operator_rewrite": None,
    }
    if not expl.strip():
        return CorrectnessCheck(
            name="solution_consistency",
            status="unsupported",
            error_code=CorrectnessErrorCode.UNSUPPORTED_SOLUTION_CONSISTENCY.value,
            message="no_explanation",
            evidence=evidence,
        )

    rewrite = _operator_rewrite(stem, expl)
    if rewrite is not None:
        evidence["operator_rewrite"] = rewrite
        return CorrectnessCheck(
            name="solution_consistency",
            status="fail",
            error_code=CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value,
            message="solution_stem_mismatch:operator_rewrite",
            evidence=evidence,
        )

    stem_eqs = _extract_lhs_equations(stem)
    sol_eqs = _extract_lhs_equations(expl)
    evidence["stem_constraints"] = [f"{k}={v}" for k, vs in stem_eqs.items() for v in vs]
    evidence["solution_constraints"] = [f"{k}={v}" for k, vs in sol_eqs.items() for v in vs]

    changed: list[dict[str, str]] = []
    for lhs, stem_rhss in stem_eqs.items():
        stem_rhs = stem_rhss[0]
        for sol_rhs in sol_eqs.get(lhs, []):
            eq = _rhs_equivalent(stem_rhs, sol_rhs)
            if eq is False:
                changed.append({"lhs": lhs, "stem": stem_rhs, "solution": sol_rhs})
    evidence["changed_equations"] = changed
    if changed:
        return CorrectnessCheck(
            name="solution_consistency",
            status="fail",
            error_code=CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value,
            message="solution_stem_mismatch:changed_equation",
            evidence=evidence,
        )

    stem_nums = _numbers_in(stem)
    stem_nums |= _numbers_in(" ".join(inp.choices.values()) if inp.choices else "")
    unexpected: list[str] = []
    if _ASSUME_PHRASE_RE.search(expl):
        for rx in (_ASSUME_NUMBER_BEFORE_RE, _ASSUME_NUMBER_AFTER_RE):
            for m in rx.finditer(expl):
                n = _norm_num(m.group(1))
                if n not in stem_nums:
                    unexpected.append(n)
    evidence["unexpected_literals"] = unexpected
    if unexpected:
        return CorrectnessCheck(
            name="solution_consistency",
            status="fail",
            error_code=CorrectnessErrorCode.SOLUTION_STEM_MISMATCH.value,
            message="solution_stem_mismatch:unexpected_assumption",
            evidence=evidence,
        )

    return CorrectnessCheck(
        name="solution_consistency",
        status="pass",
        evidence=evidence,
    )
