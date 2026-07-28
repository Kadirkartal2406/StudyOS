"""
StudyOS — PlannerDraft Repository
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.planner_draft import PlannerDraft, PlannerDraftStatus
from app.repositories.base import BaseRepository


class PlannerDraftRepository(BaseRepository[PlannerDraft]):
    def __init__(self, db: AsyncSession):
        super().__init__(PlannerDraft, db)

    async def get_for_user(
        self, draft_id: uuid.UUID, user_id: uuid.UUID
    ) -> PlannerDraft | None:
        result = await self.db.execute(
            select(PlannerDraft).where(
                PlannerDraft.id == draft_id, PlannerDraft.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def latest_draft(
        self, user_id: uuid.UUID, *, status: PlannerDraftStatus | None = None
    ) -> PlannerDraft | None:
        stmt = (
            select(PlannerDraft)
            .where(PlannerDraft.user_id == user_id)
            .order_by(PlannerDraft.created_at.desc())
            .limit(1)
        )
        if status is not None:
            stmt = stmt.where(PlannerDraft.status == status)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pending(self, user_id: uuid.UUID) -> list[PlannerDraft]:
        """Sprint-9: return all pending (Living Plan) suggestions for the user."""
        result = await self.db.execute(
            select(PlannerDraft)
            .where(
                PlannerDraft.user_id == user_id,
                PlannerDraft.status == PlannerDraftStatus.PENDING,
            )
            .order_by(PlannerDraft.created_at.desc())
        )
        return list(result.scalars().all())
