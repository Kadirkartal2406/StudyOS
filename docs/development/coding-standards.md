# StudyOS — Kodlama Standartları

**Belge Durumu:** Aktif  
**Sürüm:** 1.0  
**Oluşturuldu:** 2026-07-06 — Meeting-007  
**Dil:** Türkçe  
**Kapsam:** Tüm geliştiriciler (Flutter, FastAPI, genel)

> Bu belge iki geliştirici arasında tutarlılığı sağlar.  
> Her kural gerekçesiyle birlikte verilmiştir.

---

## 1. Genel Prensipler

1. **Okunabilirlik önce gelir.** Kod, yazan kişi için değil; okuyan kişi için yazılır.
2. **Tutarlılık akıllılıktan önce gelir.** Standarttan sapma ancak açık gerekçeyle mümkündür.
3. **İsimlendirme anlam taşır.** `x`, `temp`, `data` gibi anlamsız isimler kabul edilmez.
4. **Yorum `neden`i açıklar.** `ne yaptığını` kodun kendisi söyler; `neden` ise yorum.
5. **Tek sorumluluk zorunludur.** Her sınıf, her fonksiyon, her modül tek bir iş yapar.

---

## 2. Flutter / Dart Kodlama Standartları

### 2.1 Dosya İsimlendirme

| Tür | Format | Örnek |
|-----|--------|-------|
| Dart dosyası | `snake_case.dart` | `study_plan_screen.dart` |
| Widget dosyası | `snake_case_widget.dart` | `plan_card_widget.dart` |
| Provider dosyası | `snake_case_provider.dart` | `auth_provider.dart` |
| Repository dosyası | `snake_case_repository.dart` | `study_plan_repository.dart` |
| Use Case dosyası | `snake_case_usecase.dart` | `login_usecase.dart` |
| Entity dosyası | `snake_case.dart` | `user.dart` |
| Test dosyası | `snake_case_test.dart` | `auth_provider_test.dart` |

### 2.2 Sınıf İsimlendirme

| Tür | Format | Örnek |
|-----|--------|-------|
| Widget | `PascalCase` | `StudyPlanCard`, `AuthButton` |
| Provider (Riverpod) | `PascalCase + Provider/Notifier` | `AuthNotifier`, `studyPlanProvider` |
| Use Case | `PascalCase + UseCase` | `LoginUseCase`, `GetStudyPlanUseCase` |
| Repository Interface | `PascalCase + Repository` | `AuthRepository`, `StudyPlanRepository` |
| Repository Impl | `PascalCase + RepositoryImpl` | `AuthRepositoryImpl` |
| Entity | `PascalCase` | `User`, `StudyPlan` |
| Model (JSON) | `PascalCase + Model` | `UserModel`, `StudyPlanModel` |
| Exception | `PascalCase + Exception` | `NetworkException`, `AuthException` |
| Enum | `PascalCase` (değerler: `camelCase`) | `ExamMode.yks`, `UserRole.student` |

### 2.3 Değişken ve Fonksiyon İsimlendirme

| Tür | Format | Örnek |
|-----|--------|-------|
| Değişken | `camelCase` | `studyPlan`, `isLoading` |
| Sabit (final) | `camelCase` | `maxRetryCount`, `apiBaseUrl` |
| Global sabit | `SCREAMING_SNAKE_CASE` | `API_TIMEOUT_SECONDS = 10` |
| Fonksiyon | `camelCase` fiil ile başlar | `getStudyPlan()`, `submitAnswer()` |
| Boolean | `is/has/can` ile başlar | `isLoggedIn`, `hasSubscription` |
| Private | `_camelCase` | `_controller`, `_handleError()` |

### 2.4 Widget Yapısı Kuralları

- Her widget kendi dosyasında olur; bir dosyaya birden fazla widget yazılmaz.
- `StatelessWidget` tercih edilir. State gerektiğinde Riverpod kullanılır.
- Widget parametreleri `final` olarak tanımlanır.
- `const` constructor mümkün olan her yerde kullanılır.

### 2.5 Riverpod Kuralları

