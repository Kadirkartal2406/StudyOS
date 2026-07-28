"""M32 P5 — in-process + cross-wait request deduplication."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

T = TypeVar("T")


class RequestDeduplicator:
    """Single-flight: concurrent identical keys share one in-flight future."""

    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}
        self._inflight: dict[str, asyncio.Future[Any]] = {}
        self._meta = asyncio.Lock()

    async def do(
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
    ) -> T:
        async with self._meta:
            existing = self._inflight.get(key)
            if existing is not None and not existing.done():
                wait_fut = existing
            else:
                wait_fut = None
                loop = asyncio.get_running_loop()
                fut: asyncio.Future[Any] = loop.create_future()
                self._inflight[key] = fut
                owner = True

        if wait_fut is not None:
            return await asyncio.shield(wait_fut)

        try:
            result = await factory()
            fut.set_result(result)
            return result
        except Exception as e:
            if not fut.done():
                fut.set_exception(e)
            raise
        finally:
            async with self._meta:
                cur = self._inflight.get(key)
                if cur is fut:
                    self._inflight.pop(key, None)


_dedup: RequestDeduplicator | None = None


def get_deduplicator() -> RequestDeduplicator:
    global _dedup
    if _dedup is None:
        _dedup = RequestDeduplicator()
    return _dedup
