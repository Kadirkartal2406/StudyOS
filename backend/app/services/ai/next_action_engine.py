"""
StudyOS — Decision Engine Projection (Next Action)

Alignment Sprint-1 + Sprint-3:
- Tek next_action; Observation > Decision
- Amaç odaklı Primary Action
- Mümkünse deep_link → Topic Work Surface (plan/pomodoro doğrudan değil)
- Work Surface karar üretmez; bu motor üretir, yüzey uygular
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.study_plan import StudyPlan, StudyPlanStatus
from app.schemas.dashboard import NextActionProjection
from app.schemas.revision import DashboardRevisionSummary
from app.services.ai.exam_experience_pack import get_pack


@dataclass(frozen=True)
class TopicRef:
    subject_code: str
    topic_code: str
    topic_name: str


@dataclass(frozen=True)
class CatalogTopic:
    subject_code: str
    topic_code: str
    topic_name: str
    subject_name: str | None = None


def exam_priority_subjects(exam_type: str) -> list[str]:
    """Sprint-11: Return priority subject prefixes for the given exam type."""
    pack = get_pack(exam_type)
    return list(pack.get("subject_priority_prefixes") or [])


def _filter_catalog_by_priority(
    catalog: list[CatalogTopic], exam_type: str | None
) -> list[CatalogTopic]:
    """Return catalog topics whose subject_code matches exam pack prefixes."""
    if not exam_type:
        return catalog
    prefixes = exam_priority_subjects(exam_type)
    if not prefixes:
        return catalog
    preferred = [
        c
        for c in catalog
        if any(c.subject_code.lower().startswith(p.lower()) for p in prefixes)
    ]
    return preferred if preferred else catalog


def _reorder_by_exam_priority(
    catalog: list[CatalogTopic],
    exam_type: str | None,
) -> list[CatalogTopic]:
    """Sprint 11 — Exam Experience Pack'e göre kataloğu yeniden sırala."""
    if not exam_type or not catalog:
        return catalog
    prefix_list = exam_priority_subjects(exam_type)
    if not prefix_list:
        return catalog
    priority: list[CatalogTopic] = []
    rest: list[CatalogTopic] = []
    for topic in catalog:
        code = topic.subject_code.lower()
        if any(code.startswith(p.lower()) for p in prefix_list):
            priority.append(topic)
        else:
            rest.append(topic)
    return priority + rest


def resolve_topic_ref(
    *,
    catalog: list[CatalogTopic],
    subject_hint: str | None,
    topic_hint: str | None,
) -> TopicRef | None:
    """Free-text subject/topic → topic_code (best-effort, migration yok)."""
    if not catalog:
        return None
    sub_h = (subject_hint or "").strip().lower()
    top_h = (topic_hint or "").strip().lower()

    # Exact topic name match (optionally scoped by subject)
    candidates = catalog
    if sub_h:
        scoped = [
            c
            for c in catalog
            if c.subject_code.lower() == sub_h
            or (c.subject_name and c.subject_name.lower() == sub_h)
            or sub_h in c.subject_code.lower()
        ]
        if scoped:
            candidates = scoped
    if top_h:
        for c in candidates:
            if c.topic_name.lower() == top_h or c.topic_code.lower() == top_h:
                return TopicRef(c.subject_code, c.topic_code, c.topic_name)
        for c in candidates:
            if top_h in c.topic_name.lower():
                return TopicRef(c.subject_code, c.topic_code, c.topic_name)
    return None


def _work_surface_path(ref: TopicRef) -> str:
    return f"/subjects/{ref.subject_code}/topics/{ref.topic_code}"