- Provider isimleri `camelCase` + `Provider` son eki: `authProvider`, `studyPlanListProvider`.
- `Notifier` sınıfları `PascalCase` + `Notifier`: `StudyPlanNotifier`.
- `ref.watch()` build metodunda, `ref.read()` event handler'larda kullanılır.
- Global state için `StateNotifier` veya `AsyncNotifier`; local state için `useState` (hooks) veya widget state.

### 2.6 Import Sıralaması

```dart
// 1. Dart built-in
import 'dart:async';

// 2. Flutter framework
import 'package:flutter/material.dart';

// 3. Pub packages
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:dio/dio.dart';

// 4. Proje içi (mutlak yol tercih)
import 'package:studyos/core/errors/app_exception.dart';
import 'package:studyos/features/auth/domain/entities/user.dart';
```

---

## 3. FastAPI / Python Kodlama Standartları

### 3.1 Dosya İsimlendirme

| Tür | Format | Örnek |
|-----|--------|-------|
| Python modülü | `snake_case.py` | `auth_service.py`, `user_repository.py` |
| Test dosyası | `test_snake_case.py` | `test_auth_service.py` |
| Migration | Alembic otomatik üretir | `20260706_add_refresh_tokens.py` |

### 3.2 Sınıf İsimlendirme

| Tür | Format | Örnek |
|-----|--------|-------|
| SQLAlchemy Model | `PascalCase` | `User`, `StudyPlan` |
| Pydantic Schema | `PascalCase` + bağlam son eki | `UserCreate`, `UserRead`, `LoginRequest` |
| Service | `PascalCase + Service` | `AuthService`, `StudyPlanService` |
| Repository | `PascalCase + Repository` | `UserRepository`, `ExamRepository` |
| Exception | `PascalCase + Error/Exception` | `UserNotFoundError`, `AuthenticationError` |
| Abstract class | `PascalCase` (Base prefix opsiyonel) | `AIProvider`, `BaseRepository` |

### 3.3 Fonksiyon ve Değişken İsimlendirme

| Tür | Format | Örnek |
|-----|--------|-------|
| Fonksiyon | `snake_case` fiil ile başlar | `get_user_by_email()`, `create_study_plan()` |
| Değişken | `snake_case` | `user_id`, `is_verified` |
| Sabit | `SCREAMING_SNAKE_CASE` | `ACCESS_TOKEN_EXPIRE_MINUTES = 15` |
| Private metod | `_snake_case` | `_hash_password()`, `_validate_token()` |
| Async fonksiyon | `async def snake_case` | `async def get_user_by_id()` |

### 3.4 FastAPI Router Kuralları

- Her domain için ayrı router dosyası oluşturulur.
- Router prefix `/api/v1/{kaynak}` formatını takip eder.
- Endpoint fonksiyon isimleri `{eylem}_{kaynak}` formatında olur:

```python
# Doğru
async def get_student(student_id: UUID, ...) → StudentRead
async def create_study_plan(body: StudyPlanCreate, ...) → StudyPlanRead
async def delete_exam(exam_id: UUID, ...) → None

# Yanlış
async def student(...)         # eylem eksik
async def handle_post(...)     # anlamsız
```

### 3.5 Pydantic Schema Konvansiyonu

| Amaç | İsim Paterni | Örnek |
|------|-------------|-------|
| Oluşturma isteği | `{Entity}Create` | `StudyPlanCreate` |
| Okuma/listeleme yanıtı | `{Entity}Read` | `StudyPlanRead` |
| Güncelleme isteği | `{Entity}Update` | `StudyPlanUpdate` |
| Detaylı yanıt | `{Entity}Detail` | `ExamDetail` |
| Liste yanıtı | `{Entity}List` | `ExamList` |
| İstek gövdesi (özel) | `{Eylem}Request` | `LoginRequest`, `ResetPasswordRequest` |

### 3.6 Tip İpuçları (Type Hints)

Tüm fonksiyon parametreleri ve dönüş tipleri açıkça belirtilir:

