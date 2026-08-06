"""M33 — Smart Question Pool Manager & inventory.

Bu modül:
- Config tabanlı minimum/target stok hedeflerini uygular
- Eksik topic'leri üretir ve question_pool_cards'a ekler
- Inventory metriklerini hesaplar
- Distributed lock ile aynı topic'in iki kez üretilmesini engeller
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import case, func, select, update, or_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.core.config import settings
from app.core.question_pool_stock_config import (
    QuestionPoolStockTarget,
    load_question_pool_stock_targets,
)
from app.database.base import get_db
from app.models.exam_intelligence import EiSubject, EiTopic
from app.models.question_pool import QuestionPoolCard
from app.models.question_pool_inventory import (
    QuestionPoolGenerationHistory,
    QuestionPoolGenerationLock,
)
from app.services.ai_cost.batch_generate import generate_batch_one_call
from app.services.ai_cost.pool import QuestionPoolService, generate_card_fingerprint
from app.services.ai_cost.flags import midnight_scheduler_enabled
from app.services.qie.types import GenerateContext

logger = logging.getLogger("studyos.question_pool_manager")


_TZ = timezone(timedelta(hours=3), name="Europe/Istanbul")


@dataclass(frozen=True)
class TopicKey:
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str


def _now_istanbul() -> datetime:
    return datetime.now(_TZ)


def _inventory_status(*, current: int, minimum: int, target: int) -> str:
    if current < minimum:
        return "empty" if current == 0 else "low"
    if current < target:
        return "low"
    return "healthy"


def _quality_from_card(row: QuestionPoolCard) -> float | None:
    """qie_card JSONB içinden kalite/difficulty skorlarını çıkarır.

    Not: M32 kodunda qie_card alanı dolmayabiliyor; bu yüzden fallback var.
    """
    qie = row.qie_card or {}
    # Prefer persisted shape (quality_score/difficulty_score)
    qscore = qie.get("quality_score")
    if isinstance(qscore, (int, float)):
        return float(qscore)

    # Fallback: quality dict veya eksik alanlar
    quality = qie.get("quality")
    if isinstance(quality, dict):
        total = quality.get("total")
        if isinstance(total, (int, float)):
            return float(total)
    return None


def _difficulty_from_card(row: QuestionPoolCard) -> float | None:
    qie = row.qie_card or {}
    dscore = qie.get("difficulty_score")
    if isinstance(dscore, (int, float)) and dscore:
        return float(dscore)
    # Fallback: difficulty_band mapping
    mapping = {"easy": 50.0, "medium": 70.0, "hard": 90.0}
    return mapping.get(str(row.difficulty_band).lower())


class QuestionPoolInventoryService:
    """Config'teki topic'ler için inventory snapshot hesaplar."""

    async def resolve_target_codes(
        self, db: AsyncSession, target: QuestionPoolStockTarget
    ) -> TopicKey | None:
        exam = (target.exam or "").strip().lower()
        difficulty_band = (target.difficulty_band or "medium").strip().lower()

        subject_code = target.subject_code
        topic_code = target.topic_code
        if subject_code and topic_code:
            return TopicKey(exam=exam, subject_code=subject_code, topic_code=topic_code, difficulty_band=difficulty_band)

        # Name-based resolution (EiCatalog)
        if not target.subject_name or not target.topic_name:
            logger.warning("Stock target missing codes/names: %s", target)
            return None

        subj_name = str(target.subject_name).strip().lower()
        topic_name = str(target.topic_name).strip().lower()

        subj_stmt = (
            select(EiSubject)
            .where(EiSubject.exam_code == exam)
            .where(func.lower(EiSubject.name) == subj_name)
            .limit(1)
        )
        subj = (await db.execute(subj_stmt)).scalar_one_or_none()
        if subj is None:
            # Try aliases/contains
            subj_stmt = (
                select(EiSubject)
                .where(EiSubject.exam_code == exam)
                .where(func.lower(EiSubject.name).like(f"%{subj_name}%"))
                .limit(1)
            )
            subj = (await db.execute(subj_stmt)).scalar_one_or_none()

        found_topic = None

        if subj is None:
            # Fallback 1: If subject_name is actually a topic name in this exam (e.g. "Problemler", "Türev")
            topic_stmt = (
                select(EiTopic)
                .join(EiSubject, EiTopic.subject_code == EiSubject.code)
                .where(EiSubject.exam_code == exam)
                .where(
                    or_(
                        func.lower(EiTopic.name) == subj_name,
                        func.lower(EiTopic.name).like(f"%{subj_name}%"),
                    )
                )
                .limit(1)
            )
            found_topic = (await db.execute(topic_stmt)).scalar_one_or_none()
            if found_topic:
                subj_stmt = select(EiSubject).where(EiSubject.code == found_topic.subject_code).limit(1)
                subj = (await db.execute(subj_stmt)).scalar_one_or_none()

        if subj is None:
            logger.warning("Subject not found in EiCatalog exam=%s name=%s", exam, target.subject_name)
            return None

        if found_topic is None:
            topic_stmt = (
                select(EiTopic)
                .where(EiTopic.subject_code == subj.code)
                .where(func.lower(EiTopic.name) == topic_name)
                .limit(1)
            )
            found_topic = (await db.execute(topic_stmt)).scalar_one_or_none()

        if found_topic is None:
            topic_stmt = (
                select(EiTopic)
                .where(EiTopic.subject_code == subj.code)
                .where(func.lower(EiTopic.name).like(f"%{topic_name}%"))
                .limit(1)
            )
            found_topic = (await db.execute(topic_stmt)).scalar_one_or_none()

        if found_topic is None:
            # Fallback 2: If topic_name equals subject name or not found, select first topic under subject
            first_topic_stmt = (
                select(EiTopic)
                .where(EiTopic.subject_code == subj.code)
                .order_by(EiTopic.display_order)
                .limit(1)
            )
            found_topic = (await db.execute(first_topic_stmt)).scalar_one_or_none()

        if found_topic is None:
            logger.warning("Topic not found in EiCatalog exam=%s subject=%s name=%s", exam, subj.code, target.topic_name)
            return None

        return TopicKey(exam=exam, subject_code=subj.code, topic_code=found_topic.code, difficulty_band=difficulty_band)

    async def snapshot(self, db: AsyncSession) -> list[dict[str, Any]]:
        targets = load_question_pool_stock_targets()
        resolved: list[tuple[QuestionPoolStockTarget, TopicKey]] = []
        for t in targets:
            key = await self.resolve_target_codes(db, t)
            if key is not None:
                resolved.append((t, key))

        if not resolved:
            return []

        rows: list[dict[str, Any]] = []
        for t, key in resolved:
            # Current count + last generated/used
            base_q = (
                select(
                    func.count().label("cnt"),
                    func.max(QuestionPoolCard.created_at).label("last_generated"),
                    func.max(
                        case(
                            (QuestionPoolCard.use_count > 0, QuestionPoolCard.created_at),
                            else_=None,
                        )
                    ).label("last_used"),
                )
                .where(QuestionPoolCard.exam == key.exam)
                .where(QuestionPoolCard.subject_code == key.subject_code)
                .where(QuestionPoolCard.topic_code == key.topic_code)
                .where(QuestionPoolCard.difficulty_band == key.difficulty_band)
            )
            agg = (await db.execute(base_q)).first()
            current = int(agg.cnt or 0) if agg else 0
            last_generated = agg.last_generated if agg else None
            last_used = agg.last_used if agg else None

            q_rows = (
                select(QuestionPoolCard)
                .where(QuestionPoolCard.exam == key.exam)
                .where(QuestionPoolCard.subject_code == key.subject_code)
                .where(QuestionPoolCard.topic_code == key.topic_code)
                .where(QuestionPoolCard.difficulty_band == key.difficulty_band)
                .order_by(QuestionPoolCard.created_at.desc())
                .limit(200)
            )
            pool_rows = (await db.execute(q_rows)).scalars().all()

            q_values: list[float] = []
            d_values: list[float] = []
            for r in pool_rows:
                qv = _quality_from_card(r)
                if qv is not None:
                    q_values.append(qv)
                dv = _difficulty_from_card(r)
                if dv is not None:
                    d_values.append(dv)

            average_quality = float(sum(q_values) / len(q_values)) if q_values else None
            average_difficulty = float(sum(d_values) / len(d_values)) if d_values else None

            status = _inventory_status(
                current=current, minimum=int(t.minimum), target=int(t.target)
            )

            rows.append(
                {
                    "exam": key.exam,
                    "subject_code": key.subject_code,
                    "subject_name": t.subject_name or key.subject_code,
                    "topic_code": key.topic_code,
                    "topic_name": t.topic_name or key.topic_code,
                    "difficulty_band": key.difficulty_band,
                    "current": current,
                    "minimum": int(t.minimum),
                    "target": int(t.target),
                    "status": status,
                    "quality": average_quality,
                    "average_difficulty": average_difficulty,
                    "last_generated": last_generated,
                    "last_used": last_used,
                    "last_review": None,
                    "average_quality": average_quality,
                    "average_difficulty_value": average_difficulty,
                }
            )

        return rows


class QuestionPoolManagerService:
    """Konfigürasyondaki minimum hedefleri korur."""

    def __init__(self) -> None:
        self.inventory_service = QuestionPoolInventoryService()

    async def _count_topic(self, db: AsyncSession, key: TopicKey) -> int:
        stmt = (
            select(func.count())
            .select_from(QuestionPoolCard)
            .where(QuestionPoolCard.exam == key.exam)
            .where(QuestionPoolCard.subject_code == key.subject_code)
            .where(QuestionPoolCard.topic_code == key.topic_code)
            .where(QuestionPoolCard.difficulty_band == key.difficulty_band)
        )
        r = await db.execute(stmt)
        return int(r.scalar() or 0)

    async def acquire_topic_lock(
        self, db: AsyncSession, *, key: TopicKey, ttl_minutes: int = 15
    ) -> bool:
        lock_key = f"exam={key.exam}|subj={key.subject_code}|topic={key.topic_code}|diff={key.difficulty_band}"
        now = datetime.now(tz=UTC)
        expires_at = now + timedelta(minutes=ttl_minutes)

        ins = pg_insert(QuestionPoolGenerationLock).values(
            lock_key=lock_key, expires_at=expires_at
        )
        ins = ins.on_conflict_do_nothing(index_elements=["lock_key"])
        res = await db.execute(ins)
        # rowcount is unreliable; fallback to checking existence
        if res.rowcount and int(res.rowcount) > 0:
            return True

        # If lock exists but expired, extend it.
        upd = (
            update(QuestionPoolGenerationLock)
            .where(QuestionPoolGenerationLock.lock_key == lock_key)
            .where(QuestionPoolGenerationLock.expires_at < now)
            .values(expires_at=expires_at)
        )
        upd_res = await db.execute(upd)
        return bool(upd_res.rowcount and int(upd_res.rowcount) > 0)

    async def _read_cost_events_between(
        self, *, start_utc: datetime, end_utc: datetime, kind: str
    ) -> list[dict[str, Any]]:
        """data/ai_cost/events_YYYY-MM-DD.jsonl üzerinden best-effort okur."""
        # cost_logger default root: backend/data/ai_cost
        # Use same convention to locate files.
        # This may fail in production if filesystem is ephemeral.
        from app.services.ai_cost.cost_logger import _default_root  # type: ignore

        try:
            root = _default_root()
            day_key = start_utc.astimezone(timezone.utc).strftime("%Y-%m-%d")
            path = root / f"events_{day_key}.jsonl"
            if not path.exists():
                return []
            out: list[dict[str, Any]] = []
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    evt = json.loads(line)
                    ts = datetime.fromisoformat(evt.get("timestamp"))
                    if evt.get("kind") != kind:
                        continue
                    if start_utc <= ts <= end_utc:
                        out.append(evt)
            return out
        except Exception:
            return []

    async def fill_topic_to_target(
        self,
        db: AsyncSession,
        *,
        key: TopicKey,
        minimum: int,
        target: int,
        dry_run: bool,
        subject_name: str | None = None,
        topic_name: str | None = None,
        max_batches: int = 30,
    ) -> dict[str, Any]:
        """Bir topic için current < minimum ise hedefe kadar üretir."""
        current = await self._count_topic(db, key)
        if current >= minimum:
            return {
                "key": key,
                "planned": 0,
                "accepted": 0,
                "rejected": 0,
                "skipped": True,
            }

        planned = max(0, int(target) - current)
        if planned <= 0:
            return {
                "key": key,
                "planned": 0,
                "accepted": 0,
                "rejected": 0,
                "skipped": True,
            }

        if dry_run:
            return {
                "key": key,
                "planned": planned,
                "accepted": 0,
                "rejected": 0,
                "skipped": False,
                "dry_run": True,
            }

        # If AI provider is null/disabled, batch_generate will not be able to
        # produce valid JSON payloads (so pool remains unchanged).
        primary = (settings.AI_PROVIDER or "null").strip().lower()
        if primary in ("", "null", "none"):
            return {
                "key": key,
                "planned": planned,
                "accepted": 0,
                "rejected": planned,
                "skipped": True,
                "reason": "AI_PROVIDER is null (no Gemini/batch payloads)",
            }

        ok = await self.acquire_topic_lock(db, key=key)
        if not ok:
            return {
                "key": key,
                "planned": planned,
                "accepted": 0,
                "rejected": 0,
                "skipped": True,
                "reason": "locked",
            }

        start = datetime.now(tz=UTC)
        before = current
        accepted_total = 0
        duration_ms = None
        gemini_calls = 0
        estimated_cost = None
        provider = None
        model = None

        attempts = 0
        try:
            while accepted_total < planned and attempts < max_batches:
                remaining = planned - accepted_total
                batch_n = min(remaining, 20)
                ctx = GenerateContext(
                    exam=key.exam,
                    subject_code=key.subject_code,
                    subject_name=subject_name or key.subject_code,
                    topic_code=key.topic_code,
                    topic_name=topic_name or key.topic_code,
                    count=batch_n,
                    difficulty_band=key.difficulty_band,
                    user_id=None,
                    kind="batch_generate",
                )
                t0 = datetime.now(tz=UTC)
                cards, _fp, result = await generate_batch_one_call(
                    db, ctx, count=batch_n
                )
                # Ensure newly added rows are visible
                await db.commit()
                _ = cards  # accepted_count computed via counts

                after = await self._count_topic(db, key)
                accepted_total = max(0, after - before)

                # Best-effort meta from batch result
                if result is not None:
                    provider = getattr(result, "provider", None)
                    model = getattr(result, "model", None)

                # avoid tight infinite loops when no new cards are added
                if accepted_total == max(0, after - before) and len(cards) == 0:
                    # still might have been dedup/skipped; don't hard-fail immediately
                    pass

                attempts += 1

            duration_ms = (
                (datetime.now(tz=UTC) - start).total_seconds() * 1000.0
            )
        except Exception as e:
            duration_ms = (
                (datetime.now(tz=UTC) - start).total_seconds() * 1000.0
            )
            logger.exception("fill_topic failed key=%s: %s", key, e)
            await db.rollback()
            raise

        end = datetime.now(tz=UTC)
        events = await self._read_cost_events_between(
            start_utc=start, end_utc=end, kind="batch_generate"
        )
        # Compute gemini calls + estimated cost
        gemini_calls = sum(1 for evt in events if evt.get("provider") == "gemini")
        try:
            total_cost = sum(float(evt.get("estimated_cost_usd") or 0.0) for evt in events)
            estimated_cost = total_cost if total_cost > 0 else None
        except Exception:
            estimated_cost = None

        rejected = max(0, planned - accepted_total)

        # Best-effort quality average from the latest cards.
        q_rows = (
            select(QuestionPoolCard)
            .where(QuestionPoolCard.exam == key.exam)
            .where(QuestionPoolCard.subject_code == key.subject_code)
            .where(QuestionPoolCard.topic_code == key.topic_code)
            .where(QuestionPoolCard.difficulty_band == key.difficulty_band)
            .order_by(QuestionPoolCard.created_at.desc())
            .limit(200)
        )
        latest = (await db.execute(q_rows)).scalars().all()
        q_vals: list[float] = []
        for r in latest:
            qv = _quality_from_card(r)
            if qv is not None:
                q_vals.append(qv)
        quality_average = float(sum(q_vals) / len(q_vals)) if q_vals else None

        # Persist generation history
        hist = QuestionPoolGenerationHistory(
            timestamp=start,
            exam=key.exam,
            subject_code=key.subject_code,
            topic_code=key.topic_code,
            difficulty_band=key.difficulty_band,
            generated_count=planned,
            accepted=int(accepted_total),
            rejected=int(rejected),
            quality_average=quality_average,
            duration_ms=float(duration_ms) if duration_ms is not None else None,
            gemini_calls=int(gemini_calls),
            estimated_cost=float(estimated_cost) if estimated_cost is not None else None,
            provider=provider,
            model=model,
        )
        db.add(hist)
        await db.commit()

        return {
            "key": key,
            "planned": planned,
            "accepted": accepted_total,
            "rejected": rejected,
            "skipped": False,
            "dry_run": False,
            "gemini_calls": gemini_calls,
            "estimated_cost": estimated_cost,
        }

    async def fill_topic_amount(
        self,
        db: AsyncSession,
        *,
        key: TopicKey,
        count: int,
        dry_run: bool,
        max_batches: int = 30,
    ) -> dict[str, Any]:
        """Manual admin fill: belirli topic için istenen count kadar üretmeye çalışır."""
        if count <= 0:
            raise ValidationError("count must be positive")

        if dry_run:
            return {
                "key": key,
                "planned": int(count),
                "accepted": 0,
                "rejected": 0,
                "dry_run": True,
            }

        primary = (settings.AI_PROVIDER or "null").strip().lower()
        if primary in ("", "null", "none"):
            return {
                "key": key,
                "planned": int(count),
                "accepted": 0,
                "rejected": int(count),
                "skipped": True,
                "reason": "AI_PROVIDER is null (no Gemini/batch payloads)",
            }

        ok = await self.acquire_topic_lock(db, key=key)
        if not ok:
            return {
                "key": key,
                "planned": int(count),
                "accepted": 0,
                "rejected": 0,
                "skipped": True,
                "reason": "locked",
            }

        start = datetime.now(tz=UTC)
        before = await self._count_topic(db, key)
        accepted_total = 0
        duration_ms = None
        gemini_calls = 0
        estimated_cost = None
        provider = None
        model = None

        attempts = 0
        try:
            while accepted_total < count and attempts < max_batches:
                remaining = count - accepted_total
                batch_n = min(remaining, 10)
                ctx = GenerateContext(
                    exam=key.exam,
                    subject_code=key.subject_code,
                    subject_name=key.subject_code,
                    topic_code=key.topic_code,
                    topic_name=key.topic_code,
                    count=batch_n,
                    difficulty_band=key.difficulty_band,
                    user_id=None,
                    kind="batch_generate",
                )

                cards, status, result = await generate_batch_one_call(db, ctx, count=batch_n)
                if cards:
                    pool_svc = QuestionPoolService(db)
                    for c in cards:
                        fp = generate_card_fingerprint(ctx, c.plan)
                        await pool_svc.put_card(
                            fingerprint=fp,
                            card=c,
                            exam=key.exam,
                            subject_code=key.subject_code,
                            topic_code=key.topic_code,
                            difficulty_band=key.difficulty_band,
                            skill=c.plan.skill,
                        )
                await db.commit()

                after = await self._count_topic(db, key)
                accepted_total = max(0, after - before)
                attempts += 1
        except Exception as e:
            duration_ms = (
                (datetime.now(tz=UTC) - start).total_seconds() * 1000.0
            )
            logger.exception("fill_topic_amount failed key=%s: %s", key, e)
            await db.rollback()
            raise

        duration_ms = (datetime.now(tz=UTC) - start).total_seconds() * 1000.0
        end = datetime.now(tz=UTC)
        events = await self._read_cost_events_between(
            start_utc=start, end_utc=end, kind="batch_generate"
        )
        gemini_calls = sum(1 for evt in events if evt.get("provider") == "gemini")
        try:
            total_cost = sum(float(evt.get("estimated_cost_usd") or 0.0) for evt in events)
            estimated_cost = total_cost if total_cost > 0 else None
        except Exception:
            estimated_cost = None

        rejected = max(0, int(count) - accepted_total)

        # Quality average from latest cards
        q_rows = (
            select(QuestionPoolCard)
            .where(QuestionPoolCard.exam == key.exam)
            .where(QuestionPoolCard.subject_code == key.subject_code)
            .where(QuestionPoolCard.topic_code == key.topic_code)
            .where(QuestionPoolCard.difficulty_band == key.difficulty_band)
            .order_by(QuestionPoolCard.created_at.desc())
            .limit(200)
        )
        latest = (await db.execute(q_rows)).scalars().all()
        q_vals: list[float] = []
        for r in latest:
            qv = _quality_from_card(r)
            if qv is not None:
                q_vals.append(qv)
        quality_average = float(sum(q_vals) / len(q_vals)) if q_vals else None

        hist = QuestionPoolGenerationHistory(
            timestamp=start,
            exam=key.exam,
            subject_code=key.subject_code,
            topic_code=key.topic_code,
            difficulty_band=key.difficulty_band,
            generated_count=int(count),
            accepted=int(accepted_total),
            rejected=int(rejected),
            quality_average=quality_average,
            duration_ms=float(duration_ms) if duration_ms is not None else None,
            gemini_calls=int(gemini_calls),
            estimated_cost=float(estimated_cost) if estimated_cost is not None else None,
            provider=provider,
            model=model,
        )
        db.add(hist)
        await db.commit()

        return {
            "key": key,
            "planned": int(count),
            "accepted": accepted_total,
            "rejected": rejected,
            "skipped": False,
            "dry_run": False,
            "gemini_calls": gemini_calls,
            "estimated_cost": estimated_cost,
        }

    async def fill_missing(
        self,
        db: AsyncSession,
        *,
        dry_run: bool,
    ) -> dict[str, Any]:
        primary = (settings.AI_PROVIDER or "null").strip().lower()
        if primary in ("", "null", "none") and not dry_run:
            # In this mode batch_generate yields invalid payloads and makes no progress.
            logger.warning("M33: AI_PROVIDER is null — skipping fill_missing (non-dry_run).")
            return {"planned": 0, "accepted": 0, "items": [], "skipped": True, "reason": "AI_PROVIDER is null"}

        from app.services.question_production.cost_gate import check_can_generate

        gate = check_can_generate(planned_count=1)
        if not gate.can_generate and not dry_run:
            return {
                "planned": 0,
                "accepted": 0,
                "items": [],
                "skipped": True,
                "reason": gate.reason,
                "cost_gate": gate.to_dict(),
            }

        targets = load_question_pool_stock_targets()
        resolved: list[tuple[QuestionPoolStockTarget, TopicKey]] = []
        for t in targets:
            key = await self.inventory_service.resolve_target_codes(db, t)
            if key is not None:
                resolved.append((t, key))

        results = []
        for t, key in resolved:
            results.append(
                await self.fill_topic_to_target(
                    db,
                    key=key,
                    minimum=int(t.minimum),
                    target=int(t.target),
                    dry_run=dry_run,
                    subject_name=t.subject_name,
                    topic_name=t.topic_name,
                )
            )

        accepted = sum(int(r.get("accepted") or 0) for r in results)
        planned = sum(int(r.get("planned") or 0) for r in results)
        return {
            "planned": planned,
            "accepted": accepted,
            "items": results,
        }

