"""
StudyOS — Notification Settings Endpoint'leri
Bkz. docs/architecture/api-design.md §2.17 (Sprint-1.8)
Inbox yok — yalnızca tercihler + FCM token kaydı.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.notification_settings import (
    FcmTokenUpdate,
    NotificationSettingsRead,
    NotificationSettingsUpdate,
)
from app.services.notification_settings_service import NotificationSettingsService

router = APIRouter()


@router.get("", response_model=SuccessResponse[NotificationSettingsRead])
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[NotificationSettingsRead]:
    data = await NotificationSettingsService(db).get_settings(current_user.id)
    return SuccessResponse(data=data)


@router.put("", response_model=SuccessResponse[NotificationSettingsRead])
async def put_notification_settings(
    body: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[NotificationSettingsRead]:
    data = await NotificationSettingsService(db).update_settings(current_user.id, body)
    return SuccessResponse(data=data, message="Bildirim ayarları güncellendi")


@router.put("/fcm-token", response_model=SuccessResponse[NotificationSettingsRead])
async def put_fcm_token(
    body: FcmTokenUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[NotificationSettingsRead]:
    """FCM token saklar; sunucu push gönderimi sonraki sprintte."""
    data = await NotificationSettingsService(db).update_fcm_token(current_user.id, body)
    return SuccessResponse(data=data, message="FCM token kaydedildi")
