"""
StudyOS Backend — FastAPI Application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exceptions import StudyOSException, studyos_exception_to_http
from app.middleware.rate_limit import limiter


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="StudyOS REST API",
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url="/api/redoc" if settings.DEBUG else None,
    )

    # ── Rate Limiting ────────────────────────────────────────
    application.state.limiter = limiter
    application.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )

    # ── Domain Exception Handler ─────────────────────────────
    # Servisler yalnızca StudyOSException fırlatır; HTTP durum kodu ve
    # response envelope'u burada merkezi olarak üretilir (coding-standards.md §3.7).
    @application.exception_handler(StudyOSException)
    async def studyos_exception_handler(_request: Request, exc: StudyOSException) -> JSONResponse:
        http_exc = studyos_exception_to_http(exc)
        return JSONResponse(
            status_code=http_exc.status_code,
            content={"success": False, "error": {"code": exc.code, "message": exc.message}},
        )

    # ── CORS ──────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # ── Routers ───────────────────────────────────────────────
    from app.api.router import api_router

    application.include_router(api_router, prefix="/api/v1")

    return application


app = create_application()
