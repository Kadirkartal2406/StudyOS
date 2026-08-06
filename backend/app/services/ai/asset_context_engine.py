"""Sprint A — EAE Asset Context Engine (AI Layer)."""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.educational_asset import EducationalAsset


class AssetContextEngine:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_asset_context(self, asset_id: str) -> dict | None:
        """Verilen asset_id'ye ait görsel metadatasını (node'ları) çeker ve LLM için bağlam oluşturur."""
        stmt = (
            select(EducationalAsset)
            .options(selectinload(EducationalAsset.nodes))
            .where(EducationalAsset.asset_id == asset_id)
        )
        result = await self.db.execute(stmt)
        asset = result.scalar_one_or_none()

        if not asset:
            return None

        # Build context JSON
        context = {
            "asset_id": asset.asset_id,
            "title": asset.title,
            "viewport": asset.viewport,
            "format": asset.format,
            "nodes": [],
        }

        for node in asset.nodes:
            context["nodes"].append(
                {
                    "node_id": node.node_id,
                    "name": node.name,
                    "bounding_box": node.bounding_box,
                    "attributes": node.attributes,
                }
            )

        return context

    def inject_to_prompt(self, base_prompt: str, context: dict) -> str:
        """Asset bağlamını (JSON) sistem prompt'una enjekte eder."""
        asset_json = json.dumps(context, ensure_ascii=False, indent=2)
        injection = (
            "\n\n--- EDUCATIONAL ASSET CONTEXT ---\n"
            "You are provided with an interactive visual asset.\n"
            "You MUST use the 'correct_node_id' to point to one of the nodes provided below when generating questions.\n"
            f"Asset Data:\n{asset_json}\n"
            "--- END ASSET CONTEXT ---\n"
        )
        return base_prompt + injection
