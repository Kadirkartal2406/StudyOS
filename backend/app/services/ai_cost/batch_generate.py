"""M32 P6 — batch generation: one Gemini call → N QuestionCards (thin adapter)."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.services.ai.quiz_quality_gate import (
    ValidatedQuizItem,
    extract_json_payload,
    validate_quiz_payload,
)
from app.services.ai_cost.metrics import get_metrics
from app.services.qie.difficulty_analyzer import analyze_for_plan
from app.services.qie.planner import QuestionPlanner
from app.services.qie.quality_gate_v2 import passes_quality_gate, score_quality
from app.services.qie.question_card import build_card
from app.services.qie.similarity import is_similar_question
from app.services.qie.style_intelligence import StyleIntelligence
from app.services.qie.types import (
    MIN_DIFFICULTY_SCORE,
    GenerateContext,
    QuestionCard,
    QuestionPlan,
)
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("studyos.ai_cost.batch")


def _batch_messages(plans: list[QuestionPlan], style: dict[str, Any]) -> list[ChatMessageDTO]:
    compact_plans = [p.to_dict() for p in plans]
    system = """Sen StudyOS batch soru üreticisisin.
Tek JSON: {"questions":[{"plan_index":0,"stem":"...","choices":{...},"correct_key":"A","explanation":"..."}, ...]}
Her plan_index için tam bir soru. Telif yok. ÖSYM üslubu."""
    user = (
        f"STYLE={json.dumps({k: style.get(k) for k in ('choice_count','bloom_default','language_level') if k in style}, ensure_ascii=False)}\n"
        f"PLANS={json.dumps(compact_plans, ensure_ascii=False)}\n"
        f"COUNT={len(plans)}\nYalnızca JSON."
    )
    return [
        ChatMessageDTO(role="system", content=system),
        ChatMessageDTO(role="user", content=user),
    ]


async def generate_batch_one_call(
    db: AsyncSession,
    ctx: GenerateContext,
    *,
    count: int | None = None,
) -> tuple[list[QuestionCard], str, Any]:
    """One Gemini call for up to `count` questions. Frozen gates still applied."""
    get_metrics().record_batch()
    n = max(1, min(int(count or ctx.count or 20), 20))
    ctx_local = GenerateContext(
        exam=ctx.exam,
        subject_code=ctx.subject_code,
        subject_name=ctx.subject_name,
        topic_code=ctx.topic_code,
        topic_name=ctx.topic_name,
        count=n,
        difficulty_band=ctx.difficulty_band,
        user_id=ctx.user_id,
        preferred_provider=ctx.preferred_provider,
        preferred_model=ctx.preferred_model,
        existing_stems=list(ctx.existing_stems),
        recent_skills=list(ctx.recent_skills),
        recent_patterns=list(ctx.recent_patterns),
        plans=ctx.plans,
        choice_count=ctx.choice_count,
        style_override=ctx.style_override,
        kind=ctx.kind or "batch_generate",
    )
    style = StyleIntelligence(db)
    dna = await style.dna(
        ctx_local.exam,
        subject_code=ctx_local.subject_code,
        difficulty=ctx_local.difficulty_band,
    )
    plans = QuestionPlanner().plan_batch(ctx_local, style=dna)
    if not plans:
        logger.info("[PIPELINE] 2. QuestionPlanner returned zero plans")
        return [], "batch_empty", None

    logger.info("[PIPELINE] 2. Gemini request sending | exam=%s topic=%s count=%s", ctx_local.exam, ctx_local.topic_code, len(plans))
    result = await generate_with_fallback(
        GenerateRequest(
            messages=_batch_messages(plans, dna),
            context={
                "kind": "batch_generate",
                "exam": ctx_local.exam,
                "topic_code": ctx_local.topic_code,
                "count": len(plans),
                "max_output_tokens": 8192,
            },
        ),
        preferred=ctx_local.preferred_provider,
        model=ctx_local.preferred_model,
    )
    logger.info(
        "[PIPELINE] 3. Gemini response received | provider=%s model=%s text_len=%s",
        getattr(result, "provider", None),
        getattr(result, "model", None),
        len(getattr(result, "text", "") or ""),
    )
    try:
        payload = extract_json_payload(result.text)
    except Exception as exc:
        logger.info("[PIPELINE] 3b. extract_json_payload FAILED | err=%s text_preview=%s", exc, (getattr(result, "text", "") or "")[:100])
        return [], "batch_parse_fail", result

    gate = validate_quiz_payload(
        payload,
        topic_name=ctx_local.topic_name,
        expected_count=len(plans),
        choice_count=plans[0].choice_count,
        max_stem=2500,
    )
    logger.info(
        "[PIPELINE] 4. validate_quiz_payload | valid=%s valid_count=%s errors=%s",
        bool(gate.valid),
        len(gate.valid) if gate.valid else 0,
        gate.errors,
    )
    if not gate.valid:
        return [], "batch_gate_fail", result

    plan_by_i = {p.index: p for p in plans}
    existing = list(ctx_local.existing_stems)
    existing_opts: list[dict[str, str]] = []
    out: list[QuestionCard] = []
    raw_q = payload.get("questions") if isinstance(payload, dict) else None
    for i, item in enumerate(gate.valid):
        plan = plans[i] if i < len(plans) else plans[0]
        if isinstance(raw_q, list) and i < len(raw_q) and isinstance(raw_q[i], dict):
            try:
                hint = int(raw_q[i].get("plan_index"))
                plan = plan_by_i.get(hint, plan)
            except Exception:
                pass
        if is_similar_question(item, existing_stems=existing, existing_option_sets=existing_opts):
            logger.info("[PIPELINE] 4b. Card skipped: similar question stem=%s...", (item.get("stem") or "")[:30])
            continue
        diff = analyze_for_plan(item, plan, style=dna)
        if diff.score < MIN_DIFFICULTY_SCORE:
            logger.info("[PIPELINE] 4b. Card skipped: low difficulty score=%s min=%s", diff.score, MIN_DIFFICULTY_SCORE)
            continue
        quality = score_quality(
            item, plan, difficulty_score=diff.score, existing_stems=existing, style_dna=dna
        )
        if not passes_quality_gate(quality):
            logger.info("[PIPELINE] 4b. Card skipped: failed QIE quality gate")
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
        out.append(card)
        existing.append(card.stem)
        existing_opts.append(card.choices)

    logger.info("[PIPELINE] 4c. Cards building finished | total_built_cards=%s", len(out))

    return out, f"batch_one_call:{len(out)}", result
