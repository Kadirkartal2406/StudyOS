"""M29.1 Author Planner — Question Plan only (no stem)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.qie.types import QuestionPlan
from app.services.question_author.llm_utils import default_llm, parse_json_obj
from app.services.question_author.prompt_library import plan_messages
from app.services.question_author.types import AuthorPlan


def _load_style_contract(exam: str, topic_code: str, data_root: Path | None) -> dict[str, Any]:
    if data_root is None:
        return {}
    try:
        from app.services.exam_intelligence.style_learning import StyleRepository

        repo = StyleRepository(data_root)
        c = repo.get_style(topic_code)
        if c:
            return c
        if "__" in topic_code:
            left, slug = topic_code.split("__", 1)
            subject = left.split("_", 1)[-1] if "_" in left else left
            return repo.get_topic_style(exam, subject, slug) or {}
    except Exception:
        return {}
    return {}


def _heuristic_plan(qie: QuestionPlan, style: dict[str, Any]) -> AuthorPlan:
    trap = "yakin_anlam"
    traps = (style.get("trap") or {}).get("primary") or []
    if traps:
        trap = str(traps[0])
    intent = (style.get("intent") or {}).get("primary") or qie.skill
    reasoning = (
        ((style.get("reasoning") or {}).get("dominant"))
        or qie.reasoning_type
        or "iki_adim"
    )
    return AuthorPlan(
        measured_outcome=str(intent),
        reasoning_type=str(reasoning),
        distractor_type=qie.distractor_pattern or trap,
        paragraph_length=int(qie.paragraph_length or 120),
        option_strategy=qie.option_balance or "tight",
        bloom_level=qie.bloom or "analyze",
        difficulty_target=int(qie.difficulty or 70),
        reading_duration_sec=int(qie.reading_time_sec or 60),
        trap_type=trap,
        exam=qie.exam,
        subject_code=qie.subject_code,
        topic_code=qie.topic_code,
        topic_name=qie.topic_name,
        choice_count=qie.choice_count,
        style_contract=style,
        qie_plan_index=qie.index,
        forbidden_patterns=list(qie.forbidden_recent_patterns or []),
    )


async def build_author_plan(
    qie_plan: QuestionPlan,
    *,
    data_root: Path | None = None,
    preferred: str | None = None,
    model: str | None = None,
    use_llm: bool = True,
) -> AuthorPlan:
    style = _load_style_contract(qie_plan.exam, qie_plan.topic_code, data_root)
    base = _heuristic_plan(qie_plan, style)
    if not use_llm:
        return base

    try:
        result = await default_llm(
            plan_messages(qie_plan.to_dict(), style),
            context={
                "kind": "author_planner",
                "exam": qie_plan.exam,
                "topic_code": qie_plan.topic_code,
            },
            preferred=preferred,
            model=model,
        )
        data = parse_json_obj(result.text)
        if not data:
            return base
        return AuthorPlan(
            measured_outcome=str(data.get("measured_outcome") or base.measured_outcome),
            reasoning_type=str(data.get("reasoning_type") or base.reasoning_type),
            distractor_type=str(data.get("distractor_type") or base.distractor_type),
            paragraph_length=int(data.get("paragraph_length") or base.paragraph_length),
            option_strategy=str(data.get("option_strategy") or base.option_strategy),
            bloom_level=str(data.get("bloom_level") or base.bloom_level),
            difficulty_target=int(data.get("difficulty_target") or base.difficulty_target),
            reading_duration_sec=int(
                data.get("reading_duration_sec") or base.reading_duration_sec
            ),
            trap_type=str(data.get("trap_type") or base.trap_type),
            exam=base.exam,
            subject_code=base.subject_code,
            topic_code=base.topic_code,
            topic_name=base.topic_name,
            choice_count=base.choice_count,
            style_contract=style,
            qie_plan_index=base.qie_plan_index,
            forbidden_patterns=base.forbidden_patterns,
        )
    except Exception:
        return base
