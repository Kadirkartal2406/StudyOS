# StudyOS — Sprint Yol Haritası

**Son Güncelleme:** 2026-07-22  
**Referans:** `docs/product/learning-operating-system.md`  
**Kural:** Her sprint bağımsız test edilebilir bir deneyim üretir. Bir sprint bitmeden diğerine geçilmez.

---

## Tamamlanan Sprintler (Özet)

| Sprint | Konu | Durum |
|--------|------|-------|
| Sprint 1–3 | Temel backend, auth, subjects, sessions | ✅ |
| Alignment Sprint 1–2 | Today Engine, Next Action card | ✅ |
| Alignment Sprint 3 | Topic Work Surface, deep-link | ✅ |
| Alignment Sprint 4 | Living Plan dili hizalaması | ✅ |
| LOS M1 | Evidence Engine (TopicEvidence model + service) | ✅ |
| LOS M2 | Confidence Engine (TopicConfidence + recalculate) | ✅ |
| LOS M3 | Observation Mode (gate-based state machine) | ✅ |
| LOS M4 | Policy Decision Engine (RuleEngine → policy) | ✅ |
| LOS M5 | Today Engine Refactor (policy → dashboard) | ✅ |
| LOS M6 | Living Plan Adapt (MUTATE_PLAN loop) | ✅ |
| LOS M7 | Behavioral Memory (chronotype, tempo, receptivity) | ✅ |
| Sprint 5 | Çalışma oturumu tam döngü (session → evidence) | ✅ |
| Sprint 6 | Soru kaydı ↔ topic / Work Surface performans | ✅ |
| Sprint 7 | Revision ↔ LOS + overdue days Next Action | ✅ |
| Sprint 8 | Today gerçek veri, icon, streak strip | ✅ |
| Sprint 9 | Living Plan öneri → kabul / red | ✅ |
| Sprint 10 | Journey Surface | ✅ |
| Sprint 11 | Exam Experience Pack | ✅ |
| Sprint 12 | AI Explain (tek /explain endpoint) | ✅ |
| Sprint 13 | Notification Decision Service | ✅ |
| Sprint 14 | Topic Quiz Generation (LLM → Quality Gate → Evidence) | ✅ |
| Sprint 15 | Learning Intelligence & Personalized Study Feed | ✅ |
| Sprint 16 | Design System & Product Polish | ✅ |
| Sprint 17 | Beta Readiness & Core Product Hardening | ✅ CLOSED |
| Sprint 18 | Assessment Engine & Daily Challenge (LOS §11) | 📋 Plan (Onay Bekliyor) |

---

## Detay (Sprint 5–13)

Aşağıdaki maddeler implementasyon referansıdır; durumları ✅ Tamamlandı.

---

### Sprint 5 — Çalışma Oturumu: Tam Döngü
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-5.md`

### Sprint 6 — Soru Kaydı ↔ Topic Entegrasyonu
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-6.md`

### Sprint 7 — Revision Engine ↔ LOS
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-7.md`

### Sprint 8 — Today Engine: Gerçek Veri Gösterimi
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-8.md`

### Sprint 9 — Living Plan: Öneri → Kabul → Adaptasyon
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-9.md`

### Sprint 10 — Journey Surface
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-10.md`

### Sprint 11 — Exam Experience Pack
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-11.md`

### Sprint 12 — AI Explain (LLM Karar Değil, Açıklar)
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-12.md`

### Sprint 13 — Akıllı Bildirimler
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-13.md`

### Sprint 14 — Topic Quiz Generation (LLM → Evidence)
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-14.md`
(NotebookLM adapter sonraki sprint; Quality Gate provider-bağımsız)

### Sprint 15 — Learning Intelligence & Personalized Study Feed
**Durum:** ✅ Tamamlandı — bkz. `docs/sprints/Sprint-15.md`
Ürün sprinti: mevcut LOS/AI verisini görünür kılmak. Yeni Decision motoru yok.

### Sprint 16 — Design System & Product Polish
**Durum:** ✅ Tamamlandı (çekirdek) — bkz. `docs/sprints/Sprint-16.md`
UI/UX only. Audit: `docs/sprints/Sprint-16-UI-Audit.md`

### Sprint 17 — Beta Readiness & Core Product Hardening
**Durum:** ✅ CLOSED — bkz. `docs/sprints/Sprint-17.md`

M17.1 Multi-Exam · M17.2 Resource · M17.3 Completion Audit.  
Active Exam SSOT.

### Sprint 18 — Assessment Engine & Daily Challenge (LOS §11)
**Durum:** 📋 Plan (Onay Bekliyor) — bkz. `docs/sprints/Sprint-18.md`

İlk kalibrasyon + günlük deneme/branş + tahmini puan/sıralama + Assessment Evidence.  
Sense layer; Decision/Living Plan üretmez. Sprint 14 Quiz altyapısı yeniden kullanılır.

---

## Sprint Sıralaması ve Bağımlılıklar

```
… → 14 (Quiz) → 15 → 16 → 17 (Beta) ✅ → 18 (Assessment & Daily Challenge) 📋
```

---

## Her Sprint'in Dosyası

- `docs/sprints/Sprint-5.md` … `Sprint-16.md` (✅)
- `docs/sprints/Sprint-16-UI-Audit.md`
- `docs/sprints/Sprint-17.md` (✅ CLOSED)
- `docs/sprints/Sprint-17-M17.1-Multi-Exam-Audit.md`
- `docs/sprints/Sprint-17-M17.2-Resource-Audit.md`
- `docs/sprints/Sprint-17.3-Completion-Audit.md`
- `docs/sprints/Sprint-18.md` (📋 Onay Bekliyor)
