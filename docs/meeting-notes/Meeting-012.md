# Meeting-012 — Sprint-1.4 Study Plan Module

**Tarih:** 2026-07-16
**Katılımcı AI:** Claude Sonnet 5 (Thinking)
**Oturum Hedefi:** Kullanıcının günlük çalışma planını (StudyPlan) oluşturabileceği, düzenleyebileceği, başlatıp tamamlayabileceği veya atlayabileceği tam bir modülü — backend CRUD + durum geçişleri, Flutter Clean Architecture katmanları — geliştirmek; Dashboard'u placeholder veriden gerçek `StudyPlan` verisine geçirmek.
**Durum:** ✅ Tamamlandı

---

## Amaç

Sprint-1.3 (Dashboard) tamamlandığında `today_study_minutes`, `today_questions_solved`, `today_studied_topic` ve `daily_progress_percentage` alanları placeholder/varsayılan değer döndürüyordu; kullanıcı çalışma planı oluşturamıyordu. Bu oturumun amacı, StudyOS'un ilk gerçek üretkenlik modülünü — Study Plan — hem backend hem Flutter tarafında production kalitesinde geliştirmek ve Dashboard'u bu gerçek veriye bağlamaktı.

---

## Yapılan Geliştirmeler

- Ön hazırlık: `ai-rules.md`, `database-design.md`, `api-design.md` okundu; §1.9 StudyPlan'ın önceki taslağının (`StudyPlanItem`, `student_id`/`subject_id` FK'leri) `Student`/`Subject` modelleri implemente edilmediği için kullanılamayacağı belirlendi; sprint talebindeki alan listesi doğrultusunda flatter bir tasarım kararı `[ONAY GEREKTİRİR]` etiketiyle dokümante edildi.
- **Backend:** `StudyPlan` modeli (soft delete, status enum), Alembic migration, `StudyPlanRepository` (sahiplik + tarih filtresi + saat çakışması sorgusu), `StudyPlanService` (durum geçişi state machine'i, otomatik `order_index`), `/study-plans` router'ı (`CRUD` + `start`/`complete`/`skip`). `docs/architecture/database-design.md` §1.9 ve `docs/architecture/api-design.md` §2.6 güncellendi.
- **Dashboard Entegrasyonu:** `DashboardService` artık bugünün `StudyPlan` kayıtlarını okuyup `daily_study_goal_minutes`, `today_study_minutes`, `today_questions_solved`, `today_studied_topic`, `today_plan_count`, `completed_plan_count`, `today_plans` alanlarını gerçek veriden hesaplıyor. `docs/architecture/api-design.md` §2.16 güncellendi.
- **Flutter Domain/Data/Presentation:** `study_plan` feature'ı Clean Architecture ile kuruldu — 3 entity (`StudyPlanEntity`, `StudyPlanStatus`, framework'ten bağımsız `StudyTime` değer nesnesi), repository interface + implementasyon, 8 usecase, Riverpod `StudyPlanNotifier` (sealed state, tekil kart mutasyon göstergesi).
- **Flutter UI:** 5 widget (`StudyCard`, `StudyPlanTimeline`, `DailyProgress`, `StudyPlanEmptyState`, `DateSelector`) ve 3 ekran (`StudyPlanScreen` — Drag & Drop `ReorderableListView`, `AddStudyPlanScreen`, `EditStudyPlanScreen` — paylaşılan `StudyPlanForm`).
- **Router/Navigasyon:** `/study-plan`, `/study-plan/add`, `/study-plan/edit/:id` rotaları eklendi; `AppBottomNavBar` gerçek `currentIndex` ve Plan sekmesi yönlendirmesi aldı; Dashboard'daki "Çalışma Planı" hızlı işlem butonu artık gerçek ekrana gidiyor.
- Backend: `pytest` (70/70), `ruff check` (0 hata), `mypy app/` (0 hata, 46 dosya). Flutter: `flutter analyze` (0 sorun), `flutter test` (44/44).

---

## Oluşturulan Dosyalar

Bkz. `docs/sprints/Sprint-1.4.md` — "Oluşturulan Dosyalar" tablosu (backend: 8 dosya, Flutter: 22 dosya, dokümantasyon: 2 dosya).

## Güncellenen Dosyalar

Bkz. `docs/sprints/Sprint-1.4.md` — "Güncellenen Dosyalar" tablosu (9 backend, 7 Flutter, 2 mimari doküman).

## Silinen Dosyalar

Bu sprintte dosya silinmedi.

---

## Test Sonuçları

| Test | Sonuç |
|------|-------|
| `pytest` (backend) | ✅ 70/70 (37 mevcut + 33 yeni) |
| `ruff check .` | ✅ All checks passed! |
| `mypy app/` | ✅ 0 hata, 46 dosya |
| `flutter analyze` | ✅ No issues found! |
| `flutter test` (mobile) | ✅ 44/44 (17 mevcut + 27 yeni) |

---

## Alınan Kararlar