```python
# Doğru
async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User | None:

# Yanlış
async def get_user_by_id(user_id, db):
```

### 3.7 Hata Yönetimi

- `try/except` bloklarında sadece beklenen exception'lar yakalanır; `except Exception` kullanılmaz.
- Her servis fonksiyonu domain exception fırlatır; HTTP exception fırlatmaz (bu `api` katmanının işidir).
- Exception handler'lar `app/core/exceptions.py` dosyasında merkezi olarak tanımlanır.

---

## 4. API İsimlendirme Standartları

### 4.1 Endpoint URL Kuralları

| Kural | Doğru | Yanlış |
|-------|-------|--------|
| Çoğul isim | `/students` | `/student` |
| Küçük harf | `/study-plans` | `/StudyPlans` |
| Kebab-case | `/study-plans` | `/study_plans` |
| Fiil kullanma | `/institutions/{id}/teachers/invite` (POST ile eylem) | `/createTeacher` |
| İç içe kaynak | `/institutions/{id}/classes` | `/getClassesByInstitution` |

### 4.2 HTTP Metod Seçimi

| Eylem | HTTP Metod | Örnek |
|-------|-----------|-------|
| Listeleme | GET | `GET /students` |
| Tekil okuma | GET | `GET /students/{id}` |
| Oluşturma | POST | `POST /study-plans` |
| Tam güncelleme | PUT | `PUT /users/{id}` |
| Kısmi güncelleme | PATCH | `PATCH /users/me` |
| Silme | DELETE | `DELETE /notifications/{id}` |
| Özel eylem | POST | `POST /auth/logout`, `POST /files/confirm` |

---

## 5. Git Dallanma (Branch) Stratejisi

### 5.1 Kalıcı Dallar

| Dal | Amaç |
|-----|------|
| `main` | Üretim kodu. Her commit deploy edilebilir durumda. |
| `develop` | Aktif geliştirme. Feature dalları buraya merge edilir. |

### 5.2 Geçici Dallar

| Tip | Format | Örnek |
|-----|--------|-------|
| Özellik | `feature/{ticket}-{kısa-açıklama}` | `feature/S01-login-screen` |
| Hata düzeltme | `fix/{ticket}-{kısa-açıklama}` | `fix/S17-notification-not-sent` |
| Acil düzeltme | `hotfix/{kısa-açıklama}` | `hotfix/auth-token-expiry` |
| Refactor | `refactor/{kısa-açıklama}` | `refactor/study-plan-service` |
| Dokümantasyon | `docs/{kısa-açıklama}` | `docs/api-design-update` |
| Altyapı | `infra/{kısa-açıklama}` | `infra/railway-config` |

### 5.3 Dal Akışı

```
feature/S01-login → develop → main
                  ↑ Pull Request ile
```

- Her özellik için `develop` dalından yeni dal oluşturulur.
- Pull Request (PR) açılır; diğer geliştirici kodu inceler.
- Onaylanan PR `develop`'a squash merge yapılır.
- `develop` → `main` geçişi her sürümde yapılır.

---

## 6. Commit Mesajı Konvansiyonu

### 6.1 Format

```
<tip>(<kapsam>): <kısa açıklama>

[opsiyonel gövde]

[opsiyonel alt bilgi]
```

### 6.2 Commit Tipleri

| Tip | Açıklama | Örnek |
|-----|---------|-------|
| `feat` | Yeni özellik | `feat(auth): JWT login endpoint eklendi` |
| `fix` | Hata düzeltme | `fix(notification): FCM token null kontrolü eklendi` |
| `refactor` | Davranışı değiştirmeyen yeniden yazım | `refactor(study-plan): service katmanı ayırıldı` |
| `test` | Test ekleme veya düzeltme | `test(auth): login service unit testleri eklendi` |
| `docs` | Dokümantasyon değişikliği | `docs(api): /students endpoint güncellendi` |
| `style` | Biçimlendirme, boşluk (mantık değişimi yok) | `style(auth): dart format uygulandı` |
| `chore` | Bağımlılık, CI/CD, config değişikliği | `chore: sentry_flutter 8.1.0 güncellendi` |
| `perf` | Performans iyileştirmesi | `perf(statistics): sorgu indexi eklendi` |
| `ci` | CI/CD pipeline değişikliği | `ci: GitHub Actions test adımı güncellendi` |