def build_next_action(
    *,
    today_plans: list[StudyPlan],
    revision: DashboardRevisionSummary | None,
    ai_reason: str | None = None,
    catalog: list[CatalogTopic] | None = None,
    revision_subject: str | None = None,
    revision_topic: str | None = None,
    exam_type: str | None = None,
) -> NextActionProjection:
    """Sunucu SSOT: tek Primary Action. Flutter / Work Surface karar vermez."""
    catalog = catalog or []
    # Sprint 11 — Sınav tipine göre konu önceliği
    catalog = _reorder_by_exam_priority(catalog, exam_type)

    due = revision.due_today if revision else 0
    if due > 0:
        ref = resolve_topic_ref(
            catalog=catalog,
            subject_hint=revision_subject,
            topic_hint=revision_topic or (revision.next_title if revision else None),
        )
        reason = (
            revision.overview_reason
            if revision and revision.overview_reason
            else f"Bugün {due} tekrar bekliyor."
        )
        overdue_days = revision.overdue_days if revision else None
        overdue_label = (
            f"{overdue_days} gün gecikmiş"
            if overdue_days is not None and overdue_days > 0
            else None
        )
        if overdue_label:
            reason = f"{reason} {overdue_label}".strip()
        if ai_reason:
            reason = f"{reason} {ai_reason}".strip()
        topic_label = ref.topic_name if ref else (revision.next_title if revision else "bu konu")
        if overdue_label:
            topic_label = f"{topic_label} · {overdue_label}"
        deep = _work_surface_path(ref) if ref else "/subjects"
        return NextActionProjection(
            title="Bu konu üzerinde tekrar yap",
            subtitle=topic_label,
            reason=reason,
            action_type="revision",
            deep_link_hint=deep,
            cta_label="Başla",
            confidence_tone="high",
            subject_code=ref.subject_code if ref else None,
            topic_code=ref.topic_code if ref else None,
            purpose="review",
            tool_hint="revision",
        )

    incomplete = [
        p
        for p in today_plans
        if p.status in (StudyPlanStatus.PLANNED, StudyPlanStatus.IN_PROGRESS)
    ]
    incomplete.sort(
        key=lambda p: (
            0 if p.status == StudyPlanStatus.IN_PROGRESS else 1,
            p.order_index if p.order_index is not None else 10_000,
        )
    )
    if incomplete:
        plan = incomplete[0]
        subject = (plan.subject or "").strip()
        topic = (plan.topic or "").strip()
        ref = resolve_topic_ref(
            catalog=catalog, subject_hint=subject, topic_hint=topic or plan.title
        )
        minutes = plan.estimated_minutes or 25
        questions = plan.target_question_count or 0
        reason = ai_reason or "Bugünkü sıradaki çalışma bloğun."
        topic_label = ref.topic_name if ref else (topic or plan.title or subject or "bu konu")
        if subject and topic_label and subject.casefold() not in topic_label.casefold():
            topic_label = f"{subject} · {topic_label}"
        deep = _work_surface_path(ref) if ref else "/subjects"
        duration_part = f"{minutes} dk"
        if questions > 0:
            duration_part = f"{duration_part} / {questions} soru"
        return NextActionProjection(
            title="Bu konu üzerinde çalış",
            subtitle=f"{topic_label} — {duration_part}",
            reason=reason,
            action_type="study_plan",
            deep_link_hint=deep,
            cta_label="Başla",
            confidence_tone="high",
            subject_code=ref.subject_code if ref else None,
            topic_code=ref.topic_code if ref else None,
            purpose="study",
            tool_hint="pomodoro",
        )

    # Observation — konu çözülemezse Subject container; rastgele ilk katalog konusu önerme
    reason = (
        ai_reason
        or "Henüz yeterli sinyal yok; seni tanımaya devam ediyoruz. Bir konu seçerek başla."
    )
    return NextActionProjection(
        title="Çalışmaya başla",
        subtitle="Derslerinden bir konu seç",
        reason=reason,
        action_type="focus",
        deep_link_hint="/subjects",
        cta_label="Dersleri Gör",
        confidence_tone="low",
        subject_code=None,
        topic_code=None,
        purpose="study",
        tool_hint=None,
    )


def build_action_for_topic(
    *,
    subject_code: str,
    topic_code: str,
    topic_name: str,
    revision_due_for_topic: bool,
    ai_reason: str | None = None,
) -> NextActionProjection:
    """
    Topic Work Surface için Decision Projection.
    Yüzey karar vermez — bu fonksiyon Decision Engine kurallarını topic kapsamında uygular.
    """
    ref = TopicRef(subject_code, topic_code, topic_name)
    deep = _work_surface_path(ref)
    if revision_due_for_topic:
        return NextActionProjection(
            title="Bu konu üzerinde tekrar yap",
            subtitle=topic_name,
            reason=ai_reason or "Bu konu için tekrar zamanı geldi.",
            action_type="revision",
            deep_link_hint=deep,
            cta_label="Başla",
            confidence_tone="high",
            subject_code=subject_code,
            topic_code=topic_code,
            purpose="review",
            tool_hint="revision",
        )
    return NextActionProjection(
        title="Bu konu üzerinde çalış",
        subtitle=f"{topic_name} · 25 dk",
        reason=ai_reason or "Bu konu üzerinde çalışmaya devam et.",
        action_type="study_plan",
        deep_link_hint=deep,
        cta_label="Başla",
        confidence_tone="high",
        subject_code=subject_code,
        topic_code=topic_code,
        purpose="study",
        tool_hint="pomodoro",
    )


def build_today_context_lines(
    *,
    today_plan_count: int,
    completed_plan_count: int,
    revision_due_today: int,
) -> list[str]:
    lines: list[str] = []
    remaining_blocks = max(today_plan_count - completed_plan_count, 0)
    if remaining_blocks > 0:
        lines.append(f"Bugün {remaining_blocks} çalışma bloğun kaldı")
    elif today_plan_count > 0:
        lines.append("Bugünkü çalışma blokların tamamlandı")
    if revision_due_today > 0:
        lines.append(f"Bugün {revision_due_today} tekrar bekliyor")
    return lines[:3]


def build_journey_line(
    *,
    active_exam_type: str | None,
    days_remaining: int | None,
    primary_university: str | None = None,
    primary_department: str | None = None,
) -> str | None:
    parts: list[str] = []
    if active_exam_type:
        parts.append(active_exam_type.upper())
    if primary_university:
        label = primary_university
        if primary_department:
            label = f"{primary_university} {primary_department}"
        parts.append(label)
    if days_remaining is not None:
        parts.append(f"{days_remaining} gün kaldı")
    if not parts:
        return None
    return " · ".join(parts)
