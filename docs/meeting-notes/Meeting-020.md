# Meeting-020 — Sprint-2.2 AI Coach Chat

**Tarih:** 2026-07-16  
**Katılımcı AI:** Cursor Grok 4.5  
**Oturum Hedefi:** Context-aware AI Coach chat mimarisi (NullAIProvider)  
**Durum:** Tamamlandı

## Yapılanlar

- Backend: Conversation/Message, Context/Prompt katmanı, chat API, provider stubs
- Flutter: `ai_chat` (liste + sohbet), quick action → `/ai-chat`
- Docs: Sprint-2.2, api §2.14c, database §1.11d, feature-matrix S-15 G1 notu

## Alınan Kararlar

- A1, B1, C1, D1, E1, F2, G1 (öneriler onaylı uygulandı)

## Oluşturulan / Güncellenen Dosyalar

### Backend (yeni)
- `models/conversation.py`, schemas, repositories
- `services/ai/context_builder.py`, `prompt_builder.py`, `prompt_templates.py`
- `services/chat_service.py`, `api/v1/ai_chat.py`
- `providers/ai/gemini|openai|claude_provider.py` (stub)
- migration `f6a7b8c9d0e1`
- tests: prompt unit + chat integration

### Backend (güncellenen)
- `providers/ai/base.py`, `router.py`, `config.py`, `constants.py`, `models/__init__.py`

### Flutter (yeni)
- `lib/features/ai_chat/**`
- tests: model, repository, conversations widget

### Flutter (güncellenen)
- `api_endpoints.dart`, `app_router.dart`, quick actions, AI recommendation card

### Dokümantasyon
- `docs/sprints/Sprint-2.2.md`, `docs/meeting-notes/Meeting-020.md`
- api-design, database-design, software-architecture, feature-matrix

## Açık Sorular

- Gerçek Gemini ne zaman? Streaming zorunlu mu?

## Bir Sonraki Adım

GeminiProvider HTTP + API key doğrulama.
