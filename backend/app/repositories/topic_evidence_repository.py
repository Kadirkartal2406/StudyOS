"""
StudyOS — TopicEvidence Repository
LOS Module 1 — Evidence Engine storage layer.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_evidence import EvidenceCategory, EvidenceHorizon, TopicEvidence
from app.repositories.base import BaseRepository


class TopicEvidenceRepository(BaseRepository[TopicEvidence]):
    def __init__(self, db: AsyncSession):
        super().__init__(TopicEvidence, db)

    # ── Write ──────────────────────────────────────────────────────

    async def add_evidence(self, evidence: TopicEvidence) -> TopicEvidence:
        self.db.add(evidence)
        await self.db.flush()
        return evidence

    async def add_many(self, items: list[TopicEvidence]) -> list[TopicEvidence]:
        for item in items:
            self.db.add(item)
        await self.db.flush()
        return items

    # ── Read: Topic scope ──────────────────────────────────────────

    async def list_for_topic(
        self,
        user_id: uuid.UUID,
        topic_code: str,
        *,
        category: EvidenceCategory | None = None,
        since: datetime | None = None,
        limit: int = 200,
    ) -> list[TopicEvidence]:
        stmt = select(TopicEvidence).where(
            TopicEvidence.user_id == user_id,
            TopicEvidence.topic_code == topic_code,
        )
        if category is not None:
            stmt = stmt.where(TopicEvidence.category == category)
        if since is not None:
            stmt = stmt.where(TopicEvidence.occurred_at >= since)
        stmt = stmt.order_by(TopicEvidence.occurred_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_for_subject(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        *,
        category: EvidenceCategory | None = None,
        since: datetime | None = None,
        limit: int = 500,
    ) -> list[TopicEvidence]:
        stmt = select(TopicEvidence).where(
            TopicEvidence.user_id == user_id,
            TopicEvidence.subject_code == subject_code,
        )
        if category is not None:
            stmt = stmt.where(TopicEvidence.category == category)
        if since is not None:
            stmt = stmt.where(TopicEvidence.occurred_at >= since)
        stmt = stmt.order_by(TopicEvidence.occurred_at.desc()).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ── Aggregate helpers ──────────────────────────────────────────

    async def topic_evidence_count(
        self,
        user_id: uuid.UUID,
        topic_code: str,
        *,
        since: datetime | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(TopicEvidence).where(
            TopicEvidence.user_id == user_id,
            TopicEvidence.topic_code == topic_code,
        )
        if since is not None:
            stmt = stmt.where(TopicEvidence.occurred_at >= since)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def distinct_topic_count(self, user_id: uuid.UUID) -> int:
        """Kaç farklı topic'te en az 1 evidence var?"""
        stmt = (
            select(func.count(func.distinct(TopicEvidence.topic_code)))
            .select_from(TopicEvidence)
            .where(
                TopicEvidence.user_id == user_id,
                TopicEvidence.topic_code != "unbound",
            )
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def weighted_accuracy_for_topic(
        self,
        user_id: uuid.UUID,
        topic_code: str,
        *,
        since: datetime | None = None,
        horizon: EvidenceHorizon | None = None,
    ) -> float | None:
        """Quality-weighted average value for PERFORMANCE evidence."""
        stmt = select(TopicEvidence).where(
            TopicEvidence.user_id == user_id,
            TopicEvidence.topic_code == topic_code,
            TopicEvidence.category == EvidenceCategory.PERFORMANCE,
        )
        if since is not None:
            stmt = stmt.where(TopicEvidence.occurred_at >= since)
        if horizon is not None:
            stmt = stmt.where(TopicEvidence.horizon == horizon)
        result = await self.db.execute(stmt)
        rows = list(result.scalars().all())
        if not rows:
            return None
        total_w = sum(r.quality_weight for r in rows)
        if total_w == 0:
            return None
        return sum(r.value * r.quality_weight for r in rows) / total_w

    async def total_effort_minutes_for_topic(
        self,
        user_id: uuid.UUID,
        topic_code: str,
        *,
        since: datetime | None = None,
    ) -> float:
        """Raw effort minutes accumulated for topic (from EFFORT metadata)."""
        stmt = select(TopicEvidence).where(
            TopicEvidence.user_id == user_id,
            TopicEvidence.topic_code == topic_code,
            TopicEvidence.category == EvidenceCategory.EFFORT,
        )
        if since is not None:
            stmt = stmt.where(TopicEvidence.occurred_at >= since)
        result = await self.db.execute(stmt)
        rows = list(result.scalars().all())
        total = 0.0
        for r in rows:
            total += float(r.metadata_.get("actual_minutes", 0))
        return total

    async def last_evidence_at(
        self, user_id: uuid.UUID, topic_code: str
    ) -> datetime | None:
        stmt = (
            select(func.max(TopicEvidence.occurred_at))
            .select_from(TopicEvidence)
            .where(
                TopicEvidence.user_id == user_id,
                TopicEvidence.topic_code == topic_code,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def already_ingested(
        self, source_type: str, source_id: uuid.UUID
    ) -> bool:
        """Aynı kaynak tekrar işlenmesini önle (idempotency)."""
        stmt = (
            select(func.count())
            .select_from(TopicEvidence)
            .where(
                TopicEvidence.source_type == source_type,
                TopicEvidence.source_id == source_id,
            )
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one()) > 0
