"""M29.4 Rewrite Engine — max 2 rewrites when critic thresholds fail."""

from __future__ import annotations

from typing import Any

from app.services.question_author.llm_utils import default_llm, parse_json_obj
from app.services.question_author.prompt_library import rewrite_messages
from app.services.question_author.types import AuthorPlan, CriticScores, MAX_REWRITE


async def rewrite_question(
    question: dict[str, Any],
    plan: AuthorPlan,
    critic: CriticScores,
    *,
    preferred: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> dict[str, Any]:
    if not use_llm:
        # Light heuristic tweak for stub path
        q = dict(question)
        q["stem"] = str(q.get("stem") or "") + " [revize: stil ve çeldirici güçlendirildi]"
        return q
    try:
        result = await default_llm(
            rewrite_messages(
                {
                    "stem": question.get("stem"),
                    "choices": question.get("choices"),
                    "correct_key": question.get("correct_key"),
                    "explanation": question.get("explanation"),
                },
                plan.to_dict(),
                critic.to_dict(),
            ),
            context={"kind": "author_rewrite", "exam": plan.exam},
            preferred=preferred,
            model=model,
        )
        data = parse_json_obj(result.text)
        if data.get("stem") and isinstance(data.get("choices"), dict):
            return {
                "stem": str(data["stem"]),
                "choices": {str(k): str(v) for k, v in data["choices"].items()},
                "correct_key": str(data.get("correct_key") or question.get("correct_key") or "A").upper(),
                "explanation": data.get("explanation") or question.get("explanation"),
                "_provider": result.provider,
                "_model": result.model,
            }
    except Exception:
        pass
    return question


def should_rewrite(critic: CriticScores, rewrite_count: int) -> bool:
    return critic.needs_rewrite() and rewrite_count < MAX_REWRITE
