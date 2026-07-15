# Sprint-1.1 — Proje Kurulumu Raporu

**Tarih:** 2026-07-06 / 2026-07-07  
**Sprint:** 1.1  
**Hedef:** Projenin temel yapısını kurmak; iş mantığı yazmadan geliştirmeye hazır duruma getirmek.  
**Durum:** ✅ Tamamlandı

---

## Özet

| Bileşen | Durum | Not |
|---------|-------|-----|
| Depo kök yapısı | ✅ | `.gitignore`, `.env.example`, `docker-compose.yml`, `.editorconfig`, `README.md` |
| FastAPI Backend | ✅ | Lint, test ve HTTP doğrulaması geçti |
| Flutter Mobile | ✅ | `pub get` + `flutter analyze — No issues found!` |
| Flutter Web | ✅ | `pub get` + `flutter analyze — No issues found!` |
| GitHub Actions CI | ✅ | Backend, Mobile, Web pipeline'ları |
| PR Şablonu | ✅ | `.github/PULL_REQUEST_TEMPLATE.md` |
| Alembic | ✅ | `alembic.ini`, `env.py`, `script.py.mako` |
| Scripts | ✅ | `check_env.py`, `setup.ps1` |
| Flutter SDK kurulumu | ✅ | 3.32.4 — `C:\Users\kadir\AppData\Local\flutter` |

---

## Oluşturulan Dosyalar

### Kök Dizin

| Dosya | Açıklama |
|-------|---------|
| `.gitignore` | Python, Flutter, Docker, iOS, Android hariç tutmaları |
| `.env.example` | Tüm ortam değişkeni şablonu (gerçek değer içermez) |
| `.editorconfig` | Editör tutarlılığı (indent, encoding, newline) |
| `docker-compose.yml` | PostgreSQL 16 + MinIO servisleri |
| `README.md` | Proje giriş noktası ve hızlı başlangıç kılavuzu |

### Backend (`backend/`)

| Dosya | Açıklama |
|-------|---------|
| `pyproject.toml` | Tüm bağımlılıklar + ruff/mypy/pytest konfigürasyonu |
| `alembic.ini` | Migration konfigürasyonu |
| `app/main.py` | FastAPI uygulama fabrikası + CORS |
| `app/core/config.py` | Pydantic BaseSettings — ortam değişkenleri |
| `app/core/exceptions.py` | Domain exception hiyerarşisi |
| `app/api/router.py` | Merkezi router + `/api/v1/health` endpoint |
| `app/database/base.py` | SQLAlchemy async engine, session, Base |
| `app/database/migrations/env.py` | Alembic ortam dosyası |
| `app/database/migrations/script.py.mako` | Migration şablon dosyası |
| `app/schemas/common.py` | Paylaşımlı response zarfları |
| `app/providers/ai/base.py` | AI provider placeholder |
| `tests/conftest.py` | pytest AsyncClient fixture |
| `tests/integration/test_health.py` | Health-check entegrasyon testi |
| `README.md` | Backend hızlı başlangıç |

### Flutter Mobile (`mobile/`)

| Dosya | Açıklama |
|-------|---------|
| `pubspec.yaml` | Tüm bağımlılıklar (Riverpod, Dio, Drift, GoRouter, Firebase…) |
| `analysis_options.yaml` | Flutter lint kuralları |
| `lib/main.dart` | Uygulama giriş noktası (ProviderScope) |
| `lib/app.dart` | MaterialApp.router kök widget'ı |
| `lib/core/router/app_router.dart` | GoRouter + geçici Splash ekranı |
| `lib/core/theme/app_theme.dart` | Light/Dark MaterialTheme |
| `lib/core/theme/app_colors.dart` | Renk paleti sabitler |

### Flutter Web (`web/`)

| Dosya | Açıklama |
|-------|---------|
| `pubspec.yaml` | Web bağımlılıkları (data_table_2 dahil) |
| `analysis_options.yaml` | Flutter lint kuralları |
| `lib/main.dart` | Giriş noktası |
| `lib/app.dart` | MaterialApp.router kök widget'ı |
| `lib/core/router/app_router.dart` | GoRouter + Dashboard placeholder |
| `lib/core/theme/app_theme.dart` | Web panel teması |

### CI/CD (`.github/`)

| Dosya | Açıklama |
|-------|---------|
| `workflows/backend-ci.yml` | ruff → mypy → pytest pipeline |
| `workflows/mobile-ci.yml` | dart format → flutter analyze → flutter test |
| `workflows/web-ci.yml` | dart format → flutter analyze → flutter test |
| `PULL_REQUEST_TEMPLATE.md` | PR zorunlu alanları ve DoD kontrol listesi |

---

## Çalıştırılan Komutlar

```powershell
# uv kurulumu
pip install uv

# Dart SDK (winget)
winget install --id Google.DartSDK

# Backend bağımlılıkları
cd backend && uv sync --extra dev

# Backend lint
uv run ruff check . && uv run ruff format .

# Backend doğrulama
Invoke-WebRequest http://localhost:8001/api/v1/health
# → 200 OK {"success":true,"data":{"status":"ok","service":"studyos-api"}}
```

