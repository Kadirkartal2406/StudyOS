"""M29.2 Question Writer — single question from Author Plan."""

from __future__ import annotations

import logging
from typing import Any

from app.services.question_author.llm_utils import default_llm, parse_json_obj
from app.services.question_author.prompt_library import writer_messages
from app.services.question_author.stub_guard import AuthorLLMError
from app.services.question_author.types import AuthorPlan

logger = logging.getLogger("studyos.question_author.writer")


def _stub_question(plan: AuthorPlan, *, correct_only: bool = False) -> dict[str, Any]:
    keys = ["A", "B", "C", "D", "E"][: plan.choice_count]
    stem = (
        f"{plan.topic_name or plan.topic_code} alanında günlük yaşamdan bir durumu "
        f"anlatan kısa bir metin düşününüz. Anlatıcı, gözlemlediği olaylar arasında "
        f"neden-sonuç ilişkisi kurarak okuyucuyu {plan.reasoning_type} yürütmeye "
        f"çağırmaktadır. Bloom düzeyi {plan.bloom_level} olacak şekilde, yaklaşık "
        f"{plan.paragraph_length} kelimelik resmi bir üslup hedeflenmiştir. "
        f"Okuma süresi yaklaşık {plan.reading_duration_sec} saniyedir. "
        f"Bu metne göre ölçülen kazanım: {plan.measured_outcome}. "
        f"Aşağıdakilerden hangisi metnin temel vurgusuna en uygundur?"
    )
    if correct_only:
        return {
            "stem": stem,
            "correct_answer_text": f"Doğru yanıt — {plan.measured_outcome}",
            "rationale": f"Plan: {plan.measured_outcome}",
        }
    choices = {k: f"Seçenek {k} ({plan.trap_type})" for k in keys}
    choices[keys[0]] = f"Doğru yanıt — {plan.measured_outcome}"
    return {
        "stem": stem,
        "choices": choices,
        "correct_key": keys[0],
        "explanation": f"Plan: {plan.measured_outcome}",
    }


async def write_question(
    plan: AuthorPlan,
    *,
    preferred: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
    correct_only: bool = False,
    eae_grounding_context: str | None = None,
) -> dict[str, Any]:
    if not use_llm:
        return _stub_question(plan, correct_only=correct_only)

    try:
        result = await default_llm(
            writer_messages(
                plan.to_dict(),
                style=plan.style_contract,
                correct_only=correct_only,
                eae_grounding_context=eae_grounding_context,
            ),
            context={
                "kind": "author_writer",
                "exam": plan.exam,
                "topic_code": plan.topic_code,
            },
            preferred=preferred,
            model=model,
        )
        if result.provider == "null" or result.used_fallback:
            raise AuthorLLMError(
                f"Author writer needs a real LLM (got provider={result.provider})"
            )
        data = parse_json_obj(result.text)
        if correct_only and data.get("stem") and data.get("correct_answer_text"):
            return data
        if data.get("stem") and isinstance(data.get("choices"), dict):
            return {
                "stem": str(data["stem"]),
                "choices": {str(k): str(v) for k, v in data["choices"].items()},
                "correct_key": str(data.get("correct_key") or "A").upper(),
                "explanation": data.get("explanation"),
                "_provider": result.provider,
                "_model": result.model,
            }
        raise AuthorLLMError("Author writer LLM returned unusable JSON")
    except AuthorLLMError:
        raise
    except Exception as e:
        logger.warning("Author writer LLM failed: %s", e)
        raise AuthorLLMError(f"Author writer LLM failed: {e}") from e
