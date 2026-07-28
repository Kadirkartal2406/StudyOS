# Sprint-3.1.C.x — Subject Catalog & Exam Structure Redesign

**Durum:** Tamamlandı  
**Tür:** Domain model (Subject Catalog)  
**Bağımlılık:** Sprint-3.1.C Subject Hub  
**Migration:** Yok  
**Feature:** S-38 (catalog redesign)

## Domain ilkesi

Subject Catalog yalnızca UI listesi değil; Topic System, Flashcards, Resources, Question Bank, AI Coach ve Adaptive Planner için çekirdek domain modelidir. Kimlik = `subject_code`.

## Özet

| Alan | Sonuç |
|------|--------|
| TYT | Paket yok; bireysel dersler (Türkçe…Biyoloji) |
| YKS | TYT herkese ortak; AYT `branch` ile (sayisal/ea/sozel/dil) |
| KPSS | Lisans/Önlisans/Ortaöğretim aynı dersler; GY/GK yok |
| YDS | Vocabulary…Listening (genişletilmiş) |
| Hub | `TYT Matematik` / `KPSS Türkçe` (compose) |
| Dashboard | Kısa ders adı |

## Teknik

- [`subject_catalog_seed.py`](../../backend/app/services/ai/subject_catalog_seed.py) — SSOT + `codes_for_exam`
- `ensure_catalog_synced()` — upsert, Alembic yok
- `_seed_subjects_for_exams(targets)` — branch-aware
- Onboarding Flutter: YKS alan + KPSS program adımı → `exam_targets.branch`

## Dışarıda

- EB / Alan Bilgisi / ÖABT
- FK / subject_code normalize migration
- Topic / Flashcard motorları