---

## Kurulan Bağımlılıklar

### Python (backend/.venv)

`uv sync --extra dev` ile 110 paket kuruldu. Öne çıkanlar:

| Paket | Sürüm | Amaç |
|-------|-------|------|
| fastapi | 0.115.x | Web framework |
| sqlalchemy | 2.0.x | ORM |
| alembic | 1.14.x | Migration |
| asyncpg | 0.30.x | PostgreSQL async driver |
| pydantic | 2.9.x | Veri doğrulama |
| pydantic-settings | 2.6.x | Env var yönetimi |
| python-jose | 3.3.x | JWT |
| passlib[bcrypt] | 1.7.x | Şifre hash |
| ruff | 0.8.x | Linting + format |
| pytest | 8.x | Test |

### Flutter

Flutter 3.32.4 indirmesi devam ediyordu; kurulum tamamlanınca:
```
flutter pub get   # mobile/ ve web/ için
```

---

## Doğrulama Sonuçları

| Test | Sonuç |
|------|-------|
| `ruff check .` (backend) | ✅ Temiz |
| `ruff format .` (backend) | ✅ Uygulandı |
| `GET /api/v1/health` → HTTP 200 | ✅ |
| `pytest tests/integration/test_health.py` | ✅ 1 passed |
| `flutter pub get` (mobile) | ✅ 154 paket |
| `flutter analyze` (mobile) | ✅ No issues found! |
| `flutter pub get` (web) | ✅ 121 paket |
| `flutter analyze` (web) | ✅ No issues found! |

---

## Karşılaşılan Sorunlar ve Çözümler

| Sorun | Çözüm |
|-------|-------|
| Flutter winget'te `Google.Flutter` ID'si bulunamadı | Resmi storage URL'den ZIP indirme yöntemi kullanıldı |
| `.gitignore` bir dizin olarak var | `Remove-Item -Recurse` ile silindi, dosya olarak yeniden oluşturuldu |
| `ruff check` 8 hata (List deprecation, UP046, N818) | `--fix --unsafe-fixes` ile otomatik düzeltildi; N818 için `# noqa: N818` eklendi |
| Server restart nedeniyle Flutter indirme yarıda kesildi | Yeniden tam indirme başlatıldı |

---

## Alınan Kararlar

| Karar | Gerekçe |
|-------|---------|
| `uv` pip yerine kullanıldı | 10–100x daha hızlı; lock file ile deterministic kurulum |
| Dart SDK winget ile ayrı kuruldu | Flutter winget'te yok; Dart ek araç olarak kuruldu |
| N818 noqa ile bastırıldı | `StudyOSException` kasıtlı domain ismi; Error suffix uygun değil |
| Backend 8001 portunda test edildi | 8000 başka bir servis tarafından kullanılıyor olabilir |
| Flutter bağımlılıkları elle `pubspec.yaml`'a yazıldı | Flutter SDK olmadan `flutter create` çalışmaz; kurulum sonrası `pub get` yeterli |

---

## Sprint-1.2 Önerisi

Sprint-1.1 altyapı kurulumunu tamamladı. Sprint-1.2 şu görevlere odaklanmalıdır:

**Öncelik 1 — Tamamlama:**
- [ ] Flutter SDK kurulumunu tamamla, `flutter pub get` çalıştır
- [ ] `flutter analyze` ile lint doğrula
- [ ] `flutter build` ile build doğrula

**Öncelik 2 — Sprint-1.2 Backend Auth:**
- [ ] `User` ve `RefreshToken` SQLAlchemy modelleri
- [ ] İlk Alembic migration
- [ ] `AuthService`: kayıt, giriş, JWT üretimi
- [ ] `/api/v1/auth/register`, `/login`, `/refresh`, `/logout` endpoint'leri

**Öncelik 3 — Sprint-1.2 Flutter Auth:**
- [ ] `AuthRepository` interface + Dio implementasyonu
- [ ] JWT interceptor (refresh token otomasyonu)
- [ ] Login ve Register ekranları

---

## Mimari Uyum Kontrolü

| Gereksinim (software-architecture.md) | Durum |
|--------------------------------------|-------|
| `mobile/` — Feature-First Clean Architecture | ✅ Dizin yapısı oluşturuldu |
| `web/` — Flutter Web kurumsal panel | ✅ Temel yapı oluşturuldu |
| `backend/` — Domain-Based Modular Monolith | ✅ Tam katmanlı yapı oluşturuldu |
| Bağımlılık yönü: api → services → repositories | ✅ Katmanlar ayrı |
| Pydantic BaseSettings ile config | ✅ `core/config.py` |
| AI Provider soyutlama katmanı | ✅ `providers/ai/base.py` placeholder |
| Alembic migration altyapısı | ✅ |
| GitHub Actions CI | ✅ 3 pipeline |
