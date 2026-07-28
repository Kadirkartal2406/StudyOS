"""
StudyOS — StudyPlan Service
Çalışma planı CRUD ve durum geçişi (start/complete/skip) iş mantığı.
Bkz. docs/architecture/software-architecture.md, Sprint-1.4 (Meeting-012)
"""

import uuid
from datetime import date, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.repositories.study_plan_repository import StudyPlanRepository
from app.schemas.study_plan import (
    StudyPlanCompleteRequest,
    StudyPlanCreate,
    StudyPlanUpdate,
)
from app.services.activity_service import ActivityService

# Terminal durumdan çıkış yoktur; tamamlanan/atlanan bir plan yeniden başlatılamaz.
_TERMINAL_STATUSES = (StudyPlanStatus.COMPLETED, StudyPlanStatus.SKIPPED)


class StudyPlanService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = StudyPlanRepository(db)
        self.activity_service = ActivityService(db)

    async def list_plans(self, user_id: uuid.UUID, study_date: date | None) -> list[StudyPlan]:
        return await self.repo.list_for_user(user_id, study_date)

    async def get_plan(self, plan_id: uuid.UUID, user_id: uuid.UUID) -> StudyPlan:
        plan = await self.repo.get_by_id_for_user(plan_id, user_id)
        if plan is None:
            raise NotFoundError("Çalışma planı", str(plan_id))
        return plan

    async def create_plan(self, user_id: uuid.UUID, data: StudyPlanCreate) -> StudyPlan:
        await self._check_time_conflict(
            user_id, data.study_date, data.planned_start_time, data.planned_end_time
        )

        order_index = data.order_index
        if order_index is None:
            order_index = await self.repo.next_order_index(user_id, data.study_date)

        plan = StudyPlan(
            user_id=user_id,
            title=data.title,
            subject=data.subject,
            topic=data.topic,
            target_question_count=data.target_question_count,
            estimated_minutes=data.estimated_minutes,
            planned_start_time=data.planned_start_time,
            planned_end_time=data.planned_end_time,
            study_date=data.study_date,
            order_index=order_index,
            status=StudyPlanStatus.PLANNED,
        )
        return await self.repo.add(plan)

    async def update_plan(
        self, plan_id: uuid.UUID, user_id: uuid.UUID, data: StudyPlanUpdate
    ) -> StudyPlan:
        plan = await self.get_plan(plan_id, user_id)

        await self._check_time_conflict(
            user_id,
            data.study_date,
            data.planned_start_time,
            data.planned_end_time,
            exclude_id=plan.id,
        )

        plan.title = data.title
        plan.subject = data.subject
        plan.topic = data.topic
        plan.target_question_count = data.target_question_count
        plan.estimated_minutes = data.estimated_minutes
        plan.planned_start_time = data.planned_start_time
        plan.planned_end_time = data.planned_end_time
        plan.study_date = data.study_date
        if data.order_index is not None:
            plan.order_index = data.order_index

        await self.db.flush()
        return plan

    async def delete_plan(self, plan_id: uuid.UUID, user_id: uuid.UUID) -> None:
        plan = await self.get_plan(plan_id, user_id)
        await self.repo.soft_delete(plan)

    async def start_plan(self, plan_id: uuid.UUID, user_id: uuid.UUID) -> StudyPlan:
        plan = await self.get_plan(plan_id, user_id)
        self._assert_transition_allowed(plan, StudyPlanStatus.IN_PROGRESS)
        plan.status = StudyPlanStatus.IN_PROGRESS
        await self.db.flush()
        return plan

    async def complete_plan(
        self, plan_id: uuid.UUID, user_id: uuid.UUID, data: StudyPlanCompleteRequest
    ) -> StudyPlan:
        plan = await self.get_plan(plan_id, user_id)
        self._assert_transition_allowed(plan, StudyPlanStatus.COMPLETED)

        plan.status = StudyPlanStatus.COMPLETED
        plan.completed_question_count = (
            data.completed_question_count
            if data.completed_question_count is not None
            else plan.target_question_count
        )
        plan.completed_minutes = (
            data.completed_minutes if data.completed_minutes is not None else plan.estimated_minutes
        )
        await self.db.flush()
        await self.activity_service.record_plan_completed(plan)
        # B1 — Goal progress Plan complete'ten güncellenmez (Session/QR kaynak)
        from app.services.goal_progress_service import GoalProgressEvent, GoalProgressService

        await GoalProgressService(self.db).apply_event(
            user_id,
            GoalProgressEvent(kind="plan_completed"),
        )
        return plan

    async def skip_plan(self, plan_id: uuid.UUID, user_id: uuid.UUID) -> StudyPlan:
        plan = await self.get_plan(plan_id, user_id)
        self._assert_transition_allowed(plan, StudyPlanStatus.SKIPPED)
        plan.status = StudyPlanStatus.SKIPPED
        await self.db.flush()
        return plan

    def _assert_transition_allowed(self, plan: StudyPlan, target: StudyPlanStatus) -> None:
        if plan.status in _TERMINAL_STATUSES:
            raise ConflictError(
                f"Plan zaten '{plan.status}' durumunda; bu işlem gerçekleştirilemez"
            )
        if plan.status == target:
            raise ConflictError(f"Plan zaten '{target}' durumunda")

    async def _check_time_conflict(
        self,
        user_id: uuid.UUID,
        study_date: date,
        start: time | None,
        end: time | None,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        if start is None or end is None:
            return

        others = await self.repo.list_overlapping(user_id, study_date, exclude_id=exclude_id)
        for other in others:
            # list_overlapping yalnızca her iki zaman alanı da dolu olan kayıtları döner.
            other_start, other_end = other.planned_start_time, other.planned_end_time
            if other_start is None or other_end is None:
                continue
            if start < other_end and end > other_start:
                raise ValidationError(
                    f"Saat çakışması: '{other.title}' planı ile ({other_start}"
                    f"–{other_end}) çakışıyor",
                    field="planned_start_time",
                )
