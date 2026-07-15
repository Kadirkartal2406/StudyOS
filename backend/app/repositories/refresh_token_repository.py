"""
StudyOS — RefreshToken Repository
Refresh token rotation için veri erişim işlemleri.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.is_revoked = True
        await self.db.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id, RefreshToken.is_revoked.is_(False)
            )
        )
        for token in result.scalars().all():
            token.is_revoked = True
        await self.db.flush()

    def is_valid(self, token: RefreshToken) -> bool:
        """Token iptal edilmemiş ve süresi dolmamışsa geçerlidir."""
        return not token.is_revoked and token.expires_at > datetime.now(UTC)
