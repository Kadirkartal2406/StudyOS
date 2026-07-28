"""

StudyOS — StudySession Service

Pomodoro oturumu start/pause/resume/finish iş mantığı.

Bkz. Sprint-1.5 (Meeting-013), Sprint-1.7 (Meeting-015) activity hooks.



Kararlar:

- Aynı anda tek aktif (running/paused) oturum; ikinci start → 409 CONFLICT.

- Finish sırasında bağlı StudyPlan'a completed_minutes/questions artımlı eklenir;

  plan planned ise in_progress'e geçer; otomatik completed yapılmaz (B1).

- Mola istemci tarafında yönetilir; break_duration_minutes yalnızca seçilen mola

  süresini taşır (pause ≠ break).

- Her start/pause/resume/finish Activity event yazar (A2).

"""



import math
import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    STUDY_SESSION_HISTORY_DEFAULT_PAGE_SIZE,
    STUDY_SESSION_HISTORY_MAX_PAGE_SIZE,
)
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.study_plan import StudyPlanStatus
from app.models.study_session import StudySession, StudySessionStatus
from app.repositories.study_plan_repository import StudyPlanRepository
from app.repositories.study_session_repository import StudySessionRepository
from app.schemas.common import PaginationMeta
from app.models.study_session import StudySessionMode, StudySessionPhase
from app.schemas.study_session import (
    StudySessionFinishRequest,
    StudySessionRead,
    StudySessionStartRequest,
    StudySessionStatistics,
    StudyTodaySummary,
    SubjectMinutesItem,
)
from app.services.activity_service import ActivityService


