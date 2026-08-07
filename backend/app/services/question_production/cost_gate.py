"""M34.5 P0+P1 — cost / rate gate before generation."""

from __future__ import annotations

import logging

from app.core.config import settings
from app.services.ai_cost.budget import get_daily_budget
from app.services.ai_cost.cost_logger import estimate_cost
from app.services.question_production.rate_windows import get_rate_windows
from app.services.question_production.types import CostGateResult

logger = logging.getLogger("studyos.m345")

_ASSUMED_PROMPT_TOKENS = 800
_ASSUMED_COMPLETION_TOKENS = 400


def _batch_size_from_ratio(ratio: float) -> int:
    """Map remaining/limit budget ratio → suggested batch size (capped at 5)."""
    return 5


def _hourly_limit() -> int:
    hourly = int(getattr(settings, "AI_HOURLY_REQUEST_BUDGET", 0) or 0)
    if hourly > 0:
        return hourly
    minute = max(0, int(settings.AI_RATE_LIMIT_PER_MINUTE or 0))
    return minute * 60


def _est_cost_per_question() -> float:
    configured = float(
        getattr(settings, "QUESTION_PRODUCTION_EST_COST_PER_QUESTION_USD", 0.002) or 0.002
    )
    token_est = estimate_cost(_ASSUMED_PROMPT_TOKENS, _ASSUMED_COMPLETION_TOKENS)
    # Prefer configured rough estimate when present; fall back to token model.
    return configured if configured > 0 else token_est


def suggest_batch_size() -> int:
    """Suggested batch size from remaining budget ratio, capped by rate windows."""
    budget = get_daily_budget()
    daily_limit = int(budget.limit)
    daily_remaining = int(budget.remaining()) if daily_limit > 0 else 10**9

    if daily_limit <= 0:
        ratio = 1.0
    else:
        ratio = daily_remaining / max(daily_limit, 1)

    size = _batch_size_from_ratio(ratio)

    minute_limit = max(0, int(settings.AI_RATE_LIMIT_PER_MINUTE or 0))
    windows = get_rate_windows()
    minute_remaining = (
        max(0, minute_limit - windows.count_last_minute()) if minute_limit > 0 else 10**9
    )

    hourly_limit = _hourly_limit()
    hourly_remaining = (
        max(0, hourly_limit - windows.count_last_hour()) if hourly_limit > 0 else 10**9
    )

    caps = [size, 50]
    if minute_limit > 0:
        caps.append(minute_remaining)
    if daily_limit > 0:
        caps.append(daily_remaining)
    if hourly_limit > 0:
        caps.append(hourly_remaining)
    return max(0, min(caps))


def check_can_generate(*, planned_count: int = 10) -> CostGateResult:
    """Return whether a generation batch of `planned_count` is allowed."""
    planned = max(0, int(planned_count or 0))
    budget = get_daily_budget()
    daily_limit = int(budget.limit)
    daily_remaining = int(budget.remaining()) if daily_limit > 0 else 10**9

    minute_limit = max(0, int(settings.AI_RATE_LIMIT_PER_MINUTE or 0))
    windows = get_rate_windows()
    minute_used = windows.count_last_minute()
    minute_remaining = max(0, minute_limit - minute_used) if minute_limit > 0 else 10**9

    hourly_limit = _hourly_limit()
    hourly_used = windows.count_last_hour()
    hourly_remaining = max(0, hourly_limit - hourly_used) if hourly_limit > 0 else 10**9

    est_per_q = _est_cost_per_question()
    estimated_batch_cost = float(planned) * est_per_q
    suggested = suggest_batch_size()

    provider = (settings.AI_PROVIDER or "null").strip().lower()
    can = True
    reason: str | None = None

    if provider in ("", "null", "none"):
        can = False
        reason = "AI_PROVIDER is null"
    elif daily_limit > 0 and (budget.is_exhausted() or daily_remaining < 1):
        can = False
        reason = "daily budget exhausted"
    elif minute_limit > 0 and minute_remaining < 1:
        can = False
        reason = "minute rate limit exhausted"
    elif hourly_limit > 0 and hourly_remaining < 1:
        can = False
        reason = "hourly request budget exhausted"

    result = CostGateResult(
        can_generate=can,
        reason=reason,
        daily_limit=daily_limit,
        daily_remaining=daily_remaining if daily_limit > 0 else -1,
        hourly_limit=hourly_limit,
        hourly_remaining=hourly_remaining if hourly_limit > 0 else -1,
        minute_limit=minute_limit,
        minute_remaining=minute_remaining if minute_limit > 0 else -1,
        estimated_batch_cost=estimated_batch_cost,
        suggested_batch_size=suggested,
    )
    if not can:
        logger.info("M34.5 cost gate blocked: %s", reason)
    return result
