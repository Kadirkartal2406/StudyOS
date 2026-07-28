# Meeting-033 — Sprint-3.1.C.x Subject Catalog Redesign

**Tarih:** 2026-07-19  
**Konu:** Subject Catalog & Exam Structure (ders odaklı domain model)

## Kararlar

1. Catalog uzun vadeli domain modeli (Topic/Flashcards/Resources/QBank/AI/Planner temeli).
2. TYT paket yok; bireysel dersler. TYT tüm YKS alanlarında ortak; yalnızca AYT branch’e göre değişir.
3. KPSS Lisans/Önlisans/Ortaöğretim aynı ders listesi; GY/GK ürün dili değil.
4. `subject_code` canonical (`tyt_matematik`, `kpss_turkce`…). `branch` onboarding’de zorunlu (YKS/KPSS).
5. Dashboard kısa ad; Hub başlığı `TYT Matematik` / `AYT Matematik` / `KPSS …`.
6. Migration yok; `ensure_catalog_synced` + seed.

## Teslim

Kod + Sprint-3.1.C.x + feature-matrix/api notları + pytest / flutter test.
