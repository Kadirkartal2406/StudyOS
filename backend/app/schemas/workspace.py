from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class AnnotationLayerBase(BaseModel):
    page_index: str = Field(..., description="Page index (e.g., '0' for blank canvas, 'page_1' for PDF)")
    objects_data: Dict[str, Any] = Field(default_factory=dict, description="JSON representing strokes, text, shapes, and EAE references")

class AnnotationLayerCreate(AnnotationLayerBase):
    pass

class AnnotationLayerUpdate(BaseModel):
    objects_data: Dict[str, Any]

class AnnotationLayerRead(AnnotationLayerBase):
    id: UUID
    workspace_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkspaceBase(BaseModel):
    title: str = Field(..., description="Title of the workspace")
    resource_id: Optional[UUID] = None
    subject_code: Optional[str] = None
    topic_code: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    title: Optional[str] = None
    is_deleted: Optional[bool] = None

class WorkspaceRead(WorkspaceBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True
