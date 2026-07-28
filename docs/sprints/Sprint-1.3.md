# Sprint-1.3 — Dashboard (Home Screen)

**Tarih:** 2026-07-15
**Sprint:** 1.3 (Meeting-011)
**Hedef:** Authentication sonrası kullanıcının gördüğü ilk gerçek ekranı (Dashboard) geliştirmek; boş/placeholder Home ekranını gerçek bir altyapıyla değiştirmek.
**Durum:** ✅ Tamamlandı

---

## Kapsam

`api-design.md`, `database-design.md`, `software-architecture.md` ve `coding-standards.md`'ye tam sadakatle:

- Backend: `GET /api/v1/dashboard` — kullanıcı adı, günlük hedef, bugünkü çalışma süresi/soru sayısı, günlük ilerleme yüzdesi, son giriş zamanı.
- Flutter: `DashboardEntity` → `DashboardRepository` → `DashboardProvider (Riverpod)` → `DashboardScreen` — Clean Architecture katmanları.
- Dashboard UI: karşılama + tarih, 4 kart (Bugünkü Hedef, Bugünkü Çalışma, Son Aktiviteler, Hızlı İşlemler), 5 sekmeli alt navigation (yalnızca Dashboard aktif).
- State management: `DashboardInitial` / `DashboardLoading` / `DashboardLoaded` / `DashboardError` — retry butonu ile hata yönetimi.
- Router: authentication sonrası yönlendirme `/home` → `/dashboard` olarak güncellendi; eski placeholder `HomeScreen` kaldırıldı.

**Bu sprintte geliştirilmeyenler (bilinçli olarak kapsam dışı):** AI, çalışma planı mantığı, Pomodoro mantığı, istatistik hesaplamaları, bildirimler. Bkz. Meeting-011 talimatı.

---

## Backend — Dashboard Endpoint

| Adım | Sonuç |
|------|-------|
| `GET /api/v1/dashboard` | `SuccessResponse[DashboardResponse]` — Bearer JWT ile korunur (`get_current_user`) |
| Alan adları | `first_name`, `daily_study_goal_minutes`, `today_study_minutes`, `today_questions_solved`, `today_studied_topic`, `daily_progress_percentage`, `last_login_at` — gelecekteki Student/StudyPlan/StudySession/QuestionStatistics modelleriyle uyumlu seçildi (sözleşme bozulmadan gerçek veriye geçiş) |
| Placeholder değerler | `daily_study_goal_minutes` = sabit varsayılan (120 dk, `app/core/constants.py`); `today_study_minutes`, `today_questions_solved` = 0; `today_studied_topic` = `null`; `daily_progress_percentage` = hesaplanan (şu an 0.0) |
| Gerçek veri | `first_name` ve `last_login_at` — `User` modelinden gerçek değer döner (placeholder değil) |
| Dokümantasyon | `docs/architecture/api-design.md` §2.16 eklendi (sürüm 1.0 → 1.1) |

---

## Flutter — Dashboard Data Layer & UI

| Katman | Dosya |
|--------|-------|
| Domain | `dashboard_entity.dart`, `dashboard_repository.dart` (interface) |
| Data | `dashboard_model.dart`, `dashboard_remote_datasource.dart`, `dashboard_repository_impl.dart` |
| Presentation (state) | `dashboard_state.dart` (sealed class), `dashboard_provider.dart` (Riverpod `StateNotifier`) |
| Presentation (UI) | `dashboard_screen.dart`, `dashboard_header.dart`, `daily_goal_card.dart`, `today_study_card.dart`, `recent_activity_card.dart`, `quick_actions_card.dart` |
| Ortak (shared) | `app_bottom_nav_bar.dart` (Material 3 `NavigationBar`, 5 sekme) |
| Yardımcı | `core/utils/date_time_helper.dart` (saat bazlı karşılama + Türkçe tarih formatı) |

Repository → Provider → UI akışı, mevcut `auth` feature'ındaki desenle (Riverpod `Provider`/`StateNotifierProvider` DI zinciri) birebir tutarlı kuruldu.

---

## Doğrulama

