"""
StudyOS — API Router
Tüm v1 router'larını tek noktada toplar.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

api_router = APIRouter()


@api_router.get("/health", tags=["system"])
async def health_check() -> JSONResponse:
    """Sistem sağlık kontrolü endpoint'i."""
    return JSONResponse(
        content={
            "success": True,
            "data": {"status": "ok", "service": "studyos-api"},
            "message": "Servis çalışıyor",
        }
    )


# Sprint-1+ endpoint'leri buraya eklenecek:
# from app.api.v1 import auth, users, students
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
