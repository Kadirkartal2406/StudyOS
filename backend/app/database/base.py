"""
StudyOS — Veritabanı Bağlantısı
SQLAlchemy async engine ve session factory.
Sprint-1.2'de model ve migration'lar eklenecek.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Tüm SQLAlchemy modellerinin temel sınıfı."""

    pass


async def get_db() -> AsyncSession:
    """FastAPI Depends() ile kullanılacak veritabanı oturum bağımlılığı."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
