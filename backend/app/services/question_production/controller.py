"""M34.5 — Cost-aware production validation & generation control."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.ai_cost.batch_generate import generate_batch_one_call
from app.services.ai_cost.cost_logger import estimate_cost
from app.services.ai_cost.pool import QuestionPoolService, fingerprint_for_plan
from app.services.qie.types import GenerateContext, QualityBreakdown, QuestionCard, QuestionPlan
from app.services.question_intelligence.pipeline import evaluate_question
from app.services.question_pool_manager import QuestionPoolInventoryService
from app.services.question_production.cost_gate import check_can_generate, suggest_batch_size
from app.services.question_production.pending_queue import get_pending_queue
from app.services.question_production.progress import get_progress_tracker
from app.services.question_production.rate_windows import get_rate_windows
from app.services.question_production.types import (
    BatchCostReport,
    PendingQuestion,
)

logger = logging.getLogger("studyos.m345")

_EST_PROMPT = 800
_EST_COMPLETION = 400


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _est_per_question() -> float:
    configured = float(
        getattr(settings, "QUESTION_PRODUCTION_EST_COST_PER_QUESTION_USD", 0.002) or 0.002
    )
    if configured > 0:
        return configured
    return estimate_cost(_EST_PROMPT, _EST_COMPLETION)


def _score_dict(eval_result: dict[str, Any]) -> dict[str, Any]:
    sc = eval_result.get("scorecard")
    scores: dict[str, Any] = {}
    if sc is not None and hasattr(sc, "to_dict"):
        scores = sc.to_dict()
    elif isinstance(sc, dict):
        scores = dict(sc)
    scores["accepted"] = bool(eval_result.get("accepted"))
    scores["reject_reason"] = eval_result.get("reject_reason")
    repair = eval_result.get("repair")
    if repair is not None and hasattr(repair, "repaired"):
        scores["repaired"] = bool(repair.repaired)
    return scores


def _preview_from_pool_row(row: Any, eval_result: dict[str, Any]) -> dict[str, Any]:
    q = eval_result.get("question") or {}
    return {
        "source": "pool_cache",
        "exam": getattr(row, "exam", "") or "",
        "subject_code": getattr(row, "subject_code", "") or "",
        "topic_code": getattr(row, "topic_code", "") or "",
        "difficulty_band": getattr(row, "difficulty_band", "") or "",
        "stem": str(q.get("stem") or getattr(row, "stem", "") or ""),
        "choices": dict(q.get("choices") or getattr(row, "choices", None) or {}),
        "correct_key": str(q.get("correct_key") or getattr(row, "correct_key", "A") or "A"),
        "explanation": q.get("explanation", getattr(row, "explanation", None)),
        "scores": _score_dict(eval_result),
        "accepted": bool(eval_result.get("accepted")),
        "plan": {},
    }


def _preview_from_card(card: QuestionCard, eval_result: dict[str, Any]) -> dict[str, Any]:
    q = eval_result.get("question") or {}
    plan_dict = card.plan.to_dict() if hasattr(card.plan, "to_dict") else {}
    return {
        "source": "generated",
        "exam": getattr(card.plan, "exam", "") or "",
        "subject_code": getattr(card.plan, "subject_code", "") or "",
        "topic_code": getattr(card.plan, "topic_code", "") or "",
        "difficulty_band": "",
        "stem": str(q.get("stem") or card.stem or ""),
        "choices": dict(q.get("choices") or card.choices or {}),
        "correct_key": str(q.get("correct_key") or card.correct_key or "A"),
        "explanation": q.get("explanation", card.explanation),
        "scores": _score_dict(eval_result),
        "accepted": bool(eval_result.get("accepted")),
        "plan": plan_dict,
        "provider": card.provider,
        "model": card.model,
    }


def _record_gemini_if_real(result: Any) -> bool:
    if result is None:
        return False
    provider = str(getattr(result, "provider", None) or "").strip().lower()
    if provider in ("", "null", "none"):
        return False
    get_rate_windows().record_call()
    return True


def _max_retry() -> int:
    return max(0, int(getattr(settings, "QUESTION_PRODUCTION_MAX_RETRY", 2) or 2))


class ProductionController:
    """Cost-aware generation orchestration (validation + missing-topic fill)."""

    def stop(self) -> dict[str, Any]:
        tracker = get_progress_tracker()
        tracker.request_stop()
        return tracker.get().to_dict()

    def get_progress(self) -> dict[str, Any]:
        return get_progress_tracker().get().to_dict()

    def list_pending(self) -> list[dict[str, Any]]:
        return [p.to_dict() for p in get_pending_queue().list()]

    def reject_pending(self, *, pending_id: str | None = None, item_id: str | None = None) -> dict[str, Any]:
        key = pending_id or item_id or ""
        ok = get_pending_queue().reject(key)
        return {"ok": ok, "pending_id": key}

    async def approve_pending(
        self,
        db: AsyncSession,
        item_id: str | None = None,
        *,
        pending_id: str | None = None,
    ) -> dict[str, Any]:
        key = pending_id or item_id or ""
        queue = get_pending_queue()
        item = queue.get(key)
        if item is None:
            return {"ok": False, "reason": "not_found"}
        approved = queue.approve(key)
        if approved is None:
            return {"ok": False, "reason": "not_found"}

        pool = QuestionPoolService(db)
        plan_raw = approved.get("plan") or {}
        # Build a minimal GenerateContext for fingerprinting when plan is incomplete.
        ctx = GenerateContext(
            exam=str(approved.get("exam") or ""),
            subject_code=str(approved.get("subject_code") or ""),
            subject_name=str(approved.get("subject_code") or ""),
            topic_code=str(approved.get("topic_code") or ""),
            topic_name=str(approved.get("topic_code") or ""),
            difficulty_band=str(approved.get("difficulty_band") or "medium"),
            kind="batch_generate",
        )
        plan = QuestionPlan(
            exam=str(plan_raw.get("exam") or ctx.exam),
            subject_code=str(plan_raw.get("subject_code") or ctx.subject_code),
            subject_name=str(plan_raw.get("subject_name") or ctx.subject_name),
            topic_code=str(plan_raw.get("topic_code") or ctx.topic_code),
            topic_name=str(plan_raw.get("topic_name") or ctx.topic_name),
            skill=str(plan_raw.get("skill") or ""),
            bloom=str(plan_raw.get("bloom") or "analyze"),
            stem_type=str(plan_raw.get("stem_type") or ""),
            choice_count=int(plan_raw.get("choice_count") or 5),
            index=int(plan_raw.get("index") or 0),
            difficulty=int(plan_raw.get("difficulty") or 70),
        )
        card = QuestionCard(
            stem=str(approved.get("stem") or ""),
            choices={str(k): str(v) for k, v in (approved.get("choices") or {}).items()},
            correct_key=str(approved.get("correct_key") or "A").upper(),
            explanation=approved.get("explanation"),
            plan=plan,
            difficulty_score=int((approved.get("scores") or {}).get("difficulty") or 70),
            quality=QualityBreakdown(),
            style_score=int((approved.get("scores") or {}).get("style") or 0),
        )
        fp = fingerprint_for_plan(plan, ctx)
        await pool.put_card(
            fingerprint=fp,
            card=card,
            exam=ctx.exam,
            subject_code=ctx.subject_code,
            topic_code=ctx.topic_code,
            difficulty_band=ctx.difficulty_band,
            skill=plan.skill,
        )
        await db.commit()
        return {"ok": True, "question": approved}

    async def validate_generate_five(
        self,
        db: AsyncSession,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty_band: str = "medium",
        subject_name: str = "",
        topic_name: str = "",
        count: int = 5,
    ) -> dict[str, Any]:
        """P10: Generate up to 5 questions for preview — do NOT save to pool."""
        planned = max(1, min(int(count or 5), 5))
        gate = check_can_generate(planned_count=planned)
        tracker = get_progress_tracker()
        tracker.reset(
            exam=exam,
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty_band,
            planned=planned,
            approval_mode="auto",
        )

        if not gate.can_generate:
            tracker.update(status="failed", remaining=planned)
            return {
                "questions": [],
                "cost_gate": gate.to_dict(),
                "cost_report": BatchCostReport().to_dict(),
                "progress": tracker.get().to_dict(),
                "skipped": True,
                "reason": gate.reason,
            }

        t0 = time.perf_counter()
        pool = QuestionPoolService(db)
        existing_stems: list[str] = []
        previews: list[dict[str, Any]] = []
        gemini_calls = 0
        accepted = 0
        rejected = 0
        rewrite = 0
        est_cost = 0.0

        # P6 — prefer pool cache
        cached = await pool.get_unused_for_topic(
            exam=exam.lower(),
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty_band or "medium",
            limit=planned,
        )
        if len(cached) >= planned:
            for row in cached[:planned]:
                qdict = {
                    "stem": row.stem,
                    "choices": dict(row.choices or {}),
                    "correct_key": row.correct_key,
                    "explanation": row.explanation,
                }
                ev = evaluate_question(qdict, {}, existing_stems=existing_stems)
                if ev.get("repair") and getattr(ev["repair"], "repaired", False):
                    rewrite += 1
                preview = _preview_from_pool_row(row, ev)
                previews.append(preview)
                tracker.set_last_preview(preview)
                existing_stems.append(preview["stem"])
                if preview["accepted"]:
                    accepted += 1
                else:
                    rejected += 1
                tracker.update(
                    current_index=len(previews),
                    accepted=accepted,
                    rejected=rejected,
                    rewrite=rewrite,
                    remaining=max(0, planned - len(previews)),
                )
            report = BatchCostReport(
                gemini_calls=0,
                estimated_cost=0.0,
                questions_generated=len(previews),
                questions_accepted=accepted,
                questions_rejected=rejected,
                average_cost_per_question=0.0,
                duration_ms=(time.perf_counter() - t0) * 1000.0,
            )
            tracker.update(status="completed", cost_report=report.to_dict(), remaining=0)
            return {
                "questions": previews,
                "cost_gate": gate.to_dict(),
                "cost_report": report.to_dict(),
                "progress": tracker.get().to_dict(),
                "cache_reuse": True,
            }

        batch_n = min(5, max(1, suggest_batch_size()), 5)
        ctx = GenerateContext(
            exam=exam.lower(),
            subject_code=subject_code,
            subject_name=subject_name or subject_code,
            topic_code=topic_code,
            topic_name=topic_name or topic_code,
            count=batch_n,
            difficulty_band=difficulty_band or "medium",
            kind="batch_generate",
        )
        cards, _fp, result = await generate_batch_one_call(db, ctx, count=batch_n)
        if _record_gemini_if_real(result):
            gemini_calls += 1
            est_cost += _est_per_question() * max(1, len(cards) or batch_n)

        for card in cards[:planned]:
            qdict = {
                "stem": card.stem,
                "choices": dict(card.choices),
                "correct_key": card.correct_key,
                "explanation": card.explanation,
            }
            plan_dict = card.plan.to_dict() if hasattr(card.plan, "to_dict") else {}
            ev = evaluate_question(qdict, plan_dict, existing_stems=existing_stems)
            if ev.get("repair") and getattr(ev["repair"], "repaired", False):
                rewrite += 1
            preview = _preview_from_card(card, ev)
            previews.append(preview)
            tracker.set_last_preview(preview)
            existing_stems.append(preview["stem"])
            if preview["accepted"]:
                accepted += 1
            else:
                rejected += 1
            tracker.update(
                current_index=len(previews),
                accepted=accepted,
                rejected=rejected,
                rewrite=rewrite,
                gemini_calls=gemini_calls,
                estimated_cost=est_cost,
                remaining=max(0, planned - len(previews)),
            )

        duration_ms = (time.perf_counter() - t0) * 1000.0
        avg = (est_cost / accepted) if accepted > 0 else 0.0
        report = BatchCostReport(
            gemini_calls=gemini_calls,
            prompt_tokens=_EST_PROMPT * gemini_calls,
            completion_tokens=_EST_COMPLETION * gemini_calls,
            estimated_cost=est_cost,
            questions_generated=len(previews),
            questions_accepted=accepted,
            questions_rejected=rejected,
            average_cost_per_question=avg,
            duration_ms=duration_ms,
        )
        tracker.update(status="completed", cost_report=report.to_dict(), remaining=0)
        return {
            "questions": previews,
            "cost_gate": gate.to_dict(),
            "cost_report": report.to_dict(),
            "progress": tracker.get().to_dict(),
            "cache_reuse": False,
        }

    async def generate_topic(
        self,
        db: AsyncSession,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty_band: str,
        count: int,
        approval_mode: str = "auto",
        save: bool = True,
        subject_name: str = "",
        topic_name: str = "",
    ) -> dict[str, Any]:
        """Generate `count` questions for one topic (optional save / manual queue)."""
        planned = max(0, int(count or 0))
        mode = (approval_mode or getattr(settings, "QUESTION_PRODUCTION_APPROVAL_MODE", "auto") or "auto").lower()
        if mode not in ("auto", "manual"):
            mode = "auto"

        tracker = get_progress_tracker()
        tracker.reset(
            exam=exam,
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty_band,
            planned=planned,
            approval_mode=mode,
        )

        if planned <= 0:
            report = BatchCostReport()
            tracker.update(status="completed", cost_report=report.to_dict())
            return {
                "planned": 0,
                "accepted": 0,
                "rejected": 0,
                "items": [],
                "cost_report": report.to_dict(),
                "progress": tracker.get().to_dict(),
            }

        gate = check_can_generate(planned_count=min(planned, 5))
        if not gate.can_generate:
            tracker.update(status="failed")
            return {
                "planned": planned,
                "accepted": 0,
                "rejected": 0,
                "items": [],
                "skipped": True,
                "reason": gate.reason,
                "cost_gate": gate.to_dict(),
                "cost_report": BatchCostReport().to_dict(),
                "progress": tracker.get().to_dict(),
            }

        result = await self._produce_for_topic(
            db,
            exam=exam.lower(),
            subject_code=subject_code,
            topic_code=topic_code,
            difficulty_band=difficulty_band or "medium",
            subject_name=subject_name or subject_code,
            topic_name=topic_name or topic_code,
            needed=planned,
            approval_mode=mode,
            save=save,
        )
        return result

    async def run_missing_topics(
        self,
        db: AsyncSession,
        *,
        approval_mode: str | None = None,
        max_topics: int | None = None,
    ) -> dict[str, Any]:
        """P2: Fill topics where current < minimum (cost-gated, stoppable)."""
        mode = (
            approval_mode
            or getattr(settings, "QUESTION_PRODUCTION_APPROVAL_MODE", "auto")
            or "auto"
        ).lower()
        if mode not in ("auto", "manual"):
            mode = "auto"

        inventory = QuestionPoolInventoryService()
        snapshot = await inventory.snapshot(db)
        missing = [row for row in snapshot if int(row.get("current") or 0) < int(row.get("minimum") or 0)]
        if max_topics is not None:
            missing = missing[: max(0, int(max_topics))]

        total_planned = sum(
            max(0, int(r.get("target") or r.get("minimum") or 0) - int(r.get("current") or 0))
            for r in missing
        )
        tracker = get_progress_tracker()
        tracker.reset(planned=total_planned, approval_mode=mode)

        gate0 = check_can_generate(planned_count=1)
        if not gate0.can_generate and missing:
            tracker.update(status="failed")
            return {
                "planned": 0,
                "accepted": 0,
                "items": [],
                "skipped": True,
                "reason": gate0.reason,
                "cost_gate": gate0.to_dict(),
                "progress": tracker.get().to_dict(),
            }

        t0 = time.perf_counter()
        items: list[dict[str, Any]] = []
        total_accepted = 0
        total_rejected = 0
        total_gemini = 0
        total_cost = 0.0
        total_generated = 0

        for row in missing:
            if tracker.is_stop_requested():
                tracker.update(status="stopped")
                break

            exam = str(row.get("exam") or "")
            subject_code = str(row.get("subject_code") or "")
            topic_code = str(row.get("topic_code") or "")
            difficulty_band = str(row.get("difficulty_band") or "medium")
            subject_name = str(row.get("subject_name") or subject_code)
            topic_name = str(row.get("topic_name") or topic_code)
            current = int(row.get("current") or 0)
            minimum = int(row.get("minimum") or 0)
            target = int(row.get("target") or minimum)
            if current >= minimum:
                continue
            needed = max(0, target - current)
            if needed <= 0:
                continue

            tracker.update(
                exam=exam,
                subject_code=subject_code,
                topic_code=topic_code,
                difficulty_band=difficulty_band,
                remaining=needed,
            )

            topic_result = await self._produce_for_topic(
                db,
                exam=exam,
                subject_code=subject_code,
                topic_code=topic_code,
                difficulty_band=difficulty_band,
                subject_name=subject_name,
                topic_name=topic_name,
                needed=needed,
                approval_mode=mode,
                save=True,
                reset_progress=False,
            )
            items.append(topic_result)
            total_accepted += int(topic_result.get("accepted") or 0)
            total_rejected += int(topic_result.get("rejected") or 0)
            total_gemini += int((topic_result.get("cost_report") or {}).get("gemini_calls") or 0)
            total_cost += float((topic_result.get("cost_report") or {}).get("estimated_cost") or 0.0)
            total_generated += int((topic_result.get("cost_report") or {}).get("questions_generated") or 0)

            if tracker.is_stop_requested():
                tracker.update(status="stopped")
                break

        duration_ms = (time.perf_counter() - t0) * 1000.0
        avg = (total_cost / total_accepted) if total_accepted > 0 else 0.0
        report = BatchCostReport(
            gemini_calls=total_gemini,
            prompt_tokens=_EST_PROMPT * total_gemini,
            completion_tokens=_EST_COMPLETION * total_gemini,
            estimated_cost=total_cost,
            questions_generated=total_generated,
            questions_accepted=total_accepted,
            questions_rejected=total_rejected,
            average_cost_per_question=avg,
            duration_ms=duration_ms,
        )
        status = tracker.get().status
        if status not in ("stopped", "failed"):
            status = "completed"
        tracker.update(
            status=status,
            accepted=total_accepted,
            rejected=total_rejected,
            gemini_calls=total_gemini,
            estimated_cost=total_cost,
            remaining=0,
            cost_report=report.to_dict(),
        )
        return {
            "planned": total_planned,
            "accepted": total_accepted,
            "rejected": total_rejected,
            "items": items,
            "cost_report": report.to_dict(),
            "progress": tracker.get().to_dict(),
        }

    async def _produce_for_topic(
        self,
        db: AsyncSession,
        *,
        exam: str,
        subject_code: str,
        topic_code: str,
        difficulty_band: str,
        subject_name: str,
        topic_name: str,
        needed: int,
        approval_mode: str,
        save: bool,
        reset_progress: bool = True,
    ) -> dict[str, Any]:
        logger.info(
            "[PIPELINE] 1. _produce_for_topic entered | exam=%s subject=%s topic=%s needed=%s approval_mode=%s save=%s",
            exam, subject_code, topic_code, needed, approval_mode, save,
        )
        tracker = get_progress_tracker()
        if reset_progress:
            tracker.reset(
                exam=exam,
                subject_code=subject_code,
                topic_code=topic_code,
                difficulty_band=difficulty_band,
                planned=needed,
                approval_mode=approval_mode,
            )

        pool = QuestionPoolService(db)
        pending = get_pending_queue()
        t0 = time.perf_counter()

        accepted = 0
        rejected = 0
        rewrite = 0
        failed = 0
        gemini_calls = 0
        est_cost = 0.0
        generated = 0
        cache_hits = 0
        items: list[dict[str, Any]] = []
        existing_stems: list[str] = []
        remaining = needed
        max_retry = _max_retry()

        while remaining > 0:
            if tracker.is_stop_requested():
                tracker.update(status="stopped")
                break

            gate = check_can_generate(planned_count=min(remaining, 5))
            if not gate.can_generate:
                tracker.update(status="failed")
                break

            batch_n = min(remaining, suggest_batch_size(), 5)
            if batch_n < 1:
                tracker.update(status="failed")
                break

            # P6 — pool cache first (especially useful for save=False validation)
            cached = await pool.get_unused_for_topic(
                exam=exam,
                subject_code=subject_code,
                topic_code=topic_code,
                difficulty_band=difficulty_band,
                exclude_stems=existing_stems,
                limit=batch_n,
            )
            used_cache = False
            cards: list[QuestionCard] = []
            result: Any = None

            if cached and not save:
                used_cache = True
                for row in cached[:batch_n]:
                    qdict = {
                        "stem": row.stem,
                        "choices": dict(row.choices or {}),
                        "correct_key": row.correct_key,
                        "explanation": row.explanation,
                    }
                    ev = evaluate_question(qdict, {}, existing_stems=existing_stems)
                    if ev.get("repair") and getattr(ev["repair"], "repaired", False):
                        rewrite += 1
                        tracker.update(increment_rewrite=1)
                    preview = _preview_from_pool_row(row, ev)
                    items.append(preview)
                    tracker.set_last_preview(preview)
                    existing_stems.append(preview["stem"])
                    generated += 1
                    cache_hits += 1
                    if preview["accepted"]:
                        accepted += 1
                        remaining = max(0, remaining - 1)
                        tracker.update(increment_accepted=1, remaining=remaining)
                    else:
                        rejected += 1
                        remaining = max(0, remaining - 1)
                        tracker.update(increment_rejected=1, remaining=remaining)
                continue

            # Generate with retries (P7)
            attempt = 0
            cards = []
            result = None
            while attempt <= max_retry:
                if tracker.is_stop_requested():
                    break
                gate = check_can_generate(planned_count=batch_n)
                if not gate.can_generate:
                    break
                ctx = GenerateContext(
                    exam=exam,
                    subject_code=subject_code,
                    subject_name=subject_name,
                    topic_code=topic_code,
                    topic_name=topic_name,
                    count=batch_n,
                    difficulty_band=difficulty_band,
                    existing_stems=list(existing_stems),
                    kind="batch_generate",
                )
                cards, _fp, result = await generate_batch_one_call(db, ctx, count=batch_n)
                if _record_gemini_if_real(result):
                    gemini_calls += 1
                    est_cost += _est_per_question() * max(1, len(cards) or batch_n)
                    tracker.update(increment_gemini=1, add_cost=_est_per_question() * max(1, len(cards) or batch_n))
                if cards:
                    break
                attempt += 1

            if tracker.is_stop_requested():
                tracker.update(status="stopped")
                break

            if not cards:
                failed += 1
                tracker.update(increment_failed=1, status="failed")
                return {
                    "exam": exam,
                    "subject_code": subject_code,
                    "topic_code": topic_code,
                    "difficulty_band": difficulty_band,
                    "planned": needed,
                    "accepted": accepted,
                    "rejected": rejected,
                    "failed": True,
                    "status": "FAILED",
                    "reason": "generate_returned_zero_after_retries",
                    "items": items,
                    "cache_hits": cache_hits,
                    "cost_report": BatchCostReport(
                        gemini_calls=gemini_calls,
                        prompt_tokens=_EST_PROMPT * gemini_calls,
                        completion_tokens=_EST_COMPLETION * gemini_calls,
                        estimated_cost=est_cost,
                        questions_generated=generated,
                        questions_accepted=accepted,
                        questions_rejected=rejected,
                        average_cost_per_question=(est_cost / accepted) if accepted else 0.0,
                        duration_ms=(time.perf_counter() - t0) * 1000.0,
                    ).to_dict(),
                    "progress": tracker.get().to_dict(),
                    "cost_gate": gate.to_dict(),
                }

            for card in cards:
                if remaining <= 0:
                    break
                qdict = {
                    "stem": card.stem,
                    "choices": dict(card.choices),
                    "correct_key": card.correct_key,
                    "explanation": card.explanation,
                }
                plan_dict = card.plan.to_dict() if hasattr(card.plan, "to_dict") else {}
                logger.info("[PIPELINE] 5. evaluate_question starting | stem_preview=%s...", (card.stem or "")[:40])
                ev = evaluate_question(qdict, plan_dict, existing_stems=existing_stems)
                if ev.get("repair") and getattr(ev["repair"], "repaired", False):
                    rewrite += 1
                    tracker.update(increment_rewrite=1)
                preview = _preview_from_card(card, ev)
                items.append(preview)
                tracker.set_last_preview(preview)
                existing_stems.append(preview["stem"])
                generated += 1

                if not preview["accepted"]:
                    rejected += 1
                    remaining = max(0, remaining - 1)
                    tracker.update(
                        increment_rejected=1,
                        remaining=remaining,
                        current_index=generated,
                    )
                    logger.info("[PIPELINE] 7. Card REJECTED | reject_reason=%s", preview.get("scores", {}).get("reject_reason"))
                    continue

                if save and approval_mode == "auto":
                    ctx = GenerateContext(
                        exam=exam,
                        subject_code=subject_code,
                        subject_name=subject_name,
                        topic_code=topic_code,
                        topic_name=topic_name,
                        difficulty_band=difficulty_band,
                        kind="batch_generate",
                    )
                    fp = fingerprint_for_plan(card.plan, ctx)
                    await pool.put_card(
                        fingerprint=fp,
                        card=card,
                        exam=exam,
                        subject_code=subject_code,
                        topic_code=topic_code,
                        difficulty_band=difficulty_band,
                        skill=card.plan.skill,
                    )
                    logger.info("[PIPELINE] 9. Card saved to QuestionPool db pool | topic=%s", topic_code)
                elif save and approval_mode == "manual":
                    pq = PendingQuestion(
                        id=str(uuid4()),
                        stem=preview["stem"],
                        choices=dict(preview["choices"]),
                        correct_key=preview["correct_key"],
                        explanation=preview.get("explanation"),
                        scores=dict(preview.get("scores") or {}),
                        exam=exam,
                        subject_code=subject_code,
                        topic_code=topic_code,
                        difficulty_band=difficulty_band,
                        plan=plan_dict,
                        created_at=_now_iso(),
                    )
                    pending.add(pq)
                    preview["pending_id"] = pq.id
                    logger.info("[PIPELINE] 9. Card saved to PendingQueue | pending_id=%s", pq.id)

                accepted += 1
                remaining = max(0, remaining - 1)
                tracker.update(
                    increment_accepted=1,
                    remaining=remaining,
                    current_index=generated,
                )
                logger.info("[PIPELINE] 8. accepted += 1 EXECUTED | total_accepted=%s remaining=%s", accepted, remaining)

            if save and approval_mode == "auto":
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()
                    raise

            # Avoid tight loop if nothing progressed
            if not used_cache and not cards:
                break

        duration_ms = (time.perf_counter() - t0) * 1000.0
        avg = (est_cost / accepted) if accepted > 0 else 0.0
        report = BatchCostReport(
            gemini_calls=gemini_calls,
            prompt_tokens=_EST_PROMPT * gemini_calls,
            completion_tokens=_EST_COMPLETION * gemini_calls,
            estimated_cost=est_cost,
            questions_generated=generated,
            questions_accepted=accepted,
            questions_rejected=rejected,
            average_cost_per_question=avg,
            duration_ms=duration_ms,
        )
        status = tracker.get().status
        if status not in ("stopped", "failed", "stopping"):
            status = "completed"
        elif status == "stopping":
            status = "stopped"
        if reset_progress:
            tracker.update(status=status, cost_report=report.to_dict(), remaining=remaining)

        return {
            "exam": exam,
            "subject_code": subject_code,
            "topic_code": topic_code,
            "difficulty_band": difficulty_band,
            "planned": needed,
            "accepted": accepted,
            "rejected": rejected,
            "rewrite": rewrite,
            "failed": failed,
            "items": items,
            "cache_hits": cache_hits,
            "approval_mode": approval_mode,
            "saved": save and approval_mode == "auto",
            "cost_report": report.to_dict(),
            "progress": tracker.get().to_dict(),
        }
