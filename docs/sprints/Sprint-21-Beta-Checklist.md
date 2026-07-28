# Sprint 21 — Beta Checklist & Smoke (RC1)

**Sürüm:** `0.21.0-rc1`  
**Feature Freeze:** yeni AI/Decision/Assessment/Quiz/Notebook motoru yok.

---

## Kritik akışlar (manuel)

| # | Akış | Beklenen | OK |
|---|------|----------|----|
| 1 | Kayıt / giriş | Token + Today | ☐ |
| 2 | Onboarding | Exam + dersler | ☐ |
| 3 | Active Exam switch | Scope değişir, feed güncellenir | ☐ |
| 4 | Today | Next Action + Koç kartı | ☐ |
| 5 | Subject → Topic Work Surface | Primary + Kaynak özeti | ☐ |
| 6 | Explain | Metin + (varsa) citation / follow-up | ☐ |
| 7 | Topic Quiz | Üret → çöz → sonuç | ☐ |
| 8 | Assessment overview | Progress + koç özeti | ☐ |
| 9 | Daily / branch assessment | Start → submit | ☐ |
| 10 | Knowledge reindex | Kaynak özeti güncellenir | ☐ |
| 11 | Journey | Haftalık yansıma + timeline | ☐ |
| 12 | Geri bildirim | `/feedback` gönderilir | ☐ |
| 13 | Loading / empty / error | Boş/hata durumları kullanıcı dostu | ☐ |

---

## RC audit notları

### RC.2 Performance
- Coach `timeline` artık `today()` çağırmıyor.
- Work Surface CoachService.today çağırmıyor (Dashboard SSOT).

### RC.7 Analytics
- `POST /beta/analytics/track` (+ batch)
- Mobile: `app_open`, `today_viewed`, `coach_viewed`, `feedback_sent`

### RC.8 Crash
- Backend: unhandled `Exception` → log + 500 envelope
- Mobile: `FlutterError` + `runZonedGuarded` + `PlatformDispatcher.onError`

### RC.9 Feedback
- `POST /beta/feedback`
- Mobile: `/feedback`

---

## Dağıtım öncesi

- [ ] `alembic upgrade head` (`s21_rc_beta_ops`)
- [ ] Backend health `/api/v1/health`
- [ ] Flutter `API_BASE_URL` beta ortamına
- [ ] Smoke tablo tamam
- [ ] Bilinen kritik bug yok
