# Sprint-1.8 — Notifications, Widgets & OS Integration

**Belge Durumu:** Tamamlandı  
**Tarih:** 2026-07-16  
**Toplantı:** Meeting-016  
**Kapsam:** Local notifications + FCM token stub, notification settings, Android Medium widget (cache-fed), platform abstractions, feature-matrix S-30 → MVP

---

## Amaç

OS entegrasyon katmanını (bildirim, widget, shortcuts) ortak `PlatformService` / `WidgetService` mimarisiyle kurmak; gerçek FCM push ve iOS Live Activities’i sonraki sprintlere bırakmak.

---

## Alınan Kararlar

| Kod | Karar |
|-----|--------|
| P3 | Medium Android widget + notification settings + stub’lar |
| A1 | Local notification; FCM token altyapısı; gerçek push sonraki sprint |
| B1 | Notification Inbox yok; yalnızca Settings |
| C1 | `notification_preferences` ayrı tablo (User JSON yok) |
| D2 | iOS Runner yok; Live Activity interface/stub |
| E1 | Feature matrix S-30 → Zorunlu / MVP |
| F | Widget Flutter cache’ten beslensin; backend’e bağımlı olmasın |
| G | Platform/Widget servisleri WearOS/watchOS için genişletilebilir |

---

## Kapsam

### Backend

| Bileşen | Durum |
|---------|-------|
| `NotificationPreference` model + migration | ✅ |
| `GET/PUT /notification-settings` | ✅ |
| `PUT /notification-settings/fcm-token` | ✅ |
| Unit + integration testler | ✅ |

### Flutter

| Bileşen | Durum |
|---------|-------|
| Platform / Notification / Widget / Shortcut soyutlamaları | ✅ |
| LocalNotificationService + FCM stub token | ✅ |
| Notification Settings ekranı + provider | ✅ |
| Dashboard OS Integration kartı | ✅ |
| Android Medium widget (`StudyOsMediumWidgetProvider`) | ✅ |
| Dashboard/Pomodoro → widget cache feed (F) | ✅ |
| Quick Actions shortcuts | ✅ |
| StubLiveActivityService (D2) | ✅ |

### Docs

| Bileşen | Durum |
|---------|-------|
| api-design §2.12 notification-settings | ✅ |
| database-design §1.14b | ✅ |
| feature-matrix S-30 → MVP | ✅ |
| Sprint-1.8 / Meeting-016 | ✅ |

---

## Test Sonuçları

| Kontrol | Sonuç |
|---------|-------|
| `pytest` | 104 passed |
| `ruff check` (notification slice) | All checks passed |
| `mypy` (notification slice) | OK |
| `flutter analyze` (değişen paketler) | No issues found |
| `flutter test` | 73 passed |

---

## Bilinen Sınırlamalar

- Gerçek FCM push yok; token stub kaydı var.
- iOS Live Activities / ActivityKit implementasyonu yok (Mac ortamına bırakıldı).
- Widget yalnızca Android Medium; iOS Widget Extension sonraki sprint.
- Notification Inbox yok.
- Profil sekmesi geçici olarak Bildirim Ayarları’na yönlendirir.

---

## Bir Sonraki Sprint Önerisi

Gerçek FCM push + Notification Inbox; iOS Widget/Live Activities (Mac); WearOS iskeleti.
