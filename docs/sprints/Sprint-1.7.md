# Sprint-1.7 — Study Plan ↔ Pomodoro ↔ Session History Integration

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-015  
**Kapsam:** Activity event log, session history/detail, plan→Pomodoro CTA, Dashboard gerçek aktiviteler, finish sonrası refresh

---

## Amaç

Mevcut Study Plan, Pomodoro, Session, Dashboard ve Statistics modüllerini uçtan uca bağlamak; yeni büyük modül eklemeden entegrasyonu tamamlamak.

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| A2 | Yeni `Activity` tablosu; event tipleri: session_started/paused/resumed/completed, plan_completed |
| B1 | Finish yalnızca plan progress yazar; otomatik `completed` yok |
| C2 | Plan kartında ayrı **Çalışmaya Başla** (mevcut **Başlat** korunur) |
| D1 | History `running` / `paused` / `completed` filtreleri; abandoned yok |
| E1 | Plan adı araması JOIN + ILIKE |

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| Activity model + migration + repo + service | ✅ |
| Session start/pause/resume/finish + plan complete → Activity | ✅ |
| History: plan/status/q filtreleri + `GET /{id}` + plan_title | ✅ |
| Dashboard `recent_activities` | ✅ |
| Unit testler | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| Plan kartı “Çalışmaya Başla” → setContext + /pomodoro | ✅ |
| Finish → invalidate dashboard / statistics / studyPlan | ✅ |
| Session History + Detail ekranları | ✅ |
| RecentActivityCard gerçek veri | ✅ |
| Quick action: Oturum Geçmişi | ✅ |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 101 passed |
| `ruff check` | All checks passed |
| `mypy app` | Success |
| `flutter analyze` | No issues found |
| `flutter test` | 65 passed |

---

## Bilinen Sınırlamalar

- Session History ekranı bottom nav'da yok; Dashboard quick action / derin link ile açılır.
- Finish sonrası history provider invalidate edilmiyor (circular import önlendi); ekran açılınca yeniden yüklenir.
- Activity metadata şeması henüz versiyonlanmadı (JSONB serbest).

---

## Bir Sonraki Sprint Önerisi

Bildirimlerin Activity'ye bağlanması, plan kartından otomatik Pomodoro start, veya Teacher Analytics timeline.
