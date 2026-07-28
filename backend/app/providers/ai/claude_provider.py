"""
ClaudeProvider — Sprint-2.4 gerçek HTTP (httpx / Anthropic Messages API).
"""

from __future__ import annotations

from app.core.config import settings
from app.core.constants import AI_DEFAULT_MODELS
from app.core.exceptions import AIProviderError, AIUnavailableError
from app.providers.ai.base import AIProvider, GenerateRequest
from app.providers.ai.http_transport import post_json


class ClaudeProvider(AIProvider):
    def __init__(self, model: str | None = None) -> None:
        self._model = model or settings.AI_MODEL or AI_DEFAULT_MODELS["claude"]

    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def model_name(self) -> str:
        return self._model

    async def generate(self, request: GenerateRequest) -> str:
        key = (settings.ANTHROPIC_API_KEY or "").strip()
        if not key:
            raise AIUnavailableError("Anthropic API anahtarı yapılandırılmamış")

        system_parts: list[str] = []
        messages: list[dict] = []
        for msg in request.messages:
            if msg.role == "system":
                system_parts.append(msg.content)
                continue
            if msg.role not in ("user", "assistant"):
                continue
            messages.append({"role": msg.role, "content": msg.content})
        if not messages:
            raise AIProviderError("Claude için mesaj listesi boş")

        payload: dict = {
            "model": self._model,
            "max_tokens": settings.AI_MAX_TOKENS,
            "temperature": settings.AI_TEMPERATURE,
            "messages": messages,
        }
        if system_parts:
            payload["system"] = " ".join(system_parts)

        data = await post_json(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            payload=payload,
            provider_label="claude",
        )
        try:
            blocks = data["content"]
            texts = [
                b.get("text", "")
                for b in blocks
                if isinstance(b, dict) and b.get("type") == "text"
            ]
            text = "".join(texts).strip()
        except (KeyError, TypeError) as exc:
            raise AIProviderError("Claude yanıtı parse edilemedi") from exc
        if not text:
            raise AIProviderError("Claude boş yanıt döndü")
        return text
