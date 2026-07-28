"""
StudyOS — Behavioral Learning Memory Service (LOS Module 7)
LOS § 7 — Evidence'dan behavioral model güncelleme.

Prensipler:
  - Tek olay overwrite etmez (soft / exponential moving average)
  - Memory Decide'ı bias eder; yerine geçmez
  - Kullanıcıya açık CRUD yoktur
  - Privacy kapısı: belge kapsamı dışında; servis sessizce günceller
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.behavioral_memory import BehavioralMemory
from app.repositories.topic_evidence_repository import TopicEvidenceRepository

# ── Soft update parametreleri ─────────────────────────────────────────────────

# Exponential moving average alpha (yeni verinin ağırlığı)
_EMA_ALPHA = 0.2   # 0.2 = yavaş güncelleme (LOS prensibi)


class BehavioralMemoryService:
    """
    LOS § 7 — Behavioral Memory güncelleme servisi.

    Kullanım:
        svc = BehavioralMemoryService(db)
        await svc.update_from_session(user_id, session)
        mem = await svc.get_or_create(user_id)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_repo = TopicEvidenceRepository(db)

    # ── CRUD ─────────────────────────────────────────────────────────────────

    async def get_or_create(self, user_id: uuid.UUID) -> BehavioralMemory:
        stmt = select(BehavioralMemory).where(BehavioralMemory.user_id == user_id)
        result = await self.db.execute(stmt)
        mem = result.scalar_one_or_none()
        if mem is None:
            mem = BehavioralMemory(user_id=user_id)
            self.db.add(mem)
            await self.db.flush()
        return mem

    # ── Update: StudySession → chronotype + tempo + pomodoro_signature ────────

    async def update_from_session(
        self,
        user_id: uuid.UUID,
        session,  # StudySession
    ) -> None:
        """
        Oturum tamamlandığında behavioral memory'yi güncelle.
        Fire-and-forget; hata oluşursa sessizce devam et.
        """
        try:
            mem = await self.get_or_create(user_id)
            ended = session.ended_at or datetime.now(UTC)
            actual = session.actual_duration_minutes or 0

            # ── Chronotype ─────────────────────────────────────────
            hour = ended.hour
            chron = dict(mem.chronotype)
            hourly = chron.get("hourly_counts", {})
            hourly[str(hour)] = hourly.get(str(hour), 0) + 1
            chron["hourly_counts"] = hourly

            # Peak / low hours (saatlik sayım > ortalama 1.5x → peak)
            if hourly:
                avg = sum(hourly.values()) / len(hourly)
                peak = [int(h) for h, c in hourly.items() if c > avg * 1.5]
                low = [int(h) for h, c in hourly.items() if c < avg * 0.5]
                chron["peak_hours"] = sorted(peak)
                chron["low_hours"] = sorted(low)

            # Soft update avg_start_hour
            prev_avg = chron.get("avg_start_hour", hour)
            chron["avg_start_hour"] = _ema(prev_avg, hour, _EMA_ALPHA)
            mem.chronotype = chron

            # ── Tempo ──────────────────────────────────────────────
            tempo = dict(mem.tempo)
            prev_daily = tempo.get("avg_daily_minutes", actual)
            tempo["avg_daily_minutes"] = _ema(prev_daily, actual, _EMA_ALPHA)
            tempo["session_count"] = tempo.get("session_count", 0) + 1
            mem.tempo = tempo

            # ── Pomodoro signature ─────────────────────────────────
            planned = session.planned_duration_minutes or 25
            completion = actual / max(planned, 1)
            pom = dict(mem.pomodoro_signature)
            prev_dur = pom.get("preferred_duration", planned)
            pom["preferred_duration"] = int(_ema(prev_dur, planned, _EMA_ALPHA))
            prev_comp = pom.get("avg_completion", completion)
            pom["avg_completion"] = round(_ema(prev_comp, completion, _EMA_ALPHA), 3)
            pom["session_count"] = pom.get("session_count", 0) + 1
            mem.pomodoro_signature = pom

            # ── Schedule signature ─────────────────────────────────
            sched = dict(mem.schedule_signature)
            weekday = ended.weekday()  # 0=Mon
            wd_dist = sched.get("weekday_distribution", {})
            wd_dist[str(weekday)] = wd_dist.get(str(weekday), 0) + 1
            sched["weekday_distribution"] = wd_dist
            mem.schedule_signature = sched

            mem.last_updated_at = datetime.now(UTC)
            await self.db.flush()
        except Exception:
            pass

    # ── Update: QuestionRecord → difficulty_signature ─────────────────────────

    async def update_from_question_record(
        self,
        user_id: uuid.UUID,
        qr,  # QuestionRecord
        topic_code: str,
    ) -> None:
        """Soru kaydından difficulty_signature güncelle."""
        try:
            mem = await self.get_or_create(user_id)
            accuracy = float(qr.correct_count) / max(qr.question_count, 1)

            diff = dict(mem.difficulty_signature)
            existing = diff.get(topic_code, {"avg_accuracy": accuracy, "sample": 0})
            existing["avg_accuracy"] = _ema(existing.get("avg_accuracy", accuracy), accuracy, _EMA_ALPHA)
            existing["sample"] = existing.get("sample", 0) + 1
            diff[topic_code] = existing
            mem.difficulty_signature = diff
            mem.last_updated_at = datetime.now(UTC)
            await self.db.flush()
        except Exception:
            pass

    # ── Update: Plan receptivity (accept/reject) ──────────────────────────────

    async def record_plan_decision(
        self, user_id: uuid.UUID, *, accepted: bool
    ) -> None:
        """Kullanıcı planı kabul/reddetti → plan_receptivity güncelle."""
        try:
            mem = await self.get_or_create(user_id)
            rec = dict(mem.plan_receptivity)
            if accepted:
                rec["accept_count"] = rec.get("accept_count", 0) + 1
            else:
                rec["reject_count"] = rec.get("reject_count", 0) + 1
            total = rec.get("accept_count", 0) + rec.get("reject_count", 0)
            if total > 0:
                rec["accept_rate"] = round(rec.get("accept_count", 0) / total, 3)
            mem.plan_receptivity = rec
            mem.last_updated_at = datetime.now(UTC)
            await self.db.flush()
        except Exception:
            pass

    # ── Read: Today Engine için behavioral input ──────────────────────────────

    async def get_behavioral_context(self, user_id: uuid.UUID) -> dict:
        """
        Today Engine ve Planner için özet behavioral context.
        Decide'ı bias etmek için kullanılır; yerine geçmez.
        """
        mem = await self.get_or_create(user_id)
        return {
            "peak_hours": mem.chronotype.get("peak_hours", []),
            "avg_daily_minutes": mem.tempo.get("avg_daily_minutes", 120),
            "preferred_pomodoro_duration": mem.pomodoro_signature.get("preferred_duration", 25),
            "avg_completion_rate": mem.pomodoro_signature.get("avg_completion", 0.8),
            "accept_rate": mem.plan_receptivity.get("accept_rate", 0.5),
            "session_count": mem.tempo.get("session_count", 0),
        }


# ── Yardımcı ──────────────────────────────────────────────────────────────────

def _ema(prev: float, new: float, alpha: float) -> float:
    """Exponential Moving Average — soft update."""
    return prev * (1 - alpha) + new * alpha
