"""
StudyOS — Revision Service
Sprint-2.8 — CRUD + SM-2 review + generate (rules) + explain (LLM)
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    REVISION_DEFAULT_DIFFICULTY,
    REVISION_DEFAULT_EASE,
    REVISION_GENERATE_MAX_ITEMS,
    REVISION_HEATMAP_DAYS,
    REVISION_QUESTION_WEAK_RATE,
    AI_CONTEXT_REVISIONS,
)
from app.core.exceptions import NotFoundError, ValidationError
from app.models.activity import ActivityEventType
from app.models.revision import (
    RevisionGrade,
    RevisionItem,
    RevisionItemStatus,
    RevisionReview,
    RevisionSchedule,
    RevisionSourceType,
)
from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.repositories.revision_repository import RevisionRepository
from app.schemas.revision import (
    DashboardRevisionSummary,
    RevisionCreate,
    RevisionExplainResponse,
    RevisionGenerateRequest,
    RevisionGenerateResponse,
    RevisionHeatmapDay,
    RevisionHeatmapResponse,
    RevisionItemRead,
    RevisionPostponeRequest,
    RevisionReviewRequest,
    RevisionScheduleRead,
    RevisionSkipRequest,
    RevisionStatisticsResponse,
    RevisionUpdate,
)
from app.services.activity_service import ActivityService
from app.services.ai.revision_engine import apply_sm2_lite, initial_reason_for_subject
from app.services.exam_service import ExamService
from app.services.notification_settings_service import NotificationSettingsService
from app.services.question_record_service import QuestionRecordService


def _day_start(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time(), tzinfo=UTC)


def _week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


class RevisionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RevisionRepository(db)
        self.activity = ActivityService(db)
        self.questions = QuestionRecordService(db)
        self.exams = ExamService(db)
        self.notif = NotificationSettingsService(db)

    async def _active_subjects(self, user_id: uuid.UUID) -> set[str] | None:
        """M17.3 — Active Exam subject names; None/empty = no exam scope."""
        from app.services.learning_profile_service import LearningProfileService

        _, _, names = await LearningProfileService(self.db).resolve_active_scope(
            user_id
        )
        return names or None

    def _to_read(self, item: RevisionItem) -> RevisionItemRead:
        schedule = None
        if item.schedule is not None:
            schedule = RevisionScheduleRead.model_validate(item.schedule)
        return RevisionItemRead(
            id=item.id,
            title=item.title,
            subject=item.subject,
            topic=item.topic,
            note=item.note,
            source_type=RevisionSourceType(item.source_type),
            source_id=item.source_id,
            difficulty=item.difficulty,
            reason=item.reason,
            status=RevisionItemStatus(item.status),
            schedule=schedule,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    async def _ensure(self, item_id: uuid.UUID, user_id: uuid.UUID) -> RevisionItem:
        item = await self.repo.get_for_user(item_id, user_id)
        if item is None:
            raise NotFoundError("Tekrar kartı", str(item_id))
        return item

    async def create(self, user_id: uuid.UUID, data: RevisionCreate) -> RevisionItemRead:
        reason = (data.reason or "").strip() or initial_reason_for_subject(
            data.subject, source=str(data.source_type)
        )
        now = datetime.now(UTC)
        item = RevisionItem(
            user_id=user_id,
            title=data.title.strip(),
            subject=data.subject.strip(),
            topic=data.topic.strip() if data.topic else None,
            note=data.note,
            source_type=data.source_type,
            source_id=data.source_id,
            difficulty=data.difficulty,
            reason=reason[:500],
            status=RevisionItemStatus.ACTIVE,
            metadata_={},
        )
        item.schedule = RevisionSchedule(
            due_at=now,
            interval_days=1,
            ease_factor=REVISION_DEFAULT_EASE,
            repetition_count=0,
            lapse_count=0,
        )
        item = await self.repo.add(item)
        await self.db.refresh(item, attribute_names=["schedule"])
        await self.activity.record(
            user_id=user_id,
            event_type=ActivityEventType.REVISION_CREATED,
            title=f"Tekrar eklendi: {item.subject}",
            description=item.reason,
            metadata={
                "revision_id": str(item.id),
                "source_type": str(item.source_type),
                "difficulty": item.difficulty,
            },
        )
        # ── LOS Module 1: Consistency evidence ────────────────────
        try:
            from app.services.evidence_service import EvidenceService
            await EvidenceService(self.db).ingest_revision_item_created(item)
        except Exception:
            pass

        return self._to_read(item)

    async def list_items(
        self,
        user_id: uuid.UUID,
        *,
        status: RevisionItemStatus | None = None,
        subject: str | None = None,
        source_type: RevisionSourceType | None = None,
    ) -> list[RevisionItemRead]:
        items = await self.repo.list_for_user(
            user_id, status=status, subject=subject, source_type=source_type
        )
        names = await self._active_subjects(user_id)
        if names and subject is None:
            items = [
                i for i in items if (i.subject or "").strip().lower() in names
            ]
        return [self._to_read(i) for i in items]

    async def get(self, item_id: uuid.UUID, user_id: uuid.UUID) -> RevisionItemRead:
        return self._to_read(await self._ensure(item_id, user_id))

    async def update(
        self, item_id: uuid.UUID, user_id: uuid.UUID, data: RevisionUpdate
    ) -> RevisionItemRead:
        item = await self._ensure(item_id, user_id)
        payload = data.model_dump(exclude_unset=True)
        for key, value in payload.items():
            if key == "title" and value is not None:
                setattr(item, key, value.strip())
            elif key == "subject" and value is not None:
                setattr(item, key, value.strip())
            elif key == "topic":
                setattr(item, key, value.strip() if value else None)
            else:
                setattr(item, key, value)
        item.updated_at = datetime.now(UTC)
        await self.db.flush()
        return self._to_read(item)

    async def soft_delete(self, item_id: uuid.UUID, user_id: uuid.UUID) -> None:
        item = await self._ensure(item_id, user_id)
        item.deleted_at = datetime.now(UTC)
        item.status = RevisionItemStatus.ARCHIVED
        item.updated_at = datetime.now(UTC)
        await self.db.flush()

    async def review(
        self, item_id: uuid.UUID, user_id: uuid.UUID, data: RevisionReviewRequest
    ) -> RevisionItemRead:
        item = await self._ensure(item_id, user_id)
        if item.status != RevisionItemStatus.ACTIVE:
            raise ValidationError("Yalnızca aktif kartlar tekrarlanabilir")
        if item.schedule is None:
            raise ValidationError("Kartın zamanlaması yok")

        sched = item.schedule
        prev_interval = sched.interval_days
        prev_ease = sched.ease_factor
        prev_diff = item.difficulty

        result = apply_sm2_lite(
            grade=data.grade,
            interval_days=sched.interval_days,
            ease_factor=sched.ease_factor,
            repetition_count=sched.repetition_count,
            lapse_count=sched.lapse_count,
            difficulty=item.difficulty,
        )

        now = datetime.now(UTC)
        review = RevisionReview(
            revision_item_id=item.id,
            grade=data.grade,
            previous_interval_days=prev_interval,
            new_interval_days=result.interval_days,
            previous_difficulty=prev_diff,
            new_difficulty=result.difficulty,
            previous_ease=prev_ease,
            new_ease=result.ease_factor,
            duration_seconds=data.duration_seconds,
            reviewed_at=now,
        )
        self.db.add(review)

        # Sprint 7 — LOS Confidence bias + forgetting
        adjusted_interval = result.interval_days
        try:
            from app.models.topic_confidence import TopicConfidence
            from sqlalchemy import select as _sel

            topic_key = getattr(item, "topic_code", None) or (item.topic or "")
            subject_key = getattr(item, "subject_code", None) or (item.subject or "")
            conf_row = None
            if topic_key:
                conf_row = await self.db.scalar(
                    _sel(TopicConfidence).where(
                        TopicConfidence.user_id == item.user_id,
                        TopicConfidence.topic_code == topic_key,
                    ).limit(1)
                )
            if conf_row is None and subject_key and topic_key:
                conf_row = await self.db.scalar(
                    _sel(TopicConfidence).where(
                        TopicConfidence.user_id == item.user_id,
                        TopicConfidence.subject_code == subject_key,
                        TopicConfidence.topic_code == topic_key,
                    ).limit(1)
                )
            if conf_row is not None:
                belief = float(conf_row.belief or 0.5)
                # Forgotten: yüksek inanç + uzun süredir due → agresif kısalt
                overdue_days = max(0, (now - sched.due_at).days) if sched.due_at else 0
                forgotten = belief >= 0.6 and overdue_days >= 14
                if forgotten or belief < 0.3:
                    adjusted_interval = max(1, round(result.interval_days * 0.5))
                elif belief > 0.7:
                    adjusted_interval = round(result.interval_days * 1.5)
        except Exception:
            pass

        sched.interval_days = adjusted_interval
        sched.ease_factor = result.ease_factor
        sched.repetition_count = result.repetition_count
        sched.lapse_count = result.lapse_count
        sched.last_reviewed_at = now
        sched.due_at = now + timedelta(days=adjusted_interval)
        sched.updated_at = now

        item.difficulty = result.difficulty
        item.updated_at = now
        # Mastered heuristic: easy + interval >= 21 + reps >= 4
        if (
            data.grade == RevisionGrade.EASY
            and result.interval_days >= 21
            and result.repetition_count >= 4
        ):
            item.status = RevisionItemStatus.MASTERED

        await self.db.flush()
        await self.activity.record(
            user_id=user_id,
            event_type=ActivityEventType.REVISION_REVIEWED,
            title=f"Tekrar: {item.subject}",
            description=f"Not: {data.grade} · sonraki {result.interval_days} gün",
            metadata={
                "revision_id": str(item.id),
                "grade": str(data.grade),
                "new_difficulty": result.difficulty,
                "new_interval_days": result.interval_days,
            },
        )
        if item.status == RevisionItemStatus.MASTERED:
            await self.activity.record(
                user_id=user_id,
                event_type=ActivityEventType.REVISION_COMPLETED,
                title=f"Tekrar tamamlandı: {item.subject}",
                description=item.reason,
                metadata={"revision_id": str(item.id)},
            )
        from app.schemas.achievement import AchievementCheckRequest
        from app.services.achievement_service import AchievementService

        await AchievementService(self.db).check(
            user_id, AchievementCheckRequest(event="revision_reviewed")
        )
        if item.status == RevisionItemStatus.MASTERED:
            await AchievementService(self.db).check(
                user_id, AchievementCheckRequest(event="revision_completed")
            )
        from app.services.goal_progress_service import GoalProgressEvent, GoalProgressService

        await GoalProgressService(self.db).apply_event(
            user_id,
            GoalProgressEvent(
                kind="revision_reviewed",
                amount=1.0,
                subject=item.subject,
                note=f"Tekrar: {data.grade}",
            ),
        )

        # ── LOS Module 1: Evidence ingestion ──────────────────────
        try:
            from app.services.evidence_service import EvidenceService
            _ev_svc = EvidenceService(self.db)
            await _ev_svc.ingest_revision_review(review, item)
        except Exception:
            pass

        return self._to_read(item)

    async def skip(
        self, item_id: uuid.UUID, user_id: uuid.UUID, data: RevisionSkipRequest
    ) -> RevisionItemRead:
        item = await self._ensure(item_id, user_id)
        if item.schedule is None:
            raise ValidationError("Kartın zamanlaması yok")
        item.schedule.due_at = item.schedule.due_at + timedelta(days=data.days)
        item.schedule.updated_at = datetime.now(UTC)
        item.updated_at = datetime.now(UTC)
        await self.db.flush()
        return self._to_read(item)

    async def postpone(
        self, item_id: uuid.UUID, user_id: uuid.UUID, data: RevisionPostponeRequest
    ) -> RevisionItemRead:
        item = await self._ensure(item_id, user_id)
        if item.schedule is None:
            raise ValidationError("Kartın zamanlaması yok")
        now = datetime.now(UTC)
        item.schedule.due_at = now + timedelta(days=data.days)
        item.schedule.updated_at = now
        item.updated_at = now
        await self.db.flush()
        return self._to_read(item)

    async def today(self, user_id: uuid.UUID) -> list[RevisionItemRead]:
        today = datetime.now(UTC).date()
        start = _day_start(today)
        end = start + timedelta(days=1)
        names = await self._active_subjects(user_id)
        items = await self.repo.list_due(user_id, until=end, subjects=names)
        seen: set[uuid.UUID] = set()
        out: list[RevisionItem] = []
        for it in items:
            if it.id not in seen:
                seen.add(it.id)
                out.append(it)
        return [self._to_read(i) for i in out]

    async def week(self, user_id: uuid.UUID) -> list[RevisionItemRead]:
        today = datetime.now(UTC).date()
        monday = _week_monday(today)
        end = _day_start(monday + timedelta(days=7))
        names = await self._active_subjects(user_id)
        items = await self.repo.list_due(user_id, until=end, subjects=names)
        return [self._to_read(i) for i in items]

    async def overdue(self, user_id: uuid.UUID) -> list[RevisionItemRead]:
        today = datetime.now(UTC).date()
        names = await self._active_subjects(user_id)
        items = await self.repo.list_due(
            user_id,
            until=_day_start(today),
            overdue_only=True,
            subjects=names,
        )
        return [self._to_read(i) for i in items]

    async def _create_seed(
        self,
        user_id: uuid.UUID,
        *,
        subject: str,
        source_type: RevisionSourceType,
        reason: str,
        source_id: uuid.UUID | None = None,
        topic: str | None = None,
        difficulty: int = REVISION_DEFAULT_DIFFICULTY,
    ) -> RevisionItem | None:
        existing = await self.repo.find_seed_duplicate(
            user_id,
            source_type=source_type,
            subject=subject,
            source_id=source_id,
            topic=topic,
        )
        if existing is not None:
            return None
        now = datetime.now(UTC)
        item = RevisionItem(
            user_id=user_id,
            title=f"{subject} tekrarı",
            subject=subject,
            topic=topic,
            source_type=source_type,
            source_id=source_id,
            difficulty=difficulty,
            reason=reason[:500],
            status=RevisionItemStatus.ACTIVE,
            metadata_={},
        )
        item.schedule = RevisionSchedule(
            due_at=now,
            interval_days=1,
            ease_factor=REVISION_DEFAULT_EASE,
            repetition_count=0,
            lapse_count=0,
        )
        return await self.repo.add(item)

    async def generate(
        self, user_id: uuid.UUID, data: RevisionGenerateRequest
    ) -> RevisionGenerateResponse:
        created: list[RevisionItem] = []
        skipped = 0
        limit = min(data.max_items, REVISION_GENERATE_MAX_ITEMS)

        if data.include_questions:
            dist = await self.questions.get_subjects_distribution(user_id)
            for row in dist.items:
                if len(created) >= limit:
                    break
                if row.correct_rate >= REVISION_QUESTION_WEAK_RATE:
                    continue
                reason = initial_reason_for_subject(
                    row.name, source="question_tracking", accuracy=row.correct_rate
                )
                # higher difficulty when accuracy lower
                diff = 5 if row.correct_rate < 35 else (4 if row.correct_rate < 45 else 3)
                item = await self._create_seed(
                    user_id,
                    subject=row.name,
                    source_type=RevisionSourceType.QUESTION_TRACKING,
                    reason=reason,
                    difficulty=diff,
                )
                if item is None:
                    skipped += 1
                else:
                    created.append(item)
                    await self.activity.record(
                        user_id=user_id,
                        event_type=ActivityEventType.REVISION_CREATED,
                        title=f"Tekrar eklendi: {item.subject}",
                        description=item.reason,
                        metadata={
                            "revision_id": str(item.id),
                            "source_type": str(item.source_type),
                        },
                    )

        if data.include_exams and len(created) < limit:
            from app.core.constants import REVISION_EXAM_MIN_QUESTIONS
            from app.services.subject_net_targets import (
                compute_subject_target_net,
                resolve_user_target_net,
            )

            trends = await self.exams.get_trends(user_id)
            user_target = await resolve_user_target_net(self.db, user_id)
            total_q = sum(
                r.question_count
                for r in trends.by_subject
                if r.question_count >= REVISION_EXAM_MIN_QUESTIONS
            )
            for row in trends.by_subject:
                if len(created) >= limit:
                    break
                if row.question_count < REVISION_EXAM_MIN_QUESTIONS:
                    continue
                target = compute_subject_target_net(
                    user_target_net=user_target,
                    subject_question_count=row.question_count,
                    total_question_count=total_q,
                )
                if row.average_net >= target:
                    continue
                reason = initial_reason_for_subject(
                    row.subject,
                    source="exam",
                    net=row.average_net,
                    target_net=target,
                )
                gap = target - float(row.average_net)
                diff = 5 if gap >= max(target * 0.5, 1) else 4
                item = await self._create_seed(
                    user_id,
                    subject=row.subject,
                    source_type=RevisionSourceType.EXAM,
                    reason=reason,
                    difficulty=diff,
                )
                if item is None:
                    skipped += 1
                else:
                    created.append(item)
                    await self.activity.record(
                        user_id=user_id,
                        event_type=ActivityEventType.REVISION_CREATED,
                        title=f"Tekrar eklendi: {item.subject}",
                        description=item.reason,
                        metadata={
                            "revision_id": str(item.id),
                            "source_type": str(item.source_type),
                        },
                    )

        for item in created:
            await self.db.refresh(item, attribute_names=["schedule"])

        return RevisionGenerateResponse(
            created=[self._to_read(i) for i in created],
            skipped_existing=skipped,
            message=f"{len(created)} kart oluşturuldu, {skipped} mevcut atlandı",
        )

    async def explain(
        self, item_id: uuid.UUID, user_id: uuid.UUID
    ) -> RevisionExplainResponse:
        item = await self._ensure(item_id, user_id)
        system = (
            "Sen StudyOS çalışma koçusun. Tekrar kartını sen üretmedin; kural motoru üretti. "
            "Sana verilen reason ve difficulty değerlerini doğal Türkçe ile açıkla. "
            "Yeni interval veya difficulty önerme; sayıları uydurma."
        )
        user_msg = (
            f"Ders: {item.subject}\n"
            f"Konu: {item.topic or '-'}\n"
            f"Kaynak: {item.source_type}\n"
            f"Zorluk (1-5): {item.difficulty}\n"
            f"Gerekçe: {item.reason}\n"
            f"Interval: {item.schedule.interval_days if item.schedule else '-'} gün\n"
            "Öğrenciye neden bu tekrarın önerildiğini 2–3 kısa paragrafta anlat."
        )
        pref = await self.notif.get_or_create(user_id)
        result = await generate_with_fallback(
            GenerateRequest(
                messages=[
                    ChatMessageDTO(role="system", content=system),
                    ChatMessageDTO(role="user", content=user_msg),
                ],
                context={"revision_id": str(item.id)},
            ),
            preferred=pref.ai_preferred_provider,
            model=pref.ai_preferred_model,
        )
        return RevisionExplainResponse(
            revision_id=item.id,
            explanation=result.text,
            provider=result.provider,
            used_fallback=result.used_fallback,
            reason=item.reason,
            difficulty=item.difficulty,
        )

    async def statistics(self, user_id: uuid.UUID) -> RevisionStatisticsResponse:
        today = datetime.now(UTC).date()
        start_today = _day_start(today)
        end_today = start_today + timedelta(days=1)
        monday = _week_monday(today)
        week_start = _day_start(monday)
        week_end = week_start + timedelta(days=7)

        return RevisionStatisticsResponse(
            total_active=await self.repo.count_active(user_id),
            total_mastered=await self.repo.count_mastered(user_id),
            due_today=await self.repo.count_due_between(user_id, start_today, end_today)
            + await self.repo.count_overdue(user_id, start_today),
            overdue=await self.repo.count_overdue(user_id, start_today),
            due_this_week=await self.repo.count_due_between(user_id, week_start, week_end)
            + await self.repo.count_overdue(user_id, week_start),
            reviewed_today=await self.repo.count_reviews_between(
                user_id, start_today, end_today
            ),
            reviewed_this_week=await self.repo.count_reviews_between(
                user_id, week_start, week_end
            ),
            average_difficulty=round(await self.repo.average_difficulty(user_id), 2),
            average_ease=round(await self.repo.average_ease(user_id), 2),
        )

    async def heatmap(self, user_id: uuid.UUID) -> RevisionHeatmapResponse:
        end = datetime.now(UTC).date()
        start = end - timedelta(days=REVISION_HEATMAP_DAYS - 1)
        counts = await self.repo.heatmap_counts(user_id, start, end)
        days: list[RevisionHeatmapDay] = []
        cursor = start
        while cursor <= end:
            days.append(RevisionHeatmapDay(day=cursor, review_count=counts.get(cursor, 0)))
            cursor += timedelta(days=1)
        return RevisionHeatmapResponse(days=days, start_date=start, end_date=end)

    async def dashboard_summary(self, user_id: uuid.UUID) -> DashboardRevisionSummary:
        today = datetime.now(UTC).date()
        start_today = _day_start(today)
        end_today = start_today + timedelta(days=1)
        monday = _week_monday(today)
        week_end = _day_start(monday + timedelta(days=7))
        names = await self._active_subjects(user_id)

        overdue = await self.repo.count_overdue(
            user_id, start_today, subjects=names
        )
        due_today = (
            await self.repo.count_due_between(
                user_id, start_today, end_today, subjects=names
            )
            + overdue
        )
        due_week = (
            await self.repo.count_due_between(
                user_id, _day_start(monday), week_end, subjects=names
            )
            + overdue
        )

        nxt = await self.repo.next_due_item(user_id, subjects=names)
        overdue_days: int | None = None
        if nxt and nxt.schedule and nxt.schedule.due_at:
            due_at = nxt.schedule.due_at
            if due_at.tzinfo is None:
                due_at = due_at.replace(tzinfo=UTC)
            delta = (datetime.now(UTC) - due_at).days
            if delta > 0:
                overdue_days = delta
        elif overdue > 0:
            # Sıradaki öğe yoksa ama gecikmiş sayaç > 0 — en az 1 gün işaretle
            overdue_days = 1

        return DashboardRevisionSummary(
            due_today=due_today,
            overdue=overdue,
            due_this_week=due_week,
            next_due_at=nxt.schedule.due_at if nxt and nxt.schedule else None,
            next_title=nxt.title if nxt else None,
            overview_reason=nxt.reason if nxt else None,
            overdue_days=overdue_days,
        )

    async def context_payload(self, user_id: uuid.UUID) -> dict:
        today_items = await self.today(user_id)
        summary = await self.dashboard_summary(user_id)
        return {
            "due_today": summary.due_today,
            "overdue": summary.overdue,
            "items": [
                {
                    "id": str(i.id),
                    "subject": i.subject,
                    "difficulty": i.difficulty,
                    "reason": i.reason,
                    "source_type": str(i.source_type),
                    "due_at": i.schedule.due_at.isoformat() if i.schedule else None,
                }
                for i in today_items[:AI_CONTEXT_REVISIONS]
            ],
        }
