"""
StudyOS — Learning Profile & Onboarding Service (Sprint-3.0)
LLM plan/hedef/ders üretmez (I1). Journey stage RuleEngine (M1).
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from urllib.parse import quote

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_DAILY_STUDY_GOAL_MINUTES
from app.core.exceptions import NotFoundError, ValidationError
from app.models.exam import Exam
from app.models.learning_profile import (
    BaselineLevel,
    ExamTarget,
    JourneyStage,
    Student,
    SubjectCatalog,
    TopicCatalog,
    UserSubject,
)
from app.models.question_record import ExamType, QuestionRecord
from app.repositories.learning_profile_repository import LearningProfileRepository
from app.services.ai.subject_catalog_seed import (
    SUBJECT_CATALOG_SEED,
    codes_for_exam,
)
from app.services.ai.topic_catalog_seed import TOPIC_CATALOG_SEED
from app.schemas.learning_profile import (
    DashboardSubjectsSummary,
    ExamTargetCreate,
    ExamTargetRead,
    ExamTargetUpdate,
    JourneyProgressSummary,
    LearningProfileRead,
    LearningProfileUpdate,
    OnboardingCompleteRequest,
    OnboardingStatusRead,
    SubjectCatalogRead,
    SubjectHubAi,
    SubjectHubDetail,
    SubjectHubExamSummary,
    SubjectHubFlashcards,
    SubjectHubIdentity,
    SubjectHubPlans,
    SubjectHubProgress,
    SubjectHubResources,
    SubjectHubRevision,
    SubjectHubToday,
    SubjectHubTopics,
    TopicCatalogRead,
    UserSubjectRead,
)
from app.schemas.topic_work_surface import (
    TopicLearningState,
    TopicSecondaryTool,
    TopicWorkSurfaceProjection,
)
from app.services.ai.journey_stage_engine import build_stage_reason, evaluate_journey_stage
from app.services.ai.next_action_engine import build_action_for_topic
from app.services.statistics_service import StatisticsService
from app.services.revision_service import RevisionService
from app.services.exam_catalog_service import ExamCatalogService
from app.services.topic_catalog_resolver import (
    canonical_topic_code_for_display,
    is_blocked_legacy_topic,
    topic_catalog_ssot_enabled,
)



class LearningProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LearningProfileRepository(db)

    async def ensure_student(self, user_id: uuid.UUID) -> Student:
        student = await self.repo.get_student(user_id)
        if student:
            return student
        student = Student(
            user_id=user_id,
            journey_stage=JourneyStage.NEW_USER,
            daily_study_minutes=DEFAULT_DAILY_STUDY_GOAL_MINUTES,
            available_days=[0, 1, 2, 3, 4],
            available_hours=2.0,
            baseline_level=BaselineLevel.UNKNOWN,
            baseline_reason="Henüz değerlendirilmedi",
        )
        return await self.repo.create_student(student)

    def _onboarding_flags(self, student: Student) -> tuple[bool, bool, bool]:
        completed = student.onboarding_completed_at is not None
        skipped = student.onboarding_skipped_at is not None
        # Sprint-3.1.A — hard gate: skip artık required'ı kapatmaz
        required = not completed
        return completed, skipped, required

    def _primary_exam_type(self, targets: list) -> str | None:
        for t in targets:
            if t.is_primary:
                return str(t.exam_type)
        return str(targets[0].exam_type) if targets else None

    def resolve_active_exam_type(
        self, student: Student, targets: list, *, override: str | None = None
    ) -> str | None:
        """Active → override → stored → Primary. Geçersiz stored Primary'ye düşer."""
        allowed = {str(t.exam_type) for t in targets}
        if override:
            return override if override in allowed else None
        stored = student.active_exam_type
        if stored and stored in allowed:
            return stored
        return self._primary_exam_type(targets)

    async def get_profile(self, user_id: uuid.UUID) -> LearningProfileRead:
        student = await self.ensure_student(user_id)
        await self.refresh_journey_stage(user_id)
        student = await self.repo.get_student(user_id) or student
        completed, skipped, required = self._onboarding_flags(student)
        targets = await self.repo.list_exam_targets(user_id)
        if targets:
            await self._seed_subjects_for_exams(user_id, targets)
        subjects = await self._active_user_subjects(user_id)
        primary = self._primary_exam_type(targets)
        active = self.resolve_active_exam_type(student, targets)
        # Self-heal: stored active geçersizse Primary'ye yaz
        if targets and student.active_exam_type != active:
            student.active_exam_type = active
            await self.db.flush()
        # Active Exam scope — Derslerim'de başka sınavın konuları (örn. Anayasa/KPSS) görünmesin
        allowed = self._allowed_codes_for_active(targets, active)
        if allowed is not None:
            subjects = [r for r in subjects if r.subject_code in allowed]
        elif active:
            catalog = await self.repo.list_catalog(exam_type=active)
            codes = {c.code for c in catalog}
            if codes:
                subjects = [r for r in subjects if r.subject_code in codes]
        return LearningProfileRead(
            user_id=user_id,
            journey_stage=JourneyStage(student.journey_stage),
            onboarding_completed=completed,
            onboarding_skipped=skipped,
            onboarding_required=required,
            daily_study_minutes=student.daily_study_minutes,
            available_days=list(student.available_days or []),
            available_hours=float(student.available_hours),
            baseline_level=BaselineLevel(student.baseline_level),
            baseline_reason=student.baseline_reason,
            exam_targets=[ExamTargetRead.model_validate(t) for t in targets],
            subjects=await self._enrich_subjects(user_id, subjects),
            primary_exam_type=primary,
            active_exam_type=active,
        )

    async def update_profile(
        self, user_id: uuid.UUID, data: LearningProfileUpdate
    ) -> LearningProfileRead:
        student = await self.ensure_student(user_id)
        if data.daily_study_minutes is not None:
            student.daily_study_minutes = data.daily_study_minutes
        if data.available_days is not None:
            student.available_days = data.available_days
        if data.available_hours is not None:
            student.available_hours = data.available_hours
        if data.baseline_level is not None:
            student.baseline_level = data.baseline_level
        if data.baseline_reason is not None:
            student.baseline_reason = data.baseline_reason
        await self.db.flush()
        await self.refresh_journey_stage(user_id)
        return await self.get_profile(user_id)

    async def onboarding_status(self, user_id: uuid.UUID) -> OnboardingStatusRead:
        student = await self.ensure_student(user_id)
        await self.refresh_journey_stage(user_id)
        student = await self.repo.get_student(user_id) or student
        completed, skipped, required = self._onboarding_flags(student)
        return OnboardingStatusRead(
            onboarding_required=required,
            onboarding_completed=completed,
            onboarding_skipped=skipped,
            journey_stage=JourneyStage(student.journey_stage),
            can_skip=False,
        )

    async def complete_onboarding(
        self, user_id: uuid.UUID, data: OnboardingCompleteRequest
    ) -> LearningProfileRead:
        """Rule-based complete — LLM yok (I1). Dersler katalogdan seed (C1)."""
        student = await self.ensure_student(user_id)
        # Replace targets for clean onboarding
        existing = await self.repo.list_exam_targets(user_id)
        for row in existing:
            await self.repo.delete_exam_target(row)

        primary_set = False
        for idx, item in enumerate(data.exam_targets):
            is_primary = bool(item.is_primary) if any(t.is_primary for t in data.exam_targets) else idx == 0
            if is_primary and primary_set:
                is_primary = False
            if is_primary:
                primary_set = True
            exam_date = item.exam_date
            if exam_date is None:
                from app.services.exam_calendar import next_exam_date

                exam_date = next_exam_date(str(item.exam_type))
            await self.repo.add_exam_target(
                ExamTarget(
                    user_id=user_id,
                    exam_type=str(item.exam_type),
                    is_primary=is_primary,
                    weight=item.weight,
                    target_net=item.target_net,
                    target_score=item.target_score,
                    target_rank=item.target_rank,
                    target_university=item.target_university,
                    target_department=item.target_department,
                    branch=item.branch,
                    exam_date=exam_date,
                )
            )

        student.available_days = data.available_days
        student.available_hours = data.available_hours
        student.daily_study_minutes = data.daily_study_minutes
        student.baseline_level = data.baseline_level
        student.baseline_reason = data.baseline_reason or (
            "Kullanıcı onboarding self-assess"
            if data.baseline_level != BaselineLevel.UNKNOWN
            else "Seviye henüz bilinmiyor"
        )
        student.onboarding_completed_at = datetime.now(UTC)
        student.onboarding_skipped_at = None
        # Sprint-3.1.A — Active = Primary after complete
        primary_type = None
        for t in data.exam_targets:
            if t.is_primary:
                primary_type = str(t.exam_type)
                break
        if primary_type is None and data.exam_targets:
            primary_type = str(data.exam_targets[0].exam_type)
        student.active_exam_type = primary_type
        await self.db.flush()

        targets = await self.repo.list_exam_targets(user_id)
        await self._seed_subjects_for_exams(user_id, targets)
        await self.refresh_journey_stage(user_id)
        return await self.get_profile(user_id)

    async def set_active_exam(
        self, user_id: uuid.UUID, exam_type: ExamType | str
    ) -> LearningProfileRead:
        """Sprint-3.1.A — Active Exam SSOT; Primary değişmez."""
        student = await self.ensure_student(user_id)
        targets = await self.repo.list_exam_targets(user_id)
        allowed = {str(t.exam_type) for t in targets}
        et = str(exam_type)
        if et not in allowed:
            raise ValidationError(
                f"Active exam profilinizde yok: {et.upper()}",
                field="exam_type",
            )
        student.active_exam_type = et
        await self.db.flush()
        return await self.get_profile(user_id)

    async def skip_onboarding(self, user_id: uuid.UUID) -> LearningProfileRead:
        """D2 — soft skip; Dashboard erişilebilir."""
        student = await self.ensure_student(user_id)
        if student.onboarding_completed_at is None:
            student.onboarding_skipped_at = datetime.now(UTC)
        await self.db.flush()
        await self.refresh_journey_stage(user_id)
        return await self.get_profile(user_id)

    async def ensure_catalog_synced(self) -> None:
        """Sprint-3.1.C.x — upsert SUBJECT_CATALOG_SEED into DB (no migration)."""
        for item in SUBJECT_CATALOG_SEED:
            code = str(item["code"])
            row = await self.repo.get_catalog_by_code(code)
            is_active = bool(item.get("is_active", True))
            name = str(item["name"])
            exam_types = list(item.get("exam_types") or [])
            sort_order = int(item.get("sort_order") or 0)
            section = item.get("section")
            if row is None:
                await self.repo.add_catalog_row(
                    SubjectCatalog(
                        code=code,
                        name=name,
                        exam_types=exam_types,
                        sort_order=sort_order,
                        section=section,
                        is_active=is_active,
                    )
                )
            else:
                row.name = name
                row.exam_types = exam_types
                row.sort_order = sort_order
                row.section = section
                row.is_active = is_active
        await self.db.flush()

    async def ensure_topic_catalog_synced(self) -> None:
        """Sprint-3.2.A — upsert TOPIC_CATALOG_SEED (requires subject catalog rows)."""
        await self.ensure_catalog_synced()
        for item in TOPIC_CATALOG_SEED:
            code = str(item["code"])
            subject_code = str(item["subject_code"])
            # Skip if parent subject missing (FK)
            parent = await self.repo.get_catalog_by_code(subject_code)
            if parent is None:
                continue
            row = await self.repo.get_topic_by_code(code)
            name = str(item["name"])
            sort_order = int(item.get("sort_order") or 0)
            difficulty = item.get("difficulty")
            is_active = bool(item.get("is_active", True))
            if row is None:
                await self.repo.add_topic_row(
                    TopicCatalog(
                        code=code,
                        name=name,
                        subject_code=subject_code,
                        sort_order=sort_order,
                        difficulty=int(difficulty) if difficulty is not None else None,
                        is_active=is_active,
                    )
                )
            else:
                row.name = name
                row.subject_code = subject_code
                row.sort_order = sort_order
                row.difficulty = int(difficulty) if difficulty is not None else None
                row.is_active = is_active
        await self.db.flush()

    async def list_topics_for_subject(self, subject_code: str) -> list[TopicCatalogRead]:
        code = subject_code.strip()
        if not code:
            raise ValidationError("subject_code gerekli", field="subject_code")
        await self.ensure_topic_catalog_synced()
        parent = await self.repo.get_catalog_by_code(code)
        if parent is None or not parent.is_active:
            raise NotFoundError("Subject", code)
        rows = await self.repo.list_topics(subject_code=code, active_only=True)
        return [TopicCatalogRead.model_validate(r) for r in rows]

    async def _seed_subjects_for_exams(
        self, user_id: uuid.UUID, targets: list[ExamTarget]
    ) -> None:
        """Seed user_subjects from catalog using exam_type + branch (3.1.C.x)."""
        await self.ensure_catalog_synced()
        allowed: set[str] = set()
        for t in targets:
            et = str(t.exam_type)
            branch = t.branch
            specific = codes_for_exam(et, branch)
            if specific is not None:
                allowed.update(specific)
            else:
                catalog = await self.repo.list_catalog(exam_type=et)
                allowed.update(c.code for c in catalog)

        # Activate / upsert allowed codes
        for code in sorted(allowed):
            cat = await self.repo.get_catalog_by_code(code)
            if cat is None or not cat.is_active:
                continue
            existing = await self.repo.get_user_subject(user_id, code)
            if existing:
                existing.is_active = True
                existing.subject_name = cat.name
                continue
            await self.repo.add_user_subject(
                UserSubject(
                    user_id=user_id,
                    subject_code=code,
                    subject_name=cat.name,
                    is_active=True,
                    source="onboarding",
                )
            )

        # Soft-deactivate user subjects whose catalog row is inactive or not allowed
        all_user = await self.repo.list_user_subjects(user_id, active_only=False)
        for row in all_user:
            cat = await self.repo.get_catalog_by_code(row.subject_code)
            if cat is None or not cat.is_active or row.subject_code not in allowed:
                if row.is_active:
                    row.is_active = False
        await self.db.flush()

    def _allowed_codes_for_active(
        self, targets: list[ExamTarget], effective: str | None
    ) -> set[str] | None:
        if not effective:
            return None
        target = next((t for t in targets if str(t.exam_type) == effective), None)
        branch = target.branch if target else None
        specific = codes_for_exam(effective, branch)
        if specific is not None:
            return specific
        return None

    async def resolve_active_scope(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> tuple[str | None, set[str], set[str]]:
        """M17.3 SSOT — (effective_exam, subject_codes_lower, subject_names_lower)."""
        student = await self.ensure_student(user_id)
        targets = await self.repo.list_exam_targets(user_id)
        effective = self.resolve_active_exam_type(
            student, targets, override=exam_type
        )
        if effective is None:
            effective = self._primary_exam_type(targets)
        codes: set[str] = set()
        names: set[str] = set()
        if not effective:
            return None, codes, names
        allowed = self._allowed_codes_for_active(targets, effective)
        if allowed is not None:
            codes = {c.lower() for c in allowed}
            catalog = await self.repo.list_catalog()
            names = {
                c.name.lower()
                for c in catalog
                if c.code.lower() in codes
            }
        else:
            catalog = await self.repo.list_catalog(exam_type=effective)
            codes = {c.code.lower() for c in catalog}
            names = {c.name.lower() for c in catalog}
        return effective, codes, names

    async def list_catalog(self, exam_type: str | None = None) -> list[SubjectCatalogRead]:
        await self.ensure_catalog_synced()
        rows = await self.repo.list_catalog(exam_type=exam_type)
        return [SubjectCatalogRead.model_validate(r) for r in rows]

    async def list_my_subjects(
        self, user_id: uuid.UUID, *, exam_type: str | None = None
    ) -> list[UserSubjectRead]:
        """Sprint-3.1.C — default Active Exam scope; identity = subject_code."""
        student = await self.ensure_student(user_id)
        targets = await self.repo.list_exam_targets(user_id)
        if targets:
            await self._seed_subjects_for_exams(user_id, targets)
        rows = await self._active_user_subjects(user_id)
        effective = self.resolve_active_exam_type(student, targets, override=exam_type)
        if effective is None:
            effective = self._primary_exam_type(targets)
        allowed = self._allowed_codes_for_active(targets, effective)
        if allowed is not None:
            rows = [r for r in rows if r.subject_code in allowed]
        elif effective:
            catalog = await self.repo.list_catalog(exam_type=effective)
            codes = {c.code for c in catalog}
            if codes:
                rows = [r for r in rows if r.subject_code in codes]
        return await self._enrich_subjects(user_id, rows)

    async def get_subject_hub(
        self, user_id: uuid.UUID, subject_code: str
    ) -> SubjectHubDetail:
        """Sprint-3.1.C — Subject Hub detail; lookup by subject_code only."""
        code = subject_code.strip()
        if not code:
            raise ValidationError("subject_code gerekli", field="subject_code")

        student = await self.ensure_student(user_id)
        targets = await self.repo.list_exam_targets(user_id)
        if targets:
            await self._seed_subjects_for_exams(user_id, targets)

        row = await self.repo.get_user_subject(user_id, code)
        if row is None:
            raise NotFoundError("Subject", code)

        # M17.1 — Active Exam soft-guard: hub başka sınav dersine açılmasın
        active = self.resolve_active_exam_type(student, targets)
        allowed = self._allowed_codes_for_active(targets, active)
        if allowed is not None and code not in allowed:
            raise NotFoundError("Subject", code)
        if allowed is None and active:
            catalog_for_active = await self.repo.list_catalog(exam_type=active)
            active_codes = {c.code for c in catalog_for_active}
            if active_codes and code not in active_codes:
                raise NotFoundError("Subject", code)

        catalog_rows = await self.repo.list_catalog()
        cat = next((c for c in catalog_rows if c.code == code), None)
        enriched = await self._enrich_subjects(user_id, [row])
        metrics = enriched[0]

        today = datetime.now(UTC).date()
        # Legacy activity bridge: display name on UserSubject row only (not API identity)
        display_name = row.subject_name

        from app.models.study_plan import StudyPlanStatus
        from app.repositories.study_plan_repository import StudyPlanRepository
        from app.services.ai_insights_service import AiInsightsService
        from app.services.exam_service import ExamService
        from app.services.question_record_service import QuestionRecordService
        from app.services.revision_service import RevisionService

        plans = await StudyPlanRepository(self.db).list_for_user(user_id, today)
        subject_plans = [
            p for p in plans if (p.subject or "").strip().casefold() == display_name.strip().casefold()
        ]
        completed_plans = sum(
            1 for p in subject_plans if p.status == StudyPlanStatus.COMPLETED
        )
        next_plan = next(
            (p for p in subject_plans if p.status != StudyPlanStatus.COMPLETED),
            None,
        )

        q_rows, _ = await QuestionRecordService(self.db).list_records(
            user_id,
            page=1,
            page_size=50,
            date_from=today,
            date_to=today,
            subject=display_name,
        )
        today_q = sum(int(r.question_count or 0) for r in q_rows)

        revision_summary = await RevisionService(self.db).dashboard_summary(user_id)
        rev_items = await RevisionService(self.db).repo.list_for_user(
            user_id, subject=display_name, limit=50
        )
        due_today = 0
        overdue = 0
        now = datetime.now(UTC)
        next_rev_title = None
        for item in rev_items:
            sched = item.schedule
            if sched is None or sched.due_at is None:
                continue
            due_at = sched.due_at
            if due_at.tzinfo is None:
                due_at = due_at.replace(tzinfo=UTC)
            if due_at.date() == today:
                due_today += 1
                next_rev_title = next_rev_title or item.title
            elif due_at < now:
                overdue += 1
                next_rev_title = next_rev_title or item.title

        exam_summary = SubjectHubExamSummary(placeholder=True, available=False)
        trends = await ExamService(self.db).get_trends(user_id)
        match = next(
            (
                s
                for s in trends.by_subject
                if s.subject.strip().casefold() == display_name.strip().casefold()
            ),
            None,
        )
        if match is not None:
            exam_summary = SubjectHubExamSummary(
                average_net=match.average_net,
                exam_count=match.exam_count,
                last_net=None,
                available=True,
                placeholder=False,
            )

        top_rec = await AiInsightsService(self.db).get_top_recommendation(user_id)
        ai = SubjectHubAi(explain_available=False)
        if top_rec is not None:
            name_cf = display_name.strip().casefold()
            msg = (top_rec.message or "").casefold()
            reason = (top_rec.reason or "").casefold()
            related = (
                name_cf in msg
                or name_cf in reason
                or top_rec.code
                in {"neglected_subject", "low_accuracy", "keep_going", "insufficient_data"}
            )
            if related:
                ai = SubjectHubAi(
                    recommendation=top_rec.message,
                    reason=top_rec.reason,
                    code=top_rec.code,
                    explain_available=False,
                )

        active = self.resolve_active_exam_type(student, targets)
        primary = self._primary_exam_type(targets)

        return SubjectHubDetail(
            subject=SubjectHubIdentity(
                subject_code=row.subject_code,
                subject_name=row.subject_name,
                section=cat.section if cat else metrics.section,
                exam_types=list(cat.exam_types) if cat and cat.exam_types else [],
                is_active=row.is_active,
                source=row.source,
            ),
            progress=SubjectHubProgress(
                progress_pct=metrics.progress_pct,
                accuracy=metrics.accuracy,
                total_questions=metrics.total_questions,
                study_minutes=metrics.study_minutes,
                last_studied_at=metrics.last_studied_at,
                last_revision_at=metrics.last_revision_at,
            ),
            today=SubjectHubToday(
                study_minutes=0,
                questions_solved=today_q,
                plan_count=len(subject_plans),
                completed_plan_count=completed_plans,
            ),
            revision=SubjectHubRevision(
                due_today=due_today,
                overdue=overdue,
                due_this_week=revision_summary.due_this_week,
                next_title=next_rev_title or revision_summary.next_title,
                overview_reason=revision_summary.overview_reason,
                available=True,
            ),
            plans=SubjectHubPlans(
                today_count=len(subject_plans),
                completed_count=completed_plans,
                next_title=(next_plan.title if next_plan else None),
                overview_reason=None,
                available=True,
            ),
            exam_summary=exam_summary,
            resources=SubjectHubResources(placeholder=True, available=False),
            flashcards=SubjectHubFlashcards(),
            topics=await self._hub_topics(code, exam_type=active or primary),
            ai=ai,
            active_exam_type=active,
            primary_exam_type=primary,
        )

    async def get_topic_work_surface(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
    ) -> TopicWorkSurfaceProjection:
        """
        Alignment Sprint-3 — Topic Work Surface projection.
        Karar üretmez; Decision Engine (build_action_for_topic) uygular.
        """
        sub = subject_code.strip()
        top = topic_code.strip()
        if not sub or not top:
            raise ValidationError(
                "subject_code ve topic_code gerekli",
                field="topic_code",
            )

        await self.ensure_topic_catalog_synced()
        topic = await self.repo.get_topic_by_code(top)
        if topic is None or topic.subject_code != sub:
            raise NotFoundError("Topic", top)

        catalog = await self.repo.get_catalog_by_code(sub)
        subject_name = catalog.name if catalog else None

        revision_due = await self._topic_revision_due(
            user_id, subject_code=sub, topic_name=topic.name, topic_code=top
        )

        # ── LOS Module 4+5: Topic-scoped Policy Decision ──────────────
        topic_ai_reason: str | None = None
        try:
            from app.services.policy_decision_engine import PolicyDecisionEngine
            decision = await PolicyDecisionEngine(self.db).decide_for_topic(
                user_id, sub, top
            )
            topic_ai_reason = decision.reason
        except Exception:
            pass

        primary = build_action_for_topic(
            subject_code=sub,
            topic_code=top,
            topic_name=topic.name,
            revision_due_for_topic=revision_due,
            ai_reason=topic_ai_reason,
        )

        # Confidence-aware summary line
        if revision_due:
            summary = "Bu konu için tekrar zamanı geldi."
        elif topic_ai_reason:
            summary = topic_ai_reason
        else:
            summary = "Bu konu üzerinde çalışmaya hazırsın."
        q = (
            f"subject_code={sub}&topic_code={top}"
            f"&topic_name={quote(topic.name, safe='')}"
        )
        secondary = [
            TopicSecondaryTool(
                id="pomodoro",
                label="Pomodoro",
                deep_link_hint=f"/pomodoro?{q}",
            ),
            TopicSecondaryTool(
                id="resources",
                label="Kaynak",
                deep_link_hint=f"/resources?{q}",
            ),
            TopicSecondaryTool(
                id="questions",
                label="Soru Kaydı",
                deep_link_hint=f"/questions?{q}",
            ),
            TopicSecondaryTool(
                id="topic_quiz",
                label="Bu konu için soru üret",
                deep_link_hint=f"/quiz-session?{q}",
            ),
            TopicSecondaryTool(
                id="revision",
                label="Revision Durumu",
                deep_link_hint=f"/revisions?{q}",
            ),
        ]
        # M5.3 — Sprint 5: Bu konudaki oturum istatistiklerini sorgula
        from sqlalchemy import func as sqlfunc, select as sqlselect
        from app.models.study_session import StudySession as StudySessionModel
        from app.models.question_record import QuestionRecord as QuestionRecordModel

        topic_stats = await self.db.execute(
            sqlselect(
                sqlfunc.coalesce(sqlfunc.sum(StudySessionModel.actual_duration_minutes), 0),
                sqlfunc.count(StudySessionModel.id),
            ).where(
                StudySessionModel.user_id == user_id,
                StudySessionModel.topic_code == top,
                StudySessionModel.status == "finished",
            )
        )
        topic_minutes, topic_sessions = topic_stats.one()

        # M6.3 — Sprint 6: D/Y/B performans özeti
        qr_stats = await self.db.execute(
            sqlselect(
                sqlfunc.coalesce(sqlfunc.sum(QuestionRecordModel.correct_count), 0),
                sqlfunc.coalesce(sqlfunc.sum(QuestionRecordModel.wrong_count), 0),
                sqlfunc.coalesce(sqlfunc.sum(QuestionRecordModel.blank_count), 0),
                sqlfunc.coalesce(sqlfunc.sum(QuestionRecordModel.question_count), 0),
            ).where(
                QuestionRecordModel.user_id == user_id,
                QuestionRecordModel.topic_code == top,
            )
        )
        q_correct, q_wrong, q_blank, q_total = qr_stats.one()
        q_correct = int(q_correct or 0)
        q_wrong = int(q_wrong or 0)
        q_blank = int(q_blank or 0)
        q_total = int(q_total or 0)
        accuracy_pct = round((q_correct / q_total) * 100, 1) if q_total > 0 else 0.0

        # Sprint 15 — Intelligence projections (read-only)
        from app.services.learning_intelligence_service import LearningIntelligenceService

        intel_svc = LearningIntelligenceService(self.db)
        intelligence = await intel_svc.topic_intelligence(
            user_id,
            sub,
            top,
            topic_name=topic.name,
            revision_due=revision_due,
            suggestion_fallback=summary,
        )
        timeline = await intel_svc.topic_timeline(user_id, sub, top, limit=12)
        insights = await intel_svc.topic_insights(
            user_id,
            sub,
            top,
            topic_name=topic.name,
            revision_due=revision_due,
        )
        quiz_history = await intel_svc.quiz_history(user_id, top, limit=8)
        resources = await intel_svc.resource_intelligence(
            user_id,
            sub,
            top,
            confidence_level=intelligence.confidence_level,
            revision_due=revision_due,
        )

        coach_headline = primary.title
        coach_body = primary.reason
        coach_cta = primary.cta_label
        coach_deep = primary.deep_link_hint
        # RC.2 — Work Surface CoachService.today çağırmaz (Dashboard zaten taşır);
        # Primary Action SSOT ile tutarlı kalır.

        return TopicWorkSurfaceProjection(
            learning_state=TopicLearningState(
                subject_code=sub,
                topic_code=top,
                topic_name=topic.name,
                subject_name=subject_name,
                summary_line=summary,
                revision_due=revision_due,
                study_minutes=int(topic_minutes or 0),
                session_count=int(topic_sessions or 0),
                correct_count=q_correct,
                wrong_count=q_wrong,
                blank_count=q_blank,
                question_count=q_total,
                accuracy_pct=accuracy_pct,
            ),
            primary_action=primary,
            secondary_tools=secondary,
            intelligence=intelligence,
            timeline=timeline,
            insights=insights,
            quiz_history=quiz_history,
            resources=resources,
            coach_headline=coach_headline,
            coach_body=coach_body,
            coach_cta_label=coach_cta,
            coach_deep_link_hint=coach_deep,
        )

    async def _topic_revision_due(
        self,
        user_id: uuid.UUID,
        *,
        subject_code: str,
        topic_name: str,
        topic_code: str,
    ) -> bool:
        """Best-effort: due today revision eşleşmesi (topic_code FK migration yok)."""
        from datetime import timedelta

        revision = RevisionService(self.db)
        today = datetime.now(UTC).date()
        start = datetime(today.year, today.month, today.day, tzinfo=UTC)
        end = start + timedelta(days=1)
        due_items = await revision.repo.list_due(user_id, until=end)
        overdue = await revision.repo.list_due(
            user_id, until=start, overdue_only=False
        )
        by_id = {item.id: item for item in [*due_items, *overdue]}
        items = list(by_id.values())
        name_l = topic_name.strip().lower()
        code_l = topic_code.strip().lower()
        sub_l = subject_code.strip().lower()
        catalog = await self.repo.get_catalog_by_code(subject_code)
        sub_name_l = (catalog.name if catalog else "").strip().lower()

        for item in items:
            t = (item.topic or "").strip().lower()
            s = (item.subject or "").strip().lower()
            topic_match = t and (t == name_l or t == code_l or name_l in t or t in name_l)
            subject_match = (
                not s
                or s == sub_l
                or (sub_name_l and (s == sub_name_l or sub_name_l in s or s in sub_name_l))
            )
            if topic_match and subject_match:
                return True
        return False

    async def _hub_topics(
        self, subject_code: str, *, exam_type: str | None = None
    ) -> SubjectHubTopics:
        if topic_catalog_ssot_enabled() and exam_type:
            try:
                ei_topics = await ExamCatalogService(self.db).list_topics(
                    exam_type, subject_code
                )
                items = [
                    TopicCatalogRead(
                        id=t.id,
                        code=canonical_topic_code_for_display(t.code),
                        name=t.name,
                        subject_code=t.subject_code,
                        sort_order=t.display_order,
                        difficulty=None,
                        is_active=t.is_active,
                    )
                    for t in ei_topics
                    if t.code and not is_blocked_legacy_topic(t.code)
                ]
                if items:
                    return SubjectHubTopics(
                        items=items, count=len(items), available=True
                    )
            except Exception:
                pass
        await self.ensure_topic_catalog_synced()
        rows = await self.repo.list_topics(subject_code=subject_code, active_only=True)
        items = [TopicCatalogRead.model_validate(r) for r in rows]
        return SubjectHubTopics(items=items, count=len(items), available=True)

    async def _active_user_subjects(self, user_id: uuid.UUID) -> list[UserSubject]:
        """Pasif katalog kodlarını gizle (legacy seed sonrası)."""
        rows = await self.repo.list_user_subjects(user_id)
        catalog = await self.repo.list_catalog()
        active_codes = {c.code for c in catalog}
        return [r for r in rows if r.subject_code in active_codes]

    async def _enrich_subjects(
        self, user_id: uuid.UUID, rows: list[UserSubject]
    ) -> list[UserSubjectRead]:
        catalog = await self.repo.list_catalog()
        by_code = {c.code: c for c in catalog}
        q_map = await self.repo.question_metrics_by_subject(user_id)
        s_map = await self.repo.study_minutes_by_subject(user_id)
        r_map = await self.repo.last_revision_by_subject(user_id)

        out: list[UserSubjectRead] = []
        for row in rows:
            cat = by_code.get(row.subject_code)
            key = row.subject_name.strip().casefold()
            q_total, q_correct, q_duration, q_last = q_map.get(key, (0, 0, 0, None))
            study_minutes, session_last = s_map.get(key, (0, None))
            # Soru kaydı süresi + oturum süresi (çift sayım riski düşük; additive UX)
            total_minutes = int(study_minutes) + int(q_duration)
            accuracy = round((q_correct / q_total) * 100, 1) if q_total > 0 else 0.0
            last_studied = q_last
            if session_last is not None and (last_studied is None or session_last > last_studied):
                last_studied = session_last
            # Progress: accuracy ağırlıklı + hacim soft-cap
            volume_boost = min(q_total / 100.0, 1.0) * 20.0 if q_total else 0.0
            progress = round(min(100.0, accuracy * 0.8 + volume_boost), 1) if q_total else 0.0

            out.append(
                UserSubjectRead(
                    id=row.id,
                    subject_code=row.subject_code,
                    subject_name=row.subject_name,
                    is_active=row.is_active,
                    source=row.source,
                    section=cat.section if cat else None,
                    total_questions=q_total,
                    study_minutes=total_minutes,
                    accuracy=accuracy,
                    last_studied_at=last_studied,
                    last_revision_at=r_map.get(key),
                    progress_pct=progress,
                )
            )
        order = {c.code: c.sort_order for c in catalog}
        out.sort(key=lambda s: (order.get(s.subject_code, 9999), s.subject_name))
        return out

    def build_subjects_summary(
        self,
        subjects: list[UserSubjectRead],
        *,
        primary_exam_type: str | None = None,
    ) -> DashboardSubjectsSummary:
        today = datetime.now(UTC).date()
        most_studied = None
        weakest = None
        longest_idle = None
        if subjects:
            most_studied = max(subjects, key=lambda s: (s.study_minutes, s.total_questions)).subject_name
            with_q = [s for s in subjects if s.total_questions > 0]
            # Furthest below typical target band (accuracy as proxy when no exam row here).
            # Prefer none over labeling a strong subject "weak".
            target_acc = 70.0
            below = [s for s in with_q if s.accuracy < target_acc]
            if below:
                weakest = min(
                    below,
                    key=lambda s: (s.accuracy - target_acc, -s.total_questions),
                ).subject_name
            else:
                weakest = None
            # En uzun süredir çalışılmayan: last_studied_at None önce, sonra en eski
            def idle_key(s: UserSubjectRead) -> tuple:
                if s.last_studied_at is None:
                    return (0, datetime.min.replace(tzinfo=UTC))
                return (1, s.last_studied_at)

            longest_idle = min(subjects, key=idle_key).subject_name

        today_count = sum(
            1
            for s in subjects
            if s.last_studied_at is not None and s.last_studied_at.astimezone(UTC).date() == today
        )
        return DashboardSubjectsSummary(
            most_studied_subject=most_studied,
            weakest_subject=weakest,
            longest_idle_subject=longest_idle,
            today_studied_count=today_count,
            primary_exam_type=primary_exam_type,
            subject_count=len(subjects),
        )

    async def create_exam_target(
        self, user_id: uuid.UUID, data: ExamTargetCreate
    ) -> ExamTargetRead:
        await self.ensure_student(user_id)
        existing = await self.repo.get_exam_target_by_type(user_id, str(data.exam_type))
        if existing:
            raise ValidationError("Bu sınav hedefi zaten kayıtlı")
        if data.is_primary:
            await self.repo.clear_primary(user_id)
        row = await self.repo.add_exam_target(
            ExamTarget(
                user_id=user_id,
                exam_type=str(data.exam_type),
                is_primary=data.is_primary,
                weight=data.weight,
                target_net=data.target_net,
                target_score=data.target_score,
                target_rank=data.target_rank,
                target_university=data.target_university,
                target_department=data.target_department,
                branch=data.branch,
                exam_date=data.exam_date,
            )
        )
        # Primary yoksa ilk hedefi primary yap
        targets = await self.repo.list_exam_targets(user_id)
        if targets and not any(t.is_primary for t in targets):
            targets[0].is_primary = True
        await self._seed_subjects_for_exams(user_id, targets)
        await self.refresh_journey_stage(user_id)
        return ExamTargetRead.model_validate(row)

    async def update_exam_target(
        self, user_id: uuid.UUID, target_id: uuid.UUID, data: ExamTargetUpdate
    ) -> ExamTargetRead:
        row = await self.repo.get_exam_target(user_id, target_id)
        if not row:
            raise NotFoundError("Sınav hedefi", str(target_id))
        payload = data.model_dump(exclude_unset=True)
        if payload.get("is_primary") is True:
            await self.repo.clear_primary(user_id)
        for key, value in payload.items():
            setattr(row, key, value)
        await self.db.flush()
        targets = await self.repo.list_exam_targets(user_id)
        await self._seed_subjects_for_exams(user_id, targets)
        await self.refresh_journey_stage(user_id)
        return ExamTargetRead.model_validate(row)

    async def delete_exam_target(self, user_id: uuid.UUID, target_id: uuid.UUID) -> None:
        row = await self.repo.get_exam_target(user_id, target_id)
        if not row:
            raise NotFoundError("Sınav hedefi", str(target_id))
        await self.repo.delete_exam_target(row)
        targets = await self.repo.list_exam_targets(user_id)
        if targets and not any(t.is_primary for t in targets):
            targets[0].is_primary = True
        await self.refresh_journey_stage(user_id)

    async def refresh_journey_stage(self, user_id: uuid.UUID) -> JourneyStage:
        student = await self.ensure_student(user_id)
        overview = await StatisticsService(self.db).get_overview(user_id)
        targets = await self.repo.list_exam_targets(user_id)
        exam_count = await self.db.scalar(
            select(func.count()).select_from(Exam).where(Exam.user_id == user_id)
        )
        question_count = await self.db.scalar(
            select(func.count()).select_from(QuestionRecord).where(QuestionRecord.user_id == user_id)
        )
        completed = student.onboarding_completed_at is not None
        skipped = student.onboarding_skipped_at is not None
        stage = evaluate_journey_stage(
            onboarding_completed=completed,
            onboarding_skipped=skipped,
            has_exam_targets=len(targets) > 0,
            streak_days=overview.streak_days,
            total_study_minutes=overview.total_study_minutes,
            exam_count=int(exam_count or 0),
            question_count=int(question_count or 0),
        )
        student.journey_stage = stage
        await self.db.flush()
        return stage

    async def journey_progress(self, user_id: uuid.UUID) -> JourneyProgressSummary:
        """K1 — additive dashboard progress."""
        student = await self.ensure_student(user_id)
        await self.refresh_journey_stage(user_id)
        student = await self.repo.get_student(user_id) or student
        overview = await StatisticsService(self.db).get_overview(user_id)
        completed, skipped, required = self._onboarding_flags(student)

        daily_goal = student.daily_study_minutes or DEFAULT_DAILY_STUDY_GOAL_MINUTES
        from app.services.goal_progress_service import calc_progress

        today_pct = calc_progress(float(overview.today_study_minutes), float(daily_goal))
        week_goal = daily_goal * max(1, len(student.available_days or [0, 1, 2, 3, 4]))
        week_pct = calc_progress(float(overview.week_study_minutes), float(week_goal))
        # Ay: haftalık hedefin ~4 katı (basit)
        month_goal = week_goal * 4
        month_pct = calc_progress(float(overview.total_study_minutes), float(max(month_goal, 1)))

        targets = await self.repo.list_exam_targets(user_id)
        primary = next((t for t in targets if t.is_primary), targets[0] if targets else None)
        active_type = self.resolve_active_exam_type(student, targets)
        active = (
            next((t for t in targets if str(t.exam_type) == active_type), None)
            if active_type
            else None
        )
        focus = active or primary
        overall = 0.0
        days_remaining = None
        if focus and focus.target_net and focus.target_net > 0:
            # overall: onboarding + baseline known + some activity
            overall = 25.0 if completed or skipped else 0.0
            if student.baseline_level != BaselineLevel.UNKNOWN:
                overall += 15.0
            if overview.total_study_minutes > 0:
                overall += min(40.0, overview.total_study_minutes / 50.0)
            if overview.streak_days > 0:
                overall += min(20.0, overview.streak_days * 2.0)
            overall = min(100.0, overall)
        elif completed or skipped:
            overall = min(100.0, 20.0 + min(50.0, overview.total_study_minutes / 40.0))

        days_remaining = None
        exam_date_out = None
        if focus and focus.exam_date:
            exam_date_out = focus.exam_date
            days_remaining = (focus.exam_date - date.today()).days
        elif focus:
            from app.services.exam_calendar import next_exam_date

            exam_date_out = next_exam_date(
                str(focus.exam_type) if focus.exam_type else None
            )
            days_remaining = (exam_date_out - date.today()).days

        assessment_pct = 0.0
        assessment_msg = None
        try:
            from app.services.assessment_service import AssessmentService

            ov = await AssessmentService(self.db).overview(user_id)
            assessment_pct = ov.progress_pct
            assessment_msg = ov.message
        except Exception:
            pass

        return JourneyProgressSummary(
            today_pct=round(today_pct, 1),
            week_pct=round(week_pct, 1),
            month_pct=round(month_pct, 1),
            overall_pct=round(overall, 1),
            journey_stage=JourneyStage(student.journey_stage),
            onboarding_required=required,
            primary_exam_type=primary.exam_type if primary else None,
            days_remaining=days_remaining,
            exam_date=exam_date_out,
            baseline_level=BaselineLevel(student.baseline_level),
            assessment_progress_pct=assessment_pct,
            assessment_message=assessment_msg,
        )

    async def context_payload(self, user_id: uuid.UUID) -> dict:
        profile = await self.get_profile(user_id)
        stage_reason = build_stage_reason(profile.journey_stage)
        return {
            "journey_stage": profile.journey_stage,
            "journey_stage_reason": stage_reason,
            "onboarding_required": profile.onboarding_required,
            "onboarding_completed": profile.onboarding_completed,
            "onboarding_skipped": profile.onboarding_skipped,
            "daily_study_minutes": profile.daily_study_minutes,
            "available_days": profile.available_days,
            "available_hours": profile.available_hours,
            "baseline_level": profile.baseline_level,
            "baseline_reason": profile.baseline_reason,
            "exam_targets": [
                {
                    "exam_type": str(t.exam_type),
                    "is_primary": t.is_primary,
                    "target_net": t.target_net,
                    "target_score": t.target_score,
                    "target_rank": t.target_rank,
                    "target_university": t.target_university,
                    "target_department": t.target_department,
                    "branch": t.branch,
                    "exam_date": t.exam_date.isoformat() if t.exam_date else None,
                    "weight": t.weight,
                }
                for t in profile.exam_targets
            ],
            "subjects": [
                {"code": s.subject_code, "name": s.subject_name, "active": s.is_active}
                for s in profile.subjects
            ],
        }

    async def planner_defaults(self, user_id: uuid.UUID) -> dict | None:
        """F1 — planner generate için profile default.

        Planner her zaman PRIMARY exam hedefini kullanır.
        active_exam_type yalnızca dashboard görünümü içindir; çalışma planı
        birincil sınav üzerinden oluşturulmalıdır.
        """
        student = await self.repo.get_student(user_id)
        if not student:
            return None
        targets = await self.repo.list_exam_targets(user_id)
        if not targets:
            return None
        # Primary exam target öncelikli; yoksa ilk hedef kullanılır.
        focus = next((t for t in targets if t.is_primary), targets[0])
        days = list(student.available_days or [])
        if not days:
            days = [0, 1, 2, 3, 4]
        net = focus.target_net or 80.0
        return {
            "target_exam": focus.exam_type,
            "target_net": float(net),
            "available_days": days,
            "available_hours": float(student.available_hours or 2.0),
        }

