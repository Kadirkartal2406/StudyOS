"""
Unit tests for EAE Asset Tenant Isolation and Delta Sync Engine.
"""

import uuid
import pytest

from app.core.exceptions import AuthorizationError
from app.models.educational_asset import EducationalAsset
from app.models.user import User, UserRole
from app.services.asset_compiler.packager import BundlePackager
from app.services.asset_delta_service import AssetDeltaService
from app.services.asset_tenant_service import AssetTenantService


def test_tenant_access_core_asset_public():
    service = AssetTenantService()
    public_asset = EducationalAsset(
        asset_id="studyos://assets/geography/turkey_admin/v1",
        version="1.0.0",
        domain="geography",
        format="svg",
        title={"tr": "Test"},
        viewport={"width": 100, "height": 100},
        tags=[],
        tenant_id=None,
    )
    user = User(id=uuid.uuid4(), role=UserRole.STUDENT)

    # Should not raise exception
    service.enforce_tenant_access(public_asset, user)


def test_tenant_access_restricted_tenant_denied():
    service = AssetTenantService()
    tenant_uuid = uuid.uuid4()
    tenant_asset = EducationalAsset(
        asset_id="studyos://assets/geography/private_map/v1",
        version="1.0.0",
        domain="geography",
        format="svg",
        title={"tr": "Private Map"},
        viewport={"width": 100, "height": 100},
        tags=[],
        tenant_id=tenant_uuid,
    )
    unauthorized_user = User(id=uuid.uuid4(), role=UserRole.STUDENT)

    with pytest.raises(AuthorizationError):
        service.enforce_tenant_access(tenant_asset, unauthorized_user)


def test_delta_sync_compute_and_apply():
    packager = BundlePackager()
    old_bundle = packager.package(
        manifest_dto={"asset_id": "studyos://assets/geography/turkey/v1", "version": "1.0.0"},
        sanitized_svg="<svg v1></svg>",
        spatial_tree={"root": {}},
    )
    new_bundle = packager.package(
        manifest_dto={"asset_id": "studyos://assets/geography/turkey/v1", "version": "1.1.0"},
        sanitized_svg="<svg v1.1></svg>",
        spatial_tree={"root": {}},
    )

    delta_service = AssetDeltaService()
    patch = delta_service.compute_delta(
        from_version="1.0.0",
        to_version="1.1.0",
        old_bundle_payload=old_bundle.binary_payload,
        new_bundle_payload=new_bundle.binary_payload,
    )

    assert patch.from_version == "1.0.0"
    assert patch.to_version == "1.1.0"
    assert patch.patch_size_bytes > 0

    unpacked_delta = delta_service.apply_delta(patch.patch_bytes)
    assert unpacked_delta["to_version"] == "1.1.0"
    assert unpacked_delta["new_svg_content"] == "<svg v1.1></svg>"
