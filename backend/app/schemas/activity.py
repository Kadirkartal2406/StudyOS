"""
StudyOS — Activity Pydantic Şemaları
Bkz. docs/architecture/api-design.md §2.16 / §2.17 (Sprint-1.7)
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class ActivityRead(BaseModel):
    """Tek aktivite kaydı — Dashboard ve ileride timeline/bildirimler."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    title: str
    description: str | None = None
    study_session_id: uuid.UUID | None = None
    study_plan_id: uuid.UUID | None = None
    metadata: dict[str, Any] | None = None
    occurred_at: datetime
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _map_orm_metadata(cls, data: Any) -> Any:
        # ORM alanı `metadata_` (SQLAlchemy reserved `metadata` çakışması).
        if hasattr(data, "metadata_"):
            return {
                "id": data.id,
                "user_id": data.user_id,
                "event_type": data.event_type,
                "title": data.title,
                "description": data.description,
                "study_session_id": data.study_session_id,
                "study_plan_id": data.study_plan_id,
                "metadata": data.metadata_,
                "occurred_at": data.occurred_at,
                "created_at": data.created_at,
            }
        return data
