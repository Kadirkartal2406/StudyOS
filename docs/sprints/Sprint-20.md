# Sprint 20 — Adaptive AI Coach (LOS §13)

**Durum:** ✅ Uygulama tamam (smoke / QA)  
**Tür:** Experience Sprint (Adaptive Coaching)  
**Tarih:** 2026-07-22  
**Önkoşul:** Sprint 1–19 ✅  

---

## Sprint Amacı

Coach = deneyim katmanı. Decision / Planner / Confidence **yeniden yazılmaz**.  
Mevcut Next Action + Insights + Assessment + Knowledge + Behavioral **yorumlanır**.

---

## Modül durumu

| ID | Konu | Durum |
|----|------|-------|
| M20.1 | `coach_service` | ✅ |
| M20.2 | Daily Coach Message (Dashboard `coach_today`) | ✅ |
| M20.3 | Weekly Reflection (Journey) | ✅ |
| M20.4 | Win Detection | ✅ |
| M20.5 | Smart Follow-up (Explain) | ✅ |
| M20.6 | Habit Intelligence | ✅ |
| M20.7 | Knowledge Coach hint | ✅ |
| M20.8 | Assessment Coach summary | ✅ |
| M20.9 | Explain Evolution (follow-ups) | ✅ |
| M20.10 | Coach Timeline (Journey) | ✅ |

---

## API (`/coach`)

| Method | Path |
|--------|------|
| GET | `/coach/today` |
| GET | `/coach/weekly` |
| GET | `/coach/timeline` |
| GET | `/coach/assessment-summary` |

Dashboard: `coach_today` alanı  
Work Surface: `coach_headline` / `coach_body`  
Assessment overview: `coach_summary` / rank / critical / next  
Explain: `coach_follow_ups`

---

## Mimari

- Coach karar vermez; `build_next_action` SSOT’unu okur
- LLM zorunlu değil (template builder)
- Tek “Koçun” sesi: Today / Journey / WS / Assessment

---

## Stratejik not

Sprint 20 sonrası **Sprint 21: Release Candidate** önerilir — özellik dondur, polish + feedback.

---

## Yapılmayanlar

- Yeni Decision / Confidence / Assessment / Knowledge / Quiz motoru
- Sosyal özellikler
