"""Admin monitoring helpers for Topic Test Catalog."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import TOPIC_TEST_DIFFICULTIES, TOPIC_TEST_QUESTION_COUNT
from app.models.topic_test import TopicTest, TopicTestStatus
from app.services.question_pool_inventory_catalog import iter_catalog_inventory_slots
from app.services.topic_test_catalog_service import iso_week_id


class TopicTestAdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def inventory_topic_count(self, exam: str | None = None) -> int:
        seen: set[tuple[str, str, str]] = set()
        for slot in iter_catalog_inventory_slots():
            if exam and slot.exam != exam.strip().lower():
                continue
            seen.add((slot.exam, slot.subject_code, slot.topic_code))
        return len(seen)

    async def status(
        self,
        *,
        exam: str | None = None,
        week_id: str | None = None,
        limit_topics: int = 200,
    ) -> dict:
        week = (week_id or "").strip() or iso_week_id()
        exam_f = exam.strip().lower() if exam else None
        total_topics = self.inventory_topic_count(exam_f)

        q = select(TopicTest).where(TopicTest.week_id == week)
        if exam_f:
            q = q.where(TopicTest.exam == exam_f)
        tests = list((await self.db.execute(q)).scalars().all())

        by_status: dict[str, int] = defaultdict(int)
        by_diff_pub: dict[str, int] = {d: 0 for d in TOPIC_TEST_DIFFICULTIES}
        for t in tests:
            by_status[str(t.status)] += 1
            if t.status == TopicTestStatus.PUBLISHED:
                by_diff_pub[str(t.difficulty)] = by_diff_pub.get(str(t.difficulty), 0) + 1

        expected = total_topics * len(TOPIC_TEST_DIFFICULTIES)
        published = by_status.get(TopicTestStatus.PUBLISHED, 0)
        draft = by_status.get(TopicTestStatus.DRAFT, 0)
        failed = by_status.get(TopicTestStatus.FAILED, 0)
        missing = max(0, expected - published)

        pub_q = select(func.max(TopicTest.published_at)).where(
            TopicTest.week_id == week,
            TopicTest.status == TopicTestStatus.PUBLISHED,
        )
        if exam_f:
            pub_q = pub_q.where(TopicTest.exam == exam_f)
        last_pub = await self.db.scalar(pub_q)

        fail_q = (
            select(TopicTest)
            .where(
                TopicTest.week_id == week,
                TopicTest.status == TopicTestStatus.FAILED,
            )
            .order_by(TopicTest.updated_at.desc())
            .limit(1)
        )
        if exam_f:
            fail_q = fail_q.where(TopicTest.exam == exam_f)
        last_failed = (await self.db.execute(fail_q)).scalar_one_or_none()

        matrix_map: dict[tuple[str, str, str], dict[str, str]] = {}
        for t in tests:
            key = (t.exam, t.subject_code, t.topic_code)
            matrix_map.setdefault(
                key,
                {
                    "exam": t.exam,
                    "subject_code": t.subject_code,
                    "topic_code": t.topic_code,
                    "subject_name": t.subject_name,
                    "topic_name": t.topic_name,
                    "easy": "missing",
                    "medium": "missing",
                    "hard": "missing",
                    "test_ids": {},
                },
            )
            matrix_map[key][t.difficulty] = t.status
            matrix_map[key]["test_ids"][t.difficulty] = str(t.id)

        for slot in iter_catalog_inventory_slots():
            if exam_f and slot.exam != exam_f:
                continue
            key = (slot.exam, slot.subject_code, slot.topic_code)
            if key in matrix_map:
                continue
            if len(matrix_map) >= limit_topics:
                break
            matrix_map[key] = {
                "exam": slot.exam,
                "subject_code": slot.subject_code,
                "topic_code": slot.topic_code,
                "subject_name": slot.subject_name,
                "topic_name": slot.topic_name,
                "easy": "missing",
                "medium": "missing",
                "hard": "missing",
                "test_ids": {},
            }

        topics_matrix = list(matrix_map.values())[:limit_topics]

        def _score(row: dict) -> int:
            return sum(1 for d in TOPIC_TEST_DIFFICULTIES if row.get(d) != "published")

        topics_matrix.sort(key=_score, reverse=True)

        return {
            "current_week": week,
            "week_id": week,
            "exam": exam_f,
            "total_topics": total_topics,
            "expected_tests_this_week": expected,
            "published_tests": published,
            "draft_tests": draft,
            "failed_tests": failed,
            "missing_tests": missing,
            "easy_published": by_diff_pub.get("easy", 0),
            "medium_published": by_diff_pub.get("medium", 0),
            "hard_published": by_diff_pub.get("hard", 0),
            "weekly_progress": {
                "week_id": week,
                "published": published,
                "expected": expected,
                "pct": round(100.0 * published / expected, 2) if expected else 0.0,
                "failed": failed,
                "draft": draft,
                "missing": missing,
            },
            "last_release_at": last_pub.isoformat() if last_pub else None,
            "last_error": (
                {
                    "test_id": str(last_failed.id),
                    "exam": last_failed.exam,
                    "subject_code": last_failed.subject_code,
                    "topic_code": last_failed.topic_code,
                    "difficulty": last_failed.difficulty,
                    "updated_at": last_failed.updated_at.isoformat()
                    if last_failed.updated_at
                    else None,
                    "question_count": last_failed.question_count,
                }
                if last_failed
                else None
            ),
            "by_status": dict(by_status),
            "topics": topics_matrix,
            "questions_per_test": TOPIC_TEST_QUESTION_COUNT,
            "generated_at": datetime.now(UTC).isoformat(),
            "published": published,
            "failed": failed,
            "draft": draft,
        }

    async def list_tests(
        self,
        *,
        exam: str | None = None,
        week_id: str | None = None,
        status: str | None = None,
        difficulty: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        week = (week_id or "").strip() or None
        q = select(TopicTest).order_by(TopicTest.updated_at.desc()).limit(limit)
        if week:
            q = q.where(TopicTest.week_id == week)
        if exam:
            q = q.where(TopicTest.exam == exam.strip().lower())
        if status:
            q = q.where(TopicTest.status == status.strip().lower())
        if difficulty:
            q = q.where(TopicTest.difficulty == difficulty.strip().lower())
        rows = list((await self.db.execute(q)).scalars().all())
        return [
            {
                "id": str(t.id),
                "exam": t.exam,
                "subject_code": t.subject_code,
                "topic_code": t.topic_code,
                "subject_name": t.subject_name,
                "topic_name": t.topic_name,
                "week_id": t.week_id,
                "difficulty": t.difficulty,
                "ordinal": t.ordinal,
                "status": t.status,
                "question_count": t.question_count,
                "published_at": t.published_at.isoformat() if t.published_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in rows
        ]

    async def test_detail(self, test_id: uuid.UUID) -> dict | None:
        test = await self.db.scalar(
            select(TopicTest)
            .where(TopicTest.id == test_id)
            .options(selectinload(TopicTest.items))
        )
        if test is None:
            return None
        items = []
        for it in sorted(test.items, key=lambda x: x.ord_index):
            qie = it.qie_card or {}
            plan = qie.get("plan") if isinstance(qie, dict) else {}
            corr = qie.get("correctness") if isinstance(qie, dict) else {}
            items.append(
                {
                    "id": str(it.id),
                    "ord_index": it.ord_index,
                    "pool_card_id": str(it.pool_card_id),
                    "content_hash": it.content_hash,
                    "stem_preview": (it.stem or "")[:160],
                    "correct_key": it.correct_key,
                    "skill": (plan or {}).get("skill") or qie.get("skill"),
                    "stem_type": (plan or {}).get("stem_type") or qie.get("stem_type"),
                    "plan_difficulty": (plan or {}).get("difficulty"),
                    "difficulty_band": qie.get("difficulty_band")
                    if isinstance(qie, dict)
                    else None,
                    "correctness_verdict": (corr or {}).get("verdict"),
                }
            )
        return {
            "id": str(test.id),
            "exam": test.exam,
            "subject_code": test.subject_code,
            "topic_code": test.topic_code,
            "subject_name": test.subject_name,
            "topic_name": test.topic_name,
            "week_id": test.week_id,
            "difficulty": test.difficulty,
            "ordinal": test.ordinal,
            "status": test.status,
            "question_count": test.question_count,
            "published_at": test.published_at.isoformat() if test.published_at else None,
            "items": items,
        }
