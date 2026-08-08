"""
Sprint 18 — Assessment & Daily Challenge API
LOS §11 Sense — Decision üretmez.
"""

from __future__ import annotations

import uuid

from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.exceptions import NotFoundError, ValidationError
from app.database.base import get_db
from app.models.assessment import AssessmentSessionStatus
from app.models.user import User
from app.schemas.assessment import (
    AssessmentOverview,
    AssessmentSessionRead,
    AssessmentStartRequest,
    AssessmentSubmitRequest,
    AssessmentSubmitResult,
    AssessmentWrongExplainRequest,
    AssessmentWrongExplainResponse,
    DailyChallengeBundle,
    DailyHistoryItemRead,
    DailySubjectsBundle,
    EstimatedScoreRead,
    LeaderboardRead,
    RankingRead,
)
from app.schemas.common import SuccessResponse
from app.services.assessment_explain_service import AssessmentExplainService
from app.services.assessment_service import AssessmentService
from app.services.booklet_generation import run_booklet_generation
from app.services.booklet_pdf_service import build_assessment_report_pdf, build_booklet_pdf

router = APIRouter()


@router.get("", response_model=SuccessResponse[AssessmentOverview])
async def assessment_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AssessmentOverview]:
    data = await AssessmentService(db).overview(current_user.id)
    return SuccessResponse(data=data)


@router.post("/start", response_model=SuccessResponse[AssessmentSessionRead])
async def assessment_start(
    body: AssessmentStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AssessmentSessionRead]:
    data = await AssessmentService(db).start(current_user.id, body)
    await db.commit()
    return SuccessResponse(data=data, message="Assessment hazır")


@router.get(
    "/sessions/{session_id}",
    response_model=SuccessResponse[AssessmentSessionRead],
)
async def assessment_get(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AssessmentSessionRead]:
    data = await AssessmentService(db).get_session(current_user.id, session_id)
    await db.commit()
    return SuccessResponse(data=data)


@router.get("/sessions/{session_id}/pdf")
async def assessment_session_pdf(
    session_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    svc = AssessmentService(db)
    session = await svc.repo.get_session(session_id, current_user.id)
    if session is None:
        raise NotFoundError("Assessment", str(session_id))
    if session.status == AssessmentSessionStatus.PENDING or not session.questions:
        # Sync üretme — timeout. Worker'ı tetikle, client poll etsin.
        if session.is_booklet and session.status == AssessmentSessionStatus.PENDING:
            background_tasks.add_task(
                run_booklet_generation, session.id, current_user.id
            )
        raise ValidationError(
            "Kitapçık henüz hazır değil — birkaç saniye sonra tekrar dene"
        )
    from app.services.asset_registry_service import AssetRegistryService
    from app.services.asset_compiler.packager import BundlePackager
    registry = AssetRegistryService(db)
    packager = BundlePackager()

    for q in session.questions:
        q_meta = q.qie_card or {}
        if isinstance(q_meta, dict) and "target_asset_id" in q_meta and "eae_svg_content" not in q_meta:
            try:
                asset = await registry.get_asset_by_uri(q_meta["target_asset_id"])
                if asset and asset.versions:
                    # Pick latest version
                    latest_version = sorted(asset.versions, key=lambda v: v.version)[-1]
                    if latest_version.bundle_payload:
                        unpacked = packager.unpack(latest_version.bundle_payload)
                        # We mutate it in memory. Since we don't db.commit(), it's fine.
                        new_meta = dict(q_meta)
                        new_meta["eae_svg_content"] = unpacked.get("svg_content")
                        q.qie_card = new_meta
            except Exception:
                pass

    pdf_bytes = build_booklet_pdf(session)
    filename = f"gunun-denemesi-{session.challenge_date or session_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post(
    "/sessions/{session_id}/submit",
    response_model=SuccessResponse[AssessmentSubmitResult],
)
async def assessment_submit(
    session_id: uuid.UUID,
    body: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AssessmentSubmitResult]:
    data = await AssessmentService(db).submit(current_user.id, session_id, body)
    await db.commit()
    return SuccessResponse(data=data, message="Assessment kaydedildi")


