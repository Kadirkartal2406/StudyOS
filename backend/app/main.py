"""
StudyOS Backend — FastAPI Application
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exceptions import StudyOSException, studyos_exception_to_http
from app.core.secrets_guard import enforce_or_exit
from app.core.sentry import capture_exception, init_sentry
from app.middleware.rate_limit import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(name)s - %(message)s",
    force=True,
)

logger = logging.getLogger("studyos.api")

# RC2 M22.5 — prod/beta'da zayıf secret ile ayağa kalkma
enforce_or_exit(settings)
# RC2 M22.3 — Sentry (DSN yoksa no-op)
init_sentry(settings)


from contextlib import asynccontextmanager
from app.providers.ai.http_transport import (
    close_http_transport,
    init_http_transport,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio
    from app.services.ai_cost.flags import (
        ai_warmup_enabled,
        midnight_scheduler_enabled,
    )

    # 1. AI Shared HTTP client initialization (connection pooling)
    await init_http_transport()

    provider = (settings.AI_PROVIDER or "null").strip().lower()
    if provider in ("", "null", "none"):
        logger.warning(
            "⚠️ AI_PROVIDER is set to 'null'! Question generation is disabled. Set AI_PROVIDER=gemini and GEMINI_API_KEY in environment variables."
        )
    else:
        logger.info("AI_PROVIDER initialized: %s (model: %s)", provider, settings.AI_MODEL or "default")

    # 2. Startup background tasks tracking with names
    background_tasks: list[asyncio.Task] = []

    background_tasks.append(
        asyncio.create_task(_seed_exam_catalog(), name="seed_exam_catalog")
    )
    background_tasks.append(
        asyncio.create_task(_bootstrap_admin(), name="bootstrap_admin")
    )

    if ai_warmup_enabled():
        background_tasks.append(
            asyncio.create_task(_seed_exam_style(), name="seed_exam_style")
        )
    else:
        logger.info("M32: ENABLE_AI_WARMUP=false — style seed skipped at startup")

    if midnight_scheduler_enabled():
        from app.services.booklet_scheduler import midnight_booklet_loop
        from app.services.scoring_scheduler import scoring_loop
        from app.services.smart_question_pool_scheduler import (
            midnight_question_pool_loop,
        )

        background_tasks.append(
            asyncio.create_task(
                midnight_booklet_loop(), name="midnight_booklet_loop"
            )
        )
        background_tasks.append(
            asyncio.create_task(
                scoring_loop(), name="scoring_loop"
            )
        )
        background_tasks.append(
            asyncio.create_task(
                midnight_question_pool_loop(), name="midnight_question_pool_loop"
            )
        )
    else:
        logger.info(
            "M32: ENABLE_MIDNIGHT_SCHEDULER=false — no auto Gemini on startup"
        )

    yield

    # 3. Shutdown cleanup: cancel long-running background loops & wait for cancellation
    logger.info(
        "Lifespan shutdown starting. Active background tasks count=%s",
        len(background_tasks),
    )
    for task in background_tasks:
        if not task.done():
            task_name = task.get_name() if hasattr(task, "get_name") else str(task)
            logger.info("Cancelling background task: %s", task_name)
            task.cancel()

    if background_tasks:
        await asyncio.gather(*background_tasks, return_exceptions=True)

    await close_http_transport()

    # Log any remaining tasks in event loop for diagnosis
    current_task = asyncio.current_task()
    remaining_tasks = [
        t for t in asyncio.all_tasks() if t is not current_task and not t.done()
    ]
    if remaining_tasks:
        remaining_names = [
            t.get_name() if hasattr(t, "get_name") else str(t)
            for t in remaining_tasks
        ]
        logger.info(
            "Lifespan shutdown complete. Remaining event loop tasks count=%s: %s",
            len(remaining_tasks),
            remaining_names,
        )
    else:
        logger.info("Lifespan shutdown complete. Event loop is completely clean.")


async def _bootstrap_admin() -> None:
    from app.services.admin_bootstrap import ensure_admin_user

    await ensure_admin_user()


async def _seed_exam_catalog() -> None:
    try:
        from app.database.base import AsyncSessionLocal
        from app.services.exam_catalog_service import ExamCatalogService

        async with AsyncSessionLocal() as db:
            n = await ExamCatalogService(db).ensure_synced()
            await db.commit()
            if n and n > 0:
                logger.info("Exam catalog seeded topics=%s", n)
    except Exception:
        logger.exception("Exam catalog seed failed")


async def _seed_exam_style() -> None:
    try:
        from app.database.base import AsyncSessionLocal
        from app.services.exam_style_service import ExamStyleService

        async with AsyncSessionLocal() as db:
            n = await ExamStyleService(db).ensure_synced()
            await db.commit()
            logger.info("Exam style profiles synced count=%s", n)
    except Exception:
        logger.exception("Exam style seed failed")


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.23.1-s23p1",
        description="StudyOS REST API",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )


    # ── Rate Limiting ────────────────────────────────────────
    application.state.limiter = limiter
    application.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )

    # ── Domain Exception Handler ─────────────────────────────
    @application.exception_handler(StudyOSException)
    async def studyos_exception_handler(
        _request: Request, exc: StudyOSException
    ) -> JSONResponse:
        http_exc = studyos_exception_to_http(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "success": False,
                "error": {"code": exc.code, "message": exc.message},
            },
        )

    # Sprint 21 RC.8 + RC2 M22.3 — Unhandled → log + Sentry
    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "unhandled path=%s method=%s err=%s",
            request.url.path,
            request.method,
            exc,
        )
        capture_exception(exc)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Beklenmeyen bir sunucu hatası oluştu",
                },
            },
        )

    # ── CORS ──────────────────────────────────────────────────
    origins = list(settings.ALLOWED_ORIGINS or [])
    allow_all = origins == ["*"]
    cors_kwargs: dict = {
        "allow_origins": ["*"] if allow_all else origins,
        # "*" ile credentials birlikte kullanılamaz
        "allow_credentials": not allow_all,
        "allow_methods": ["*"],
        # PDF / bytes istekleri için Accept ve özel header'lara izin
        "allow_headers": ["*"],
        "expose_headers": ["Content-Disposition", "Content-Type"],
    }
    # Flutter Web bazen localhost'un rastgele bir portundan çalışır (örn:
    # http://localhost:xxxx). Bu yüzden development/beta/prod fark etmeksizin
    # localhost için regex ile izin veriyoruz.
    if not allow_all:
        cors_kwargs["allow_origin_regex"] = (
            r"https?://(localhost|127\.0\.0\.1)(:\d+)?|"
            r"https://.*\.onrender\.com"
        )
    application.add_middleware(CORSMiddleware, **cors_kwargs)

    # ── Routers ───────────────────────────────────────────────
    from pathlib import Path

    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import RedirectResponse

    from app.api.router import api_router

    application.include_router(api_router, prefix="/api/v1")

    admin_dir = Path(__file__).resolve().parent / "admin_static"
    if admin_dir.is_dir():
        application.mount(
            "/admin",
            StaticFiles(directory=str(admin_dir), html=True),
            name="admin",
        )

        @application.get("/admin-panel", include_in_schema=False)
        async def admin_panel_redirect():
            return RedirectResponse(url="/admin/")

    uploads_dir = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    application.mount(
        "/uploads",
        StaticFiles(directory=str(uploads_dir)),
        name="uploads",
    )

    @application.get("/docs", include_in_schema=False)
    async def docs_redirect():
        return RedirectResponse(url="/api/docs")

    return application


app = create_application()
