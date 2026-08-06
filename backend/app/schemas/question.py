"""Sprint A — QIE EAE Interactive Question Schemas."""

from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field


class AssetInteractiveQuestionDTO(BaseModel):
    """QIE'den (M34) dönen veya Pool'dan çekilen EAE destekli soru modeli."""

    id: uuid.UUID
    exam: str
    subject_code: str
    topic_code: str
    difficulty_band: str

    stem: str
    choices: dict[str, Any]
    correct_key: str
    explanation: str | None = None

    # EAE Entegrasyon Alanları
    target_asset_id: uuid.UUID | None = None
    correct_node_id: str | None = None

    qie_card: dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}
