"""
StudyOS — User Endpoint'leri
Bkz. docs/architecture/api-design.md §2.2
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.user import UserRead

router = APIRouter()


@router.get("/me", response_model=SuccessResponse[UserRead])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[UserRead]:
    """Giriş yapan kullanıcının profil bilgisini döner."""
    return SuccessResponse(data=UserRead.from_user(current_user))
