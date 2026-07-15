"""
StudyOS — FastAPI Dependencies
JWT doğrulama ve mevcut kullanıcı (current user) bağımlılığı.
"""

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.database.base import get_db
from app.models.user import User
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

    return user
