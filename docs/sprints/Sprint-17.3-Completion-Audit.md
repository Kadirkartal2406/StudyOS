# Sprint 17.3 — Multi-Exam Completion Audit

**Durum:** ✅ CLOSED  
**Tür:** Audit + Refactor (yeni feature yok)  
**Tarih:** 2026-07-22  

Sprint 17 kapanışı. Active Exam SSOT tamamlandı.

---

## Tamamlanan

| Modül | Durum |
|-------|--------|
| M17.3.1 Statistics | ✅ Active `subject_codes` scope |
| M17.3.2 Revision | ✅ Active subject names filter |
| M17.3.3 Goals | ✅ Active default + list/weekly filter |
| M17.3.4 Explain | ✅ `active_exam_type` prompt context |
| M17.3.5 Analytics consistency | ✅ `resolve_active_scope()` SSOT helper |
| M17.3.6 Backend legacy | ✅ Primary defaults → Active |
| M17.3.7 Mobile legacy | ✅ revision/edit_goal/chip Active |
| M17.3.8 Cache invalidate | ✅ resources/notebook/work-surface |

---

## Ana değişiklikler

- `LearningProfileService.resolve_active_scope()`
- Statistics repo/service Active filtre
- Revision due/list/dashboard Active subject
- Goal create default + list/progress/weekly Active
- Planner defaults Active
- Explain + TopicAIContext `active_exam_type`
- Switcher invalidate genişletildi

---

## Bilinçli kalan (None kritik)

- `primary_exam_type` alanı profil/API’de **kimlik** olarak duruyor (Ana sınav etiketi); aggregate SSOT değil.
- Session’larda `subject_code` null olan eski kayıtlar Active filtrede görünmez.
