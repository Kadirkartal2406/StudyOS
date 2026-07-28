# StudyOS — Deployment Notları

**Belge Durumu:** Aktif  
**Sürüm:** 1.0  
**Oluşturuldu:** 2026-07-16 — Meeting-022 (Sprint-2.4)  
**Dil:** Türkçe

---

## AI / LLM ortam değişkenleri

API anahtarları **yalnızca sunucu `.env`** üzerinden yönetilir. Mobil istemciye key gönderilmez / loglanmaz.

| Değişken | Açıklama | Örnek |
|----------|----------|-------|
| `AI_PROVIDER` | Varsayılan sağlayıcı | `null` \| `gemini` \| `openai` \| `claude` |
| `AI_MODEL` | Model adı (boş = provider default) | `gemini-2.0-flash` |
| `AI_TEMPERATURE` | 0–1 | `0.7` |
| `AI_MAX_TOKENS` | Maks çıktı token | `1024` |
| `AI_TIMEOUT_SECONDS` | HTTP timeout | `30` |
| `AI_RETRY_COUNT` | Geçici hata retry | `2` |
| `AI_RATE_LIMIT_PER_MINUTE` | Rezerv (uygulama seviyesi) | `20` |
| `AI_FALLBACK_PROVIDER` | Primary fail → (B1) | `null` |
| `GEMINI_API_KEY` | Google AI | |
| `OPENAI_API_KEY` | OpenAI | |
| `ANTHROPIC_API_KEY` | Claude | |

**Güvenlik**

- Key’leri loglama, exception mesajına gömme, Flutter AI Settings’e koyma.
- Production’da `AI_PROVIDER=null` ile başlayıp key doğrulandıktan sonra geçiş önerilir.
- Debug telemetry yalnızca `DEBUG=true` iken `/ai/settings` yanıtında (key değerleri değil, varlık bayrakları).

---

## Backend deploy checklist (özet)

1. PostgreSQL + Alembic `upgrade head`
2. `.env` secrets (JWT, DB, AI keys)
3. `uvicorn` / container health: `GET /api/v1/health`
4. AI smoke: `AI_PROVIDER=null` ile chat; key varsa tek provider denemesi

**Ücretsiz beta:** [Render + Neon](deployment/render-neon.md) (`render.yaml` + `backend/Dockerfile`).

---

## Streaming

`POST /api/v1/ai/chat/stream` şu an **501 stub**. Gerçek SSE sonraki sprint.