### 6.3 Kapsam (Scope) Örnekleri

Flutter: `auth`, `study-plan`, `pomodoro`, `statistics`, `notification`, `ui`  
Backend: `auth`, `student`, `institution`, `exam`, `ai`, `storage`, `db`

### 6.4 Kural ve Yasaklar

- Kısa açıklama 72 karakteri geçmez.
- Türkçe commit mesajı yazılır; teknoloji isimleri İngilizce kalır.
- Geniş zaman (imperative mood değil) kullanılır: "eklendi", "düzeltildi", "kaldırıldı".
- `WIP`, `düzeltildi`, `test` gibi anlamsız mesajlar yasaktır.
- Her commit tek bir mantıksal değişikliği kapsar.

**Doğru örnekler:**
```
feat(auth): şifre sıfırlama e-posta akışı eklendi
fix(study-plan): boş plan günü istatistik hatası düzeltildi
test(institution): kurum davet servisi unit testleri eklendi
chore: python-jose 3.4.0 bağımlılığı güncellendi
```

**Yanlış örnekler:**
```
düzeltme                               # anlamsız
fix everything                         # ne düzeltildi?
WIP                                    # çalışmayan kod commit edilmez
feat: çok şey eklendi                  # tek commit tek değişiklik
```

---

## 7. Kod İnceleme (Code Review) Kuralları

### 7.1 Pull Request Standartları

- Her PR tek bir özellik veya düzeltme içerir.
- PR başlığı commit mesajı formatını takip eder: `feat(auth): login akışı`
- PR açıklaması şunları içerir:
  - Ne değişti?
  - Neden değişti?
  - Nasıl test edildi?
  - İlgili özellik kodu (S-01, K-07 gibi)

### 7.2 İnceleme Kriterleri

- [ ] Kodlama standartlarına uygun mu?
- [ ] Test var mı (en az bir senaryo)?
- [ ] Hata yönetimi yapılmış mı?
- [ ] Gereksiz bağımlılık eklendi mi?
- [ ] Güvenlik açığı var mı?
- [ ] Dokümantasyon güncellendi mi?

---

## 8. Kod Formatı ve Linting

### 8.1 Flutter

| Araç | Konfigürasyon | Amaç |
|------|--------------|------|
| `dart format` | Otomatik | Kod biçimlendirme |
| `flutter analyze` | `analysis_options.yaml` | Statik analiz |
| `dart fix` | — | Otomatik düzeltme |

Commit öncesi `dart format .` ve `flutter analyze` çalıştırılır.

### 8.2 Python (FastAPI)

| Araç | Konfigürasyon | Amaç |
|------|--------------|------|
| `ruff` | `pyproject.toml` | Linting + formatting (flake8 + isort + black yerine) |
| `mypy` | `pyproject.toml` | Statik tip kontrolü |
| `pytest` | `pyproject.toml` | Test çalıştırma |

Commit öncesi `ruff check .` ve `mypy app/` çalıştırılır.

---

## 9. Ortam Değişkenleri Kuralları

- Tüm hassas değerler (API key, veritabanı bağlantısı, şifre) `.env` dosyasında tutulur.
- `.env` dosyası git'e eklenmez; `.env.example` eklenir.
- Değişken isimleri `SCREAMING_SNAKE_CASE`:
  - `DATABASE_URL`, `JWT_SECRET_KEY`, `AWS_ACCESS_KEY_ID`
- FastAPI'de `pydantic BaseSettings` ile ortam değişkenleri yüklenir ve tip güvenliği sağlanır.
- Her ortam için ayrı değişken dosyası: `.env.development`, `.env.production`.

---

## Sürüm Geçmişi

| Sürüm | Tarih | Değişiklik |
|-------|-------|-----------|
| 1.0 | 2026-07-06 | İlk sürüm — Meeting-007 |
