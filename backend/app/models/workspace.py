import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database.base import Base


class StudyWorkspace(Base):
    """
    Represents a digital workspace. This can be a blank canvas or bound to an existing PDF/StudyResource.
    """
    __tablename__ = "study_workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Metadata
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # PDF linkage (optional)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("study_resources.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # LOS linkage (optional)
    subject_code = Column(String, nullable=True, index=True)
    topic_code = Column(String, nullable=True, index=True)
    
    # Storage flags
    is_deleted = Column(Boolean, default=False, nullable=False)


class AnnotationLayer(Base):
    """
    Holds drawing, text, shape and EAE references on top of the workspace.
    PDFs are NEVER modified, everything here is just coordinates/overlays.
    """
    __tablename__ = "annotation_layers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("study_workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    
    page_index = Column(String, nullable=False, default="0") # '0' for blank canvas, or 'page_1', etc. for PDF

    # The actual stroke/shape data in JSON. 
    # Example: {"strokes": [...], "texts": [...], "eae_refs": [{"asset_id": "...", "x": 10, "y": 20, "scale": 1.5}]}
    objects_data = Column(JSONB, nullable=False, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
