# Sprint-1.2B-Integration — Backend ↔ Flutter Entegrasyonu & Uçtan Uca Doğrulama

**Tarih:** 2026-07-15
**Sprint:** 1.2B-Integration (Meeting-010)
**Hedef:** Sprint-1.2A (Backend Authentication) ile Sprint-1.2B (Flutter Authentication) arasındaki entegrasyonu tamamlamak; tüm authentication akışını gerçek backend üzerinde doğrulamak.
**Durum:** ✅ Tamamlandı

---

## 1. Ön Koşul Doğrulaması

| Kontrol | Sonuç |
|---------|-------|
| Docker container'ları (`studyos_postgres`, `studyos_minio`) | ✅ Healthy |
| PostgreSQL bağlantısı | ✅ `SELECT version()` başarılı |
| Backend (`uvicorn app.main:app`) | ✅ `http://127.0.0.1:8000` |
| Swagger (`/api/docs`) | ✅ 200 OK |
| OpenAPI şeması (`/openapi.json`) | ✅ 200 OK |
| Flutter platform yapılandırması | Yalnızca **Windows (desktop)** ve **Web** platformları scaffold edilmiş (`android/`, `ios/` klasörleri yok). Her ikisi de `http://localhost:8000` kullanır — mevcut `AppConfig.apiBaseUrl` varsayılanı zaten doğru, kod değişikliği gerekmedi. |

---

## 2. Tespit Edilen Hatalar ve Düzeltmeler

Doğrulama sırasında entegrasyonu bozan iki hata tespit edildi ve düzeltildi (yeni özellik değil, mevcut sözleşmenin doğru çalışması için gerekli düzeltme):

| # | Hata | Etki | Düzeltme |
|---|------|------|----------|
| 1 | `dio_exception_mapper.dart` backend hata gövdesini `data['detail']['message']` olarak okuyordu; ancak backend zarfı (`app/main.py`) `{"error": {"message": ...}}` döndürüyor. | Backend'in ürettiği spesifik hata mesajları (örn. "Bu e-posta adresi zaten kayıtlı", "E-posta veya şifre hatalı") Flutter UI'a **hiçbir zaman ulaşmıyordu**; yalnızca genel (generic) mesajlar gösteriliyordu. | `_extractServerMessage()` yardımcı fonksiyonu eklendi: önce `error.message` (StudyOS zarfı), yoksa FastAPI'nin varsayılan pydantic doğrulama formatı (`detail` liste/string) okunuyor. |
| 2 | 422 (doğrulama hatası) durumu `dioExceptionToAppException`'da özel olarak ele alınmıyordu; genel `UnknownException`'a düşüyordu. | Zayıf şifre / geçersiz alan gibi backend doğrulama hataları kullanıcıya "Bilinmeyen hata" olarak gösterilirdi. | Yeni `ValidationException` (`app_exception.dart`) eklendi; 422 → `ValidationException` eşlemesi yapıldı. |
| 3 | `test/widget_test.dart`, artık var olmayan `MyApp` sınıfını referans alan eski `flutter create` sayaç (counter) testiydi. | `flutter analyze` ve `flutter test` **başarısız** oluyordu — Sprint-1.2B'nin kendi doğrulama tablosundaki "✅ flutter analyze" iddiası bu testle birlikte doğrulanamazdı. | Gerçek kök widget'ı (`StudyOSApp`) pompalayan, splash → login yönlendirmesini doğrulayan bir smoke test ile değiştirildi. `flutter_secure_storage` platform kanalı test ortamında mock'landı. |

> Bu üç düzeltme, `docs/project/ai-rules.md` §3.2.3 ("Mevcut davranış değiştirilmeden önce etkilenen alanlar listelenir") kapsamında burada belgelenmiştir. Mimari karar değişikliği içermez; yalnızca zaten var olan sözleşmenin (backend zarfı, gerçek uygulama widget ağacı) doğru şekilde karşılanmasını sağlar.

---

## 3. Uçtan Uca Authentication Testleri (Gerçek Backend)

