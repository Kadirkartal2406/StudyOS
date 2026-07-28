"""M29.6 Question Naturalizer — reduce AI smell / ÖSYM tone."""

from __future__ import annotations

import re
from typing import Any

from app.services.question_author.llm_utils import default_llm, parse_json_obj
from app.services.question_author.prompt_library import naturalizer_messages

_AI_PHRASES = (
    r"\bAI\b",
    r"yapay zeka",
    r"aşağıdaki metne göre",
    r"bu soruda dikkat edilirse",
    r"geçici stub",
    r"\[revize:[^\]]+\]",
)


def _heuristic_naturalize(question: dict[str, Any]) -> dict[str, Any]:
    q = {
        "stem": str(question.get("stem") or ""),
        "choices": dict(question.get("choices") or {}),
        "correct_key": str(question.get("correct_key") or "A").upper(),
        "explanation": question.get("explanation"),
    }
    stem = q["stem"]
    for pat in _AI_PHRASES:
        stem = re.sub(pat, "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"\s{2,}", " ", stem).strip()
    # Soften repetitive openers
    stem = re.sub(r"^(Bu metinde|Verilen paragrafta)\s+", "", stem)
    q["stem"] = stem
    return q


async def naturalize_question(
    question: dict[str, Any],
    *,
    exam: str,
    preferred: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> dict[str, Any]:
    base = _heuristic_naturalize(question)
    if not use_llm:
        return base
    try:
        result = await default_llm(
            naturalizer_messages(base, exam),
            context={"kind": "author_naturalizer", "exam": exam},
            preferred=preferred,
            model=model,
        )
        data = parse_json_obj(result.text)
        if data.get("stem") and isinstance(data.get("choices"), dict):
            return {
                "stem": str(data["stem"]),
                "choices": {str(k): str(v) for k, v in data["choices"].items()},
                "correct_key": str(data.get("correct_key") or base["correct_key"]).upper(),
                "explanation": data.get("explanation") or base.get("explanation"),
            }
    except Exception:
        pass
    return base
