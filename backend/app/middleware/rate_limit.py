"""
StudyOS — Rate Limiting
slowapi tabanlı istek sınırlama. Bkz. docs/architecture/software-architecture.md §3.6
Genel: 60 istek/dakika · Auth endpoint'leri: 10 istek/dakika
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)

AUTH_RATE_LIMIT = f"{settings.AUTH_RATE_LIMIT_PER_MINUTE}/minute"
