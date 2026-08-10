"""Measurement soft-integration feature flags (default OFF)."""

from __future__ import annotations

from app.core.config import settings

_VALID_MODES = frozenset({"off", "shadow", "soft_review"})


def measurement_mode() -> str:
    raw = str(getattr(settings, "MEASUREMENT_MODE", "off") or "off").strip().lower()
    if raw in {"soft-review", "softreview", "soft"}:
        raw = "soft_review"
    return raw if raw in _VALID_MODES else "off"


def measurement_enabled() -> bool:
    return measurement_mode() != "off"


def measurement_shadow() -> bool:
    return measurement_mode() == "shadow"


def measurement_soft_review() -> bool:
    return measurement_mode() == "soft_review"


def measurement_max_regen() -> int:
    try:
        n = int(getattr(settings, "MEASUREMENT_CONTRACT_MAX_REGEN", 1) or 1)
    except (TypeError, ValueError):
        n = 1
    return max(0, min(n, 3))
