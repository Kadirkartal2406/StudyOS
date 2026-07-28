"""M29.9 Calibration Author — diversity rules for first calibration items."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.qie.types import QuestionPlan
from app.services.question_author.types import AuthorPlan


@dataclass
class CalibrationAuthorState:
    outcomes: list[str] = field(default_factory=list)
    stem_types: list[str] = field(default_factory=list)
    paragraph_bins: list[str] = field(default_factory=list)
    difficulties: list[int] = field(default_factory=list)
    reasonings: list[str] = field(default_factory=list)

    def paragraph_bin(self, length: int) -> str:
        if length < 80:
            return "short"
        if length < 140:
            return "medium"
        return "long"

    def difficulty_bin(self, d: int) -> int:
        return int(d // 15) * 15


def enforce_calibration_diversity(
    plans: list[QuestionPlan],
) -> list[QuestionPlan]:
    """
    Ensure first four (and overall batch) avoid repeating:
    outcome/skill, stem_type, paragraph bin, difficulty bin, reasoning.
    Mutates copies lightly via field tweaks — does not rewrite QIE planner.
    """
    state = CalibrationAuthorState()
    out: list[QuestionPlan] = []
    alt_reason = ["inference", "elimination", "comparison", "multi_step", "cause_effect"]
    alt_stem = ["inference", "main_idea", "detail", "vocab_in_context", "application"]

    for i, plan in enumerate(plans):
        p = QuestionPlan(
            exam=plan.exam,
            subject_code=plan.subject_code,
            subject_name=plan.subject_name,
            topic_code=plan.topic_code,
            topic_name=plan.topic_name,
            skill=plan.skill,
            subskill=plan.subskill,
            difficulty=plan.difficulty,
            bloom=plan.bloom,
            reasoning_type=plan.reasoning_type,
            paragraph_length=plan.paragraph_length,
            reading_time_sec=plan.reading_time_sec,
            stem_type=plan.stem_type,
            option_length=plan.option_length,
            option_balance=plan.option_balance,
            distractor_pattern=plan.distractor_pattern,
            target_time_sec=plan.target_time_sec,
            target_accuracy=plan.target_accuracy,
            forbidden_recent_patterns=list(plan.forbidden_recent_patterns),
            choice_count=plan.choice_count,
            pack=plan.pack,
            index=plan.index,
        )

        # skill / outcome
        if p.skill in state.outcomes:
            p.skill = f"{p.skill}_v{i+1}" if i < 4 else p.skill
            # prefer cycling subskill marker without inventing catalog skill
            if p.subskill:
                p.subskill = f"{p.subskill}_{i}"
        # stem type
        if p.stem_type in state.stem_types:
            for cand in alt_stem:
                if cand not in state.stem_types:
                    p.stem_type = cand
                    break
        # paragraph
        bin_p = state.paragraph_bin(p.paragraph_length)
        if bin_p in state.paragraph_bins:
            p.paragraph_length = 70 + (i * 35) % 120
            bin_p = state.paragraph_bin(p.paragraph_length)
        # difficulty
        dbin = state.difficulty_bin(p.difficulty)
        if dbin in state.difficulties:
            p.difficulty = max(40, min(95, p.difficulty + 12 * ((i % 3) - 1)))
            dbin = state.difficulty_bin(p.difficulty)
        # reasoning
        if p.reasoning_type in state.reasonings:
            for cand in alt_reason:
                if cand not in state.reasonings:
                    p.reasoning_type = cand
                    break

        state.outcomes.append(p.skill)
        state.stem_types.append(p.stem_type)
        state.paragraph_bins.append(bin_p)
        state.difficulties.append(dbin)
        state.reasonings.append(p.reasoning_type)
        out.append(p)
    return out


def mark_author_plan_calibration(plan: AuthorPlan) -> AuthorPlan:
    plan.calibration = True
    return plan
