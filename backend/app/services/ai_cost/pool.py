"""M32 P2 — Question Pool (DB cache; identical content → reuse)."""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_pool import QuestionPoolCard
from app.services.qie.types import GenerateContext, QuestionCard, QuestionPlan

logger = logging.getLogger("studyos.ai_cost.pool")


def pool_fingerprint(
    *,
    exam: str,
    subject_code: str,
    topic_code: str,
    difficulty_band: str,
    skill: str = "",
    bloom: str = "",
    choice_count: int = 5,
    stem_type: str = "",
    index: int = 0,
) -> str:
    raw = "|".join(
        [
            (exam or "").lower().strip(),
            (subject_code or "").lower().strip(),
            (topic_code or "").lower().strip(),
            (difficulty_band or "medium").lower().strip(),
            (skill or "").lower().strip(),
            (bloom or "").lower().strip(),
            str(int(choice_count or 5)),
            (stem_type or "").lower().strip(),
            str(int(index)),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def fingerprint_for_plan(plan: QuestionPlan, ctx: GenerateContext) -> str:
    """Plan-slot key (cache lookup). Not unique per question text."""
    return pool_fingerprint(
        exam=plan.exam or ctx.exam,
        subject_code=plan.subject_code or ctx.subject_code,
        topic_code=plan.topic_code or ctx.topic_code,
        difficulty_band=ctx.difficulty_band,
        skill=plan.skill,
        bloom=plan.bloom,
        choice_count=plan.choice_count,
        stem_type=plan.stem_type,
        index=plan.index,
    )


def card_content_hash(stem: str, choices: dict[str, str], correct_key: str) -> str:
    payload = json.dumps(
        {"stem": stem, "choices": choices, "correct_key": correct_key},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fingerprint_for_card(card: QuestionCard | dict[str, Any], ctx: GenerateContext) -> str:
    """Unique pool key: plan slot + question content (allows many cards per topic)."""
    if isinstance(card, QuestionCard):
        plan = card.plan
        stem = card.stem
        choices = dict(card.choices or {})
        correct_key = card.correct_key
    else:
        plan_raw = card.get("plan") if isinstance(card.get("plan"), dict) else {}
        from app.services.qie.types import QuestionPlan as QP

        plan = QP(
            exam=str(plan_raw.get("exam") or ctx.exam),
            subject_code=str(plan_raw.get("subject_code") or ctx.subject_code),
            subject_name=str(plan_raw.get("subject_name") or ctx.subject_name or ""),
            topic_code=str(plan_raw.get("topic_code") or ctx.topic_code),
            topic_name=str(plan_raw.get("topic_name") or ctx.topic_name or ""),
            skill=str(plan_raw.get("skill") or ""),
            bloom=str(plan_raw.get("bloom") or "analyze"),
            stem_type=str(plan_raw.get("stem_type") or ""),
            choice_count=int(plan_raw.get("choice_count") or 5),
            index=int(plan_raw.get("index") or 0),
            difficulty=int(plan_raw.get("difficulty") or 70),
        )
        stem = str(card.get("stem") or "")
        choices = {str(k): str(v) for k, v in (card.get("choices") or {}).items()}
        correct_key = str(card.get("correct_key") or "A").upper()

    slot = fingerprint_for_plan(plan, ctx)
    ch = card_content_hash(stem, choices, correct_key)
    return hashlib.sha256(f"{slot}|{ch}".encode("utf-8")).hexdigest()


class QuestionPoolService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_fingerprint(self, fingerprint: str) -> QuestionPoolCard | None:
        result = await self.db.execute(
            select(QuestionPoolCard).where(QuestionPoolCard.fingerprint == fingerprint)
        )
        return result.scalar_one_or_none()

    async def get_unused_for_topic(
        self,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty_band: str,
        exclude_stems: list[str] | None = None,
        limit: int = 10,
        target_asset_id: uuid.UUID | None = None,
    ) -> list[QuestionPoolCard]:
        q = (
            select(QuestionPoolCard)
            .where(
                QuestionPoolCard.exam == (exam or "").lower(),
                QuestionPoolCard.subject_code == subject_code,
                QuestionPoolCard.topic_code == topic_code,
                QuestionPoolCard.difficulty_band == (difficulty_band or "medium"),
            )
        )
        if target_asset_id:
            q = q.where(QuestionPoolCard.target_asset_id == target_asset_id)
            
        q = (
            q.order_by(QuestionPoolCard.use_count.asc(), QuestionPoolCard.created_at.asc())
            .limit(limit)
        )
        rows = list((await self.db.execute(q)).scalars().all())
        if not exclude_stems:
            return rows
        blocked = {s.strip().lower() for s in exclude_stems if s}
        return [r for r in rows if (r.stem or "").strip().lower() not in blocked]

    async def get_by_asset_id(
        self, target_asset_id: uuid.UUID, limit: int = 10
    ) -> list[QuestionPoolCard]:
        q = (
            select(QuestionPoolCard)
            .where(QuestionPoolCard.target_asset_id == target_asset_id)
            .order_by(QuestionPoolCard.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(q)).scalars().all())

    async def put_card(
        self,
        *,
        fingerprint: str,
        card: QuestionCard | dict[str, Any],
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty_band: str,
        skill: str = "",
        target_asset_id: uuid.UUID | None = None,
        correct_node_id: str | None = None,
    ) -> QuestionPoolCard:
        if isinstance(card, QuestionCard):
            stem = card.stem
            choices = dict(card.choices)
            correct_key = card.correct_key
            explanation = card.explanation
            qie_card = card.to_dict() if hasattr(card, "to_dict") else {}
        else:
            stem = str(card.get("stem") or "")
            choices = {str(k): str(v) for k, v in (card.get("choices") or {}).items()}
            correct_key = str(card.get("correct_key") or "A").upper()
            explanation = card.get("explanation")
            qie_card = dict(card.get("qie_card") or card)

        ch = card_content_hash(stem, choices, correct_key)

        # Exact content already in pool → reuse (do not inflate counts)
        dup = await self.db.execute(
            select(QuestionPoolCard).where(QuestionPoolCard.content_hash == ch)
        )
        hit = dup.scalar_one_or_none()
        if hit:
            logger.info(
                "pool put: content dedup topic=%s stem=%s...",
                topic_code,
                (stem or "")[:40],
            )
            return hit

        # Always store under plan-slot + content key.
        # Legacy callers pass plan-slot-only fingerprints (index 0..N); using that
        # alone made every subsequent batch silently skip inserts.
        content_fp = hashlib.sha256(f"{fingerprint}|{ch}".encode("utf-8")).hexdigest()
        existing = await self.get_by_fingerprint(content_fp)
        if existing is not None:
            return existing

        row = QuestionPoolCard(
            id=uuid.uuid4(),
            fingerprint=content_fp,
            content_hash=ch,
            exam=(exam or "").lower(),
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty_band or "medium",
            skill=skill or "",
            stem=stem,
            choices=choices,
            correct_key=correct_key,
            explanation=explanation,
            qie_card=qie_card or {},
            target_asset_id=target_asset_id,
            correct_node_id=correct_node_id,
            use_count=0,
            created_at=datetime.now(UTC),
        )
        self.db.add(row)
        await self.db.flush()
        logger.info(
            "pool put: inserted id=%s topic=%s exam=%s",
            row.id,
            topic_code,
            exam,
        )
        return row

    async def mark_used(self, card_id: uuid.UUID) -> None:
        await self.db.execute(
            update(QuestionPoolCard)
            .where(QuestionPoolCard.id == card_id)
            .values(use_count=QuestionPoolCard.use_count + 1)
        )

    def to_question_card(self, row: QuestionPoolCard, plan: QuestionPlan) -> QuestionCard:
        from app.services.qie.types import QualityBreakdown

        qie = row.qie_card or {}
        quality_raw = qie.get("quality") if isinstance(qie.get("quality"), dict) else {}
        quality = QualityBreakdown(
            style=int(quality_raw["style"]) if quality_raw.get("style") is not None else 80,
            difficulty=int(quality_raw["difficulty"]) if quality_raw.get("difficulty") is not None else 80,
            similarity=int(quality_raw["similarity"]) if quality_raw.get("similarity") is not None else 90,
            grammar=int(quality_raw["grammar"]) if quality_raw.get("grammar") is not None else 85,
            option_balance=int(quality_raw["option_balance"]) if quality_raw.get("option_balance") is not None else 85,
            distractor_quality=int(quality_raw["distractor_quality"]) if quality_raw.get("distractor_quality") is not None else 80,
            blueprint_match=int(quality_raw["blueprint_match"]) if quality_raw.get("blueprint_match") is not None else 80,
            reading_time=int(quality_raw["reading_time"]) if quality_raw.get("reading_time") is not None else 80,
            exam_feel=int(quality_raw["exam_feel"]) if quality_raw.get("exam_feel") is not None else 80,
        )
        try:
            difficulty_score = int(qie.get("difficulty_score") or plan.difficulty or 70)
        except (ValueError, TypeError):
            difficulty_score = 70
        return QuestionCard(
            stem=row.stem,
            choices=dict(row.choices or {}),
            correct_key=row.correct_key,
            explanation=row.explanation,
            plan=plan,
            difficulty_score=difficulty_score,
            quality=quality,
            style_score=int(qie.get("style_score") or quality.style),
            prompt_version=str(qie.get("prompt_version") or "pool_v1"),
            provider=str(qie.get("provider") or "pool"),
            model=qie.get("model"),
        )
