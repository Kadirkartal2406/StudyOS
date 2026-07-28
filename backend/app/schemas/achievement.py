"""
StudyOS — Achievement schemas
Sprint-2.9 (Meeting-027)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AchievementRead(BaseModel):
    id: UUID
    code: str
    title: str
    description: str
    category: str
    tier: str
    points: int
    icon_key: str
    criteria: dict = Field(default_factory=dict)
    is_active: bool = True
    sort_order: int = 0

    model_config = {"from_attributes": True}


class UserAchievementRead(BaseModel):
    id: UUID
    achievement_id: UUID
    reason: str
    source_event: str | None = None
    unlocked_at: datetime
    achievement: AchievementRead | None = None

    model_config = {"from_attributes": True}


class AchievementProgressRead(BaseModel):
    achievement_id: UUID
    current_value: float
    target_value: float
    unlocked: bool = False
    achievement: AchievementRead | None = None


class AchievementCheckRequest(BaseModel):
    event: str | None = None
    context: dict = Field(default_factory=dict)


class AchievementCheckResponse(BaseModel):
    newly_unlocked: list[UserAchievementRead] = Field(default_factory=list)
    evaluated: int = 0


class AchievementExplainResponse(BaseModel):
    achievement_id: UUID
    explanation: str
    provider: str
    used_fallback: bool = False
    reason: str
    code: str
    title: str


class DashboardAchievementSummary(BaseModel):
    total_unlocked: int = 0
    total_points: int = 0
    recent_title: str | None = None
    recent_reason: str | None = None
    recent_unlocked_at: datetime | None = None
