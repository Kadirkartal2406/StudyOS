"""
StudyOS — AI Provider httpx taşıma katmanı
Sprint-2.4 (A1): ortak timeout / retry; API key loglanmaz.
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


def _safe_error_body(text: str, limit: int = 200) -> str:
    """Yanıt gövdesinden kısa özet; key benzeri uzun token'ları kes."""
    cleaned = text.replace("\n", " ").strip()
    if len(cleaned) > limit:
        return cleaned[:limit] + "…"
    return cleaned


def map_http_error(status_code: int, body: str) -> AIProviderError:
    snippet = _safe_error_body(body)

    if status_code == 429:
        lowered = body.casefold()

        # DEBUG: Google'ın gerçek cevabını logla
        logger.warning("Gemini raw 429 body: %s", body)

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
            return AIQuotaExceededError("AI kullanım kotası doldu")

        return AIRateLimitError("AI hız limiti aşıldı (429)")

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
) -> dict[str, Any]:
    """httpx POST + retry; Authorization header loglanmaz."""
    timeout = httpx.Timeout(timeout_seconds or settings.AI_TIMEOUT_SECONDS)
    retries = max(0, int(settings.AI_RETRY_COUNT))
    last_exc: Exception | None = None

    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                err = map_http_error(response.status_code, response.text)
                # 429 / 5xx → retry; diğerleri hemen fırlat
                if response.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                    if settings.DEBUG:
                        logger.debug(
                            "ai_retry provider=%s status=%s attempt=%s",
                            provider_label,
                            response.status_code,
                            attempt + 1,
                        )
                    await asyncio.sleep(0.4 * (attempt + 1))
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
