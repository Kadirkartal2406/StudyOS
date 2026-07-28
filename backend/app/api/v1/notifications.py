"""
StudyOS — In-App Notifications API
Sprint 13 — Akıllı bildirimler (push değil; in-app banner)
"""

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.services.notification_decision_service import NotificationDecisionService

router = APIRouter()


class InAppNotification(BaseModel):
    id: str
    type: Literal["revision_due", "plan_suggestion", "streak_risk", "milestone", "observation"]
    title: str
    body: str
    deep_link: str | None = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    notifications: list[InAppNotification]
    unread_count: int


class NotificationDecisionItem(BaseModel):
    type: str
    title: str
    body: str
    deep_link: str | None = None


class NotificationDecisionsResponse(BaseModel):
    decisions: list[NotificationDecisionItem]


@router.get("", response_model=SuccessResponse[NotificationListResponse])
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[NotificationListResponse]:
    """Sprint 13 — Kullanıcının in-app bildirimlerini getir."""
    notes: list[InAppNotification] = []
    now = datetime.now(UTC)

    # Decision service adayları
    try:
        decisions = await NotificationDecisionService(db).evaluate(current_user.id)
        for i, d in enumerate(decisions):
            notes.append(
                InAppNotification(
                    id=f"decision_{d.get('type', 'n')}_{i}",
                    type=d.get("type", "revision_due"),  # type: ignore[arg-type]
                    title=d.get("title", ""),
                    body=d.get("body", ""),
                    deep_link=d.get("deep_link"),
                    created_at=now,
                )
            )
    except Exception:
        pass

    # Pending plan suggestions
    try:
        from app.services.planner_service import PlannerService

        pending = await PlannerService(db).list_pending(current_user.id)
        if pending:
            notes.append(
                InAppNotification(
                    id="plan_suggestion",
                    type="plan_suggestion",
                    title="Sistem bir öneri hazırladı",
                    body="Çalışma planın için yeni bir öneri var. İncele ve kabul et.",
                    deep_link="/planner",
                    created_at=now,
                )
            )
    except Exception:
        pass

    # Observation mode reminder
    try:
        obs_state = getattr(current_user, "observation_state", None)
        if obs_state and obs_state != "full":
            notes.append(
                InAppNotification(
                    id="observation",
                    type="observation",
                    title="Seni tanıyoruz",
                    body="StudyOS seni daha iyi tanımak için verilerini analiz ediyor. Çalışmaya devam et!",
                    deep_link="/subjects",
                    created_at=now,
                )
            )
    except Exception:
        pass

    return SuccessResponse(
        data=NotificationListResponse(
            notifications=notes,
            unread_count=len(notes),
        )
    )


@router.get("/decisions", response_model=SuccessResponse[NotificationDecisionsResponse])
async def list_notification_decisions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[NotificationDecisionsResponse]:
    """Sprint 13 — Notification Decision Service adayları (push yok)."""
    raw = await NotificationDecisionService(db).evaluate(current_user.id)
    items = [NotificationDecisionItem(**d) for d in raw]
    return SuccessResponse(data=NotificationDecisionsResponse(decisions=items))
