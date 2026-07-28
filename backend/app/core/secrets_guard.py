"""
RC2 M22.5 — Production secret validation.

APP_ENV production|prod|beta iken zayıf/default secret ile
uygulama ayağa kalkmaz.
"""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger("studyos.secrets")

_PROD_ENVS = frozenset({"production", "prod", "beta"})

_WEAK_MARKERS = (
    "",
    "change-me",
    "change-me-in-production",
    "change-me-use-openssl-rand-hex-32",
    "secret",
    "password",
    "default",
    "changeme",
    "jwt-secret",
    "your-secret",
)


def _is_weak(value: str | None) -> bool:
    if value is None:
        return True
    v = value.strip()
    if not v:
        return True
    lower = v.lower()
    if lower in _WEAK_MARKERS:
        return True
    if lower.startswith("change-me"):
        return True
    if len(v) < 16:
        return True
    return False


def is_production_like(app_env: str) -> bool:
    return (app_env or "").strip().lower() in _PROD_ENVS


def validate_production_secrets(
    *,
    app_env: str,
    jwt_secret: str,
    app_secret: str | None = None,
    cookie_secret: str | None = None,
    raise_on_fail: bool = True,
) -> list[str]:
    """Prod/beta ortamında secret'ları doğrula. Hata listesi döner."""
    if not is_production_like(app_env):
        return []

    errors: list[str] = []
    if _is_weak(jwt_secret):
        errors.append(
            "JWT_SECRET_KEY production'da zayıf/default/boş olamaz "
            "(min 16 karakter, change-me yasak)"
        )
    if app_secret is not None and _is_weak(app_secret):
        errors.append(
            "APP_SECRET / SECRET_KEY production'da zayıf/default/boş olamaz"
        )
    if cookie_secret is not None and _is_weak(cookie_secret):
        errors.append("COOKIE_SECRET production'da zayıf/default/boş olamaz")

    if errors:
        for err in errors:
            logger.critical("SECRET GUARD: %s", err)
        if raise_on_fail:
            msg = "Production secret validation failed:\n- " + "\n- ".join(errors)
            raise SystemExit(msg)
    return errors


def enforce_or_exit(settings) -> None:
    """Startup helper — settings nesnesinden okur."""
    app_secret = getattr(settings, "APP_SECRET", None) or getattr(
        settings, "SECRET_KEY", None
    )
    cookie_secret = getattr(settings, "COOKIE_SECRET", None)
    try:
        validate_production_secrets(
            app_env=settings.APP_ENV,
            jwt_secret=settings.JWT_SECRET_KEY,
            app_secret=app_secret,
            cookie_secret=cookie_secret,
            raise_on_fail=True,
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        raise
