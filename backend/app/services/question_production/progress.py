"""M34.5 P3+P9 — live progress tracker with stop flag."""

from __future__ import annotations

import threading
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.services.question_production.types import LiveProgress


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class ProgressTracker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._progress = LiveProgress()
        self._stop_requested = False

    def get(self) -> LiveProgress:
        with self._lock:
            return deepcopy(self._progress)

    def set(self, progress: LiveProgress) -> None:
        with self._lock:
            self._progress = deepcopy(progress)
            self._progress.updated_at = _now_iso()

    def reset(
        self,
        *,
        exam: str = "",
        subject_code: str = "",
        topic_code: str = "",
        difficulty_band: str = "medium",
        planned: int = 0,
        approval_mode: str = "auto",
        run_id: str | None = None,
    ) -> LiveProgress:
        with self._lock:
            self._stop_requested = False
            now = _now_iso()
            self._progress = LiveProgress(
                run_id=run_id or str(uuid4()),
                status="running",
                exam=exam,
                subject_code=subject_code,
                topic_code=topic_code,
                difficulty_band=difficulty_band,
                planned=planned,
                remaining=planned,
                approval_mode=approval_mode,
                started_at=now,
                updated_at=now,
            )
            return deepcopy(self._progress)

    def request_stop(self) -> None:
        with self._lock:
            self._stop_requested = True
            if self._progress.status == "running":
                self._progress.status = "stopping"
                self._progress.updated_at = _now_iso()

    def is_stop_requested(self) -> bool:
        with self._lock:
            return self._stop_requested

    def set_last_preview(self, preview: dict[str, Any] | None) -> None:
        with self._lock:
            self._progress.last_preview = deepcopy(preview) if preview else None
            self._progress.updated_at = _now_iso()

    def update(
        self,
        *,
        status: str | None = None,
        current_index: int | None = None,
        accepted: int | None = None,
        rejected: int | None = None,
        rewrite: int | None = None,
        failed: int | None = None,
        gemini_calls: int | None = None,
        estimated_cost: float | None = None,
        remaining: int | None = None,
        exam: str | None = None,
        subject_code: str | None = None,
        topic_code: str | None = None,
        difficulty_band: str | None = None,
        planned: int | None = None,
        cost_report: dict[str, Any] | None = None,
        increment_accepted: int = 0,
        increment_rejected: int = 0,
        increment_rewrite: int = 0,
        increment_failed: int = 0,
        increment_gemini: int = 0,
        add_cost: float = 0.0,
    ) -> LiveProgress:
        with self._lock:
            p = self._progress
            if status is not None:
                p.status = status
            if current_index is not None:
                p.current_index = current_index
            if accepted is not None:
                p.accepted = accepted
            if rejected is not None:
                p.rejected = rejected
            if rewrite is not None:
                p.rewrite = rewrite
            if failed is not None:
                p.failed = failed
            if gemini_calls is not None:
                p.gemini_calls = gemini_calls
            if estimated_cost is not None:
                p.estimated_cost = estimated_cost
            if remaining is not None:
                p.remaining = remaining
            if exam is not None:
                p.exam = exam
            if subject_code is not None:
                p.subject_code = subject_code
            if topic_code is not None:
                p.topic_code = topic_code
            if difficulty_band is not None:
                p.difficulty_band = difficulty_band
            if planned is not None:
                p.planned = planned
            if cost_report is not None:
                p.cost_report = deepcopy(cost_report)
            p.accepted += increment_accepted
            p.rejected += increment_rejected
            p.rewrite += increment_rewrite
            p.failed += increment_failed
            p.gemini_calls += increment_gemini
            p.estimated_cost += add_cost
            p.updated_at = _now_iso()
            return deepcopy(p)


_tracker: ProgressTracker | None = None
_tracker_lock = threading.Lock()


def get_progress_tracker() -> ProgressTracker:
    global _tracker
    with _tracker_lock:
        if _tracker is None:
            _tracker = ProgressTracker()
        return _tracker
