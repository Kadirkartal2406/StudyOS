"""
StudyOS — Notification Preference Şemaları
Sprint-1.8 — GET/PUT /notification-settings
"""

from datetime import time

from pydantic import BaseModel, Field, model_validator


class NotificationSettingsRead(BaseModel):
    pomodoro_enabled: bool
    long_break_enabled: bool
    daily_reminder_enabled: bool
    daily_goal_enabled: bool
    streak_reminder_enabled: bool
    revision_reminders_enabled: bool = True
    achievement_notifications_enabled: bool = True
    widget_auto_update_enabled: bool
    reminder_time: time | None = None
    quiet_hours_enabled: bool
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None
    has_fcm_token: bool = False

    model_config = {"from_attributes": True}


class NotificationSettingsUpdate(BaseModel):
    pomodoro_enabled: bool | None = None
    long_break_enabled: bool | None = None
    daily_reminder_enabled: bool | None = None
    daily_goal_enabled: bool | None = None
    streak_reminder_enabled: bool | None = None
    revision_reminders_enabled: bool | None = None
    achievement_notifications_enabled: bool | None = None
    widget_auto_update_enabled: bool | None = None
    reminder_time: time | None = None
    quiet_hours_enabled: bool | None = None
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None

    @model_validator(mode="after")
    def _validate_quiet_hours(self) -> "NotificationSettingsUpdate":
        if self.quiet_hours_enabled is True:
            if self.quiet_hours_start is None or self.quiet_hours_end is None:
                raise ValueError(
                    "Sessiz saatler açıkken quiet_hours_start ve quiet_hours_end zorunludur"
                )
        return self


class FcmTokenUpdate(BaseModel):
    """FCM token kaydı (push gönderimi sonraki sprint)."""

    fcm_token: str = Field(min_length=10, max_length=512)
