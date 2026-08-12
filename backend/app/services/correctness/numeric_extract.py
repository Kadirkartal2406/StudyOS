"""Extract a numeric conclusion from an explanation — conservative."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from app.services.correctness.math_parser import ParseResult, parse_math

# Model admits the computed value is not among the options.
_CONFESSION_RE = re.compile(
    r"(en yakın|tam sayı çıkmamaktadır|seçeneklerde yok|"
    r"uyarlanmıştır|eşdeğer kurguya)",
    re.IGNORECASE,
)

# Phase 2 signals — do NOT treat as Phase 1 answer failure.
_PHASE2_STEM_REWRITE_RE = re.compile(
    r"(düzeltilmelidir|varsayalım|varsayılırsa)",
    re.IGNORECASE,
)

_SONUC_RE = re.compile(
    r"(?:sonuç|doğru cevap|doğru seçenek)\s*[:：]?\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)
_X_EQ_RE = re.compile(
    r"(?<![A-Za-z])x\s*=\s*(\\frac\{[^{}]+\}\{[^{}]+\}|-?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?)"
    r"(?!\s*için)",
    re.IGNORECASE,
)
_LAST_EQ_VALUE_RE = re.compile(
    r"=\s*(\\frac\{[^{}]+\}\{[^{}]+\}|-?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?)\s*\.?\s*$"
)
_LINEAR_EQ_RE = re.compile(
    r"([^.\n]{3,80}=\s*[^.\n]{1,40})",
)


@dataclass(frozen=True)
class ExtractResult:
    ok: bool
    value: Any = None
    display: str | None = None
    source: str | None = None
    confession: bool = False
    reason: str | None = None


def has_answer_confession(explanation: str | None) -> bool:
    text = explanation or ""
    if _PHASE2_STEM_REWRITE_RE.search(text):
        # Rewrite/assumption language is Phase 2; do not use as Phase 1 FAIL.
        pass
    return bool(_CONFESSION_RE.search(text))


def _parse_value_token(token: str) -> ParseResult:
    t = (token or "").strip().rstrip(".").replace(",", ".")
    t = t.replace("×", "*")
    return parse_math(t)


def _try_solve_linear(equation: str) -> ParseResult:
    if equation.count("=") != 1:
        return ParseResult(ok=False, raw=equation, reason="not_single_eq")
    left, right = equation.split("=", 1)
    # Skip "şık" / "cevap" prose equations
    blob = (left + right).lower()
    if any(w in blob for w in ("şık", "cevap", "seçenek", "doğru")):
        return ParseResult(ok=False, raw=equation, reason="prose")
    lp, rp = parse_math(left), parse_math(right)
    if not lp.ok or not rp.ok:
        return ParseResult(ok=False, raw=equation, reason="side_unparsed")
    try:
        import sympy

        diff = sympy.simplify(lp.expr - rp.expr)
        symbols = list(diff.free_symbols)
        if len(symbols) != 1:
            return ParseResult(ok=False, raw=equation, reason="not_one_unknown")
        sols = sympy.solve(diff, symbols[0])
        if len(sols) != 1:
            return ParseResult(ok=False, raw=equation, reason="not_unique")
        return ParseResult(ok=True, expr=sols[0], raw=equation)
    except Exception:
        return ParseResult(ok=False, raw=equation, reason="solve_error")


def extract_numeric_answer(explanation: str | None) -> ExtractResult:
    """Return a single numeric conclusion, or unsupported.

    Never invent a value. Prefer explicit result lines over equation solving.
    """
    text = (explanation or "").strip()
    if not text:
        return ExtractResult(ok=False, reason="empty_explanation")
    confession = has_answer_confession(text)

    # 1) Sonuç / Doğru cevap line — last numeric token on that line
    for match in _SONUC_RE.finditer(text):
        line = match.group(1)
        tokens = re.findall(
            r"\\frac\{[^{}]+\}{[^{}]+\}|-?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?",
            line,
        )
        if tokens:
            parsed = _parse_value_token(tokens[-1])
            if parsed.ok:
                return ExtractResult(
                    ok=True,
                    value=parsed.expr,
                    display=tokens[-1],
                    source="sonuc_line",
                    confession=confession,
                )

    # 2) x = value (not "x = 12 için")
    x_matches = list(_X_EQ_RE.finditer(text))
    if x_matches:
        token = x_matches[-1].group(1)
        parsed = _parse_value_token(token)
        if parsed.ok:
            return ExtractResult(
                ok=True,
                value=parsed.expr,
                display=token,
                source="x_equals",
                confession=confession,
            )

    # 3) Last " = value" on a result-like line (probability = 2/3)
    last_eq = None
    for m in _LAST_EQ_VALUE_RE.finditer(text):
        last_eq = m
    if last_eq:
        token = last_eq.group(1)
        parsed = _parse_value_token(token)
        if parsed.ok:
            return ExtractResult(
                ok=True,
                value=parsed.expr,
                display=token,
                source="last_equality",
                confession=confession,
            )

    # 4) Single-unknown linear equation, only when the text looks computational
    #    (contains "toplam" / "denklem" / confession). Avoid intermediate steps
    #    in otherwise well-formed solutions.
    allow_solve = confession or bool(
        re.search(r"(toplam[ıi]|denklem|olasılık)", text, re.IGNORECASE)
    )
    if allow_solve:
        candidates: list[ParseResult] = []
        for m in _LINEAR_EQ_RE.finditer(text.replace("\n", " ")):
            eq = m.group(1)
            if "\\implies" in eq or "=>" in eq:
                # take the last segment
                eq = re.split(r"\\implies|=>", eq)[-1]
            parsed = _try_solve_linear(eq)
            if parsed.ok:
                candidates.append(parsed)
        if len(candidates) == 1:
            return ExtractResult(
                ok=True,
                value=candidates[0].expr,
                display=str(candidates[0].expr),
                source="linear_solve",
                confession=confession,
            )

    return ExtractResult(
        ok=False,
        confession=confession,
        reason="no_reliable_value",
    )
