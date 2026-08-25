"""Topic Test Catalog — list / start / submit (no Gemini on user path)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import TOPIC_TEST_QUESTION_COUNT, normalize_exam_code
from app.core.exceptions import NotFoundError, ValidationError
from app.services.topic_catalog_resolver import topic_codes_for_dual_read
from app.models.topic_test import (
    TopicTest,
    TopicTestAttempt,
    TopicTestAttemptAnswer,
    TopicTestAttemptStatus,
    TopicTestItem,
    TopicTestStatus,
)
from app.schemas.topic_test import (
    TopicTestAttemptRead,
    TopicTestCatalogRead,
    TopicTestItemPublic,
    TopicTestListItem,
    TopicTestReviewItem,
    TopicTestSubmitRequest,
    TopicTestSubmitResult,
)

logger = logging.getLogger("studyos.topic_test_catalog")

_DIFF_LABEL = {"easy": "Kolay", "medium": "Orta", "hard": "Zor"}

# Parent exam keys that may map to multiple pool exam identities.
_EXAM_PARENTS = frozenset(
    {"kpss", "ayt", "yks", "lgs", "yokdil", "ales", "dgs", "ags"}
)


def _exam_match_clause(exam_n: str):
    """Match exact exam or parent family (kpss → kpss_lisans|...)."""
    if exam_n in _EXAM_PARENTS:
        return or_(
            TopicTest.exam == exam_n,
            TopicTest.exam.startswith(f"{exam_n}_"),
        )
    return TopicTest.exam == exam_n


def iso_week_id(dt: datetime | None = None) -> str:
    """Canonical week id: YYYY-Www in Europe/Istanbul (not bare UTC)."""
    istanbul = timezone(timedelta(hours=3), name="Europe/Istanbul")
    if dt is None:
        d = datetime.now(istanbul)
    elif dt.tzinfo is None:
        d = dt.replace(tzinfo=UTC).astimezone(istanbul)
    else:
        d = dt.astimezone(istanbul)
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def production_target_week_id(dt: datetime | None = None) -> str:
    """ISO week id for the Monday users will open (production runs the prior Mon–Sat)."""
    istanbul = timezone(timedelta(hours=3), name="Europe/Istanbul")
    if dt is None:
        now = datetime.now(istanbul)
    elif dt.tzinfo is None:
        now = dt.replace(tzinfo=UTC).astimezone(istanbul)
    else:
        now = dt.astimezone(istanbul)

    wd = now.weekday()  # Mon=0 … Sun=6
    if wd == 6:
        target = now + timedelta(days=1)
    elif wd == 0:
        target = now + timedelta(days=7)
    elif wd == 5:
        target = now + timedelta(days=2)
    else:
        target = now + timedelta(days=7 - wd)
    return iso_week_id(target)


def test_title(*, difficulty: str, ordinal: int) -> str:
    label = _DIFF_LABEL.get((difficulty or "").lower(), difficulty)
    return f"{label} Test {ordinal}"


class TopicTestCatalogService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_catalog(
        self,
        user_id: uuid.UUID,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
    ) -> TopicTestCatalogRead:
        exam_n = normalize_exam_code(exam)
        sub = subject_code.strip()
        top = topic_code.strip()
        topic_codes = topic_codes_for_dual_read(top) or (top,)
        q = (
            select(TopicTest)
            .where(
                _exam_match_clause(exam_n),
                TopicTest.subject_code == sub,
                TopicTest.topic_code.in_(topic_codes),
                TopicTest.status == TopicTestStatus.PUBLISHED,
            )
            .order_by(TopicTest.week_id.desc(), TopicTest.difficulty.asc())
        )
        tests = list((await self.db.execute(q)).scalars().all())
        subject_name = tests[0].subject_name if tests else None
        topic_name = tests[0].topic_name if tests else None

        attempt_map: dict[uuid.UUID, TopicTestAttempt] = {}
        if tests:
            ids = [t.id for t in tests]
            att_q = await self.db.execute(
                select(TopicTestAttempt)
                .where(
                    TopicTestAttempt.user_id == user_id,
                    TopicTestAttempt.test_id.in_(ids),
                )
                .order_by(TopicTestAttempt.started_at.desc())
            )
            for a in att_q.scalars().all():
                # Prefer submitted over in_progress when both exist
                prev = attempt_map.get(a.test_id)
                if prev is None:
                    attempt_map[a.test_id] = a
                elif (
                    prev.status != TopicTestAttemptStatus.SUBMITTED
                    and a.status == TopicTestAttemptStatus.SUBMITTED
                ):
                    attempt_map[a.test_id] = a

        items: list[TopicTestListItem] = []
        for t in tests:
            att = attempt_map.get(t.id)
            user_status = "not_started"
            accuracy = None
            attempt_id = None
            if att is not None:
                attempt_id = att.id
                if att.status == TopicTestAttemptStatus.SUBMITTED:
                    user_status = "submitted"
                    accuracy = att.accuracy_pct
                else:
                    user_status = "in_progress"
            items.append(
                TopicTestListItem(
                    id=t.id,
                    week_id=t.week_id,
                    difficulty=t.difficulty,
                    ordinal=t.ordinal,
                    question_count=t.question_count,
                    status=t.status,
                    published_at=t.published_at,
                    title=test_title(difficulty=t.difficulty, ordinal=t.ordinal),
                    user_status=user_status,
                    accuracy_pct=accuracy,
                    attempt_id=attempt_id,
                )
            )
        return TopicTestCatalogRead(
            exam=exam_n,
            subject_code=sub,
            topic_code=top,
            subject_name=subject_name,
            topic_name=topic_name,
            tests=items,
        )

    async def start_attempt(
        self,
        user_id: uuid.UUID,
        test_id: uuid.UUID,
    ) -> TopicTestAttemptRead:
        """Start or resume a catalog test. NEVER calls Gemini."""
        test = await self.db.scalar(
            select(TopicTest)
            .where(TopicTest.id == test_id)
            .options(selectinload(TopicTest.items))
        )
        if test is None or test.status != TopicTestStatus.PUBLISHED:
            raise NotFoundError("Test bulunamadı")
        if len(test.items) != TOPIC_TEST_QUESTION_COUNT:
            raise ValidationError("Test henüz hazır değil")

        existing = await self.db.scalar(
            select(TopicTestAttempt)
            .where(
                TopicTestAttempt.user_id == user_id,
                TopicTestAttempt.test_id == test_id,
                TopicTestAttempt.status == TopicTestAttemptStatus.IN_PROGRESS,
            )
            .order_by(TopicTestAttempt.started_at.desc())
            .limit(1)
        )
        if existing is not None:
            attempt = existing
        else:
            # Allow re-open of submitted tests as a fresh in_progress attempt
            # (archive review uses submitted attempt via get; re-solve creates new).
            attempt = TopicTestAttempt(
                id=uuid.uuid4(),
                user_id=user_id,
                test_id=test_id,
                status=TopicTestAttemptStatus.IN_PROGRESS,
            )
            self.db.add(attempt)
            await self.db.flush()

        logger.info(
            "topic_test start (no gemini) user=%s test_id=%s week=%s diff=%s attempt=%s",
            user_id,
            test_id,
            test.week_id,
            test.difficulty,
            attempt.id,
        )
        return TopicTestAttemptRead(
            attempt_id=attempt.id,
            test_id=test.id,
            week_id=test.week_id,
            difficulty=test.difficulty,
            ordinal=test.ordinal,
            status=attempt.status,
            question_count=len(test.items),
            items=[
                TopicTestItemPublic(
                    id=it.id,
                    ord_index=it.ord_index,
                    stem=it.stem,
                    choices=dict(it.choices or {}),
                )
                for it in sorted(test.items, key=lambda x: x.ord_index)
            ],
        )

    async def get_attempt(
        self,
        user_id: uuid.UUID,
        attempt_id: uuid.UUID,
        *,
        include_answers: bool = False,
    ) -> TopicTestAttemptRead | TopicTestSubmitResult:
        attempt = await self.db.scalar(
            select(TopicTestAttempt)
            .where(
                TopicTestAttempt.id == attempt_id,
                TopicTestAttempt.user_id == user_id,
            )
            .options(
                selectinload(TopicTestAttempt.test).selectinload(TopicTest.items),
                selectinload(TopicTestAttempt.answers),
            )
        )
        if attempt is None or attempt.test is None:
            raise NotFoundError("Deneme bulunamadı")
        test = attempt.test
        if attempt.status == TopicTestAttemptStatus.SUBMITTED and include_answers:
            return self._submit_result(attempt, test)
        return TopicTestAttemptRead(
            attempt_id=attempt.id,
            test_id=test.id,
            week_id=test.week_id,
            difficulty=test.difficulty,
            ordinal=test.ordinal,
            status=attempt.status,
            question_count=len(test.items),
            items=[
                TopicTestItemPublic(
                    id=it.id,
                    ord_index=it.ord_index,
                    stem=it.stem,
                    choices=dict(it.choices or {}),
                )
                for it in sorted(test.items, key=lambda x: x.ord_index)
            ],
        )

    async def submit(
        self,
        user_id: uuid.UUID,
        attempt_id: uuid.UUID,
        body: TopicTestSubmitRequest,
    ) -> TopicTestSubmitResult:
        attempt = await self.db.scalar(
            select(TopicTestAttempt)
            .where(
                TopicTestAttempt.id == attempt_id,
                TopicTestAttempt.user_id == user_id,
            )
            .options(
                selectinload(TopicTestAttempt.test).selectinload(TopicTest.items),
                selectinload(TopicTestAttempt.answers),
            )
        )
        if attempt is None or attempt.test is None:
            raise NotFoundError("Deneme bulunamadı")
        if attempt.status == TopicTestAttemptStatus.SUBMITTED:
            return self._submit_result(attempt, attempt.test)

        test = attempt.test
        by_id = {it.id: it for it in test.items}
        answers_in = {a.item_id: a.selected_key for a in body.answers}

        correct = wrong = blank = 0
        # Clear prior partial answers if any
        for old in list(attempt.answers):
            await self.db.delete(old)
        await self.db.flush()

        for it in test.items:
            selected = answers_in.get(it.id)
            is_correct: bool | None = None
            if selected is None:
                blank += 1
            elif selected == (it.correct_key or "").upper():
                correct += 1
                is_correct = True
            else:
                wrong += 1
                is_correct = False
            self.db.add(
                TopicTestAttemptAnswer(
                    id=uuid.uuid4(),
                    attempt_id=attempt.id,
                    item_id=it.id,
                    selected_key=selected,
                    is_correct=is_correct,
                )
            )

        total = len(test.items) or TOPIC_TEST_QUESTION_COUNT
        attempt.correct_count = correct
        attempt.wrong_count = wrong
        attempt.blank_count = blank
        attempt.accuracy_pct = round(100.0 * correct / total, 2)
        attempt.status = TopicTestAttemptStatus.SUBMITTED
        attempt.submitted_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(attempt, attribute_names=["answers"])

        logger.info(
            "topic_test submit user=%s attempt=%s test=%s correct=%s/%s",
            user_id,
            attempt.id,
            test.id,
            correct,
            total,
        )
        return self._submit_result(attempt, test)

    def _submit_result(
        self, attempt: TopicTestAttempt, test: TopicTest
    ) -> TopicTestSubmitResult:
        ans_map = {a.item_id: a for a in attempt.answers}
        review: list[TopicTestReviewItem] = []
        for it in sorted(test.items, key=lambda x: x.ord_index):
            a = ans_map.get(it.id)
            review.append(
                TopicTestReviewItem(
                    id=it.id,
                    ord_index=it.ord_index,
                    stem=it.stem,
                    choices=dict(it.choices or {}),
                    correct_key=it.correct_key,
                    explanation=it.explanation,
                    selected_key=a.selected_key if a else None,
                    is_correct=a.is_correct if a else None,
                )
            )
        return TopicTestSubmitResult(
            attempt_id=attempt.id,
            test_id=test.id,
            correct_count=int(attempt.correct_count or 0),
            wrong_count=int(attempt.wrong_count or 0),
            blank_count=int(attempt.blank_count or 0),
            accuracy_pct=float(attempt.accuracy_pct or 0.0),
            review_items=review,
        )
