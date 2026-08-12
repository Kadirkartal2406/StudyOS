"""Linear relation option / explanation parsing — conservative subset."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.services.correctness.constants import MAX_EXPR_LEN
from app.services.correctness.math_parser import ParseResult, _latex_to_plain, values_equal

# Prose / non-math options — never force-parse.
_PROSE_RE = re.compile(
    r"[çğıöşüÇĞİÖŞÜ]|"
    r"\b(ve|ile|için|olan|hangisi|aşağıdak|göre|birim|"
    r"metin|doğru|yanlış|öncelikle|according|which|following)\b",
    re.IGNORECASE,
)

# Single-equation linear relation candidates (option-sized).
_OPTION_REL_RE = re.compile(
    r"^\s*"
    r"((?:\d+)?(?:\\frac\{[^{}]+\}\{[^{}]+\})?[a-zA-Z](?:\s*[·*⋅]?\s*[a-zA-Z])?)"
    r"\s*=\s*"
    r"((?:\\frac\{[^{}]+\}\{[^{}]+\}|\([^)]+\)|\d+/\d+|\d*)\s*"
    r"[a-zA-Z](?:\s*[·*⋅]?\s*[a-zA-Z])?)"
    r"\s*$"
)

# Explanation: scan for short relation snippets.
_TEXT_REL_RE = re.compile(
    r"(?<![A-Za-z0-9_/])"
    r"("
    r"(?:\d+)?(?:\\frac\{[^{}]+\}\{[^{}]+\})?[a-zA-Z](?:\s*[·*⋅]?\s*[a-zA-Z])?"
    r"\s*=\s*"
    r"(?:\\frac\{[^{}]+\}\{[^{}]+\}|\([^)]+\)|\d+/\d+|\d*)\s*"
    r"[a-zA-Z](?:\s*[·*⋅]?\s*[a-zA-Z])?"
    r")"
    r"(?![A-Za-z0-9])"
)

_SIDE_OK_RE = re.compile(r"^[0-9a-zA-Z_+\-*/^().,\s·*⋅]+$")


@dataclass(frozen=True)
class RelationForm:
    """Homogeneous linear relation c1*v1 + c2*v2 = 0 (ratio form)."""

    v1: str
    v2: str
    c1: Any
    c2: Any
    raw: str

    @property
    def ratio_v1_over_v2(self) -> Any:
        """v1/v2 when c1*v1 + c2*v2 = 0 ⇒ v1/v2 = -c2/c1."""
        return -self.c2 / self.c1


def _looks_like_prose(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if len(t) > 48:
        return True
    if _PROSE_RE.search(t):
        return True
    # Multiple words without '=' → not a relation option.
    if "=" not in t and len(t.split()) >= 3:
        return True
    return False


def _parse_side(side: str) -> ParseResult:
    raw = (side or "").strip()
    if not raw or len(raw) > MAX_EXPR_LEN:
        return ParseResult(ok=False, raw=raw, reason="side_bad")
    plain = _latex_to_plain(raw)
    if not plain or not _SIDE_OK_RE.match(plain.replace("·", "*").replace("⋅", "*")):
        return ParseResult(ok=False, raw=raw, reason="side_charset")
    plain = plain.replace("·", "*").replace("⋅", "*")
    # Reuse parse_math via a thin import cycle-safe path: inline sympy parse like math_parser.
    from app.services.correctness.math_parser import parse_math

    # parse_math denies '=' already stripped; side has no '='.
    return parse_math(plain)


def _to_relation_form(lhs: Any, rhs: Any, raw: str) -> RelationForm | None:
    try:
        import sympy
    except ImportError:
        return None
    try:
        diff = sympy.expand(lhs - rhs)
        if diff == 0:
            return None
        # Drop overall numeric content; require homogeneous (no constant term).
        syms = list(diff.free_symbols)
        if not syms:
            return None
        if diff.subs({s: 0 for s in syms}) != 0:
            return None

        # Factor out common symbols (e.g. k*(7*y - 9*x)).
        fac = sympy.factor(diff)
        target = fac
        if fac.is_Mul:
            two_var_parts = [
                p
                for p in fac.args
                if getattr(p, "free_symbols", None) and len(p.free_symbols) == 2
            ]
            if len(two_var_parts) == 1:
                target = two_var_parts[0]
            elif not two_var_parts:
                # Maybe fac itself has 2 symbols after cancelling 1-symbol factors.
                core = fac
                for p in list(fac.args):
                    if len(getattr(p, "free_symbols", set())) == 1 and p.is_symbol:
                        core = sympy.simplify(core / p)
                if len(core.free_symbols) == 2:
                    target = core

        syms2 = sorted(target.free_symbols, key=str)
        if len(syms2) != 2:
            # Direct two-symbol diff without factoring.
            syms2 = sorted(diff.free_symbols, key=str)
            if len(syms2) != 2:
                return None
            target = diff

        v1, v2 = str(syms2[0]), str(syms2[1])
        # Coefficients of linear form.
        poly = sympy.Poly(sympy.expand(target), *syms2)
        if poly.total_degree() != 1:
            return None
        c1 = poly.coeff_monomial(syms2[0])
        c2 = poly.coeff_monomial(syms2[1])
        if c1 == 0 and c2 == 0:
            return None
        if c1 == 0 or c2 == 0:
            # Degenerate axis relation — still a valid ratio (0 or inf); skip for safety.
            return None
        return RelationForm(v1=v1, v2=v2, c1=c1, c2=c2, raw=raw)
    except Exception:
        return None


def parse_linear_relation(text: str) -> RelationForm | None:
    """Parse option-sized linear relations. None = unsupported (not FAIL)."""
    raw = (text or "").strip()
    if not raw or _looks_like_prose(raw):
        return None
    if len(raw) > MAX_EXPR_LEN:
        return None
    if raw.count("=") != 1:
        return None
    m = _OPTION_REL_RE.match(raw.replace("−", "-"))
    if not m:
        # Fallback: split once on '=' if both sides look math-ish.
        left, right = raw.split("=", 1)
        if _looks_like_prose(left) or _looks_like_prose(right):
            return None
    else:
        left, right = m.group(1), m.group(2)

    lp, rp = _parse_side(left), _parse_side(right)
    if not lp.ok or not rp.ok:
        return None
    return _to_relation_form(lp.expr, rp.expr, raw)


def relations_equal(a: RelationForm, b: RelationForm) -> bool | None:
    """True/False if same two-var ratio; None if incomparable."""
    vars_a = {a.v1, a.v2}
    vars_b = {b.v1, b.v2}
    if vars_a != vars_b:
        return None
    try:
        import sympy

        def ratio_for(form: RelationForm, num: str, den: str) -> Any:
            # c_num*num + c_den*den = 0 ⇒ num/den = -c_den/c_num
            if form.v1 == num and form.v2 == den:
                c_num, c_den = form.c1, form.c2
            elif form.v1 == den and form.v2 == num:
                c_num, c_den = form.c2, form.c1
            else:
                raise ValueError("var mismatch")
            return sympy.simplify(-c_den / c_num)

        v_num, v_den = sorted(vars_a)
        ra = ratio_for(a, v_num, v_den)
        rb = ratio_for(b, v_num, v_den)
        return values_equal(ra, rb)
    except Exception:
        return None


def extract_relations_from_text(text: str) -> list[RelationForm]:
    """Collect parseable homogeneous linear relations from explanation prose."""
    found: list[RelationForm] = []
    seen: set[str] = set()
    blob = (text or "").replace("−", "-")
    for m in _TEXT_REL_RE.finditer(blob):
        snippet = m.group(1).strip()
        key = re.sub(r"\s+", "", snippet.lower())
        if key in seen:
            continue
        seen.add(key)
        rel = parse_linear_relation(snippet)
        if rel is not None:
            found.append(rel)
    return found


def parse_option_value(text: str) -> ParseResult:
    """Parse a choice: relation (expr=RelationForm) or numeric/algebraic math.

    Unparseable / prose → ok=False (UNSUPPORTED path). Never invent.
    """
    raw = (text or "").strip()
    if not raw:
        return ParseResult(ok=False, raw=raw, reason="empty")
    if _looks_like_prose(raw) and "=" not in raw:
        return ParseResult(ok=False, raw=raw, reason="prose")

    rel = parse_linear_relation(raw)
    if rel is not None:
        return ParseResult(ok=True, expr=rel, raw=raw)

    if "=" in raw:
        # Equation that is not a safe linear relation — unsupported.
        return ParseResult(ok=False, raw=raw, reason="non_linear_equation")

    from app.services.correctness.math_parser import parse_math

    return parse_math(raw)
