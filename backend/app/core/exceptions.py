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
    def __init__(self, message: str):
        super().__init__(message=message, code="CONFLICT")


def studyos_exception_to_http(exc: StudyOSException) -> HTTPException:
    """Domain exception'ı HTTP exception'a dönüştürür."""
    code_to_status = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "CONFLICT": status.HTTP_409_CONFLICT,
    }
    http_status = code_to_status.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HTTPException(
        status_code=http_status,
        detail={"code": exc.code, "message": exc.message},
    )
