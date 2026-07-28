# Sprint-1.4 — Study Plan Module

**Tarih:** 2026-07-16
**Sprint:** 1.4 (Meeting-012)
**Hedef:** Kullanıcının günlük çalışma planını (StudyPlan) yönetebileceği tam bir modül geliştirmek — backend CRUD + durum geçişleri, Flutter Clean Architecture katmanları, Dashboard'un gerçek plan verisine geçişi.
**Durum:** ✅ Tamamlandı

---

## Kapsam

`ai-rules.md`, `database-design.md`, `api-design.md`, `software-architecture.md`, `coding-standards.md`'ye tam sadakatle:

- Backend: `StudyPlan` modeli (soft delete, status enum), `StudyPlanRepository`, `StudyPlanService`, `/study-plans` endpoint'leri (CRUD + `start`/`complete`/`skip`).
- Backend: `DashboardService` artık gerçek `StudyPlan` verisini kullanır (placeholder kaldırıldı).
- Flutter: `study_plan` feature'ı — Clean Architecture (`domain`/`data`/`presentation`), 3 ekran (`StudyPlanScreen`, `AddStudyPlanScreen`, `EditStudyPlanScreen`), 5 widget (`StudyCard`, `StudyPlanTimeline`, `DailyProgress`, `StudyPlanEmptyState`, `DateSelector`), Drag & Drop sıralama.
- Router ve Dashboard entegrasyonu: alt navigasyon "Plan" sekmesi ve "Hızlı İşlemler" kartındaki "Çalışma Planı" butonu artık gerçek ekrana yönlendirir.

---

## Backend — Study Plan Modülü

| Adım | Sonuç |
|------|-------|
| Model | `StudyPlan` — `user_id` FK, düz `subject`/`topic` string alanları, `status` enum (`planned`/`in_progress`/`completed`/`skipped`), soft delete (`deleted_at`) |
| Migration | `c68d9085b762_add_study_plans_table.py` — `study_plans` tablosu, `user_id`/`study_date` indeksleri |
| Repository | `StudyPlanRepository` — sahiplik filtresi, tarih filtresi, saat çakışması sorgusu, `order_index` hesaplama, soft delete |
| Service | `StudyPlanService` — CRUD, saat çakışması doğrulaması, otomatik `order_index` ataması, durum geçişi state machine'i (`planned → in_progress → completed`/`skipped`, terminal durumdan çıkış yok) |
| Endpoint'ler | `GET/POST /study-plans`, `GET/PUT/DELETE /study-plans/{id}`, `PATCH /study-plans/{id}/start`\|`/complete`\|`/skip` |
| Validasyon | Başlık boş olamaz, soru/dakika > 0, bitiş saati > başlangıç saati, saat çakışması `400`, terminal durum geçişi `409` |
| Dokümantasyon | `docs/architecture/database-design.md` §1.9 ve `docs/architecture/api-design.md` §2.6 güncellendi (bkz. "Mimari Kararlar") |

### Dashboard Entegrasyonu

`DashboardService.get_dashboard()` artık bugünün `StudyPlan` kayıtlarını okuyup şu alanları gerçek veriden hesaplar: `daily_study_goal_minutes` (plan varsa `estimated_minutes` toplamı, yoksa `DEFAULT_DAILY_STUDY_GOAL_MINUTES`), `today_study_minutes`, `today_questions_solved`, `today_studied_topic` (devam eden veya en son tamamlanan planın konusu), `today_plan_count`, `completed_plan_count`, `today_plans` (tam liste).

---

## Flutter — Study Plan Modülü

