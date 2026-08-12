"""M32 P6 — batch generation: one Gemini call → N QuestionCards (thin adapter)."""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.services.ai.measurement_integration import (
    allow_autopool_from_meta,
    apply_soft_measurement,
    inject_measurement_into_style,
    load_contract_for_context,
    measurement_meta_payload,
    prompt_block_from_contract,
)
from app.services.ai.quiz_quality_gate import (
    ValidatedQuizItem,
    extract_json_payload,
    validate_quiz_payload,
)
from app.services.ai_cost.measurement_flags import (
    measurement_enabled,
    measurement_max_regen,
    measurement_soft_review,
)
from app.services.ai_cost.metrics import get_metrics
from app.services.correctness.apply import attach_correctness_meta, evaluate_item_correctness
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

logger = logging.getLogger("studyos.ai_cost.batch")


def _batch_messages(
    plans: list[QuestionPlan],
    style: dict[str, Any],
    *,
    measurement_contract_block: str | None = None,
) -> list[ChatMessageDTO]:
    compact_plans = [p.to_dict() for p in plans]
    style_for_prompt = {
        k: v for k, v in style.items() if k != "measurement_soft_block"
    }
    system = """Sen ÖSYM (Ölçme, Seçme ve Yerleştirme Merkezi) standartlarında soru hazırlayan kıdemli bir kurulsun.
Görevlerin:
1. HATA YAPMAMAK (Halüsinasyon Önleme): Çözümleri adım adım, %100 matematiksel ve mantıksal tutarlılıkla (Chain of Thought) oluştur. Asla kural uydurma.
2. ÇELDİRİCİ MÜHENDİSLİĞİ: Şıklar sadece 'yanlış' olmamalıdır. En güçlü çeldiriciler, öğrencinin yapabileceği işlem hatalarına veya kavram yanılgılarına (misconceptions) dayandırılmalıdır. Birbiriyle kelime kelime aynı olan şıklardan kaçın.
3. ÖLÇME GÜCÜ: Doğrudan ezber yerine muhakeme, çıkarım ve okuduğunu anlama (veya modelleme) yeteneğini ölç. Sorular lise müfredatına (MEB) uygun olmalı, ancak akademik/robotik dilden uzak, açık ve anlaşılır bir Türkçeyle yazılmalıdır.
4. GEREKSİZ BİLGİDEN KAÇIN: Soru kökünü zorlaştırmak için alakası olmayan dolgu metinler (filler) ekleme. Zorluk, işlemin veya mantığın çok adımlı olmasından gelmelidir. Paragraf veya okuma parçası içeren sorularda, paragraf metnini MUTLAKA 'stem' (soru kökü) alanının en başına ekle.
5. JSON FORMATI: Çıktı sadece geçerli bir JSON objesi olmalıdır. LaTeX ifadelerinde ters bölü işaretlerini çift kaçır (örn. \\\\frac, \\\\lim).

Tek JSON Formatı: {"questions":[{"plan_index":0,"stem":"...","choices":{"A":"...","B":"...","C":"...","D":"...","E":"..."},"correct_key":"A","explanation":"Adım 1: ...\\nAdım 2: ...\\nSonuç: ..."}, ...]}
"""
    # Actively pass all rich DNA parameters, not just basic ones.
    user = (
        f"STYLE={json.dumps(style_for_prompt, ensure_ascii=False)}\n"
        f"PLANS={json.dumps(compact_plans, ensure_ascii=False)}\n"
        f"COUNT={len(plans)}\n"
    )
    block = measurement_contract_block or style.get("measurement_soft_block")
    if block:
        user += f"{block}\n"
    user += "Kurallara katı şekilde uyarak soruları üret. Yalnızca JSON ver."
    return [
        ChatMessageDTO(role="system", content=system),
        ChatMessageDTO(role="user", content=user),
    ]

