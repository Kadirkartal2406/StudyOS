"""
StudyOS — AI Chat / Settings / Stream stub
Sprint-2.2 + 2.4
"""

import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.database.base import get_db
from app.models.user import User
from app.schemas.ai_chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationListResponse,
)
from app.schemas.ai_settings import AiSettingsRead, AiSettingsUpdate
from app.schemas.common import SuccessResponse
from app.services.ai_settings_service import AiSettingsService
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=SuccessResponse[ChatResponse])
async def post_chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ChatResponse]:
    data = await ChatService(db).chat(
        current_user,
        message=body.message,
        conversation_id=body.conversation_id,
        topic_code=getattr(body, 'topic_code', None),
        subject_code=getattr(body, 'subject_code', None),
    )
    return SuccessResponse(data=data)


@router.post("/chat/stream")
async def post_chat_stream_stub(
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    """D1 — SSE altyapı rezervi; gerçek streaming sonraki sprint."""
    _ = current_user
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "success": False,
            "error": {
                "code": "STREAMING_NOT_IMPLEMENTED",
                "message": "SSE streaming henüz aktif değil; POST /ai/chat kullanın.",
            },
        },
    )


@router.get("/settings", response_model=SuccessResponse[AiSettingsRead])
async def get_ai_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiSettingsRead]:
    data = await AiSettingsService(db).get_settings(current_user.id)
    return SuccessResponse(data=data)


@router.patch("/settings", response_model=SuccessResponse[AiSettingsRead])
async def patch_ai_settings(
    body: AiSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[AiSettingsRead]:
    data = await AiSettingsService(db).update_settings(current_user.id, body)
    return SuccessResponse(data=data, message="AI ayarları güncellendi")


@router.get("/conversations", response_model=SuccessResponse[ConversationListResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ConversationListResponse]:
    data = await ChatService(db).list_conversations(current_user.id)
    return SuccessResponse(data=data)


@router.get(
    "/conversations/{conversation_id}",
    response_model=SuccessResponse[ConversationDetail],
)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[ConversationDetail]:
    data = await ChatService(db).get_conversation(conversation_id, current_user.id)
    return SuccessResponse(data=data)


@router.delete(
    "/conversations/{conversation_id}",
    response_model=SuccessResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse[dict]:
    await ChatService(db).delete_conversation(conversation_id, current_user.id)
    return SuccessResponse(data={}, message="Sohbet silindi")
