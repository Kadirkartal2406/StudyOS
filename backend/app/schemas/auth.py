"""
StudyOS — Auth Pydantic Şemaları
Bkz. docs/architecture/api-design.md §2.1
"""

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: UserRole = UserRole.STUDENT


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    """Register/login başarı yanıtı — Flutter AuthResponseModel ile eşleşir."""

    access_token: str
    refresh_token: str
    user: UserRead


class TokenRefreshResponse(BaseModel):
    """Refresh başarı yanıtı — Flutter TokenRefreshModel ile eşleşir."""

    access_token: str
    refresh_token: str
