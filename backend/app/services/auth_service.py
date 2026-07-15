"""
StudyOS — Auth Service
Kayıt, giriş, token yenileme (rotation) ve çıkış iş mantığı.
Bkz. docs/architecture/software-architecture.md §3.1, §3.2
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    refresh_token_expiry,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole, UserStatus
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    async def register(self, data: RegisterRequest) -> tuple[User, str, str]:
        """Yeni kullanıcı kaydı oluşturur ve token çifti üretir."""
        if await self.user_repo.email_exists(data.email):
            raise ConflictError("Bu e-posta adresi zaten kayıtlı")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            role=UserRole(data.role),
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

    async def _issue_token_pair(self, user: User) -> tuple[str, str]:
        """Kullanıcı için yeni access + refresh token çifti üretir ve refresh'i DB'ye kaydeder."""
        access_token = create_access_token(user.id, user.role)
        raw_refresh_token = generate_refresh_token()

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh_token),
            expires_at=refresh_token_expiry(),
        )
        await self.token_repo.add(refresh_token_record)

        return access_token, raw_refresh_token
