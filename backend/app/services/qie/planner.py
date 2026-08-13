"""Question Planner — brain of QIE. LLM cannot change this plan."""

from __future__ import annotations

from app.services.qie.distractor_model import pick_distractor
from app.services.qie.skill_profiles import (
    LANGUAGE_SKILLS,
    LANGUAGE_STEMS,
    get_skill_profile,
    paragraph_length_for_stem,
    skill_pool_for_context,
    stem_cycle_for_profile,
)
from app.services.qie.types import GenerateContext, QuestionPlan

# Re-exported for backward compatibility. LANGUAGE_* are Türkçe-only —
# do NOT use as cross-domain defaults (see skill_profiles.get_skill_profile).
_SKILL_DEFAULTS = list(LANGUAGE_SKILLS)
_STEM_CYCLE = list(LANGUAGE_STEMS)

_BLOOM_BY_DIFFICULTY = [
    (40, "understand"),
    (60, "apply"),
    (75, "analyze"),
    (90, "evaluate"),
    (101, "create"),
]

_DIFF_BAND = {"easy": 45, "medium": 70, "hard": 85}

_REASONING_STEMS = frozenset(
    {
        "inference",
        "cause_effect",
        "logical_reasoning",
        "problem_solving",
        "application",
        "calculation",
        "interpretation",
        "comparison",
        "analysis",
        "argument_analysis",
        "data_interpretation",
        "multi_step",
    }
)


def _bloom_for(difficulty: int) -> str:
    for lim, bloom in _BLOOM_BY_DIFFICULTY:
        if difficulty < lim:
            return bloom
    return "analyze"


def _difficulty_for_band(band: str, index: int, count: int) -> int:
    base = _DIFF_BAND.get((band or "medium").lower(), 70)
    # slight spread within batch
    spread = ((index * 7) % 15) - 7
    return max(25, min(95, base + spread))


def _reasoning_type(stem_type: str) -> str:
    if stem_type in _REASONING_STEMS:
        return stem_type if stem_type in ("inference", "cause_effect") else (
            "inference" if stem_type in ("interpretation", "analysis", "argument_analysis") else stem_type
        )
    return "inference"


class QuestionPlanner:
    """Produce immutable QuestionPlan list before any LLM call."""

    def plan_batch(self, ctx: GenerateContext, style: dict | None = None) -> list[QuestionPlan]:
        if ctx.plans:
            return list(ctx.plans)

        style = style or {}
        choice_count = ctx.choice_count or int(style.get("choice_count") or 5)
        is_reading_topic = any(
            k in (ctx.topic_name or "").lower() or k in (ctx.topic_code or "").lower()
            for k in ("paragraf", "anlam", "okuma", "reading", "clozer", "passage", "metin")
        )
        default_para = 180 if is_reading_topic else 40
        default_read = 75 if is_reading_topic else 45
        para_avg = int(style.get("paragraph_length_avg") or style.get("paragraph_words_avg") or default_para)
        reading = int(style.get("reading_time_sec_avg") or style.get("reading_time") or default_read)
        preferred_dist = list(style.get("distractor_patterns") or style.get("distractor_types") or [])

        profile = get_skill_profile(
            exam=ctx.exam,
            subject_code=ctx.subject_code,
            subject_name=ctx.subject_name,
            topic_code=ctx.topic_code,
            topic_name=ctx.topic_name,
        )
        skill_pool = skill_pool_for_context(
            profile,
            style,
            topic_code=ctx.topic_code,
            topic_name=ctx.topic_name,
        )
        stem_cycle = stem_cycle_for_profile(profile)

        forbidden_patterns = list(ctx.recent_patterns)
        used_skills = list(ctx.recent_skills)
        plans: list[QuestionPlan] = []

        for i in range(max(1, ctx.count)):
            skill = self._next_from_pool(i, used_skills, skill_pool)
            used_skills.append(skill)
            difficulty = _difficulty_for_band(ctx.difficulty_band, i, ctx.count)
            stem_type = stem_cycle[i % len(stem_cycle)]
            # Avoid recent stem/skill collisions when forbidden
            if stem_type in forbidden_patterns:
                stem_type = stem_cycle[(i + 3) % len(stem_cycle)]
            distractor = pick_distractor(
                index=i,
                forbidden=forbidden_patterns,
                preferred=preferred_dist,
            )
            forbidden_patterns.append(distractor)
            para_len = paragraph_length_for_stem(
                stem_type=stem_type,
                para_avg=para_avg,
                is_reading_topic=is_reading_topic,
            )
            plans.append(
                QuestionPlan(
                    exam=ctx.exam,
                    subject_code=ctx.subject_code,
                    subject_name=ctx.subject_name,
                    topic_code=ctx.topic_code,
                    topic_name=ctx.topic_name,
                    skill=skill,
                    difficulty=difficulty,
                    bloom=_bloom_for(difficulty),
                    reasoning_type=_reasoning_type(stem_type),
                    paragraph_length=para_len,
                    reading_time_sec=reading,
                    stem_type=stem_type,
                    distractor_pattern=distractor,
                    target_time_sec=max(45, reading + 15),
                    target_accuracy=max(0.35, min(0.75, 1.0 - difficulty / 150)),
                    forbidden_recent_patterns=list(forbidden_patterns[-5:]),
                    choice_count=choice_count,
                    index=i,
                )
            )
        return plans

    def _next_from_pool(self, index: int, used: list[str], pool: list[str]) -> str:
        if not pool:
            pool = ["problem_solving", "logical_reasoning", "analysis"]
        for offset in range(len(pool)):
            cand = pool[(index + offset) % len(pool)]
            if cand not in used:
                return cand
        return pool[index % len(pool)]

    # Backward-compatible alias (Türkçe DNA path only — prefer plan_batch).
    def _next_skill(self, index: int, used: list[str], style: dict) -> str:
        profile = get_skill_profile(subject_code="turkce", subject_name="Türkçe")
        pool = skill_pool_for_context(profile, style)
        return self._next_from_pool(index, used, pool)
