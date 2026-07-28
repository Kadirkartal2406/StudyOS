"""
StudyOS — NotificationPreference Modeli
Bildirim / widget tercihleri. Bkz. docs/architecture/database-design.md §1.14b
Sprint-1.8 (Meeting-016) — Inbox yok; yalnızca ayarlar + FCM token altyapısı.
Ayrı tablo; User JSON gömülmez (C1).
"""

import uuid
from datetime import UTC, datetime, time

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class NotificationPreference(Base):
    """Kullanıcı başına tek satır bildirim tercihi."""

    __tablename__ = "notification_preferences"
    __table_args__ = (UniqueConstraint("user_id", name="uq_notification_preferences_user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    pomodoro_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    long_break_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    daily_reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    daily_goal_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    streak_reminder_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Sprint-2.8 N1 — tekrar hatırlatıcı toggle
    revision_reminders_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Sprint-2.9 L1 — rozet bildirim toggle
    achievement_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    widget_auto_update_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Sprint-2.3 — AI Memory Engine gizlilik anahtarı (C1).
    ai_memory_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Sprint-2.4 E2 — kullanıcı provider/model tercihi (API key değil).
    ai_preferred_provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ai_preferred_model: Mapped[str | None] = mapped_column(String(120), nullable=True)

    # Günlük çalışma hatırlatma saati (yerel saat; istemci TZ ile yorumlar).
    reminder_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quiet_hours_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    quiet_hours_end: Mapped[time | None] = mapped_column(Time, nullable=True)

    # FCM token altyapısı (A1) — gerçek push sonraki sprint.
    fcm_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    fcm_token_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
