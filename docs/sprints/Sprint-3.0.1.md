# Sprint-3.0.1 — Product Consistency & Learning Profile Integration

**Durum:** Tamamlandı  
**Tür:** Product Polish (yeni büyük özellik yok)  
**Bağımlılık:** Sprint-3.0 Learning Profile

## Amaç

Learning Profile uygulamanın **Single Source of Truth** kaynağı olur.
Primary Exam tüm create/edit/list ekranlarında varsayılan context’tir.

## Kapsam

| Hedef | Sonuç |
|-------|--------|
| 1 Primary Exam SSOT | Question/Exam/Goal create+edit, Planner, Revision, Dashboard, Subjects |
| 2 Subjects ekranı | Metrik kartları (soru, süre, accuracy, last study/revision, progress) |
| 3 Dashboard Derslerim | En çok / en zayıf / idle / bugün sayısı |
| 4–5 Subject filtresi | Primary exam katalogundan; KPSS↔YKS karışmaz |
| 6 Profil değişimi | `learningProfileProvider` invalidate → ekranlar yenilenir |
| 7 Tek provider | `learningProfileProvider` + extension helpers |
| 8 Docs | Bu dosya + Meeting-029 + feature-matrix notu |

## Migration

**Yok.** Metrikler mevcut question/session/revision aggregatelerinden additive hesaplanır.

## API (additive)

- `UserSubjectRead` + metrics alanları
- `DashboardResponse.subjects_summary`

## Korunan kurallar

- LLM plan/hedef/ders üretmez
- RuleEngine korunur
- exam_targets 1:N multi-exam bozulmaz
