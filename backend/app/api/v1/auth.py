"""
StudyOS — Auth Endpoint'leri
Bkz. docs/architecture/api-design.md §2.1
Domain exception'lar servis katmanından fırlatılır; HTTP çevirisi
app/main.py'deki merkezi exception handler tarafından yapılır.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import get_db
from app.middleware.rate_limit import AUTH_RATE_LIMIT, limiter
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenRefreshResponse,
)
from app.schemas.common import SuccessResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse[AuthResponse],
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit(AUTH_RATE_LIMIT)
async def register_user(
    request: Request,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AuthResponse]:
    """Yeni kullanıcı kaydı oluşturur; access + refresh token döner."""
    user, access_token, refresh_token = await AuthService(db).register(body)
    data = AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.from_user(user),
    )
    return SuccessResponse(data=data, message="Kayıt başarılı")


@router.post("/login", response_model=SuccessResponse[AuthResponse])
@limiter.limit(AUTH_RATE_LIMIT)
async def login_user(
    request: Request,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AuthResponse]:
    """E-posta ve şifre ile giriş yapar; access + refresh token döner."""
    user, access_token, refresh_token = await AuthService(db).login(body)
    data = AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserRead.from_user(user),
    )
    return SuccessResponse(data=data, message="Giriş başarılı")


@router.post("/refresh", response_model=SuccessResponse[TokenRefreshResponse])
@limiter.limit(AUTH_RATE_LIMIT)
async def refresh_token(
    request: Request,
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[TokenRefreshResponse]:
    """Refresh token rotation ile yeni access + refresh token üretir."""
    access_token, new_refresh_token = await AuthService(db).refresh(body.refresh_token)
    data = TokenRefreshResponse(access_token=access_token, refresh_token=new_refresh_token)
    return SuccessResponse(data=data, message="Token yenilendi")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(AUTH_RATE_LIMIT)
async def logout_user(
    request: Request,
    body: LogoutRequest,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Refresh token'ı geçersiz kılar."""
    await AuthService(db).logout(body.refresh_token)


@router.post(
    "/forgot-password",
    response_model=SuccessResponse[ForgotPasswordResponse],
)
@limiter.limit(AUTH_RATE_LIMIT)
async def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ForgotPasswordResponse]:
    """Şifre sıfırlama e-postası / geliştirme token'ı üretir."""
    data = await AuthService(db).forgot_password(str(body.email))
    await db.commit()
    return SuccessResponse(data=data, message=data.message)


@router.post("/reset-password", response_model=SuccessResponse[dict])
@limiter.limit(AUTH_RATE_LIMIT)
async def reset_password(
    request: Request,
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    """Token ile yeni şifre belirler."""
    await AuthService(db).reset_password(body.token, body.new_password)
    await db.commit()
    return SuccessResponse(data={}, message="Şifre güncellendi")
