"""
StudyOS — Ortak Pydantic Şemaları
Tüm response'larda kullanılan envelope ve pagination yapıları.
"""

from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse[T](BaseModel):
    """Tek nesne başarı yanıtı."""

    success: bool = True
    data: T
    message: str = "İşlem başarılı"


class PaginatedResponse[T](BaseModel):
    """Sayfalı liste yanıtı."""

    success: bool = True
    data: list[T]
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
