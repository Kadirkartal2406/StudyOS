"""
StudyOS — StudySession Repository
Pomodoro oturumu tablosuna özel veri erişim işlemleri.
"""

import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_plan import StudyPlan
from app.models.study_session import StudySession, StudySessionStatus
from app.repositories.base import BaseRepository

_ACTIVE_STATUSES = (StudySessionStatus.RUNNING, StudySessionStatus.PAUSED)


class StudySessionRepository(BaseRepository[StudySession]):
    def __init__(self, db: AsyncSession):
        super().__init__(StudySession, db)

    async def get_by_id_for_user(
        self, session_id: uuid.UUID, user_id: uuid.UUID
    ) -> StudySession | None:
        result = await self.db.execute(
            select(StudySession).where(
                StudySession.id == session_id,
                StudySession.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_active_for_user(self, user_id: uuid.UUID) -> StudySession | None:
        """Kullanıcının running/paused durumundaki tek aktif oturumunu döner."""
        result = await self.db.execute(
            select(StudySession)
            .where(
                StudySession.user_id == user_id,
                StudySession.status.in_(_ACTIVE_STATUSES),
            )
            .order_by(StudySession.started_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_for_user_on_date(
        self, user_id: uuid.UUID, session_date: date
    ) -> list[StudySession]:
        """Belirtilen gün başlayan oturumları (started_at tarihine göre) listeler."""
        result = await self.db.execute(
            select(StudySession)
            .where(
                StudySession.user_id == user_id,
                func.date(StudySession.started_at) == session_date,
            )
            .order_by(StudySession.started_at.desc())
        )
        return list(result.scalars().all())

    async def list_history(
        self,
        user_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
        date_from: date | None = None,
        date_to: date | None = None,
        study_plan_id: uuid.UUID | None = None,
        status: StudySessionStatus | None = None,
        search: str | None = None,
    ) -> tuple[list[StudySession], int]:
        """Sayfalı oturum geçmişi; plan adı araması JOIN ile (Sprint-1.7)."""
        filters = [StudySession.user_id == user_id]
        if date_from is not None:
            filters.append(func.date(StudySession.started_at) >= date_from)
        if date_to is not None:
            filters.append(func.date(StudySession.started_at) <= date_to)
        if study_plan_id is not None:
            filters.append(StudySession.study_plan_id == study_plan_id)
        if status is not None:
            filters.append(StudySession.status == status)

        stmt = select(StudySession)
        count_stmt = select(func.count()).select_from(StudySession)

        if search:
            # Plan başlığında ILIKE; plansız oturumlar aramaya dahil edilmez.
            like = f"%{search}%"
            stmt = stmt.join(
                StudyPlan, StudySession.study_plan_id == StudyPlan.id, isouter=False
            ).where(StudyPlan.title.ilike(like), *filters)
            count_stmt = (
                select(func.count())
                .select_from(StudySession)
                .join(StudyPlan, StudySession.study_plan_id == StudyPlan.id, isouter=False)
                .where(StudyPlan.title.ilike(like), *filters)
            )
        else:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        count_result = await self.db.execute(count_stmt)
        total = int(count_result.scalar_one())

        offset = (page - 1) * page_size
        result = await self.db.execute(
            stmt.order_by(StudySession.started_at.desc()).offset(offset).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def list_completed_between(
        self,
        user_id: uuid.UUID,
        started_from: datetime,
        started_to: datetime,
    ) -> list[StudySession]:
        """Tamamlanmış oturumları [started_from, started_to) aralığında döner."""
        result = await self.db.execute(
            select(StudySession).where(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
                StudySession.started_at >= started_from,
                StudySession.started_at < started_to,
            )
        )
        return list(result.scalars().all())
