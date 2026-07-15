"""
StudyOS — Uygulama Konfigürasyonu
Ortam değişkenleri pydantic-settings ile yüklenir.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Uygulama ──────────────────────────────────────────────
    APP_NAME: str = "StudyOS"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Veritabanı ────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://studyos:studyos@localhost:5432/studyos_dev"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── AWS S3 / MinIO ────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    AWS_REGION: str = "eu-central-1"
    AWS_S3_BUCKET_NAME: str = "studyos-dev"
    AWS_S3_ENDPOINT_URL: str = "http://localhost:9000"

    # ── AI ────────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_PROVIDER: str = "gemini"

    # ── Firebase ──────────────────────────────────────────────
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""

    # ── E-posta ───────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@studyos.com"
    SMTP_FROM_NAME: str = "StudyOS"

    # ── Sentry ────────────────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── CORS ──────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
