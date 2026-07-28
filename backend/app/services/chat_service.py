"""
StudyOS — AI Chat Service
Sprint-2.2 / 2.4 — gerçek LLM + fallback + standart context.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    AI_CHAT_TITLE_MAX_LEN,
    AI_CONTEXT_VERSION,
    AI_SYSTEM_PROMPT_VERSION,
)
from app.core.exceptions import NotFoundError, ValidationError
from app.models.conversation import Conversation, Message, MessageRole
from app.models.user import User
from app.providers.ai.base import GenerateRequest, generate_with_fallback
from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.schemas.ai_chat import (
    ChatResponse,
    ConversationDetail,
    ConversationListResponse,
    ConversationSummary,
    MessageRead,
    PlanProposalCard,
)
from app.services.ai.context_builder import ContextBuilder
from app.services.ai.memory_writer import MemoryWriter
from app.services.ai.prompt_builder import PromptBuilder
from app.services.memory_service import MemoryService
from app.services.notification_settings_service import NotificationSettingsService


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)
        self.context_builder = ContextBuilder(db)
        self.prompt_builder = PromptBuilder()
        self.memory_service = MemoryService(db)
        self.memory_writer = MemoryWriter(db)
        self.notif = NotificationSettingsService(db)

    def _message_read(self, msg: Message) -> MessageRead:
        return MessageRead(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            metadata=dict(msg.metadata_ or {}),
            created_at=msg.created_at,
        )

    async def _summary(self, conv: Conversation) -> ConversationSummary:
        count = await self.conversations.message_count(conv.id)
        return ConversationSummary(
            id=conv.id,
            title=conv.title,
            context_version=conv.context_version,
            system_prompt_version=conv.system_prompt_version,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=count,
        )

    async def list_conversations(self, user_id: uuid.UUID) -> ConversationListResponse:
        items = await self.conversations.list_for_user(user_id)
        summaries = [await self._summary(c) for c in items]
        return ConversationListResponse(items=summaries)

    async def get_conversation(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> ConversationDetail:
        conv = await self.conversations.get_for_user(
            conversation_id, user_id, with_messages=True
        )
        if conv is None:
            raise NotFoundError("Sohbet", str(conversation_id))
        return ConversationDetail(
            id=conv.id,
            title=conv.title,
            context_version=conv.context_version,
            system_prompt_version=conv.system_prompt_version,
            metadata=dict(conv.metadata_ or {}),
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[self._message_read(m) for m in conv.messages],
        )

    async def delete_conversation(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        conv = await self.conversations.get_for_user(conversation_id, user_id)
        if conv is None:
            raise NotFoundError("Sohbet", str(conversation_id))
        await self.conversations.delete(conv)

    async def chat(
        self,
        user: User,
        *,
        message: str,
        conversation_id: uuid.UUID | None = None,
        topic_code: str | None = None,
        subject_code: str | None = None,
    ) -> ChatResponse:
        text = message.strip()
        if not text:
            raise ValidationError("Mesaj boş olamaz", field="message")

        if conversation_id is None:
            title = text[:AI_CHAT_TITLE_MAX_LEN]
            conv = Conversation(
                user_id=user.id,
                title=title,
                context_version=AI_CONTEXT_VERSION,
                system_prompt_version=AI_SYSTEM_PROMPT_VERSION,
                topic_code=topic_code,
                subject_code=subject_code,
                metadata_={"memory": "rule_based", "rag": None, "summary": None},
                summary=None,
            )
            await self.conversations.add(conv)
            history: list[Message] = []
        else:
            conv = await self.conversations.get_for_user(conversation_id, user.id)
            if conv is None:
                raise NotFoundError("Sohbet", str(conversation_id))
            history = await self.messages.list_for_conversation(conv.id)

        user_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.USER,
            content=text,
            metadata_={},
        )
        await self.messages.add(user_msg)

        # J1: summary alanı context'e rezerv; aktif üretim yok → None geçilir
        context = await self.context_builder.build(
            user, conversation_summary=None
        )

        # Topic context enjeksiyonu (AI Sprint FAZ 5)
        active_topic_code = topic_code or (conv.topic_code if conv else None)
        active_subject_code = subject_code or (conv.subject_code if conv else None)
        if active_topic_code and active_subject_code:
            try:
                from app.services.ai.topic_context_builder import TopicContextBuilder
                topic_ctx = await TopicContextBuilder(self.db).build(
                    user.id, active_subject_code, active_topic_code,
                )
                context["topic"] = topic_ctx.to_prompt_dict()
            except Exception:
                pass
        payload = self.prompt_builder.build(
            context=context,
            history=history,
            user_message=text,
            prompt_version=conv.system_prompt_version,
        )

        pref = await self.notif.get_or_create(user.id)
        result = await generate_with_fallback(
            GenerateRequest(messages=payload.messages, context=context),
            preferred=pref.ai_preferred_provider,
            model=pref.ai_preferred_model,
        )

        display_text, proposal_meta = await self._maybe_create_plan_proposal(
            user.id, conv.id, text, result.text
        )

        assistant_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.ASSISTANT,
            content=display_text,
            metadata_={
                "provider": result.provider,
                "model": result.model,
                "used_fallback": result.used_fallback,
                "context_version": context.get("context_version"),
                **(proposal_meta or {}),
            },
        )
        await self.messages.add(assistant_msg)
        conv.updated_at = datetime.now(UTC)

        if await self.memory_service.is_memory_enabled(user.id):
            await self.memory_writer.extract_from_chat(
                user.id, text, conversation_id=conv.id
            )

        await self.db.flush()

        plan_card = None
        if proposal_meta and proposal_meta.get("plan_proposal"):
            pp = proposal_meta["plan_proposal"]
            plan_card = PlanProposalCard(
                draft_id=pp["draft_id"],
                reason=pp.get("reason") or "",
                status=pp.get("status") or "pending",
                summary=pp.get("summary"),
            )

        return ChatResponse(
            conversation=await self._summary(conv),
            user_message=self._message_read(user_msg),
            assistant_message=self._message_read(assistant_msg),
            plan_proposal=plan_card,
        )

    async def _maybe_create_plan_proposal(
        self,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        user_text: str,
        assistant_text: str,
    ) -> tuple[str, dict | None]:
        """Parse plan_proposal fence or intent → pending PlannerDraft (no apply)."""
        import json
        import re

        from app.models.planner_draft import PlannerDraftStatus
        from app.schemas.planner import PlannerGenerateRequest
        from app.services.planner_service import PlannerService

        reason = ""
        wants = False
        fence = re.search(
            r"```plan_proposal\s*([\s\S]*?)```", assistant_text, re.IGNORECASE
        )
        display = assistant_text
        if fence:
            wants = True
            raw = fence.group(1).strip()
            display = (assistant_text[: fence.start()] + assistant_text[fence.end() :]).strip()
            try:
                data = json.loads(raw)
                reason = str(data.get("reason") or "")
            except Exception:
                reason = raw[:200]
        else:
            low = user_text.casefold()
            if any(
                k in low
                for k in (
                    "planı değiştir",
                    "plani degistir",
                    "plan değiştir",
                    "yeni plan",
                    "plan öner",
                    "plan oner",
                    "çalışma planı",
                    "calisma plani",
                )
            ):
                wants = True
                reason = "Kullanıcı sohbet üzerinden plan değişikliği istedi."

        if not wants:
            return assistant_text, None

        try:
            svc = PlannerService(self.db)
            draft_read = await svc.generate(user_id, PlannerGenerateRequest())
            # Mark as chat proposal awaiting approval
            from app.repositories.planner_draft_repository import PlannerDraftRepository

            draft = await PlannerDraftRepository(self.db).get_for_user(
                draft_read.id, user_id
            )
            if draft:
                draft.status = PlannerDraftStatus.PENDING
                draft.source = "chat"
                draft.conversation_id = conversation_id
                await self.db.flush()
            summary = (draft_read.rationale or {}).get("overview") if draft_read.rationale else None
            if not summary and draft_read.summary:
                weak = draft_read.summary.get("weak_subjects") or []
                summary = "Öncelik: " + ", ".join(weak[:3]) if weak else "Yeni haftalık taslak hazır."
            meta = {
                "plan_proposal": {
                    "draft_id": str(draft_read.id),
                    "reason": reason
                    or "Sohbet üzerinden oluşturulan plan önerisi. Onaylamadan uygulanmaz.",
                    "status": "pending",
                    "summary": summary,
                }
            }
            if "onay" not in display.casefold():
                display = (
                    display
                    + "\n\nPlan önerisi hazır. Uygulamak için onaylaman gerekiyor "
                    "(Uygula / Reddet)."
                ).strip()
            return display, meta
        except Exception:
            return assistant_text, None
