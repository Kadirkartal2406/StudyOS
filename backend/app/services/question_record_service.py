"""
StudyOS — QuestionRecord Service
Soru takip CRUD + istatistik aggregate. Sprint-1.9 (Meeting-017).
Net formülü: YKS emsali correct - wrong/4 (constants).
"""

import math
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    QUESTION_NET_WRONG_PENALTY,
    QUESTION_RECORD_DEFAULT_PAGE_SIZE,
    QUESTION_RECORD_MAX_PAGE_SIZE,
    STATISTICS_DISTRIBUTION_LIMIT,
)
from app.core.exceptions import NotFoundError, ValidationError
from app.models.question_record import ExamType, QuestionRecord, QuestionSource
from app.repositories.question_record_repository import QuestionRecordRepository
from app.repositories.study_plan_repository import StudyPlanRepository
from app.repositories.study_session_repository import StudySessionRepository
from app.schemas.question_record import (
    QuestionDailyBucket,
    QuestionDailyResponse,
    QuestionDistributionItem,
    QuestionDistributionResponse,
    QuestionRecordCreate,
    QuestionRecordUpdate,
    QuestionStatisticsOverview,
)


def _day_bounds(d: date) -> tuple[datetime, datetime]:
    start = datetime.combine(d, datetime.min.time(), tzinfo=UTC)
    return start, start + timedelta(days=1)


def _week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def compute_net_score(correct: int, wrong: int) -> Decimal:
    """YKS tarzı net: doğru − yanlış × ceza. Diğer exam_type şimdilik aynı."""
    raw = Decimal(correct) - (Decimal(wrong) * Decimal(str(QUESTION_NET_WRONG_PENALTY)))
    return raw.quantize(Decimal("0.01"))