| Test | Sonuç |
|------|-------|
| `pytest` (backend, 37 test) | ✅ 37 passed (27 mevcut + 10 yeni: 7 servis unit, 3 endpoint entegrasyon) |
| `ruff check .` | ✅ All checks passed! |
| `mypy app/` | ✅ Success: no issues found in 40 source files |
| `flutter analyze` | ✅ No issues found! |
| `flutter test` (mobile, 17 test) | ✅ 17 passed (1 mevcut + 16 yeni: 6 `date_time_helper`, 3 `dashboard_model`, 2 `dashboard_repository`, 5 `dashboard_screen` widget) |
| Manuel E2E (canlı sunucu) | ✅ register → `GET /api/v1/dashboard` (200, doğru alanlar) → token'sız istek (401) → Swagger/OpenAPI şemasında `dashboard` tag'i doğrulandı |

---

## Oluşturulan Dosyalar

### Backend

| Dosya | Açıklama |
|-------|----------|
| `app/core/constants.py` | `DEFAULT_DAILY_STUDY_GOAL_MINUTES` — sihirli sayı önleme |
| `app/schemas/dashboard.py` | `DashboardResponse` |
| `app/services/dashboard_service.py` | `DashboardService` — placeholder/gerçek veri birleştirme mantığı |
| `app/api/v1/dashboard.py` | `GET /dashboard` endpoint'i |
| `tests/unit/test_dashboard_service.py` | 7 senaryo |
| `tests/integration/test_dashboard_endpoints.py` | 3 senaryo |

### Flutter

| Dosya | Açıklama |
|-------|----------|
| `lib/core/utils/date_time_helper.dart` | Saat bazlı karşılama + Türkçe tarih formatı |
| `lib/features/dashboard/domain/entities/dashboard_entity.dart` | Domain entity |
| `lib/features/dashboard/domain/repositories/dashboard_repository.dart` | Repository interface |
| `lib/features/dashboard/data/models/dashboard_model.dart` | JSON model + `toEntity()` |
| `lib/features/dashboard/data/datasources/dashboard_remote_datasource.dart` | `GET /dashboard` çağrısı |
| `lib/features/dashboard/data/repositories/dashboard_repository_impl.dart` | Repository implementasyonu |
| `lib/features/dashboard/presentation/providers/dashboard_state.dart` | Sealed state sınıfı |
| `lib/features/dashboard/presentation/providers/dashboard_provider.dart` | `DashboardNotifier` + DI provider'ları |
| `lib/features/dashboard/presentation/screens/dashboard_screen.dart` | Ana ekran |
| `lib/features/dashboard/presentation/widgets/dashboard_header.dart` | Karşılama + tarih |
| `lib/features/dashboard/presentation/widgets/daily_goal_card.dart` | Kart 1 |
| `lib/features/dashboard/presentation/widgets/today_study_card.dart` | Kart 2 |
| `lib/features/dashboard/presentation/widgets/recent_activity_card.dart` | Kart 3 |
| `lib/features/dashboard/presentation/widgets/quick_actions_card.dart` | Kart 4 |
| `lib/shared/widgets/app_bottom_nav_bar.dart` | Alt navigation (5 sekme) |
| `test/unit/date_time_helper_test.dart` | 6 senaryo |
| `test/unit/dashboard_model_test.dart` | 3 senaryo |
| `test/unit/dashboard_repository_test.dart` | 2 senaryo |
| `test/widget/dashboard_screen_test.dart` | 5 senaryo |

---

## Güncellenen Dosyalar

| Dosya | Değişiklik |
|-------|------------|
| `backend/app/api/router.py` | `dashboard` router'ı `/dashboard` prefix'i ile bağlandı |
| `docs/architecture/api-design.md` | §2.16 `/api/v1/dashboard` eklendi; yetki matrisine satır eklendi; sürüm 1.0 → 1.1 |
| `mobile/lib/core/constants/api_endpoints.dart` | `dashboard` endpoint sabiti eklendi |
| `mobile/lib/core/router/app_router.dart` | `/home` → `/dashboard` rota adı/yönlendirmesi; `DashboardScreen` bağlandı |
| `mobile/integration_test/auth_flow_test.dart` | Eski `HomeScreen` metinleri (`Auth Çalışıyor!`, `Merhaba, Test`) yerine Dashboard içeriği (`Bugünkü Hedef`) doğrulanıyor; `/home` → `/dashboard` |

## Silinen Dosyalar

| Dosya | Neden |
|-------|-------|
| `mobile/lib/features/auth/presentation/screens/home_screen.dart` | Sprint-1.2B placeholder'ı; `DashboardScreen` ile tamamen değiştirildi |

