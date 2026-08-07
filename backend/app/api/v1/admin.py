"""Admin API — system_admin only."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from app.core.dependencies import require_system_admin
from app.database.base import get_db
from app.models.user import User
from app.schemas.admin import AdminOverview, AdminUserListItem, AdminUserUpdate
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.question_pool_manager import (
    QuestionPoolFillMissingRequest,
    QuestionPoolFillRequest,
    QuestionPoolInventoryRow,
    QuestionPoolMetrics,
    QuestionPoolDeleteRequest,
    QuestionPoolRegenerateRequest,
    ProductionValidateRequest,
    ProductionRunMissingRequest,
    ProductionGenerateTopicRequest,
    ProductionApproveRequest,
)
from app.services.question_pool_manager import (
    QuestionPoolInventoryService,
    QuestionPoolManagerService,
    TopicKey,
)
from app.models.question_pool_inventory import QuestionPoolGenerationHistory
from app.services.admin_service import AdminService
from app.core.config import settings

router = APIRouter()


@router.get(
    "/question-pool/scheduler-status",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_scheduler_status(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    from sqlalchemy import func, select

    enabled = bool(settings.ENABLE_MIDNIGHT_SCHEDULER)
    dry_run = bool(settings.QUESTION_POOL_SCHEDULER_DRY_RUN)

    # Last run: use max history timestamp as proxy
    last_ts_stmt = select(func.max(QuestionPoolGenerationHistory.timestamp))
    last_ts = (await db.execute(last_ts_stmt)).scalar_one_or_none()

    # Next run: compute next Istanbul midnight
    tz = timezone(timedelta(hours=3), name="Europe/Istanbul")
    now_local = datetime.now(timezone.utc).astimezone(tz)
    nxt_local = (now_local + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    next_run_utc = nxt_local.astimezone(timezone.utc)
    seconds = max(0, (next_run_utc - datetime.now(timezone.utc)).total_seconds())

    return SuccessResponse(
        data={
            "enabled": enabled,
            "dry_run": dry_run,
            "last_run": last_ts,
            "next_run_utc": next_run_utc,
            "seconds_until_next": seconds,
        },
        message="OK",
    )


@router.get("/overview", response_model=SuccessResponse[AdminOverview])
async def admin_overview(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AdminOverview]:
    data = await AdminService(db).overview()
    return SuccessResponse(data=data)


@router.get("/users", response_model=PaginatedResponse[AdminUserListItem])
async def admin_list_users(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> PaginatedResponse[AdminUserListItem]:
    items, total = await AdminService(db).list_users(q=q, page=page, page_size=page_size)
    meta = AdminService.pagination_meta(page, page_size, total)
    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(**meta),
    )


@router.get("/users/{user_id}", response_model=SuccessResponse[AdminUserListItem])
async def admin_get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AdminUserListItem]:
    data = await AdminService(db).get_user(user_id)
    return SuccessResponse(data=data)


@router.patch("/users/{user_id}", response_model=SuccessResponse[AdminUserListItem])
async def admin_update_user(
    user_id: uuid.UUID,
    body: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AdminUserListItem]:
    data = await AdminService(db).update_user(user_id, body)
    return SuccessResponse(data=data, message="Kullanıcı güncellendi")


@router.delete("/users/{user_id}", response_model=SuccessResponse[dict])
async def admin_delete_user(
    user_id: uuid.UUID,
    hard: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    if admin.id == user_id and hard:
        from app.core.exceptions import ValidationError

        raise ValidationError("Kendi hesabınızı kalıcı silemezsiniz")
    await AdminService(db).delete_user(user_id, hard=hard)
    return SuccessResponse(
        data={},
        message="Kullanıcı kalıcı silindi" if hard else "Kullanıcı pasife alındı",
    )


@router.get("/users/{user_id}/export")
async def admin_export_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> Response:
    payload = await AdminService(db).export_user_data(user_id)
    raw = AdminService.export_json_bytes(payload)
    filename = f"studyos-user-{user_id}.json"
    return Response(
        content=raw,
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/questions")
async def admin_list_questions(
    source: str = Query(default="all"),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=40, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
):
    items, total = await AdminService(db).list_questions(
        source=source, q=q, page=page, page_size=page_size
    )
    meta = AdminService.pagination_meta(page, page_size, total)
    return {
        "success": True,
        "data": [i.model_dump(mode="json") for i in items],
        "pagination": meta,
        "message": "OK",
    }


@router.get(
    "/question-pool/inventory",
    response_model=SuccessResponse[list[QuestionPoolInventoryRow]],
)
async def admin_question_pool_inventory(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[list[QuestionPoolInventoryRow]]:
    rows = await QuestionPoolInventoryService().snapshot(db)
    return SuccessResponse(data=rows, message="OK")


@router.get(
    "/question-pool/metrics",
    response_model=SuccessResponse[QuestionPoolMetrics],
)
async def admin_question_pool_metrics(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[QuestionPoolMetrics]:
    inventory_rows = await QuestionPoolInventoryService().snapshot(db)
    
    from app.models.question_pool import QuestionPoolCard
    from sqlalchemy import func
    total_questions = int((await db.execute(select(func.count()).select_from(QuestionPoolCard))).scalar() or 0)

    healthy_topics = int(sum(1 for r in inventory_rows if r.get("status") == "healthy"))
    low_topics = int(sum(1 for r in inventory_rows if r.get("status") == "low"))
    empty_topics = int(sum(1 for r in inventory_rows if r.get("status") == "empty"))

    # Generation stats — pool'a yazılan kartlar (gerçek sayı) + history (gemini/cost)
    now = datetime.now(timezone.utc)
    tz = timezone(timedelta(hours=3), name="Europe/Istanbul")
    now_local = now.astimezone(tz)
    today_local = now_local.date()
    yesterday_local = (now_local - timedelta(days=1)).date()
    start_today_local = datetime.combine(today_local, datetime.min.time(), tzinfo=tz)
    start_yesterday_local = datetime.combine(
        yesterday_local, datetime.min.time(), tzinfo=tz
    )
    start_week_local = start_today_local - timedelta(days=now_local.weekday())

    # Convert to UTC timestamps for querying
    start_today_utc = start_today_local.astimezone(timezone.utc)
    start_yesterday_utc = start_yesterday_local.astimezone(timezone.utc)
    start_week_utc = start_week_local.astimezone(timezone.utc)
    end_utc = now

    async def _count_cards_created(day_start_utc: datetime, day_end_utc: datetime) -> int:
        stmt_c = (
            select(func.count())
            .select_from(QuestionPoolCard)
            .where(QuestionPoolCard.created_at >= day_start_utc)
            .where(QuestionPoolCard.created_at < day_end_utc)
        )
        return int((await db.execute(stmt_c)).scalar() or 0)

    # Bugün/dün/haftalık: havuza gerçekten eklenen kart sayısı
    today_generated = await _count_cards_created(start_today_utc, end_utc)
    yesterday_generated = await _count_cards_created(start_yesterday_utc, start_today_utc)
    weekly_generated = await _count_cards_created(start_week_utc, end_utc)

    stmt = (
        select(QuestionPoolGenerationHistory)
        .where(QuestionPoolGenerationHistory.timestamp >= start_week_utc)
        .where(QuestionPoolGenerationHistory.timestamp <= end_utc)
    )
    records = list((await db.execute(stmt.order_by(QuestionPoolGenerationHistory.timestamp.desc()))).scalars().all())

    gemini_calls_today = sum(
        int(r.gemini_calls or 0)
        for r in records
        if start_today_utc <= r.timestamp < end_utc
    )

    # Avg quality/difficulty from latest inventory snapshot
    qualities = [r.get("average_quality") for r in inventory_rows if r.get("average_quality") is not None]
    diffs = [r.get("average_difficulty") for r in inventory_rows if r.get("average_difficulty") is not None]
    average_quality = float(sum(qualities) / len(qualities)) if qualities else None
    average_difficulty = float(sum(diffs) / len(diffs)) if diffs else None

    costs = [r.estimated_cost for r in records if r.estimated_cost is not None]
    estimated_ai_cost_today = (
        float(sum(r.estimated_cost or 0.0 for r in records if start_today_utc <= r.timestamp < end_utc))
        if costs else None
    )

    # cache_hit_pct: gerçek in-memory pool hit/miss sayaçlarından hesaplanır
    from app.services.ai_cost.metrics import get_metrics as _get_ai_metrics
    _snap = _get_ai_metrics().snapshot()
    cache_hit_pct = float(_snap.get("cache_hit_pct") or 0.0)

    metrics = QuestionPoolMetrics(
        total_questions=total_questions,
        healthy_topics=healthy_topics,
        low_topics=low_topics,
        empty_topics=empty_topics,
        today_generated=int(today_generated),
        yesterday_generated=int(yesterday_generated),
        weekly_generated=int(weekly_generated),
        gemini_calls_today=int(gemini_calls_today),
        cache_hit_pct=cache_hit_pct,
        average_quality=average_quality,
        average_difficulty=average_difficulty,
        estimated_ai_cost_today=estimated_ai_cost_today,
    )
    return SuccessResponse(data=metrics, message="OK")


@router.post(
    "/question-pool/fill",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_fill(
    body: QuestionPoolFillRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    key = TopicKey(
        exam=body.exam.strip().lower(),
        subject_code=body.subject_code.strip(),
        topic_code=body.topic_code.strip(),
        difficulty_band=body.difficulty_band.strip().lower(),
    )
    svc = QuestionPoolManagerService()
    result = await svc.fill_topic_amount(
        db, key=key, count=int(body.count), dry_run=bool(body.dry_run)
    )
    return SuccessResponse(data=result, message="OK")


@router.post(
    "/question-pool/fill-missing",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_fill_missing(
    body: QuestionPoolFillMissingRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    svc = QuestionPoolManagerService()
    result = await svc.fill_missing(db=db, dry_run=bool(body.dry_run))
    return SuccessResponse(data=result, message="OK")


@router.post(
    "/question-pool/delete",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_delete(
    body: QuestionPoolDeleteRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    from sqlalchemy import delete, func, select
    from app.models.question_pool import QuestionPoolCard

    stmt = (
        delete(QuestionPoolCard)
        .where(QuestionPoolCard.exam == body.exam.strip().lower())
        .where(QuestionPoolCard.subject_code == body.subject_code.strip())
        .where(QuestionPoolCard.topic_code == body.topic_code.strip())
        .where(
            QuestionPoolCard.difficulty_band == body.difficulty_band.strip().lower()
        )
    )
    # dry_run: count only
    if body.dry_run:
        count_stmt = (
            select(func.count())
            .select_from(QuestionPoolCard)
            .where(QuestionPoolCard.exam == body.exam.strip().lower())
            .where(QuestionPoolCard.subject_code == body.subject_code.strip())
            .where(QuestionPoolCard.topic_code == body.topic_code.strip())
            .where(
                QuestionPoolCard.difficulty_band == body.difficulty_band.strip().lower()
            )
        )
        cnt = int((await db.execute(count_stmt)).scalar() or 0)
        return SuccessResponse(data={"planned_deleted": cnt}, message="OK")

    res = await db.execute(stmt)
    await db.commit()
    return SuccessResponse(data={"deleted": int(res.rowcount or 0)}, message="OK")


@router.post(
    "/question-pool/regenerate",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_regenerate(
    body: QuestionPoolRegenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    from sqlalchemy import delete
    from app.models.question_pool import QuestionPoolCard

    # Delete first
    del_stmt = (
        delete(QuestionPoolCard)
        .where(QuestionPoolCard.exam == body.exam.strip().lower())
        .where(QuestionPoolCard.subject_code == body.subject_code.strip())
        .where(QuestionPoolCard.topic_code == body.topic_code.strip())
        .where(
            QuestionPoolCard.difficulty_band == body.difficulty_band.strip().lower()
        )
    )
    if not body.dry_run:
        await db.execute(del_stmt)
        await db.commit()

    # Then refill requested count
    key = TopicKey(
        exam=body.exam.strip().lower(),
        subject_code=body.subject_code.strip(),
        topic_code=body.topic_code.strip(),
        difficulty_band=body.difficulty_band.strip().lower(),
    )
    svc = QuestionPoolManagerService()
    result = await svc.fill_topic_amount(
        db, key=key, count=int(body.count), dry_run=bool(body.dry_run)
    )
    return SuccessResponse(data=result, message="OK")


@router.post(
    "/question-pool/run-scheduler",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_run_scheduler(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """Manual trigger: run the smart pool scheduler once (fill-missing, non-dry)."""
    svc = QuestionPoolManagerService()
    result = await svc.fill_missing(db=db, dry_run=False)
    return SuccessResponse(data=result, message="Scheduler çalıştırıldı")


@router.post(
    "/question-pool/rebuild",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_rebuild(
    body: QuestionPoolRegenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    # Rebuild = hard reset + fill to requested count (same as regenerate for now)
    return await admin_question_pool_regenerate(body=body, db=db, _=_)


@router.post(
    "/question-pool/review",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_review(
    body: QuestionPoolRegenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    # Review: for now regenerate using existing pipeline, so review-qualified questions can be produced.
    return await admin_question_pool_regenerate(body=body, db=db, _=_)


@router.get(
    "/question-pool/preview/{card_id}",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_preview(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P7 — Preview a single pool card with full M34 scorecard."""
    from sqlalchemy import select
    from app.models.question_pool import QuestionPoolCard

    stmt = select(QuestionPoolCard).where(QuestionPoolCard.id == card_id)
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Card not found")

    question = {
        "stem": row.stem,
        "choices": row.choices or {},
        "correct_key": row.correct_key,
        "explanation": row.explanation,
    }
    qie = row.qie_card or {}
    plan = qie.get("plan", qie)  # qie_card often contains plan fields

    from app.services.question_intelligence.pipeline import evaluate_question
    result = evaluate_question(
        question, plan,
        author_scores=qie,
        review_scores=qie,
        vsse_scores=qie,
    )

    return SuccessResponse(
        data={
            "id": str(row.id),
            "exam": row.exam,
            "subject_code": row.subject_code,
            "topic_code": row.topic_code,
            "difficulty_band": row.difficulty_band,
            "stem": row.stem,
            "choices": row.choices,
            "correct_key": row.correct_key,
            "explanation": row.explanation,
            "use_count": row.use_count,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "qie_card": qie,
            "scorecard": result["scorecard"].to_dict(),
            "blueprint": result["blueprint"].to_dict(),
            "exam_feel": result["exam_feel"].to_dict(),
            "option_balance": result["option_balance"].to_dict(),
            "distractor_quality": result["distractor_quality"].to_dict(),
            "multi_stage": result["multi_stage"].to_dict(),
            "accepted": result["accepted"],
            "reject_reason": result["reject_reason"],
        },
        message="OK",
    )


