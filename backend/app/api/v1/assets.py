"""
StudyOS Educational Asset Engine (EAE) — API Endpoints
"""

from __future__ import annotations

import json
import uuid
import zlib

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_system_admin
from app.core.exceptions import NotFoundError, ValidationError
from app.database.base import get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse, PaginationMeta, SuccessResponse
from app.schemas.educational_asset import (
    AssetCreateRequestDTO,
    AssetDetailDTO,
    AssetListItemDTO,
    AssetNodeUpdateRequestDTO,
    AssetSearchQueryDTO,
    build_asset_detail_dto,
)
from app.services.asset_compiler.packager import BundlePackager
from app.services.asset_delta_service import AssetDeltaService
from app.services.asset_registry_service import AssetRegistryService
from app.services.asset_search_service import AssetSearchService
from app.services.asset_tenant_service import AssetTenantService
from app.services.asset_version_service import AssetVersionService

router = APIRouter()


def _latest_bundle_manifest(asset) -> dict | None:
    versions = sorted(
        list(asset.versions or []),
        key=lambda v: v.created_at or asset.created_at,
        reverse=True,
    )
    for ver in versions:
        if ver.bundle_payload:
            try:
                unpacked = BundlePackager().unpack(ver.bundle_payload)
                return unpacked.get("manifest")
            except Exception:
                continue
    return None


def _latest_bundle_bytes(asset) -> bytes | None:
    versions = sorted(
        list(asset.versions or []),
        key=lambda v: v.created_at or asset.created_at,
        reverse=True,
    )
    for ver in versions:
        if ver.bundle_payload:
            return ver.bundle_payload
    return None


async def _resolve_asset(db: AsyncSession, asset_key: str):
    """Resolve by DB UUID or logical asset URI (studyos://assets/...)."""
    svc = AssetRegistryService(db)
    key = (asset_key or "").strip()
    try:
        return await svc.get_asset_by_id(uuid.UUID(key))
    except ValueError:
        return await svc.get_asset_by_uri(key)


