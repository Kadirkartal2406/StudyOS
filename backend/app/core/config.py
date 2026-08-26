"""
StudyOS — Uygulama Konfigürasyonu
Ortam değişkenleri pydantic-settings ile yüklenir.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Neon/Render postgres URL → SQLAlchemy asyncpg (+ SSL)."""
    u = (url or "").strip()
    if not u:
        return u
    if u.startswith("postgres://"):
        u = "postgresql+asyncpg://" + u[len("postgres://") :]
    elif u.startswith("postgresql://"):
        u = "postgresql+asyncpg://" + u[len("postgresql://") :]
    # Neon often ships sslmode=require; asyncpg wants ssl=require
    if "sslmode=require" in u:
        u = u.replace("sslmode=require", "ssl=require")
    return u


def database_url_for_alembic(url: str) -> str:
    """asyncpg URL → psycopg2 sync URL for Alembic."""
    u = normalize_database_url(url).replace("+asyncpg", "")
    if "ssl=require" in u and "sslmode=" not in u:
        u = u.replace("ssl=require", "sslmode=require")
    return u


def _normalize_origin_list(values: Any) -> list[str]:
    """Strip, drop empties/wildcards, preserve order (dedupe)."""
    out: list[str] = []
    seen: set[str] = set()
    for raw in values:
        origin = str(raw).strip().rstrip("/")
        if not origin or origin == "*":
            continue
        if origin in seen:
            continue
        seen.add(origin)
        out.append(origin)
    return out


# Flutter Web loopback — rastgele port (chrome/web-server).
LOCALHOST_ORIGIN_REGEX = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"


