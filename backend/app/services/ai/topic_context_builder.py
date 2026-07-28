"""
StudyOS — Topic Context Builder (AI Sprint - FAZ 1)
LOS § 3+4+7 — Topic-scoped lightweight AI context.

Global ContextBuilder'dan farklı olarak:
  - Tek Topic'e odaklanmış (subject_code + topic_code)
  - Hafif: yalnızca AI servisleri için gereken veri
  - Confidence + Evidence + Behavioral + Resources bağlamı
  - LLM'e giden prompt context'ini oluşturur

LOS prensibi: Bu builder karar vermez.
Yalnızca AI servislerine bilgi sağlar.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_confidence import ConfidenceLevel
from app.services.behavioral_memory_service import BehavioralMemoryService
from app.services.confidence_engine import ConfidenceEngine
from app.services.evidence_service import EvidenceService
from app.services.study_resource_service import StudyResourceService


@dataclass
class TopicAIContext:
    """
    Topic bazlı AI context - tüm AI servislerinin ortak girdisi.
    LOS § 3+4+7 verilerini tek yapıda toplar.
    """
    # ── Kimlik ──────────────────────────────────────────────────
    user_id: uuid.UUID
    subject_code: str
    topic_code: str
    topic_name: str | None = None
    subject_name: str | None = None

    # ── Confidence (LOS § 4) ───────────────────────────────
    confidence_level: str = ConfidenceLevel.UNKNOWN
    belief: float = 0.5
    uncertainty: float = 1.0
    trend_direction: float = 0.0
    consistency_score: float = 0.0
    days_since_last_evidence: int | None = None
    forgetting_applied: bool = False

    # ── Evidence Aggregate (LOS § 3) ────────────────────────
    performance_sample_count: int = 0
    weighted_accuracy: float | None = None
    effort_minutes: float = 0.0
    last_evidence_at: str | None = None  # ISO format

    # ── Behavioral Memory (LOS § 7) ───────────────────────
    peak_hours: list[int] = field(default_factory=list)
    avg_daily_minutes: float = 120.0
    preferred_pomodoro_duration: int = 25
    avg_completion_rate: float = 0.8
    topic_difficulty_signature: dict = field(default_factory=dict)
    # topic için kişiye özel zorluk: {avg_accuracy, sample, trend}

    # ── Resources (Notebook kaynak listesi) ────────────────
    resource_count: int = 0
    resources: list[dict] = field(default_factory=list)
    # [{title, resource_type, status, url, provider}]

    # ── Knowledge Layer (Sprint 19 / LOS §12) ──────────────
    knowledge_ready: bool = False
    knowledge_chunk_count: int = 0
    knowledge_citation_count: int = 0
    knowledge_summary: str | None = None
    knowledge_passages: list[dict] = field(default_factory=list)
    # [{source_title, page_hint, content, score}]

    # ── Active Exam (M17.3) ───────────────────────────────
    active_exam_type: str | None = None

    # ── Meta ────────────────────────────────────────────────
    built_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_prompt_dict(self) -> dict:
        """
        AI prompt için serialize edilmiş dict.
        Sadece AI'nın ihtiyacı olan alanlar.
        """
        accuracy_pct = (
            round(self.weighted_accuracy * 100, 1)
            if self.weighted_accuracy is not None
            else None
        )
        behavioral_hint = self._behavioral_hint()
        return {
            "topic": {
                "code": self.topic_code,
                "name": self.topic_name or self.topic_code,
                "subject_code": self.subject_code,
                "subject_name": self.subject_name or self.subject_code,
            },
            "exam": {
                "active_exam_type": self.active_exam_type,
            },
            "confidence": {
                "level": self.confidence_level,
                "belief_pct": round(self.belief * 100, 1),
                "uncertainty_pct": round(self.uncertainty * 100, 1),
                "trend": _trend_label(self.trend_direction),
                "forgetting": self.forgetting_applied,
                "days_silent": self.days_since_last_evidence,
            },
            "evidence": {
                "sample_count": self.performance_sample_count,
                "accuracy_pct": accuracy_pct,
                "effort_minutes": round(self.effort_minutes, 0),
                "last_at": self.last_evidence_at,
            },
            "behavioral": {
                "hint": behavioral_hint,
                "peak_hours": self.peak_hours[:3],
                "preferred_duration": self.preferred_pomodoro_duration,
                "avg_completion": round(self.avg_completion_rate * 100, 0),
                "topic_avg_accuracy": self.topic_difficulty_signature.get("avg_accuracy"),
            },
            "resources": {
                "count": self.resource_count,
                "items": self.resources[:5],
            },
            "knowledge": {
                "ready": self.knowledge_ready,
                "chunk_count": self.knowledge_chunk_count,
                "citation_count": self.knowledge_citation_count,
                "summary": self.knowledge_summary,
                "passages": self.knowledge_passages[:5],
            },
        }

    def _behavioral_hint(self) -> str | None:
        """Kısa behavioral ipucu metni."""
        if self.peak_hours:
            hours_str = ", ".join(f"{h:02d}:00" for h in self.peak_hours[:2])
            return f"En verimli saatler: {hours_str}"
        return None

    @property
    def needs_explain(self) -> bool:
        """Explain trigger: düşük confidence veya yeni hata."""
        return self.confidence_level in (ConfidenceLevel.LOW, ConfidenceLevel.CONFLICTED)

    @property
    def quiz_difficulty(self) -> str:
        """Confidence seviyesine göre önerilen quiz zorluğu."""
        if self.confidence_level == ConfidenceLevel.HIGH:
            return "hard"
        if self.confidence_level == ConfidenceLevel.MEDIUM:
            return "medium"
        return "easy"


def _trend_label(trend: float) -> str:
    if trend > 0.15:
        return "rising"
    if trend < -0.15:
        return "falling"
    return "stable"


class TopicContextBuilder:
    """
    LOS § 3+4+7 — Topic-scoped AI context builder.

    Kullanım:
        builder = TopicContextBuilder(db)
        ctx = await builder.build(user_id, subject_code, topic_code)
        prompt_dict = ctx.to_prompt_dict()
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_svc = EvidenceService(db)
        self.confidence_engine = ConfidenceEngine(db)
        self.behavioral_svc = BehavioralMemoryService(db)
        self.resource_svc = StudyResourceService(db)

    async def build(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
        *,
        topic_name: str | None = None,
        subject_name: str | None = None,
    ) -> TopicAIContext:
        """
        Topic için AI context oluştur.
        Hata durumunda varsayılan değerlerle devam et (fire-and-forget).
        """
        ctx = TopicAIContext(
            user_id=user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            topic_name=topic_name,
            subject_name=subject_name,
        )

        # M17.3 — Active Exam context (Explain örnekleri sınava göre)
        try:
            from app.services.learning_profile_service import LearningProfileService

            effective, _, _ = await LearningProfileService(self.db).resolve_active_scope(
                user_id
            )
            ctx.active_exam_type = effective
        except Exception:
            pass

        # 1. Confidence (LOS § 4)
        try:
            conf = await self.confidence_engine.get_for_topic(user_id, topic_code)
            if conf is not None:
                ctx.confidence_level = conf.confidence_level
                ctx.belief = conf.belief
                ctx.uncertainty = conf.uncertainty
                ctx.trend_direction = conf.trend_direction
                ctx.consistency_score = conf.consistency_score
                ctx.days_since_last_evidence = conf.days_since_last_evidence
                ctx.forgetting_applied = conf.forgetting_applied
        except Exception:
            pass

        # 2. Evidence Aggregate (LOS § 3)
        try:
            since_mid = datetime.now(UTC) - timedelta(days=21)
            agg = await self.evidence_svc.topic_aggregate(
                user_id, topic_code, since=since_mid
            )
            ctx.performance_sample_count = agg.get("performance_sample_count", 0)
            ctx.weighted_accuracy = agg.get("weighted_accuracy")
            ctx.effort_minutes = agg.get("effort_minutes", 0.0)
            ctx.last_evidence_at = agg.get("last_evidence_at")
        except Exception:
            pass

        # 3. Behavioral Memory (LOS § 7)
        try:
            behavioral = await self.behavioral_svc.get_behavioral_context(user_id)
            ctx.peak_hours = behavioral.get("peak_hours", [])
            ctx.avg_daily_minutes = behavioral.get("avg_daily_minutes", 120.0)
            ctx.preferred_pomodoro_duration = behavioral.get("preferred_pomodoro_duration", 25)
            ctx.avg_completion_rate = behavioral.get("avg_completion_rate", 0.8)
            # Topic-specific difficulty signature
            mem = await self.behavioral_svc.get_or_create(user_id)
            topic_sig = mem.difficulty_signature.get(topic_code, {})
            ctx.topic_difficulty_signature = topic_sig
        except Exception:
            pass

        # 4. Resources / Notebook — Topic-first only (M17.2: no subject fallback)
        try:
            resource_list = await self.resource_svc.list_resources(
                user_id, topic_code=topic_code, subject_code=subject_code
            )
            # Exclude archived from AI context
            active_items = [
                r
                for r in resource_list.items
                if str(r.status).split(".")[-1].lower() != "archived"
            ]
            ctx.resource_count = len(active_items)
            ctx.resources = [
                {
                    "title": r.title,
                    "resource_type": str(r.resource_type),
                    "status": str(r.status),
                    "provider": r.provider,
                    "url": r.url,
                }
                for r in active_items[:10]
            ]
        except Exception:
            pass

        # 5. Knowledge Layer (LOS §12) — Decision değil
        try:
            from app.services.knowledge_service import KnowledgeService

            kn = KnowledgeService(self.db)
            notebook = await kn.get_notebook(
                user_id, subject_code, topic_code, topic_name=topic_name
            )
            ctx.knowledge_chunk_count = notebook.chunk_count
            ctx.knowledge_citation_count = notebook.citation_count
            ctx.knowledge_summary = notebook.ai_summary
            ctx.knowledge_ready = notebook.chunk_count > 0
            if ctx.knowledge_ready:
                query = topic_name or topic_code
                passages = await kn.retrieve_for_topic(
                    user_id, subject_code, topic_code, query, top_k=5
                )
                ctx.knowledge_passages = [
                    {
                        "source_title": p.source_title,
                        "page_hint": p.page_hint,
                        "content": p.content[:500],
                        "score": p.score,
                        "source_id": str(p.source_id) if p.source_id else None,
                        "chunk_id": str(p.chunk_id) if p.chunk_id else None,
                    }
                    for p in passages
                ]
        except Exception:
            pass

        return ctx
