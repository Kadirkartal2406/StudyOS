"""
StudyOS — Notification Decision Service
Sprint 13 — LOS policy'ye göre bildirim adayları üretir (push göndermez).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notification_settings_service import NotificationSettingsService
from app.services.revision_service import RevisionService

logger = logging.getLogger(__name__)


class NotificationDecisionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = NotificationSettingsService(db)
        self.revision = RevisionService(db)

    async def evaluate(self, user_id: uuid.UUID) -> list[dict]:
        """
        Bildirim adaylarını değerlendir.
        Push göndermez; yalnızca karar listesi döner.
        """
        candidates: list[dict] = []
        try:
            pref = await self.settings.get_or_create(user_id)
        except Exception:
            logger.exception("notification preferences load failed user=%s", user_id)
            return []

        if self._in_quiet_hours(pref):
            return []

        # Revision due
        if getattr(pref, "revision_reminders_enabled", True):
            try:
                summary = await self.revision.dashboard_summary(user_id)
                due = summary.due_today or 0
                if due > 0:
                    overdue_bit = ""
                    if summary.overdue_days and summary.overdue_days > 0:
                        overdue_bit = f" ({summary.overdue_days} gün gecikmiş)"
                    title = summary.next_title or "Tekrar"
                    candidates.append(
                        {
                            "type": "revision_due",
                            "title": "Tekrar zamanı!",
                            "body": f"Bugün {due} tekrar bekliyor{overdue_bit}: {title}",
                            "deep_link": "/revisions",
                        }
                    )
            except Exception:
                logger.exception("revision_due decision failed user=%s", user_id)

        return candidates

    @staticmethod
    def _in_quiet_hours(pref) -> bool:
        """Sessiz saatler açıksa ve şu an aralıktaysa True."""
        if not getattr(pref, "quiet_hours_enabled", False):
            return False
        start: time | None = getattr(pref, "quiet_hours_start", None)
        end: time | None = getattr(pref, "quiet_hours_end", None)
        if start is None or end is None:
            return False
        now = datetime.now(UTC).time().replace(tzinfo=None)
        if start <= end:
            return start <= now <= end
        # Gece yarısını geçen aralık (örn. 22:00–07:00)
        return now >= start or now <= end