| Karar | Detay |
|-------|-------|
| `StudyPlan` tekil, düz tablo olarak implemente edildi **[ONAY GEREKTİRİR]** | `database-design.md` §1.9'daki önceki taslak (`StudyPlan` + `StudyPlanItem`, FK tabanlı `student_id`/`subject_id`) `Student`/`Subject` modelleri implemente edilmediği için kullanılamadı. Sprint-1.4 talebindeki alan listesi (`user_id` FK, düz `subject`/`topic` string) doğrudan uygulandı ve dokümantasyona işlendi. `Student`/`Subject` eklendiğinde FK'li yapıya migrasyon değerlendirilebilir. |
| Saat çakışması kontrolü veritabanı kısıtı değil, servis katmanında yapılıyor | PostgreSQL `EXCLUDE` kısıtı ek bir uzantı (`btree_gist`) gerektirirdi; servis katmanında basit aralık çakışma kontrolü "Basitlik önce gelir" ilkesiyle uyumlu ve yeterli. |
| Drag & Drop için ayrı bir reorder endpoint'i eklenmedi | Mevcut `PUT /study-plans/{id}` zaten `order_index` kabul ediyor; her sürükleme sonrası yalnızca değişen kalemler bu endpoint üzerinden güncelleniyor. |
| Flutter domain katmanında `TimeOfDay` yerine saf Dart `StudyTime` kullanıldı | Domain katmanının Flutter framework'ünden bağımsız olması ilkesiyle (`dashboard_entity.dart`'ta zaten belirtilen) tutarlı; dönüşüm yalnızca form/time picker sınırında yapılıyor. |
| `dio_exception_mapper.dart`'a `400 → ValidationException` eşlemesi eklendi | Backend'in özel `ValidationError`'ı (saat çakışması) `400` döner; önceden yalnızca `422` eşlenmişti. Tek satır eklemekle sınırlı, geriye dönük uyumlu bir genişletme. |
| `AppBottomNavBar`/`QuickActionsCard`'daki "Çalışma Planı" aksiyonu gerçek yönlendirmeye geçirildi | Sprint talebi gerçek ekranı açıkça istiyor; diğer placeholder sekmeler/butonlar (ilgili modülleri henüz yok) değiştirilmedi. |

---

## Karşılaşılan Problemler ve Çözümler

| # | Problem | Çözüm |
|---|---------|-------|
| 1 | Entegrasyon testleri `KeyError: 'data'` ile başarısız oluyordu. | `slowapi` rate limiter testler arası paylaşılan IP nedeniyle limiti aşıyordu; `tests/conftest.py`'a `autouse=True` `_reset_rate_limiter` fixture'ı eklendi. |
| 2 | `mypy`, saat çakışması kontrolünde `time \| None` için tip hatası veriyordu. | Yerel değişkenlere atama + `None` kontrolüyle tip daraltması sağlandı. |
| 3 | Oturumlar arası uzun boşluk sonrası Docker Desktop kapanmış, tüm backend testleri bağlantı hatasıyla başarısız oldu. | Docker Desktop yeniden başlatıldı, container'ların `healthy` durumu doğrulandı, testler tekrar çalıştırılıp 70/70 geçti (kod hatası değil, operasyonel bir durumdu). |
| 4 | Flutter Riverpod testlerinde provider'ın lazy oluşturulması, ilk `load()` çağrısının test beklemesinden sonra tetiklenmesine (yarış durumu) yol açtı. | `setUp`'ta notifier erkenden `container.read(...)` ile oluşturuldu; her testin ilk `await settle()`'ı gerçek ilk yüklemeyi bekleyebildi. |
| 5 | Widget testinde plan başlığı metni iki kez bulunuyordu. | `StudyPlanTimeline` saat aralığı tanımlı planların başlığını da gösterdiği için ikileniyordu; test verisi varsayılan olarak saat aralığı içermeyecek şekilde güncellendi. |

---

## Bilinen Eksikler

- Bir planın `study_date`'i Add/Edit formunda değiştirilemiyor (tarih, ekranda o an seçili güne sabit); başka bir güne taşımak için silip yeniden oluşturmak gerekiyor.
- Drag & Drop her değişen kalem için ayrı `PUT` isteği gönderiyor; günlük plan ölçeğinde sorun değil, çok büyük listelerde toplu reorder endpoint'i değerlendirilebilir.
- `integration_test/auth_flow_test.dart`, Meeting-010'da belgelenen Visual Studio Desktop C++ toolchain eksikliği nedeniyle hâlâ çalıştırılamıyor (bu sprintle ilgisiz, devam eden bir kısıt).
- Pomodoro oturumları (`StudySession`) henüz yok; Dashboard'daki süre/soru verileri yalnızca `StudyPlan.completed_*` alanlarından geliyor.

---

## Bir Sonraki Sprint

**Sprint-2 (öneri):** Pomodoro Oturumları modülü (`StudySession` — S-10) — `StudyPlan` ile ilişkilendirilebilir zamanlayıcı; oturum bitince ilgili plana `completed_minutes` eklenir. Ardından soru istatistikleri (`QuestionStatistics`) ve haftalık/aylık özet ekranları planlanabilir.
