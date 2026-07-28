# Sprint-2.8 — Revision & Spaced Repetition Engine

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-17  
**Toplantı:** Meeting-026  
**Kapsam:** S-11 Yanlış Defteri + S-12 SRS (SM-2 lite) + saklanan reason/difficulty + Explain + Flutter + dashboard  
**Feature:** S-11 + S-12 → MVP

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | S-11 + S-12 birlikte MVP |
| B1 | `/api/v1/revisions` |
| C1 | Feature-matrix S-11/S-12 → MVP |
| D1 | Normalize items + schedules + reviews |
| E1 | SM-2 lite |
| F1 | Manuel + kural seed (QR) |
| G1 | Eşikli exam seed |
| H1 | StudyPlan’a yazılmaz |
| I1 | Soft archive (`deleted_at`) |
| J1 | generate + explain ayrı |
| K1 | Dashboard `revision_summary` |
| L1 | Activity created/reviewed/completed |
| M1 | Memory sadece oku |
| N1 | Local due + prefs toggle |
| O1 | Goal yok |
| P1 | LLM Explain + Null |
| Q1 | ContextBuilder `revisions` |
| R2 | statistics + heatmap |
| S1 | Flutter `features/revision` |

**Ek notlar:** `source_type`, `reason`, `difficulty` (1–5); LLM difficulty/interval’a dokunmaz.

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `alembic upgrade head` | `g3b4c5d6e7f8` |
| `pytest` | **167 passed** |
| `flutter test` | **117 passed** |

---

## Bilinen Sınırlamalar

- Tekil soru metni/OCR yok (batch QR seed).
- Flashcard (S-25) yok.
- FCM / inbox yok.
- StudyPlan’a otomatik yazma yok.
- Goal / MemoryWriter yok.
