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
from app.providers.ai.base import AIProvider, ChatMessageDTO, GenerateRequest
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
        self._model = model or settings.AI_MODEL or AI_DEFAULT_MODELS["gemini"]

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    def _candidate_models(self) -> list[str]:
        ordered: list[str] = []

        for name in (self._model, *AI_GEMINI_MODEL_FALLBACKS):
            n = (name or "").strip()
            if n and n not in ordered:
                ordered.append(n)

        max_fallbacks = max(
            0,
            int(getattr(settings, "AI_GEMINI_MAX_FALLBACKS", 1)),
        )

        return ordered[: 1 + max_fallbacks]

    def _get_api_keys(self) -> list[str]:
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
        keys = self._get_api_keys()

        if not keys:
            raise AIUnavailableError("Gemini API anahtarı yapılandırılmamış")

        if _current_key_index >= len(keys):
            _current_key_index = 0
            
        rotated_keys = keys[_current_key_index:] + keys[:_current_key_index]

        system, contents = _to_gemini_contents(request.messages)

        if not contents:
            raise AIProviderError("Gemini için mesaj listesi boş")

        ctx = request.context or {}

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

                    logger.warning(
                        "Gemini quota exceeded. key=%s...%s model=%s",
                        key[:4],
                        key[-4:],
                        model,
                    )

                    # Bu anahtarın limiti doldu, sistemin kalıcı hafızasındaki (global) sırayı bir sonrakine kaydır
                    _current_key_index = (_current_key_index + 1) % len(keys)
                    
                    # Aynı key'in model döngüsünü bırak, sonraki key'e geç
                    break

                except AIProviderError as exc:
                    msg = (exc.message or "").lower()

                    if (
                        "404" in msg
                        or "not found" in msg
                        or "no longer" in msg
                    ):
                        last_exc = exc
                        continue

                    raise

        if isinstance(last_exc, AIProviderError):
            raise last_exc

        raise AIUnavailableError("Gemini modelleri kullanılamıyor")