class StudySessionService:

    def __init__(self, db: AsyncSession):

        self.db = db

        self.repo = StudySessionRepository(db)

        self.plan_repo = StudyPlanRepository(db)

        self.activity_service = ActivityService(db)



    async def start(self, user_id: uuid.UUID, data: StudySessionStartRequest) -> StudySession:

        active = await self.repo.get_active_for_user(user_id)

        if active is not None:

            raise ConflictError(

                f"Zaten aktif bir oturum var (id={active.id}, status={active.status})"

            )



        plan = None

        if data.study_plan_id is not None:

            plan = await self.plan_repo.get_by_id_for_user(data.study_plan_id, user_id)

            if plan is None:

                raise NotFoundError("Çalışma planı", str(data.study_plan_id))

            if plan.status in (StudyPlanStatus.COMPLETED, StudyPlanStatus.SKIPPED):

                raise ConflictError(f"Plan '{plan.status}' durumunda; oturum başlatılamaz")

            if plan.status == StudyPlanStatus.PLANNED:

                plan.status = StudyPlanStatus.IN_PROGRESS



        mode = (data.mode or StudySessionMode.POMODORO).strip().lower()
        if mode not in (StudySessionMode.POMODORO, StudySessionMode.CHRONOMETER):
            raise ValidationError("mode pomodoro veya chronometer olmalı", field="mode")
        planned = data.planned_duration_minutes
        if mode == StudySessionMode.POMODORO and planned is None:
            raise ValidationError("Pomodoro için süre gerekli", field="planned_duration_minutes")

        session = StudySession(
            user_id=user_id,
            study_plan_id=data.study_plan_id,
            started_at=datetime.now(UTC),
            planned_duration_minutes=planned,
            break_duration_minutes=data.break_duration_minutes,
            status=StudySessionStatus.RUNNING,
            mode=mode,
            phase=StudySessionPhase.FOCUS,
            subject_code=getattr(data, "subject_code", None),
            topic_code=getattr(data, "topic_code", None),
            break_segments=[],
        )

        session = await self.repo.add(session)

        await self.activity_service.record_session_started(session, plan)

        return session



    async def pause(self, user_id: uuid.UUID) -> StudySession:

        session = await self._require_active(user_id)

        if session.status != StudySessionStatus.RUNNING:

            raise ConflictError("Yalnızca 'running' durumundaki oturum duraklatılabilir")



        session.status = StudySessionStatus.PAUSED

        session.paused_at = datetime.now(UTC)

        await self.db.flush()

        await self.activity_service.record_session_paused(session)

        return session



    async def resume(self, user_id: uuid.UUID) -> StudySession:

        session = await self._require_active(user_id)

        if session.status != StudySessionStatus.PAUSED:

            raise ConflictError("Yalnızca 'paused' durumundaki oturum devam ettirilebilir")



        now = datetime.now(UTC)

        if session.paused_at is not None:

            pause_delta = now - session.paused_at

            session.paused_seconds += max(0, int(pause_delta.total_seconds()))

        session.paused_at = None

        session.status = StudySessionStatus.RUNNING

        await self.db.flush()

        await self.activity_service.record_session_resumed(session)

        return session



    async def finish(self, user_id: uuid.UUID, data: StudySessionFinishRequest) -> StudySession:

        session = await self._require_active(user_id)

        now = datetime.now(UTC)

        # Close open break without counting as focus
        if getattr(session, "phase", "focus") == StudySessionPhase.BREAK and session.break_started_at:
            await self._close_break(session, now)

        if session.status == StudySessionStatus.PAUSED and session.paused_at is not None:

            pause_delta = now - session.paused_at

            session.paused_seconds += max(0, int(pause_delta.total_seconds()))

            session.paused_at = None

        elapsed_seconds = max(
            0,
            int((now - session.started_at).total_seconds())
            - session.paused_seconds
            - int(getattr(session, "actual_break_minutes", 0) or 0) * 60,
        )

        actual_minutes = math.ceil(elapsed_seconds / 60) if elapsed_seconds > 0 else 0

        session.ended_at = now
        session.actual_duration_minutes = actual_minutes
        session.completed_questions = data.completed_questions or 0
        session.completed_topics = data.completed_topics or 0
        session.status = StudySessionStatus.COMPLETED
        session.phase = StudySessionPhase.FOCUS
        await self.db.flush()



        plan = None

        if session.study_plan_id is not None:

            plan = await self._apply_progress_to_plan(session)



        await self.activity_service.record_session_completed(session, plan)
        await self.activity_service.record_study_finished(session)

        from app.services.goal_progress_service import GoalProgressEvent, GoalProgressService

        await GoalProgressService(self.db).apply_event(
            user_id,
            GoalProgressEvent(
                kind="session_completed",
                amount=float(session.actual_duration_minutes),
                occurred_on=session.started_at.date(),
            ),
        )
        from app.schemas.achievement import AchievementCheckRequest
        from app.services.achievement_service import AchievementService

        await AchievementService(self.db).check(
            user_id,
            AchievementCheckRequest(event="session_completed"),
        )
        await AchievementService(self.db).check(
            user_id,
            AchievementCheckRequest(event="goal_progress"),
        )

        # ── LOS Module 1: Evidence ingestion ──────────────────────
        try:
            from app.services.evidence_service import EvidenceService
            await EvidenceService(self.db).ingest_session(session)
        except Exception:
            pass  # Evidence hataları kullanıcı akışını kesmez

        # ── LOS Module 7: Behavioral Memory update ────────────────
        try:
            from app.services.behavioral_memory_service import BehavioralMemoryService
            await BehavioralMemoryService(self.db).update_from_session(user_id, session)
        except Exception:
            pass

        return session



    async def get_by_id(self, session_id: uuid.UUID, user_id: uuid.UUID) -> StudySession:

        session = await self.repo.get_by_id_for_user(session_id, user_id)

        if session is None:

            raise NotFoundError("Çalışma oturumu", str(session_id))

        return session



    async def get_today(self, user_id: uuid.UUID) -> list[StudySession]:

        today = datetime.now(UTC).date()

        return await self.repo.list_for_user_on_date(user_id, today)



    async def get_history(

        self,

        user_id: uuid.UUID,

        *,

        page: int = 1,

        page_size: int = STUDY_SESSION_HISTORY_DEFAULT_PAGE_SIZE,

        date_from: date | None = None,

        date_to: date | None = None,

        study_plan_id: uuid.UUID | None = None,

        status: StudySessionStatus | None = None,

        q: str | None = None,

    ) -> tuple[list[StudySession], PaginationMeta]:

        if page < 1:

            raise ValidationError("page 1 veya daha büyük olmalıdır", field="page")

        if page_size < 1 or page_size > STUDY_SESSION_HISTORY_MAX_PAGE_SIZE:

            raise ValidationError(

                f"page_size 1–{STUDY_SESSION_HISTORY_MAX_PAGE_SIZE} arasında olmalıdır",

                field="page_size",

            )

        if date_from is not None and date_to is not None and date_from > date_to:

            raise ValidationError("date_from, date_to'dan büyük olamaz", field="date_from")



        search = q.strip() if q else None

        if search == "":

            search = None



        sessions, total = await self.repo.list_history(

            user_id,

            page=page,

            page_size=page_size,

            date_from=date_from,

            date_to=date_to,

            study_plan_id=study_plan_id,

            status=status,

            search=search,

        )

        total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 0

        meta = PaginationMeta(

            page=page,

            page_size=page_size,

            total_items=total,

            total_pages=total_pages,

        )

        return sessions, meta



    async def to_read(self, session: StudySession) -> StudySessionRead:
        """Plan başlığı/konusu + M25 engine_state ile zenginleştirilmiş Read şeması."""
        plan_title = None
        plan_subject = None
        if session.study_plan_id is not None:
            plan = await self.plan_repo.get_by_id_for_user(session.study_plan_id, session.user_id)
            if plan is not None:
                plan_title = plan.title
                plan_subject = plan.subject
        base = StudySessionRead.model_validate(session)
        return base.model_copy(
            update={
                "plan_title": plan_title,
                "plan_subject": plan_subject,
                "engine_state": self._engine_state(session),
            }
        )



    async def get_statistics(

        self,

        user_id: uuid.UUID,

        *,

        date_from: date | None = None,

        date_to: date | None = None,

    ) -> StudySessionStatistics:

        if date_from is not None and date_to is not None and date_from > date_to:

            raise ValidationError("date_from, date_to'dan büyük olamaz", field="date_from")



        started_from = (

            datetime.combine(date_from, datetime.min.time(), tzinfo=UTC)

            if date_from is not None

            else datetime(1970, 1, 1, tzinfo=UTC)

        )

        started_to = (

            datetime.combine(date_to + timedelta(days=1), datetime.min.time(), tzinfo=UTC)

            if date_to is not None

            else datetime.now(UTC) + timedelta(days=1)

        )



        completed = await self.repo.list_completed_between(user_id, started_from, started_to)

        _, total_all = await self.repo.list_history(

            user_id, page=1, page_size=1, date_from=date_from, date_to=date_to

        )



        total_focus = sum(s.actual_duration_minutes for s in completed)

        total_questions = sum(s.completed_questions for s in completed)

        total_topics = sum(s.completed_topics for s in completed)

        completed_count = len(completed)

        avg = round(total_focus / completed_count, 1) if completed_count > 0 else 0.0



        return StudySessionStatistics(

            total_sessions=total_all,

            completed_sessions=completed_count,

            total_focus_minutes=total_focus,

            total_questions=total_questions,

            total_topics=total_topics,

            average_session_minutes=avg,

            date_from=date_from,

            date_to=date_to,

        )



    async def start_break(self, user_id: uuid.UUID) -> StudySession:
        """Focus → break (pause ≠ break)."""
        session = await self._require_active(user_id)
        if session.status != StudySessionStatus.RUNNING:
            raise ConflictError("Mola yalnızca running oturumda başlatılabilir")
        if getattr(session, "phase", StudySessionPhase.FOCUS) == StudySessionPhase.BREAK:
            raise ConflictError("Zaten moladasın")
        session.phase = StudySessionPhase.BREAK
        session.break_started_at = datetime.now(UTC)
        await self.db.flush()
        await self.activity_service.record_break_started(session)
        return session

    async def end_break(self, user_id: uuid.UUID) -> StudySession:
        session = await self._require_active(user_id)
        if getattr(session, "phase", StudySessionPhase.FOCUS) != StudySessionPhase.BREAK:
            raise ConflictError("Aktif mola yok")
        await self._close_break(session, datetime.now(UTC))
        session.status = StudySessionStatus.RUNNING
        await self.db.flush()
        await self.activity_service.record_break_ended(session)
        return session

    async def _close_break(self, session: StudySession, now: datetime) -> None:
        started = session.break_started_at
        if started is None:
            session.phase = StudySessionPhase.FOCUS
            return
        seconds = max(0, int((now - started).total_seconds()))
        minutes = math.ceil(seconds / 60) if seconds > 0 else 0
        session.actual_break_minutes = int(getattr(session, "actual_break_minutes", 0) or 0) + minutes
        # Also treat break time as non-focus (like pause)
        session.paused_seconds += seconds
        segs = list(getattr(session, "break_segments", None) or [])
        segs.append(
            {
                "started_at": started.isoformat(),
                "ended_at": now.isoformat(),
                "minutes": minutes,
            }
        )
        session.break_segments = segs
        session.break_started_at = None
        session.phase = StudySessionPhase.FOCUS

    async def today_summary(self, user_id: uuid.UUID) -> StudyTodaySummary:
        today = datetime.now(UTC).date()
        sessions = await self.repo.list_for_user_on_date(user_id, today)
        completed = [s for s in sessions if s.status == StudySessionStatus.COMPLETED]
        focus = sum(s.actual_duration_minutes for s in completed)
        breaks = sum(int(getattr(s, "actual_break_minutes", 0) or 0) for s in completed)

        plans = await self.plan_repo.list_for_user(user_id, today)
        planned = sum(p.estimated_minutes or 0 for p in plans)
        done_plans = sum(
            1
            for p in plans
            if p.status == StudyPlanStatus.COMPLETED
        )
        adherence = (
            round(100.0 * done_plans / len(plans), 1) if plans else 0.0
        )

        # Goal: planned minutes or profile daily
        goal = planned
        if goal <= 0:
            try:
                from app.services.learning_profile_service import LearningProfileService

                student = await LearningProfileService(self.db).ensure_student(user_id)
                goal = int(getattr(student, "daily_study_minutes", 0) or 0)
            except Exception:
                goal = 0

        by_code: dict[str, int] = {}
        for s in completed:
            code = (s.subject_code or "serbest").strip() or "serbest"
            by_code[code] = by_code.get(code, 0) + s.actual_duration_minutes

        plan_by_subj: dict[str, int] = {}
        for p in plans:
            key = (p.subject or "serbest").strip() or "serbest"
            plan_by_subj[key] = plan_by_subj.get(key, 0) + int(p.estimated_minutes or 0)

        by_subject = [
            SubjectMinutesItem(
                subject_code=code,
                subject_label=code,
                focus_minutes=mins,
                planned_minutes=plan_by_subj.get(code, 0),
            )
            for code, mins in sorted(by_code.items(), key=lambda x: -x[1])
        ]

        hourly = [0] * 24
        for s in completed:
            h = s.started_at.astimezone(UTC).hour if s.started_at.tzinfo else s.started_at.hour
            hourly[h] += s.actual_duration_minutes

        return StudyTodaySummary(
            focus_minutes=focus,
            break_minutes=breaks,
            planned_minutes=planned,
            goal_minutes=goal,
            plan_adherence_pct=adherence,
            goal_gap_minutes=max(0, goal - focus),
            completed_plan_count=done_plans,
            total_plan_count=len(plans),
            by_subject=by_subject,
            hourly_minutes=hourly,
        )

    def _engine_state(self, session: StudySession) -> str:
        """M25 state machine projection — IDLE|STUDYING|BREAK|PAUSED|COMPLETED."""
        status = session.status
        phase = getattr(session, "phase", StudySessionPhase.FOCUS)
        if status == StudySessionStatus.COMPLETED:
            return "COMPLETED"
        if status == StudySessionStatus.PAUSED:
            return "PAUSED"
        if status == StudySessionStatus.RUNNING:
            if phase == StudySessionPhase.BREAK:
                return "BREAK"
            return "STUDYING"
        return "IDLE"

    async def get_active(self, user_id: uuid.UUID) -> StudySession | None:
        """Aktif (running/paused) oturum; yoksa None."""
        return await self.repo.get_active_for_user(user_id)

    async def _require_active(self, user_id: uuid.UUID) -> StudySession:

        session = await self.repo.get_active_for_user(user_id)

        if session is None:

            raise NotFoundError("Aktif çalışma oturumu", "")

        return session



    async def _apply_progress_to_plan(self, session: StudySession):

        """Finish sonrası bağlı plana artımlı ilerleme yazar; otomatik completed yapmaz."""

        if session.study_plan_id is None:

            return None

        plan = await self.plan_repo.get_by_id_for_user(session.study_plan_id, session.user_id)

        if plan is None:

            return None

        if plan.status in (StudyPlanStatus.COMPLETED, StudyPlanStatus.SKIPPED):

            return plan



        plan.completed_minutes += session.actual_duration_minutes

        plan.completed_question_count += session.completed_questions

        if plan.status == StudyPlanStatus.PLANNED:

            plan.status = StudyPlanStatus.IN_PROGRESS

        await self.db.flush()

        return plan


