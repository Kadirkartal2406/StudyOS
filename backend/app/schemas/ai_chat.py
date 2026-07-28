"""
StudyOS — AI Chat Şemaları
Sprint-2.2 (Meeting-020)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.conversation import MessageRole


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None
    topic_code: str | None = None
    subject_code: str | None = None


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime


class ConversationSummary(BaseModel):
    id: UUID
    title: str
    topic_code: str | None = None
    subject_code: str | None = None
    context_version: str
    system_prompt_version: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetail(BaseModel):
    id: UUID
    title: str
    topic_code: str | None = None
    subject_code: str | None = None
    context_version: str
    system_prompt_version: str
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    messages: list[MessageRead] = Field(default_factory=list)


class PlanProposalCard(BaseModel):
    """Chat'ten gelen, kullanıcı onayı bekleyen plan önerisi."""

    draft_id: UUID
    reason: str = ""
    status: str = "pending"
    summary: str | None = None


class ChatResponse(BaseModel):
    conversation: ConversationSummary
    user_message: MessageRead
    assistant_message: MessageRead
    plan_proposal: PlanProposalCard | None = None


class ConversationListResponse(BaseModel):
    items: list[ConversationSummary]
