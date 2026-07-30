"""Question Planner — brain of QIE. LLM cannot change this plan."""

from __future__ import annotations

from app.services.qie.distractor_model import pick_distractor
from app.services.qie.types import GenerateContext, QuestionPlan

_BLOOM_BY_DIFFICULTY = [
    (40, "understand"),
    (60, "apply"),
    (75, "analyze"),
    (90, "evaluate"),
    (101, "create"),
]

_STEM_CYCLE = [
    "inference",
    "main_idea",
    "supporting_detail",
    "comparison",
    "sentence_ordering",
    "paragraph_completion",
    "vocabulary",
    "grammar",
    "cause_effect",
    "tone",
]

_SKILL_DEFAULTS = [
    "vocabulary",
    "sentence_meaning",
    "main_idea",
    "supporting_idea",
    "paragraph_completion",
    "sentence_ordering",
    "coherence",
    "grammar",
    "spelling",
    "punctuation",
    "logic",
    "mixed_reasoning",
]

_DIFF_BAND = {"easy": 45, "medium": 70, "hard": 85}


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

        forbidden_patterns = list(ctx.recent_patterns)
        used_skills = list(ctx.recent_skills)
        plans: list[QuestionPlan] = []

        for i in range(max(1, ctx.count)):
            skill = self._next_skill(i, used_skills, style)
            used_skills.append(skill)
            difficulty = _difficulty_for_band(ctx.difficulty_band, i, ctx.count)
            stem_type = _STEM_CYCLE[i % len(_STEM_CYCLE)]
            # Avoid recent stem/skill collisions when forbidden
            if stem_type in forbidden_patterns:
                stem_type = _STEM_CYCLE[(i + 3) % len(_STEM_CYCLE)]
            distractor = pick_distractor(
                index=i,
                forbidden=forbidden_patterns,
                preferred=preferred_dist,
            )
            forbidden_patterns.append(distractor)
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
                    reasoning_type=stem_type if stem_type in ("inference", "cause_effect") else "inference",
                    paragraph_length=para_avg,
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

    def _next_skill(self, index: int, used: list[str], style: dict) -> str:
        dist = style.get("skill_distribution") or {}
        pool = list(dist.keys()) if isinstance(dist, dict) and dist else list(_SKILL_DEFAULTS)
        for offset in range(len(pool)):
            cand = pool[(index + offset) % len(pool)]
            if cand not in used:
                return cand
        return pool[index % len(pool)]
