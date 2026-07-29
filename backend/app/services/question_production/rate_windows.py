"""M34.5 — in-memory sliding window counters for AI call rate limits."""

from __future__ import annotations

import threading
import time
from collections import deque


class RateWindows:
    """Thread-safe minute/hour sliding windows for AI call counts."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._timestamps: deque[float] = deque()

    def record_call(self) -> None:
        now = time.monotonic()
        with self._lock:
            self._timestamps.append(now)
            self._prune(now)

    def count_last_minute(self) -> int:
        now = time.monotonic()
        with self._lock:
            self._prune(now)
            cutoff = now - 60.0
            return sum(1 for t in self._timestamps if t >= cutoff)

    def count_last_hour(self) -> int:
        now = time.monotonic()
        with self._lock:
            self._prune(now)
            cutoff = now - 3600.0
            return sum(1 for t in self._timestamps if t >= cutoff)

    def _prune(self, now: float) -> None:
        cutoff = now - 3600.0
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()


_rate_windows: RateWindows | None = None
_rate_lock = threading.Lock()


def get_rate_windows() -> RateWindows:
    global _rate_windows
    with _rate_lock:
        if _rate_windows is None:
            _rate_windows = RateWindows()
        return _rate_windows
