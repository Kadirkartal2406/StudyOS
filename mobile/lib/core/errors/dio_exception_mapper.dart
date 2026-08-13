import 'package:dio/dio.dart';

import 'app_exception.dart';

/// Dio exception'larını AppException'a dönüştürür.
AppException dioExceptionToAppException(DioException e) {
  switch (e.type) {
    case DioExceptionType.connectionTimeout:
    case DioExceptionType.receiveTimeout:
    case DioExceptionType.sendTimeout:
    case DioExceptionType.transformTimeout:
      return const NetworkException(message: 'Bağlantı zaman aşımı');
    case DioExceptionType.connectionError:
      // Web'de CORS engeli de connectionError olarak düşer.
      return const NetworkException(
        message: 'Sunucuya bağlanılamadı. Backend çalışıyor mu?',
      );
    case DioExceptionType.badResponse:
      final statusCode = e.response?.statusCode;
      final serverMessage = _extractServerMessage(e.response?.data);
      final serverCode = _extractServerCode(e.response?.data);

      if (serverCode != null && serverCode.startsWith('AI_')) {
        return AiProviderException(
          message: serverMessage ?? 'AI sağlayıcı hatası',
          code: serverCode,
        );
      }

      return switch (statusCode) {
        400 => ValidationException(message: serverMessage ?? 'Girdi doğrulama hatası'),
        401 => AuthException(message: serverMessage ?? 'Kimlik doğrulama başarısız'),
        403 => const ForbiddenException(),
        404 => NotFoundException(message: serverMessage ?? 'Kaynak bulunamadı'),
        409 => ConflictException(message: serverMessage ?? 'Kayıt zaten mevcut'),
        422 => ValidationException(message: serverMessage ?? 'Girdi doğrulama hatası'),
        429 => AiProviderException(
            message: serverMessage ?? 'AI kota / hız limiti aşıldı',
            code: serverCode ?? 'AI_RATE_LIMIT',
          ),
        502 || 503 || 504 => AiProviderException(
            message: serverMessage ?? 'AI sağlayıcı kullanılamıyor',
            code: serverCode ?? 'AI_UNAVAILABLE',
          ),
        int s when s >= 500 => ServerException(
            message: serverMessage ?? 'Sunucu hatası, lütfen tekrar deneyin',
          ),
        _ => UnknownException(message: serverMessage ?? 'Bilinmeyen hata'),
      };
    case DioExceptionType.cancel:
      return const CancelledException();
    case DioExceptionType.unknown:
    case DioExceptionType.badCertificate:
      return const NetworkException(message: 'Bağlantı kurulamadı');
  }
}

/// Backend hata gövdesinden kullanıcıya gösterilecek mesajı çıkarır.
///
/// StudyOS API zarfı (`{"success": false, "error": {"code", "message"}}`)
/// önceliklidir. FastAPI'nin varsayılan pydantic doğrulama hatası formatı
/// (`{"detail": [{"msg": ...}]}` veya `{"detail": "..."}`) yedek olarak desteklenir.
String? _extractServerMessage(Object? data) {
  if (data is! Map) return null;

  final error = data['error'];
  if (error is Map) {
    return error['message'] as String?;
  }

  final detail = data['detail'];
  if (detail is String) return detail;
  if (detail is Map) {
    return detail['message'] as String?;
  }
  if (detail is List && detail.isNotEmpty) {
    final first = detail.first;
    if (first is Map) return first['msg'] as String?;
  }

  return null;
}

String? _extractServerCode(Object? data) {
  if (data is! Map) return null;
  final error = data['error'];
  if (error is Map) return error['code'] as String?;
  final detail = data['detail'];
  if (detail is Map) return detail['code'] as String?;
  return null;
}
