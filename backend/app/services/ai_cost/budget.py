"""M32 P8 — daily AI request budget."""

from __future__ import annotations

import logging
import threading

from app.core.config import settings
from app.services.ai_cost.cost_logger import get_cost_logger

logger = logging.getLogger("studyos.ai_cost.budget")


class DailyAiBudget:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._warned = False

    @property
    def limit(self) -> int:
        return max(0, int(settings.AI_DAILY_REQUEST_BUDGET))

    def current(self) -> int:
        return get_cost_logger().daily_count

    def remaining(self) -> int:
        return max(0, self.limit - self.current())

    def is_exhausted(self) -> bool:
        if self.limit <= 0:
            return False
        return self.current() >= self.limit

    def allow_ai_call(self) -> bool:
        """Return False → pool-only mode (no new Gemini)."""
        if self.limit <= 0:
            return True
        cur = self.current()
        warn_at = int(self.limit * 0.9)
        with self._lock:
            if cur >= warn_at and not self._warned and cur < self.limit:
                self._warned = True
                logger.warning(
                    "AI daily budget warning count=%s limit=%s",
                    cur,
                    self.limit,
                )
            if cur >= self.limit:
                logger.warning(
                    "AI daily budget exhausted count=%s limit=%s — pool-only mode",
                    cur,
                    self.limit,
                )
                return False
        return True


_budget: DailyAiBudget | None = None


def get_daily_budget() -> DailyAiBudget:
    global _budget
    if _budget is None:
        _budget = DailyAiBudget()
    return _budget
