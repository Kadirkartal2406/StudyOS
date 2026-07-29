"""M34.5 P5 — in-memory MANUAL approval queue."""

from __future__ import annotations

import threading
from copy import deepcopy
from typing import Any

from app.services.question_production.types import PendingQuestion


class PendingQueue:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._items: dict[str, PendingQuestion] = {}

    def add(self, item: PendingQuestion) -> PendingQuestion:
        with self._lock:
            self._items[item.id] = deepcopy(item)
            return deepcopy(item)

    def list(self) -> list[PendingQuestion]:
        with self._lock:
            return [deepcopy(v) for v in self._items.values()]

    def get(self, item_id: str) -> PendingQuestion | None:
        with self._lock:
            item = self._items.get(item_id)
            return deepcopy(item) if item else None

    def approve(self, item_id: str) -> dict[str, Any] | None:
        with self._lock:
            item = self._items.pop(item_id, None)
            return item.to_dict() if item else None

    def reject(self, item_id: str) -> bool:
        with self._lock:
            if item_id not in self._items:
                return False
            del self._items[item_id]
            return True

    def clear(self) -> int:
        with self._lock:
            n = len(self._items)
            self._items.clear()
            return n


_queue: PendingQueue | None = None
_queue_lock = threading.Lock()


def get_pending_queue() -> PendingQueue:
    global _queue
    with _queue_lock:
        if _queue is None:
            _queue = PendingQueue()
        return _queue
