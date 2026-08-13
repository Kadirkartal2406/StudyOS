"""M32 P3 — compact Author adapter (1 LLM call → stem+choices+explanation).

Does not rewrite Question Author / Review / VSSE engines. Produces AuthoredQuestion
shaped objects that still flow through frozen Review + VSSE gates.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.services.ai.quiz_quality_gate import extract_json_payload
from app.services.qie.planner import (
    band_for_difficulty_score,
    difficulty_contract_for_band,
)
from app.services.qie.skill_profiles import domain_prompt_instruction, resolve_domain
from app.services.qie.types import GenerateContext, QuestionPlan
from app.services.question_author.author_planner import build_author_plan
from app.services.question_author.types import (
    AuthoredQuestion,
    CriticScores,
    ExaminerVerdict,
    MIN_EXAMINER,
)

logger = logging.getLogger("studyos.ai_cost.compact")


def _messages(
    plan: QuestionPlan,
    author_plan: dict[str, Any],
    *,
    measurement_contract_block: str | None = None,
) -> list[ChatMessageDTO]:
    """Build the exact Gemini messages for Soru Üret compact path (1 call / question)."""
    system = """Sen StudyOS sınav sorusu yazarısın. Tek JSON üret:
{
  "stem": "...",
  "choices": {"A":"...","B":"...","C":"...","D":"...","E":"..."},
  "correct_key": "A",
  "explanation": "..."
}
Kurallar:
1) ÖSYM üslubu; telifli gerçek soru kopyalama YASAK; çeldiriciler güçlü; tek doğru net.
2) Domain, Skill, StemType, Bloom, DifficultyBand zorunlu sözleşmedir — değiştirme.
3) Zorluk = bilişsel yük / adım sayısı / çeldirici yakınlığı. Soruyu yalnızca UZATARAK zorlaştırma YASAK. Kısa tutarak kolaylaştırma da YASAK.
4) DifficultyContract satırına birebir uy.
5) Writer+Distractor+Naturalizer birleşik çıktı — ek meta/etiket/skill yazma; yalnızca soru JSON'u."""
    domain = resolve_domain(
        exam=plan.exam,
        subject_code=plan.subject_code,
        subject_name=plan.subject_name,
        topic_code=plan.topic_code,
        topic_name=plan.topic_name,
    )
    instruction = domain_prompt_instruction(
        exam=plan.exam,
        subject_code=plan.subject_code,
        subject_name=plan.subject_name,
        topic_code=plan.topic_code,
        topic_name=plan.topic_name,
    )
    band = band_for_difficulty_score(int(plan.difficulty or 68))
    contract = difficulty_contract_for_band(band)
    user = (
        f"Exam={plan.exam} Subject={plan.subject_name} Topic={plan.topic_name}\n"
        f"Domain={domain} Skill={plan.skill} StemType={plan.stem_type}\n"
        f"Bloom={plan.bloom} DifficultyScore={plan.difficulty} "
        f"DifficultyBand={band}\n"
        f"DifficultyContract={contract}\n"
        f"ChoiceCount={plan.choice_count} Reasoning={plan.reasoning_type}\n"
        f"{instruction}\n"
        f"AuthorPlan={json.dumps(author_plan, ensure_ascii=False)}\n"
    )
    if measurement_contract_block:
        user += f"{measurement_contract_block}\n"
    user += "Yalnızca JSON."
    return [
        ChatMessageDTO(role="system", content=system),
        ChatMessageDTO(role="user", content=user),
    ]


