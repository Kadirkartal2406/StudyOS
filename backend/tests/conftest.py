"""
StudyOS — Test Yapılandırması
Sprint-1.2'de gerçek testler eklenecek.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """FastAPI test istemcisi."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