| Katman | Dosya |
|--------|-------|
| Domain (entities) | `study_plan_entity.dart`, `study_plan_status.dart`, `study_time.dart` (domain katmanını Flutter framework'ünden bağımsız tutmak için `TimeOfDay` yerine kullanılan saf Dart değer nesnesi) |
| Domain (repository + usecases) | `study_plan_repository.dart` (interface), 8 usecase: get/create/update/delete/start/complete/skip/reorder |
| Data | `study_plan_model.dart`, `study_plan_remote_datasource.dart`, `study_plan_repository_impl.dart` |
| Presentation (state) | `study_plan_state.dart` (sealed class — `Initial`/`Loading`/`Loaded`/`Error`, `mutatingPlanId` ile tekil kart yükleniyor göstergesi), `study_plan_provider.dart` (`StudyPlanNotifier`) |
| Presentation (widgets) | `study_card.dart`, `study_plan_timeline.dart`, `daily_progress.dart`, `study_plan_empty_state.dart`, `date_selector.dart`, `study_plan_form.dart` (Add/Edit arasında paylaşılan form) |
| Presentation (screens) | `study_plan_screen.dart` (Drag & Drop `ReorderableListView`, gün seçici, "Bugün" butonu), `add_study_plan_screen.dart`, `edit_study_plan_screen.dart` |

**Drag & Drop:** `ReorderableListView.onReorder` → `StudyPlanNotifier.reorder()` — yeni sıralamayı önce yerel olarak uygular (optimistic update), sadece `order_index`'i değişen kalemleri `ReorderStudyPlanUsecase` ile backend'e kaydeder (mevcut `PUT /study-plans/{id}` üzerinden — ayrı bir reorder endpoint'i yok).

**Router:** `/study-plan`, `/study-plan/add`, `/study-plan/edit/:id` rotaları eklendi. `AppBottomNavBar` artık `currentIndex` parametresi alır ve Dashboard/Plan sekmeleri gerçek rotalara yönlendirir; `QuickActionsCard`'daki "Çalışma Planı" butonu `/study-plan`'a yönlendirir.

---

## Doğrulama

| Test | Sonuç |
|------|-------|
| `pytest` (backend, 70 test) | ✅ 70 passed (37 mevcut + 33 yeni: 18 servis unit, 15 endpoint entegrasyon; ayrıca dashboard testleri StudyPlan verisiyle güncellendi) |
| `ruff check .` | ✅ All checks passed! |
| `mypy app/` | ✅ Success: no issues found in 46 source files |
| `flutter analyze` | ✅ No issues found! |
| `flutter test` (mobile, 44 test) | ✅ 44 passed (17 mevcut + 27 yeni: 5 `study_plan_model`, 6 `study_plan_repository`, 9 `study_plan_provider`, 9 `study_plan_screen` widget) |

---

## Oluşturulan Dosyalar

### Backend

| Dosya | Açıklama |
|-------|----------|
| `app/models/study_plan.py` | `StudyPlan`, `StudyPlanStatus` |
| `app/repositories/study_plan_repository.py` | `StudyPlanRepository` |
| `app/schemas/study_plan.py` | `StudyPlanCreate`, `StudyPlanUpdate`, `StudyPlanCompleteRequest`, `StudyPlanRead` |
| `app/services/study_plan_service.py` | `StudyPlanService` |
| `app/api/v1/study_plans.py` | `/study-plans` router'ı |
| `app/database/migrations/versions/c68d9085b762_add_study_plans_table.py` | Migration |
| `tests/unit/test_study_plan_service.py` | 18 senaryo |
| `tests/integration/test_study_plan_endpoints.py` | 15 senaryo |

### Flutter

| Dosya | Açıklama |
|-------|----------|
| `lib/features/study_plan/domain/entities/study_plan_entity.dart` | Domain entity |
| `lib/features/study_plan/domain/entities/study_plan_status.dart` | Status enum |
| `lib/features/study_plan/domain/entities/study_time.dart` | Framework'ten bağımsız saat değer nesnesi |
| `lib/features/study_plan/domain/repositories/study_plan_repository.dart` | Repository interface |
| `lib/features/study_plan/domain/usecases/*.dart` | 8 usecase (get/create/update/delete/start/complete/skip/reorder) |
| `lib/features/study_plan/data/models/study_plan_model.dart` | JSON model + `toEntity()` |
| `lib/features/study_plan/data/datasources/study_plan_remote_datasource.dart` | `/study-plans` çağrıları |
| `lib/features/study_plan/data/repositories/study_plan_repository_impl.dart` | Repository implementasyonu |
| `lib/features/study_plan/presentation/providers/study_plan_state.dart` | Sealed state sınıfı |
| `lib/features/study_plan/presentation/providers/study_plan_provider.dart` | `StudyPlanNotifier` + DI provider'ları |
| `lib/features/study_plan/presentation/widgets/study_card.dart` | Plan kartı (başlat/tamamla/atla/düzenle/sil) |
| `lib/features/study_plan/presentation/widgets/study_plan_timeline.dart` | Saat aralığı tanımlı planların kronolojik görünümü |
| `lib/features/study_plan/presentation/widgets/daily_progress.dart` | Günlük ilerleme özeti |
| `lib/features/study_plan/presentation/widgets/study_plan_empty_state.dart` | Boş durum |
| `lib/features/study_plan/presentation/widgets/date_selector.dart` | Gün seçici + Bugün butonu |
| `lib/features/study_plan/presentation/widgets/study_plan_form.dart` | Add/Edit paylaşılan form |
| `lib/features/study_plan/presentation/screens/study_plan_screen.dart` | Ana ekran |
| `lib/features/study_plan/presentation/screens/add_study_plan_screen.dart` | Plan ekle |
| `lib/features/study_plan/presentation/screens/edit_study_plan_screen.dart` | Plan düzenle |
| `test/unit/study_plan_model_test.dart` | 5 senaryo |
| `test/unit/study_plan_repository_test.dart` | 6 senaryo |
| `test/unit/study_plan_provider_test.dart` | 9 senaryo |
| `test/widget/study_plan_screen_test.dart` | 9 senaryo |

### Dokümantasyon

| Dosya | Açıklama |
|-------|----------|
| `docs/sprints/Sprint-1.4.md` | Bu belge |
| `docs/meeting-notes/Meeting-012.md` | Oturum notu |

---

## Güncellenen Dosyalar

| Dosya | Değişiklik |
|-------|------------|
| `app/models/__init__.py` | `StudyPlan`, `StudyPlanStatus` export edildi |
| `app/core/constants.py` | `STUDY_PLAN_INITIAL_ORDER_INDEX` eklendi |
| `app/api/router.py` | `study_plans` router'ı `/study-plans` prefix'i ile bağlandı |
| `app/schemas/dashboard.py` | `today_plan_count`, `completed_plan_count`, `today_plans` alanları eklendi |
| `app/services/dashboard_service.py` | Gerçek `StudyPlan` verisiyle hesaplama yapacak şekilde yeniden yazıldı |
| `app/api/v1/dashboard.py` | `db` dependency'si eklendi, `async` yapıldı |
| `tests/unit/test_dashboard_service.py` | `StudyPlan` verisiyle güncellendi |
| `tests/integration/test_dashboard_endpoints.py` | Yeni alanlar + StudyPlan senaryosu eklendi |
| `tests/conftest.py` | `_reset_rate_limiter` fixture'ı eklendi (test izolasyonu — bkz. "Karşılaşılan Problemler") |
| `docs/architecture/database-design.md` | §1.9 StudyPlan gerçek implementasyona göre güncellendi; sürüm 1.1 → 1.2 |
| `docs/architecture/api-design.md` | §2.6 `/study-plans` ve §2.16 `/dashboard` güncellendi; sürüm 1.1 → 1.2 |
| `mobile/lib/core/constants/api_endpoints.dart` | `studyPlanToday` (kullanılmayan eski taslak) kaldırıldı; gerçek `/study-plans` endpoint yardımcıları eklendi |
| `mobile/lib/core/errors/dio_exception_mapper.dart` | `400` durum kodu `ValidationException`'a eşlendi (backend'in saat çakışması hatası `400` döner) |
| `mobile/lib/core/router/app_router.dart` | `/study-plan`, `/study-plan/add`, `/study-plan/edit/:id` rotaları eklendi |
| `mobile/lib/shared/widgets/app_bottom_nav_bar.dart` | `currentIndex` parametresi eklendi; Dashboard/Plan sekmeleri gerçek rotaya yönlendirir |
| `mobile/lib/features/dashboard/presentation/screens/dashboard_screen.dart` | `AppBottomNavBar(currentIndex: 0)` |
| `mobile/lib/features/dashboard/presentation/widgets/quick_actions_card.dart` | "Çalışma Planı" butonu `/study-plan`'a yönlendirir |

## Silinen Dosyalar

Bu sprintte dosya silinmedi.

---

## Mimari Kararlar

| Karar | Gerekçe |
|-------|---------|
| **[ONAY GEREKTİRİR]** `StudyPlan` tekil, düz tablo olarak implemente edildi (`user_id` FK, string `subject`/`topic`) | `database-design.md` §1.9'daki önceki taslak (`StudyPlan` + `StudyPlanItem`, `student_id`/`subject_id` FK'leri) `Student`/`Subject` modelleri henüz implemente edilmediği için kullanılamadı. Sprint-1.4 talebindeki alan listesi doğrudan uygulandı; karar dokümantasyona işlendi, `Student`/`Subject` eklendiğinde migrasyon değerlendirilebilir. |
| Saat çakışması kontrolü serviste yapılıyor, veritabanı kısıtı değil | PostgreSQL `EXCLUDE` kısıtı, `study_date` + zaman aralığı için ek bir uzantı (`btree_gist`) gerektirirdi; servis katmanında basit aralık çakışma kontrolü ("Basitlik önce gelir" ilkesi) yeterli ve taşınabilir. |
| Drag & Drop için ayrı bir `PATCH /study-plans/reorder` endpoint'i eklenmedi | Mevcut `PUT /study-plans/{id}` zaten `order_index` alanını kabul ediyor; her sürükleme sonrası yalnızca gerçekten değişen kalemler için bu endpoint çağrılıyor (`ReorderStudyPlanUsecase`). API sözleşmesi büyütülmeden mevcut endpoint yeniden kullanıldı. |
| Flutter domain katmanında saat için `TimeOfDay` (Flutter framework) yerine `StudyTime` (saf Dart) kullanıldı | `dashboard_entity.dart`'taki "framework bağımlılığı yok" ilkesiyle tutarlı; `TimeOfDay`↔`StudyTime` dönüşümü yalnızca presentation katmanının form/time picker sınırında yapılır. |
| `dio_exception_mapper.dart`'a `400` → `ValidationException` eşlemesi eklendi | Backend'in özel `ValidationError` (örn. saat çakışması) `400` döner; önceden yalnızca Pydantic'in `422`'si eşlenmişti, `400` "Bilinmeyen hata" olarak gösteriliyordu. Bu değişiklik yalnızca yeni bir `case` eklemekle sınırlı, mevcut davranış bozulmadı. |
| `StudyPlanTimeline` yalnızca saat aralığı tanımlı planları gösterir | "Zaman Çizelgesi" kavramsal olarak saatle ilişkilidir; saati olmayan planlar ana listede `order_index` ile sıralı kalır. Plan hiç saat içermiyorsa widget `SizedBox.shrink()` döner. |
| `AppBottomNavBar` ve `QuickActionsCard`'daki "Çalışma Planı" aksiyonu gerçek yönlendirmeye geçirildi | Sprint talebi "Alt Navigation" ve gerçek ekranı açıkça istiyor; önceki "Yakında" placeholder'ı artık geçerli değildi. Diğer sekmeler/butonlar (Pomodoro, İstatistik, Profil) ilgili modüller henüz yok, placeholder olarak bırakıldı. |

