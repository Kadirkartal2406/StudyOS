"""
StudyOS — Güvenlik Yardımcıları
bcrypt şifre hash/doğrulama ve JWT access token üretme/doğrulama.
Refresh token, JWT değil; rastgele opak bir dizedir (DB'de hash'i tutulur).
Bkz. docs/architecture/software-architecture.md §3.1, §3.2
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthenticationError

_pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)

TOKEN_TYPE_ACCESS = "access"


def hash_password(plain_password: str) -> str:
    """Düz metin şifreyi bcrypt ile hash'ler."""
    return _pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Düz metin şifreyi bcrypt hash'i ile karşılaştırır."""
    return _pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    """Kısa ömürlü (15 dk) JWT access token üretir."""
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "type": TOKEN_TYPE_ACCESS,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """JWT access token'ı doğrular ve payload'ı döner. Geçersizse AuthenticationError fırlatır."""
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError as exc:
        raise AuthenticationError("Geçersiz veya süresi dolmuş oturum") from exc

    if payload.get("type") != TOKEN_TYPE_ACCESS:
        raise AuthenticationError("Geçersiz token türü")
    return payload


def generate_refresh_token() -> str:
    """Kriptografik olarak güvenli, rastgele bir refresh token dizesi üretir."""
    return secrets.token_urlsafe(64)


def hash_token(raw_token: str) -> str:
    """Refresh token'ın veritabanında saklanacak SHA-256 hash'ini üretir."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def refresh_token_expiry() -> datetime:
    """Yeni bir refresh token için son kullanma tarihini hesaplar."""
    return datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
