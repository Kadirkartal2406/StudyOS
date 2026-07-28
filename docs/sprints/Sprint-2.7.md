# Sprint-2.7 — Adaptive Study Planner

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-17  
**Toplantı:** Meeting-025  
**Kapsam:** Rule-based haftalık plan taslağı + saklanan `reason` + Explain (LLM yalnızca açıklar) + Accept → StudyPlan + Flutter wizard + dashboard  
**Feature:** S-07 → MVP (S-16 alias/deprecated)

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | `planner_drafts` + JSONB `plan_payload` |
| B1 | `/api/v1/planner/*` |
| C1 | Feature-matrix **S-07 → MVP**; S-16 alias/deprecated |
| D1 | `POST /generate`, `GET /{id}`, `POST /{id}/accept`, `POST /{id}/explain` |
| E1 | Accept → N `StudyPlan` (haftanın günleri) |
| F1 | StudyPlan `source=planner` + `planner_draft_id` |
| G3 | Accept çakışması → 409 unless `force=true` |
| H1 | `target_exam` = ExamType |
| I2 | Body `target_net` primary; Goal hint okunur |
| J1 | Yetersiz veri → fallback TYT-benzeri dersler |
| K1 | Kaynak eşlemesi title/subject contains |
| L1 | Ayrı Explain endpoint |
| M1 | Memory: yalnızca `category=preference` |
| N1 | Activity `planner_generated` + `planner_accepted` |
| O1 | Dashboard `planner_summary` |
| P1 | LLM Explain + Null fallback |
| Q1 | Goal oluşturulmaz |

**Ek not:** Her öneri maddesi için kısa `reason` (AI rationale) draft’ta saklanır.
Explain / Dashboard / Chat yeniden üretim yapmadan okur. LLM plan üretmez.

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `alembic upgrade head` | `f2a3b4c5d6e7` |
| `pytest` | **161 passed** |
| `flutter analyze` | error yok (info/warning) |
| `flutter test` | **113 passed** |

---

## Bilinen Sınırlamalar

- LLM plan üretmez (bilinçli).
- Goal create yok (Q1).
- FCM yok (local `plannerReady` only).
- Yeni istatistik endpoint’i yok.
- AI Chat henüz planner rationale’ı otomatik inject etmez (alan hazır).
