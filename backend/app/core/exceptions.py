"""
StudyOS — Temel Hata Sınıfları
Tüm domain exception'ları bu modülden türer.
"""

from fastapi import HTTPException, status


class StudyOSException(Exception):  # noqa: N818
    """StudyOS temel exception sınıfı."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(StudyOSException):
    def __init__(self, resource: str, identifier: str = ""):
        super().__init__(
            message=f"{resource} bulunamadı: {identifier}",
            code="NOT_FOUND",
        )


class AuthenticationError(StudyOSException):
    def __init__(self, message: str = "Kimlik doğrulama başarısız"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationError(StudyOSException):
    def __init__(self, message: str = "Bu işlem için yetkiniz yok"):
        super().__init__(message=message, code="AUTHORIZATION_ERROR")


class ValidationError(StudyOSException):
    def __init__(self, message: str, field: str = ""):
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field


class ConflictError(StudyOSException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, code="CONFLICT")
        self.details = details or {}


class AIProviderError(StudyOSException):
    """LLM sağlayıcı hatası — mesajda API key asla yer almaz."""

    def __init__(self, message: str, code: str = "AI_PROVIDER_ERROR"):
        super().__init__(message=message, code=code)


class AITimeoutError(AIProviderError):
    def __init__(self, message: str = "AI sağlayıcı zaman aşımına uğradı"):
        super().__init__(message=message, code="AI_TIMEOUT")


class AIRateLimitError(AIProviderError):
    def __init__(self, message: str = "AI kota / hız limiti aşıldı"):
        super().__init__(message=message, code="AI_RATE_LIMIT")


class AIQuotaExceededError(AIProviderError):
    def __init__(self, message: str = "AI kullanım kotası doldu"):
        super().__init__(message=message, code="AI_QUOTA_EXCEEDED")


class AIUnavailableError(AIProviderError):
    def __init__(self, message: str = "AI sağlayıcı kullanılamıyor"):
        super().__init__(message=message, code="AI_UNAVAILABLE")


def studyos_exception_to_http(exc: StudyOSException) -> HTTPException:
    """Domain exception'ı HTTP exception'a dönüştürür."""
    code_to_status = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "CONFLICT": status.HTTP_409_CONFLICT,
        "AI_TIMEOUT": status.HTTP_504_GATEWAY_TIMEOUT,
        "AI_RATE_LIMIT": status.HTTP_429_TOO_MANY_REQUESTS,
        "AI_QUOTA_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "AI_UNAVAILABLE": status.HTTP_503_SERVICE_UNAVAILABLE,
        "AI_PROVIDER_ERROR": status.HTTP_502_BAD_GATEWAY,
    }
    http_status = code_to_status.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    detail: dict = {"code": exc.code, "message": exc.message}
    if isinstance(exc, ConflictError) and exc.details:
        detail["details"] = exc.details
    return HTTPException(
        status_code=http_status,
        detail=detail,
    )
