import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.workspace import StudyWorkspace, AnnotationLayer
from app.models.topic_evidence import TopicEvidence, EvidenceCategory, EvidenceHorizon, EvidenceSourceType
from app.schemas.workspace import (
    WorkspaceCreate, WorkspaceUpdate, AnnotationLayerCreate, AnnotationLayerUpdate
)
from app.services.evidence_engine import EvidenceEngine


class WorkspaceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.evidence_engine = EvidenceEngine(db)

    async def get_user_workspaces(self, user_id: uuid.UUID) -> List[StudyWorkspace]:
        stmt = select(StudyWorkspace).where(
            StudyWorkspace.user_id == user_id, 
            StudyWorkspace.is_deleted == False
        ).order_by(StudyWorkspace.updated_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_workspace(self, user_id: uuid.UUID, dto: WorkspaceCreate) -> StudyWorkspace:
        ws = StudyWorkspace(
            user_id=user_id,
            title=dto.title,
            resource_id=dto.resource_id,
            subject_code=dto.subject_code,
            topic_code=dto.topic_code,
        )
        self.db.add(ws)
        await self.db.flush()

        if dto.subject_code and dto.topic_code:
            await self._log_evidence(user_id, dto.subject_code, dto.topic_code, "workspace_created")
            
        return ws

    async def update_workspace(self, workspace_id: uuid.UUID, user_id: uuid.UUID, dto: WorkspaceUpdate) -> StudyWorkspace:
        ws = await self._get_workspace_or_404(workspace_id, user_id)
        if dto.title is not None:
            ws.title = dto.title
        if dto.is_deleted is not None:
            ws.is_deleted = dto.is_deleted
        await self.db.flush()
        return ws

    async def get_annotation_layers(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> List[AnnotationLayer]:
        # Validate ownership
        await self._get_workspace_or_404(workspace_id, user_id)
        
        stmt = select(AnnotationLayer).where(AnnotationLayer.workspace_id == workspace_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def upsert_annotation_layer(self, workspace_id: uuid.UUID, user_id: uuid.UUID, dto: AnnotationLayerCreate) -> AnnotationLayer:
        ws = await self._get_workspace_or_404(workspace_id, user_id)
        
        stmt = select(AnnotationLayer).where(
            AnnotationLayer.workspace_id == workspace_id,
            AnnotationLayer.page_index == dto.page_index
        )
        result = await self.db.execute(stmt)
        layer = result.scalars().first()
        
        if layer:
            layer.objects_data = dto.objects_data
        else:
            layer = AnnotationLayer(
                workspace_id=workspace_id,
                page_index=dto.page_index,
                objects_data=dto.objects_data
            )
            self.db.add(layer)

        await self.db.flush()
        
        if ws.subject_code and ws.topic_code:
            await self._log_evidence(user_id, ws.subject_code, ws.topic_code, "annotation_added")

        return layer

    async def _get_workspace_or_404(self, workspace_id: uuid.UUID, user_id: uuid.UUID) -> StudyWorkspace:
        stmt = select(StudyWorkspace).where(
            StudyWorkspace.id == workspace_id,
            StudyWorkspace.user_id == user_id,
            StudyWorkspace.is_deleted == False
        )
        result = await self.db.execute(stmt)
        ws = result.scalars().first()
        if not ws:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        return ws

    async def _log_evidence(self, user_id: uuid.UUID, subject_code: str, topic_code: str, action: str):
        # A simple evidence logging logic
        await self.evidence_engine.register_observation(
            user_id=user_id,
            subject_code=subject_code,
            topic_code=topic_code,
            category=EvidenceCategory.EFFORT,
            horizon=EvidenceHorizon.SHORT,
            source=EvidenceSourceType.WORKSPACE_INTERACTION,
            quality_weight=0.5,
            metadata={"action": action}
        )
