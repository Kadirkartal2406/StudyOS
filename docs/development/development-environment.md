# StudyOS — Geliştirme Ortamı

**Belge Durumu:** Aktif  
**Sürüm:** 1.0  
**Oluşturuldu:** 2026-07-06 — Meeting-008  
**Dil:** Türkçe  
**Kapsam:** İki kişilik geliştirme ekibi için standart ortam tanımı

> Bu belgede tanımlanan sürümler ve araçlar tüm geliştiriciler için zorunludur.  
> Farklı sürüm kullanmak için proje sahibi onayı gerekir.

---

## 1. Depo (Repository) Yapısı

StudyOS tek bir Git deposunda (monorepo-lite) yönetilir. Üç bağımsız proje tek çatı altında tutulur; her biri kendi bağımlılık ve konfigürasyon dosyalarını taşır.

```
StudyOS/                          ← Git kök dizini
│
├── mobile/                       ← Flutter Mobil Uygulaması (iOS + Android)
│   ├── lib/
│   ├── test/
│   ├── assets/
│   ├── pubspec.yaml
│   └── README.md
│
├── web/                          ← Flutter Web Uygulaması (Kurumsal Panel)
│   ├── lib/
│   ├── test/
│   ├── web/                      ← Flutter Web index.html vb.
│   ├── pubspec.yaml
│   └── README.md
│
├── backend/                      ← FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── middleware/
│   │   └── providers/
│   ├── tests/
│   ├── alembic.ini
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── README.md
│
├── docs/                         ← Proje dokümantasyonu (kaynak gerçeği)
│   ├── architecture/
│   ├── decisions/
│   ├── development/
│   ├── meeting-notes/
│   ├── planning/
│   ├── project/
│   ├── requirements/
│   └── research/
│
├── scripts/                      ← Otomasyon ve yardımcı betikler
│   ├── setup.sh                  ← Geliştirme ortamı kurulum betiği
│   ├── seed_db.py                ← Veritabanı test verisi yükleme
│   └── check_env.py              ← Ortam değişkeni doğrulama
│
├── .github/                      ← GitHub Actions CI/CD ve PR şablonları
│   ├── workflows/
│   │   ├── backend-ci.yml
│   │   ├── mobile-ci.yml
│   │   └── web-ci.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│
├── docker-compose.yml            ← Yerel geliştirme servisleri (PostgreSQL + MinIO)
├── docker-compose.override.yml   ← Kişisel geliştirici ayarları (git'e eklenmez)
├── .env.example                  ← Tüm ortam değişkeni şablonu
├── .gitignore
├── .editorconfig                 ← Editör tutarlılığı (indent, encoding)
└── README.md                     ← Proje giriş noktası

```

### Klasör Sorumlulukları

| Klasör | Sorumluluk |
|--------|-----------|
| `mobile/` | Flutter iOS/Android uygulaması; kendi `pubspec.yaml` ile bağımsız |
| `web/` | Flutter Web kurumsal paneli; mobil ile paylaşımlı widget paketi hedefi |
| `backend/` | FastAPI REST API; tüm iş mantığı, kimlik doğrulama, AI entegrasyonu |
| `docs/` | Tek kaynak gerçeği; proje anayasası, mimari, gereksinimler |
| `scripts/` | Geliştirici verimliliği betikleri; CI/CD dışı otomasyon |
| `.github/` | GitHub Actions pipeline'ları ve PR/issue şablonları |

---

## 2. Gerekli Yazılımlar

### 2.1 Zorunlu Araçlar (Sprint-1 Başlamadan Kurulmalı)

| Araç | Versiyon | Amaç | Öncelik |
|------|---------|------|---------|
| **Flutter SDK** | 3.27.x (stable) | Mobil ve Web uygulama geliştirme | 🔴 Kritik |
| **Dart SDK** | 3.6.x (Flutter ile gelir) | Flutter'ın dili | 🔴 Kritik |
| **Python** | 3.12.x | FastAPI backend geliştirme | 🔴 Kritik |
| **uv** | latest | Python bağımlılık yönetimi (pip yerine) | 🔴 Kritik |
| **Git** | 2.45+ | Versiyon kontrolü | 🔴 Kritik |
| **Docker Desktop** | 4.x | PostgreSQL + MinIO yerel çalıştırma | 🔴 Kritik |
| **VS Code** veya **Cursor** | latest | IDE | 🔴 Kritik |

### 2.2 VS Code Eklentileri (Zorunlu)

