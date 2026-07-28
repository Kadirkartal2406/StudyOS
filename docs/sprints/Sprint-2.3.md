# Sprint-2.3 — AI Memory Engine

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-021  
**Kapsam:** Memory model/API + rule-based Retriever/Writer + Flutter `memory` + privacy  
**Embedding / pgvector:** Yok

---

## Amaç

AI Chat’i uzun dönem bellek ile beslemek: kural tabanlı yazma/okuma, kullanıcı kontrolü
(export / clear / disable), ContextBuilder + PromptBuilder entegrasyonu.

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | Embedding kolonu yok; `metadata.embedding_ready` rezerv |
| B1 | Güncelleme `PATCH /memory/{id}` |
| C1 | `ai_memory_enabled` preference ile kapatma |
| D1 | MemoryWriter yalnızca AI Chat kullanıcı mesajından |
| E2 | Full: Writer + Flutter UI + privacy + tests/docs |
| F1 | S-15 notu “Memory Engine foundation”; yeni matrix ID yok |
| G1 | Arama = ILIKE + kategori filtresi |

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| `memories` tablosu + migration | ✅ |
| `ai_memory_enabled` (notification_preferences) | ✅ |
| MemoryRetriever / MemoryWriter | ✅ |
| ContextBuilder + PromptBuilder wire | ✅ |
| ChatService → Writer (D1) | ✅ |
| `/memory` CRUD + search + privacy | ✅ |
| Unit + integration testler | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| `features/memory` Clean Architecture | ✅ |
| Liste / ara / ekle / düzenle / sil | ✅ |
| Privacy: enable, export, clear | ✅ |
| AI Chat → Bellek girişi | ✅ |
| Model / repository / widget testler | ✅ |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 140 passed |
| `flutter analyze` (memory) | No issues found |
| `flutter test` | 100 passed |

---

## Bilinen Sınırlamalar

- Gerçek embedding / semantic search yok.
- Writer yalnızca chat mesajından (Goal/Question kaynakları yok — D2 seçilmedi).
- Arama ILIKE; Türkçe morfoloji yok.

---

## Bir Sonraki Sprint Önerisi

Gemini HTTP adaptörü veya hafif embedding + pgvector (ayrı onay).
