"""Narrow polynomial vs |x| area template — SymPy CAS, fail-open to unsupported."""

from __future__ import annotations

import re
from typing import Any

from app.services.correctness.math_parser import ParseResult, parse_math

# Canonical: f(x) = <quadratic/linear poly> and g(x) = |x|
_F_DEF_RE = re.compile(
    r"f\s*\(\s*x\s*\)\s*=\s*([0-9a-zA-Z+\-*/^\\\s{}]+?)(?=\s*(?:parabol|fonksiyon|ile|ve|,|\.|$))",
    re.IGNORECASE,
)
_G_ABS_RE = re.compile(
    r"g\s*\(\s*x\s*\)\s*=\s*\|x\|"
    r"|g\s*\(\s*x\s*\)\s*=\s*\\left\|\s*x\s*\\right\|"
    r"|g\s*\(\s*x\s*\)\s*=\s*\\lvert\s*x\s*\\rvert"
    r"|g\s*\(\s*x\s*\)\s*=\s*\\abs\s*\(\s*x\s*\)",
    re.IGNORECASE,
)
_POLY_OK_RE = re.compile(
    r"^[0-9xX+\-*/^\\\s{}().]+$",
)


def try_poly_abs_area(stem: str) -> ParseResult:
    """Compute area between poly f(x) and |x| when the stem matches the template.

    On any doubt → ok=False (UNSUPPORTED). Never invent.
    """
    text = (stem or "").strip()
    if not text:
        return ParseResult(ok=False, raw=text, reason="empty")
    if not _G_ABS_RE.search(text):
        return ParseResult(ok=False, raw=text, reason="no_abs_g")
    # Prefer explicit f(x)= ...
    fm = _F_DEF_RE.search(text)
    if not fm:
        return ParseResult(ok=False, raw=text, reason="no_f_def")
    f_raw = fm.group(1).strip().rstrip(".")
    f_raw = re.sub(r"\s*(parabolü|parabolu|fonksiyonu)\s*$", "", f_raw, flags=re.I)
    f_raw = f_raw.strip()
    if not f_raw or not _POLY_OK_RE.match(f_raw.replace(" ", "")):
        return ParseResult(ok=False, raw=f_raw, reason="f_not_polyish")
    # Deny non-poly constructs inside f.
    if re.search(r"sin|cos|tan|log|ln|int|sqrt|\|", f_raw, re.I):
        return ParseResult(ok=False, raw=f_raw, reason="f_denied")

    parsed = parse_math(f_raw)
    if not parsed.ok:
        return ParseResult(ok=False, raw=f_raw, reason=parsed.reason or "f_unparsed")

    try:
        import sympy

        x = sympy.symbols("x")
        f_expr = parsed.expr
        # Must be univariate in x only (or constant).
        syms = {str(s) for s in f_expr.free_symbols}
        if syms - {"x"}:
            return ParseResult(ok=False, raw=f_raw, reason="extra_symbols")
        f_expr = f_expr.subs({s: x for s in f_expr.free_symbols})

        # Intersection for x >= 0: f(x) = x
        eq = sympy.Eq(f_expr, x)
        roots = sympy.solve(eq, x)
        pos = []
        for r in roots:
            try:
                rv = complex(r.evalf())
                if abs(rv.imag) > 1e-9:
                    continue
                if rv.real > 1e-12:
                    pos.append(sympy.simplify(r))
            except Exception:
                continue
        if len(pos) != 1:
            return ParseResult(ok=False, raw=text, reason="intersection_not_unique")
        x0 = pos[0]

        # Area = 2 * ∫_0^{x0} (f(x) - x) dx  (even: f even-ish + |x|)
        # Require f(x) - x >= 0 on (0, x0) at midpoint.
        mid = x0 / 2
        gap = sympy.simplify(f_expr - x)
        try:
            mid_val = complex(gap.subs(x, mid).evalf())
            if mid_val.real <= 0:
                return ParseResult(ok=False, raw=text, reason="non_positive_region")
        except Exception:
            return ParseResult(ok=False, raw=text, reason="region_check_failed")

        area = sympy.simplify(2 * sympy.integrate(gap, (x, 0, x0)))
        if area.free_symbols:
            return ParseResult(ok=False, raw=text, reason="area_symbolic")
        if complex(area.evalf()).real <= 0:
            return ParseResult(ok=False, raw=text, reason="non_positive_area")
        return ParseResult(ok=True, expr=area, raw=f"area:{f_raw}_vs_|x|")
    except Exception:
        return ParseResult(ok=False, raw=text, reason="cas_error")


def area_template_evidence(stem: str) -> dict[str, Any]:
    r = try_poly_abs_area(stem)
    return {
        "ok": r.ok,
        "reason": r.reason,
        "value": str(r.expr) if r.ok else None,
    }
