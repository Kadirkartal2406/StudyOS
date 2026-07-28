"""
RC2 M22.3 — Sentry init (environment-aware).

DEV: DSN yoksa no-op.
BETA/PROD: DSN varsa FastAPI + logging entegrasyonu.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("studyos.sentry")


def init_sentry(settings) -> bool:
    """Sentry'yi başlat. Başarılıysa True."""
    dsn = (getattr(settings, "SENTRY_DSN", None) or "").strip()
    if not dsn:
        logger.info("Sentry disabled (SENTRY_DSN empty)")
        return False

    env = (settings.APP_ENV or "development").strip().lower()
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    except ImportError:
        logger.warning("sentry-sdk not installed; crash reporting skipped")
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=env,
        release=f"studyos-api@{getattr(settings, 'APP_NAME', 'StudyOS')}",
        traces_sample_rate=0.1 if env in {"production", "prod", "beta"} else 0.0,
        send_default_pii=False,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
    )
    logger.info("Sentry initialized env=%s", env)
    return True


def capture_exception(exc: BaseException) -> None:
    """Unhandled exception'ı Sentry'ye gönder (no-op if not init)."""
    try:
        import sentry_sdk

        sentry_sdk.capture_exception(exc)
    except Exception:
        pass
