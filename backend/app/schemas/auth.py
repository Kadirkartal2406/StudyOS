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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Her zaman başarılı görünür (email enumeration önleme)."""

    message: str = "E-posta kayıtlıysa sıfırlama bağlantısı gönderildi"
    email_sent: bool = False
    # Yalnızca DEBUG / SMTP yokken — üretimde null
    dev_reset_token: str | None = None
    reset_url: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)
    new_password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    """Register/login başarı yanıtı — Flutter AuthResponseModel ile eşleşir."""

    access_token: str
    refresh_token: str
    user: UserRead


class TokenRefreshResponse(BaseModel):
    """Refresh başarı yanıtı — Flutter TokenRefreshModel ile eşleşir."""

    access_token: str
    refresh_token: str
