"""
StudyOS Educational Asset Engine (EAE) — Asset Search Service
"""

from __future__ import annotations

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.educational_asset import EducationalAsset
from app.repositories.educational_asset_repository import EducationalAssetRepository
from app.schemas.educational_asset import AssetSearchQueryDTO


class AssetSearchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EducationalAssetRepository(db)

    async def search(
        self, query: AssetSearchQueryDTO
    ) -> tuple[Sequence[EducationalAsset], int]:
        """
        Executes multi-dimensional search over Educational Assets database.
        Supports text query, domain namespace, tag filters, and tenant isolation.
        """
        return await self.repo.search_assets(query)