@router.post(
    "/question-pool/preview-latest",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_preview_latest(
    body: QuestionPoolDeleteRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P7 — Preview a latest pool card for a topic (for admin UI)."""
    from sqlalchemy import select

    from app.models.question_pool import QuestionPoolCard
    from app.services.question_intelligence.pipeline import evaluate_question

    stmt = (
        select(QuestionPoolCard)
        .where(QuestionPoolCard.exam == body.exam.strip().lower())
        .where(QuestionPoolCard.subject_code == body.subject_code.strip())
        .where(QuestionPoolCard.topic_code == body.topic_code.strip())
        .where(
            QuestionPoolCard.difficulty_band == body.difficulty_band.strip().lower()
        )
        .order_by(QuestionPoolCard.created_at.desc())
        .limit(1)
    )
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("No pool card found for given topic")

    question = {
        "stem": row.stem,
        "choices": row.choices or {},
        "correct_key": row.correct_key,
        "explanation": row.explanation,
    }
    qie = row.qie_card or {}
    plan = qie.get("plan", qie)

    result = evaluate_question(
        question,
        plan,
        author_scores=qie,
        review_scores=qie,
        vsse_scores=qie,
    )

    return SuccessResponse(
        data={
            "id": str(row.id),
            "exam": row.exam,
            "subject_code": row.subject_code,
            "topic_code": row.topic_code,
            "difficulty_band": row.difficulty_band,
            "stem": row.stem,
            "choices": row.choices,
            "correct_key": row.correct_key,
            "explanation": row.explanation,
            "use_count": row.use_count,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "qie_card": qie,
            "scorecard": result["scorecard"].to_dict(),
            "blueprint": result["blueprint"].to_dict(),
            "exam_feel": result["exam_feel"].to_dict(),
            "option_balance": result["option_balance"].to_dict(),
            "distractor_quality": result["distractor_quality"].to_dict(),
            "multi_stage": result["multi_stage"].to_dict(),
            "accepted": result["accepted"],
            "reject_reason": result["reject_reason"],
        },
        message="OK",
    )

@router.get(
    "/question-pool/batch-report",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_batch_report(
    exam: str = Query(default=""),
    subject_code: str = Query(default=""),
    topic_code: str = Query(default=""),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P8 — Generate batch quality report for pool cards."""
    from sqlalchemy import select
    from app.models.question_pool import QuestionPoolCard
    from app.services.question_intelligence.pipeline import evaluate_batch

    stmt = select(QuestionPoolCard).order_by(QuestionPoolCard.created_at.desc()).limit(limit)
    if exam:
        stmt = stmt.where(QuestionPoolCard.exam == exam.strip().lower())
    if subject_code:
        stmt = stmt.where(QuestionPoolCard.subject_code == subject_code.strip())
    if topic_code:
        stmt = stmt.where(QuestionPoolCard.topic_code == topic_code.strip())

    rows = list((await db.execute(stmt)).scalars().all())

    questions = []
    plans = []
    for row in rows:
        questions.append({
            "stem": row.stem,
            "choices": row.choices or {},
            "correct_key": row.correct_key,
            "explanation": row.explanation,
        })
        qie = row.qie_card or {}
        plans.append(qie.get("plan", qie))

    results, report = evaluate_batch(questions, plans)

    return SuccessResponse(
        data={
            "report": report.to_dict(),
            "sample_results": [
                {
                    "stem_preview": str(r["question"].get("stem", ""))[:80],
                    "accepted": r["accepted"],
                    "reject_reason": r["reject_reason"],
                    "overall": r["scorecard"].overall,
                    "blueprint": r["blueprint"].score,
                    "exam_feel": r["exam_feel"].score,
                }
                for r in results[:20]
            ],
        },
        message="OK",
    )


@router.get(
    "/question-pool/production-report",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_production_report(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P10 — Production readiness report."""
    from sqlalchemy import select
    from app.models.question_pool import QuestionPoolCard
    from app.services.question_intelligence.pipeline import evaluate_batch
    from app.services.question_intelligence.production_report import build_production_report

    # Get last 200 cards grouped by topic
    stmt = select(QuestionPoolCard).order_by(QuestionPoolCard.created_at.desc()).limit(200)
    rows = list((await db.execute(stmt)).scalars().all())

    # Group by topic
    topic_groups: dict[str, list] = {}
    for row in rows:
        key = f"{row.exam}:{row.subject_code}:{row.topic_code}"
        topic_groups.setdefault(key, []).append(row)

    batch_reports = []
    topic_scores: dict[str, float] = {}

    for topic_key, topic_rows in topic_groups.items():
        questions = [{
            "stem": r.stem,
            "choices": r.choices or {},
            "correct_key": r.correct_key,
            "explanation": r.explanation,
        } for r in topic_rows]
        plans = [(r.qie_card or {}).get("plan", r.qie_card or {}) for r in topic_rows]

        results, report = evaluate_batch(questions, plans)
        batch_reports.append(report)
        topic_scores[topic_key] = report.average_quality

    prod_report = build_production_report(batch_reports, topic_scores)

    return SuccessResponse(
        data=prod_report.to_dict(),
        message="OK",
    )


# ── M34.5 Production Validation & Cost-Aware Generation ───────


@router.get(
    "/question-pool/cost-gate",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_cost_gate(
    planned_count: int = Query(default=10, ge=1, le=200),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P0 — Can Generate? daily/hourly/minute + estimated batch cost."""
    from app.services.question_production.cost_gate import check_can_generate

    gate = check_can_generate(planned_count=planned_count)
    return SuccessResponse(data=gate.to_dict(), message="OK")


@router.get(
    "/question-pool/live-progress",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_live_progress(
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P3 — Live generation progress snapshot."""
    from app.services.question_production.progress import get_progress_tracker

    return SuccessResponse(data=get_progress_tracker().get().to_dict(), message="OK")


@router.post(
    "/question-pool/stop-generation",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_stop_generation(
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P9 — Safe stop: finish current question, then halt batch."""
    from app.services.question_production.controller import ProductionController

    ProductionController().stop()
    return SuccessResponse(data={"stopping": True}, message="Stop requested")


@router.post(
    "/question-pool/validate-generate",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_validate_generate(
    body: ProductionValidateRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P10 — Generate up to 5 questions, DO NOT SAVE to pool."""
    from app.services.question_production.controller import ProductionController

    result = await ProductionController().validate_generate_five(
        db,
        exam=body.exam,
        subject_code=body.subject_code,
        topic_code=body.topic_code,
        difficulty_band=body.difficulty_band,
        subject_name=body.subject_name or body.subject_code,
        topic_name=body.topic_name or body.topic_code,
        count=int(body.count),
    )
    return SuccessResponse(data=result, message="Validation generate OK")


@router.post(
    "/question-pool/run-missing-safe",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_run_missing_safe(
    body: ProductionRunMissingRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P2 — Only generate topics where current < minimum (cost-aware)."""
    from app.services.question_production.controller import ProductionController

    result = await ProductionController().run_missing_topics(
        db,
        approval_mode=body.approval_mode,
        max_topics=body.max_topics,
    )
    return SuccessResponse(data=result, message="OK")


@router.post(
    "/question-pool/generate-topic-safe",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_generate_topic_safe(
    body: ProductionGenerateTopicRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """Cost-aware topic generation with optional manual approval."""
    from app.services.question_production.controller import ProductionController

    result = await ProductionController().generate_topic(
        db,
        exam=body.exam,
        subject_code=body.subject_code,
        topic_code=body.topic_code,
        difficulty_band=body.difficulty_band,
        count=int(body.count),
        approval_mode=body.approval_mode,
        save=bool(body.save),
        subject_name=body.subject_name or body.subject_code,
        topic_name=body.topic_name or body.topic_code,
    )
    return SuccessResponse(data=result, message="OK")


@router.get(
    "/question-pool/pending",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_pending(
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P5 — List pending questions awaiting manual approval."""
    from app.services.question_production.controller import ProductionController

    items = ProductionController().list_pending()
    return SuccessResponse(data={"items": items}, message="OK")


@router.post(
    "/question-pool/approve-pending",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_approve_pending(
    body: ProductionApproveRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P5 — Approve a pending question → save to pool."""
    from app.services.question_production.controller import ProductionController

    result = await ProductionController().approve_pending(db, pending_id=body.pending_id)
    return SuccessResponse(data=result, message="Approved")


@router.post(
    "/question-pool/reject-pending",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_reject_pending(
    body: ProductionApproveRequest,
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """P5 — Reject a pending question (do not save)."""
    from app.services.question_production.controller import ProductionController

    result = ProductionController().reject_pending(pending_id=body.pending_id)
    return SuccessResponse(data=result, message="Rejected")


@router.post(
    "/question-pool/card",
    response_model=SuccessResponse[dict],
)
async def admin_question_pool_create_card(
    body: QuestionPoolCardCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """Manually create a pool card with optional EAE interaction."""
    from app.models.question_pool import QuestionPoolCard
    from app.services.qie.types import QuestionPlan, QualityBreakdown, QuestionCard

    # Dummy QIE plan and card for manual inserts
    plan = QuestionPlan(
        exam=body.exam.lower(),
        subject_code=body.subject_code,
        subject_name=body.subject_code,
        topic_code=body.topic_code,
        topic_name=body.topic_code,
        skill="manual_entry",
        difficulty=70,
    )
    
    qie_card = QuestionCard(
        stem=body.stem,
        choices=body.choices,
        correct_key=body.correct_key,
        explanation=body.explanation,
        plan=plan,
        difficulty_score=70,
        quality=QualityBreakdown(total=100),
        provider="manual",
    )
    
    qie_dict = qie_card.to_persist_dict()
    if body.eae_interaction:
        qie_dict["eae_interaction"] = body.eae_interaction

    import hashlib
    content = f"{body.exam}:{body.subject_code}:{body.topic_code}:{body.stem}:{body.correct_key}"
    fp = hashlib.sha256(content.encode()).hexdigest()

    card = QuestionPoolCard(
        fingerprint=fp,
        content_hash=fp,
        exam=body.exam.lower(),
        subject_code=body.subject_code,
        topic_code=body.topic_code,
        difficulty_band=body.difficulty_band.lower(),
        skill="manual_entry",
        stem=body.stem,
        choices=body.choices,
        correct_key=body.correct_key,
        explanation=body.explanation,
        qie_card=qie_dict,
    )

    db.add(card)
    await db.commit()
    return SuccessResponse(data={"id": str(card.id)}, message="Soru havuza eklendi")


@router.post(
    "/trial-exams/trigger",
    response_model=SuccessResponse[dict],
)
async def admin_trigger_trial_exam_generation(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[dict]:
    """Manually trigger the midnight trial exam generation pipeline."""
    from app.services.trial_exam_scheduler import generate_trial_exams_for_today
    import asyncio
    
    # Run in background to avoid blocking the HTTP response
    asyncio.create_task(generate_trial_exams_for_today(db))
    return SuccessResponse(data={"message": "Trial exam generation started in background."})

