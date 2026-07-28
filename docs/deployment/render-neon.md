# Render + Neon (StudyOS API)

Ücretsiz beta için: **Neon** (Postgres) + **Render** (FastAPI).

## A) Neon (veritabanı) — 5 dk

1. https://neon.tech → hesap aç → **Create project**
   - Name: `studyos`
   - Region: Frankfurt / EU (Render ile aynı bölge tercihen)
2. Dashboard → **Connection string** → **URI** kopyala  
   Örnek:
   `postgresql://user:pass@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require`
3. Not et — Render’a yapıştıracaksın.  
   Uygulama `postgresql://` veya `postgres://` gelse bile otomatik `+asyncpg` + SSL’e çevirir.

## B) GitHub

Kod Render’a GitHub üzerinden gider:

```powershell
cd "c:\Users\kadir\OneDrive\Masaüstü\StudyOS"
git status
# commit + push (senin remote’una)
```

`render.yaml`, `backend/Dockerfile`, `backend/requirements.txt` repoda olmalı.

## C) Render (API) — 10 dk

### Seçenek 1 — Blueprint (önerilen)

1. https://dashboard.render.com → **New** → **Blueprint**
2. StudyOS GitHub repo’sunu bağla
3. `render.yaml` algılanır → **Apply**
4. Environment’ta doldurman gerekenler (`sync: false`):

| Key | Değer |
|-----|--------|
| `DATABASE_URL` | Neon URI (yukarıdaki) |
| `ADMIN_BOOTSTRAP_PASSWORD` | `Kadir_kartal49` (veya yeni güçlü şifre) |
| `PUBLIC_APP_URL` | Deploy sonrası: `https://studyos-api.onrender.com` (gerçek hostname) |

JWT / APP_SECRET Render `generateValue` ile üretir.

### Seçenek 2 — Elle Web Service

1. **New** → **Web Service** → repo
2. Root Directory: `backend`
3. Runtime: **Docker** (Dockerfile)
4. Instance: **Free**
5. Health Check Path: `/api/v1/health`
6. Env vars (en azından):

```
APP_ENV=beta
DEBUG=false
DATABASE_URL=<neon-uri>
JWT_SECRET_KEY=<openssl rand -hex 32>
APP_SECRET=<openssl rand -hex 32>
COOKIE_SECRET=<openssl rand -hex 32>
SECRET_KEY=<aynı veya ayrı>
ADMIN_BOOTSTRAP_EMAIL=kadirkartal4921@icloud.com
ADMIN_BOOTSTRAP_PASSWORD=Kadir_kartal49
PUBLIC_APP_URL=https://<servis-adı>.onrender.com
ALLOWED_ORIGINS=*
AI_PROVIDER=null
ASSESSMENT_BOOKLET_SYNTHETIC=true
ENABLE_AUTO_BOOKLET=false
ENABLE_MIDNIGHT_SCHEDULER=false
ENABLE_CATCHUP=false
ENABLE_AI_WARMUP=false
ENABLE_BACKGROUND_AI=false
AWS_S3_ENDPOINT_URL=
```

## D) Doğrulama

Deploy bitince:

```text
https://<servis>.onrender.com/api/v1/health
https://<servis>.onrender.com/admin/
```

Admin: `kadirkartal4921@icloud.com` + bootstrap şifresi.

İlk istek **ücretsiz planda 30–60 sn** sürebilir (cold start).

## E) Mobil (App Distribution)

```powershell
.\scripts\distribute_android.ps1 `
  -ApiBaseUrl "https://<servis>.onrender.com/api/v1" `
  -FirebaseAppId "1:198461093012:android:e33d9fec662b26d3dab081" `
  -Groups "testers"
```

## Notlar

- Free Render uyur; Neon da idle’da suspend olabilir → ilk açılış yavaş.
- Gemini kullanacaksan Render’a `GEMINI_API_KEY` + `AI_PROVIDER=gemini` ekle.
- MinIO yok; dosya upload şimdilik opsiyonel.
- Migration’lar container start’ta `alembic upgrade head` ile çalışır.
