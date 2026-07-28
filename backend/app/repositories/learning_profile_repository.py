"""
StudyOS — Learning Profile repository (Sprint-3.0)
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning_profile import ExamTarget, Student, SubjectCatalog, TopicCatalog, UserSubject
from app.models.question_record import QuestionRecord
from app.models.revision import RevisionItem, RevisionItemStatus, RevisionSchedule
from app.models.study_plan import StudyPlan
from app.models.study_session import StudySession, StudySessionStatus


class LearningProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student(self, user_id: uuid.UUID) -> Student | None:
        result = await self.db.execute(select(Student).where(Student.user_id == user_id))
        return result.scalar_one_or_none()

    async def create_student(self, student: Student) -> Student:
        self.db.add(student)
        await self.db.flush()
        return student

    async def list_exam_targets(self, user_id: uuid.UUID) -> list[ExamTarget]:
        result = await self.db.execute(
            select(ExamTarget)
            .where(ExamTarget.user_id == user_id)
            .order_by(ExamTarget.is_primary.desc(), ExamTarget.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_exam_target(self, user_id: uuid.UUID, target_id: uuid.UUID) -> ExamTarget | None:
        result = await self.db.execute(
            select(ExamTarget).where(ExamTarget.id == target_id, ExamTarget.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_exam_target_by_type(self, user_id: uuid.UUID, exam_type: str) -> ExamTarget | None:
        result = await self.db.execute(
            select(ExamTarget).where(
                ExamTarget.user_id == user_id, ExamTarget.exam_type == exam_type
            )
        )
        return result.scalar_one_or_none()

    async def add_exam_target(self, target: ExamTarget) -> ExamTarget:
        self.db.add(target)
        await self.db.flush()
        return target

    async def delete_exam_target(self, target: ExamTarget) -> None:
        await self.db.delete(target)
        await self.db.flush()

    async def clear_primary(self, user_id: uuid.UUID) -> None:
        targets = await self.list_exam_targets(user_id)
        for t in targets:
            t.is_primary = False
        await self.db.flush()

    async def list_catalog(
        self, exam_type: str | None = None, *, active_only: bool = True
    ) -> list[SubjectCatalog]:
        q = select(SubjectCatalog).order_by(
            SubjectCatalog.sort_order.asc(), SubjectCatalog.name.asc()
        )
        if active_only:
            q = q.where(SubjectCatalog.is_active.is_(True))
        result = await self.db.execute(q)
        rows = list(result.scalars().all())
        if exam_type is None:
            return rows
        return [r for r in rows if exam_type in (r.exam_types or [])]

    async def get_catalog_by_code(self, code: str) -> SubjectCatalog | None:
        result = await self.db.execute(
            select(SubjectCatalog).where(SubjectCatalog.code == code)
        )
        return result.scalar_one_or_none()

    async def add_catalog_row(self, row: SubjectCatalog) -> SubjectCatalog:
        self.db.add(row)
        await self.db.flush()
        return row

    async def get_topic_by_code(self, code: str) -> TopicCatalog | None:
        result = await self.db.execute(
            select(TopicCatalog).where(TopicCatalog.code == code)
        )
        return result.scalar_one_or_none()

    async def list_topics(
        self, subject_code: str | None = None, *, active_only: bool = True
    ) -> list[TopicCatalog]:
        q = select(TopicCatalog).order_by(
            TopicCatalog.sort_order.asc(), TopicCatalog.name.asc()
        )
        if active_only:
            q = q.where(TopicCatalog.is_active.is_(True))
        if subject_code is not None:
            q = q.where(TopicCatalog.subject_code == subject_code)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def add_topic_row(self, row: TopicCatalog) -> TopicCatalog:
        self.db.add(row)
        await self.db.flush()
        return row

    async def list_user_subjects(self, user_id: uuid.UUID, *, active_only: bool = True) -> list[UserSubject]:
        q = select(UserSubject).where(UserSubject.user_id == user_id)
        if active_only:
            q = q.where(UserSubject.is_active.is_(True))
        q = q.order_by(UserSubject.subject_name.asc())
        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def get_user_subject(self, user_id: uuid.UUID, code: str) -> UserSubject | None:
        result = await self.db.execute(
            select(UserSubject).where(
                UserSubject.user_id == user_id, UserSubject.subject_code == code
            )
        )
        return result.scalar_one_or_none()

    async def add_user_subject(self, row: UserSubject) -> UserSubject:
        self.db.add(row)
        await self.db.flush()
        return row

    async def question_metrics_by_subject(
        self, user_id: uuid.UUID
    ) -> dict[str, tuple[int, int, int, datetime | None]]:
        """subject_lower -> (questions, correct, duration_minutes, last_at)."""
        result = await self.db.execute(
            select(
                QuestionRecord.subject,
                func.coalesce(func.sum(QuestionRecord.question_count), 0),
                func.coalesce(func.sum(QuestionRecord.correct_count), 0),
                func.coalesce(func.sum(QuestionRecord.duration_minutes), 0),
                func.max(QuestionRecord.created_at),
            )
            .where(QuestionRecord.user_id == user_id)
            .group_by(QuestionRecord.subject)
        )
        out: dict[str, tuple[int, int, int, datetime | None]] = {}
        for subject, q, c, d, last_at in result.all():
            key = str(subject or "").strip().casefold()
            if not key:
                continue
            out[key] = (int(q), int(c), int(d), last_at)
        return out

    async def study_minutes_by_subject(
        self, user_id: uuid.UUID
    ) -> dict[str, tuple[int, datetime | None]]:
        """subject_lower -> (minutes, last_session_at)."""
        subject_label = func.coalesce(StudyPlan.subject, "Serbest")
        result = await self.db.execute(
            select(
                subject_label,
                func.coalesce(func.sum(StudySession.actual_duration_minutes), 0),
                func.max(StudySession.started_at),
            )
            .select_from(StudySession)
            .outerjoin(StudyPlan, StudySession.study_plan_id == StudyPlan.id)
            .where(
                StudySession.user_id == user_id,
                StudySession.status == StudySessionStatus.COMPLETED,
            )
            .group_by(subject_label)
        )
        out: dict[str, tuple[int, datetime | None]] = {}
        for subject, minutes, last_at in result.all():
            key = str(subject or "").strip().casefold()
            if not key:
                continue
            out[key] = (int(minutes), last_at)
        return out

    async def last_revision_by_subject(self, user_id: uuid.UUID) -> dict[str, datetime | None]:
        """subject_lower -> last_reviewed_at."""
        result = await self.db.execute(
            select(
                RevisionItem.subject,
                func.max(RevisionSchedule.last_reviewed_at),
            )
            .join(RevisionSchedule, RevisionSchedule.revision_item_id == RevisionItem.id)
            .where(
                RevisionItem.user_id == user_id,
                RevisionItem.deleted_at.is_(None),
                RevisionItem.status != RevisionItemStatus.ARCHIVED,
            )
            .group_by(RevisionItem.subject)
        )
        out: dict[str, datetime | None] = {}
        for subject, last_at in result.all():
            key = str(subject or "").strip().casefold()
            if not key:
                continue
            out[key] = last_at
        return out