@router.post(
    "/sessions/{session_id}/continue-adaptive",
    response_model=SuccessResponse[AssessmentSessionRead],
)
async def assessment_continue_adaptive(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    early_correct: int | None = Query(default=None, ge=0),
    early_total: int | None = Query(default=None, ge=0),
) -> SuccessResponse[AssessmentSessionRead]:
    """Sprint 25 — fill remaining calibration questions after first batch."""
    data = await AssessmentService(db).continue_adaptive_calibration(
        current_user.id,
        session_id,
        early_answers_correct=early_correct,
        early_answers_total=early_total,
    )
    await db.commit()
    return SuccessResponse(data=data, message="Adaptive sorular eklendi")


@router.post(
    "/sessions/{session_id}/questions/{question_id}/explain",
    response_model=SuccessResponse[AssessmentWrongExplainResponse],
)
async def assessment_wrong_explain(
    session_id: uuid.UUID,
    question_id: uuid.UUID,
    body: AssessmentWrongExplainRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AssessmentWrongExplainResponse]:
    data = await AssessmentExplainService(db).explain_wrong(
        current_user.id, session_id, question_id, body
    )
    await db.commit()
    return SuccessResponse(data=data)


@router.get("/sessions/{session_id}/report.pdf")
async def assessment_session_report_pdf(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    svc = AssessmentService(db)
    session = await svc.repo.get_session(session_id, current_user.id)
    if session is None:
        raise NotFoundError("Assessment", str(session_id))
    if session.status != AssessmentSessionStatus.SUBMITTED:
        raise ValidationError("Rapor yalnızca gönderilmiş oturumlarda")
    pdf_bytes = build_assessment_report_pdf(session)
    filename = f"assessment-rapor-{session.challenge_date or session_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/daily-challenge", response_model=SuccessResponse[DailyChallengeBundle])
async def daily_challenge(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[DailyChallengeBundle]:
    data = await AssessmentService(db).daily_bundle(current_user.id)
    return SuccessResponse(data=data)


@router.get(
    "/daily-challenge/history",
    response_model=SuccessResponse[list[DailyHistoryItemRead]],
)
async def daily_challenge_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[list[DailyHistoryItemRead]]:
    data = await AssessmentService(db).daily_history(current_user.id)
    return SuccessResponse(data=data)


@router.get(
    "/daily-challenge/subjects",
    response_model=SuccessResponse[DailySubjectsBundle],
)
async def daily_challenge_subjects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[DailySubjectsBundle]:
    data = await AssessmentService(db).daily_subjects(current_user.id)
    return SuccessResponse(data=data)


@router.post(
    "/daily-challenge/start",
    response_model=SuccessResponse[AssessmentSessionRead],
)
async def daily_challenge_start(
    body: AssessmentStartRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AssessmentSessionRead]:
    # Soru üretimi kullanıcı isteğinde yapılmaz — gece 00:00 Gemini job
    req = AssessmentStartRequest(
        kind="daily_challenge",
        subject_code=None,
        topic_code=None,
        count=None,
        difficulty=(body.difficulty if body else "medium") or "medium",
        synthetic=False,
    )
    data = await AssessmentService(db).start(current_user.id, req)
    await db.commit()
    if data.is_booklet and data.status == "pending":
        return SuccessResponse(
            data=data,
            message="Günün denemesi henüz hazır değil — gece Gemini üretimi bekleniyor",
        )
    return SuccessResponse(data=data, message="Günün denemesi hazır")


@router.get(
    "/daily-challenge/leaderboard",
    response_model=SuccessResponse[LeaderboardRead],
)
async def daily_challenge_leaderboard(
    subject_code: str | None = Query(default=None),
    challenge_date: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LeaderboardRead]:
    data = await AssessmentService(db).leaderboard(
        current_user.id,
        subject_code=subject_code,
        challenge_date=challenge_date,
    )
    return SuccessResponse(data=data)


@router.get(
    "/daily-challenge/leaderboard/overall",
    response_model=SuccessResponse[LeaderboardRead],
)
async def daily_challenge_leaderboard_overall(
    challenge_date: date | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[LeaderboardRead]:
    data = await AssessmentService(db).leaderboard(
        current_user.id,
        subject_code=None,
        challenge_date=challenge_date,
    )
    return SuccessResponse(data=data)


@router.get("/estimated-score", response_model=SuccessResponse[EstimatedScoreRead])
async def estimated_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[EstimatedScoreRead]:
    data = await AssessmentService(db).estimated_score(current_user.id)
    return SuccessResponse(data=data)


@router.get("/ranking", response_model=SuccessResponse[RankingRead])
async def ranking(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[RankingRead]:
    data = await AssessmentService(db).ranking(current_user.id)
    return SuccessResponse(data=data)