| Eklenti | Amaç |
|---------|------|
| `Dart` (Dart Code) | Dart dil desteği |
| `Flutter` (Dart Code) | Flutter geliştirme araçları |
| `Python` (Microsoft) | Python dil desteği |
| `Pylance` | Python type-checking |
| `Ruff` | Python linting ve formatlama |
| `Docker` (Microsoft) | Docker Compose yönetimi |
| `GitLens` | Git geçmişi ve blame |
| `Thunder Client` veya `REST Client` | API test aracı |
| `Mermaid Preview` | Mermaid diyagramlarını önizleme |

### 2.3 Platform Araçları (iOS/Android)

| Araç | Platform | Amaç |
|------|---------|------|
| Xcode 16+ | macOS (iOS) | iOS simülatör ve build |
| Android Studio | Windows/macOS | Android emülatör ve SDK |
| CocoaPods | macOS | iOS bağımlılık yönetimi |

> **Not:** İki kişilik ekipten her biri hem Android hem iOS geliştirme araçlarını kurmalıdır.

### 2.4 Sürüm Doğrulama Komutları

Kurulumu doğrulamak için çalıştırılacak komutlar:

```
flutter --version       → Flutter 3.27.x
dart --version          → Dart 3.6.x
python --version        → Python 3.12.x
uv --version            → 0.x.x
git --version           → git 2.45+
docker --version        → Docker 4.x
docker compose version  → v2.x
```

---

## 3. Yerel Geliştirme Ortamı (Docker)

### 3.1 docker-compose.yml Servisleri

Yerel geliştirme için iki servis çalışır. Uygulama kodu Docker'da çalışmaz; yalnızca altyapı servisleri Docker'da çalışır.

| Servis | Image | Port | Amaç |
|--------|-------|------|------|
| `postgres` | `postgres:16-alpine` | 5432 | Ana veritabanı |
| `minio` | `minio/minio:latest` | 9000 / 9001 | S3 uyumlu yerel depolama |

### 3.2 MinIO Yapılandırması

Geliştirmede tüm dosya işlemleri MinIO üzerinden yapılır. MinIO, AWS S3 API'si ile birebir uyumludur; `boto3` kodu değişiklik gerektirmez.

MinIO web arayüzü: `http://localhost:9001`

### 3.3 Backend Başlatma

Backend Docker olmadan direkt çalışır:

```
cd backend/
uv sync                          # Bağımlılıkları yükle
uv run alembic upgrade head      # Veritabanı migration'larını uygula
uv run uvicorn app.main:app --reload --port 8000
```

---

## 4. Ortam Değişkenleri

`.env.example` dosyası tüm ortam değişkenlerini açıklamalı olarak içerir. Gerçek değerler hiçbir zaman git'e eklenmez.

### 4.1 Backend Ortam Değişkenleri

```ini
# ─── Uygulama ───────────────────────────────────────────
APP_NAME=StudyOS
APP_ENV=development           # development | staging | production
DEBUG=true
SECRET_KEY=                   # Rastgele 32+ karakter; openssl rand -hex 32

# ─── Veritabanı ─────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://studyos:studyos@localhost:5432/studyos_dev
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10

# ─── JWT ────────────────────────────────────────────────
JWT_SECRET_KEY=               # Rastgele 32+ karakter; openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# ─── AWS S3 / MinIO ─────────────────────────────────────
AWS_ACCESS_KEY_ID=            # Geliştirmede: minioadmin
AWS_SECRET_ACCESS_KEY=        # Geliştirmede: minioadmin
AWS_REGION=eu-central-1
AWS_S3_BUCKET_NAME=studyos-dev
AWS_S3_ENDPOINT_URL=          # Geliştirmede: http://localhost:9000 | Prod: boş bırak

# ─── AI (Sprint-2.4) ────────────────────────────────────
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
AI_PROVIDER=null              # null | gemini | openai | claude
AI_MODEL=
AI_FALLBACK_PROVIDER=null
# Ayrıntı: docs/deployment.md

# ─── Firebase (FCM) ─────────────────────────────────────
FIREBASE_PROJECT_ID=
FIREBASE_PRIVATE_KEY_ID=
FIREBASE_PRIVATE_KEY=         # Firebase Console > Service Account
FIREBASE_CLIENT_EMAIL=
FIREBASE_CLIENT_ID=

# ─── E-posta (SMTP) ─────────────────────────────────────
SMTP_HOST=smtp.gmail.com      # Veya başka SMTP sağlayıcı
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@studyos.com
SMTP_FROM_NAME=StudyOS

# ─── Sentry ─────────────────────────────────────────────
SENTRY_DSN=                   # Sentry.io > Projeden alınır

# ─── CORS ───────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# ─── Rate Limiting ──────────────────────────────────────
RATE_LIMIT_PER_MINUTE=60
AUTH_RATE_LIMIT_PER_MINUTE=10
```

