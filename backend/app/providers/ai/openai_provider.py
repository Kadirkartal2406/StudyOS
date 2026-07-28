"""
OpenAIProvider — Sprint-2.4 gerçek HTTP (httpx / Chat Completions).
"""

from __future__ import annotations

from app.core.config import settings
from app.core.constants import AI_DEFAULT_MODELS
from app.core.exceptions import AIProviderError, AIUnavailableError
from app.providers.ai.base import AIProvider, GenerateRequest
from app.providers.ai.http_transport import post_json


class OpenAIProvider(AIProvider):
    def __init__(self, model: str | None = None) -> None:
        self._model = model or settings.AI_MODEL or AI_DEFAULT_MODELS["openai"]

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, request: GenerateRequest) -> str:
        key = (settings.OPENAI_API_KEY or "").strip()
        if not key:
            raise AIUnavailableError("OpenAI API anahtarı yapılandırılmamış")

        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        if not messages:
            raise AIProviderError("OpenAI için mesaj listesi boş")

        data = await post_json(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": self._model,
                "messages": messages,
                "temperature": settings.AI_TEMPERATURE,
                "max_tokens": settings.AI_MAX_TOKENS,
            },
            provider_label="openai",
        )
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("OpenAI yanıtı parse edilemedi") from exc
        if not isinstance(text, str) or not text.strip():
            raise AIProviderError("OpenAI boş yanıt döndü")
        return text.strip()