@router.get(
    "/search",
    response_model=PaginatedResponse[AssetListItemDTO],
    summary="Search educational assets",
)
async def search_assets(
    q: str | None = Query(default=None, description="Search query string"),
    domain: str | None = Query(default=None, description="Domain namespace filter"),
    tag: str | None = Query(default=None, description="Tag filter"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[AssetListItemDTO]:
    query_dto = AssetSearchQueryDTO(
        q=q, domain=domain, tag=tag, page=page, page_size=page_size
    )
    items, total = await AssetSearchService(db).search(query_dto)
    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total,
        total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )
    return PaginatedResponse(
        data=[AssetListItemDTO.model_validate(item) for item in items],
        pagination=meta,
    )


@router.post(
    "/compile",
    response_model=SuccessResponse[AssetDetailDTO],
    status_code=status.HTTP_201_CREATED,
    summary="Compile SVG+manifest and register asset (Admin)",
)
async def compile_and_register_asset(
    svg_file: UploadFile = File(...),
    manifest_json: str = Form(..., description="EAE manifest JSON string"),
    change_log: str | None = Form(default=None),
    is_breaking: bool = Form(default=False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AssetDetailDTO]:
    try:
        raw_manifest = json.loads(manifest_json)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid manifest JSON: {exc}") from exc

    raw_svg = (await svg_file.read()).decode("utf-8", errors="replace")
    asset, _bundle = await AssetRegistryService(db).compile_and_register_asset(
        raw_svg=raw_svg,
        raw_manifest=raw_manifest,
        change_log=change_log,
        is_breaking=is_breaking,
    )
    await db.commit()
    detail = build_asset_detail_dto(asset, svg_manifest=raw_manifest)
    return SuccessResponse(data=detail, message="Asset compiled and registered")


@router.get(
    "/{asset_key:path}",
    response_model=SuccessResponse[AssetDetailDTO],
    summary="Get detailed asset manifest and nodes (UUID or asset URI)",
)
async def get_asset_detail(
    asset_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SuccessResponse[AssetDetailDTO]:
    asset = await _resolve_asset(db, asset_key)
    AssetTenantService().enforce_tenant_access(asset, current_user)
    return SuccessResponse(
        data=build_asset_detail_dto(asset, svg_manifest=_latest_bundle_manifest(asset))
    )


@router.get(
    "/{asset_key:path}/bundle",
    summary="Download compiled zlib EAE bundle for mobile sync (UUID or asset URI)",
)
async def download_asset_bundle(
    asset_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    asset = await _resolve_asset(db, asset_key)
    AssetTenantService().enforce_tenant_access(asset, current_user)
    payload = _latest_bundle_bytes(asset)
    if not payload:
        raise NotFoundError("Asset bundle", asset_key)
    return Response(
        content=payload,
        media_type="application/octet-stream",
        headers={
            "X-EAE-Asset-Id": asset.asset_id,
            "X-EAE-Version": asset.version,
            "X-EAE-Hash": asset.bundle_hash_sha256 or "",
        },
    )


@router.patch(
    "/{asset_key:path}/nodes/{node_id}",
    response_model=SuccessResponse[AssetDetailDTO],
    summary="Update node metadata (Admin)",
)
async def patch_asset_node(
    asset_key: str,
    node_id: str,
    body: AssetNodeUpdateRequestDTO,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AssetDetailDTO]:
    asset = await _resolve_asset(db, asset_key)
    target = next((n for n in asset.nodes if n.node_id == node_id), None)
    if target is None:
        raise NotFoundError("Asset node", node_id)
    if body.name is not None:
        target.name = body.name
    if body.attributes is not None:
        target.attributes = body.attributes
    if body.bounding_box is not None:
        target.bounding_box = body.bounding_box
    await db.commit()
    await db.refresh(asset)
    return SuccessResponse(
        data=build_asset_detail_dto(asset, svg_manifest=_latest_bundle_manifest(asset)),
        message="Node metadata updated",
    )


@router.get(
    "/{asset_key}/delta",
    summary="Download binary delta patch between versions for mobile sync",
)
async def get_asset_delta(
    asset_key: str,
    from_version: str = Query(..., description="Current client SemVer version e.g. 1.0.0"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    asset = await _resolve_asset(db, asset_key)
    AssetTenantService().enforce_tenant_access(asset, current_user)

    new_bundle_meta: dict = {
        "manifest": {
            "asset_id": asset.asset_id,
            "version": asset.version,
            "domain": asset.domain,
            "format": asset.format,
            "title": asset.title,
            "tags": asset.tags,
            "bundle_hash_sha256": asset.bundle_hash_sha256,
            "bundle_size_bytes": asset.bundle_size_bytes,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "name": n.name,
                    "bounding_box": n.bounding_box,
                }
                for n in asset.nodes
            ],
        },
        "svg_content": None,
        "spatial_tree": None,
    }
    old_bundle_meta: dict = {
        "manifest": {"version": from_version},
        "svg_content": None,
        "spatial_tree": None,
    }

    old_version_entry = next((v for v in asset.versions if v.version == from_version), None)
    new_version_entry = next((v for v in asset.versions if v.version == asset.version), None)

    if old_version_entry and old_version_entry.bundle_payload:
        old_payload = old_version_entry.bundle_payload
    else:
        old_payload = zlib.compress(json.dumps(old_bundle_meta, ensure_ascii=False).encode())

    if new_version_entry and new_version_entry.bundle_payload:
        new_payload = new_version_entry.bundle_payload
    else:
        new_payload = zlib.compress(json.dumps(new_bundle_meta, ensure_ascii=False).encode())
    delta_patch = AssetDeltaService().compute_delta(
        from_version=from_version,
        to_version=asset.version,
        old_bundle_payload=old_payload,
        new_bundle_payload=new_payload,
    )
    return Response(
        content=delta_patch.patch_bytes,
        media_type="application/octet-stream",
        headers={
            "X-EAE-From-Version": from_version,
            "X-EAE-To-Version": asset.version,
            "X-EAE-Patch-Size": str(delta_patch.patch_size_bytes),
        },
    )


@router.post(
    "/register",
    response_model=SuccessResponse[AssetDetailDTO],
    summary="Register or upgrade an asset manifest (Admin only)",
)
async def register_asset_manifest(
    body: AssetCreateRequestDTO,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AssetDetailDTO]:
    asset = await AssetRegistryService(db).register_asset_manifest(
        raw_manifest=body.manifest,
        change_log=body.change_log,
        is_breaking=body.is_breaking,
    )
    return SuccessResponse(
        data=build_asset_detail_dto(asset, svg_manifest=body.manifest),
        message="Asset manifest registered successfully",
    )


@router.post(
    "/{asset_key}/deprecate",
    response_model=SuccessResponse[AssetDetailDTO],
    summary="Mark an asset version as deprecated (Admin only)",
)
async def deprecate_asset(
    asset_key: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_system_admin),
) -> SuccessResponse[AssetDetailDTO]:
    asset = await _resolve_asset(db, asset_key)
    deprecated = await AssetVersionService(db).deprecate_asset(asset.asset_id)
    return SuccessResponse(
        data=build_asset_detail_dto(deprecated),
        message="Asset version marked as deprecated",
    )
