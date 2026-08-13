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

from app.core.constants import normalize_exam_code
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
            normalize_exam_code(exam or ""),
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
        pool_type: str = "general",
        max_fetch: int | None = None,
    ) -> list[QuestionPoolCard]:
        canonical_exam = normalize_exam_code(exam)
        q = (
            select(QuestionPoolCard)
            .where(
                QuestionPoolCard.exam == canonical_exam,
                QuestionPoolCard.subject_code == subject_code,
                QuestionPoolCard.topic_code == topic_code,
                QuestionPoolCard.difficulty_band == (difficulty_band or "medium"),
                QuestionPoolCard.pool_type == pool_type,
            )
        )
        if target_asset_id:
            q = q.where(QuestionPoolCard.target_asset_id == target_asset_id)

        fetch_n = max_fetch if max_fetch is not None else max(limit * 8, 24)
        q = (
            q.order_by(QuestionPoolCard.use_count.asc(), QuestionPoolCard.created_at.asc())
            .limit(fetch_n)
        )
        rows = list((await self.db.execute(q)).scalars().all())
        from app.services.correctness.apply import pool_row_is_quarantined
        from app.services.qie.skill_profiles import pool_row_compatible

        rows = [r for r in rows if not pool_row_is_quarantined(r)]
        compatible: list[QuestionPoolCard] = []
        for r in rows:
            if pool_row_compatible(
                r,
                exam=canonical_exam,
                subject_code=subject_code,
                topic_code=topic_code,
            ):
                compatible.append(r)
            else:
                logger.info(
                    "pool skip domain-incompatible id=%s exam=%s subject=%s topic=%s skill=%s",
                    getattr(r, "id", None),
                    canonical_exam,
                    subject_code,
                    topic_code,
                    getattr(r, "skill", None) or "",
                )
        rows = compatible
        if not exclude_stems:
            return rows[:limit]
        blocked = {s.strip().lower() for s in exclude_stems if s}
        return [r for r in rows if (r.stem or "").strip().lower() not in blocked][:limit]

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
        pool_type: str = "general",
    ) -> QuestionPoolCard:
        if isinstance(card, QuestionCard):
            stem = card.stem
            choices = dict(card.choices)
            correct_key = card.correct_key
            explanation = card.explanation
            qie_card = card.to_persist_dict()
        else:
            stem = str(card.get("stem") or "")
            choices = {str(k): str(v) for k, v in (card.get("choices") or {}).items()}
            correct_key = str(card.get("correct_key") or "A").upper()
            explanation = card.get("explanation")
            qie_card = dict(card.get("qie_card") or card)

        corr_meta = qie_card.get("correctness") if isinstance(qie_card, dict) else None
        if isinstance(corr_meta, dict) and str(corr_meta.get("verdict") or "").lower() == "fail":
            logger.warning(
                "pool put refused: correctness fail topic=%s stem=%s...",
                topic_code,
                (stem or "")[:40],
            )
            raise ValueError("correctness_fail_not_pooled")

        stem_type = ""
        if isinstance(qie_card, dict):
            stem_type = str(qie_card.get("stem_type") or "")
            plan_raw = qie_card.get("plan")
            if not stem_type and isinstance(plan_raw, dict):
                stem_type = str(plan_raw.get("stem_type") or "")
        from app.services.qie.skill_profiles import pool_card_compatible

        if not pool_card_compatible(
            exam=exam,
            subject_code=subject_code,
            topic_code=topic_code,
            skill=skill,
            stem_type=stem_type,
        ):
            logger.info(
                "pool put refused: domain_incompatible exam=%s subject=%s topic=%s skill=%s stem_type=%s",
                exam,
                subject_code,
                topic_code,
                skill,
                stem_type,
            )
            raise ValueError("domain_incompatible_not_pooled")

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

        canonical_exam = normalize_exam_code(exam)
        row = QuestionPoolCard(
            id=uuid.uuid4(),
            fingerprint=content_fp,
            content_hash=ch,
            exam=canonical_exam,
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=(difficulty_band or "medium"),
            skill=skill,
            stem=stem,
            choices=choices,
            correct_key=correct_key,
            explanation=explanation,
            qie_card=qie_card,
            target_asset_id=target_asset_id,
            correct_node_id=correct_node_id,
            pool_type=pool_type,
            use_count=0,
            created_at=datetime.now(UTC),
        )
        self.db.add(row)
        await self.db.flush()
        logger.info(
            "pool put: inserted id=%s topic=%s exam=%s",
            row.id,
            topic_code,
            canonical_exam,
        )
        return row

    async def update_correctness_metadata(
        self, row: QuestionPoolCard, meta: dict[str, Any]
    ) -> None:
        qie = dict(row.qie_card or {})
        qie["correctness"] = dict(meta or {})
        row.qie_card = qie
        await self.db.flush()

    async def mark_quarantined(
        self, row: QuestionPoolCard, *, reason: str | None = None
    ) -> None:
        from app.services.correctness.constants import CORRECTNESS_VERSION

        qie = dict(row.qie_card or {})
        corr = dict(qie.get("correctness") or {})
        corr["version"] = corr.get("version") or CORRECTNESS_VERSION
        corr["verdict"] = "fail"
        corr["quarantined"] = True
        if reason:
            corr["reason"] = reason
        qie["correctness"] = corr
        row.qie_card = qie
        await self.db.flush()
        logger.info(
            "pool quarantine id=%s topic=%s reason=%s",
            row.id,
            row.topic_code,
            reason or "-",
        )

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
        corr = qie.get("correctness") if isinstance(qie.get("correctness"), dict) else None
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
            correctness_meta=corr,
        )

    async def try_serve_row(
        self, row: QuestionPoolCard, plan: QuestionPlan
    ) -> QuestionCard | None:
        """Serve-time correctness. None → skip/quarantine (caller falls back to fresh).

        Does not run M34. Does not increment use_count.
        """
        from app.services.correctness.apply import (
            attach_correctness_meta,
            evaluate_pool_row_correctness,
            pool_row_can_skip_recheck,
            pool_row_is_quarantined,
        )

        if pool_row_is_quarantined(row):
            return None
        from app.services.qie.skill_profiles import pool_row_compatible

        if not pool_row_compatible(
            row,
            exam=getattr(plan, "exam", None),
            subject_code=getattr(plan, "subject_code", None),
            topic_code=getattr(plan, "topic_code", None),
            topic_name=getattr(plan, "topic_name", None),
        ):
            logger.info(
                "pool serve skip domain-incompatible id=%s exam=%s subject=%s topic=%s skill=%s",
                getattr(row, "id", None),
                getattr(plan, "exam", None),
                getattr(plan, "subject_code", None),
                getattr(plan, "topic_code", None),
                getattr(row, "skill", None) or "",
            )
            return None
        if pool_row_can_skip_recheck(row):
            return self.to_question_card(row, plan)

        corr = evaluate_pool_row_correctness(row, mode="serve")
        if not corr.passed:
            await self.mark_quarantined(row, reason=corr.reason)
            return None
        from app.services.correctness.constants import requires_verified_correctness
        from app.services.correctness.types import CorrectnessVerdict

        if (
            corr.verdict == CorrectnessVerdict.UNSUPPORTED
            and requires_verified_correctness(plan=plan)
        ):
            logger.info(
                "pool serve skip stem_unsupported id=%s exam=%s subject=%s topic=%s",
                getattr(row, "id", None),
                getattr(plan, "exam", None),
                getattr(plan, "subject_code", None),
                getattr(plan, "topic_code", None),
            )
            return None
        await self.update_correctness_metadata(row, corr.to_metadata())
        card = self.to_question_card(row, plan)
        attach_correctness_meta(card, corr)
        return card

    def _plan_for_pool_row(
        self,
        row: QuestionPoolCard,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
    ) -> QuestionPlan:
        return QuestionPlan(
            exam=str(getattr(row, "exam", None) or exam),
            subject_code=str(getattr(row, "subject_code", None) or subject_code),
            subject_name=str(getattr(row, "subject_code", None) or subject_code),
            topic_code=str(getattr(row, "topic_code", None) or topic_code),
            topic_name=str(getattr(row, "topic_code", None) or topic_code),
            skill=str(getattr(row, "skill", None) or ""),
        )

    async def serve_unused_for_topic(
        self,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty_band: str,
        exclude_stems: list[str] | None = None,
        limit: int = 10,
        target_asset_id: uuid.UUID | None = None,
        pool_type: str = "general",
        mark_used: bool = True,
    ) -> list[QuestionCard]:
        """Booklet/pool-hit serve: candidates → correctness → skip FAIL → use_count on serve.

        Does not change get_unused_for_topic's default contract. One FAIL candidate
        does not discard later PASS/UNSUPPORTED rows in the same topic batch.
        """
        if limit <= 0:
            return []
        fetch_n = max(int(limit) * 8, 24)
        candidates = await self.get_unused_for_topic(
            exam=exam,
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty_band,
            exclude_stems=exclude_stems,
            limit=fetch_n,
            target_asset_id=target_asset_id,
            pool_type=pool_type,
            max_fetch=fetch_n,
        )
        served: list[QuestionCard] = []
        blocked = {s.strip().lower() for s in (exclude_stems or []) if s}
        for row in candidates:
            if len(served) >= limit:
                break
            stem_l = (getattr(row, "stem", None) or "").strip().lower()
            if stem_l and stem_l in blocked:
                continue
            plan = self._plan_for_pool_row(
                row, exam=exam, subject_code=subject_code, topic_code=topic_code
            )
            card = await self.try_serve_row(row, plan)
            if card is None:
                continue
            if mark_used:
                await self.mark_used(row.id)
            served.append(card)
            if stem_l:
                blocked.add(stem_l)
        return served

