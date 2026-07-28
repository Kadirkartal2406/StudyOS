"""
StudyOS — Rule Engine
Sprint-2.0: LLM yok; InsightContext → öneri listesi.
Sprint-3.1.B: her öneriye RuleEngine `reason` (evidence) eklenir.
"""

from app.core.constants import (
    AI_IDLE_DAYS_THRESHOLD,
    AI_LOW_ACCURACY_THRESHOLD,
    AI_STUDY_DROP_PCT_THRESHOLD,
    AI_SUBJECT_NEGLECT_ENABLED,
)
from app.schemas.ai_insights import AiRecommendation
from app.services.ai.insight_engine import InsightContext


class RuleEngine:
    """Sabit kurallarla öneri üretir."""

    def generate(self, ctx: InsightContext) -> list[AiRecommendation]:
        items: list[AiRecommendation] = []

        if not ctx.has_enough_data:
            items.append(
                AiRecommendation(
                    code="insufficient_data",
                    message=(
                        "Henüz yeterli çalışma verisi yok. "
                        "Bir Pomodoro veya soru kaydı ekleyerek koçu besleyebilirsin."
                    ),
                    priority=50,
                    category="onboarding",
                    reason="Yeterli oturum veya soru kaydı henüz oluşmadı.",
                )
            )
            return items

        if (
            ctx.days_since_last_study is not None
            and ctx.days_since_last_study >= AI_IDLE_DAYS_THRESHOLD
        ):
            days = ctx.days_since_last_study
            items.append(
                AiRecommendation(
                    code="idle_streak",
                    message="Çalışmaya tekrar başlaman gerekiyor.",
                    priority=10,
                    category="habit",
                    reason=f"Son çalışmandan bu yana {days} gün geçti.",
                )
            )

        if ctx.today_study_minutes == 0 and ctx.streak_days > 0:
            items.append(
                AiRecommendation(
                    code="streak_at_risk",
                    message="Bugün en az 1 Pomodoro önerilir — streak'in bozulmasın.",
                    priority=15,
                    category="streak",
                    reason=f"Bugün henüz çalışma yok; mevcut streak {ctx.streak_days} gün.",
                )
            )

        if (
            ctx.previous_week_study_minutes > 0
            and ctx.week_study_minutes < ctx.previous_week_study_minutes
        ):
            drop = (
                (ctx.previous_week_study_minutes - ctx.week_study_minutes)
                / ctx.previous_week_study_minutes
                * 100
            )
            if drop >= AI_STUDY_DROP_PCT_THRESHOLD:
                items.append(
                    AiRecommendation(
                        code="performance_drop",
                        message="Performansında düşüş var — son 7 günde çalışma süren azaldı.",
                        priority=20,
                        category="trend",
                        reason=(
                            f"Bu hafta {ctx.week_study_minutes} dk; "
                            f"önceki hafta {ctx.previous_week_study_minutes} dk "
                            f"(%{drop:.0f} düşüş)."
                        ),
                    )
                )

        for subject, rate in ctx.low_accuracy_subjects:
            if rate < AI_LOW_ACCURACY_THRESHOLD:
                items.append(
                    AiRecommendation(
                        code="low_accuracy",
                        message=f"{subject} tekrar önerilir (doğruluk %{rate:.0f}).",
                        priority=25,
                        category="accuracy",
                        reason=f"{subject} doğruluk oranı %{rate:.0f} — eşik altında.",
                    )
                )

        if AI_SUBJECT_NEGLECT_ENABLED:
            for subject in ctx.neglected_subjects[:3]:
                items.append(
                    AiRecommendation(
                        code="neglected_subject",
                        message=f"{subject} dersi tekrar edilmeli — son 10 günde çalışılmadı.",
                        priority=30,
                        category="coverage",
                        reason=f"{subject}: son 10 gündür tekrar yapılmadı.",
                    )
                )

        if ctx.pomodoro_completion_rate > 0 and ctx.pomodoro_completion_rate < 50:
            items.append(
                AiRecommendation(
                    code="pomodoro_low",
                    message=(
                        f"Pomodoro tamamlanma oranın %{ctx.pomodoro_completion_rate:.0f}. "
                        "Daha kısa odak süreleri deneyebilirsin."
                    ),
                    priority=40,
                    category="pomodoro",
                    reason=(
                        f"Pomodoro tamamlanma oranı %{ctx.pomodoro_completion_rate:.0f} "
                        "(hedef ≥ %50)."
                    ),
                )
            )

        # Sprint-2.1 — Goal Engine kuralları (Goal oluşturmaz)
        if ctx.active_goals_count > 0 and ctx.top_goal_title:
            pct = ctx.top_goal_progress
            if pct >= 82:
                items.append(
                    AiRecommendation(
                        code="goal_almost_done",
                        message=(
                            f"«{ctx.top_goal_title}» hedefinin %{pct:.0f}'ini tamamladın. "
                            "Son sprint için tempoyu koru."
                        ),
                        priority=12,
                        category="goal",
                        reason=f"Hedef ilerlemesi %{pct:.0f} — bitişe yakın.",
                    )
                )
            elif pct >= 40 and (
                ctx.days_left_in_top_goal is not None and ctx.days_left_in_top_goal <= 3
            ):
                per_day = (
                    round(ctx.top_goal_remaining / max(ctx.days_left_in_top_goal, 1), 0)
                    if ctx.top_goal_remaining > 0
                    else 0
                )
                items.append(
                    AiRecommendation(
                        code="goal_behind",
                        message=(
                            f"«{ctx.top_goal_title}» için yetişmek üzere "
                            f"bugün yaklaşık {per_day:.0f} birim ilerleme önerilir."
                        ),
                        priority=14,
                        category="goal",
                        reason=(
                            f"Kalan süre {ctx.days_left_in_top_goal} gün; "
                            f"ilerleme %{pct:.0f}."
                        ),
                    )
                )
            elif ctx.top_goal_eta_hint:
                items.append(
                    AiRecommendation(
                        code="goal_on_track",
                        message=(
                            f"Hedefinin %{pct:.0f}'ini tamamladın. "
                            f"{ctx.top_goal_eta_hint}."
                        ),
                        priority=35,
                        category="goal",
                        reason=f"Hedef yolunda; ETA: {ctx.top_goal_eta_hint}.",
                    )
                )

        if not items:
            items.append(
                AiRecommendation(
                    code="keep_going",
                    message="Güzel gidiyorsun — düzenli temponu koru.",
                    priority=90,
                    category="motivation",
                    reason="Kritik uyarı kuralı tetiklenmedi; mevcut tempo uygun.",
                )
            )

        items.sort(key=lambda r: r.priority)
        return items