---

## Karşılaşılan Problemler ve Çözümler

| # | Problem | Çözüm |
|---|---------|-------|
| 1 | Entegrasyon testleri `KeyError: 'data'` ile başarısız oluyordu. | `slowapi` rate limiter, testler aynı IP'yi (127.0.0.1) paylaştığı için ardışık `/auth/register` çağrılarında limiti aşıyordu. `tests/conftest.py`'a `autouse=True` bir `_reset_rate_limiter` fixture'ı eklenerek her testten önce sayaç sıfırlandı. |
| 2 | `mypy`, `StudyPlanService._check_time_conflict` içinde `time | None` tipleri için "Unsupported operand types for <" hatası veriyordu. | `other.planned_start_time`/`planned_end_time` yerel değişkenlere atanıp `None` kontrolü yapılarak tip daraltması (narrowing) sağlandı. |
| 3 | Oturumlar arası ~18 saatlik boşluk sonrası Docker Desktop kapanmış, tüm backend testleri `ConnectionRefusedError` ile başarısız oldu. | Docker Desktop yeniden başlatıldı, `studyos_postgres`/`studyos_minio` container'larının `healthy` durumuna geçtiği doğrulandı; testler tekrar çalıştırılıp 70/70 geçti. Kod hatası değildi — ortam/operasyonel bir durumdu. |
| 4 | Riverpod unit testlerinde (`study_plan_provider_test.dart`) provider'ın lazy oluşturulması nedeniyle `constructor`'daki ilk `load()` çağrısı, testin `await settle()` beklemesinden SONRA tetikleniyor, bu da yarış durumuna (race condition) yol açıyordu. | `setUp`'ta `container.read(studyPlanProvider)` ile notifier erkenden oluşturuldu; böylece her testin ilk `await settle()`'ı gerçekten ilk yüklemeyi bekleyebildi. |
| 5 | Widget testinde `find.text(title)` iki eşleşme buluyordu. | `StudyPlanTimeline`, saat aralığı tanımlı planların başlığını da gösterdiği için ana listedeki kartla birlikte metin ikilendi. Test yardımcısı varsayılan olarak saat aralığı vermeyecek şekilde güncellendi. |

