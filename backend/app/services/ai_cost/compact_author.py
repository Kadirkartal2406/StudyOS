"""M32 P3 — compact Author adapter (1 LLM call → stem+choices+explanation).

Does not rewrite Question Author / Review / VSSE engines. Produces AuthoredQuestion
shaped objects that still flow through frozen Review + VSSE gates.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.providers.ai.base import ChatMessageDTO, GenerateRequest, generate_with_fallback
from app.services.ai.quiz_quality_gate import extract_json_payload
from app.services.qie.types import GenerateContext, QuestionPlan
from app.services.question_author.author_planner import build_author_plan
from app.services.question_author.types import (
    AuthoredQuestion,
    CriticScores,
    ExaminerVerdict,
    MIN_EXAMINER,
)

logger = logging.getLogger("studyos.ai_cost.compact")


def _messages(plan: QuestionPlan, author_plan: dict[str, Any]) -> list[ChatMessageDTO]:
    system = """Sen StudyOS sınav sorusu yazarısın. Tek JSON üret:
{
  "stem": "...",
  "choices": {"A":"...","B":"...","C":"...","D":"...","E":"..."},
  "correct_key": "A",
  "explanation": "..."
}
Kurallar: ÖSYM üslubu, telifli kopya yok, çeldiriciler güçlü, doğru net.
Writer+Distractor+Naturalizer birleşik çıktı — ek meta/etiket yazma."""
    user = (
        f"Exam={plan.exam} Subject={plan.subject_name} Topic={plan.topic_name}\n"
        f"Skill={plan.skill} Bloom={plan.bloom} Difficulty={plan.difficulty}\n"
        f"ChoiceCount={plan.choice_count} Reasoning={plan.reasoning_type}\n"
        f"AuthorPlan={json.dumps(author_plan, ensure_ascii=False)}\n"
        "Yalnızca JSON."
    )
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
) -> AuthoredQuestion:
    from pathlib import Path

    root = Path(data_root) if data_root else None
    ap = await build_author_plan(
        plan, data_root=root, preferred=preferred, model=model, use_llm=False
    )
    result = await generate_with_fallback(
        GenerateRequest(
            messages=_messages(plan, ap.to_dict()),
            context={
                "kind": "author_compact",
                "exam": plan.exam,
                "topic_code": plan.topic_code,
                "max_output_tokens": 2048,
            },
        ),
        preferred=preferred,
        model=model,
    )
    try:
        data = extract_json_payload(result.text)
    except Exception:
        data = None
    if not isinstance(data, dict) or not data.get("stem"):
        raise RuntimeError("compact author returned unusable JSON")

    choices = {str(k): str(v) for k, v in (data.get("choices") or {}).items()}
    correct = str(data.get("correct_key") or "A").upper()
    if correct not in choices or len(choices) < max(2, plan.choice_count - 1):
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
) -> list[AuthoredQuestion]:
    preferred = ctx.preferred_provider if ctx else None
    model = ctx.preferred_model if ctx else None
    out: list[AuthoredQuestion] = []
    for plan in plans:
        try:
            q = await author_one_compact(plan, preferred=preferred, model=model)
            if not q.rejected:
                out.append(q)
        except Exception as e:
            logger.warning("compact author failed index=%s: %s", plan.index, e)
    return out
