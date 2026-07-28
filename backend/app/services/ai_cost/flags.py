"""M32 P1 — feature-flag helpers (defaults: auto-AI off)."""

from __future__ import annotations

from app.core.config import settings


def auto_booklet_enabled() -> bool:
    return bool(settings.ENABLE_AUTO_BOOKLET)


def background_ai_enabled() -> bool:
    return bool(settings.ENABLE_BACKGROUND_AI)


def midnight_scheduler_enabled() -> bool:
    return bool(settings.ENABLE_MIDNIGHT_SCHEDULER)


def catchup_enabled() -> bool:
    return bool(settings.ENABLE_CATCHUP)


def ai_warmup_enabled() -> bool:
    return bool(settings.ENABLE_AI_WARMUP)


def compact_author_enabled() -> bool:
    return bool(getattr(settings, "ENABLE_COMPACT_AUTHOR", True))


def pool_only_mode() -> bool:
    """True when daily budget exhausted — serve pool only, no new Gemini."""
    from app.services.ai_cost.budget import get_daily_budget

    return get_daily_budget().is_exhausted()
