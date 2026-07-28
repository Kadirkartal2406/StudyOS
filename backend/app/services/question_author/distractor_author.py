"""M29.5 Distractor Author — wrong options as a separate layer."""

from __future__ import annotations

import logging
from typing import Any

from app.services.question_author.llm_utils import default_llm, parse_json_obj
from app.services.question_author.prompt_library import distractor_messages
from app.services.question_author.stub_guard import AuthorLLMError
from app.services.question_author.types import AuthorPlan

logger = logging.getLogger("studyos.question_author.distractor")

DEFAULT_TRAPS = [
    "yanlis_cikarim",
    "yarim_bilgi",
    "yakin_kavram",
    "hesap_hatasi",
    "dikkat_hatasi",
]


async def author_distractors(
    *,
    stem: str,
    correct_key: str,
    correct_text: str,
    plan: AuthorPlan,
    preferred: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> dict[str, str]:
    """Return full choices map including correct key."""
    keys = ["A", "B", "C", "D", "E"][: plan.choice_count]
    traps = list(DEFAULT_TRAPS)
    if plan.trap_type and plan.trap_type not in traps:
        traps.insert(0, plan.trap_type)

    choices = {correct_key: correct_text}
    wrong_keys = [k for k in keys if k != correct_key]

    if not use_llm:
        for i, k in enumerate(wrong_keys):
            trap = traps[i % len(traps)]
            choices[k] = f"{trap.replace('_', ' ')} içeren çeldirici ({k})"
        return {k: choices[k] for k in keys if k in choices}

    try:
        result = await default_llm(
            distractor_messages(
                stem,
                correct_text,
                correct_key,
                traps[: len(wrong_keys)],
                plan.choice_count,
            ),
            context={"kind": "author_distractor", "exam": plan.exam},
            preferred=preferred,
            model=model,
        )
        if result.provider == "null" or result.used_fallback:
            raise AuthorLLMError(
                f"Distractor author needs a real LLM (got provider={result.provider})"
            )
        data = parse_json_obj(result.text)
        items = data.get("distractors") if isinstance(data, dict) else None
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                k = str(item.get("key") or "").upper()
                text = str(item.get("text") or "").strip()
                if k in wrong_keys and text:
                    choices[k] = text
    except AuthorLLMError:
        raise
    except Exception as e:
        logger.warning("Distractor author LLM failed: %s", e)
        raise AuthorLLMError(f"Distractor author LLM failed: {e}") from e

    missing = [k for k in wrong_keys if k not in choices or not str(choices.get(k) or "").strip()]
    if missing:
        raise AuthorLLMError(
            f"Distractor author incomplete choices for keys={missing}"
        )
    return {k: choices.get(k, "") for k in keys}
