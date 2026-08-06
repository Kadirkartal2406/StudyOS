"""
StudyOS Educational Asset Engine (EAE) — Tenant Isolation Service
Enforces institutional multi-tenant boundaries for proprietary educational assets.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.core.exceptions import AuthorizationError
from app.models.educational_asset import EducationalAsset
from app.models.user import User, UserRole


class AssetTenantService:
    """
    Validates tenant access boundaries for Educational Assets.
    """

    def enforce_tenant_access(
        self, asset: EducationalAsset, user: User
    ) -> None:
        """
        Validates if user has permission to access a tenant-restricted asset.
        - Core assets (tenant_id is None) are accessible to all users.
        - Tenant assets are only accessible to users belonging to that tenant_id or system admins.
        """
        if asset.tenant_id is None:
            return  # Public/Core StudyOS asset

        if user.role == UserRole.SYSTEM_ADMIN:
            return  # System admin override

        # Check tenant match
        user_tenant_id = getattr(user, "tenant_id", None)
        if user_tenant_id is None or str(user_tenant_id) != str(asset.tenant_id):
            raise AuthorizationError(
                f"Access denied to tenant-isolated asset '{asset.asset_id}'"
            )