---

## Bilinen Sınırlamalar / Sonraki Sprint'e Bırakılanlar

- Bir planın `study_date`'ini değiştirmek (başka bir güne taşımak) Add/Edit formunda desteklenmiyor; tarih, Study Plan Screen'de o an seçili olan güne sabittir. Plan başka bir güne taşınacaksa silinip o günde yeniden oluşturulmalıdır.
- Drag & Drop sıralaması her değişen kalem için ayrı bir `PUT` isteği gönderir; çok uzun listelerde (yüzlerce kalem) performans için toplu bir reorder endpoint'i değerlendirilebilir (şu an gerçekçi kullanım senaryosunda — günlük plan — sorun oluşturmuyor).
- `integration_test/auth_flow_test.dart`, Meeting-010'da belgelenen Visual Studio Desktop C++ toolchain eksikliği nedeniyle bu ortamda hâlâ çalıştırılamıyor (bu sprintle ilgisiz, devam eden bir kısıt).
- Pomodoro oturumları (`StudySession`) henüz yok; bu nedenle Dashboard'daki `today_study_minutes`/`today_questions_solved` yalnızca `StudyPlan.completed_*` alanlarından gelir (fiili oturum bazlı zaman takibi Sprint-2+'da eklenecek).

---

## Bir Sonraki Sprint

**Sprint-2 (öneri):** Pomodoro Oturumları modülü (`StudySession` — S-10). `StudyPlan` ile ilişkilendirilebilir bir zamanlayıcı; oturum bitince ilgili plana `completed_minutes` ekler. Ardından soru istatistikleri (`QuestionStatistics`) ve haftalık/aylık özet ekranları planlanabilir.
