from app.core.config import database_url_for_alembic, normalize_database_url


def test_normalize_neon_uri():
    raw = "postgresql://u:p@ep-x.eu-central-1.aws.neon.tech/neondb?sslmode=require"
    out = normalize_database_url(raw)
    assert out.startswith("postgresql+asyncpg://")
    assert "ssl=require" in out
    assert "sslmode" not in out


def test_alembic_sync_url():
    raw = "postgresql://u:p@host/db?sslmode=require"
    sync = database_url_for_alembic(raw)
    assert "+asyncpg" not in sync
    assert "sslmode=require" in sync
