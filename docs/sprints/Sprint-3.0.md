# Sprint-3.0 — Learning Profile & Intelligent Onboarding

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-17  
**Toplantı:** Meeting-028  
**Kapsam:** S-02/S-03 + S-34 Learning Profile — Student hub, multi-exam, subject catalog, onboarding (soft), journey_stage, Context/Dashboard additive  
**Feature:** S-34 Learning Profile (S-02/S-03 aktivasyon)

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A1 | `students` = Learning Profile hub |
| B1 | `exam_targets` 1:N multi-exam |
| C1 | `subject_catalog` + `user_subjects` dual-write (FK migration yok) |
| D1 | 6 adımlı onboarding |
| D2 | Soft skip (hard gate yok) |
| E1 | Hedef asıl `exam_targets`; Goal tip redesign 3.1 |
| F1 | Planner profile-default + wizard override |
| G1 | Baseline level (self-assess / unknown) |
| H1 | S-02/S-03 + S-34 |
| I1 | LLM plan/hedef/ders üretmez |
| J1 | Memory opsiyonel (yazılmadı) |
| K1 | Dashboard `journey_progress` additive |
| L1 | Scope = 3.0 foundation |
| M1 | `journey_stage` RuleEngine; LLM yalnızca yorumlar |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `alembic upgrade head` | `i5d6e7f8a9b0` |
| `pytest` | **175 passed** |
| `flutter test` | **124 passed** |
| `flutter analyze` | exit 0 (`--no-fatal-infos`) |

---

## Bilinen Sınırlamalar

- Goal ürün tipleri (net/puan/sıralama) → 3.1
- Subject sert FK → yok (C1)
- Full adaptive re-plan loop → 3.2
- S-15 proaktif koç derinliği → sonraki sprint
- Memory seed yazılmadı (J1)
