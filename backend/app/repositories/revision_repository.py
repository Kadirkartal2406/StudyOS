"""
StudyOS — Revision Repository
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.revision import (
    RevisionItem,
    RevisionItemStatus,
    RevisionReview,
    RevisionSchedule,
    RevisionSourceType,
)
from app.repositories.base import BaseRepository


class RevisionRepository(BaseRepository[RevisionItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(RevisionItem, db)

    def _base_filter(self, user_id: uuid.UUID):
        return and_(
            RevisionItem.user_id == user_id,
            RevisionItem.deleted_at.is_(None),
        )

    @staticmethod
    def _subject_filter(subjects: set[str] | None):
        if not subjects:
            return None
        lowered = {s.lower() for s in subjects}
        return func.lower(RevisionItem.subject).in_(lowered)

    async def get_for_user(
        self, item_id: uuid.UUID, user_id: uuid.UUID
    ) -> RevisionItem | None:
        result = await self.db.execute(
            select(RevisionItem)
            .options(
                selectinload(RevisionItem.schedule),
                selectinload(RevisionItem.reviews),
            )
            .where(self._base_filter(user_id), RevisionItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        status: RevisionItemStatus | None = None,
        subject: str | None = None,
        source_type: RevisionSourceType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[RevisionItem]:
        stmt = (
            select(RevisionItem)
            .options(selectinload(RevisionItem.schedule))
            .where(self._base_filter(user_id))
            .order_by(RevisionItem.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status is not None:
            stmt = stmt.where(RevisionItem.status == status)
        if subject:
            stmt = stmt.where(RevisionItem.subject.ilike(f"%{subject}%"))
        if source_type is not None:
            stmt = stmt.where(RevisionItem.source_type == source_type)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def find_seed_duplicate(
        self,
        user_id: uuid.UUID,
        *,
        source_type: RevisionSourceType,
        subject: str,
        source_id: uuid.UUID | None = None,
        topic: str | None = None,
    ) -> RevisionItem | None:
        stmt = select(RevisionItem).where(
            self._base_filter(user_id),
            RevisionItem.source_type == source_type,
            RevisionItem.subject == subject,
            RevisionItem.status == RevisionItemStatus.ACTIVE,
        )
        if source_id is not None:
            stmt = stmt.where(RevisionItem.source_id == source_id)
        else:
            stmt = stmt.where(RevisionItem.source_id.is_(None))
        if topic:
            stmt = stmt.where(RevisionItem.topic == topic)
        else:
            stmt = stmt.where(RevisionItem.topic.is_(None))
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none()

    async def list_due(
        self,
        user_id: uuid.UUID,
        *,
        until: datetime,
        overdue_only: bool = False,
        since: datetime | None = None,
        limit: int = 100,
        subjects: set[str] | None = None,
    ) -> list[RevisionItem]:
        now = datetime.now(UTC)
        conditions = [
            self._base_filter(user_id),
            RevisionItem.status == RevisionItemStatus.ACTIVE,
            RevisionSchedule.due_at <= until,
        ]
        subj = self._subject_filter(subjects)
        if subj is not None:
            conditions.append(subj)
        stmt = (
            select(RevisionItem)
            .join(RevisionSchedule, RevisionSchedule.revision_item_id == RevisionItem.id)
            .options(selectinload(RevisionItem.schedule))
            .where(*conditions)
            .order_by(RevisionSchedule.due_at.asc())
            .limit(limit)
        )
        if overdue_only:
            stmt = stmt.where(RevisionSchedule.due_at < now.replace(hour=0, minute=0, second=0, microsecond=0))
        if since is not None:
            stmt = stmt.where(RevisionSchedule.due_at >= since)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def count_active(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(RevisionItem)
            .where(
                self._base_filter(user_id),
                RevisionItem.status == RevisionItemStatus.ACTIVE,
            )
        )
        return int(result.scalar_one())

    async def count_mastered(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(RevisionItem)
            .where(
                self._base_filter(user_id),
                RevisionItem.status == RevisionItemStatus.MASTERED,
            )
        )
        return int(result.scalar_one())

    async def count_due_between(
        self,
        user_id: uuid.UUID,
        start: datetime,
        end: datetime,
        *,
        subjects: set[str] | None = None,
    ) -> int:
        conditions = [
            self._base_filter(user_id),
            RevisionItem.status == RevisionItemStatus.ACTIVE,
            RevisionSchedule.due_at >= start,
            RevisionSchedule.due_at < end,
        ]
        subj = self._subject_filter(subjects)
        if subj is not None:
            conditions.append(subj)
        result = await self.db.execute(
            select(func.count())
            .select_from(RevisionSchedule)
            .join(RevisionItem, RevisionItem.id == RevisionSchedule.revision_item_id)
            .where(*conditions)
        )
        return int(result.scalar_one())

    async def count_overdue(
        self,
        user_id: uuid.UUID,
        before: datetime,
        *,
        subjects: set[str] | None = None,
    ) -> int:
        conditions = [
            self._base_filter(user_id),
            RevisionItem.status == RevisionItemStatus.ACTIVE,
            RevisionSchedule.due_at < before,
        ]
        subj = self._subject_filter(subjects)
        if subj is not None:
            conditions.append(subj)
        result = await self.db.execute(
            select(func.count())
            .select_from(RevisionSchedule)
            .join(RevisionItem, RevisionItem.id == RevisionSchedule.revision_item_id)
            .where(*conditions)
        )
        return int(result.scalar_one())

    async def count_reviews_between(
        self, user_id: uuid.UUID, start: datetime, end: datetime
    ) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(RevisionReview)
            .join(RevisionItem, RevisionItem.id == RevisionReview.revision_item_id)
            .where(
                self._base_filter(user_id),
                RevisionReview.reviewed_at >= start,
                RevisionReview.reviewed_at < end,
            )
        )
        return int(result.scalar_one())

    async def average_difficulty(self, user_id: uuid.UUID) -> float:
        result = await self.db.execute(
            select(func.avg(RevisionItem.difficulty)).where(
                self._base_filter(user_id),
                RevisionItem.status == RevisionItemStatus.ACTIVE,
            )
        )
        val = result.scalar_one()
        return float(val or 0)

    async def average_ease(self, user_id: uuid.UUID) -> float:
        result = await self.db.execute(
            select(func.avg(RevisionSchedule.ease_factor))
            .select_from(RevisionSchedule)
            .join(RevisionItem, RevisionItem.id == RevisionSchedule.revision_item_id)
            .where(
                self._base_filter(user_id),
                RevisionItem.status == RevisionItemStatus.ACTIVE,
            )
        )
        val = result.scalar_one()
        return float(val or 0)

    async def heatmap_counts(
        self, user_id: uuid.UUID, start: date, end: date
    ) -> dict[date, int]:
        start_dt = datetime.combine(start, datetime.min.time(), tzinfo=UTC)
        end_dt = datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=UTC)
        day_col = func.date_trunc("day", RevisionReview.reviewed_at)
        result = await self.db.execute(
            select(day_col, func.count())
            .select_from(RevisionReview)
            .join(RevisionItem, RevisionItem.id == RevisionReview.revision_item_id)
            .where(
                self._base_filter(user_id),
                RevisionReview.reviewed_at >= start_dt,
                RevisionReview.reviewed_at < end_dt,
            )
            .group_by(day_col)
        )
        out: dict[date, int] = {}
        for truncated, count in result.all():
            if truncated is None:
                continue
            d = truncated.date() if hasattr(truncated, "date") else truncated
            out[d] = int(count)
        return out

    async def next_due_item(
        self, user_id: uuid.UUID, *, subjects: set[str] | None = None
    ) -> RevisionItem | None:
        now = datetime.now(UTC)
        conditions = [
            self._base_filter(user_id),
            RevisionItem.status == RevisionItemStatus.ACTIVE,
            RevisionSchedule.due_at >= now,
        ]
        subj = self._subject_filter(subjects)
        if subj is not None:
            conditions.append(subj)
        result = await self.db.execute(
            select(RevisionItem)
            .join(RevisionSchedule, RevisionSchedule.revision_item_id == RevisionItem.id)
            .options(selectinload(RevisionItem.schedule))
            .where(*conditions)
            .order_by(RevisionSchedule.due_at.asc())
            .limit(1)
        )
        item = result.scalar_one_or_none()
        if item is not None:
            return item
        # overdue first
        overdue_conditions = [
            self._base_filter(user_id),
            RevisionItem.status == RevisionItemStatus.ACTIVE,
        ]
        if subj is not None:
            overdue_conditions.append(subj)
        result = await self.db.execute(
            select(RevisionItem)
            .join(RevisionSchedule, RevisionSchedule.revision_item_id == RevisionItem.id)
            .options(selectinload(RevisionItem.schedule))
            .where(*overdue_conditions)
            .order_by(RevisionSchedule.due_at.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()
