"""M32 P9 — in-memory AI cost / cache metrics."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class AiCostMetrics:
    pool_hits: int = 0
    pool_misses: int = 0
    author_calls: int = 0
    gemini_calls: int = 0
    compact_calls: int = 0
    batch_calls: int = 0
    dedup_joins: int = 0
    budget_blocks: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record_pool_hit(self) -> None:
        with self._lock:
            self.pool_hits += 1

    def record_pool_miss(self) -> None:
        with self._lock:
            self.pool_misses += 1

    def record_author(self) -> None:
        with self._lock:
            self.author_calls += 1

    def record_gemini(self, duration_ms: float | None = None) -> None:
        with self._lock:
            self.gemini_calls += 1
            if duration_ms is not None:
                self.latencies_ms.append(float(duration_ms))
                if len(self.latencies_ms) > 500:
                    self.latencies_ms = self.latencies_ms[-500:]

    def record_compact(self) -> None:
        with self._lock:
            self.compact_calls += 1

    def record_batch(self) -> None:
        with self._lock:
            self.batch_calls += 1

    def record_dedup_join(self) -> None:
        with self._lock:
            self.dedup_joins += 1

    def record_budget_block(self) -> None:
        with self._lock:
            self.budget_blocks += 1

    def snapshot(self) -> dict:
        with self._lock:
            total = self.pool_hits + self.pool_misses
            hit_pct = round(100.0 * self.pool_hits / total, 2) if total else 0.0
            avg_lat = (
                round(sum(self.latencies_ms) / len(self.latencies_ms), 2)
                if self.latencies_ms
                else 0.0
            )
            return {
                "pool_hits": self.pool_hits,
                "pool_misses": self.pool_misses,
                "cache_hit_pct": hit_pct,
                "author_calls": self.author_calls,
                "gemini_calls": self.gemini_calls,
                "compact_calls": self.compact_calls,
                "batch_calls": self.batch_calls,
                "dedup_joins": self.dedup_joins,
                "budget_blocks": self.budget_blocks,
                "average_latency_ms": avg_lat,
                "updated_at": time.time(),
            }


_metrics: AiCostMetrics | None = None


def get_metrics() -> AiCostMetrics:
    global _metrics
    if _metrics is None:
        _metrics = AiCostMetrics()
    return _metrics
