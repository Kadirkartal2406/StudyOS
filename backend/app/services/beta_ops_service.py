"""Sprint 21 RC — Analytics + Feedback services (feature freeze uyumlu)."""

from __future__ import annotations

import logging
import uuid
from collections import Counter
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.models.beta_ops import AnalyticsEvent, BetaFeedback
from app.schemas.beta_ops import (
    AnalyticsBatchRequest,
    AnalyticsBatchResult,
    AnalyticsDashboardRead,
    AnalyticsMetricCount,
    AnalyticsNamedCount,
    AnalyticsTrackRequest,
    AnalyticsTrackResult,
    BetaFeedbackCreate,
    BetaFeedbackRead,
)

logger = logging.getLogger("studyos.analytics")

_ALLOWED_KINDS = {"bug", "suggestion", "other"}

# Mevcut event adları (yeni event üretilmez; sadece okunur / alias)
_POMODORO_ALIASES = ("pomodoro_started", "pomodoro_start", "session_started")
_NEXT_ACTION_ALIASES = ("next_action_completed", "next_action_done")
_JOURNEY_ALIASES = ("journey_viewed", "journey_open")
_KNOWLEDGE_ALIASES = ("notebook_viewed", "knowledge_used")


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def track(
        self,
        data: AnalyticsTrackRequest,
        *,
        user_id: uuid.UUID | None,
    ) -> AnalyticsTrackResult:
        name = (data.name or "").strip().lower()
        if not name:
            raise ValidationError("event name gerekli")
        ev = AnalyticsEvent(
            user_id=user_id,
            name=name[:80],
            platform=data.platform,
            app_version=data.app_version,
            session_id=data.session_id,
            properties=data.properties or {},
        )
        self.db.add(ev)
        await self.db.flush()
        logger.info("analytics name=%s user=%s", name, user_id)
        return AnalyticsTrackResult(id=ev.id, name=ev.name, created_at=ev.created_at)

    async def track_batch(
        self,
        data: AnalyticsBatchRequest,
        *,
        user_id: uuid.UUID | None,
    ) -> AnalyticsBatchResult:
        n = 0
        for item in data.events[:50]:
            await self.track(item, user_id=user_id)
            n += 1
        return AnalyticsBatchResult(accepted=n)

    async def dashboard(self, *, days: int = 7) -> AnalyticsDashboardRead:
        """RC2 M22.4 — aggregation over existing analytics_events."""
        days = max(1, min(int(days), 90))
        since = datetime.now(UTC) - timedelta(days=days)

        result = await self.db.execute(
            select(AnalyticsEvent).where(AnalyticsEvent.created_at >= since)
        )
        rows = list(result.scalars().all())

        today = datetime.now(UTC).date()
        dau_users = {
            r.user_id
            for r in rows
            if r.user_id is not None and r.created_at.date() == today
        }
        sessions = {r.session_id for r in rows if r.session_id}

        def count_name(*names: str) -> int:
            wanted = {n.lower() for n in names}
            return sum(1 for r in rows if r.name.lower() in wanted)

        exam_c: Counter[str] = Counter()
        topic_c: Counter[str] = Counter()
        screen_c: Counter[str] = Counter()

        for r in rows:
            props = r.properties or {}
            exam = (
                props.get("exam")
                or props.get("exam_type")
                or props.get("active_exam")
            )
            if exam:
                exam_c[str(exam).lower()] += 1
            topic = props.get("topic_code") or props.get("topic")
            if topic:
                topic_c[str(topic)] += 1
            screen = props.get("screen") or props.get("screen_hint") or r.name
            screen_c[str(screen)] += 1

        drop_off = [
            AnalyticsNamedCount(
                name="assessment",
                count=max(
                    0,
                    count_name("assessment_started")
                    - count_name("assessment_finished"),
                ),
            ),
            AnalyticsNamedCount(
                name="quiz",
                count=max(
                    0,
                    count_name("quiz_generated") - count_name("quiz_finished"),
                ),
            ),
        ]

        name_totals = Counter(r.name for r in rows)

        return AnalyticsDashboardRead(
            days=days,
            dau=len(dau_users),
            session_count=len(sessions),
            assessment_completion=count_name("assessment_finished"),
            quiz_completion=count_name("quiz_finished"),
            pomodoro_started=count_name(*_POMODORO_ALIASES),
            next_action_completed=count_name(*_NEXT_ACTION_ALIASES),
            explain_used=count_name("explain_used"),
            knowledge_used=count_name(*_KNOWLEDGE_ALIASES),
            coach_viewed=count_name("coach_viewed"),
            journey_viewed=count_name(*_JOURNEY_ALIASES),
            exam_distribution=[
                AnalyticsNamedCount(name=k, count=v)
                for k, v in exam_c.most_common(20)
            ],
            topic_distribution=[
                AnalyticsNamedCount(name=k, count=v)
                for k, v in topic_c.most_common(30)
            ],
            screen_usage=[
                AnalyticsNamedCount(name=k, count=v)
                for k, v in screen_c.most_common(30)
            ],
            drop_off=drop_off,
            event_totals=[
                AnalyticsMetricCount(key=k, label=k, value=v)
                for k, v in name_totals.most_common(40)
            ],
        )


class BetaFeedbackService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID | None,
        data: BetaFeedbackCreate,
    ) -> BetaFeedbackRead:
        kind = (data.kind or "").strip().lower()
        if kind not in _ALLOWED_KINDS:
            raise ValidationError("kind: bug | suggestion | other")
        row = BetaFeedback(
            user_id=user_id,
            kind=kind,
            message=data.message.strip(),
            screen_hint=data.screen_hint,
            app_version=data.app_version,
            platform=data.platform,
            log_excerpt=(data.log_excerpt or "")[:8000] or None,
        )
        self.db.add(row)
        await self.db.flush()
        logger.info("beta_feedback kind=%s user=%s", kind, user_id)
        return BetaFeedbackRead.model_validate(row)
