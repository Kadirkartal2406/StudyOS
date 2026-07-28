# Sprint-1.5 — Pomodoro (Study Session) Module

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-013  
**Kapsam:** Backend StudySession + Flutter Pomodoro ekranı + Dashboard entegrasyonu

---

## Amaç

Kullanıcı Pomodoro oturumu başlatıp duraklatıp bitirebilsin; oturum backend'e kaydedilsin; süre sonunda bildirim alsın; Dashboard ve StudyPlan ilerlemesi otomatik güncellensin.

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| `StudySession` modeli + Alembic migration | ✅ |
| Repository / Service / Schemas | ✅ |
| `POST /study-sessions/start\|pause\|resume\|finish` | ✅ |
| `GET /study-sessions/today\|history\|statistics` | ✅ |
| Dashboard: süre/soru → tamamlanmış oturumlardan | ✅ |
| Finish → bağlı StudyPlan artımlı güncelleme | ✅ |
| Unit + integration testler | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| `features/study_session` Clean Architecture | ✅ |
| PomodoroScreen (geri sayım, halka, kontroller) | ✅ |
| Preset 25/5, 50/10, 90/15 + özel süre | ✅ |
| `flutter_local_notifications` (ses/titreşim/zamanlanmış) | ✅ |
| Bottom nav + Dashboard quick actions bağlantısı | ✅ |
| Model / repository / provider / widget testler | ✅ |

---

## Alınan Kararlar

1. **Tek aktif oturum:** İkinci `start` → `409 CONFLICT`.
2. **StudyPlan:** Finish artımlı `completed_*` yazar; `planned` → `in_progress`; otomatik `completed` yok.
3. **Dashboard:** `today_study_minutes` / `today_questions_solved` → `StudySession` (plansız oturum dahil).
4. **Mola:** İstemci fazı; backend yalnızca focus `start/pause/resume/finish` yönetir.
5. **Model:** `user_id` FK + `study_plan_id` nullable (Student/Subject henüz yok) — `[ONAY GEREKTİRİR]` dokümante edildi.
6. **API path:** `/study-sessions/*` (eski taslak `/sessions` yerine).

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 89 passed |
| `ruff check` | All checks passed |
| `mypy app` | Success |
| `flutter analyze` | No issues found |
| `flutter test` | 59 passed |

---

## Bilinen Sınırlamalar

- Arka plan zamanlayıcısı OS kısıtlarına tabidir (`exactAllowWhileIdle`); bazı Android OEM'lerde gecikebilir.
- Plan'dan Pomodoro'ya `study_plan_id` ile derin bağlantı UI'da henüz otomatik (setContext API hazır; plan kartından tek dokunuşla bağlama sonraki iyileştirme).
- FCM push (sunucu bildirimleri) bu sprintte yok — yalnızca yerel bildirim.
- `Student` / `Subject` FK migrasyonu ertelendi.

---

## Bir Sonraki Sprint Önerisi

İstatistik ekranı (S-14) veya plan kartından doğrudan Pomodoro başlatma + oturum geçmişi UI.
