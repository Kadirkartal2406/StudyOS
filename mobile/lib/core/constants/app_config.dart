/// StudyOS — Uygulama sabitleri.
/// Değerler --dart-define ile derleme zamanında verilir.
class AppConfig {
  AppConfig._();

  /// Backend API base URL.
  /// Geliştirme: http://localhost:8000/api/v1
  /// Üretim: https://api.studyos.com/api/v1
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );

  /// Sentry DSN (hata izleme).
  static const String sentryDsn = String.fromEnvironment('SENTRY_DSN');

  /// Uygulama sürümü.
  static const String appVersion = '0.1.0';

  /// API istek zaman aşımı (saniye).
  static const int apiTimeoutSeconds = 30;

  /// Refresh token güvenli depolama anahtarı.
  static const String refreshTokenKey = 'studyos_refresh_token';

  /// Access token bellek anahtarı.
  static const String accessTokenKey = 'studyos_access_token';

  /// Kullanıcı verisi güvenli depolama anahtarı.
  static const String currentUserKey = 'studyos_current_user';
}
