# Sprint-1.2A — Backend Authentication

**Tarih:** 2026-07-15  
**Sprint:** 1.2A  
**Hedef:** FastAPI backend'inde gerçek JWT authentication sistemini implement etmek; Flutter (Sprint-1.2B) ile uçtan uca entegrasyonu sağlamak.  
**Durum:** ✅ Tamamlandı

---

## Kapsam

`api-design.md` ve `database-design.md`'ye tam sadakatle:

- PostgreSQL (Docker) + SQLAlchemy 2.0 (async) + Alembic
- `User` ve `RefreshToken` modelleri (KVKK alanları dahil)
- bcrypt şifre hash/doğrulama, JWT access token
- Refresh token rotation (opak, rastgele, DB'de SHA-256 hash olarak saklanır)
- `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/users/me`
- Unit + entegrasyon testleri, ruff/mypy doğrulaması, Swagger kontrolü

---

## Altyapı Kurulumu

| Adım | Sonuç |
|------|-------|
| Git repository | `main` + `develop` branch'leri oluşturuldu, `feature/sprint-1.2a-backend-auth` üzerinde geliştirildi |
| GitHub remote | `https://github.com/Kadirkartal2406/StudyOS.git` bağlandı, `main`/`develop` push edildi |
| Docker | `docker-compose` ile `postgres` (16) ve `minio` container'ları çalışır durumda |
| Port çakışması | Native `postgresql-x64-15` servisi (Windows) 5432 portunu tutuyordu — servis durduruldu, Docker container'a geçildi |
| `.env` | Root ve `backend/` için `.env.example`'dan oluşturuldu; `SECRET_KEY`/`JWT_SECRET_KEY` rastgele üretildi; `ALLOWED_ORIGINS` JSON array formatına düzeltildi (pydantic-settings uyumu) |
| `psycopg2-binary` | Alembic senkron migration için eklendi |
| `bcrypt` sürüm sabitleme | `bcrypt==4.0.1` — passlib 1.7.4, bcrypt≥4.1 ile uyumsuz (`detect_wrap_bug` hatası, `AttributeError: module 'bcrypt' has no attribute '__about__'`) |

---

## Doğrulama

| Test | Sonuç |
|------|-------|
| `pytest` (27 test) | ✅ 27 passed |
| `pytest --cov` | ✅ %92 satır kapsamı (`app/`) |
| `ruff check .` | ✅ All checks passed |
| `ruff format --check .` | ✅ 44 files formatted |
| `mypy app` | ✅ Success: no issues found in 36 source files |
| Manuel Swagger doğrulama | ✅ `/api/docs` üzerinden tüm endpoint'ler, request/response şemaları doğrulandı |
| Manuel E2E akış (canlı sunucu) | ✅ register → me → login → refresh (rotation) → eski refresh reddi → logout → yanlış şifre reddi → duplicate email reddi → token'sız erişim reddi |

---

## Oluşturulan Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `app/models/user.py` | `User` modeli — `UserRole`, `UserStatus` (StrEnum), KVKK alanları (`deletion_requested_at`, `anonymized_at`) |
| `app/models/refresh_token.py` | `RefreshToken` modeli — rotation için `token_hash`, `is_revoked`, `expires_at` |
| `app/database/migrations/versions/e031a8862d10_*.py` | `users` ve `refresh_tokens` tablolarını oluşturan Alembic migration |
| `app/core/security.py` | bcrypt hash/verify, JWT access token üretme/doğrulama, opak refresh token üretme/hashleme |
| `app/core/dependencies.py` | `get_current_user` — Bearer JWT doğrulama bağımlılığı |
| `app/repositories/base.py` | Generic `BaseRepository[ModelType]` (PEP 695 tip parametresi) |
| `app/repositories/user_repository.py` | `UserRepository` — email lookup, `last_login_at` güncelleme |
| `app/repositories/refresh_token_repository.py` | `RefreshTokenRepository` — hash lookup, revoke, geçerlilik kontrolü |
| `app/schemas/user.py` | `UserRead` — `status`/`is_verified` → Flutter uyumlu `is_active`/`is_email_verified` dönüşümü |
| `app/schemas/auth.py` | `RegisterRequest`, `LoginRequest`, `RefreshRequest`, `LogoutRequest`, `AuthResponse`, `TokenRefreshResponse` |
| `app/services/auth_service.py` | `AuthService` — register/login/refresh (rotation)/logout iş mantığı |
| `app/api/v1/auth.py` | `/auth/*` endpoint'leri (rate limit: 10/dk) |
| `app/api/v1/users.py` | `/users/me` endpoint'i |
| `app/middleware/rate_limit.py` | slowapi `Limiter` konfigürasyonu |
| `tests/unit/test_security.py` | bcrypt + JWT birim testleri (7 senaryo) |
| `tests/unit/test_auth_service.py` | `AuthService` birim testleri (9 senaryo) |
| `tests/integration/test_auth_endpoints.py` | HTTP entegrasyon testleri (10 senaryo) |

## Güncellenen Dosyalar

| Dosya | Değişiklik |
|-------|------------|
| `app/main.py` | Rate limiter durumu, merkezi `StudyOSException` → HTTP + envelope handler |
| `app/api/router.py` | `auth` ve `users` router'ları bağlandı |
| `app/database/base.py` | `get_db()` dönüş tipi `AsyncGenerator` olarak düzeltildi (mypy) |
| `app/database/migrations/env.py` | `import app.models` eklendi (autogenerate için) |
| `app/models/__init__.py` | Model içe aktarımları (Alembic metadata kaydı) |
| `pyproject.toml` | `bcrypt==4.0.1` pinlendi; `asyncio_default_fixture_loop_scope`/`asyncio_default_test_loop_scope = "session"` eklendi |
| `tests/conftest.py` | Gerçek DB'ye bağlı, test sonunda rollback edilen `db_session` + `client` fixture'ları |

---

## Mimari Kararlar

| Karar | Gerekçe |
|-------|---------|
| Refresh token = opak rastgele dize (JWT değil) | `secrets.token_urlsafe(64)`, DB'de SHA-256 hash — rotation'da JWT decode/verify karmaşıklığı gerekmiyor, çalınma riskinde DB kaydı tek doğrulama noktası |
| `UserRead.from_user()` dönüşümü | `database-design.md`'deki `status`/`is_verified` alanları korunurken, Flutter'ın (Sprint-1.2B) beklediği `is_active`/`is_email_verified` response alanları üretiliyor — mimari değişmeden sözleşme uyumu sağlandı |
| Domain exception → merkezi handler | Servisler yalnızca `StudyOSException` fırlatır; HTTP durum kodu + response envelope `app/main.py`'de tek noktadan üretilir (DRY, `coding-standards.md` §3.7) |
| `bcrypt==4.0.1` pin | `passlib[bcrypt]` mimari kararı korunuyor (ADR gereği değiştirilmedi); yalnızca bilinen sürüm uyumsuzluğu için pin eklendi |
| pytest `loop_scope=session` | SQLAlchemy async engine'in asyncpg connection pool'u tek event loop'a bağlı; test başına yeni loop "another operation is in progress" hatasına yol açıyordu |

---

## Bilinen Sınırlamalar / Sonraki Sprint'e Bırakılanlar

- E-posta doğrulama (`is_verified` → `true` akışı) henüz yok — Sprint-2 kapsamında.
- Şifre sıfırlama (`forgot-password`) endpoint'i Flutter'da placeholder; backend'de henüz yok.
- RBAC (rol bazlı yetkilendirme middleware'i) henüz eklenmedi — `/users/me` dışında korumalı endpoint yok.
- `RefreshTokenRepository.revoke_all_for_user` yazıldı ama henüz hiçbir endpoint tarafından kullanılmıyor (çoklu cihaz çıkışı — ileride).

---

## Bir Sonraki Adım

1. Flutter tarafında backend'e karşı gerçek entegrasyon testi (Sprint-1.2B'nin canlı backend ile doğrulanması).
2. `feature/sprint-1.2a-backend-auth` → `develop` merge.
3. Sprint-1.3 planlaması: Dashboard, çalışma planı modülü.
