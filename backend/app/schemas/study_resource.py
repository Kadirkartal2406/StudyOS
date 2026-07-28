"""
StudyOS — StudyResource Pydantic Şemaları
Sprint-2.5 (Meeting-023)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.study_resource import ResourceStatus, ResourceType


class StudyResourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=4000)
    resource_type: ResourceType = ResourceType.OTHER
    url: str | None = Field(default=None, max_length=2000)
    thumbnail_url: str | None = Field(default=None, max_length=2000)
    provider: str | None = Field(default=None, max_length=100)
    duration_seconds: int | None = Field(default=None, ge=0, le=86400 * 7)
    author: str | None = Field(default=None, max_length=200)
    study_plan_id: UUID | None = None
    subject_code: str | None = Field(default=None, max_length=100)
    topic_code: str | None = Field(default=None, max_length=200)
    status: ResourceStatus = ResourceStatus.NOT_STARTED
    order_index: int = Field(default=0, ge=0)
    metadata: dict | None = None


class StudyResourceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=4000)
    resource_type: ResourceType | None = None
    url: str | None = Field(default=None, max_length=2000)
    thumbnail_url: str | None = Field(default=None, max_length=2000)
    provider: str | None = Field(default=None, max_length=100)
    duration_seconds: int | None = Field(default=None, ge=0, le=86400 * 7)
    author: str | None = Field(default=None, max_length=200)
    study_plan_id: UUID | None = None
    subject_code: str | None = Field(default=None, max_length=100)
    topic_code: str | None = Field(default=None, max_length=200)
    status: ResourceStatus | None = None
    order_index: int | None = Field(default=None, ge=0)
    metadata: dict | None = None


class StudyResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    study_plan_id: UUID | None
    subject_code: str | None = None
    topic_code: str | None = None
    title: str
    description: str | None
    resource_type: ResourceType
    url: str | None
    thumbnail_url: str | None
    provider: str | None
    duration_seconds: int | None
    author: str | None
    status: ResourceStatus
    order_index: int
    last_opened_at: datetime | None
    completed_at: datetime | None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class StudyResourceListResponse(BaseModel):
    items: list[StudyResourceRead]


class ResourceStatistics(BaseModel):
    total_count: int = 0
    completed_count: int = 0
    in_progress_count: int = 0
    today_completed_count: int = 0
    today_opened_count: int = 0
    total_video_duration_seconds: int = 0
    completed_video_duration_seconds: int = 0
    by_type: dict[str, int] = Field(default_factory=dict)


class DashboardResourceSummary(BaseModel):
    today_opened_count: int = 0
    today_completed_count: int = 0
    recent_items: list[StudyResourceRead] = Field(default_factory=list)