### 4.2 Flutter Ortam Değişkenleri

Flutter'da gizli değerler `--dart-define` ile derleme zamanında verilir. `lib/core/constants/` altında sabit dosyası ile yönetilir.

```
# Derleme komutu örneği:
flutter run \
  --dart-define=API_BASE_URL=http://localhost:8000/api/v1 \
  --dart-define=SENTRY_DSN=

# .env.flutter.example
API_BASE_URL=http://localhost:8000/api/v1
SENTRY_DSN=
FIREBASE_ANDROID_API_KEY=      # google-services.json'dan
FIREBASE_IOS_API_KEY=          # GoogleService-Info.plist'ten
```

---

## 5. Bağımlılık Planlaması

### 5.1 Flutter Bağımlılıkları

```yaml
# pubspec.yaml — üretim bağımlılıkları
dependencies:
  flutter:
    sdk: flutter

  # ─── State Management ───────────────────────────────
  flutter_riverpod: ^2.5.x      # Seçim: Meeting-006; derleme zamanı tip güvenliği
  riverpod_annotation: ^2.3.x   # Kod üretimi ile boilerplate azaltma

  # ─── Networking ────────────────────────────────────
  dio: ^5.x                     # HTTP istemci; interceptor, retry, timeout
  retrofit: ^4.x                # Dio üzeri type-safe API istemci üretimi

  # ─── Local Database ─────────────────────────────────
  drift: ^2.x                   # Seçim: Meeting-006; SQLite üzeri type-safe ORM
  sqlite3_flutter_libs: ^0.5.x  # Native SQLite bağlamaları

  # ─── Navigation ────────────────────────────────────
  go_router: ^14.x              # Flutter resmi router; deep link, guard desteği

  # ─── Secure Storage ────────────────────────────────
  flutter_secure_storage: ^9.x  # JWT refresh token güvenli depolama

  # ─── Notifications ─────────────────────────────────
  firebase_core: ^3.x           # Firebase temel paketi
  firebase_messaging: ^15.x     # FCM push notification
  firebase_analytics: ^11.x     # Firebase Analytics

  # ─── Monitoring ────────────────────────────────────
  sentry_flutter: ^8.x          # Crash ve hata takibi

  # ─── UI Yardımcıları ───────────────────────────────
  cached_network_image: ^3.x    # Görsel önbellekleme
  fl_chart: ^0.x                # İstatistik grafikleri (S-14)
  intl: ^0.19.x                 # Türkçe tarih/sayı formatı
  gap: ^3.x                     # SizedBox alternatifi; daha okunabilir boşluk
  loading_animation_widget: ^1.x # Loading animasyonları

  # ─── Utilities ─────────────────────────────────────
  freezed_annotation: ^2.x      # Immutable model sınıfları
  json_annotation: ^4.x         # JSON serileştirme anotasyonları
  uuid: ^4.x                    # UUID üretimi
  logger: ^2.x                  # Geliştirme loglama

dev_dependencies:
  # Kod üretimi
  build_runner: ^2.x
  riverpod_generator: ^2.x
  drift_dev: ^2.x
  freezed: ^2.x
  json_serializable: ^6.x
  retrofit_generator: ^8.x

  # Test
  flutter_test:
    sdk: flutter
  mocktail: ^1.x
  integration_test:
    sdk: flutter
```

**Bağımlılık Gerekçeleri:**

| Paket | Gerekçe |
|-------|---------|
| `flutter_riverpod` | Meeting-006 kararı; derleme zamanı güvenliği, az boilerplate |
| `dio` | Interceptor ile JWT yenileme otomasyonu; retry mekanizması |
| `drift` | Meeting-006 kararı; olgun, type-safe, SQLAlchemy ile uyumlu SQL paradigması |
| `go_router` | Flutter resmi çözümü; deep link ve auth guard desteği |
| `flutter_secure_storage` | Refresh token'ı keychain/keystore'da saklar |
| `freezed` | Immutable model; eşitlik, kopyalama, JSON otomasyonu |

---

### 5.2 FastAPI (Python) Bağımlılıkları

