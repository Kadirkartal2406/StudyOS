"""
GeminiProvider — Sprint-2.4 gerçek HTTP (httpx / Generative Language API).
"""

from __future__ import annotations

import logging

from app.core.config import settings
from app.core.constants import AI_DEFAULT_MODELS, AI_GEMINI_MODEL_FALLBACKS
from app.core.exceptions import (
    AIProviderError,
    AIQuotaExceededError,
    AIUnavailableError,
)
from app.providers.ai.base import (
    AIProvider,
    ChatMessageDTO,
    GenerateRequest,
    sanitize_ai_model,
)


def _sanitize_gemini_model(model: str | None) -> str | None:
    """Only real Gemini model ids. 'template' / OpenAI names never hit the URL."""
    n = sanitize_ai_model(model)
    if n is None:
        return None
    leaf = n.split("/")[-1]
    if not leaf.lower().startswith("gemini"):
        logger.warning("gemini refusing non-gemini model name=%s", n)
        return None
    return leaf
from app.providers.ai.http_transport import post_json

logger = logging.getLogger("studyos.ai.gemini")


def _to_gemini_contents(
    messages: list[ChatMessageDTO],
) -> tuple[str | None, list[dict]]:
    system_parts: list[str] = []
    contents: list[dict] = []

    for msg in messages:
        if msg.role == "system":
            system_parts.append(msg.content)
            continue

        role = "model" if msg.role == "assistant" else "user"
        contents.append(
            {
                "role": role,
                "parts": [{"text": msg.content}],
            }
        )

    system = " ".join(system_parts) if system_parts else None
    return system, contents


_current_key_index = 0

class GeminiProvider(AIProvider):
    def __init__(self, model: str | None = None) -> None:
        self._model = (
            _sanitize_gemini_model(model)
            or _sanitize_gemini_model(settings.AI_MODEL)
            or AI_DEFAULT_MODELS["gemini"]
        )

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    def _candidate_models(self) -> list[str]:
        ordered: list[str] = []

        for name in (self._model, *AI_GEMINI_MODEL_FALLBACKS):
            n = _sanitize_gemini_model(name)
            if n and n not in ordered:
                ordered.append(n)

        max_fallbacks = max(
            0,
            int(getattr(settings, "AI_GEMINI_MAX_FALLBACKS", 1)),
        )

        return ordered[: 1 + max_fallbacks]

    def _get_api_keys(self, override: str | None = None) -> list[str]:
        if override:
            cleaned = override.strip()
            if cleaned and not cleaned.startswith("<MagicMock"):
                return [cleaned]
                
        raw_keys = [
            str(getattr(settings, "GEMINI_API_KEY", "") or ""),
            str(getattr(settings, "GEMINI_API_KEY_2", "") or ""),
            str(getattr(settings, "GEMINI_API_KEY_3", "") or ""),
        ]
        valid_keys = []
        for k in raw_keys:
            cleaned = k.strip()
            if cleaned and not cleaned.startswith("<MagicMock"):
                valid_keys.append(cleaned)

        return valid_keys

    async def generate(self, request: GenerateRequest) -> str:
        global _current_key_index
        ctx = request.context or {}
        api_key_override = ctx.get("api_key_override")
        keys = self._get_api_keys(override=api_key_override)

        if not keys:
            raise AIUnavailableError("Gemini API anahtarı yapılandırılmamış")

        if _current_key_index >= len(keys):
            _current_key_index = 0
            
        rotated_keys = keys[_current_key_index:] + keys[:_current_key_index]

        system, contents = _to_gemini_contents(request.messages)

        if not contents:
            raise AIProviderError("Gemini için mesaj listesi boş")

        max_tokens = int(
            ctx.get("max_output_tokens") or settings.AI_MAX_TOKENS
        )
        timeout_seconds = ctx.get("timeout_seconds")

        last_exc: Exception | None = None

        for key in rotated_keys:
            for model in self._candidate_models():
                url = (
                    "https://generativelanguage.googleapis.com/v1beta/models/"
                    f"{model}:generateContent"
                )

                payload: dict = {
                    "contents": contents,
                    "generationConfig": {
                        "temperature": settings.AI_TEMPERATURE,
                        "maxOutputTokens": max_tokens,
                    },
                }

                if system:
                    payload["systemInstruction"] = {
                        "parts": [{"text": system}]
                    }

                try:
                    data = await post_json(
                        url,
                        headers={
                            "Content-Type": "application/json",
                            "x-goog-api-key": key,
                        },
                        payload=payload,
                        provider_label="gemini",
                        timeout_seconds=(
                            float(timeout_seconds)
                            if timeout_seconds
                            else None
                        ),
                    )

                    try:
                        candidates = data["candidates"]
                        parts = candidates[0]["content"]["parts"]
                        texts = [
                            p.get("text") or ""
                            for p in parts
                            if isinstance(p, dict)
                        ]
                        text = "".join(texts).strip()

                    except (KeyError, IndexError, TypeError) as exc:
                        raise AIProviderError(
                            "Gemini yanıtı parse edilemedi"
                        ) from exc

                    if not text:
                        raise AIProviderError("Gemini boş yanıt döndü")

                    if model != self._model:
                        self._model = model

                        if settings.DEBUG:
                            logger.debug(
                                "gemini_model_fallback used=%s",
                                model,
                            )

                    return text

                except AIQuotaExceededError as exc:
                    last_exc = exc

                    retry_after = getattr(exc, "retry_after", None) or 0
                    logger.warning(
                        "Gemini quota exceeded. key=%s...%s model=%s retry_after=%.0fs",
                        key[:4],
                        key[-4:],
                        model,
                        retry_after,
                    )

                    _current_key_index = (_current_key_index + 1) % len(keys)

                    if retry_after > 0:
                        wait = min(retry_after + 1.0, 60.0)
                        logger.info("Waiting %.0fs before next key (retryDelay)", wait)
                        await asyncio.sleep(wait)

                    break

                except AIProviderError as exc:
                    msg = (exc.message or "").lower()

                    if (
                        "404" in msg
                        or "401" in msg
                        or "403" in msg
                        or "not found" in msg
                        or "no longer" in msg
                        or "kimlik" in msg
                        or "unauthorized" in msg
                    ):
                        last_exc = exc
                        logger.warning(
                            "gemini model skipped model=%s err=%s",
                            model,
                            exc.message,
                        )
                        continue

                    raise

        if isinstance(last_exc, AIProviderError):
            raise last_exc

        raise AIUnavailableError("Gemini modelleri kullanılamıyor")