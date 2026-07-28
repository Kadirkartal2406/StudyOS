"""
StudyOS — Behavioral Learning Memory (LOS Module 7)
LOS § 7 — Kullanıcının zamanla oluşan davranış modeli.

NOT: Bu tablo kullanıcıya açık CRUD DEĞİLDİR.
     Sistem tarafından Evidence'dan sessizce güncellenir.
     Memory editörü ana ürün değildir.

Oluşum prensibi:
  1. Preference + Consistency Evidence → Memory'ye süzülür
  2. Tek olay overwrite etmez (yumuşak güncelleme)
  3. Memory Decide'ı bias eder; yerine geçmez
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BehavioralMemory(Base):
    """
    LOS § 7.1 — Kullanıcı başına tek behavioral memory kaydı.
    Tüm alanlar JSON; yavaş güncelleme prensibine göre değişir.
    """

    __tablename__ = "behavioral_memory"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_behavioral_memory_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── LOS § 7.1 — Öğrenilen alanlar ────────────────────────────
    # {peak_hours: [h,...], low_hours: [h,...], avg_start_hour: float}
    chronotype: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {avg_daily_minutes: float, avg_weekly_minutes: float, pattern: str}
    tempo: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {topic_code → {avg_accuracy: float, trend: float, sample: int}, ...}
    difficulty_signature: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {topic_code → {sessions_to_medium_conf: int, speed_score: float}, ...}
    acquisition_speed: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {topic_code → {decay_rate: float, forgetting_risk: str}, ...}
    forgetting_curve: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {preferred_duration: int, abort_rate: float, avg_actual: float}
    pomodoro_signature: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {avg_break_minutes: float, extension_rate: float, early_exit_rate: float}
    break_signature: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {type → usage_count: int} (video/pdf/question/…)
    resource_preference: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {weekday_distribution: {...}, pattern: 'consistent'|'bursty'}
    schedule_signature: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {skip_days: [weekday,...], cancellation_clusters: [...]}
    motivation_dips: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {accept_rate: float, reject_rate: float, cooldown_skips: int}
    plan_receptivity: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # {primary_exam: str, active_exam: str, days_remaining: int|null}
    exam_context: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<BehavioralMemory user={self.user_id}>"
