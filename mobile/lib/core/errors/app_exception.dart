/// StudyOS Flutter — Uygulama hata hiyerarşisi.
/// Backend exception'larıyla eşleştirilmiş client-side hatalar.
sealed class AppException implements Exception {
  const AppException({required this.message, this.code});

  final String message;
  final String? code;

  @override
  String toString() => 'AppException($code): $message';
}

/// Ağ bağlantısı veya zaman aşımı hatası.
final class NetworkException extends AppException {
  const NetworkException({required super.message}) : super(code: 'NETWORK_ERROR');
}

/// Kimlik doğrulama hatası (401).
final class AuthException extends AppException {
  const AuthException({required super.message}) : super(code: 'AUTH_ERROR');
}

/// Yetki hatası (403).
final class ForbiddenException extends AppException {
  const ForbiddenException({super.message = 'Bu işlem için yetkiniz yok'})
      : super(code: 'FORBIDDEN');
}

/// Kaynak bulunamadı (404).
final class NotFoundException extends AppException {
  const NotFoundException({required super.message}) : super(code: 'NOT_FOUND');
}

/// Çakışma hatası (409) — örn. e-posta zaten kayıtlı.
final class ConflictException extends AppException {
  const ConflictException({required super.message}) : super(code: 'CONFLICT');
}

/// Sunucu hatası (5xx).
final class ServerException extends AppException {
  const ServerException({super.message = 'Sunucu hatası, lütfen tekrar deneyin'})
      : super(code: 'SERVER_ERROR');
}

/// Beklenmeyen genel hata.
final class UnknownException extends AppException {
  const UnknownException({super.message = 'Beklenmeyen bir hata oluştu'})
      : super(code: 'UNKNOWN');
}