---

## Mimari Kararlar

| Karar | Gerekçe |
|-------|---------|
| Dashboard alan adları gelecekteki modellerle (Student/StudyPlan/StudySession/QuestionStatistics) uyumlu seçildi | "API tasarımını ileride bozmadan geliştir" talimatı — gerçek veri hesaplaması eklendiğinde response şeması (Flutter sözleşmesi) değişmeyecek |
| `today_studied_topic` alanı backend response'una eklendi | Meeting-011 talimatının §1 (backend alanları) listesinde açıkça yer almasa da, §3 (UI Kart 2) "Çalışılan Konu" göstermeyi zorunlu kılıyor; veri olmadığı için `null` placeholder döner, Flutter tarafı bunu "Henüz konu çalışılmadı" olarak gösterir. Talimatlar arası bu küçük tutarsızlık, "gerçek analiz yok, placeholder yeterli" ilkesiyle çözüldü |
| Dashboard UI, sabit koyu renk paleti yerine `Theme.of(context).colorScheme` kullanır | Mevcut `AppTheme`/`AppColors` altyapısı (Material 3, `ColorScheme.fromSeed`) daha önce hiçbir ekranda kullanılmıyordu (auth ekranları sabit koyu renk hardcode ediyor). Görev "Dark Mode uyumlu olacak" şartını gerektirdiği için Dashboard, sistem temasına göre otomatik light/dark geçiş yapan doğru (ve ilk) ekran oldu; mevcut tema bozulmadı, ilk kez doğru kullanıldı |
| `/home` rotası `/dashboard` olarak yeniden adlandırıldı | Rota artık gerçekten Dashboard'a karşılık geliyor; isimlendirme netliği için `coding-standards.md` §4.1 (anlamlı, kaynak temelli endpoint/route adları) ile uyumlu |
| Çıkış (logout) butonu Dashboard AppBar'ına taşındı | Profil ekranı bu sprintte henüz yok (placeholder); oturumu kapatmak için erişilebilir bir yol gerekliydi. Profil modülü eklendiğinde bu buton oraya taşınabilir |
| Tablet/geniş ekran için içerik `maxWidth: 640` ile sınırlandı | Kart tabanlı düzenin geniş ekranlarda aşırı gerilmesini önler; "Tablet görünümü bozulmayacak" şartı için basit ve bakımı kolay bir çözüm |
| `DashboardService.get_dashboard()` senkron (async değil) | Şu an hiçbir I/O (DB sorgusu) içermiyor; gereksiz `async` tanımı `coding-standards.md` §1 "Basitlik önce gelir" ilkesine aykırı olurdu. Gerçek veri modelleri eklendiğinde `async` yapılacak |

---

## Bilinen Sınırlamalar / Sonraki Sprint'e Bırakılanlar

- `today_study_minutes`, `today_questions_solved`, `today_studied_topic`, `daily_progress_percentage` gerçek veriden hesaplanmıyor — `StudyPlan`/`Session`/`QuestionStatistics` modülleri (Sprint-2+) eklendiğinde `DashboardService` güncellenecek.
- Alt navigation'daki Plan/Pomodoro/İstatistik/Profil sekmeleri ve Hızlı İşlemler kartındaki 4 buton yalnızca "Yakında" placeholder bildirimi gösterir; gerçek yönlendirme yok (talimat gereği).
- Profil ekranı henüz yok; çıkış butonu geçici olarak Dashboard AppBar'ında.
- `integration_test/auth_flow_test.dart` bu ortamda hâlâ çalıştırılamıyor (Meeting-010'da belgelenen Visual Studio Desktop C++ toolchain eksikliği devam ediyor); metinler yeni Dashboard içeriğine göre güncellendi ancak gerçek buton tıklamalarıyla doğrulanamadı.

---

## Bir Sonraki Adım

1. Visual Studio Desktop C++ workload kurulduğunda `integration_test/auth_flow_test.dart` çalıştırılıp doğrulanmalı.
2. Sprint-2 planlaması: Çalışma Planı modülü (`StudyPlan`), Pomodoro oturumları (`Session`), soru istatistikleri — bunlar tamamlandığında `DashboardService` placeholder değerleri gerçek hesaplamalarla değiştirilmeli.
3. Profil ekranı geliştirildiğinde çıkış butonu oraya taşınmalı.
