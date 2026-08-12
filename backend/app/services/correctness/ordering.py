"""Roman-numeral ordering constraints — conservative discourse markers only."""

from __future__ import annotations

import itertools
import re
from typing import Any

from app.services.correctness.types import (
    CorrectnessCheck,
    CorrectnessErrorCode,
    CorrectnessInput,
)

_ORDERING_Q_RE = re.compile(
    r"hangi s[ıi]ralama|do[gğ]ru s[ıi]ralama|s[ıi]ralamas[ıi] hangisi",
    re.IGNORECASE,
)
_ROMAN_CHOICE_RE = re.compile(
    r"\b(I{1,3}|IV|V|VI{0,3}|IX|X)\s*[-–—,]\s*"
    r"(I{1,3}|IV|V|VI{0,3}|IX|X)",
    re.IGNORECASE,
)
_STATEMENT_RE = re.compile(
    r"(?:^|\n)\s*(I{1,3}|IV|V)\s*[.)\-–:]\s*(.+?)(?=(?:\n\s*(?:I{1,3}|IV|V)\s*[.)\-–:])|$)",
    re.IGNORECASE | re.DOTALL,
)
_MARKERS = (
    ("öncelikle", "first"),
    ("daha sonra", "then"),
    ("ardından", "then"),
    ("bunun sonucunda", "result"),
    ("bu nedenle", "result"),
    ("bu durum", "anaphora"),
    ("ancak", "contrast"),
)
_ROMAN_ORDER = ("I", "II", "III", "IV", "V")


def _is_ordering_question(inp: CorrectnessInput) -> bool:
    blob = (inp.stem or "") + " " + " ".join((inp.choices or {}).values())
    if _ORDERING_Q_RE.search(inp.stem or ""):
        return True
    roman_choices = sum(1 for v in (inp.choices or {}).values() if _ROMAN_CHOICE_RE.search(str(v)))
    return roman_choices >= 2


def _statements(stem: str) -> dict[str, str]:
    found: dict[str, str] = {}
    for m in _STATEMENT_RE.finditer(stem or ""):
        key = m.group(1).upper()
        found[key] = m.group(2).strip()
    return found


def _constraints(statements: dict[str, str]) -> list[tuple[str, str]] | None:
    """Return (before, after) pairs. None = could not parse reliably."""
    pairs: list[tuple[str, str]] = []
    items = [(k, statements[k]) for k in _ROMAN_ORDER if k in statements]
    if len(items) < 2:
        return None
    first_key = None
    then_keys: list[str] = []
    result_keys: list[str] = []
    for key, text in items:
        low = text.lower()
        if "öncelikle" in low:
            first_key = key
        if "daha sonra" in low or "ardından" in low:
            then_keys.append(key)
        if "bunun sonucunda" in low or "bu nedenle" in low:
            result_keys.append(key)
    if first_key:
        for k, _ in items:
            if k != first_key:
                pairs.append((first_key, k))
    for tk in then_keys:
        if first_key and tk != first_key:
            pairs.append((first_key, tk))
        for rk in result_keys:
            if tk != rk:
                pairs.append((tk, rk))
    for rk in result_keys:
        for k, _ in items:
            if k != rk and k not in result_keys:
                pairs.append((k, rk))
    return pairs


def _count_linear_extensions(keys: list[str], pairs: list[tuple[str, str]]) -> int:
    valid = 0
    before = {p[0] + ">" + p[1] for p in pairs}
    for perm in itertools.permutations(keys):
        pos = {k: i for i, k in enumerate(perm)}
        ok = True
        for a, b in pairs:
            if a not in pos or b not in pos:
                continue
            if pos[a] >= pos[b]:
                ok = False
                break
        if ok:
            valid += 1
        _ = before
    return valid


def check_ordering(inp: CorrectnessInput) -> CorrectnessCheck:
    evidence: dict[str, Any] = {
        "is_ordering": False,
        "statements": [],
        "constraint_count": 0,
        "valid_orders": None,
    }
    if not _is_ordering_question(inp):
        return CorrectnessCheck(
            name="ordering",
            status="unsupported",
            error_code=CorrectnessErrorCode.AMBIGUOUS_ORDERING.value,
            message="not_ordering_question",
            evidence=evidence,
        )
    evidence["is_ordering"] = True
    stmts = _statements(inp.stem or "")
    evidence["statements"] = list(stmts.keys())
    if len(stmts) < 2:
        return CorrectnessCheck(
            name="ordering",
            status="unsupported",
            error_code=CorrectnessErrorCode.AMBIGUOUS_ORDERING.value,
            message="ordering:statements_unparsed",
            evidence=evidence,
        )
    pairs = _constraints(stmts)
    if pairs is None:
        return CorrectnessCheck(
            name="ordering",
            status="unsupported",
            error_code=CorrectnessErrorCode.AMBIGUOUS_ORDERING.value,
            message="ordering:unsupported_semantics",
            evidence=evidence,
        )
    evidence["constraint_count"] = len(pairs)
    keys = [k for k in _ROMAN_ORDER if k in stmts]
    if not pairs:
        n = _count_linear_extensions(keys, [])
        evidence["valid_orders"] = n
        if n > 1:
            return CorrectnessCheck(
                name="ordering",
                status="fail",
                error_code=CorrectnessErrorCode.AMBIGUOUS_ORDERING.value,
                message="ambiguous_ordering",
                evidence=evidence,
            )
        return CorrectnessCheck(name="ordering", status="pass", evidence=evidence)

    n = _count_linear_extensions(keys, pairs)
    evidence["valid_orders"] = n
    if n == 0:
        return CorrectnessCheck(
            name="ordering",
            status="fail",
            error_code=CorrectnessErrorCode.AMBIGUOUS_ORDERING.value,
            message="ambiguous_ordering:inconsistent",
            evidence=evidence,
        )
    if n == 1:
        return CorrectnessCheck(name="ordering", status="pass", evidence=evidence)
    return CorrectnessCheck(
        name="ordering",
        status="fail",
        error_code=CorrectnessErrorCode.AMBIGUOUS_ORDERING.value,
        message="ambiguous_ordering",
        evidence=evidence,
    )
