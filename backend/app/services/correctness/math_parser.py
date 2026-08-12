"""Conservative math parser — unsupported beats a wrong parse."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.services.correctness.constants import ABS_TOL, MAX_EXPR_LEN, REL_TOL

_DENY_RE = re.compile(
    r"(?:\\int|\bintegral\b|\blim\b|\bsin\b|\bcos\b|\btan\b|\bcot\b|\bsec\b|"
    r"\bcsc\b|\blog\b|\bln\b|\bsum\b|\bprod\b|\bmatrix\b|\bpiecewise\b|"
    r"\\sum|\\prod|\\lim|\\sin|\\cos|\\tan|\\log|\\ln|\\int|"
    r"d/dx|partial|infty|infinity)",
    re.IGNORECASE,
)

_FRAC_RE = re.compile(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}")
_SQRT_BRACE_RE = re.compile(r"\\sqrt\s*\{([^{}]+)\}")
_SQRT_BARE_RE = re.compile(r"\\sqrt\s*([0-9a-zA-Z]+)")
_ALLOWED_AFTER_RE = re.compile(r"^[0-9a-zA-Z_+\-*/^().,\s]+$")
_IMPLICIT_NUM_IDENT = re.compile(r"(\d)([a-zA-Z])")
_IMPLICIT_RPAREN_LPAREN = re.compile(r"\)\(")
_IMPLICIT_RPAREN_IDENT = re.compile(r"\)([a-zA-Z])")
_UNICODE_SQRT = "√"


@dataclass(frozen=True)
class ParseResult:
    ok: bool
    expr: Any = None
    raw: str = ""
    reason: str | None = None

    @property
    def unsupported(self) -> bool:
        return not self.ok


def _latex_to_plain(text: str) -> str:
    s = (text or "").strip()
    s = s.replace("$", "")
    s = s.replace(r"\left", "").replace(r"\right", "")
    s = s.replace(r"\cdot", "*").replace(r"\times", "*")
    s = s.replace("×", "*").replace("·", "*")
    s = s.replace("−", "-").replace("–", "-")
    s = s.replace("²", "**2").replace("³", "**3")
    s = s.replace(_UNICODE_SQRT, "sqrt")
    # Nested-ish frac: apply a few times for simple nesting
    for _ in range(4):
        nxt = _FRAC_RE.sub(r"(\1)/(\2)", s)
        if nxt == s:
            break
        s = nxt
    s = _SQRT_BRACE_RE.sub(r"sqrt(\1)", s)
    s = _SQRT_BARE_RE.sub(r"sqrt(\1)", s)
    s = s.replace(r"\{", "").replace(r"\}", "")
    s = s.replace("{", "(").replace("}", ")")
    s = s.replace(r"\ ", " ")
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = s.replace("^", "**")
    s = re.sub(r"\s+", "", s)
    # 2sqrt(34) → 2*sqrt(34)
    s = re.sub(r"(\d)sqrt", r"\1*sqrt", s)
    s = re.sub(r"sqrt(\d)", r"sqrt(\1)", s)
    s = re.sub(r"(\d)\(", r"\1*(", s)
    s = _IMPLICIT_NUM_IDENT.sub(r"\1*\2", s)
    s = _IMPLICIT_RPAREN_LPAREN.sub(")*(", s)
    s = _IMPLICIT_RPAREN_IDENT.sub(r")*\1", s)
    # Single-letter implicit mul: x( → x*(  (does not split 'sqrt')
    s = re.sub(r"(?<![a-zA-Z])([a-zA-Z])\(", r"\1*(", s)
    return s


def parse_math(text: str) -> ParseResult:
    """Parse a short arithmetic/algebra snippet. Never force a parse."""
    raw = (text or "").strip()
    if not raw:
        return ParseResult(ok=False, raw=raw, reason="empty")
    if len(raw) > MAX_EXPR_LEN:
        return ParseResult(ok=False, raw=raw, reason="too_long")
    if _DENY_RE.search(raw):
        return ParseResult(ok=False, raw=raw, reason="denied_construct")

    plain = _latex_to_plain(raw)
    if not plain:
        return ParseResult(ok=False, raw=raw, reason="empty_after_latex")
    if len(plain) > MAX_EXPR_LEN:
        return ParseResult(ok=False, raw=raw, reason="too_long")
    if not _ALLOWED_AFTER_RE.match(plain):
        return ParseResult(ok=False, raw=raw, reason="charset")

    try:
        import sympy
        from sympy.parsing.sympy_parser import (
            convert_xor,
            implicit_multiplication_application,
            parse_expr,
            standard_transformations,
        )
    except ImportError:
        return ParseResult(ok=False, raw=raw, reason="sympy_missing")

    local_dict = {"sqrt": sympy.sqrt}
    transformations = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )
    try:
        expr = parse_expr(
            plain,
            local_dict=local_dict,
            transformations=transformations,
            evaluate=False,
        )
    except Exception:
        return ParseResult(ok=False, raw=raw, reason="parse_error")

    if expr is None:
        return ParseResult(ok=False, raw=raw, reason="parse_error")

    try:
        for sym in expr.free_symbols:
            name = str(sym)
            if not re.fullmatch(r"[a-zA-Z]", name):
                return ParseResult(ok=False, raw=raw, reason="unexpected_symbol")
    except Exception:
        return ParseResult(ok=False, raw=raw, reason="symbol_inspect")

    return ParseResult(ok=True, expr=expr, raw=raw)


def values_equal(left: Any, right: Any) -> bool | None:
    """True/False if comparable; None if comparison is unsupported."""
    try:
        import sympy
    except ImportError:
        return None
    try:
        diff = sympy.simplify(left - right)
        if diff == 0:
            return True
        if getattr(diff, "is_zero", None) is True:
            return True
        num = complex(diff.evalf())
        mag = abs(num)
        scale = max(abs(complex(sympy.N(left))), abs(complex(sympy.N(right))), 1.0)
        return mag <= max(ABS_TOL, REL_TOL * scale)
    except Exception:
        return None
