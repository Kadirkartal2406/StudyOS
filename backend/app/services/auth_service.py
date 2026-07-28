"""
StudyOS — Auth Service
Kayıt, giriş, token yenileme (rotation) ve çıkış iş mantığı.
Bkz. docs/architecture/software-architecture.md §3.1, §3.2
"""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, ValidationError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    refresh_token_expiry,
    verify_password,
)
from app.models.password_reset import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole, UserStatus
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    ForgotPasswordResponse,
    LoginRequest,
    RegisterRequest,
)
from app.services.email_service import send_password_reset_email, smtp_configured

logger = logging.getLogger("studyos.auth")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(self, data: RegisterRequest) -> tuple[User, str, str]:
        """Yeni kullanıcı kaydı oluşturur ve token çifti üretir."""
        if await self.user_repo.email_exists(data.email):
            raise ConflictError("Bu e-posta adresi zaten kayıtlı")

        # Public register: yalnızca öğrenci (admin rolü bootstrap ile gelir)
        role = UserRole.STUDENT
        if data.role not in (UserRole.STUDENT, UserRole.TEACHER):
            role = UserRole.STUDENT
        else:
            role = UserRole(data.role)

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=role,
            status=UserStatus.ACTIVE,
            is_verified=False,
        )
        await self.user_repo.add(user)

        access_token, refresh_token = await self._issue_token_pair(user)
        return user, access_token, refresh_token

    async def login(self, data: LoginRequest) -> tuple[User, str, str]:
        """E-posta ve şifre ile giriş yapar; token çifti üretir."""
        user = await self.user_repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise AuthenticationError("E-posta veya şifre hatalı")

        if user.status in (UserStatus.INACTIVE, UserStatus.ANONYMIZED):
            raise AuthenticationError("Bu hesap artık kullanılamıyor")

        await self.user_repo.update_last_login(user)

        access_token, refresh_token = await self._issue_token_pair(user)
        return user, access_token, refresh_token

    async def refresh(self, raw_refresh_token: str) -> tuple[str, str]:
        """Refresh token rotation: eski token'ı iptal eder, yeni çift üretir."""
        token_hash = hash_token(raw_refresh_token)
        stored_token = await self.token_repo.get_by_hash(token_hash)

        if stored_token is None or not self.token_repo.is_valid(stored_token):
            raise AuthenticationError("Geçersiz veya süresi dolmuş refresh token")

        user = await self.user_repo.get_by_id(stored_token.user_id)
        if user is None:
            raise AuthenticationError("Kullanıcı bulunamadı")

        await self.token_repo.revoke(stored_token)
        access_token, new_refresh_token = await self._issue_token_pair(user)
        return access_token, new_refresh_token

    async def logout(self, raw_refresh_token: str) -> None:
        """Refresh token'ı geçersiz kılar. Token bulunamasa da hata fırlatmaz (idempotent)."""
        token_hash = hash_token(raw_refresh_token)
        stored_token = await self.token_repo.get_by_hash(token_hash)
        if stored_token is not None and not stored_token.is_revoked:
            await self.token_repo.revoke(stored_token)

    async def forgot_password(self, email: str) -> ForgotPasswordResponse:
        """
        Sıfırlama token'ı üretir ve e-posta gönderir.
        Bilinmeyen e-posta için de aynı genel başarı mesajını döner.
        """
        generic = ForgotPasswordResponse()
        user = await self.user_repo.get_by_email(email.strip().lower())
        if user is None:
            user = await self.user_repo.get_by_email(email.strip())
        if user is None or user.status in (UserStatus.INACTIVE, UserStatus.ANONYMIZED):
            return generic

        raw_token = secrets.token_urlsafe(48)
        expires = datetime.now(UTC) + timedelta(
            minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
        )
        self.db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(raw_token),
                expires_at=expires,
            )
        )
        await self.db.flush()

        base = settings.PUBLIC_APP_URL.rstrip("/")
        reset_url = f"{base}/admin/reset-password.html?token={raw_token}"
        email_sent = await send_password_reset_email(to=user.email, reset_url=reset_url)

        # Dev / SMTP yok: log + DEBUG yanıtı (mobil/admin test için)
        if not email_sent:
            logger.warning(
                "Password reset token for %s (SMTP missing or send failed): %s",
                user.email,
                raw_token,
            )

        include_dev = settings.DEBUG or not smtp_configured()
        return ForgotPasswordResponse(
            message=(
                "Sıfırlama bağlantısı e-posta ile gönderildi"
                if email_sent
                else "Sıfırlama kodu oluşturuldu (e-posta yapılandırılmadı — geliştirme modu)"
            ),
            email_sent=email_sent,
            dev_reset_token=raw_token if include_dev else None,
            reset_url=reset_url if include_dev else None,
        )

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        """Token ile şifreyi günceller; tüm refresh token'ları iptal eder."""
        token_hash = hash_token(raw_token.strip())
        result = await self.db.execute(
            select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        )
        row = result.scalar_one_or_none()
        now = datetime.now(UTC)
        if row is None or row.used_at is not None or row.expires_at < now:
            raise ValidationError("Geçersiz veya süresi dolmuş sıfırlama bağlantısı")

        user = await self.user_repo.get_by_id(row.user_id)
        if user is None:
            raise ValidationError("Geçersiz veya süresi dolmuş sıfırlama bağlantısı")

        user.hashed_password = hash_password(new_password)
        row.used_at = now
        await self.token_repo.revoke_all_for_user(user.id)
        await self.db.flush()

    async def _issue_token_pair(self, user: User) -> tuple[str, str]:
        """Kullanıcı için yeni access + refresh token çifti üretir ve refresh'i DB'ye kaydeder."""
        access_token = create_access_token(user.id, str(user.role))
        raw_refresh_token = generate_refresh_token()

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh_token),
            expires_at=refresh_token_expiry(),
        )
        await self.token_repo.add(refresh_token_record)

        return access_token, raw_refresh_token
