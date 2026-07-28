"""
StudyOS — StudyResource Service
Sprint-2.5 (Meeting-023)
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import AI_CONTEXT_TODAY_PLANS
from app.core.exceptions import NotFoundError, ValidationError
from app.models.study_resource import ResourceStatus, ResourceType, StudyResource
from app.repositories.study_plan_repository import StudyPlanRepository
from app.repositories.study_resource_repository import StudyResourceRepository
from app.schemas.study_resource import (
    DashboardResourceSummary,
    ResourceStatistics,
    StudyResourceCreate,
    StudyResourceListResponse,
    StudyResourceRead,
    StudyResourceUpdate,
)

_YOUTUBE_RE = re.compile(
    r"(youtube\.com|youtu\.be)",
    re.IGNORECASE,
)


class StudyResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = StudyResourceRepository(db)
        self.plans = StudyPlanRepository(db)

    def _to_read(self, row: StudyResource) -> StudyResourceRead:
        return StudyResourceRead(
            id=row.id,
            user_id=row.user_id,
            study_plan_id=row.study_plan_id,
            subject_code=row.subject_code,
            topic_code=row.topic_code,
            title=row.title,
            description=row.description,
            resource_type=row.resource_type,
            url=row.url,
            thumbnail_url=row.thumbnail_url,
            provider=row.provider,
            duration_seconds=row.duration_seconds,
            author=row.author,
            status=row.status,
            order_index=row.order_index,
            last_opened_at=row.last_opened_at,
            completed_at=row.completed_at,
            metadata=dict(row.metadata_ or {}),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def _ensure_plan(self, plan_id: uuid.UUID | None, user_id: uuid.UUID) -> None:
        if plan_id is None:
            return
        plan = await self.plans.get_by_id_for_user(plan_id, user_id)
        if plan is None:
            raise NotFoundError("Çalışma planı", str(plan_id))

    def _normalize_create(self, data: StudyResourceCreate) -> StudyResourceCreate:
        url = data.url.strip() if data.url else None
        rtype = data.resource_type
        provider = data.provider
        meta = dict(data.metadata or {})
        if url and _YOUTUBE_RE.search(url):
            if rtype == ResourceType.OTHER:
                rtype = ResourceType.YOUTUBE
            provider = provider or "youtube"
            meta.setdefault("youtube_ready", False)
        return data.model_copy(
            update={
                "url": url,
                "resource_type": rtype,
                "provider": provider,
                "metadata": meta,
            }
        )

    async def list_resources(
        self,
        user_id: uuid.UUID,
        *,
        study_plan_id: uuid.UUID | None = None,
        subject_code: str | None = None,
        topic_code: str | None = None,
        status: ResourceStatus | None = None,
        resource_type: ResourceType | None = None,
    ) -> StudyResourceListResponse:
        items = await self.repo.list_for_user(
            user_id,
            study_plan_id=study_plan_id,
            subject_code=subject_code,
            topic_code=topic_code,
            status=status,
            resource_type=resource_type,
        )
        return StudyResourceListResponse(items=[self._to_read(i) for i in items])

    async def get_resource(self, resource_id: uuid.UUID, user_id: uuid.UUID) -> StudyResourceRead:
        row = await self.repo.get_for_user(resource_id, user_id)
        if row is None:
            raise NotFoundError("Kaynak", str(resource_id))
        return self._to_read(row)

    async def create_resource(
        self, user_id: uuid.UUID, data: StudyResourceCreate
    ) -> StudyResourceRead:
        data = self._normalize_create(data)
        title = data.title.strip()
        if not title:
            raise ValidationError("Başlık zorunlu", field="title")
        await self._ensure_plan(data.study_plan_id, user_id)
        if data.url:
            dup = await self.repo.find_duplicate_url(
                user_id,
                data.url,
                topic_code=data.topic_code,
                subject_code=data.subject_code,
            )
            if dup is not None:
                raise ValidationError(
                    "Bu URL bu konuda zaten kayıtlı",
                    field="url",
                )
        order = data.order_index
        if order == 0:
            order = (await self.repo.max_order_index(user_id, data.study_plan_id)) + 1
        meta = dict(data.metadata or {})
        meta.setdefault("youtube_ready", False)
        row = StudyResource(
            user_id=user_id,
            study_plan_id=data.study_plan_id,
            subject_code=data.subject_code,
            topic_code=data.topic_code,
            title=title,
            description=data.description,
            resource_type=data.resource_type,
            url=data.url,
            thumbnail_url=data.thumbnail_url,
            provider=data.provider,
            duration_seconds=data.duration_seconds,
            author=data.author,
            status=data.status,
            order_index=order,
            metadata_=meta,
        )
        row = await self.repo.add(row)
        return self._to_read(row)

    async def update_resource(
        self, resource_id: uuid.UUID, user_id: uuid.UUID, data: StudyResourceUpdate
    ) -> StudyResourceRead:
        row = await self.repo.get_for_user(resource_id, user_id)
        if row is None:
            raise NotFoundError("Kaynak", str(resource_id))
        payload = data.model_dump(exclude_unset=True)
        if "study_plan_id" in payload:
            await self._ensure_plan(payload["study_plan_id"], user_id)
        if "title" in payload and payload["title"] is not None:
            payload["title"] = payload["title"].strip()
            if not payload["title"]:
                raise ValidationError("Başlık zorunlu", field="title")
        if "metadata" in payload:
            meta = dict(payload.pop("metadata") or {})
            meta.setdefault("youtube_ready", False)
            row.metadata_ = meta
        if "status" in payload and payload["status"] is not None:
            new_status = payload["status"]
            if new_status == ResourceStatus.COMPLETED and row.status != ResourceStatus.COMPLETED:
                row.completed_at = datetime.now(UTC)
            elif new_status != ResourceStatus.COMPLETED:
                row.completed_at = None
        for key, value in payload.items():
            setattr(row, key, value)
        row.updated_at = datetime.now(UTC)
        await self.db.flush()
        return self._to_read(row)

    async def delete_resource(self, resource_id: uuid.UUID, user_id: uuid.UUID) -> None:
        row = await self.repo.get_for_user(resource_id, user_id)
        if row is None:
            raise NotFoundError("Kaynak", str(resource_id))
        await self.repo.delete(row)

    async def mark_opened(
        self, resource_id: uuid.UUID, user_id: uuid.UUID
    ) -> StudyResourceRead:
        row = await self.repo.get_for_user(resource_id, user_id)
        if row is None:
            raise NotFoundError("Kaynak", str(resource_id))
        row.last_opened_at = datetime.now(UTC)
        if row.status == ResourceStatus.NOT_STARTED:
            row.status = ResourceStatus.IN_PROGRESS
        row.updated_at = datetime.now(UTC)
        await self.db.flush()
        return self._to_read(row)

    async def get_statistics(self, user_id: uuid.UUID) -> ResourceStatistics:
        items = await self.repo.list_for_user(user_id, limit=1000)
        today = datetime.now(UTC).date()
        by_type: dict[str, int] = {}
        completed = 0
        in_progress = 0
        total_video = 0
        completed_video = 0
        for item in items:
            key = str(item.resource_type)
            by_type[key] = by_type.get(key, 0) + 1
            if item.status == ResourceStatus.COMPLETED:
                completed += 1
            if item.status == ResourceStatus.IN_PROGRESS:
                in_progress += 1
            dur = int(item.duration_seconds or 0)
            if item.resource_type in (ResourceType.YOUTUBE, ResourceType.VIDEO, ResourceType.AUDIO):
                total_video += dur
                if item.status == ResourceStatus.COMPLETED:
                    completed_video += dur
        return ResourceStatistics(
            total_count=len(items),
            completed_count=completed,
            in_progress_count=in_progress,
            today_completed_count=await self.repo.count_completed_on(user_id, today),
            today_opened_count=await self.repo.count_opened_on(user_id, today),
            total_video_duration_seconds=total_video,
            completed_video_duration_seconds=completed_video,
            by_type=by_type,
        )

    async def dashboard_summary(self, user_id: uuid.UUID) -> DashboardResourceSummary:
        today = datetime.now(UTC).date()
        recent = await self.repo.list_recent(user_id, limit=5)
        return DashboardResourceSummary(
            today_opened_count=await self.repo.count_opened_on(user_id, today),
            today_completed_count=await self.repo.count_completed_on(user_id, today),
            recent_items=[self._to_read(r) for r in recent],
        )

    async def context_items(self, user_id: uuid.UUID) -> list[dict]:
        items = await self.repo.list_for_user(user_id, limit=AI_CONTEXT_TODAY_PLANS)
        return [
            {
                "title": r.title,
                "resource_type": str(r.resource_type),
                "status": str(r.status),
                "provider": r.provider,
                "duration_seconds": r.duration_seconds,
            }
            for r in items
        ]
