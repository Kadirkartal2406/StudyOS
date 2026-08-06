"""
StudyOS Educational Asset Engine (EAE) — SQLAlchemy Models
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    LargeBinary,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EducationalAsset(Base):
    __tablename__ = "educational_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )  # studyos://assets/<domain>/<name>/v<major>
    version: Mapped[str] = mapped_column(String(50), nullable=False)  # SemVer e.g. 1.2.0
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(50), nullable=False, default="svg")
    title: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)
    viewport: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    license_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="studyos_core"
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    is_deprecated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Compiler bundle fields (Sprint 2 prep)
    bundle_hash_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bundle_size_bytes: Mapped[int | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_educational_assets_tags_gin", "tags", postgresql_using="gin"),
    )

    # Relationships
    nodes: Mapped[list[EducationalAssetNode]] = relationship(
        "EducationalAssetNode",
        back_populates="asset",
        cascade="all, delete-orphan",
    )
    versions: Mapped[list[EducationalAssetVersion]] = relationship(
        "EducationalAssetVersion",
        back_populates="asset",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_educational_assets_domain_deprecated", "domain", "is_deprecated"),
        Index("idx_educational_assets_tags_gin", "tags", postgresql_using="gin"),
    )


class EducationalAssetNode(Base):
    __tablename__ = "educational_asset_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_db_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("educational_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )  # <asset>::<type>::<name>
    name: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)
    bounding_box: Mapped[list[float]] = mapped_column(JSONB, nullable=False)
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    asset: Mapped[EducationalAsset] = relationship(
        "EducationalAsset", back_populates="nodes"
    )

    __table_args__ = (
        Index("idx_asset_nodes_asset_node_id", "asset_db_id", "node_id", unique=True),
    )


class EducationalAssetVersion(Base):
    __tablename__ = "educational_asset_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    asset_db_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("educational_assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    change_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bundle_payload: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    asset: Mapped[EducationalAsset] = relationship(
        "EducationalAsset", back_populates="versions"
    )

    __table_args__ = (
        Index("idx_asset_versions_asset_ver", "asset_db_id", "version", unique=True),
    )
