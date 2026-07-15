"""
StudyOS — API Router
Tüm v1 router'larını tek noktada toplar.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.v1 import auth, users

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


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Sprint-2+ endpoint'leri buraya eklenecek:
# from app.api.v1 import students, institutions
# api_router.include_router(students.router, prefix="/students", tags=["students"])