class QuestionRecordService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = QuestionRecordRepository(db)
        self.plan_repo = StudyPlanRepository(db)
        self.session_repo = StudySessionRepository(db)

    async def create(self, user_id: uuid.UUID, data: QuestionRecordCreate) -> QuestionRecord:
        await self._validate_links(user_id, data.study_plan_id, data.study_session_id)
        record = QuestionRecord(
            user_id=user_id,
            study_plan_id=data.study_plan_id,
            study_session_id=data.study_session_id,
            subject=data.subject.strip(),
            topic=data.topic.strip() if data.topic else None,
            subject_code=data.subject_code,
            topic_code=data.topic_code,
            question_count=data.question_count,
            correct_count=data.correct_count,
            wrong_count=data.wrong_count,
            blank_count=data.blank_count,
            duration_minutes=data.duration_minutes,
            difficulty=data.difficulty,
            source=data.source,
            exam_type=data.exam_type,
            note=data.note,
            net_score=compute_net_score(data.correct_count, data.wrong_count),
        )
        await self.repo.add(record)
        from app.services.goal_progress_service import GoalProgressEvent, GoalProgressService

        await GoalProgressService(self.db).apply_event(
            user_id,
            GoalProgressEvent(
                kind="question_recorded",
                amount=float(record.question_count),
                subject=record.subject,
                topic=record.topic,
                occurred_on=record.created_at.date()
                if hasattr(record.created_at, "date")
                else None,
            ),
        )

        # ── LOS Module 1: Evidence ingestion ──────────────────────
        try:
            from app.services.evidence_service import EvidenceService
            await EvidenceService(self.db).ingest_question_record(record)
        except Exception:
            pass

        # EAE Sprint 6+1 — Sub-node evidence bridge: if this question record has
        # EAE node metadata, propagate to Confidence Engine via EAEEvidenceBridge.
        try:
            meta = {}
            if hasattr(record, "metadata_") and isinstance(record.metadata_, dict):
                meta = record.metadata_
            eae_node_id = meta.get("eae_node_id") or meta.get("selected_node_id")
            expected_node_id = meta.get("expected_node_id") or meta.get("correct_node_id")
            selected_node_id = meta.get("selected_node_id") or eae_node_id
            if eae_node_id and record.subject_code and record.topic_code:
                from app.services.eae_evidence_bridge import EAEEvidenceBridge

                bridge = EAEEvidenceBridge(self.db)
                if expected_node_id and selected_node_id:
                    confusable = meta.get("confusable_with")
                    await bridge.ingest_node_selection(
                        user_id=user_id,
                        subject_code=record.subject_code,
                        topic_code=record.topic_code,
                        expected_node_id=str(expected_node_id),
                        selected_node_id=str(selected_node_id),
                        confusable_with=list(confusable)
                        if isinstance(confusable, list)
                        else None,
                    )
                else:
                    is_correct = (record.correct_count or 0) > (record.wrong_count or 0)
                    await bridge.ingest_sub_node_evidence(
                        user_id=user_id,
                        subject_code=record.subject_code,
                        topic_code=record.topic_code,
                        node_id=str(eae_node_id),
                        is_correct=is_correct,
                    )
        except Exception:
            pass

        return record


    async def get(self, record_id: uuid.UUID, user_id: uuid.UUID) -> QuestionRecord:
        record = await self.repo.get_by_id_for_user(record_id, user_id)
        if record is None:
            raise NotFoundError("Soru kaydı", str(record_id))
        return record

    async def list_records(
        self,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = QUESTION_RECORD_DEFAULT_PAGE_SIZE,
        date_from: date | None = None,
        date_to: date | None = None,
        subject: str | None = None,
        topic: str | None = None,
        exam_type: ExamType | None = None,
        source: QuestionSource | None = None,
        study_plan_id: uuid.UUID | None = None,
        study_session_id: uuid.UUID | None = None,
    ) -> tuple[list[QuestionRecord], int]:
        page = max(1, page)
        page_size = min(max(1, page_size), QUESTION_RECORD_MAX_PAGE_SIZE)
        return await self.repo.list_filtered(
            user_id,
            page=page,
            page_size=page_size,
            date_from=date_from,
            date_to=date_to,
            subject=subject,
            topic=topic,
            exam_type=exam_type,
            source=source,
            study_plan_id=study_plan_id,
            study_session_id=study_session_id,
        )

    async def update(
        self, record_id: uuid.UUID, user_id: uuid.UUID, data: QuestionRecordUpdate
    ) -> QuestionRecord:
        record = await self.get(record_id, user_id)
        payload = data.model_dump(exclude_unset=True)

        if "study_plan_id" in payload or "study_session_id" in payload:
            await self._validate_links(
                user_id,
                payload.get("study_plan_id", record.study_plan_id),
                payload.get("study_session_id", record.study_session_id),
            )

        for field, value in payload.items():
            if field in ("subject",) and isinstance(value, str):
                value = value.strip()
            if field == "topic" and isinstance(value, str):
                value = value.strip() or None
            setattr(record, field, value)

        q = record.question_count
        c, w, b = record.correct_count, record.wrong_count, record.blank_count
        if c + w + b != q:
            raise ValidationError(
                "correct_count + wrong_count + blank_count, question_count ile eşit olmalıdır"
            )
        record.net_score = compute_net_score(c, w)
        await self.db.flush()
        return record

    async def delete(self, record_id: uuid.UUID, user_id: uuid.UUID) -> None:
        record = await self.get(record_id, user_id)
        await self.repo.delete(record)

    async def get_statistics_overview(self, user_id: uuid.UUID) -> QuestionStatisticsOverview:
        today = datetime.now(UTC).date()
        week_start = _week_monday(today)
        month_start = today.replace(day=1)
        today_from, today_to = _day_bounds(today)
        week_from = datetime.combine(week_start, datetime.min.time(), tzinfo=UTC)
        month_from = datetime.combine(month_start, datetime.min.time(), tzinfo=UTC)
        now_to = datetime.now(UTC) + timedelta(days=1)

        total_q, total_c, total_w, total_b, total_net, total_dur, rec_count = (
            await self.repo.aggregate_between(user_id)
        )
        today_q, *_ = await self.repo.aggregate_between(
            user_id, created_from=today_from, created_to=today_to
        )
        week_q, *_ = await self.repo.aggregate_between(
            user_id, created_from=week_from, created_to=now_to
        )
        month_q, *_ = await self.repo.aggregate_between(
            user_id, created_from=month_from, created_to=now_to
        )

        correct_rate = round((total_c / total_q) * 100, 1) if total_q else 0.0
        wrong_rate = round((total_w / total_q) * 100, 1) if total_q else 0.0

        return QuestionStatisticsOverview(
            total_questions=total_q,
            today_questions=today_q,
            week_questions=week_q,
            month_questions=month_q,
            total_correct=total_c,
            total_wrong=total_w,
            total_blank=total_b,
            correct_rate=correct_rate,
            wrong_rate=wrong_rate,
            total_net=round(total_net, 2),
            total_duration_minutes=total_dur,
            record_count=rec_count,
        )

    async def get_daily(
        self, user_id: uuid.UUID, *, days: int = 14
    ) -> QuestionDailyResponse:
        days = min(max(1, days), 90)
        today = datetime.now(UTC).date()
        start = today - timedelta(days=days - 1)
        created_from, _ = _day_bounds(start)
        _, created_to = _day_bounds(today)
        rows = await self.repo.daily_buckets(user_id, created_from, created_to)
        buckets = [
            QuestionDailyBucket(
                date=str(row[0]),
                question_count=int(row[1]),
                correct_count=int(row[2]),
                wrong_count=int(row[3]),
                blank_count=int(row[4]),
                net_score=round(float(row[5]), 2),
                duration_minutes=int(row[6]),
            )
            for row in rows
        ]
        return QuestionDailyResponse(
            buckets=buckets,
            total_questions=sum(b.question_count for b in buckets),
        )

    async def get_subjects_distribution(
        self, user_id: uuid.UUID
    ) -> QuestionDistributionResponse:
        rows = await self.repo.group_by_subject(
            user_id, limit=STATISTICS_DISTRIBUTION_LIMIT
        )
        return self._to_distribution(rows)

    async def get_topics_distribution(
        self, user_id: uuid.UUID
    ) -> QuestionDistributionResponse:
        rows = await self.repo.group_by_topic(user_id, limit=STATISTICS_DISTRIBUTION_LIMIT)
        return self._to_distribution(rows)

    async def get_exams_distribution(
        self, user_id: uuid.UUID
    ) -> QuestionDistributionResponse:
        rows = await self.repo.group_by_exam(user_id, limit=STATISTICS_DISTRIBUTION_LIMIT)
        return self._to_distribution(rows)

    async def today_question_count(self, user_id: uuid.UUID) -> int:
        today_from, today_to = _day_bounds(datetime.now(UTC).date())
        q, *_ = await self.repo.aggregate_between(
            user_id, created_from=today_from, created_to=today_to
        )
        return q

    @staticmethod
    def _to_distribution(rows: list[tuple]) -> QuestionDistributionResponse:
        items: list[QuestionDistributionItem] = []
        total = 0
        for row in rows:
            name = str(row[0])
            qc, cc, wc, bc = int(row[1]), int(row[2]), int(row[3]), int(row[4])
            net, dur = float(row[5]), int(row[6])
            total += qc
            items.append(
                QuestionDistributionItem(
                    name=name,
                    question_count=qc,
                    correct_count=cc,
                    wrong_count=wc,
                    blank_count=bc,
                    net_score=round(net, 2),
                    duration_minutes=dur,
                    correct_rate=round((cc / qc) * 100, 1) if qc else 0.0,
                )
            )
        return QuestionDistributionResponse(items=items, total_questions=total)

    async def _validate_links(
        self,
        user_id: uuid.UUID,
        study_plan_id: uuid.UUID | None,
        study_session_id: uuid.UUID | None,
    ) -> None:
        if study_plan_id is not None:
            plan = await self.plan_repo.get_by_id_for_user(study_plan_id, user_id)
            if plan is None:
                raise NotFoundError("Çalışma planı", str(study_plan_id))
        if study_session_id is not None:
            session = await self.session_repo.get_by_id_for_user(study_session_id, user_id)
            if session is None:
                raise NotFoundError("Çalışma oturumu", str(study_session_id))


def pagination_meta(page: int, page_size: int, total: int) -> dict:
    total_pages = max(1, math.ceil(total / page_size)) if total else 0
    return {
        "page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": total_pages,
    }