```toml
# pyproject.toml
[project]
name = "studyos-backend"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
  # ─── Web Framework ────────────────────────────────
  "fastapi>=0.115",           # Async REST API framework
  "uvicorn[standard]>=0.32", # ASGI sunucu; websocket + http2

  # ─── ORM ve Veritabanı ────────────────────────────
  "sqlalchemy>=2.0",          # Meeting-006 kararı; async ORM
  "alembic>=1.14",            # Şema migration yönetimi
  "asyncpg>=0.30",            # PostgreSQL async sürücüsü

  # ─── Veri Doğrulama ───────────────────────────────
  "pydantic>=2.9",            # Request/response şema doğrulama
  "pydantic-settings>=2.6",   # Ortam değişkeni yönetimi (BaseSettings)

  # ─── Kimlik Doğrulama ─────────────────────────────
  "python-jose[cryptography]>=3.3",  # JWT üretme ve doğrulama
  "passlib[bcrypt]>=1.7",            # Şifre hashing (bcrypt)

  # ─── E-posta ──────────────────────────────────────
  "fastapi-mail>=1.4",        # SMTP e-posta gönderme

  # ─── AWS S3 ───────────────────────────────────────
  "boto3>=1.35",              # AWS S3 ve MinIO istemcisi

  # ─── AI ───────────────────────────────────────────
  "google-generativeai>=0.8", # Gemini 2.5 Flash SDK

  # ─── Firebase (FCM) ───────────────────────────────
  "firebase-admin>=6.5",      # Push notification gönderme

  # ─── Rate Limiting ────────────────────────────────
  "slowapi>=0.1",             # FastAPI rate limiter

  # ─── Monitoring ───────────────────────────────────
  "sentry-sdk[fastapi]>=2.x", # Hata takibi

  # ─── Utilities ────────────────────────────────────
  "python-multipart>=0.0.9",  # Form ve dosya upload desteği
  "httpx>=0.28",              # Async HTTP istemci (test ve dış çağrı)
]

[project.optional-dependencies]
dev = [
  # Test
  "pytest>=8.x",
  "pytest-asyncio>=0.24",
  "pytest-cov>=6.x",
  "httpx>=0.28",               # TestClient için

  # Linting ve Formatlama
  "ruff>=0.8",                 # Linter + formatter (flake8 + black + isort)
  "mypy>=1.13",                # Statik tip kontrolü

  # Tip Stub'ları
  "types-passlib",
  "boto3-stubs[s3]",
]
```

**Bağımlılık Gerekçeleri:**

| Paket | Gerekçe |
|-------|---------|
| `sqlalchemy>=2.0` | Meeting-006 kararı; async desteği, Alembic entegrasyonu |
| `asyncpg` | SQLAlchemy async ile PostgreSQL için en hızlı sürücü |
| `pydantic-settings` | `.env` dosyasını otomatik yükler, tip güvenliği sağlar |
| `python-jose` | JWT standartlarına tam uyum; RS256 desteği (gelecek) |
| `passlib[bcrypt]` | bcrypt work factor 12 ile güvenli şifre hash |
| `slowapi` | FastAPI middleware olarak çalışır; Redis backend ile uyumlu |
| `ruff` | flake8 + black + isort yerine tek araç; 10–100x daha hızlı |

---

## 6. Ortam Kurulum Adımları

### Adım 1 — Depo Klonlama

```
git clone https://github.com/[org]/StudyOS.git
cd StudyOS
```

### Adım 2 — Ortam Değişkenlerini Hazırlama

```
cp .env.example .env
# .env dosyasını düzenle — gerçek değerleri gir
```

### Adım 3 — Docker Servisleri Başlatma

```
docker compose up -d postgres minio
```

### Adım 4 — Backend Kurulumu

```
cd backend/
uv sync                           # Bağımlılıkları yükle
uv run alembic upgrade head       # Migration'ları uygula
uv run python scripts/seed_db.py  # (opsiyonel) Test verisi yükle
uv run uvicorn app.main:app --reload
```

### Adım 5 — Flutter Mobil Kurulumu

```
cd mobile/
flutter pub get
flutter run
```

### Adım 6 — Flutter Web Kurulumu

```
cd web/
flutter pub get
flutter run -d chrome
```

---

## Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|-------|-------|-----------|
| 1.0 | 2026-07-06 | İlk sürüm — Meeting-008 |
| 1.1 | 2026-07-17 | Sprint-2.9 — Achievement seed migration `h4c5d6e7f8a9`; Flutter `features/achievements` |
