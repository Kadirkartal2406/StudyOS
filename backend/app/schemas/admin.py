"""Admin panel schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole, UserStatus


class AdminUserListItem(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: str
    status: str
    is_verified: bool
    created_at: datetime | None = None
    last_login_at: datetime | None = None
    study_plans: int = 0
    study_sessions: int = 0
    question_records: int = 0


class AdminUserUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    role: UserRole | None = None
    status: UserStatus | None = None
    is_verified: bool | None = None
    new_password: str | None = Field(default=None, min_length=8, max_length=128)


class AdminOverview(BaseModel):
    users_total: int
    users_active: int
    users_admin: int
    study_plans: int
    study_sessions: int
    question_records: int
    generated_questions: int
    pool_cards: int
    exams: int
    goals: int
    conversations: int
    beta_feedback: int


class AdminQuestionItem(BaseModel):
    id: uuid.UUID
    source: str  # pool | generated | record
    exam: str | None = None
    subject: str | None = None
    topic: str | None = None
    stem: str
    difficulty: str | None = None
    user_id: uuid.UUID | None = None
    created_at: datetime | None = None
    extra: dict | None = None
