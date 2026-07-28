# Sprint 17 — M17.1 Multi-Exam Audit

**Tarih:** 2026-07-22  
**Durum:** ✅ Audit + P0 düzeltmeler uygulandı  

---

## SSOT

| Katman | Mekanizma |
|--------|-----------|
| DB | `students.active_exam_type` |
| Resolve | `LearningProfileService.resolve_active_exam_type` |
| Switch | `PATCH /learning-profile/active-exam` + `ActiveExamSwitcher` |

---

## Yüzey tablosu (önce → sonra)

| Yüzey | Önce | Sonra |
|-------|------|-------|
| Profile / Subjects list | ✅ Active | ✅ |
| Dashboard my_subjects | ✅ | ✅ |
| Dashboard today_plans | ❌ tümü | ✅ Active katalog isimleri |
| Dashboard last exam | ❌ tümü | ✅ `exam_type=active` |
| Next Action katalog | ❌ tüm konular | ✅ Active subject_codes |
| Learning Feed / Insights | ❌ tümü | ✅ subject_codes filtresi |
| Journey days_remaining | ❌ Primary | ✅ Active (fallback Primary) |
| Quiz generate | ❌ exam_type yok | ✅ Active default (BE+mobile) |
| Exam list | ❌ tümü | ✅ Active filtre |
| Question list | ❌ tümü | ✅ Active filtre |
| Add exam / goal / question defaults | ❌ Primary | ✅ Active |
| Adaptive planner defaults | ❌ Primary | ✅ Active |
| Subject Hub off-exam deep link | ❌ açık | ✅ soft-guard 404 |
| Switch invalidation | ⚠️ kısmi | ✅ dashboard, exam, stats, journey, plan, revision, hub… |
| Mobile `activeSubjects` YKS | ❌ `yks_` prefix | ✅ `tyt_`/`ayt_`/`yks_` |
| Statistics overview (pomodoro vb.) | ❌ global | 📋 P1 (bilinçli bırakıldı) |
| Revisions dashboard counts | ❌ global | 📋 P1 |
| Goals weekly (exam_type filter) | ⚠️ | 📋 P1 |
| Explain prompt exam context | ❌ | 📋 P2 |
| StudyPlan `subject_code` kolonu | ❌ | 📋 P2 (migration yok) |

---

## P0 düzeltmeler (bu tur)

### Backend
- `dashboard_service.py` — active resolve erken; plans / exam summary / catalog / feed scoped
- `learning_intelligence_service.py` — `home_feed` / `home_insights` `subject_codes`
- `exam_service.dashboard_summary` — `exam_type` param
- `topic_quiz_service.generate` — Active default
- `journey_progress` — Active target için `days_remaining`
- `get_subject_hub` — Active soft-guard

### Mobile
- `ActiveExamSwitcher` — geniş invalidation
- `activeSubjects` YKS prefix fix
- Exam / Question list Active filtre
- Quiz / Add exam / goal / question / planner → Active defaults

---

## P1 / P2 (sonraki M17 maddeleri)

1. Statistics / Journey metrics Active subject_code scope
2. Goals list + weekly_summary `exam_type == active`
3. Revision due list Active subject name/code
4. Explain prompt’a `active_exam_type`
5. Study plan’a `subject_code` (migration — sprint kuralı dışında; şimdilik isim filtresi)

---

## Manuel test checklist

- [ ] KPSS → YKS switch: Derslerim, Today feed, son deneme anında değişiyor
- [ ] Quiz üret: prompt/kayıtta aktif sınav tipi
- [ ] Off-exam subject deep link → 404 / boş
- [ ] Deneme listesi sadece aktif sınav
- [ ] Uygulamayı kapat-aç: aktif sınav korunuyor (M17.7)
