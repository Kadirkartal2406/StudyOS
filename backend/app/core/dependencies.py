"""
StudyOS — FastAPI Dependencies
JWT doğrulama ve mevcut kullanıcı (current user) bağımlılığı.
"""

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.database.base import get_db
from app.models.user import User, UserRole, UserStatus
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Authorization header'ındaki Bearer JWT'yi doğrular, ilgili kullanıcıyı döner."""
    if token is None:
        raise AuthenticationError("Kimlik doğrulama gerekli")

    payload = decode_access_token(token)
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Geçersiz token içeriği") from exc

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise AuthenticationError("Kullanıcı bulunamadı")

    if user.status in (UserStatus.INACTIVE, UserStatus.ANONYMIZED):
        raise AuthenticationError("Bu hesap artık kullanılamıyor")

    return user


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Auth opsiyonel — analytics gibi anonim olaylar için."""
    if token is None:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except AuthenticationError:
        return None


async def require_system_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Yalnızca system_admin."""
    if str(user.role) != UserRole.SYSTEM_ADMIN:
        raise AuthorizationError("Bu işlem yalnızca sistem yöneticisi içindir")
    return user