# Sprint-1.2B — Flutter Authentication

**Tarih:** 2026-07-15  
**Sprint:** 1.2B  
**Hedef:** Flutter mobil uygulamasını gerçek backend authentication sistemiyle çalıştırmak.  
**Durum:** ✅ Tamamlandı

---

## Doğrulama

| Test | Sonuç |
|------|-------|
| `flutter pub get` | ✅ |
| `flutter analyze` | ✅ No issues found! |

---

## Oluşturulan Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `lib/services/local_storage_service.dart` | SecureStorage wrapper — access token in-memory, refresh token + user şifreli depoda |
| `lib/features/auth/domain/entities/auth_user.dart` | Domain entity — saf Dart, JSON serializable |
| `lib/features/auth/domain/repositories/auth_repository.dart` | Repository interface (Dart 3 records dönüş tipi) |
| `lib/features/auth/data/models/auth_response_model.dart` | API yanıt modelleri |
| `lib/features/auth/data/datasources/remote_auth_datasource.dart` | Backend API çağrıları |
| `lib/features/auth/data/repositories/auth_repository_impl.dart` | Repository implementasyonu |
| `lib/features/auth/presentation/providers/auth_state.dart` | Sealed AuthState (Initial/Loading/Authenticated/Unauthenticated/Error) |
| `lib/features/auth/presentation/providers/auth_provider.dart` | AuthNotifier + DI providers |
| `lib/features/auth/presentation/screens/splash_screen.dart` | Splash — oturum kontrolü + animasyon |
| `lib/features/auth/presentation/screens/login_screen.dart` | Giriş ekranı — form validasyon, hata snackbar |
| `lib/features/auth/presentation/screens/register_screen.dart` | Kayıt ekranı — şifre gücü validasyonu |
| `lib/features/auth/presentation/screens/forgot_password_screen.dart` | Şifre sıfırlama — placeholder |
| `lib/features/auth/presentation/screens/home_screen.dart` | Ana ekran — placeholder, logout butonu |
| `lib/features/auth/presentation/widgets/auth_text_field.dart` | Yeniden kullanılabilir input widget |
| `lib/features/auth/presentation/widgets/auth_button.dart` | Primary/secondary buton + loading state |

---

## Güncellenen Dosyalar

| Dosya | Değişiklik |
|-------|------------|
| `lib/core/network/dio_client.dart` | Auth interceptor eklendi (Bearer token inject, 401 → refresh → retry) |
| `lib/core/router/app_router.dart` | Auth guard (redirect), tüm rotalar tanımlandı |
| `lib/core/constants/app_config.dart` | `currentUserKey` sabiti eklendi |

---

## Mimari Kararlar

| Karar | Gerekçe |
|-------|---------|
| Access token → in-memory | Mimari dokümana uygun (15 dk kısa ömür, güvenlik) |
| Refresh token → flutter_secure_storage | Şifreli, platform güvenliği |
| Sealed AuthState | Dart 3 exhaustive switch — compiler garantisi |
| `skipAuthInterceptor` flag | Refresh/logout isteğinde sonsuz döngü önlemi |
| `AuthRepositoryException` kaldırıldı | Sealed class farklı kütüphaneden extend edilemez |

---

## Bir Sonraki Adım

**Sprint-1.3:** Dashboard ekranı, çalışma planı modülü, navigation bar.
