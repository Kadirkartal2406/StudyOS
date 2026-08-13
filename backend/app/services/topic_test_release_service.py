"""Topic Test Catalog release — assemble & publish (idempotent, safe resume)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    TOPIC_TEST_DIFFICULTIES,
    TOPIC_TEST_QUESTION_COUNT,
    normalize_exam_code,
)
from app.models.question_pool import QuestionPoolCard
from app.models.topic_test import (
    TopicTest,
    TopicTestItem,
    TopicTestStatus,
)
from app.schemas.topic_test import TopicTestReleaseRequest, TopicTestReleaseResult
from app.services.ai_cost.pool import QuestionPoolService
from app.services.topic_test_catalog_service import iso_week_id

logger = logging.getLogger("studyos.topic_test_release")


class TopicTestReleaseService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.pool = QuestionPoolService(db)

    async def next_ordinal(
        self,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty: str,
    ) -> int:
        n = await self.db.scalar(
            select(func.count())
            .select_from(TopicTest)
            .where(
                TopicTest.exam == exam,
                TopicTest.subject_code == subject_code,
                TopicTest.topic_code == topic_code,
                TopicTest.difficulty == difficulty,
                TopicTest.status == TopicTestStatus.PUBLISHED,
            )
        )
        return int(n or 0) + 1

    async def catalogued_pool_card_ids(self) -> set[uuid.UUID]:
        """Global: a pool card may appear in at most one catalog item."""
        rows = (await self.db.execute(select(TopicTestItem.pool_card_id))).scalars().all()
        return {r for r in rows if r is not None}

    async def catalogued_content_hashes(self) -> set[str]:
        """Global: content_hash uniqueness across all catalog items."""
        rows = (await self.db.execute(select(TopicTestItem.content_hash))).scalars().all()
        return {h for h in rows if h}

    async def pick_cards(
        self,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty: str,
        need: int = TOPIC_TEST_QUESTION_COUNT,
    ) -> list[QuestionPoolCard]:
        used_ids = await self.catalogued_pool_card_ids()
        used_hashes = await self.catalogued_content_hashes()
        candidates = await self.pool.get_unused_for_topic(
            exam=exam,
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty,
            limit=need,
            max_fetch=max(need * 20, 80),
        )
        picked: list[QuestionPoolCard] = []
        seen_hash: set[str] = set()
        band = (difficulty or "medium").strip().lower()
        for c in candidates:
            if c.id in used_ids:
                continue
            card_band = (c.difficulty_band or "").strip().lower()
            if card_band != band:
                logger.info(
                    "topic_test pick skip wrong_band id=%s want=%s got=%s",
                    c.id,
                    band,
                    card_band,
                )
                continue
            ch = (c.content_hash or "").strip()
            if not ch or ch in used_hashes or ch in seen_hash:
                continue
            picked.append(c)
            seen_hash.add(ch)
            if len(picked) >= need:
                break
        return picked

    async def ensure_pool_stock(
        self,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        subject_name: str | None,
        topic_name: str | None,
        difficulty: str,
        need: int,
    ) -> int:
        """Fill pool in a *separate* session.

        QuestionPoolManagerService commits/rollbacks its session. Using the
        release session here would wipe sibling difficulties already flushed
        in the same weekly release transaction.
        """
        from app.core.exceptions import (
            AIProviderError,
            AIQuotaExceededError,
            AIRateLimitError,
            AIUnavailableError,
        )
        from app.database.base import AsyncSessionLocal
        from app.services.question_pool_manager import QuestionPoolManagerService, TopicKey

        mgr = QuestionPoolManagerService()
        key = TopicKey(
            exam=exam,
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty,
        )
        try:
            async with AsyncSessionLocal() as fill_db:
                current = await mgr._count_topic(fill_db, key)
                minimum = int(current) + max(1, need)
                target = minimum + 5
                result = await mgr.fill_topic_to_target(
                    fill_db,
                    key=key,
                    minimum=minimum,
                    target=target,
                    dry_run=False,
                    subject_name=subject_name,
                    topic_name=topic_name,
                )
                accepted = int(result.get("accepted") or 0)
                logger.info(
                    "topic_test pool fill exam=%s topic=%s diff=%s accepted=%s "
                    "current=%s minimum=%s",
                    exam,
                    topic_code,
                    difficulty,
                    accepted,
                    current,
                    minimum,
                )
                return accepted
        except (AIQuotaExceededError, AIRateLimitError, AIUnavailableError) as exc:
            logger.warning(
                "topic_test pool fill quota/unavailable exam=%s topic=%s "
                "diff=%s err=%s — leaving incomplete for resume",
                exam,
                topic_code,
                difficulty,
                exc,
            )
            return 0
        except AIProviderError as exc:
            logger.warning(
                "topic_test pool fill provider error exam=%s topic=%s "
                "diff=%s err=%s",
                exam,
                topic_code,
                difficulty,
                exc,
            )
            return 0
        except Exception:
            logger.exception(
                "topic_test pool fill unexpected exam=%s topic=%s diff=%s",
                exam,
                topic_code,
                difficulty,
            )
            return 0

    def _cards_publishable(
        self,
        cards: list[QuestionPoolCard],
        *,
        difficulty: str,
        exam: str,
        subject_code: str,
        topic_code: str,
    ) -> tuple[bool, str]:
        if len(cards) != TOPIC_TEST_QUESTION_COUNT:
            return False, f"count:{len(cards)}"
        band = difficulty.strip().lower()
        hashes: set[str] = set()
        ids: set[uuid.UUID] = set()
        from app.services.qie.skill_profiles import pool_row_compatible

        for c in cards:
            if (c.difficulty_band or "").strip().lower() != band:
                return False, f"wrong_band:{c.id}"
            ch = (c.content_hash or "").strip()
            if not ch or ch in hashes:
                return False, "hash_dup_or_empty"
            hashes.add(ch)
            if c.id in ids:
                return False, "id_dup"
            ids.add(c.id)
            if not pool_row_compatible(
                c,
                exam=exam,
                subject_code=subject_code,
                topic_code=topic_code,
            ):
                return False, f"domain:{c.id}"
        return True, "ok"

    async def release_or_skip_one(
        self,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        week_id: str,
        difficulty: str,
        subject_name: str | None = None,
        topic_name: str | None = None,
        dry_run: bool = False,
        fill_pool_if_short: bool = True,
    ) -> str:
        exam_n = normalize_exam_code(exam)
        sub = subject_code.strip()
        top = topic_code.strip()
        diff = (difficulty or "medium").strip().lower()
        if diff not in TOPIC_TEST_DIFFICULTIES:
            return f"failed:bad_difficulty:{diff}"

        existing = await self.db.scalar(
            select(TopicTest).where(
                TopicTest.exam == exam_n,
                TopicTest.subject_code == sub,
                TopicTest.topic_code == top,
                TopicTest.week_id == week_id,
                TopicTest.difficulty == diff,
            )
        )
        if existing is not None:
            if existing.status == TopicTestStatus.PUBLISHED:
                # Immutable: never regenerate / mutate published tests.
                return "skipped:already_published"
            item_rows = list(
                (
                    await self.db.execute(
                        select(TopicTestItem).where(TopicTestItem.test_id == existing.id)
                    )
                )
                .scalars()
                .all()
            )
            if len(item_rows) == TOPIC_TEST_QUESTION_COUNT:
                # Validate snapshots still coherent before publishing draft.
                # Items are snapshots; pool_card difficulty must still match.
                card_ids = [it.pool_card_id for it in item_rows]
                cards = list(
                    (
                        await self.db.execute(
                            select(QuestionPoolCard).where(
                                QuestionPoolCard.id.in_(card_ids)
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                by_id = {c.id: c for c in cards}
                ordered = [by_id[i.pool_card_id] for i in item_rows if i.pool_card_id in by_id]
                ok, reason = self._cards_publishable(
                    ordered,
                    difficulty=diff,
                    exam=exam_n,
                    subject_code=sub,
                    topic_code=top,
                )
                if ok and not dry_run:
                    existing.status = TopicTestStatus.PUBLISHED
                    existing.published_at = existing.published_at or datetime.now(UTC)
                    existing.question_count = TOPIC_TEST_QUESTION_COUNT
                    await self.db.flush()
                    return "created:published_existing_draft"
                if ok and dry_run:
                    return "created:dry_run"
                # Invalid draft items → clear and rebuild below
                logger.warning(
                    "topic_test draft invalid id=%s reason=%s — rebuild",
                    existing.id,
                    reason,
                )
            test = existing
        else:
            test = None

        cards = await self.pick_cards(
            exam=exam_n,
            subject_code=sub,
            topic_code=top,
            difficulty=diff,
            need=TOPIC_TEST_QUESTION_COUNT,
        )
        if len(cards) < TOPIC_TEST_QUESTION_COUNT and fill_pool_if_short and not dry_run:
            await self.ensure_pool_stock(
                exam=exam_n,
                subject_code=sub,
                topic_code=top,
                subject_name=subject_name,
                topic_name=topic_name,
                difficulty=diff,
                need=TOPIC_TEST_QUESTION_COUNT - len(cards),
            )
            cards = await self.pick_cards(
                exam=exam_n,
                subject_code=sub,
                topic_code=top,
                difficulty=diff,
                need=TOPIC_TEST_QUESTION_COUNT,
            )

        ok, reason = self._cards_publishable(
            cards[:TOPIC_TEST_QUESTION_COUNT]
            if len(cards) >= TOPIC_TEST_QUESTION_COUNT
            else cards,
            difficulty=diff,
            exam=exam_n,
            subject_code=sub,
            topic_code=top,
        )
        if not ok or len(cards) < TOPIC_TEST_QUESTION_COUNT:
            if dry_run:
                return f"failed:short:{len(cards)}:{reason}"
            if test is None:
                ordinal = await self.next_ordinal(
                    exam=exam_n, subject_code=sub, topic_code=top, difficulty=diff
                )
                test = TopicTest(
                    id=uuid.uuid4(),
                    exam=exam_n,
                    subject_code=sub,
                    topic_code=top,
                    subject_name=subject_name,
                    topic_name=topic_name,
                    week_id=week_id,
                    difficulty=diff,
                    ordinal=ordinal,
                    status=TopicTestStatus.FAILED,
                    question_count=len(cards),
                )
                self.db.add(test)
                await self.db.flush()
            else:
                test.status = TopicTestStatus.FAILED
                test.question_count = len(cards)
                await self.db.flush()
            logger.warning(
                "topic_test incomplete exam=%s topic=%s week=%s diff=%s have=%s reason=%s",
                exam_n,
                top,
                week_id,
                diff,
                len(cards),
                reason,
            )
            return f"failed:short:{len(cards)}"

        if dry_run:
            return "created:dry_run"

        if test is None:
            ordinal = await self.next_ordinal(
                exam=exam_n, subject_code=sub, topic_code=top, difficulty=diff
            )
            test = TopicTest(
                id=uuid.uuid4(),
                exam=exam_n,
                subject_code=sub,
                topic_code=top,
                subject_name=subject_name,
                topic_name=topic_name,
                week_id=week_id,
                difficulty=diff,
                ordinal=ordinal,
                status=TopicTestStatus.DRAFT,
                question_count=TOPIC_TEST_QUESTION_COUNT,
            )
            self.db.add(test)
            await self.db.flush()
        else:
            if test.status == TopicTestStatus.PUBLISHED:
                return "skipped:already_published"
            old_items = (
                await self.db.execute(
                    select(TopicTestItem).where(TopicTestItem.test_id == test.id)
                )
            ).scalars().all()
            for oi in old_items:
                await self.db.delete(oi)
            await self.db.flush()

        try:
            async with self.db.begin_nested():
                for i, card in enumerate(cards[:TOPIC_TEST_QUESTION_COUNT]):
                    self.db.add(
                        TopicTestItem(
                            id=uuid.uuid4(),
                            test_id=test.id,
                            ord_index=i,
                            pool_card_id=card.id,
                            content_hash=card.content_hash,
                            stem=card.stem,
                            choices=dict(card.choices or {}),
                            correct_key=(card.correct_key or "A").upper(),
                            explanation=card.explanation,
                            qie_card=dict(card.qie_card or {}),
                        )
                    )
                    card.use_count = int(card.use_count or 0) + 1

                test.status = TopicTestStatus.PUBLISHED
                test.published_at = datetime.now(UTC)
                test.question_count = TOPIC_TEST_QUESTION_COUNT
                if subject_name:
                    test.subject_name = subject_name
                if topic_name:
                    test.topic_name = topic_name
                await self.db.flush()
        except IntegrityError as exc:
            logger.warning(
                "topic_test integrity race exam=%s topic=%s week=%s diff=%s err=%s",
                exam_n,
                top,
                week_id,
                diff,
                exc,
            )
            # Savepoint rolled back; mark FAILED without wiping other diffs.
            test.status = TopicTestStatus.FAILED
            test.question_count = 0
            await self.db.flush()
            return "failed:integrity_race"

        logger.info(
            "topic_test published id=%s exam=%s topic=%s week=%s diff=%s ordinal=%s",
            test.id,
            exam_n,
            top,
            week_id,
            diff,
            test.ordinal,
        )
        return "created:published"

    async def release_topic_week(
        self, body: TopicTestReleaseRequest
    ) -> TopicTestReleaseResult:
        week_id = (body.week_id or "").strip() or iso_week_id()
        exam_n = normalize_exam_code(body.exam)
        created: list[str] = []
        skipped: list[str] = []
        failed: list[str] = []
        for diff in TOPIC_TEST_DIFFICULTIES:
            outcome = await self.release_or_skip_one(
                exam=exam_n,
                subject_code=body.subject_code,
                topic_code=body.topic_code,
                week_id=week_id,
                difficulty=diff,
                subject_name=body.subject_name,
                topic_name=body.topic_name,
                dry_run=body.dry_run,
                fill_pool_if_short=body.fill_pool_if_short,
            )
            tag = f"{diff}:{outcome}"
            if outcome.startswith("created"):
                created.append(tag)
            elif outcome.startswith("skipped"):
                skipped.append(tag)
            else:
                failed.append(tag)
        return TopicTestReleaseResult(
            week_id=week_id,
            exam=exam_n,
            subject_code=body.subject_code.strip(),
            topic_code=body.topic_code.strip(),
            created=created,
            skipped=skipped,
            failed=failed,
            dry_run=body.dry_run,
        )
