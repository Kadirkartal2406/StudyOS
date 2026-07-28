"""
StudyOS — AI Settings Service (Sprint-2.4 E2)
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import AI_DEFAULT_MODELS
from app.core.exceptions import ValidationError
from app.providers.ai.base import get_ai_provider
from app.schemas.ai_settings import AiSettingsRead, AiSettingsUpdate
from app.services.notification_settings_service import NotificationSettingsService

_ALLOWED = frozenset({"null", "gemini", "openai", "claude"})


class AiSettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notif = NotificationSettingsService(db)

    def _effective(self, preferred: str | None, preferred_model: str | None) -> tuple[str, str | None]:
        provider = get_ai_provider(preferred=preferred, model=preferred_model)
        return provider.provider_name, provider.model_name

    async def get_settings(self, user_id: uuid.UUID) -> AiSettingsRead:
        pref = await self.notif.get_or_create(user_id)
        preferred = pref.ai_preferred_provider
        preferred_model = pref.ai_preferred_model
        effective_provider, effective_model = self._effective(preferred, preferred_model)
        env_provider = (settings.AI_PROVIDER or "null").strip().lower()
        debug = {}
        if settings.DEBUG:
            debug = {
                "env_provider": env_provider,
                "has_gemini_key": bool(settings.GEMINI_API_KEY),
                "has_openai_key": bool(settings.OPENAI_API_KEY),
                "has_anthropic_key": bool(settings.ANTHROPIC_API_KEY),
                "default_models": dict(AI_DEFAULT_MODELS),
                "timeout_seconds": settings.AI_TIMEOUT_SECONDS,
                "retry_count": settings.AI_RETRY_COUNT,
            }
        return AiSettingsRead(
            preferred_provider=preferred,
            preferred_model=preferred_model,
            effective_provider=effective_provider,
            effective_model=effective_model,
            fallback_provider=(settings.AI_FALLBACK_PROVIDER or "null"),
            streaming_enabled=False,
            debug=debug,
        )

    async def update_settings(
        self, user_id: uuid.UUID, data: AiSettingsUpdate
    ) -> AiSettingsRead:
        pref = await self.notif.get_or_create(user_id)
        payload = data.model_dump(exclude_unset=True)
        if "preferred_provider" in payload:
            value = payload["preferred_provider"]
            if value is None or (isinstance(value, str) and not value.strip()):
                pref.ai_preferred_provider = None
            else:
                normalized = value.strip().lower()
                if normalized not in _ALLOWED:
                    raise ValidationError(
                        "Geçersiz provider (null|gemini|openai|claude)",
                        field="preferred_provider",
                    )
                pref.ai_preferred_provider = normalized
        if "preferred_model" in payload:
            model = payload["preferred_model"]
            pref.ai_preferred_model = (
                model.strip() if isinstance(model, str) and model.strip() else None
            )
        await self.db.flush()
        return await self.get_settings(user_id)
