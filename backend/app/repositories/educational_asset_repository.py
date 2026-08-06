"""
StudyOS Educational Asset Engine (EAE) — Asset Repository
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import cast, func, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.educational_asset import (
    EducationalAsset,
    EducationalAssetNode,
    EducationalAssetVersion,
)
from app.schemas.educational_asset import AssetSearchQueryDTO


class EducationalAssetRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, db_id: uuid.UUID) -> EducationalAsset | None:
        stmt = (
            select(EducationalAsset)
            .options(
                selectinload(EducationalAsset.nodes),
                selectinload(EducationalAsset.versions),
            )
            .where(EducationalAsset.id == db_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_asset_id(self, asset_id: str) -> EducationalAsset | None:
        stmt = (
            select(EducationalAsset)
            .options(
                selectinload(EducationalAsset.nodes),
                selectinload(EducationalAsset.versions),
            )
            .where(EducationalAsset.asset_id == asset_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def search_assets(
        self, query: AssetSearchQueryDTO
    ) -> tuple[Sequence[EducationalAsset], int]:
        stmt = select(EducationalAsset)

        if not query.include_deprecated:
            stmt = stmt.where(EducationalAsset.is_deprecated.is_(False))

        if query.domain:
            stmt = stmt.where(EducationalAsset.domain == query.domain.strip().lower())

        if query.tenant_id:
            stmt = stmt.where(EducationalAsset.tenant_id == query.tenant_id)

        if query.tag:
            # Use PostgreSQL JSONB @> (contains) operator to properly leverage GIN index.
            # cast(String).ilike() bypasses the GIN index — this is the correct approach.
            tag_clean = query.tag.strip().lower()
            stmt = stmt.where(
                EducationalAsset.tags.op("@>")(cast([tag_clean], JSONB))
            )

        if query.q:
            q_clean = f"%{query.q.strip().lower()}%"
            # Title search uses ilike (JSONB text scan) and asset_id prefix match.
            # Tags are searched via GIN @> exact match to preserve index usage.
            stmt = stmt.where(
                (EducationalAsset.asset_id.ilike(q_clean))
                | (EducationalAsset.title.op("->>")("tr").ilike(q_clean))
                | (EducationalAsset.title.op("->>")("en").ilike(q_clean))
                | EducationalAsset.tags.op("@>")(cast([query.q.strip().lower()], JSONB))
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int((await self.db.execute(count_stmt)).scalar() or 0)

        # Paginate
        offset = (query.page - 1) * query.page_size
        stmt = (
            stmt.order_by(EducationalAsset.created_at.desc())
            .offset(offset)
            .limit(query.page_size)
        )

        res = await self.db.execute(stmt)
        return res.scalars().all(), total

    async def create_asset(
        self,
        asset: EducationalAsset,
        nodes: list[EducationalAssetNode],
        version_entry: EducationalAssetVersion,
    ) -> EducationalAsset:
        self.db.add(asset)
        await self.db.flush()

        for node in nodes:
            node.asset_db_id = asset.id
            self.db.add(node)

        version_entry.asset_db_id = asset.id
        self.db.add(version_entry)

        await self.db.flush()
        return asset

    async def add_version(
        self,
        asset: EducationalAsset,
        version_entry: EducationalAssetVersion,
        new_nodes: list[EducationalAssetNode] | None = None,
    ) -> EducationalAsset:
        version_entry.asset_db_id = asset.id
        self.db.add(version_entry)

        if new_nodes is not None:
            # Replace nodes with new version nodes
            for existing_node in asset.nodes:
                await self.db.delete(existing_node)
            await self.db.flush()

            for n in new_nodes:
                n.asset_db_id = asset.id
                self.db.add(n)

        await self.db.flush()
        return asset

    async def get_node_by_id(self, node_id: str) -> EducationalAssetNode | None:
        stmt = select(EducationalAssetNode).where(
            EducationalAssetNode.node_id == node_id
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
