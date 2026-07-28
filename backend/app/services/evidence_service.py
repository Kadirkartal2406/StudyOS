"""
StudyOS — Evidence Service (LOS Module 1)
LOS § 3 — Evidence Engine: Sense → Bind → Evidence

Bu servis:
  1. Bind: Olayı (session/QR/revision) topic_code'a bağlar
  2. Ingest: TopicEvidence kaydı oluşturur
  3. Quality: Her olayın güvenilirliğini hesaplar

RuleEngine / Confidence Engine bu servisten OKUR; bu servis karar vermez.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic_evidence import (
    EvidenceCategory,
    EvidenceHorizon,
    EvidenceSourceType,
    TopicEvidence,
)
from app.repositories.topic_evidence_repository import TopicEvidenceRepository

if TYPE_CHECKING:
    from app.models.question_record import QuestionRecord
    from app.models.revision import RevisionItem, RevisionReview
    from app.models.study_session import StudySession
    from app.models.topic_quiz import TopicQuizGeneration

# ── Sabitler ──────────────────────────────────────────────────────────────────

_UNBOUND = "unbound"
_NOISE_DURATION_THRESHOLD = 5      # < 5 dk oturum → behavioral_micro (gürültü adayı)
_SHORT_SESSION_THRESHOLD = 10      # 10–25 dk → orta kalite
_FULL_SESSION_THRESHOLD = 20       # ≥ 20 dk → yüksek kalite effort
_MIN_QR_COUNT = 3                  # < 3 soru → düşük kalite

# RevisionGrade → performans sinyali (0–1 arası normalized)
_GRADE_SIGNAL = {
    "easy": 1.0,
    "good": 0.75,
    "hard": 0.35,
    "again": 0.05,
}

# QuestionDifficulty → kalite katsayısı
_DIFFICULTY_QUALITY = {
    "easy": 0.60,
    "medium": 0.80,
    "hard": 1.00,
    None: 0.70,
}


class EvidenceService:
    """
    LOS § 3 — Evidence ingestion: Bind + ingest + quality.

    Kullanım:
        svc = EvidenceService(db)
        await svc.ingest_session(session)
        await svc.ingest_question_record(qr, catalog)
        await svc.ingest_revision_review(review, item, catalog)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TopicEvidenceRepository(db)

    # ── Bind ──────────────────────────────────────────────────────────────────

    def bind(
        self,
        *,
        subject_code: str | None,
        topic_code: str | None,
        subject_hint: str | None = None,
        topic_hint: str | None = None,
        catalog: list | None = None,
    ) -> tuple[str, str]:
        """
        Canonical (subject_code, topic_code) döndür.
        Önce explicit kod; yoksa catalog üzerinden fuzzy match dene.
        Bulunamazsa "unbound".
        """
        # 1. Explicit canonical code — en güvenilir
        if subject_code and topic_code and subject_code != _UNBOUND:
            return subject_code, topic_code

        # 2. Catalog fuzzy bind (next_action_engine.resolve_topic_ref benzeri)
        if catalog and (subject_hint or topic_hint):
            ref = self._fuzzy_bind(
                catalog=catalog,
                subject_hint=subject_hint,
                topic_hint=topic_hint,
            )
            if ref:
                return ref

        # 3. Free-text → unresolved (düşük kalite ama sakla)
        if subject_hint:
            sc = _normalize_code(subject_hint)
            tc = _normalize_code(topic_hint) if topic_hint else sc
            return sc, tc

        return _UNBOUND, _UNBOUND

    def _fuzzy_bind(
        self,
        *,
        catalog: list,
        subject_hint: str | None,
        topic_hint: str | None,
    ) -> tuple[str, str] | None:
        """Catalog içinde en iyi eşleşmeyi bul."""
        if not catalog:
            return None
        sub_h = (subject_hint or "").strip().lower()
        top_h = (topic_hint or "").strip().lower()

        candidates = catalog
        if sub_h:
            scoped = [
                c for c in catalog
                if (
                    (getattr(c, "subject_code", None) or "").lower() == sub_h
                    or sub_h in (getattr(c, "subject_code", None) or "").lower()
                    or (getattr(c, "subject_name", None) or "").lower() == sub_h
                )
            ]
            if scoped:
                candidates = scoped

        if top_h:
            for c in candidates:
                tc_name = (getattr(c, "topic_name", None) or getattr(c, "name", None) or "").lower()
                tc_code = (getattr(c, "topic_code", None) or getattr(c, "code", None) or "").lower()
                if tc_name == top_h or tc_code == top_h:
                    return getattr(c, "subject_code", _UNBOUND), getattr(c, "topic_code", getattr(c, "code", _UNBOUND))
            for c in candidates:
                tc_name = (getattr(c, "topic_name", None) or getattr(c, "name", None) or "").lower()
                if top_h in tc_name:
                    return getattr(c, "subject_code", _UNBOUND), getattr(c, "topic_code", getattr(c, "code", _UNBOUND))

        if candidates and sub_h:
            c = candidates[0]
            return getattr(c, "subject_code", _UNBOUND), getattr(c, "topic_code", getattr(c, "code", _UNBOUND))

        return None

    # ── Ingest: StudySession (Effort + Behavioral Micro) ──────────────────────

    async def ingest_session(
        self,
        session: StudySession,
        *,
        catalog: list | None = None,
    ) -> list[TopicEvidence]:
        """
        Oturum tamamlandığında çağrılır.
        Üretilen evidence kategorileri:
          - EFFORT: tamamlama oranı + süre
          - BEHAVIORAL_MICRO: çok kısa oturum (gürültü sinyali)
        """
        if await self.repo.already_ingested(
            EvidenceSourceType.STUDY_SESSION, session.id
        ):
            return []

        subject_code, topic_code = self.bind(
            subject_code=session.subject_code,
            topic_code=session.topic_code,
            catalog=catalog,
        )
        is_bound = subject_code != _UNBOUND

        actual = session.actual_duration_minutes or 0
        planned = session.planned_duration_minutes or 25
        occurred = session.ended_at or session.started_at or datetime.now(UTC)

        results: list[TopicEvidence] = []

        # A. Effort Evidence
        completion_ratio = min(actual / max(planned, 1), 1.0)
        effort_quality = _effort_quality(actual)

        effort_ev = TopicEvidence(
            user_id=session.user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            category=EvidenceCategory.EFFORT,
            horizon=EvidenceHorizon.INSTANT,
            value=completion_ratio,
            quality_weight=effort_quality if is_bound else effort_quality * 0.5,
            source_type=EvidenceSourceType.STUDY_SESSION,
            source_id=session.id,
            metadata_={
                "actual_minutes": actual,
                "planned_minutes": planned,
                "completion_ratio": completion_ratio,
                "bound": is_bound,
            },
            occurred_at=occurred,
        )
        results.append(await self.repo.add_evidence(effort_ev))

        # B. Behavioral Micro: aşırı kısa oturum → gürültü sinyali
        if actual < _NOISE_DURATION_THRESHOLD:
            noise_ev = TopicEvidence(
                user_id=session.user_id,
                subject_code=subject_code,
                topic_code=topic_code,
                category=EvidenceCategory.BEHAVIORAL_MICRO,
                horizon=EvidenceHorizon.INSTANT,
                value=0.1,   # düşük sinyal — "çok kısa"
                quality_weight=0.3,
                source_type=EvidenceSourceType.STUDY_SESSION,
                source_id=session.id,
                metadata_={
                    "type": "short_session",
                    "actual_minutes": actual,
                },
                occurred_at=occurred,
            )
            results.append(await self.repo.add_evidence(noise_ev))

        # C. Temporal Evidence: çalışma saati bilgisi
        hour = occurred.hour
        temporal_ev = TopicEvidence(
            user_id=session.user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            category=EvidenceCategory.TEMPORAL,
            horizon=EvidenceHorizon.SHORT,
            value=actual / 60.0,  # saat cinsinden
            quality_weight=0.6,
            source_type=EvidenceSourceType.STUDY_SESSION,
            source_id=session.id,
            metadata_={
                "hour_of_day": hour,
                "weekday": occurred.weekday(),
                "actual_minutes": actual,
            },
            occurred_at=occurred,
        )
        results.append(await self.repo.add_evidence(temporal_ev))

        # Oturum bittikten sonra Confidence Engine'i tetikle (M2 → M4 → M5 zinciri)
        if is_bound:
            await self.trigger_confidence_recalculation(
                session.user_id, subject_code, topic_code
            )

        return results

    # ── Ingest: QuestionRecord (Performance) ──────────────────────────────────

    async def ingest_question_record(
        self,
        qr: QuestionRecord,
        *,
        catalog: list | None = None,
    ) -> TopicEvidence | None:
        """
        Soru kaydı kaydedilince çağrılır.
        Performance Evidence üretir.
        """
        if await self.repo.already_ingested(
            EvidenceSourceType.QUESTION_RECORD, qr.id
        ):
            return None

        # Sprint 6 — canonical codes öncelikli; free-text yalnızca fallback
        subject_code, topic_code = self.bind(
            subject_code=getattr(qr, "subject_code", None),
            topic_code=getattr(qr, "topic_code", None),
            subject_hint=qr.subject,
            topic_hint=qr.topic,
            catalog=catalog,
        )
        is_bound = subject_code != _UNBOUND

        # Accuracy = doğru / toplam (net değil; D/Y/B performans kanıtı)
        q_count = max(qr.question_count, 1)
        correct = int(qr.correct_count or 0)
        accuracy = max(min(correct / q_count, 1.0), 0.0)

        # Quality weight
        diff_quality = _DIFFICULTY_QUALITY.get(qr.difficulty, 0.70)
        count_factor = min(q_count / 10.0, 1.0)  # 10+ soru = tam kalite
        if q_count < _MIN_QR_COUNT:
            count_factor = 0.4
        quality = diff_quality * count_factor * (1.0 if is_bound else 0.6)

        ev = TopicEvidence(
            user_id=qr.user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            category=EvidenceCategory.PERFORMANCE,
            horizon=EvidenceHorizon.INSTANT,
            value=accuracy,
            quality_weight=round(min(quality, 1.0), 3),
            source_type=EvidenceSourceType.QUESTION_RECORD,
            source_id=qr.id,
            metadata_={
                "question_count": qr.question_count,
                "correct": qr.correct_count,
                "wrong": qr.wrong_count,
                "blank": qr.blank_count,
                "net": float(qr.net_score or 0),
                "difficulty": qr.difficulty,
                "accuracy": accuracy,
                "bound": is_bound,
            },
            occurred_at=qr.created_at,
        )
        result = await self.repo.add_evidence(ev)
        await self.trigger_confidence_recalculation(qr.user_id, subject_code, topic_code)
        return result

    # ── Ingest: RevisionReview (Performance — SM2 grade) ──────────────────────

    async def ingest_revision_review(
        self,
        review: RevisionReview,
        item: RevisionItem,
        *,
        catalog: list | None = None,
    ) -> TopicEvidence | None:
        """
        Revision grade kaydedilince çağrılır.
        Revision, yüksek kaliteli Performance Evidence'tır.
        """
        if await self.repo.already_ingested(
            EvidenceSourceType.REVISION_REVIEW, review.id
        ):
            return None

        # Sprint 7 — revision item'daki kodlar varsa kullan
        subject_code, topic_code = self.bind(
            subject_code=getattr(item, "subject_code", None),
            topic_code=getattr(item, "topic_code", None),
            subject_hint=item.subject,
            topic_hint=item.topic,
            catalog=catalog,
        )
        is_bound = subject_code != _UNBOUND

        grade = str(review.grade).lower()
        value = _GRADE_SIGNAL.get(grade, 0.5)

        # SM-2 tabanlı kalite: yüksek tekrar → daha güvenilir sinyal
        repetition_quality = min(0.7 + review.previous_interval_days / 100.0, 1.0)
        quality = repetition_quality * (1.0 if is_bound else 0.7)

        ev = TopicEvidence(
            user_id=item.user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            category=EvidenceCategory.PERFORMANCE,
            horizon=EvidenceHorizon.SHORT,
            value=value,
            quality_weight=round(min(quality, 1.0), 3),
            source_type=EvidenceSourceType.REVISION_REVIEW,
            source_id=review.id,
            metadata_={
                "grade": grade,
                "grade_signal": value,
                "ease_factor": review.new_ease,
                "interval_days": review.new_interval_days,
                "previous_interval": review.previous_interval_days,
                "lapse_count": review.previous_difficulty,
                "bound": is_bound,
            },
            occurred_at=review.reviewed_at,
        )
        result = await self.repo.add_evidence(ev)
        await self.trigger_confidence_recalculation(item.user_id, subject_code, topic_code)
        return result

    # ── Ingest: RevisionItem oluşturulduğunda (Consistency sinyali) ───────────

    async def ingest_revision_item_created(
        self,
        item: RevisionItem,
        *,
        catalog: list | None = None,
    ) -> TopicEvidence | None:
        """Tekrar öğesi oluşturulması = hafıza zayıflık sinyali."""
        if await self.repo.already_ingested(
            EvidenceSourceType.REVISION_ITEM, item.id
        ):
            return None

        subject_code, topic_code = self.bind(
            subject_code=None,
            topic_code=None,
            subject_hint=item.subject,
            topic_hint=item.topic,
            catalog=catalog,
        )

        ev = TopicEvidence(
            user_id=item.user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            category=EvidenceCategory.CONSISTENCY,
            horizon=EvidenceHorizon.MID,
            value=0.4,   # "bu konu için tekrar gerekti" = zayıflık sinyali
            quality_weight=0.8 if subject_code != _UNBOUND else 0.5,
            source_type=EvidenceSourceType.REVISION_ITEM,
            source_id=item.id,
            metadata_={
                "source_type": item.source_type,
                "difficulty": item.difficulty,
                "reason": item.reason,
            },
            occurred_at=item.created_at,
        )
        return await self.repo.add_evidence(ev)

    # ── Ingest: Topic Quiz Generation (AI_QUESTION performance) ───────────────

    async def ingest_quiz_generation(
        self,
        gen: "TopicQuizGeneration",
    ) -> TopicEvidence | None:
        """
        Sprint 14 — Quiz Session submit → tek Performance Evidence.
        Living Plan / Policy Decision tetiklenmez; yalnızca Evidence + Confidence.
        """
        if await self.repo.already_ingested(
            EvidenceSourceType.AI_QUESTION, gen.id
        ):
            return None

        total = max(int(gen.valid_item_count or 0), len(gen.items or []), 1)
        correct = int(gen.correct_count or 0)
        accuracy = max(min(correct / total, 1.0), 0.0)
        count_factor = min(total / 5.0, 1.0)
        diff_quality = _DIFFICULTY_QUALITY.get(gen.difficulty, 0.70)
        # AI üretilmiş soru: insan kaydından biraz daha düşük kalite
        quality = diff_quality * count_factor * 0.75

        ev = TopicEvidence(
            user_id=gen.user_id,
            subject_code=gen.subject_code,
            topic_code=gen.topic_code,
            category=EvidenceCategory.PERFORMANCE,
            horizon=EvidenceHorizon.INSTANT,
            value=accuracy,
            quality_weight=round(min(quality, 1.0), 3),
            source_type=EvidenceSourceType.AI_QUESTION,
            source_id=gen.id,
            metadata_={
                "generation_id": str(gen.id),
                "question_count": total,
                "correct": gen.correct_count,
                "wrong": gen.wrong_count,
                "blank": gen.blank_count,
                "difficulty": gen.difficulty,
                "accuracy": accuracy,
                "ai_generated": True,
                "provider": gen.provider,
            },
            occurred_at=gen.submitted_at or datetime.now(UTC),
        )
        result = await self.repo.add_evidence(ev)
        await self.trigger_confidence_recalculation(
            gen.user_id, gen.subject_code, gen.topic_code
        )
        return result

    # ── Ingest: Assessment Session (Sprint 18) ────────────────────────────────

    async def ingest_assessment_session(
        self,
        session: "AssessmentSession",
    ) -> TopicEvidence | None:
        """
        Assessment submit → PERFORMANCE Evidence.
        Quiz ingest'e ek; Decision / Living Plan yok.
        Kalibrasyon niyeti: biraz daha yüksek quality_weight.
        """
        from app.models.assessment import AssessmentSession  # noqa: F401

        if await self.repo.already_ingested(
            EvidenceSourceType.ASSESSMENT, session.id
        ):
            return None
        if not session.subject_code or not session.topic_code:
            return None

        total = max(
            int(session.correct_count or 0)
            + int(session.wrong_count or 0)
            + int(session.blank_count or 0),
            1,
        )
        correct = int(session.correct_count or 0)
        accuracy = max(min(correct / total, 1.0), 0.0)
        count_factor = min(total / 5.0, 1.0)
        kind_boost = {
            "initial_calibration": 0.9,
            "daily_challenge": 0.85,
            "branch_question": 0.8,
        }.get(str(session.kind), 0.8)
        quality = kind_boost * count_factor

        ev = TopicEvidence(
            user_id=session.user_id,
            subject_code=session.subject_code,
            topic_code=session.topic_code,
            category=EvidenceCategory.PERFORMANCE,
            horizon=EvidenceHorizon.INSTANT,
            value=accuracy,
            quality_weight=round(min(quality, 1.0), 3),
            source_type=EvidenceSourceType.ASSESSMENT,
            source_id=session.id,
            metadata_={
                "assessment_session_id": str(session.id),
                "kind": session.kind,
                "exam_type": session.exam_type,
                "question_count": total,
                "correct": session.correct_count,
                "wrong": session.wrong_count,
                "blank": session.blank_count,
                "accuracy": accuracy,
                "quiz_generation_id": (
                    str(session.quiz_generation_id)
                    if session.quiz_generation_id
                    else None
                ),
            },
            occurred_at=session.submitted_at or datetime.now(UTC),
        )
        result = await self.repo.add_evidence(ev)
        await self.trigger_confidence_recalculation(
            session.user_id, session.subject_code, session.topic_code
        )
        return result

    # ── Confidence recalculation trigger ─────────────────────────────────────

    async def trigger_confidence_recalculation(
        self,
        user_id: uuid.UUID,
        subject_code: str,
        topic_code: str,
    ) -> None:
        """
        Evidence ingestion sonrası Confidence Engine'i tetikle.
        Fire-and-forget: hata kullanıcı akışını kesmez.
        """
        if topic_code == _UNBOUND:
            return
        try:
            from app.services.confidence_engine import ConfidenceEngine
            await ConfidenceEngine(self.db).recalculate(user_id, subject_code, topic_code)
        except Exception:
            pass

    # ── Aggregate view ────────────────────────────────────────────────────────

    async def topic_aggregate(
        self,
        user_id: uuid.UUID,
        topic_code: str,
        *,
        since: datetime | None = None,
    ) -> dict:
        """
        Topic için özet aggregate — Confidence Engine'e girdi.
        Confidence Engine bu değerleri alıp belief hesaplar.
        """
        perf_rows = await self.repo.list_for_topic(
            user_id, topic_code,
            category=EvidenceCategory.PERFORMANCE,
            since=since,
            limit=100,
        )
        effort_rows = await self.repo.list_for_topic(
            user_id, topic_code,
            category=EvidenceCategory.EFFORT,
            since=since,
            limit=100,
        )

        perf_count = len(perf_rows)
        total_w = sum(r.quality_weight for r in perf_rows)
        weighted_acc = (
            sum(r.value * r.quality_weight for r in perf_rows) / total_w
            if total_w > 0
            else None
        )

        effort_minutes = sum(
            float(r.metadata_.get("actual_minutes", 0)) for r in effort_rows
        )
        last_ev = await self.repo.last_evidence_at(user_id, topic_code)

        return {
            "topic_code": topic_code,
            "performance_sample_count": perf_count,
            "weighted_accuracy": round(weighted_acc, 3) if weighted_acc is not None else None,
            "total_quality_weight": round(total_w, 2),
            "effort_minutes": round(effort_minutes, 1),
            "last_evidence_at": last_ev.isoformat() if last_ev else None,
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _effort_quality(actual_minutes: int) -> float:
    if actual_minutes < _NOISE_DURATION_THRESHOLD:
        return 0.25
    if actual_minutes < _SHORT_SESSION_THRESHOLD:
        return 0.55
    if actual_minutes < _FULL_SESSION_THRESHOLD:
        return 0.75
    return 1.0


def _normalize_code(text: str) -> str:
    """Free-text → slug (lowercase, spaces→underscore)."""
    return text.strip().lower().replace(" ", "_").replace("-", "_")[:100]
