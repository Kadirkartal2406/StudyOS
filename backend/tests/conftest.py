"""
StudyOS — Test Yapılandırması
Her test, gerçek (Docker) veritabanına bağlı ayrı bir oturum kullanır.
Servis/repository katmanı yalnızca `flush()` çağırır (commit etmez); test
sonunda oturum `rollback()` edilerek tüm değişiklikler geri alınır.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import AsyncSessionLocal, get_db
from app.main import app


@pytest.fixture
async def db_session():
    """Test sonunda rollback edilen izole bir DB oturumu."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession):
    """Test DB oturumunu kullanan FastAPI HTTP test istemcisi."""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)