def build_cors_middleware_kwargs(
    allowed_origins: list[str] | None,
    *,
    allow_localhost: bool = True,
) -> dict[str, Any]:
    """CORS kwargs for FastAPI — never uses wildcard '*'."""
    origins = _normalize_origin_list(allowed_origins or [])
    kwargs: dict[str, Any] = {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        # Authorization / PDF / özel header'lar
        "allow_headers": ["*"],
        "expose_headers": ["Content-Disposition", "Content-Type"],
    }
    if allow_localhost:
        kwargs["allow_origin_regex"] = LOCALHOST_ORIGIN_REGEX
    return kwargs


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Uygulama ──────────────────────────────────────────────
    APP_NAME: str = "StudyOS"
    APP_ENV: str = "development"  # development | beta | production
    DEBUG: bool = True
    # RC2 M22.5 — genel uygulama secret'ı (prod'da zorunlu güçlü)
    APP_SECRET: str = "change-me-in-production"
    # Geriye uyum: .env SECRET_KEY → APP_SECRET alias
    SECRET_KEY: str = ""
    COOKIE_SECRET: str = "change-me-in-production"

    # ── Veritabanı ────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://studyos:studyos@localhost:5432/studyos_dev"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    # Recycle before Neon/PgBouncer idle disconnect (seconds). 0 = disabled.
    DATABASE_POOL_RECYCLE: int = 280

    # ── APIs ──────────────────────────────────────────────────
    DENEME_API_KEY: str = ""

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

    # ── AI (Sprint-2.4 — gerçek LLM; key'ler yalnızca .env) ───
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_2: str = ""
    GEMINI_API_KEY_3: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    # null | gemini | openai | claude
    AI_PROVIDER: str = "null"
    AI_MODEL: str = ""
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 4096
    AI_TIMEOUT_SECONDS: float = 90.0
    AI_RETRY_COUNT: int = 2
    AI_RATE_LIMIT_PER_MINUTE: int = 20
    # B1: primary fail → null (boş bırakılırsa null)
    AI_FALLBACK_PROVIDER: str = "null"
    # M32 — model zinciri: primary + en fazla N fallback
    AI_GEMINI_MAX_FALLBACKS: int = 0
    # M32 — günlük Gemini istek bütçesi (0 = limitsiz; prod'da 1200–1500 önerilir)
    AI_DAILY_REQUEST_BUDGET: int = 1200
    # Haftalık deneme: her gece Mon–Sat üretilecek pack üst sınırı (~19 pack / 6 gece)
    AI_NIGHTLY_DENEME_PACKS: int = 4
    # 06:00 havuz dolumu: kalan bütçe bu eşiğin altındaysa skip
    AI_POOL_FILL_MIN_REMAINING: int = 50

    # ── M32 Production readiness / cost flags (dev default: OFF) ──
    ENABLE_AUTO_BOOKLET: bool = False
    ENABLE_BACKGROUND_AI: bool = False
    ENABLE_MIDNIGHT_SCHEDULER: bool = False
    ENABLE_CATCHUP: bool = False
    ENABLE_AI_WARMUP: bool = False
    # M33 — Smart Question Pool Scheduler (dry-run: sadece hesaplar, üretmez)
    QUESTION_POOL_SCHEDULER_DRY_RUN: bool = False
    QUESTION_POOL_LOCK_TTL_MINUTES: int = 15
    # M34.5 — Production validation / cost-aware generation
    AI_HOURLY_REQUEST_BUDGET: int = 300  # 0 = unlimited
    QUESTION_PRODUCTION_APPROVAL_MODE: str = "auto"  # auto | manual
    QUESTION_PRODUCTION_MAX_RETRY: int = 2
    QUESTION_PRODUCTION_EST_COST_PER_QUESTION_USD: float = 0.002
    # Compact author: Writer+Distractor+Naturalizer tek LLM (Review/VSSE aynı)
    ENABLE_COMPACT_AUTHOR: bool = True
    # exam_catalog is the production topic-list SSOT (Derslerim / Soru Üret).
    # LP TOPIC_CATALOG_SEED remains fallback when EI list is empty or errors.
    # ASCII dual-read on topic_tests is independent of this flag.
    TOPIC_CATALOG_SSOT: bool = True
    # Soft measurement side-channel (default OFF — existing behavior unchanged)
    # off | shadow | soft_review
    MEASUREMENT_MODE: str = "off"
    MEASUREMENT_CONTRACT_MAX_REGEN: int = 1

    # ── Knowledge Layer (Sprint 19) ───────────────────────────
    # notebooklm | local  — domain servisleri provider'dan bağımsız
    KNOWLEDGE_PROVIDER: str = "notebooklm"

    # ── Assessment booklet (Sprint 23) ────────────────────────
    # true → AI yerine sentetik soru (dev/test); AI_PROVIDER=null iken de sentetik
    ASSESSMENT_BOOKLET_SYNTHETIC: bool = False

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
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15
    # Mobil / web deep-link tabanı (şifre sıfırlama URL'si)
    PUBLIC_APP_URL: str = "http://127.0.0.1:8002"
    # Admin bootstrap (yoksa startup'ta oluşturulur / role yükseltilir)
    ADMIN_BOOTSTRAP_EMAIL: str = "kadirkartal4921@icloud.com"
    ADMIN_BOOTSTRAP_PASSWORD: str = "Kadir_kartal49"
    ADMIN_BOOTSTRAP_FIRST_NAME: str = "Kadir"
    ADMIN_BOOTSTRAP_LAST_NAME: str = "Kartal"

    # ── Sentry ────────────────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── CORS ──────────────────────────────────────────────────
    # Env: "https://a.com,https://b.com" veya JSON '["https://a.com"]'
    # "*" desteklenmez (credentials + Flutter Web kırılır); yok sayılır.
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
    ]
    # Flutter Web rastgele localhost portu (örn. :57780) — yalnızca loopback.
    CORS_ALLOW_LOCALHOST: bool = True

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    AUTH_RATE_LIMIT_PER_MINUTE: int = 10

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_db(cls, v: Any) -> Any:
        if isinstance(v, str):
            return normalize_database_url(v)
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _parse_origins(cls, v: Any) -> Any:
        default = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://localhost:5173",
        ]
        if v is None or v == "":
            return default
        if isinstance(v, (list, tuple, set)):
            return _normalize_origin_list(v)
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return default
            if s == "*":
                # Wildcard yasak — boş liste; localhost regex ayrıca eklenir.
                return []
            if s.startswith("["):
                import json

                try:
                    parsed = json.loads(s)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        "ALLOWED_ORIGINS JSON dizi olmalı, örn. "
                        '[\"https://app.example.com\"]'
                    ) from exc
                if not isinstance(parsed, list):
                    raise ValueError("ALLOWED_ORIGINS JSON bir dizi olmalı")
                return _normalize_origin_list(parsed)
            return _normalize_origin_list(s.split(",")) or default
        return default
    @model_validator(mode="after")
    def _empty_s3_endpoint(self) -> Settings:
        if self.AWS_S3_ENDPOINT_URL is not None and self.AWS_S3_ENDPOINT_URL.strip() == "":
            object.__setattr__(self, "AWS_S3_ENDPOINT_URL", "")
        return self


@lru_cache
def get_settings() -> Settings:
    raw = Settings()
    updates: dict = {}
    if (not raw.APP_SECRET or raw.APP_SECRET.startswith("change-me")) and raw.SECRET_KEY:
        updates["APP_SECRET"] = raw.SECRET_KEY
    if (
        not raw.COOKIE_SECRET or raw.COOKIE_SECRET.startswith("change-me")
    ) and raw.SECRET_KEY:
        updates["COOKIE_SECRET"] = raw.SECRET_KEY
    return raw.model_copy(update=updates) if updates else raw


settings = get_settings()