def _verify_messages(generated_payload: dict) -> list[ChatMessageDTO]:
    system = """Sen kıdemli bir soru denetmenisin (Reviewer).
Sana verilen JSON formatındaki sorularda sadece şıkları ve correct_key değerini göreceksin, kendi başına bu soruları sıfırdan çözeceksin. 
Eğer üretenin bulduğu sonuç (correct_key) ile kendi matematiksel/mantıksal hesabın tutmuyorsa veya hatalıysa:
1. Şıkları (choices) düzelt.
2. Doğru şıkkı (correct_key) güncelle.
3. Açıklamayı (explanation) kendi çözümüne göre düzelt.
DİKKAT: Yeni soru üretme! Sadece sana verilen soruları analiz et ve hatalarını düzeltip aynı JSON formatında geri döndür."""
    user = (
        f"GELEN SORULAR:\n{json.dumps(generated_payload, ensure_ascii=False)}\n"
        "Soruları adım adım çöz, hataları düzelt ve sadece düzeltilmiş halini JSON formatında ver."
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
    n = max(1, min(int(count or ctx.count or 10), 10))
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
    contract = load_contract_for_context(
        exam=ctx_local.exam,
        subject_code=ctx_local.subject_code,
        topic_code=ctx_local.topic_code,
    )
    block = prompt_block_from_contract(contract) or getattr(
        ctx, "measurement_contract_block", None
    )
    ctx_local.measurement_contract_block = block
    dna = inject_measurement_into_style(dna, contract)
    plans = QuestionPlanner().plan_batch(ctx_local, style=dna)
    if not plans:
        logger.info("[PIPELINE] 2. QuestionPlanner returned zero plans")
        return [], "batch_empty", None

    logger.info("[PIPELINE] 2. Gemini request sending | exam=%s topic=%s count=%s", ctx_local.exam, ctx_local.topic_code, len(plans))
    result = await generate_with_fallback(
        GenerateRequest(
            messages=_batch_messages(plans, dna, measurement_contract_block=block),
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
        logger.info("[PIPELINE] 3b. extract_json_payload FAILED | err=%s text_preview=%s", exc, (getattr(result, "text", "") or "")[:500])
        return [], "batch_parse_fail", result

    # --- TWO-STAGE SELF-REFLECTION (Verification Pass) ---
    logger.info("[PIPELINE] 3c. Gemini Verification (Self-Correction) sending...")
    verify_result = await generate_with_fallback(
        GenerateRequest(
            messages=_verify_messages(payload),
            context={
                "kind": "batch_verify",
                "exam": ctx_local.exam,
                "topic_code": ctx_local.topic_code,
                "count": len(plans),
                "max_output_tokens": 8192,
            },
        ),
        preferred=ctx_local.preferred_provider,
        model=ctx_local.preferred_model,
    )
    try:
        payload = extract_json_payload(verify_result.text)
        logger.info("[PIPELINE] 3d. Verification successful.")
    except Exception as exc:
        logger.warning("[PIPELINE] 3d. Verification parse failed, falling back to original payload. err=%s", exc)

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
    shadow_observations: list[dict[str, Any]] = []
    raw_q = payload.get("questions") if isinstance(payload, dict) else None
    for i, item in enumerate(gate.valid):
        plan = plans[i] if i < len(plans) else plans[0]
        if isinstance(raw_q, list) and i < len(raw_q) and isinstance(raw_q[i], dict):
            try:
                hint = int(raw_q[i].get("plan_index"))
                plan = plan_by_i.get(hint, plan)
            except Exception:
                pass

        corr = evaluate_item_correctness(item, plan)
        if not corr.passed:
            logger.info(
                "[PIPELINE] 4b. Card skipped: correctness reject_reason=%s",
                corr.reason,
            )
            continue

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
            logger.info(
                "[PIPELINE] 4b. Card skipped: M34 reject_reason=%s",
                m34.get("reject_reason"),
            )
            continue
        q2 = m34.get("question") or qdict
        item = ValidatedQuizItem(
            stem=str(q2.get("stem") or ""),
            choices=dict(q2.get("choices") or {}),
            correct_key=str(q2.get("correct_key") or item.correct_key).upper(),
            explanation=q2.get("explanation"),
        )
        corr = evaluate_item_correctness(item, plan, log_pass=False)
        if not corr.passed:
            logger.info(
                "[PIPELINE] 4b. Card skipped: correctness after M34 reject_reason=%s",
                corr.reason,
            )
            continue

        if is_similar_question(item, existing_stems=existing, existing_option_sets=existing_opts):
            stem_text = getattr(item, "stem", "") or ""
            logger.info("[PIPELINE] 4b. Card skipped: similar question stem=%s...", stem_text[:30])
            continue
        diff = analyze_for_plan(item, plan, style=dna)
        if diff.score < MIN_DIFFICULTY_SCORE:
            logger.info("[PIPELINE] 4b. Card skipped: low difficulty score=%s min=%s reasons=%s", diff.score, MIN_DIFFICULTY_SCORE, diff.reasons)
            continue
        quality = score_quality(
            item, plan, difficulty_score=diff.score, existing_stems=existing, style_dna=dna
        )
        if not passes_quality_gate(quality):
            logger.info("[PIPELINE] 4b. Card skipped: failed QIE quality gate")
            # Shadow/soft: still score for observation — does not change reject/autopool.
            if measurement_enabled():
                score, decision = apply_soft_measurement(
                    stem=item.stem,
                    choices=item.choices,
                    quality_passed=False,
                    contract=contract,
                    retry_count=0,
                    subject=plan.subject_code,
                    topic=plan.topic_code,
                )
                obs = measurement_meta_payload(score, decision)
                obs["contract_injected"] = bool(block)
                obs["in_batch_output"] = False
                shadow_observations.append(obs)
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
        # Soft measurement side-channel (default OFF). Batch path: if soft_review
        # wants regen, mark hold after max_regen budget (no infinite loop).
        retry = 0
        initial_measurement_status = None
        post_regen_measurement_status = None
        regen_attempted = False
        score, decision = apply_soft_measurement(
            stem=card.stem,
            choices=card.choices,
            quality_passed=True,
            contract=contract,
            retry_count=retry,
            subject=plan.subject_code,
            topic=plan.topic_code,
        )
        initial_measurement_status = score.status if score else None
        if decision.should_regen and measurement_soft_review():
            # One soft regen attempt via compact author (capped).
            regen_attempted = True
            try:
                from app.services.ai_cost.compact_author import author_one_compact

                aq = await author_one_compact(
                    plan,
                    preferred=ctx_local.preferred_provider,
                    model=ctx_local.preferred_model,
                    measurement_contract_block=block,
                )
                retry = 1
                item2 = ValidatedQuizItem(
                    stem=aq.stem,
                    choices=dict(aq.choices),
                    correct_key=aq.correct_key,
                    explanation=aq.explanation,
                )
                diff2 = analyze_for_plan(item2, plan, style=dna)
                if diff2.score >= MIN_DIFFICULTY_SCORE:
                    quality2 = score_quality(
                        item2,
                        plan,
                        difficulty_score=diff2.score,
                        existing_stems=existing,
                        style_dna=dna,
                    )
                    if passes_quality_gate(quality2):
                        corr2 = evaluate_item_correctness(item2, plan)
                        if corr2.passed:
                            card = build_card(
                                item2,
                                plan,
                                difficulty_score=diff2.score,
                                quality=quality2,
                                style_score=quality2.style,
                                provider=aq.provider or result.provider,
                                model=aq.model or result.model,
                            )
                            attach_correctness_meta(card, corr2)
                score, decision = apply_soft_measurement(
                    stem=card.stem,
                    choices=card.choices,
                    quality_passed=True,
                    contract=contract,
                    retry_count=retry,
                    subject=plan.subject_code,
                    topic=plan.topic_code,
                )
                post_regen_measurement_status = score.status if score else None
            except Exception as e:
                logger.info("measurement soft regen skipped: %s", e)
                score, decision = apply_soft_measurement(
                    stem=card.stem,
                    choices=card.choices,
                    quality_passed=True,
                    contract=contract,
                    retry_count=measurement_max_regen(),
                    subject=plan.subject_code,
                    topic=plan.topic_code,
                )
                post_regen_measurement_status = score.status if score else None
        card.measurement_meta = measurement_meta_payload(score, decision)
        card.measurement_meta["contract_injected"] = bool(block)
        card.measurement_meta["initial_measurement_status"] = initial_measurement_status
        card.measurement_meta["post_regen_measurement_status"] = post_regen_measurement_status
        card.measurement_meta["regen_attempted"] = regen_attempted
        if measurement_soft_review() and not allow_autopool_from_meta(card.measurement_meta):
            card.measurement_meta["in_batch_output"] = False
            card.measurement_meta["mock_pool_write"] = False
            shadow_observations.append(dict(card.measurement_meta))
            logger.info(
                "[PIPELINE] 4b. measurement_review_hold — not adding to batch output"
            )
            continue
        card.measurement_meta["in_batch_output"] = True
        card.measurement_meta["mock_pool_write"] = True
        shadow_observations.append(dict(card.measurement_meta))
        out.append(card)
        existing.append(card.stem)
        existing_opts.append(card.choices)

    logger.info("[PIPELINE] 4c. Cards building finished | total_built_cards=%s", len(out))
    if result is not None:
        setattr(result, "measurement_shadow_observations", shadow_observations)
        setattr(result, "measurement_contract_injected", bool(block))
        setattr(
            result,
            "measurement_exam_unit",
            contract.exam_unit if contract else None,
        )

    return out, f"batch_one_call:{len(out)}", result
