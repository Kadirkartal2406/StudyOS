"""M32 P2 — Question Pool (DB cache; identical fingerprint → reuse)."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_pool import QuestionPoolCard
from app.services.qie.types import GenerateContext, QuestionCard, QuestionPlan


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
    ) -> list[QuestionPoolCard]:
        q = (
            select(QuestionPoolCard)
            .where(
                QuestionPoolCard.exam == exam.lower(),
                QuestionPoolCard.subject_code == subject_code,
                QuestionPoolCard.topic_code == topic_code,
                QuestionPoolCard.difficulty_band == (difficulty_band or "medium"),
            )
            .order_by(QuestionPoolCard.use_count.asc(), QuestionPoolCard.created_at.asc())
            .limit(limit)
        )
        rows = list((await self.db.execute(q)).scalars().all())
        if not exclude_stems:
            return rows
        blocked = {s.strip().lower() for s in exclude_stems if s}
        return [r for r in rows if (r.stem or "").strip().lower() not in blocked]

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

        existing = await self.get_by_fingerprint(fingerprint)
        if existing:
            existing.use_count = int(existing.use_count or 0)
            return existing

        # Also skip exact duplicate content under another fingerprint
        ch = card_content_hash(stem, choices, correct_key)
        dup = await self.db.execute(
            select(QuestionPoolCard).where(QuestionPoolCard.content_hash == ch)
        )
        hit = dup.scalar_one_or_none()
        if hit:
            return hit

        row = QuestionPoolCard(
            id=uuid.uuid4(),
            fingerprint=fingerprint,
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
            use_count=0,
            created_at=datetime.now(UTC),
        )
        self.db.add(row)
        await self.db.flush()
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
            style=int(quality_raw.get("style") or 80),
            difficulty=int(quality_raw.get("difficulty") or 80),
            similarity=int(quality_raw.get("similarity") or 90),
            grammar=int(quality_raw.get("grammar") or 85),
            option_balance=int(quality_raw.get("option_balance") or 85),
            distractor_quality=int(quality_raw.get("distractor_quality") or 80),
            blueprint_match=int(quality_raw.get("blueprint_match") or 80),
            reading_time=int(quality_raw.get("reading_time") or 80),
            exam_feel=int(quality_raw.get("exam_feel") or 80),
        )
        return QuestionCard(
            stem=row.stem,
            choices=dict(row.choices or {}),
            correct_key=row.correct_key,
            explanation=row.explanation,
            plan=plan,
            difficulty_score=int(qie.get("difficulty_score") or plan.difficulty or 70),
            quality=quality,
            style_score=int(qie.get("style_score") or quality.style),
            prompt_version=str(qie.get("prompt_version") or "pool_v1"),
            provider=str(qie.get("provider") or "pool"),
            model=qie.get("model"),
        )
