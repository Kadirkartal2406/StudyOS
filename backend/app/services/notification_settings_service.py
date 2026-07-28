"""
StudyOS — Notification Settings Service
Sprint-1.8 — tercihler + FCM token altyapısı (push yok).
"""

import uuid
from datetime import UTC, datetime, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_preference import NotificationPreference
from app.repositories.notification_preference_repository import (
    NotificationPreferenceRepository,
)
from app.schemas.notification_settings import (
    FcmTokenUpdate,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
)


class NotificationSettingsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationPreferenceRepository(db)

    async def get_or_create(self, user_id: uuid.UUID) -> NotificationPreference:
        pref = await self.repo.get_by_user_id(user_id)
        if pref is not None:
            return pref
        pref = NotificationPreference(
            user_id=user_id,
            reminder_time=time(20, 0),
        )
        return await self.repo.add(pref)

    async def get_settings(self, user_id: uuid.UUID) -> NotificationSettingsRead:
        pref = await self.get_or_create(user_id)
        return self._to_read(pref)

    async def update_settings(
        self, user_id: uuid.UUID, data: NotificationSettingsUpdate
    ) -> NotificationSettingsRead:
        pref = await self.get_or_create(user_id)
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            setattr(pref, key, value)
        await self.db.flush()
        return self._to_read(pref)

    async def update_fcm_token(
        self, user_id: uuid.UUID, data: FcmTokenUpdate
    ) -> NotificationSettingsRead:
        pref = await self.get_or_create(user_id)
        pref.fcm_token = data.fcm_token
        pref.fcm_token_updated_at = datetime.now(UTC)
        await self.db.flush()
        return self._to_read(pref)

    @staticmethod
    def _to_read(pref: NotificationPreference) -> NotificationSettingsRead:
        return NotificationSettingsRead(
            pomodoro_enabled=pref.pomodoro_enabled,
            long_break_enabled=pref.long_break_enabled,
            daily_reminder_enabled=pref.daily_reminder_enabled,
            daily_goal_enabled=pref.daily_goal_enabled,
            streak_reminder_enabled=pref.streak_reminder_enabled,
            revision_reminders_enabled=pref.revision_reminders_enabled,
            achievement_notifications_enabled=pref.achievement_notifications_enabled,
            widget_auto_update_enabled=pref.widget_auto_update_enabled,
            reminder_time=pref.reminder_time,
            quiet_hours_enabled=pref.quiet_hours_enabled,
            quiet_hours_start=pref.quiet_hours_start,
            quiet_hours_end=pref.quiet_hours_end,
            has_fcm_token=bool(pref.fcm_token),
        )
