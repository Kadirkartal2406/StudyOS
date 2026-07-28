"""M29.3 Self Critic — score authored question 0–100."""

from __future__ import annotations

from typing import Any

from app.services.question_author.llm_utils import clamp_score, default_llm, parse_json_obj
from app.services.question_author.prompt_library import critic_messages
from app.services.question_author.types import AuthorPlan, CriticScores


def _heuristic_critic(question: dict[str, Any], plan: AuthorPlan) -> CriticScores:
    stem = str(question.get("stem") or "")
    choices = question.get("choices") or {}
    words = len(stem.split())
    style = 80
    if abs(words - plan.paragraph_length) <= max(40, plan.paragraph_length // 3):
        style += 8
    low = stem.lower()
    if any(
        x in low
        for x in ("stub", "geçici", "bloom düzeyi", "ölçülen kazanım")
    ):
        style = 40
    opt_lens = [len(str(v).split()) for v in choices.values()] if choices else [0]
    spread = (max(opt_lens) - min(opt_lens)) if opt_lens else 0
    option_q = 88 if spread <= 8 else 70
    choice_blob = " ".join(str(v) for v in choices.values()).lower()
    distractors = 82 if len(choices) >= plan.choice_count - 1 else 60
    if "çeldirici" in choice_blob or "doğru yanıt" in choice_blob:
        distractors = 35
        option_q = 35
    difficulty = min(95, max(55, plan.difficulty_target - abs(words - 80) // 10))
    return CriticScores(
        style=clamp_score(style),
        difficulty=clamp_score(difficulty),
        option_quality=clamp_score(option_q),
        distractors=clamp_score(distractors),
        language=78,
        naturalness=75 if style >= 70 else 40,
        exam_feeling=76 if style >= 80 else 45,
        reasoning=80 if plan.reasoning_type else 70,
    )


async def critique_question(
    question: dict[str, Any],
    plan: AuthorPlan,
    *,
    preferred: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> CriticScores:
    base = _heuristic_critic(question, plan)
    if not use_llm:
        return base
    try:
        result = await default_llm(
            critic_messages(
                {
                    "stem": question.get("stem"),
                    "choices": question.get("choices"),
                    "correct_key": question.get("correct_key"),
                },
                plan.to_dict(),
            ),
            context={"kind": "author_critic", "exam": plan.exam},
            preferred=preferred,
            model=model,
        )
        data = parse_json_obj(result.text)
        if not data:
            return base
        return CriticScores(
            style=clamp_score(data.get("style"), base.style),
            difficulty=clamp_score(data.get("difficulty"), base.difficulty),
            option_quality=clamp_score(data.get("option_quality"), base.option_quality),
            distractors=clamp_score(data.get("distractors"), base.distractors),
            language=clamp_score(data.get("language"), base.language),
            naturalness=clamp_score(data.get("naturalness"), base.naturalness),
            exam_feeling=clamp_score(data.get("exam_feeling"), base.exam_feeling),
            reasoning=clamp_score(data.get("reasoning"), base.reasoning),
        )
    except Exception:
        return base
