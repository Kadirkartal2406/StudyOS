"""M32 P7 — AI cost logger (CSV + JSON daily files under data/ai_cost/)."""

from __future__ import annotations

import csv
import json
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class AiCostEvent:
    timestamp: str
    module: str
    model: str | None
    duration_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cache_hit: bool = False
    estimated_cost_usd: float = 0.0
    provider: str | None = None
    kind: str | None = None
    success: bool = True
    error: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


# Rough Gemini Flash free/paid estimate (USD per 1M tokens) — logging only
_COST_PER_M_PROMPT = 0.10
_COST_PER_M_COMPLETION = 0.40


def estimate_cost(prompt_tokens: int | None, completion_tokens: int | None) -> float:
    p = float(prompt_tokens or 0)
    c = float(completion_tokens or 0)
    return (p * _COST_PER_M_PROMPT + c * _COST_PER_M_COMPLETION) / 1_000_000.0


def _default_root() -> Path:
    return Path(__file__).resolve().parents[4] / "data" / "ai_cost"


class AiCostLogger:
    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else _default_root()
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._daily_count = 0
        self._weekly_count = 0
        self._day_key = ""
        self._week_key = ""
        self._load_counters()

    def _day(self) -> str:
        return datetime.now(UTC).strftime("%Y-%m-%d")

    def _week(self) -> str:
        return datetime.now(UTC).strftime("%G-W%V")

    def _load_counters(self) -> None:
        day = self._day()
        week = self._week()
        self._day_key = day
        self._week_key = week
        day_file = self.root / f"daily_{day}.json"
        week_file = self.root / f"weekly_{week}.json"
        if day_file.exists():
            try:
                self._daily_count = int(json.loads(day_file.read_text(encoding="utf-8")).get("count", 0))
            except Exception:
                self._daily_count = 0
        if week_file.exists():
            try:
                self._weekly_count = int(
                    json.loads(week_file.read_text(encoding="utf-8")).get("count", 0)
                )
            except Exception:
                self._weekly_count = 0

    def _rotate_if_needed(self) -> None:
        day = self._day()
        week = self._week()
        if day != self._day_key:
            self._day_key = day
            self._daily_count = 0
        if week != self._week_key:
            self._week_key = week
            self._weekly_count = 0

    def record(self, event: AiCostEvent) -> None:
        with self._lock:
            self._rotate_if_needed()
            if not event.cache_hit and event.success and event.provider not in (None, "null", "pool"):
                self._daily_count += 1
                self._weekly_count += 1
            self._append_jsonl(event)
            self._append_csv(event)
            self._write_counters()

    def _append_jsonl(self, event: AiCostEvent) -> None:
        path = self.root / f"events_{self._day_key}.jsonl"
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")

    def _append_csv(self, event: AiCostEvent) -> None:
        path = self.root / f"events_{self._day_key}.csv"
        exists = path.exists()
        with path.open("a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "timestamp",
                    "module",
                    "model",
                    "duration_ms",
                    "prompt_tokens",
                    "completion_tokens",
                    "cache_hit",
                    "estimated_cost_usd",
                    "provider",
                    "kind",
                    "success",
                    "error",
                ],
            )
            if not exists:
                writer.writeheader()
            row = asdict(event)
            row.pop("extra", None)
            writer.writerow(row)

    def _write_counters(self) -> None:
        (self.root / f"daily_{self._day_key}.json").write_text(
            json.dumps(
                {"date": self._day_key, "count": self._daily_count},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (self.root / f"weekly_{self._week_key}.json").write_text(
            json.dumps(
                {"week": self._week_key, "count": self._weekly_count},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    @property
    def daily_count(self) -> int:
        with self._lock:
            self._rotate_if_needed()
            return self._daily_count

    @property
    def weekly_count(self) -> int:
        with self._lock:
            self._rotate_if_needed()
            return self._weekly_count


_logger: AiCostLogger | None = None


def get_cost_logger() -> AiCostLogger:
    global _logger
    if _logger is None:
        _logger = AiCostLogger()
    return _logger


class timed_ai_call:
    """Context manager: duration + optional auto-record."""

    def __init__(self, module: str, *, kind: str | None = None, model: str | None = None):
        self.module = module
        self.kind = kind
        self.model = model
        self.t0 = 0.0
        self.duration_ms = 0.0

    def __enter__(self) -> timed_ai_call:
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.duration_ms = (time.perf_counter() - self.t0) * 1000.0
