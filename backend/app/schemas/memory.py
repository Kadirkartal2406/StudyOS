"""
StudyOS — Memory Pydantic Şemaları
Sprint-2.3 (Meeting-021)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.memory import MemoryCategory, MemorySource


class MemoryCreate(BaseModel):
    category: MemoryCategory
    content: str = Field(min_length=1, max_length=2000)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    source: MemorySource = MemorySource.MANUAL
    metadata: dict | None = None


class MemoryUpdate(BaseModel):
    category: MemoryCategory | None = None
    content: str | None = Field(default=None, min_length=1, max_length=2000)
    importance: float | None = Field(default=None, ge=0.0, le=1.0)
    is_active: bool | None = None
    metadata: dict | None = None


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    category: MemoryCategory
    importance: float
    content: str
    source: MemorySource
    last_accessed_at: datetime | None
    access_count: int
    is_active: bool
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class MemoryListResponse(BaseModel):
    items: list[MemoryRead]


class MemorySearchRequest(BaseModel):
    q: str | None = Field(default=None, max_length=200)
    category: MemoryCategory | None = None
    limit: int = Field(default=20, ge=1, le=100)


class MemorySettingsRead(BaseModel):
    ai_memory_enabled: bool = True


class MemorySettingsUpdate(BaseModel):
    ai_memory_enabled: bool


class MemoryExportResponse(BaseModel):
    exported_at: datetime
    count: int
    items: list[MemoryRead]