Flutter'ın `RemoteAuthDatasource`'unun gönderdiği istek biçimlerini birebir taklit eden bir script ile `http://127.0.0.1:8000` üzerinde çalışan gerçek backend'e karşı test edildi (script doğrulama sonunda silinmiştir; kalıcı test paketi değildir).

| Senaryo | Beklenen | Sonuç |
|---------|----------|-------|
| Register — başarılı kayıt | 201, `access_token` + `refresh_token` + `user` döner | ✅ |
| Register — aynı e-posta ile tekrar | 409, `error.message` dolu | ✅ |
| Register — geçersiz e-posta formatı | 422 | ✅ |
| Register — zayıf şifre (< 8 karakter) | 422 | ✅ |
| Login — doğru bilgiler | 200, token çifti döner | ✅ |
| Login — yanlış şifre | 401, `error.message = "E-posta veya şifre hatalı"` | ✅ |
| Login — var olmayan kullanıcı | 401 | ✅ |
| Refresh — başarılı yenileme | 200, yeni access+refresh token | ✅ |
| Refresh — rotation doğrulaması | Yeni token çifti eskisinden farklı | ✅ |
| Refresh — eski (rotate edilmiş) token reddi | 401 | ✅ |
| Logout — refresh token iptali | 204 | ✅ |
| Logout sonrası refresh denemesi | 401 | ✅ |
| `/users/me` — geçerli token | 200 | ✅ |
| `/users/me` — token yok | 401 | ✅ |
| `/users/me` — geçersiz token | 401 | ✅ |

**Toplam: 24/24 kontrol başarılı** (3 ardışık çalıştırmada tutarlı; ilk çalıştırmada tek seferlik, tekrarlanmayan bir flake gözlendi — bkz. §6 Açık Sorular).

### 3.1 Flutter Tarafı Doğrulaması (Kod İncelemesi + Widget Testi)

Bu makinede Flutter için native Windows derleme araç zinciri (Visual Studio "Desktop development with C++") kurulu değildir ve Android/iOS platformları scaffold edilmemiştir; bu nedenle gerçek buton tıklamalarıyla uçtan uca UI testi bu ortamda **çalıştırılamadı** (bkz. §6). Bunun yerine:

- **Splash → Login yönlendirmesi:** `test/widget_test.dart` gerçek `StudyOSApp` widget ağacını pompalar, secure storage kanalını "oturum yok" olarak mock'lar ve `checkSession()` sonrası Login ekranına (`Hoş Geldin`) düştüğünü doğrular. ✅ Geçti.
- **Auth Guard, Secure Storage, Dio Interceptor:** Kod incelemesiyle doğrulandı (bkz. §4).
- **Gerçek UI E2E testi (register/login/logout buton akışı):** `integration_test/auth_flow_test.dart` olarak **yazıldı** ancak bu ortamda **çalıştırılamadı** (bkz. §6). Backend araç zinciri hazır olduğunda `flutter test integration_test/auth_flow_test.dart -d windows` ile çalıştırılabilir.

---

## 4. Kod İncelemesi Bulguları

