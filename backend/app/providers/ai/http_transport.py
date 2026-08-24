"""
StudyOS — AI Provider httpx taşıma katmanı
Sprint-2.4 (A1): ortak timeout / retry / connection pooling; API key loglanmaz.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIRateLimitError,
    AITimeoutError,
    AIUnavailableError,
)

logger = logging.getLogger("studyos.ai")

_shared_client: httpx.AsyncClient | None = None
_client_lock = asyncio.Lock()


def _get_safe_timeout(timeout_seconds: float | None = None) -> httpx.Timeout:
    secs = timeout_seconds if timeout_seconds is not None else float(settings.AI_TIMEOUT_SECONDS)
    return httpx.Timeout(secs)


def get_http_limits() -> httpx.Limits:
    """Connection pooling limitleri: max 100 bağlantı, 20 keep-alive."""
    return httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30.0,
    )


async def get_shared_client() -> httpx.AsyncClient:
    """Paylaşılan httpx.AsyncClient örneğini döndürür; yoksa lazy initialize eder."""
    global _shared_client
    if _shared_client is not None and not _shared_client.is_closed:
        return _shared_client

    async with _client_lock:
        if _shared_client is None or _shared_client.is_closed:
            _shared_client = httpx.AsyncClient(
                limits=get_http_limits(),
                timeout=_get_safe_timeout(),
            )
            logger.info("Shared AI httpx.AsyncClient initialized (pooling enabled)")
        return _shared_client


async def init_http_transport() -> None:
    """FastAPI startup / lifespan anından çağrılan açık initialization."""
    await get_shared_client()


async def close_http_transport() -> None:
    """FastAPI shutdown / lifespan anında bağlantı havuzunu güvenle kapatır."""
    global _shared_client
    if _shared_client is not None and not _shared_client.is_closed:
        await _shared_client.aclose()
        _shared_client = None
        logger.info("Shared AI httpx.AsyncClient closed gracefully")


def _safe_error_body(text: str, limit: int = 200) -> str:
    """Yanıt gövdesinden kısa özet; key benzeri uzun token'ları kes."""
    cleaned = text.replace("\n", " ").strip()
    if len(cleaned) > limit:
        return cleaned[:limit] + "…"
    return cleaned


def _parse_retry_delay(body: str) -> float | None:
    """Extract retryDelay seconds from Gemini 429 JSON body."""
    import json as _json
    import re as _re

    try:
        data = _json.loads(body)
        details = data.get("error", {}).get("details", [])
        for d in details:
            if d.get("@type", "").endswith("RetryInfo"):
                raw = d.get("retryDelay", "")
                m = _re.search(r"([\d.]+)", str(raw))
                if m:
                    return float(m.group(1))
    except Exception:
        pass
    return None


def map_http_error(status_code: int, body: str) -> AIProviderError:
    snippet = _safe_error_body(body)

    if status_code == 429:
        lowered = body.casefold()

        logger.warning("Gemini raw 429 body: %s", body)

        retry_after = _parse_retry_delay(body)

        if any(
            x in lowered
            for x in (
                "quota",
                "billing",
                "insufficient",
                "resource_exhausted",
                "resource exhausted",
                "quota exceeded",
                "generative language api has been used",
                "generaterequests",
                "generative language",
            )
        ):
            exc = AIQuotaExceededError("AI kullanım kotası doldu")
            exc.retry_after = retry_after  # type: ignore[attr-defined]
            return exc

        exc2 = AIRateLimitError("AI hız limiti aşıldı (429)")
        exc2.retry_after = retry_after  # type: ignore[attr-defined]
        return exc2

    if status_code in (401, 403):
        return AIUnavailableError("AI sağlayıcı kimlik doğrulaması başarısız")

    if status_code >= 500:
        return AIUnavailableError(f"AI sağlayıcı geçici hata ({status_code})")

    return AIProviderError(f"AI sağlayıcı hata ({status_code}): {snippet}")


async def post_json(
    url: str,
    *,
    headers: dict[str, str],
    payload: dict[str, Any],
    provider_label: str,
    timeout_seconds: float | None = None,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """httpx POST + retry; Authorization header loglanmaz. Paylaşımlı AsyncClient kullanır."""
    http_client = client or await get_shared_client()
    req_timeout = _get_safe_timeout(timeout_seconds) if timeout_seconds is not None else None
    retries = max(0, int(settings.AI_RETRY_COUNT))
    last_exc: Exception | None = None

    for attempt in range(retries + 1):
        try:
            kwargs: dict[str, Any] = {
                "headers": headers,
                "json": payload,
            }
            if req_timeout is not None:
                kwargs["timeout"] = req_timeout

            response = await http_client.post(url, **kwargs)
            if response.status_code >= 400:
                err = map_http_error(response.status_code, response.text)
                # 429 / 5xx → retry; diğerleri hemen fırlat
                if response.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                    retry_after = getattr(err, "retry_after", None)
                    if response.status_code == 429 and retry_after and retry_after > 0:
                        wait = min(retry_after + 1.0, 60.0)
                    else:
                        wait = 2.0 * (attempt + 1)
                    logger.info(
                        "ai_retry provider=%s status=%s attempt=%s wait=%.1fs",
                        provider_label,
                        response.status_code,
                        attempt + 1,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    last_exc = err
                    continue
                raise err
            data = response.json()
            if not isinstance(data, dict):
                raise AIProviderError("AI sağlayıcı beklenmeyen yanıt formatı")
            return data
        except httpx.TimeoutException as exc:
            last_exc = AITimeoutError()
            if attempt < retries:
                if settings.DEBUG:
                    logger.debug(
                        "ai_retry provider=%s reason=timeout attempt=%s",
                        provider_label,
                        attempt + 1,
                    )
                await asyncio.sleep(0.4 * (attempt + 1))
                continue
            raise AITimeoutError() from exc
        except httpx.HTTPError as exc:
            last_exc = AIUnavailableError("AI ağ hatası")
            if attempt < retries:
                if settings.DEBUG:
                    logger.debug(
                        "ai_retry provider=%s reason=network attempt=%s",
                        provider_label,
                        attempt + 1,
                    )
                await asyncio.sleep(0.4 * (attempt + 1))
                continue
            raise AIUnavailableError("AI ağ hatası") from exc

    if isinstance(last_exc, AIProviderError):
        raise last_exc
    raise AIUnavailableError("AI sağlayıcı kullanılamıyor")

