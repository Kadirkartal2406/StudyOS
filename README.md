# StudyOS

AI destekli öğrenci çalışma ve kurum yönetim ekosistemi.

## Proje Bileşenleri

| Bileşen | Teknoloji | Konum |
|---------|-----------|-------|
| Öğrenci Mobil Uygulaması | Flutter (iOS + Android) | `mobile/` |
| Kurumsal Web Paneli | Flutter Web | `web/` |
| Backend API | FastAPI (Python) | `backend/` |
| Dokümantasyon | Markdown | `docs/` |

## Hızlı Başlangıç

### Gereksinimler

- Flutter SDK 3.27+
- Python 3.12+
- uv (Python paket yöneticisi)
- Docker Desktop (PostgreSQL + MinIO için)
- Git 2.45+

### Kurulum

```bash
# 1. Depoyu klonla
git clone https://github.com/[org]/StudyOS.git
cd StudyOS

# 2. Ortam değişkenlerini hazırla
cp .env.example .env
# .env dosyasını düzenle

# 3. Altyapı servislerini başlat
docker compose up -d postgres minio

# 4. Backend'i başlat
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# 5. Flutter Mobil
cd ../mobile
flutter pub get
flutter run

# 6. Flutter Web
cd ../web
flutter pub get
flutter run -d chrome
```

## Dokümantasyon

| Belge | Açıklama |
|-------|---------|
| [Proje Anayasası](docs/project/ai-rules.md) | Proje kuralları ve kısıtlar |
| [Özellik Matrisi](docs/planning/feature-matrix.md) | MVP kapsamı |
| [Teknoloji Kararları](docs/architecture/technology-decisions.md) | Stack seçimleri |
| [Yazılım Mimarisi](docs/architecture/software-architecture.md) | Sistem tasarımı |
| [Veritabanı Tasarımı](docs/architecture/database-design.md) | Veri modeli |
| [API Tasarımı](docs/architecture/api-design.md) | REST API sözleşmesi |
| [Kodlama Standartları](docs/development/coding-standards.md) | Geliştirme kuralları |
| [Git Workflow](docs/development/git-workflow.md) | Dal stratejisi |

## Lisans

[Lisans bilgisi — belirlenecek]
