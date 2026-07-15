# StudyOS Backend

FastAPI REST API — `python 3.12+` `uv` `SQLAlchemy 2.0` `PostgreSQL`

## Kurulum

```bash
# Bağımlılıkları yükle
uv sync

# Geliştirme bağımlılıkları ile
uv sync --extra dev

# Uygulamayı başlat
uv run uvicorn app.main:app --reload --port 8000

# API Dokümantasyonu (geliştirmede)
# http://localhost:8000/api/docs
```

## Testler

```bash
uv run pytest
uv run pytest --cov=app --cov-report=term-missing
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
uv run mypy app/
```

## Yapı

```
app/
├── main.py          ← FastAPI uygulama fabrikası
├── api/             ← HTTP endpoint tanımları
├── core/            ← Konfigürasyon, güvenlik, exception'lar
├── database/        ← SQLAlchemy engine, session, migration
├── models/          ← ORM modelleri
├── schemas/         ← Pydantic request/response şemaları
├── repositories/    ← Veri erişim katmanı
├── services/        ← İş mantığı katmanı
├── middleware/       ← FastAPI middleware'leri
└── providers/       ← Dış servis adaptörleri (AI, S3, FCM)
```
