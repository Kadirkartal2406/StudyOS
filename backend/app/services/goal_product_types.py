"""
StudyOS — Product Goal Types (Sprint-3.0.2)
Kullanıcıya gösterilen hedef tipleri ↔ motor GoalType/Period eşlemesi.
LLM hedef üretmez; yalnızca ürün katmanı eşlemesi.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.models.goal import GoalPeriod, GoalType


class ProductGoalType(StrEnum):
    DAILY_STUDY_TIME = "daily_study_time"
    DAILY_QUESTIONS = "daily_questions"
    WEEKLY_QUESTIONS = "weekly_questions"
    NET_TARGET = "net_target"
    SCORE_TARGET = "score_target"
    RANK_TARGET = "rank_target"
    BRANCH_NET = "branch_net"
    EXAM_COUNT = "exam_count"
    REVISION_TARGET = "revision_target"


@dataclass(frozen=True)
class ProductGoalSpec:
    engine_type: GoalType
    period: GoalPeriod
    unit: str
    requires_subject: bool = False
    progress_sources: tuple[str, ...] = ()


PRODUCT_GOAL_SPECS: dict[ProductGoalType, ProductGoalSpec] = {
    ProductGoalType.DAILY_STUDY_TIME: ProductGoalSpec(
        GoalType.STUDY_TIME,
        GoalPeriod.DAILY,
        "dk",
        progress_sources=("study_session", "pomodoro"),
    ),
    ProductGoalType.DAILY_QUESTIONS: ProductGoalSpec(
        GoalType.QUESTION,
        GoalPeriod.DAILY,
        "soru",
        progress_sources=("question_record",),
    ),
    ProductGoalType.WEEKLY_QUESTIONS: ProductGoalSpec(
        GoalType.QUESTION,
        GoalPeriod.WEEKLY,
        "soru",
        progress_sources=("question_record",),
    ),
    ProductGoalType.NET_TARGET: ProductGoalSpec(
        GoalType.CUSTOM,
        GoalPeriod.CUSTOM,
        "net",
        progress_sources=("exam",),
    ),
    ProductGoalType.SCORE_TARGET: ProductGoalSpec(
        GoalType.CUSTOM,
        GoalPeriod.CUSTOM,
        "puan",
        progress_sources=("exam_target", "manual"),
    ),
    ProductGoalType.RANK_TARGET: ProductGoalSpec(
        GoalType.CUSTOM,
        GoalPeriod.CUSTOM,
        "sıra",
        progress_sources=("exam_target", "manual"),
    ),
    ProductGoalType.BRANCH_NET: ProductGoalSpec(
        GoalType.CUSTOM,
        GoalPeriod.CUSTOM,
        "net",
        requires_subject=True,
        progress_sources=("exam",),
    ),
    ProductGoalType.EXAM_COUNT: ProductGoalSpec(
        GoalType.CUSTOM,
        GoalPeriod.WEEKLY,
        "deneme",
        progress_sources=("exam",),
    ),
    ProductGoalType.REVISION_TARGET: ProductGoalSpec(
        GoalType.CUSTOM,
        GoalPeriod.WEEKLY,
        "tekrar",
        progress_sources=("revision",),
    ),
}

PRODUCT_GOAL_LABELS_TR: dict[ProductGoalType, str] = {
    ProductGoalType.DAILY_STUDY_TIME: "Günlük Çalışma Süresi",
    ProductGoalType.DAILY_QUESTIONS: "Günlük Soru Sayısı",
    ProductGoalType.WEEKLY_QUESTIONS: "Haftalık Soru Sayısı",
    ProductGoalType.NET_TARGET: "Net Hedefi",
    ProductGoalType.SCORE_TARGET: "Puan Hedefi",
    ProductGoalType.RANK_TARGET: "Sıralama Hedefi",
    ProductGoalType.BRANCH_NET: "Branş Neti",
    ProductGoalType.EXAM_COUNT: "Deneme Sayısı",
    ProductGoalType.REVISION_TARGET: "Revision Hedefi",
}


def resolve_product_goal(
    product: ProductGoalType,
) -> tuple[GoalType, GoalPeriod, ProductGoalSpec]:
    spec = PRODUCT_GOAL_SPECS[product]
    return spec.engine_type, spec.period, spec


def progress_sources_for(
    product: ProductGoalType | None, engine_type: GoalType
) -> list[str]:
    if product is not None and product in PRODUCT_GOAL_SPECS:
        return list(PRODUCT_GOAL_SPECS[product].progress_sources)
    return {
        GoalType.STUDY_TIME: ["study_session", "pomodoro"],
        GoalType.POMODORO: ["pomodoro", "study_session"],
        GoalType.QUESTION: ["question_record"],
        GoalType.SUBJECT: ["question_record"],
        GoalType.TOPIC: ["question_record"],
        GoalType.CUSTOM: ["manual"],
    }.get(engine_type, ["manual"])


def unit_for(product: ProductGoalType | None, engine_type: GoalType) -> str:
    if product is not None and product in PRODUCT_GOAL_SPECS:
        return PRODUCT_GOAL_SPECS[product].unit
    return {
        GoalType.STUDY_TIME: "dk",
        GoalType.POMODORO: "Pomodoro",
        GoalType.QUESTION: "soru",
        GoalType.SUBJECT: "soru",
        GoalType.TOPIC: "soru",
        GoalType.CUSTOM: "birim",
    }.get(engine_type, "birim")
