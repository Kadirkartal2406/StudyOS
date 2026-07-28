"""
StudyOS — Generated Question Modeli (AI Sprint - FAZ 4)
LOS § 3+4 — AI tarafından üretilen sorular.

Bu tablo:
  1. AI'nın Confidence + Evidence verisiyle ürettigi soruları saklar
  2. Kullanıcı yanıtladığında Evidence sistemine geri beslenir
  3. 'Rastgele soru' degil; LOS-calibrated soru üretimi

NOT: LOS karar vermez; AI üretir, Evidence güncellenir.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class GeneratedQuestionDifficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GeneratedQuestionStatus(StrEnum):
    PENDING = "pending"       # Henüz yanıtlanmadı
    ANSWERED = "answered"     # Yanıtlandı
    SKIPPED = "skipped"       # Atlandı
    EXPIRED = "expired"       # Süresi doldu


class GeneratedQuestion(Base):
    """
    LOS § 3+4 — AI tarafından üretilen Topic başlı soru.
    Yanıtlandığında EvidenceService.ingest_question_record() çağrılır.
    """
    __tablename__ = "generated_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Topic kimliği (LOS § 3 Bind) ────────────────────────
    subject_code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_code: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    # ── Soru içeriği ───────────────────────────────────────
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # {A: text, B: text, C: text, D: text, E: text}
    correct_option: Mapped[str] = mapped_column(String(5), nullable=False)
    # A | B | C | D | E
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Neden doğru cevap bu?

    # ── Kalibrasyon (LOS § 4 girdisi) ──────────────────────
    difficulty: Mapped[str] = mapped_column(
        String(20), nullable=False, default=GeneratedQuestionDifficulty.MEDIUM
    )
    confidence_level_at_generation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    belief_at_generation: Mapped[float | None] = mapped_column(nullable=True)

    # ── Durum ───────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=GeneratedQuestionStatus.PENDING, index=True
    )
    user_answer: Mapped[str | None] = mapped_column(String(5), nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Üretim meta ──────────────────────────────────────
    generation_trigger: Mapped[str] = mapped_column(String(40), nullable=False, default="on_demand")
    # on_demand | policy_triggered | session_end
    ai_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    generation_context: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    # Hangi confidence/evidence verisiyle üretildiği (audit trail)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Yanıtlanmadan bu süre geçerse → expired

    def __repr__(self) -> str:
        return f"<GeneratedQuestion {self.topic_code} diff={self.difficulty} status={self.status}>"
