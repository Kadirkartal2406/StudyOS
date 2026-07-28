"""System admin operations — list/edit users, export data, inspect questions."""

from __future__ import annotations

import json
import math
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.models.beta_ops import BetaFeedback
from app.models.conversation import Conversation
from app.models.exam import Exam
from app.models.generated_question import GeneratedQuestion
from app.models.goal import Goal
from app.models.learning_profile import ExamTarget, Student, UserSubject
from app.models.memory import Memory
from app.models.planner_draft import PlannerDraft
from app.models.question_pool import QuestionPoolCard
from app.models.question_record import QuestionRecord
from app.models.study_plan import StudyPlan
from app.models.study_session import StudySession
from app.models.user import User, UserRole, UserStatus
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.admin import (
    AdminOverview,
    AdminQuestionItem,
    AdminUserListItem,
    AdminUserUpdate,
)


def _serialize(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if hasattr(obj, "value"):
        try:
            return obj.value
        except Exception:
            pass
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(x) for x in obj]
    return obj


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def overview(self) -> AdminOverview:
        async def _count(model) -> int:
            r = await self.db.execute(select(func.count()).select_from(model))
            return int(r.scalar() or 0)

        users_total = await _count(User)
        r = await self.db.execute(
            select(func.count()).select_from(User).where(User.status == UserStatus.ACTIVE)
        )
        users_active = int(r.scalar() or 0)
        r = await self.db.execute(
            select(func.count())
            .select_from(User)
            .where(User.role == UserRole.SYSTEM_ADMIN)
        )
        users_admin = int(r.scalar() or 0)
        return AdminOverview(
            users_total=users_total,
            users_active=users_active,
            users_admin=users_admin,
            study_plans=await _count(StudyPlan),
            study_sessions=await _count(StudySession),
            question_records=await _count(QuestionRecord),
            generated_questions=await _count(GeneratedQuestion),
            pool_cards=await _count(QuestionPoolCard),
            exams=await _count(Exam),
            goals=await _count(Goal),
            conversations=await _count(Conversation),
            beta_feedback=await _count(BetaFeedback),
        )

    async def list_users(
        self,
        *,
        q: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AdminUserListItem], int]:
        page = max(1, page)
        page_size = min(max(1, page_size), 200)
        stmt = select(User)
        if q:
            like = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    User.email.ilike(like),
                    User.first_name.ilike(like),
                    User.last_name.ilike(like),
                )
            )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await self.db.execute(count_stmt)).scalar() or 0)
        stmt = stmt.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        users = list((await self.db.execute(stmt)).scalars().all())

        items: list[AdminUserListItem] = []
        for u in users:
            items.append(
                AdminUserListItem(
                    id=u.id,
                    email=u.email,
                    first_name=u.first_name,
                    last_name=u.last_name,
                    role=str(u.role),
                    status=str(u.status),
                    is_verified=bool(u.is_verified),
                    created_at=u.created_at,
                    last_login_at=u.last_login_at,
                    study_plans=await self._user_count(StudyPlan, u.id),
                    study_sessions=await self._user_count(StudySession, u.id),
                    question_records=await self._user_count(QuestionRecord, u.id),
                )
            )
        return items, total

    async def _user_count(self, model, user_id: uuid.UUID) -> int:
        r = await self.db.execute(
            select(func.count()).select_from(model).where(model.user_id == user_id)
        )
        return int(r.scalar() or 0)

    async def get_user(self, user_id: uuid.UUID) -> AdminUserListItem:
        u = await self.db.get(User, user_id)
        if u is None:
            raise NotFoundError("User", str(user_id))
        return AdminUserListItem(
            id=u.id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            role=str(u.role),
            status=str(u.status),
            is_verified=bool(u.is_verified),
            created_at=u.created_at,
            last_login_at=u.last_login_at,
            study_plans=await self._user_count(StudyPlan, u.id),
            study_sessions=await self._user_count(StudySession, u.id),
            question_records=await self._user_count(QuestionRecord, u.id),
        )

    async def update_user(self, user_id: uuid.UUID, data: AdminUserUpdate) -> AdminUserListItem:
        u = await self.db.get(User, user_id)
        if u is None:
            raise NotFoundError("User", str(user_id))
        if data.email is not None and data.email != u.email:
            exists = await self.db.execute(select(User).where(User.email == str(data.email)))
            if exists.scalar_one_or_none():
                raise ConflictError("Bu e-posta başka bir kullanıcıda kayıtlı")
            u.email = str(data.email)
        if data.first_name is not None:
            u.first_name = data.first_name
        if data.last_name is not None:
            u.last_name = data.last_name
        if data.role is not None:
            u.role = data.role
        if data.status is not None:
            u.status = data.status
        if data.is_verified is not None:
            u.is_verified = data.is_verified
        if data.new_password:
            u.hashed_password = hash_password(data.new_password)
            await RefreshTokenRepository(self.db).revoke_all_for_user(u.id)
        await self.db.flush()
        return await self.get_user(user_id)

    async def delete_user(self, user_id: uuid.UUID, *, hard: bool = False) -> None:
        u = await self.db.get(User, user_id)
        if u is None:
            raise NotFoundError("User", str(user_id))
        if str(u.role) == UserRole.SYSTEM_ADMIN:
            r = await self.db.execute(
                select(func.count())
                .select_from(User)
                .where(User.role == UserRole.SYSTEM_ADMIN, User.status == UserStatus.ACTIVE)
            )
            if int(r.scalar() or 0) <= 1:
                raise ValidationError("Son aktif sistem yöneticisi silinemez")
        await RefreshTokenRepository(self.db).revoke_all_for_user(u.id)
        if hard:
            await self.db.delete(u)
        else:
            u.status = UserStatus.INACTIVE
            u.deletion_requested_at = datetime.now(UTC)
        await self.db.flush()

    async def export_user_data(self, user_id: uuid.UUID) -> dict[str, Any]:
        u = await self.db.get(User, user_id)
        if u is None:
            raise NotFoundError("User", str(user_id))

        async def _rows(model, limit: int = 5000) -> list[dict]:
            r = await self.db.execute(
                select(model).where(model.user_id == user_id).limit(limit)
            )
            out = []
            for row in r.scalars().all():
                d = {c.name: _serialize(getattr(row, c.name)) for c in row.__table__.columns}
                if "hashed_password" in d:
                    del d["hashed_password"]
                out.append(d)
            return out

        student = (
            await self.db.execute(select(Student).where(Student.user_id == user_id))
        ).scalar_one_or_none()
        student_payload = None
        if student is not None:
            student_payload = {
                c.name: _serialize(getattr(student, c.name)) for c in student.__table__.columns
            }

        targets = []
        r = await self.db.execute(select(ExamTarget).where(ExamTarget.user_id == user_id))
        for t in r.scalars().all():
            targets.append({c.name: _serialize(getattr(t, c.name)) for c in t.__table__.columns})

        subjects = []
        r = await self.db.execute(select(UserSubject).where(UserSubject.user_id == user_id))
        for s in r.scalars().all():
            subjects.append({c.name: _serialize(getattr(s, c.name)) for c in s.__table__.columns})

        return {
            "exported_at": datetime.now(UTC).isoformat(),
            "user": {
                "id": str(u.id),
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "role": str(u.role),
                "status": str(u.status),
                "is_verified": u.is_verified,
                "created_at": _serialize(u.created_at),
                "last_login_at": _serialize(u.last_login_at),
            },
            "student": student_payload,
            "exam_targets": targets,
            "user_subjects": subjects,
            "study_plans": await _rows(StudyPlan),
            "study_sessions": await _rows(StudySession),
            "question_records": await _rows(QuestionRecord),
            "generated_questions": await _rows(GeneratedQuestion),
            "exams": await _rows(Exam),
            "goals": await _rows(Goal),
            "planner_drafts": await _rows(PlannerDraft),
            "conversations": await _rows(Conversation),
            "memories": await _rows(Memory),
        }

    async def list_questions(
        self,
        *,
        source: str = "all",
        q: str | None = None,
        page: int = 1,
        page_size: int = 40,
    ) -> tuple[list[AdminQuestionItem], int]:
        page = max(1, page)
        page_size = min(max(1, page_size), 100)
        items: list[AdminQuestionItem] = []

        if source in ("all", "pool"):
            stmt = select(QuestionPoolCard).order_by(QuestionPoolCard.created_at.desc())
            if q:
                like = f"%{q}%"
                stmt = stmt.where(
                    or_(
                        QuestionPoolCard.stem.ilike(like),
                        QuestionPoolCard.subject_code.ilike(like),
                        QuestionPoolCard.topic_code.ilike(like),
                    )
                )
            rows = list((await self.db.execute(stmt.limit(page_size))).scalars().all())
            for r in rows:
                items.append(
                    AdminQuestionItem(
                        id=r.id,
                        source="pool",
                        exam=r.exam,
                        subject=r.subject_code,
                        topic=r.topic_code,
                        stem=(r.stem or "")[:400],
                        difficulty=r.difficulty_band,
                        created_at=r.created_at,
                        extra={"correct_key": r.correct_key, "use_count": r.use_count},
                    )
                )

        if source in ("all", "generated"):
            stmt = select(GeneratedQuestion).order_by(GeneratedQuestion.created_at.desc())
            if q:
                like = f"%{q}%"
                stmt = stmt.where(
                    or_(
                        GeneratedQuestion.question_text.ilike(like),
                        GeneratedQuestion.subject_code.ilike(like),
                        GeneratedQuestion.topic_code.ilike(like),
                    )
                )
            rows = list((await self.db.execute(stmt.limit(page_size))).scalars().all())
            for r in rows:
                items.append(
                    AdminQuestionItem(
                        id=r.id,
                        source="generated",
                        subject=r.subject_code,
                        topic=r.topic_code,
                        stem=(r.question_text or "")[:400],
                        difficulty=str(r.difficulty) if r.difficulty else None,
                        user_id=r.user_id,
                        created_at=getattr(r, "created_at", None),
                        extra={
                            "status": str(r.status),
                            "correct_option": r.correct_option,
                        },
                    )
                )

        if source in ("all", "record"):
            stmt = select(QuestionRecord).order_by(QuestionRecord.created_at.desc())
            if q:
                like = f"%{q}%"
                stmt = stmt.where(
                    or_(
                        QuestionRecord.subject.ilike(like),
                        QuestionRecord.topic.ilike(like),
                    )
                )
            rows = list((await self.db.execute(stmt.limit(page_size))).scalars().all())
            for r in rows:
                stem = (
                    f"{r.subject}"
                    + (f" · {r.topic}" if r.topic else "")
                    + f" — {r.correct_count}/{r.question_count} doğru"
                )
                items.append(
                    AdminQuestionItem(
                        id=r.id,
                        source="record",
                        exam=str(r.exam_type) if r.exam_type else None,
                        subject=r.subject,
                        topic=r.topic,
                        stem=stem[:400],
                        difficulty=str(r.difficulty) if r.difficulty else None,
                        user_id=r.user_id,
                        created_at=r.created_at,
                        extra={
                            "correct_count": r.correct_count,
                            "question_count": r.question_count,
                        },
                    )
                )

        # Lightweight total for UI
        total = len(items)
        start = (page - 1) * page_size
        return items[start : start + page_size], total

    @staticmethod
    def pagination_meta(page: int, page_size: int, total: int) -> dict:
        return {
            "page": page,
            "page_size": page_size,
            "total_items": total,
            "total_pages": max(1, math.ceil(total / page_size)) if total else 1,
        }

    @staticmethod
    def export_json_bytes(payload: dict) -> bytes:
        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
