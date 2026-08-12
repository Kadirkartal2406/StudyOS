"""Pairwise mathematical option equivalence."""

from __future__ import annotations

import re
from typing import Any

from app.services.correctness.math_parser import values_equal
from app.services.correctness.relation_parse import (
    RelationForm,
    parse_option_value,
    relations_equal,
)


def _norm_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def find_equivalent_option_pairs(choices: dict[str, str]) -> list[tuple[str, str, str]]:
    """Return (key_a, key_b, layer) for proven-equivalent pairs.

    Unparseable options are skipped (never treated as equivalent).
    """
    items = [(str(k).upper(), str(v)) for k, v in (choices or {}).items()]
    pairs: list[tuple[str, str, str]] = []
    for i, (ka, va) in enumerate(items):
        for kb, vb in items[i + 1 :]:
            na, nb = _norm_text(va), _norm_text(vb)
            if na and na == nb:
                pairs.append((ka, kb, "exact"))
                continue
            pa, pb = parse_option_value(va), parse_option_value(vb)
            if not pa.ok or not pb.ok:
                continue
            if isinstance(pa.expr, RelationForm) and isinstance(pb.expr, RelationForm):
                eq = relations_equal(pa.expr, pb.expr)
            elif isinstance(pa.expr, RelationForm) or isinstance(pb.expr, RelationForm):
                continue
            else:
                eq = values_equal(pa.expr, pb.expr)
            if eq is True:
                pairs.append((ka, kb, "math"))
    return pairs


def option_equivalence_evidence(choices: dict[str, str]) -> dict[str, Any]:
    pairs = find_equivalent_option_pairs(choices)
    return {
        "equivalent_pairs": [{"a": a, "b": b, "layer": layer} for a, b, layer in pairs],
        "claimed_key": None,
        "solved_value": None,
        "matching_keys": [],
    }
