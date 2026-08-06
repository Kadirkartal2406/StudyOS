"""
StudyOS Educational Asset Engine (EAE) — Asset Context Engine
Extracts model-agnostik LLM grounding prompts and taxonomy context from Educational Assets.
"""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.asset_contracts.schemas import AssetGroundingSchemaDTO
from app.models.educational_asset import EducationalAsset
from app.services.asset_registry_service import AssetRegistryService


class AssetContextEngine:
    """
    Constructs provider-agnostik AI grounding context for Question Generation, Virtual Student, and Coach.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.registry_service = AssetRegistryService(db)

    async def build_grounding_dto(self, asset_id: str) -> AssetGroundingSchemaDTO:
        asset = await self.registry_service.get_asset_by_uri(asset_id)
        return self.build_grounding_dto_from_asset(asset)

    def build_grounding_dto_from_asset(
        self, asset: EducationalAsset
    ) -> AssetGroundingSchemaDTO:
        available_node_ids = [node.node_id for node in asset.nodes]

        taxonomy_summary = []
        for node in asset.nodes:
            taxonomy_summary.append(
                {
                    "node_id": node.node_id,
                    "name": node.name,
                    "bounding_box": node.bounding_box,
                    "attributes": node.attributes,
                }
            )

        return AssetGroundingSchemaDTO(
            asset_id=asset.asset_id,
            version=asset.version,
            domain=asset.domain,
            available_node_ids=available_node_ids,
            taxonomy_summary=taxonomy_summary,
        )

    def build_prompt_context_string(
        self, grounding_dto: AssetGroundingSchemaDTO, lang: str = "tr"
    ) -> str:
        """
        Formats grounding schema into a structured markdown prompt snippet for LLMs.
        """
        lines = [
            "### EDUCATIONAL ASSET VISUAL GROUNDING CONTEXT",
            f"- **Asset URI**: `{grounding_dto.asset_id}`",
            f"- **Asset Domain**: `{grounding_dto.domain}` (v{grounding_dto.version})",
            "- **Available Interactive Node IDs** (MUST use exact Node ID strings for option targets/explanations):",
        ]

        for item in grounding_dto.taxonomy_summary:
            n_id = item["node_id"]
            name_dict = item.get("name", {})
            label = name_dict.get(lang) or name_dict.get("tr") or name_dict.get("en") or n_id
            lines.append(f"  * Node ID: `{n_id}` -> Label: \"{label}\"")

        lines.append(
            "\nIMPORTANT RULE FOR AI GENERATION: Any visual question option, distractor, or explanation targeting a diagram element MUST strictly reference one of the valid Node IDs above."
        )

        return "\n".join(lines)
