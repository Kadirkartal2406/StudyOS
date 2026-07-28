"""
Sprint 20 — Coach message builder (template; LLM zorunlu değil).
Mevcut Decision / Next Action'ı kullanıcı diline çevirir.
"""

from __future__ import annotations

from app.schemas.coach import (
    CoachFollowUp,
    CoachReason,
    CoachTodayMessage,
    CoachWin,
    KnowledgeCoachHint,
)
from app.schemas.dashboard import NextActionProjection


def build_today_message(
    *,
    next_action: NextActionProjection | None,
    insight_message: str | None,
    insight_reason: str | None,
    confidence_level: str | None,
    assessment_note: str | None,
    habit_hint: str | None,
    knowledge: KnowledgeCoachHint | None,
    win: CoachWin | None,
    revision_due: bool,
) -> CoachTodayMessage:
    if next_action is None and not insight_message:
        return CoachTodayMessage(
            headline="Bugün seni dinliyorum",
            body=(
                "Henüz yeterli sinyal yok. Kısa bir oturum veya mini assessment "
                "ile seni daha iyi tanıyabilirim."
            ),
            reasons=[
                CoachReason(
                    code="observing",
                    label="Gözlem",
                    detail="Observation / calibrating — Decision tam değil",
                )
            ],
            deep_link_hint="/subjects",
            cta_label="Derslere git",
            habit_hint=habit_hint,
            win=win,
        )

    title = (next_action.title if next_action else None) or insight_message or "Bugünkü odak"
    reason_raw = (
        (next_action.reason if next_action else None)
        or insight_reason
        or "Mevcut öğrenme durumuna göre"
    )
    topic = None
    subject = None
    deep = "/subjects"
    cta = "Başla"
    if next_action:
        topic = next_action.topic_code
        subject = next_action.subject_code
        deep = next_action.deep_link_hint or deep
        cta = next_action.cta_label or cta

    minutes = 20
    if next_action and next_action.tool_hint == "pomodoro":
        minutes = 25
    if next_action and next_action.action_type == "revision":
        minutes = 15

    reasons: list[CoachReason] = [
        CoachReason(code="next_action", label="Today kararı", detail=reason_raw)
    ]
    if confidence_level:
        reasons.append(
            CoachReason(
                code="confidence",
                label="Confidence",
                detail=f"Seviye: {confidence_level.upper()}",
            )
        )
    if assessment_note:
        reasons.append(
            CoachReason(
                code="assessment",
                label="Assessment",
                detail=assessment_note,
            )
        )
    if revision_due:
        reasons.append(
            CoachReason(
                code="revision",
                label="Revision",
                detail="Bugün tekrar zamanı gelmiş konular var",
            )
        )

    focus_name = topic or subject or "öncelikli konu"
    body_parts = [
        f"Bugün {focus_name} için yaklaşık {minutes} dakika ayırmanı öneriyorum.",
        f"Çünkü {reason_raw.rstrip('.')}.",
    ]
    if confidence_level and confidence_level.lower() in ("low", "medium", "conflicted"):
        body_parts.append(
            "Kısa ve odaklı bir çalışma Confidence'ini yükseltmeye yardımcı olur."
        )
    if knowledge and knowledge.teach_line:
        body_parts.append(knowledge.teach_line)

    follow_ups: list[CoachFollowUp] = []
    if next_action and next_action.action_type != "revision":
        follow_ups.append(
            CoachFollowUp(
                kind="quiz",
                title="Anladığını görmek için 5 soru",
                detail="Explain veya çalışma sonrası kısa quiz",
                deep_link_hint=(
                    f"/quiz-session?subject_code={subject or ''}&topic_code={topic or ''}"
                    if subject and topic
                    else "/subjects"
                ),
                cta_label="Quiz",
            )
        )
    if revision_due:
        follow_ups.append(
            CoachFollowUp(
                kind="revision",
                title="Revision'ı erteleme",
                detail="Geciken tekrarlar Confidence'i düşürür",
                deep_link_hint="/revisions",
                cta_label="Tekrarlar",
            )
        )
    if knowledge and knowledge.next_step:
        follow_ups.append(
            CoachFollowUp(
                kind="knowledge",
                title=knowledge.next_step,
                detail=knowledge.page_hint,
                deep_link_hint=knowledge.deep_link_hint,
                cta_label="Kaynağa git",
            )
        )

    return CoachTodayMessage(
        headline=title if len(title) < 80 else title[:77] + "…",
        body=" ".join(body_parts),
        focus_topic=topic,
        focus_subject=subject,
        suggested_minutes=minutes,
        reasons=reasons,
        habit_hint=habit_hint,
        knowledge_hint=knowledge.summary if knowledge else None,
        win=win,
        follow_ups=follow_ups[:3],
        deep_link_hint=deep,
        cta_label=cta,
        next_action_title=next_action.title if next_action else None,
        next_action_reason=reason_raw,
    )
