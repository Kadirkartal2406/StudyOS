"""
StudyOS — StudyPlan Repository
Çalışma planı tablosuna özel veri erişim işlemleri.
Tüm sorgular soft-delete edilmiş (`deleted_at IS NOT NULL`) kayıtları hariç tutar.
"""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_plan import StudyPlan
from app.repositories.base import BaseRepository


class StudyPlanRepository(BaseRepository[StudyPlan]):
    def __init__(self, db: AsyncSession):
        super().__init__(StudyPlan, db)

    async def get_by_id_for_user(self, plan_id: uuid.UUID, user_id: uuid.UUID) -> StudyPlan | None:
        """Plan sahibi doğrulaması ile tekil kayıt getirir; silinmişleri hariç tutar."""
        result = await self.db.execute(
            select(StudyPlan).where(
                StudyPlan.id == plan_id,
                StudyPlan.user_id == user_id,
                StudyPlan.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: uuid.UUID, study_date: date | None = None
    ) -> list[StudyPlan]:
        """Kullanıcının planlarını (opsiyonel tarih filtresiyle) order_index'e göre sıralı döner."""
        query = select(StudyPlan).where(
            StudyPlan.user_id == user_id, StudyPlan.deleted_at.is_(None)
        )
        if study_date is not None:
            query = query.where(StudyPlan.study_date == study_date)
        query = query.order_by(StudyPlan.study_date, StudyPlan.order_index)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_overlapping(
        self,
        user_id: uuid.UUID,
        study_date: date,
        exclude_id: uuid.UUID | None = None,
    ) -> list[StudyPlan]:
        """Saat çakışması kontrolü için aynı gün, zaman aralığı tanımlı diğer planları döner."""
        query = select(StudyPlan).where(
            StudyPlan.user_id == user_id,
            StudyPlan.study_date == study_date,
            StudyPlan.deleted_at.is_(None),
            StudyPlan.planned_start_time.is_not(None),
            StudyPlan.planned_end_time.is_not(None),
        )
        if exclude_id is not None:
            query = query.where(StudyPlan.id != exclude_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def next_order_index(self, user_id: uuid.UUID, study_date: date) -> int:
        """Belirtilen gün için bir sonraki order_index değerini hesaplar."""
        result = await self.db.execute(
            select(func.max(StudyPlan.order_index)).where(
                StudyPlan.user_id == user_id,
                StudyPlan.study_date == study_date,
                StudyPlan.deleted_at.is_(None),
            )
        )
        current_max = result.scalar_one_or_none()
        return 0 if current_max is None else current_max + 1

    async def soft_delete(self, plan: StudyPlan) -> None:
        plan.deleted_at = datetime.now(UTC)
        await self.db.flush()
