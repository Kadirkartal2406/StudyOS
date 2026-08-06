"""
StudyOS Educational Asset Engine (EAE) — QIE Grounding Prompt Builder
Enriches Question Authoring prompts with interactive EAE visual asset taxonomy.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.asset_context_engine import AssetContextEngine


class EAEGroundingPromptBuilder:
    def __init__(self, db: AsyncSession) -> None:
        self.context_engine = AssetContextEngine(db)

    async def inject_visual_asset_context(
        self, base_system_prompt: str, asset_uri: str
    ) -> tuple[str, list[str]]:
        """
        Retrieves asset grounding schema and appends visual node grounding instructions to prompt.
        Returns (enriched_prompt, available_node_ids).
        """
        grounding_dto = await self.context_engine.build_grounding_dto(asset_uri)
        context_str = self.context_engine.build_prompt_context_string(grounding_dto)

        enriched_prompt = f"{base_system_prompt}\n\n{context_str}"
        return enriched_prompt, grounding_dto.available_node_ids
