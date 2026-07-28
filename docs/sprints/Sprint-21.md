# Sprint 21 — Release Candidate (RC1)

**Durum:** 🚧 In Progress (Feature Freeze)  
**Tür:** Release Sprint  
**Tarih:** 2026-07-22  
**Sürüm:** `0.21.0-rc1`  
**Önkoşul:** Sprint 1–20 ✅  

---

## Feature Freeze

Yeni AI / Decision / Assessment / Quiz / Notebook / Planner motoru **yasak**.  
İzinli: polish, bugfix, analytics, feedback, test, performans.

---

## Modül durumu

| ID | Konu | Durum |
|----|------|-------|
| RC.1 | UX Audit | 🚧 checklist ile devam |
| RC.2 | Performance | ✅ Coach/WS duplicate azaltıldı |
| RC.3 | Cache Audit | 🚧 |
| RC.4 | API Audit | 🚧 envelope + unhandled 500 |
| RC.5 | Design Audit | 🚧 |
| RC.6 | Accessibility | 🚧 |
| RC.7 | Analytics | ✅ `/beta/analytics/*` + mobile bus |
| RC.8 | Crash / Error | ✅ backend + Flutter global handlers |
| RC.9 | Beta Feedback | ✅ `/beta/feedback` + `/feedback` ekranı |
| RC.10 | Beta Checklist | ✅ `Sprint-21-Beta-Checklist.md` |

---

## API (RC)

| Method | Path |
|--------|------|
| POST | `/beta/analytics/track` |
| POST | `/beta/analytics/batch` |
| POST | `/beta/feedback` |

Migration: `s21_rc_beta_ops`

---

## Sonrası

Kapalı beta → Sprint 22+ feedback → v1.0 genişleme.

Detaylı smoke: [Sprint-21-Beta-Checklist.md](./Sprint-21-Beta-Checklist.md)
