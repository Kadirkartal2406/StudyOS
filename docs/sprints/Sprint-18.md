# Sprint 18 — Assessment Engine & Daily Challenge (LOS §11)

**Durum:** ✅ Uygulama tamam (smoke / QA)  
**Tür:** Feature Sprint (LOS §11 — Initial Calibration & Continuous Assessment)  
**Tarih:** 2026-07-22  
**Önkoşul:** Sprint 1–17 ✅ (Active Exam SSOT, Topic Quiz, Evidence/Confidence)  

---

## Sprint Goal

StudyOS kullanıcıdan “Başlangıç seviyen nedir?” diye sormaz.  
Sistemi kullanarak kullanıcının seviyesini **kendisi öğrenir**.

Bu sprint:

- ilk seviye kalibrasyonu
- günlük mini denemeler
- günlük branş soruları
- tahmini puan / sıralama (istatistiksel)
- Assessment Evidence

katmanını ekler.

**Ürün hissi:** “ben seni tanıyorum” — yeni ekran yığını değil, LOS’un ilk gerçek başlangıç kalibrasyonu.

---

## LOS Prensibi

Assessment **Decision değildir**.  
Assessment **Learning değildir**.  
Assessment, LOS için yeni bir **Sense Layer** oluşturur.

```
Assessment
  ↓
Evidence
  ↓
Confidence
  ↓
Observation
  ↓
Policy
  ↓
Today
```

Assessment asla Living Plan / Today / Decision **üretmez**.  
Yalnızca daha kaliteli Evidence üretir.

---

## Modül durumu

| ID | Konu | Durum |
|----|------|-------|
| M18.1 | Assessment models + migration | ✅ |
| M18.2 | Assessment start/submit + Evidence bridge | ✅ |
| M18.3 | Daily Challenge (günlük deneme) | ✅ |
| M18.4 | Branch Challenge (ders sorusu) | ✅ |
| M18.5 | Score estimation + same-exam ranking snapshot | ✅ |
| M18.6 | Today / Feed kartları | ✅ |
| M18.7 | Journey Assessment Progress | ✅ |
| M18.8 | Mobile yüzeyler (mevcut DS ile) | ✅ |

---

## Backend

### Servisler

- `assessment_service.py` — start/submit/overview/daily_bundle
- `assessment_repository.py`
- `score_estimation_service.py` — istatistiksel puan + peer rank

### Modeller / migration

- `AssessmentSession`, `AssessmentQuestion`, `DailyChallenge`, `EstimatedScoreSnapshot`
- Alembic: `s18_assessment_engine`

### Endpointler (`/assessment`)

| Method | Path |
|--------|------|
| GET | `/assessment` |
| POST | `/assessment/start` |
| GET | `/assessment/sessions/{id}` |
| POST | `/assessment/sessions/{id}/submit` |
| GET | `/assessment/daily-challenge` |
| POST | `/assessment/daily-challenge/start` |
| GET | `/assessment/estimated-score` |
| GET | `/assessment/ranking` |

Submit → Evidence ingest (`source=assessment`) → Confidence; Policy/Today motorları değişmez.

---

## Mobile

- `/assessment` — kalibrasyon overview
- `/assessment/daily/start` — günün denemesi
- `/assessment/branch/start` — branş / kalibrasyon start
- `/assessment/session/:id` — mevcut session
- Today feed deep link’leri + Journey Assessment Progress kartı

---

## LOS kuralları (sert)

| Yapılır | Yapılmaz |
|---------|----------|
| Evidence üretir | Decision üretmez |
| Confidence aggregate günceller | Living Plan değiştirmez |
| Active Exam scope | Tek deneme Plan mutasyonu |
| Mevcut Topic Quiz pipeline | Quiz engine rewrite |

---

## Yapılmayacaklar

- Sosyal leaderboard / arkadaş / PvP
- Gerçek ÖSYM sıralaması / resmi puan
- AI koç / flashcard / canlı sınav
- Quiz altyapısının sıfırdan yeniden yazımı

---

## Başarı Kriterleri

1. Kullanıcı ilk seviyesini testlerle belirleyebilir (zorunlu değil, branş branş).
2. Assessment sonuçları doğrudan Evidence Engine’e akar.
3. Confidence başlangıçta daha doğru kalibre edilir.
4. Günlük deneme + branş soruları **aktif sınava** göre oluşur.
5. Today Challenge kartlarını gösterir; Journey Assessment Progress gösterir.
6. Aynı sınav türüyle karşılaştırmalı istatistik (tahmini).
7. LOS zinciri (Evidence → Confidence → Observation → Policy → Today) bozulmaz.
