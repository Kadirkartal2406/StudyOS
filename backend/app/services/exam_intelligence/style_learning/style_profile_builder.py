"""Build StyleContract objects from M27 stats + metadata + DNA."""

from __future__ import annotations

from typing import Any

from app.services.exam_intelligence.style_learning.bloom_distribution import (
    build_bloom_distribution,
)
from app.services.exam_intelligence.style_learning.difficulty_curve_builder import (
    build_difficulty_curve,
)
from app.services.exam_intelligence.style_learning.question_intent_analyzer import (
    analyze_question_intent,
)
from app.services.exam_intelligence.style_learning.reading_load_analyzer import (
    analyze_reading_load,
)
from app.services.exam_intelligence.style_learning.reasoning_pattern_analyzer import (
    analyze_reasoning,
)
from app.services.exam_intelligence.style_learning.style_cluster import (
    assign_cluster_for_contract,
)
from app.services.exam_intelligence.style_learning.style_contract import (
    StyleContract,
    build_thinking_pattern,
    contract_to_safe_dict,
)
from app.services.exam_intelligence.style_learning.trap_pattern_analyzer import (
    analyze_trap_patterns,
)


def _slugs(subject_code: str, topic_code: str) -> tuple[str, str]:
    topic_slug = topic_code.split("__")[-1] if "__" in topic_code else topic_code
    if "_" in subject_code:
        subject_slug = subject_code.split("_", 1)[-1]
    else:
        subject_slug = subject_code
    return subject_slug, topic_slug


def build_topic_contract(
    *,
    stats: dict[str, Any],
    exam_dna: dict[str, Any] | None = None,
    topic_questions: list[dict[str, Any]] | None = None,
    layout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    exam_code = str(
        stats.get("exam_code") or (exam_dna or {}).get("exam_code") or ""
    )
    subject_code = str(stats.get("subject_code") or "unknown")
    topic_code = str(stats.get("topic_code") or f"{subject_code}__general")
    subject_slug, topic_slug = _slugs(subject_code, topic_code)
    skill = stats.get("skill_type")
    dna = exam_dna or {}

    intent = analyze_question_intent(
        exam_code=exam_code,
        topic_code=topic_code,
        skill_type=skill,
        subject_code=subject_code,
    )
    reading = analyze_reading_load(
        paragraph_avg=float(stats.get("paragraph_avg") or 0),
        sentence_avg=float(stats.get("sentence_avg") or 0),
        reading_avg_sec=float(stats.get("reading_avg") or 0),
        option_length=float(stats.get("option_length") or 0),
        visual_ratio=float((layout or {}).get("visual_usage_ratio") or 0),
        layout=layout,
        exam_dna=dna,
    )
    reasoning = analyze_reasoning(
        exam_code=exam_code,
        skill_type=skill,
        multi_step_ratio=float(dna.get("multi_step_ratio") or 0),
        reasoning_avg=float(stats.get("reasoning_avg") or 0),
        difficulty_avg=float(stats.get("difficulty_avg") or 50),
        topic_slug=topic_slug,
        exam_dna=dna,
    )
    trap = analyze_trap_patterns(
        exam_code=exam_code,
        topic_slug=topic_slug,
        skill_type=skill,
        distractor_style=str(
            stats.get("distractor_pattern") or dna.get("distractor_style") or ""
        )
        or None,
    )
    bloom = build_bloom_distribution(
        difficulty_avg=float(stats.get("difficulty_avg") or 50),
        skill_type=skill,
        reasoning_avg=float(stats.get("reasoning_avg") or 0),
        multi_step_ratio=float(dna.get("multi_step_ratio") or 0),
        exam_dna=None,  # topic-local; do not inherit whole-exam DNA blindly
    )
    curve = build_difficulty_curve(topic_questions)
    thinking = build_thinking_pattern(intent=intent, reasoning=reasoning, trap=trap)

    para = float(stats.get("paragraph_avg") or 0)
    paragraph_ratio = round(min(1.0, para / 120.0), 3) if para else float(
        dna.get("paragraph_ratio") or 0
    )
    option_balance = str(dna.get("option_balance") or "unknown")
    if float(stats.get("option_length") or 0) >= 5:
        option_balance = "tight"
    elif float(stats.get("option_length") or 0) > 0:
        option_balance = "short"

    expected_thinking = (
        f"{intent.get('primary')} via {reasoning.get('dominant')} "
        f"under {reading.get('load_band')} reading load"
    )

    contract = StyleContract(
        exam_code=exam_code,
        subject_code=subject_code,
        topic_code=topic_code,
        subject_slug=subject_slug,
        topic_slug=topic_slug,
        sample_size=int(stats.get("sample_size") or 0),
        reading_load=reading,
        difficulty={
            "avg": float(stats.get("difficulty_avg") or 50),
            "band": (
                "high"
                if float(stats.get("difficulty_avg") or 0) >= 65
                else (
                    "medium_high"
                    if float(stats.get("difficulty_avg") or 0) >= 55
                    else "medium"
                )
            ),
            "curve_summary": [c.get("band") for c in curve],
        },
        trap=trap,
        intent=intent,
        reasoning=reasoning,
        bloom=bloom,
        thinking_pattern=thinking,
        language_style={
            "tone": dna.get("language_level") or ("formal_tr" if exam_code not in ("ydt", "yds", "yokdil") else "academic_en"),
            "skill_type": skill or "general",
            "vocabulary_register": (
                "academic"
                if topic_slug in ("paragraf", "reading", "osmanli")
                else "technical"
                if topic_slug in ("problemler", "hareket", "mol")
                else "neutral"
            ),
        },
        expected_time_sec=float(stats.get("reading_avg") or dna.get("reading_time_sec_avg") or 0),
        option_balance=option_balance,
        vocabulary={
            "register": "academic" if reading.get("load_band") in ("high", "very_high") else "standard",
            "density": reading.get("information_density"),
        },
        paragraph_ratio=paragraph_ratio,
        expected_thinking=expected_thinking.strip(),
        difficulty_curve=curve,
    )
    data = contract_to_safe_dict(contract)
    data["cluster"] = assign_cluster_for_contract(data)
    # re-validate after cluster attach
    from app.services.exam_intelligence.style_learning.style_contract import (
        validate_contract,
    )

    data["validation"] = validate_contract(data)
    return data
