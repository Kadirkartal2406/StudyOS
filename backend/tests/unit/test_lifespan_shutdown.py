"""Unit tests for FastAPI lifespan startup & clean shutdown."""

import pytest
from app.main import lifespan, create_application


@pytest.mark.asyncio
async def test_lifespan_clean_shutdown() -> None:
    app = create_application()
    async with lifespan(app):
        # Application running phase
        assert app is not None
    # Context exited cleanly after yield without hanging
