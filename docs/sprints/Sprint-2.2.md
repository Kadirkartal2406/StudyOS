# Sprint-2.2 — AI Coach Chat (Context-Aware)

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-020  
**Kapsam:** Conversation/Message + Context/Prompt + NullAIProvider chat + Flutter `ai_chat`  
**Gerçek LLM:** Yok

---

## Amaç

Kullanıcıyla konuşabilen, Goal/Insight/Statistics bağlamını okuyan AI Coach chat mimarisini kurmak. Gerçek Gemini/OpenAI çağrısı yok; NullAIProvider şablon cevap üretir.

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | `POST /ai/chat` + conversations; `study-coach` eklenmez |
| B1 | Auth only; premium yok |
| C1 | NullAIProvider = context/şablon Türkçe cevap |
| D1 | `/ai-chat` sohbet; `/ai-coach` insights kalır |
| E1 | Conversation + Message tabloları |
| F2 | Full paket (stub providers, copy/retry/regenerate, stream-ready, tests/docs) |
| G1 | S-15 v1.1; chat foundation notu |

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| Conversation / Message + migration | ✅ |
| ContextBuilder / PromptBuilder / PromptTemplate | ✅ |
| NullAIProvider chat + Gemini/OpenAI/Claude stubs | ✅ |
| `POST /ai/chat`, conversations CRUD | ✅ |
| Unit + integration testler | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| `features/ai_chat` Clean Architecture | ✅ |
| Conversations + Chat screen, bubbles, typing | ✅ |
| Copy / Retry / Regenerate | ✅ |
| Quick action + AI kart → `/ai-chat` | ✅ |
| Model / repository / widget testler | ✅ |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 133 passed |
| `flutter analyze` (ai_chat) | No issues found |
| `flutter test` | 95 passed |

---

## Bilinen Sınırlamalar

- Gerçek LLM HTTP yok; stub provider’lar sabit mesaj döner.
- SSE streaming yok (stream method hazır).
- Premium / usage limiti yok.
- Memory/RAG/Voice yalnızca metadata rezervi.

---

## Bir Sonraki Sprint Önerisi

Gemini HTTP adaptörü + gerçek `AI_PROVIDER=gemini`, isteğe bağlı SSE.
