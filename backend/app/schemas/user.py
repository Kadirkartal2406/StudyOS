"""
StudyOS — User Pydantic Şemaları
"""

import uuid

from pydantic import BaseModel, ConfigDict

from app.models.user import User, UserRole, UserStatus


class UserRead(BaseModel):
    """API yanıtlarında dönen kullanıcı bilgisi (hassas alanlar hariç)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    is_email_verified: bool

    @classmethod
    def from_user(cls, user: User) -> "UserRead":
        """SQLAlchemy User modelinden UserRead üretir; status → is_active dönüşümü yapar."""
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=UserRole(user.role),
            is_active=user.status == UserStatus.ACTIVE,
            is_email_verified=user.is_verified,
        )
