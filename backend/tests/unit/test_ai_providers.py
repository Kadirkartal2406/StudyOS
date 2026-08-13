"""
StudyOS — AI Provider unit tests (Sprint-2.4)
Mock HTTP; gerçek API çağrısı yok.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import AIProviderError, AIRateLimitError, AIUnavailableError
from app.providers.ai.base import (
    ChatMessageDTO,
    GenerateRequest,
    NullAIProvider,
    create_provider,
    generate_with_fallback,
    get_ai_provider,
)
from app.providers.ai.gemini_provider import GeminiProvider
from app.providers.ai.http_transport import map_http_error


def _req(text: str = "Merhaba") -> GenerateRequest:
    return GenerateRequest(
        messages=[
            ChatMessageDTO(role="system", content="Sen bir koçsun."),
            ChatMessageDTO(role="user", content=text),
        ],
        context={"goals": {"active_count": 0}},
    )


def test_map_http_error_429_rate_limit():
    err = map_http_error(429, "rate limit exceeded")
    assert isinstance(err, AIRateLimitError)


def test_create_provider_unknown_returns_null():
    assert create_provider("unknown").provider_name == "null"


def test_get_ai_provider_default_null():
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.AI_PROVIDER = "null"
        mock_settings.AI_MODEL = ""
        p = get_ai_provider()
        assert p.provider_name == "null"


def test_gemini_ignores_template_placeholder_model():
    from app.core.constants import AI_DEFAULT_MODELS
    from app.providers.ai.base import sanitize_ai_model

    assert sanitize_ai_model("template") is None
    assert sanitize_ai_model("TEMPLATE") is None
    assert sanitize_ai_model("gemini-3.5-flash-lite") == "gemini-3.5-flash-lite"

    with patch("app.providers.ai.gemini_provider.settings") as s:
        s.AI_MODEL = ""
        provider = GeminiProvider(model="template")
        other = GeminiProvider(model="gpt-4o-mini")
    assert provider.model_name == AI_DEFAULT_MODELS["gemini"]
    assert other.model_name == AI_DEFAULT_MODELS["gemini"]
    assert "template" not in provider._candidate_models()


def test_get_ai_provider_gemini_with_template_model_uses_default():
    from app.core.constants import AI_DEFAULT_MODELS

    with (
        patch("app.core.config.settings") as mock_settings,
        patch("app.providers.ai.gemini_provider.settings") as gemini_settings,
    ):
        mock_settings.AI_PROVIDER = "gemini"
        mock_settings.AI_MODEL = ""
        gemini_settings.AI_MODEL = ""
        p = get_ai_provider(preferred="gemini", model="template")
    assert p.provider_name == "gemini"
    assert p.model_name == AI_DEFAULT_MODELS["gemini"]
    assert p.model_name != "template"


@pytest.mark.asyncio
async def test_gemini_generate_parses_response():
    provider = GeminiProvider(model="gemini-2.0-flash")
    fake = {
        "candidates": [
            {"content": {"parts": [{"text": "Merhaba öğrencim"}]}}
        ]
    }
    with (
        patch("app.providers.ai.gemini_provider.settings") as s,
        patch(
            "app.providers.ai.gemini_provider.post_json",
            new_callable=AsyncMock,
            return_value=fake,
        ),
    ):
        s.GEMINI_API_KEY = "test-key-not-logged"
        s.AI_TEMPERATURE = 0.7
        s.AI_MAX_TOKENS = 256
        text = await provider.generate(_req())
    assert "Merhaba" in text


@pytest.mark.asyncio
async def test_gemini_missing_key():
    provider = GeminiProvider()
    with patch("app.providers.ai.gemini_provider.settings") as s:
        s.GEMINI_API_KEY = ""
        with pytest.raises(AIUnavailableError):
            await provider.generate(_req())


@pytest.mark.asyncio
async def test_generate_with_fallback_to_null():
    with patch(
        "app.providers.ai.base.get_ai_provider"
    ) as mock_get:
        failing = AsyncMock()
        failing.provider_name = "gemini"
        failing.model_name = "x"
        failing.generate = AsyncMock(
            side_effect=AIProviderError("fail", code="AI_PROVIDER_ERROR")
        )
        mock_get.return_value = failing

        with patch("app.core.config.settings") as s:
            s.AI_FALLBACK_PROVIDER = "null"
            s.DEBUG = True
            result = await generate_with_fallback(_req(), preferred="gemini")

    assert result.used_fallback is True
    assert result.provider == "null"
    assert len(result.text) > 0


@pytest.mark.asyncio
async def test_null_provider_still_works():
    text = await NullAIProvider().generate(
        GenerateRequest(
            messages=[ChatMessageDTO(role="user", content="Hedef?")],
            context={
                "goals": {
                    "active_count": 1,
                    "top_title": "500 soru",
                    "top_progress": 40.0,
                    "top_remaining": 300.0,
                },
                "insights": {},
                "statistics": {"streak_days": 2},
            },
        )
    )
    assert "500 soru" in text
