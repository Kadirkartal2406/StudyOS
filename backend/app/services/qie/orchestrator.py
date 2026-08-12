"""QIE Orchestrator — plan → Question Author (M29) → gates → QuestionCard.

Frozen: Blueprint planner, Difficulty, Similarity, Quality Gate modules.
M29 adds a thin Author path before those gates (no engine rewrites).
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.ai.base import GenerateRequest, GenerateResult, generate_with_fallback
from app.services.ai.quiz_quality_gate import (
    ValidatedQuizItem,
    extract_json_payload,
    validate_quiz_payload,
)
from app.services.correctness.apply import (
    attach_correctness_meta,
    evaluate_item_correctness,
)
from app.services.qie.difficulty_analyzer import analyze_for_plan
from app.services.qie.planner import QuestionPlanner
from app.services.qie.prompt_builder_v3 import build_qie_messages
from app.services.qie.quality_gate_v2 import passes_quality_gate, score_quality
from app.services.qie.question_card import build_card
from app.services.qie.similarity import is_similar_question
from app.services.qie.style_intelligence import StyleIntelligence
from app.services.qie.types import (
    MAX_REGENERATE,
    MIN_DIFFICULTY_SCORE,
    GenerateContext,
    QuestionCard,
    QuestionPlan,
)

logger = logging.getLogger("studyos.qie")


def _apply_measurement_to_card(
    card: QuestionCard,
    *,
    contract,
    retry_count: int = 0,
) -> tuple[QuestionCard, bool, bool]:
    """Attach measurement_meta. Returns (card, accept_into_batch, should_regen)."""
    from app.services.ai.measurement_integration import (
        allow_autopool_from_meta,
        apply_soft_measurement,
        measurement_meta_payload,
    )
    from app.services.ai_cost.measurement_flags import measurement_mode, measurement_soft_review

    score, decision = apply_soft_measurement(
        stem=card.stem,
        choices=card.choices,
        quality_passed=True,
        contract=contract,
        retry_count=retry_count,
        subject=card.plan.subject_code,
        topic=card.plan.topic_code,
    )
    card.measurement_meta = measurement_meta_payload(score, decision)
    if measurement_mode() == "off":
        return card, True, False
    if decision.should_regen and measurement_soft_review():
        return card, False, True
    if measurement_soft_review() and not allow_autopool_from_meta(card.measurement_meta):
        logger.info(
            "measurement_review_hold plan_index=%s — excluding from accepted",
            card.plan.index,
        )
        return card, False, False
    return card, True, False


def _correctness_or_reject(
    item: ValidatedQuizItem, plan: QuestionPlan, *, log_pass: bool = True
):
    """Shared gate. None → hard reject (FAIL). Result → PASS or UNSUPPORTED."""
    corr = evaluate_item_correctness(item, plan, log_pass=log_pass)
    if not corr.passed:
        return None
    return corr


def _item_from_m34(m34: dict[str, Any], item: ValidatedQuizItem) -> ValidatedQuizItem:
    q2 = m34.get("question") or {
        "stem": item.stem,
        "choices": item.choices,
        "correct_key": item.correct_key,
        "explanation": item.explanation,
    }
    return ValidatedQuizItem(
        stem=str(q2.get("stem") or ""),
        choices=dict(q2.get("choices") or {}),
        correct_key=str(q2.get("correct_key") or item.correct_key).upper(),
        explanation=q2.get("explanation"),
    )


class QieOrchestrator:
    def __init__(self, db: AsyncSession, *, use_question_author: bool = True) -> None:
        self.db = db
        self.style = StyleIntelligence(db)
        self.planner = QuestionPlanner()
        self.use_question_author = use_question_author

    async def generate_batch(
        self, ctx: GenerateContext
    ) -> tuple[list[QuestionCard], str, GenerateResult | None]:
        """
        Returns (cards, prompt_fingerprint, last_llm_result).
        Cards are quality-passed only.
        M32: pool hit → return; miss → single-flight dedup → Author/compact → pool put.
        """
        from app.services.ai_cost.cost_logger import AiCostEvent, get_cost_logger
        from app.services.ai_cost.dedup import get_deduplicator
        from app.services.ai_cost.flags import compact_author_enabled, pool_only_mode
        from app.services.ai_cost.metrics import get_metrics
        from app.services.ai_cost.pool import QuestionPoolService, fingerprint_for_plan

        dna = await self.style.dna(
            ctx.exam,
            subject_code=ctx.subject_code,
            difficulty=ctx.difficulty_band,
        )
        if ctx.style_override:
            dna = {**dna, **ctx.style_override}
        if ctx.choice_count:
            dna["choice_count"] = ctx.choice_count

        from app.services.ai.measurement_integration import (
            inject_measurement_into_style,
            load_contract_for_context,
            prompt_block_from_contract,
        )

        measurement_contract = load_contract_for_context(
            exam=ctx.exam,
            subject_code=ctx.subject_code,
            topic_code=ctx.topic_code,
        )
        measurement_block = prompt_block_from_contract(measurement_contract)
        ctx.measurement_contract_block = measurement_block
        dna = inject_measurement_into_style(dna, measurement_contract)

        plans = self.planner.plan_batch(ctx, style=dna)
        if not plans:
            return [], "", None

        pool = QuestionPoolService(self.db)
        metrics = get_metrics()
        accepted: list[QuestionCard] = []
        remaining: list[QuestionPlan] = []
        existing = list(ctx.existing_stems)

        for plan in plans:
            # Primary retrieval: topic-based, ranked by usage count + recency.
            # Slot-fingerprint lookup is intentionally omitted: put_card stores
            # cards under content_fp = sha256(slot|content_hash), not the bare
            # slot fingerprint, so get_by_fingerprint(slot_fp) always misses.
            reused = await pool.get_unused_for_topic(
                exam=ctx.exam,
                subject_code=ctx.subject_code,
                topic_code=ctx.topic_code,
                difficulty_band=ctx.difficulty_band,
                exclude_stems=existing,
                limit=1,
                pool_type=ctx.pool_type,
            )
            if reused:
                served = await pool.try_serve_row(reused[0], plan)
                if served is None:
                    metrics.record_pool_miss()
                    remaining.append(plan)
                    continue
                metrics.record_pool_hit()
                accepted.append(served)
                existing.append(served.stem)
                await pool.mark_used(reused[0].id)
                get_cost_logger().record(
                    AiCostEvent(
                        timestamp=__import__("datetime")
                        .datetime.now(__import__("datetime").UTC)
                        .isoformat(),
                        module="question_pool",
                        model=None,
                        duration_ms=0.0,
                        cache_hit=True,
                        provider="pool",
                        kind=ctx.kind,
                        success=True,
                    )
                )
            else:
                metrics.record_pool_miss()
                remaining.append(plan)

        if not remaining:
            _, fingerprint = build_qie_messages(plans, style_dna=dna)
            return accepted[: len(plans)], f"pool:{fingerprint[:24]}", None

        if pool_only_mode():
            metrics.record_budget_block()
            logger.warning("M32 pool-only mode — cannot generate remaining=%s", len(remaining))
            _, fingerprint = build_qie_messages(plans, style_dna=dna)
            return accepted[: len(plans)], f"pool_only:{fingerprint[:24]}", None

        dedup_key = "|".join(
            [
                ctx.exam,
                ctx.subject_code,
                ctx.topic_code,
                ctx.difficulty_band,
                str(len(remaining)),
                ",".join(sorted({p.skill for p in remaining})),
            ]
        )

        async def _produce() -> tuple[list[QuestionCard], str, GenerateResult | None]:
            # Prefer compact author (1 LLM / question) when enabled
            if self.use_question_author and compact_author_enabled():
                try:
                    from app.services.ai_cost.compact_author import (
                        author_batch_compact,
                        author_one_compact,
                    )
                    from app.services.question_review import QuestionReviewEngine
                    from app.services.question_virtual_student import VirtualStudentEngine

                    metrics.record_compact()
                    metrics.record_author()
                    authored = await author_batch_compact(
                        remaining,
                        ctx=ctx,
                        measurement_contract_block=measurement_block,
                    )
                    local_accepted: list[QuestionCard] = []
                    stems = list(existing)
                    opts: list[dict[str, str]] = []
                    keys: list[str] = []
                    reviewer = QuestionReviewEngine()
                    last: GenerateResult | None = None
                    plan_by_index = {p.index: p for p in remaining}
                    for aq in authored:
                        plan = plan_by_index.get(aq.author_plan.qie_plan_index) or remaining[0]
                        item = ValidatedQuizItem(
                            stem=aq.stem,
                            choices=dict(aq.choices),
                            correct_key=aq.correct_key,
                            explanation=aq.explanation,
                        )
                        corr = _correctness_or_reject(item, plan)
                        if corr is None:
                            continue
                        review = reviewer.review(
                            aq, recent_stems=stems, recent_correct_keys=keys, rewrite_used=0
                        )
                        if not review.passed:
                            continue
                        vsse = VirtualStudentEngine().simulate(aq, review_bounce_used=0)
                        if not vsse.passed:
                            continue

                        # NEW: M34 question intelligence layer (Blueprint/ExamFeel/etc)
                        from app.services.question_intelligence.pipeline import (
                            evaluate_question as m34_evaluate_question,
                        )

                        qdict = {
                            "stem": item.stem,
                            "choices": item.choices,
                            "correct_key": item.correct_key,
                            "explanation": item.explanation,
                        }
                        m34 = m34_evaluate_question(
                            qdict,
                            plan.to_dict(),
                            dna,
                            existing_stems=stems,
                            allow_repair=True,
                        )
                        if not m34.get("accepted"):
                            continue
                        item = _item_from_m34(m34, item)
                        corr = _correctness_or_reject(item, plan, log_pass=False)
                        if corr is None:
                            continue

                        diff = analyze_for_plan(item, plan, style=dna)
                        if diff.score < MIN_DIFFICULTY_SCORE:
                            continue
                        quality = score_quality(
                            item,
                            plan,
                            difficulty_score=diff.score,
                            existing_stems=stems,
                            style_dna=dna,
                        )
                        if not passes_quality_gate(quality):
                            continue

                        # Frozen similarity gate (runs after M34 + frozen quality gate)
                        if is_similar_question(
                            item, existing_stems=stems, existing_option_sets=opts
                        ):
                            continue
                        card = build_card(
                            item,
                            plan,
                            difficulty_score=diff.score,
                            quality=quality,
                            style_score=quality.style,
                            provider=aq.provider,
                            model=aq.model,
                        )
                        attach_correctness_meta(card, corr)
                        retry = 0
                        card, accept, need_regen = _apply_measurement_to_card(
                            card, contract=measurement_contract, retry_count=retry
                        )
                        if need_regen:
                            try:
                                aq_r = await author_one_compact(
                                    plan,
                                    preferred=ctx.preferred_provider,
                                    model=ctx.preferred_model,
                                    measurement_contract_block=measurement_block,
                                )
                                item_r = ValidatedQuizItem(
                                    stem=aq_r.stem,
                                    choices=dict(aq_r.choices),
                                    correct_key=aq_r.correct_key,
                                    explanation=aq_r.explanation,
                                )
                                corr_r = _correctness_or_reject(item_r, plan)
                                if corr_r is None:
                                    accept = False
                                else:
                                    diff_r = analyze_for_plan(item_r, plan, style=dna)
                                    if diff_r.score >= MIN_DIFFICULTY_SCORE:
                                        quality_r = score_quality(
                                            item_r,
                                            plan,
                                            difficulty_score=diff_r.score,
                                            existing_stems=stems,
                                            style_dna=dna,
                                        )
                                        if passes_quality_gate(quality_r) and not is_similar_question(
                                            item_r, existing_stems=stems, existing_option_sets=opts
                                        ):
                                            card = build_card(
                                                item_r,
                                                plan,
                                                difficulty_score=diff_r.score,
                                                quality=quality_r,
                                                style_score=quality_r.style,
                                                provider=aq_r.provider,
                                                model=aq_r.model,
                                            )
                                            attach_correctness_meta(card, corr_r)
                                            retry = 1
                                            card, accept, _ = _apply_measurement_to_card(
                                                card,
                                                contract=measurement_contract,
                                                retry_count=retry,
                                            )
                                        else:
                                            accept = False
                                    else:
                                        accept = False
                            except Exception as e:
                                logger.info("measurement compact regen failed: %s", e)
                                card, accept, _ = _apply_measurement_to_card(
                                    card,
                                    contract=measurement_contract,
                                    retry_count=1,
                                )
                        if not accept:
                            continue
                        local_accepted.append(card)
                        stems.append(card.stem)
                        opts.append(card.choices)
                        keys.append(card.correct_key)
                        last = GenerateResult(
                            text="compact_author",
                            provider=aq.provider or "compact",
                            model=aq.model,
                        )
                    if local_accepted:
                        _, fp = build_qie_messages(plans, style_dna=dna)
                        return local_accepted, f"m32_compact:{fp[:24]}", last
                except Exception as e:
                    logger.warning("M32 compact author failed; falling back: %s", e)

            # Existing Author path (frozen) then legacy QIE
            if self.use_question_author:
                try:
                    metrics.record_author()
                    cards, fingerprint, last = await self._generate_via_author(
                        ctx,
                        plans=remaining,
                        dna=dna,
                        measurement_contract=measurement_contract,
                    )
                    if cards:
                        return cards, fingerprint, last
                    logger.warning(
                        "Question Author produced 0 cards; falling back to QIE v3"
                    )
                except Exception as e:
                    logger.warning(
                        "Question Author path failed; falling back to QIE v3: %s", e
                    )

            return await self._generate_via_legacy_llm(
                ctx,
                plans=remaining,
                dna=dna,
                existing=existing,
                measurement_contract=measurement_contract,
            )

        produced, fingerprint, last_result = await get_deduplicator().do(
            dedup_key, _produce
        )

        for card in produced:
            from app.services.ai.measurement_integration import allow_autopool_from_meta
            from app.services.ai_cost.measurement_flags import measurement_soft_review

            if measurement_soft_review() and not allow_autopool_from_meta(
                getattr(card, "measurement_meta", None)
            ):
                logger.info(
                    "skip pool put for measurement_review_hold plan_index=%s",
                    card.plan.index,
                )
                continue
            try:
                await pool.put_card(
                    fingerprint=fingerprint_for_plan(card.plan, ctx),
                    card=card,
                    exam=ctx.exam,
                    subject_code=card.plan.subject_code or ctx.subject_code,
                    topic_code=card.plan.topic_code or ctx.topic_code,
                    difficulty_band=ctx.difficulty_band,
                    skill=card.plan.skill or "",
                    pool_type=ctx.pool_type,
                )
            except Exception as e:
                logger.warning("pool put skipped: %s", e)
            if card.stem not in {c.stem for c in accepted}:
                accepted.append(card)

        accepted.sort(key=lambda c: c.plan.index)
        return accepted[: len(plans)], fingerprint, last_result

    async def _generate_via_legacy_llm(
        self,
        ctx: GenerateContext,
        *,
        plans: list[QuestionPlan],
        dna: dict[str, Any],
        existing: list[str],
        measurement_contract: Any = None,
    ) -> tuple[list[QuestionCard], str, GenerateResult | None]:
        messages, fingerprint = build_qie_messages(plans, style_dna=dna)
        accepted: list[QuestionCard] = []
        existing_stems = list(existing)
        existing_opts: list[dict[str, str]] = []
        last_result: GenerateResult | None = None

        for attempt in range(MAX_REGENERATE + 1):
            still_needed = [
                p for p in plans if not any(c.plan.index == p.index for c in accepted)
            ]
            if not still_needed and accepted:
                break
            use_plans = still_needed or plans
            messages, fingerprint = build_qie_messages(use_plans, style_dna=dna)
            try:
                result = await generate_with_fallback(
                    GenerateRequest(
                        messages=messages,
                        context={
                            "kind": ctx.kind or "qie",
                            "exam": ctx.exam,
                            "subject_code": ctx.subject_code,
                            "topic_code": ctx.topic_code,
                            "count": len(use_plans),
                            "attempt": attempt,
                            "qie": True,
                            "api_key_override": ctx.api_key_override,
                        },
                    ),
                    preferred=ctx.preferred_provider,
                    model=ctx.preferred_model,
                )
                last_result = result
            except Exception as e:
                logger.warning("QIE LLM failed attempt=%s: %s", attempt, e)
                continue

            cards = self._process_llm_payload(
                result,
                plans=use_plans,
                dna=dna,
                existing_stems=existing_stems,
                existing_opts=existing_opts,
                measurement_contract=measurement_contract,
            )
            for card in cards:
                if any(c.plan.index == card.plan.index for c in accepted):
                    continue
                accepted.append(card)
                existing_stems.append(card.stem)
                existing_opts.append(card.choices)

            if len(accepted) >= len(plans):
                break

        accepted.sort(key=lambda c: c.plan.index)
        return accepted[: len(plans)], fingerprint, last_result

    async def _generate_via_author(
        self,
        ctx: GenerateContext,
        *,
        plans: list[QuestionPlan],
        dna: dict[str, Any],
        measurement_contract: Any = None,
    ) -> tuple[list[QuestionCard], str, GenerateResult | None]:
        from app.services.question_author import QuestionAuthorEngine
        from app.services.question_review import QuestionReviewEngine

        author = QuestionAuthorEngine(use_llm=True)
        reviewer = QuestionReviewEngine()
        authored = await author.author_batch(plans, ctx=ctx)
        existing = list(ctx.existing_stems)
        existing_opts: list[dict[str, str]] = []
        accepted: list[QuestionCard] = []
        last_result: GenerateResult | None = None
        recent_keys: list[str] = []

        plan_by_index = {p.index: p for p in plans}
        for aq in authored:
            plan = plan_by_index.get(aq.author_plan.qie_plan_index) or plans[0]

            item0 = ValidatedQuizItem(
                stem=aq.stem,
                choices=dict(aq.choices),
                correct_key=aq.correct_key,
                explanation=aq.explanation,
            )
            if _correctness_or_reject(item0, plan) is None:
                continue

            # M30 chief editor — never generates; may request one Author rewrite
            review = reviewer.review(
                aq,
                recent_stems=existing,
                recent_correct_keys=recent_keys,
                rewrite_used=0,
            )
            if not review.passed:
                try:
                    aq2 = await author.author_one(
                        plan,
                        preferred=ctx.preferred_provider,
                        model=ctx.preferred_model,
                        calibration=ctx.kind == "calibration",
                    )
                    if not aq2.rejected:
                        review2 = reviewer.review(
                            aq2,
                            recent_stems=existing,
                            recent_correct_keys=recent_keys,
                            rewrite_used=1,
                        )
                        if review2.passed:
                            aq = aq2
                            review = review2
                        else:
                            continue
                    else:
                        continue
                except Exception as e:
                    logger.info("Review rewrite skipped: %s", e)
                    continue

            # M31 Virtual Student — solve-as-student; may bounce to Review once
            from app.services.question_virtual_student import VirtualStudentEngine

            vsse = VirtualStudentEngine().simulate(aq, review_bounce_used=0)
            if not vsse.passed:
                try:
                    review_b = reviewer.review(
                        aq,
                        recent_stems=existing,
                        recent_correct_keys=recent_keys,
                        rewrite_used=getattr(review, "rewrite_used", 0),
                    )
                    if review_b.passed:
                        vsse2 = VirtualStudentEngine().simulate(
                            aq, review_bounce_used=1
                        )
                        if vsse2.passed:
                            vsse = vsse2
                            review = review_b
                        else:
                            continue
                    else:
                        continue
                except Exception as e:
                    logger.info("VSSE review bounce skipped: %s", e)
                    continue

            item = ValidatedQuizItem(
                stem=aq.stem,
                choices=dict(aq.choices),
                correct_key=aq.correct_key,
                explanation=aq.explanation,
            )
            corr = _correctness_or_reject(item, plan)
            if corr is None:
                continue

            # NEW: M34 question intelligence layer (Blueprint/ExamFeel/etc)
            from app.services.question_intelligence.pipeline import (
                evaluate_question as m34_evaluate_question,
            )

            qdict = {
                "stem": item.stem,
                "choices": item.choices,
                "correct_key": item.correct_key,
                "explanation": item.explanation,
            }
            m34 = m34_evaluate_question(
                qdict,
                plan.to_dict(),
                dna,
                existing_stems=existing,
                allow_repair=True,
            )
            if not m34.get("accepted"):
                continue
            item = _item_from_m34(m34, item)
            corr = _correctness_or_reject(item, plan, log_pass=False)
            if corr is None:
                continue

            diff = analyze_for_plan(item, plan, style=dna)
            if diff.score < MIN_DIFFICULTY_SCORE:
                continue
            quality = score_quality(
                item,
                plan,
                difficulty_score=diff.score,
                existing_stems=existing,
                style_dna=dna,
            )
            # Prefer author critic style signal when available
            if aq.style_score:
                quality.style = max(quality.style, min(100, aq.style_score))
            if not passes_quality_gate(quality):
                continue

            # Frozen similarity gate (runs after M34 + frozen quality gate)
            if is_similar_question(
                item,
                existing_stems=existing,
                existing_option_sets=existing_opts,
            ):
                continue
            card = build_card(
                item,
                plan,
                difficulty_score=diff.score,
                quality=quality,
                style_score=quality.style,
                provider=aq.provider,
                model=aq.model,
            )
            attach_correctness_meta(card, corr)
            setattr(card, "author_meta", aq.internal_metadata())
            setattr(card, "review_meta", review.internal_metadata())
            setattr(card, "vsse_meta", vsse.internal_metadata())
            card, accept, need_regen = _apply_measurement_to_card(
                card, contract=measurement_contract, retry_count=0
            )
            if need_regen:
                try:
                    aq_r = await author.author_one(
                        plan,
                        preferred=ctx.preferred_provider,
                        model=ctx.preferred_model,
                        calibration=ctx.kind == "calibration",
                    )
                    if not aq_r.rejected:
                        item_r = ValidatedQuizItem(
                            stem=aq_r.stem,
                            choices=dict(aq_r.choices),
                            correct_key=aq_r.correct_key,
                            explanation=aq_r.explanation,
                        )
                        corr_r = _correctness_or_reject(item_r, plan)
                        if corr_r is None:
                            accept = False
                        else:
                            diff_r = analyze_for_plan(item_r, plan, style=dna)
                            if diff_r.score >= MIN_DIFFICULTY_SCORE:
                                quality_r = score_quality(
                                    item_r,
                                    plan,
                                    difficulty_score=diff_r.score,
                                    existing_stems=existing,
                                    style_dna=dna,
                                )
                                if passes_quality_gate(quality_r):
                                    card = build_card(
                                        item_r,
                                        plan,
                                        difficulty_score=diff_r.score,
                                        quality=quality_r,
                                        style_score=quality_r.style,
                                        provider=aq_r.provider,
                                        model=aq_r.model,
                                    )
                                    attach_correctness_meta(card, corr_r)
                                    card, accept, _ = _apply_measurement_to_card(
                                        card,
                                        contract=measurement_contract,
                                        retry_count=1,
                                    )
                                else:
                                    accept = False
                            else:
                                accept = False
                    else:
                        accept = False
                except Exception as e:
                    logger.info("measurement author regen failed: %s", e)
                    card, accept, _ = _apply_measurement_to_card(
                        card, contract=measurement_contract, retry_count=1
                    )
            if not accept:
                continue
            accepted.append(card)
            existing.append(card.stem)
            existing_opts.append(card.choices)
            recent_keys.append(card.correct_key)
            last_result = GenerateResult(
                text="author_review_vsse_pipeline",
                provider=aq.provider or "question_author",
                model=aq.model,
            )

        _, fingerprint = build_qie_messages(plans, style_dna=dna)
        fingerprint = f"m31_vsse:{fingerprint[:24]}"
        accepted.sort(key=lambda c: c.plan.index)
        return accepted[: len(plans)], fingerprint, last_result

    def _process_llm_payload(
        self,
        result: GenerateResult,
        *,
        plans: list[QuestionPlan],
        dna: dict[str, Any],
        existing_stems: list[str],
        existing_opts: list[dict[str, str]],
        measurement_contract: Any = None,
    ) -> list[QuestionCard]:
        try:
            payload = extract_json_payload(result.text)
        except Exception:
            return []

        choice_count = plans[0].choice_count if plans else 5
        gate = validate_quiz_payload(
            payload,
            topic_name=plans[0].topic_name if plans else None,
            expected_count=len(plans),
            choice_count=choice_count,
            max_stem=2500,
        )
        if not gate.valid:
            return []

        # Optional plan_index from raw payload
        raw_questions = payload.get("questions") if isinstance(payload, dict) else payload
        index_hints: list[int | None] = []
        if isinstance(raw_questions, list):
            for raw in raw_questions:
                if isinstance(raw, dict) and "plan_index" in raw:
                    try:
                        index_hints.append(int(raw["plan_index"]))
                    except Exception:
                        index_hints.append(None)
                else:
                    index_hints.append(None)

        out: list[QuestionCard] = []
        for i, item in enumerate(gate.valid):
            plan = self._match_plan(plans, i, index_hints[i] if i < len(index_hints) else None)
            if plan is None:
                continue

            corr = _correctness_or_reject(item, plan)
            if corr is None:
                continue

            # NEW: M34 question intelligence layer (Blueprint/ExamFeel/etc)
            from app.services.question_intelligence.pipeline import (
                evaluate_question as m34_evaluate_question,
            )

            qdict = {
                "stem": item.stem,
                "choices": item.choices,
                "correct_key": item.correct_key,
                "explanation": item.explanation,
            }
            m34 = m34_evaluate_question(
                qdict,
                plan.to_dict(),
                dna,
                existing_stems=existing_stems,
                allow_repair=True,
            )
            if not m34.get("accepted"):
                continue
            item = _item_from_m34(m34, item)
            corr = _correctness_or_reject(item, plan, log_pass=False)
            if corr is None:
                continue

            diff = analyze_for_plan(item, plan, style=dna)
            if diff.score < MIN_DIFFICULTY_SCORE:
                continue
            quality = score_quality(
                item,
                plan,
                difficulty_score=diff.score,
                existing_stems=existing_stems,
                style_dna=dna,
            )
            if not passes_quality_gate(quality):
                continue

            # Frozen similarity gate (runs after M34 + frozen quality gate)
            if is_similar_question(
                item,
                existing_stems=existing_stems,
                existing_option_sets=existing_opts,
            ):
                continue
            card = build_card(
                item,
                plan,
                difficulty_score=diff.score,
                quality=quality,
                style_score=quality.style,
                provider=result.provider,
                model=result.model,
            )
            attach_correctness_meta(card, corr)
            card, accept, _ = _apply_measurement_to_card(
                card, contract=measurement_contract, retry_count=0
            )
            if not accept:
                continue
            out.append(card)
        return out

    def _match_plan(
        self,
        plans: list[QuestionPlan],
        seq: int,
        hint: int | None,
    ) -> QuestionPlan | None:
        if hint is not None:
            for p in plans:
                if p.index == hint:
                    return p
        if 0 <= seq < len(plans):
            return plans[seq]
        return plans[0] if plans else None

    async def generate_validated_items(
        self, ctx: GenerateContext
    ) -> list[ValidatedQuizItem]:
        """Adapter for booklet path that expects ValidatedQuizItem."""
        cards, _, _ = await self.generate_batch(ctx)
        return [
            ValidatedQuizItem(
                stem=c.stem,
                choices=c.choices,
                correct_key=c.correct_key,
                explanation=c.explanation,
            )
            for c in cards
        ]
