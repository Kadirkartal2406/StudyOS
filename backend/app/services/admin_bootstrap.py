"""Ensure bootstrap system_admin exists (from settings)."""

from __future__ import annotations

import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.database.base import AsyncSessionLocal
from app.models.user import User, UserRole, UserStatus

logger = logging.getLogger("studyos.admin_bootstrap")


async def ensure_admin_user() -> None:
    email = (settings.ADMIN_BOOTSTRAP_EMAIL or "").strip()
    password = settings.ADMIN_BOOTSTRAP_PASSWORD or ""
    if not email or not password:
        logger.info("Admin bootstrap skipped (no ADMIN_BOOTSTRAP_EMAIL/PASSWORD)")
        return

    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(
                    email=email,
                    hashed_password=hash_password(password),
                    first_name=settings.ADMIN_BOOTSTRAP_FIRST_NAME or "Admin",
                    last_name=settings.ADMIN_BOOTSTRAP_LAST_NAME or "User",
                    role=UserRole.SYSTEM_ADMIN,
                    status=UserStatus.ACTIVE,
                    is_verified=True,
                )
                db.add(user)
                await db.commit()
                logger.info("Admin user created email=%s", email)
                return

            changed = False
            if str(user.role) != UserRole.SYSTEM_ADMIN:
                user.role = UserRole.SYSTEM_ADMIN
                changed = True
            if user.status != UserStatus.ACTIVE:
                user.status = UserStatus.ACTIVE
                changed = True
            if not user.is_verified:
                user.is_verified = True
                changed = True
            # Keep password in sync with bootstrap setting in development
            if not verify_password(password, user.hashed_password):
                user.hashed_password = hash_password(password)
                changed = True
            if changed:
                await db.commit()
                logger.info("Admin user updated email=%s", email)
            else:
                logger.info("Admin user already present email=%s", email)
    except Exception:
        logger.exception("Admin bootstrap failed")