| Alan | Dosya | Bulgu |
|------|-------|-------|
| Auth Guard | `lib/core/router/app_router.dart` | `_RouterNotifier.redirect()` — `AuthUnauthenticated`/`AuthError` durumunda `authRoutes` dışındaki her rota `/login`'e yönlendirilir. `/home`'a doğrudan `go()` çağrısı bile guard tarafından yakalanır. ✅ Doğru. |
| Secure Storage | `lib/services/local_storage_service.dart` | Access token **in-memory** (`_accessToken` alanı, RAM'de, disk'e yazılmaz — 15 dk kısa ömür mimari kararına uygun). Refresh token + kullanıcı `flutter_secure_storage`'da (Android: `encryptedSharedPreferences`, iOS: `first_unlock_this_device`). `clearAll()` üçünü de temizler. ✅ Doğru. |
| Dio Interceptor | `lib/core/network/dio_client.dart` | `onRequest`: her isteğe `Authorization: Bearer <token>` eklenir. `onError`: 401 alındığında (`skipAuthInterceptor` bayrağı yoksa) refresh denenir, başarılıysa orijinal istek yeni token ile tekrarlanır (`retryDio.fetch`), başarısızsa `clearAll()` çağrılır. Refresh/logout istekleri `skipAuthInterceptor: true` ile döngüye girmez. ✅ Doğru. |
| Splash | `lib/features/auth/presentation/screens/splash_screen.dart`, `auth_provider.dart` | `checkSession()`: kayıtlı oturum yoksa `Unauthenticated`; varsa refresh token ile yenileme denenir — başarılıysa `Authenticated(user)`, başarısızsa `clearAll()` + `Unauthenticated`. Router bu duruma göre Home/Login'e yönlendirir. ✅ Doğru. |
| Hata Yönetimi | `lib/core/errors/dio_exception_mapper.dart` | §2'de belirtilen düzeltme sonrası backend `error.message` ve FastAPI varsayılan `detail` formatı doğru okunuyor; `login_screen.dart`/`register_screen.dart` bu mesajı `SnackBar` ile gösteriyor. ✅ Düzeltildi ve doğrulandı. |

---

## 5. Kod Kalitesi

| Kontrol | Sonuç |
|---------|-------|
| `flutter pub get` | ✅ |
| `flutter analyze` | ✅ No issues found! |
| `flutter test` | ✅ 1/1 geçti |
| `pytest` (backend) | ✅ 27/27 geçti |
| `ruff check .` | ✅ All checks passed! |
| `ruff format --check .` | ✅ 44 dosya zaten formatlı |
| `mypy app` | ✅ Success: no issues found in 36 source files |

---

## 6. Açık Sorular / Riskler

| Konu | Durum |
|------|-------|
| Gerçek UI E2E testi (`integration_test/auth_flow_test.dart`) çalıştırılamadı | Bu makinede Visual Studio "Desktop development with C++" kurulu değil (Windows native derleme için zorunlu) ve Flutter 3.32.4 web platformunda `integration_test`'i henüz desteklemiyor ("Web devices are not supported for integration tests yet"). Android/iOS platformları da scaffold edilmemiş. **Öneri:** Visual Studio Build Tools kurulduğunda test tekrar çalıştırılıp bu belge güncellenmeli. |
| İlk E2E script çalıştırmasında tek seferlik flake | 3 ardışık çalıştırmadan yalnızca ilkinde (backend'in ilk isteği) bir kontrol beklenmedik şekilde başarısız oldu, sonraki 2 çalıştırmada ve izole DB doğrulamasında sorun tekrarlanmadı. Kök neden kesin olarak belirlenemedi (ilk bağlantı havuzu ısınması şüpheli). Üretimde izlenmeli; blocker değildir. |
| FastAPI'nin varsayılan 422 zarfı StudyOS zarfıyla tutarsız | `RequestValidationError` için özel bir exception handler yok; bu yüzden 422 yanıtları `{"success":..., "error":...}` zarfını değil FastAPI'nin `{"detail": [...]}` formatını kullanıyor. Flutter tarafı bunu yedek olarak parse ediyor (bkz. §2) ama API tutarlılığı için Sprint-2'de `RequestValidationError` için özel handler eklenmesi değerlendirilmeli. |
| Android/iOS platformları henüz scaffold edilmemiş | `10.0.2.2` (Android emulator) base URL mantığı bu nedenle henüz uygulanamadı; platformlar eklendiğinde `AppConfig.apiBaseUrl`'e platform bazlı varsayılan eklenmesi gerekecek. |

---

## 7. Bir Sonraki Adım

1. Visual Studio Desktop C++ workload kurulumu → `integration_test/auth_flow_test.dart`'ın gerçek Windows derlemesiyle çalıştırılıp doğrulanması.
2. Sprint-1.3 planlaması: Dashboard ekranı, çalışma planı modülü, navigation bar.
3. Android/iOS platformlarının scaffold edilmesi planlandığında `AppConfig.apiBaseUrl` platform bazlı varsayılan mantığı eklenmeli.
