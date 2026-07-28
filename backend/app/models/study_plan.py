"""
StudyOS — StudyPlan Modeli
Kullanıcının günlük çalışma planı kalemleri. Bkz. docs/architecture/database-design.md §1.9

[ONAY GEREKTİRİR] database-design.md §1.9'da tanımlı önceki taslak (StudyPlan +
StudyPlanItem, student_id/subject_id FK'leri) `Student` ve `Subject` modelleri
henüz implemente edilmediği için kullanılamaz. Sprint-1.4 talebinde verilen alan
listesi (user_id FK, düz `subject`/`topic` string alanları, tekil tablo) yerine
uygulanmıştır. Bkz. Meeting-012 "Alınan Kararlar".
"""

import uuid
from datetime import UTC, date, datetime, time
from enum import StrEnum

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class StudyPlanStatus(StrEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class StudyPlan(Base):
    """Kullanıcının belirli bir güne ait çalışma planı kalemi."""

    __tablename__ = "study_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True)

    target_question_count: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    planned_start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    planned_end_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    status: Mapped[StudyPlanStatus] = mapped_column(
        String(20), nullable=False, default=StudyPlanStatus.PLANNED
    )

    completed_question_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    study_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Sprint-2.7 — Adaptive Planner (F1)
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    planner_draft_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planner_drafts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # ── Soft Delete ──────────────────────────────────────────────
    # Kullanıcı talebi: "Silinen plan tamamen silinmesin, soft delete kullan."
    # Alan listesinde açıkça yer almasa da kuralın uygulanabilmesi için gereklidir.
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<StudyPlan id={self.id} user_id={self.user_id} date={self.study_date} status={self.status}>"