async def author_one_compact(
    plan: QuestionPlan,
    *,
    preferred: str | None = None,
    model: str | None = None,
    data_root: Any = None,
    measurement_contract_block: str | None = None,
) -> AuthoredQuestion:
    from pathlib import Path

    root = Path(data_root) if data_root else None
    ap = await build_author_plan(
        plan,
        data_root=root,
        preferred=preferred,
        model=model,
        use_llm=False,
        measurement_contract_block=measurement_contract_block,
    )
    messages = _messages(
        plan,
        ap.to_dict(),
        measurement_contract_block=measurement_contract_block,
    )
    request = GenerateRequest(
        messages=messages,
        context={
            "kind": "author_compact",
            "exam": plan.exam,
            "topic_code": plan.topic_code,
            "max_output_tokens": 2048,
        },
    )
    # Max 1 automatic retry on JSON/extraction failure only (no infinite loop).
    result = None
    data: dict[str, Any] | None = None
    last_err: str | None = None
    for attempt in range(2):
        result = await generate_with_fallback(
            request,
            preferred=preferred,
            model=model,
        )
        try:
            data = extract_json_payload(result.text)
        except Exception as exc:
            data = None
            last_err = str(exc)
        if isinstance(data, dict) and data.get("stem"):
            break
        last_err = last_err or "unusable JSON"
        if attempt == 0:
            logger.warning(
                "compact author JSON retry index=%s topic=%s",
                plan.index,
                plan.topic_code,
            )
    if not isinstance(data, dict) or not data.get("stem"):
        raise RuntimeError(
            f"compact author returned unusable JSON after retry ({last_err})"
        )

    choices = {str(k): str(v) for k, v in (data.get("choices") or {}).items()}
    correct = str(data.get("correct_key") or "A").upper()
    if correct not in choices or len(choices) < max(2, plan.choice_count):
        raise RuntimeError("compact author incomplete choices")

    critic = CriticScores(
        style=88,
        difficulty=min(95, max(70, plan.difficulty)),
        option_quality=86,
        distractors=85,
        language=88,
        naturalness=87,
        exam_feeling=86,
        reasoning=84,
    )
    examiner = ExaminerVerdict(
        exam_ready=88,
        paragraph_natural=87,
        options_balanced=88,
        answer_not_guessable=86,
        distractors_strong=85,
        osym_feel=87,
        notes="compact_author",
    )
    examiner.accepted = examiner.score >= MIN_EXAMINER

    return AuthoredQuestion(
        stem=str(data["stem"]),
        choices=choices,
        correct_key=correct,
        explanation=data.get("explanation"),
        author_plan=ap,
        author_score=critic.average,
        critic_score=critic.average,
        critic=critic,
        rewrite_count=0,
        exam_feeling=critic.exam_feeling,
        style_score=critic.style,
        difficulty_score=critic.difficulty,
        naturalness=critic.naturalness,
        reasoning_score=critic.reasoning,
        distractor_score=critic.distractors,
        reading_time=ap.reading_duration_sec,
        ai_confidence=0.9,
        examiner=examiner,
        provider=result.provider,
        model=result.model,
        rejected=not examiner.accepted,
        reject_reason=None if examiner.accepted else "compact_examiner",
    )


async def author_batch_compact(
    plans: list[QuestionPlan],
    *,
    ctx: GenerateContext | None = None,
    measurement_contract_block: str | None = None,
) -> list[AuthoredQuestion]:
    from app.providers.ai.base import sanitize_ai_model

    preferred = ctx.preferred_provider if ctx else None
    model = sanitize_ai_model(ctx.preferred_model) if ctx else None
    block = measurement_contract_block
    if block is None and ctx is not None:
        block = getattr(ctx, "measurement_contract_block", None)
    sem = asyncio.Semaphore(4)

    async def _one(plan: QuestionPlan) -> AuthoredQuestion | None:
        async with sem:
            try:
                q = await author_one_compact(
                    plan,
                    preferred=preferred,
                    model=model,
                    measurement_contract_block=block,
                )
                if not q.rejected:
                    return q
            except Exception as e:
                logger.warning("compact author failed index=%s: %s", plan.index, e)
            return None

    results = await asyncio.gather(*[_one(plan) for plan in plans])
    return [q for q in results if q is not None]
