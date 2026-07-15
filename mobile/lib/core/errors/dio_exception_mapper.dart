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
      return const NetworkException(message: 'İnternet bağlantısı yok');
    case DioExceptionType.badResponse:
      final statusCode = e.response?.statusCode;
      final data = e.response?.data;
      String? serverMessage;
      if (data is Map) {
        final detail = data['detail'];
        if (detail is Map) {
          serverMessage = detail['message'] as String?;
        }
      }

      return switch (statusCode) {
        401 => AuthException(message: serverMessage ?? 'Kimlik doğrulama başarısız'),
        403 => const ForbiddenException(),
        404 => NotFoundException(message: serverMessage ?? 'Kaynak bulunamadı'),
        409 => ConflictException(message: serverMessage ?? 'Kayıt zaten mevcut'),
        int s when s >= 500 => const ServerException(),
        _ => UnknownException(message: serverMessage ?? 'Bilinmeyen hata'),
      };
    case DioExceptionType.cancel:
      return const UnknownException(message: 'İstek iptal edildi');
    case DioExceptionType.unknown:
    case DioExceptionType.badCertificate:
      return const NetworkException(message: 'Bağlantı kurulamadı');
  }
}
