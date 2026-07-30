import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../services/local_storage_service.dart';
import '../constants/api_endpoints.dart';
import '../constants/app_config.dart';

/// Auth Interceptor.
/// Her isteğe Bearer token ekler; 401 alındığında token yeniler ve isteği tekrarlar.
class _AuthInterceptor extends Interceptor {
  _AuthInterceptor(this._storage, this._baseUrl);

  final LocalStorageService _storage;
  final String _baseUrl;

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (_storage.accessToken == null) {
      await _storage.restoreAccessToken();
    }
    final token = _storage.accessToken;
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    // skipAuthInterceptor flag'i olan istekler (refresh/logout) döngüye girmez
    final skip = err.requestOptions.extra['skipAuthInterceptor'] as bool? ?? false;

    if (err.response?.statusCode == 401 && !skip) {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) {
        await _storage.clearAll();
        return handler.next(err);
      }

      try {
        // Token yenile
        final refreshDio = Dio(
          BaseOptions(
            baseUrl: _baseUrl,
            connectTimeout: const Duration(seconds: AppConfig.apiTimeoutSeconds),
            receiveTimeout: const Duration(seconds: AppConfig.apiTimeoutSeconds),
          ),
        );

        final refreshResponse = await refreshDio.post<Map<String, dynamic>>(
          ApiEndpoints.refresh,
          data: {'refresh_token': refreshToken},
        );

        final data = refreshResponse.data?['data'] as Map<String, dynamic>?;
        if (data == null) throw Exception('Refresh yanıtı geçersiz');

        final newAccess = data['access_token'] as String;
        final newRefresh = data['refresh_token'] as String;

        await _storage.setAccessToken(newAccess);
        await _storage.saveRefreshToken(newRefresh);

        // Orijinal isteği yeni token ile tekrarla
        final retryOptions = err.requestOptions;
        retryOptions.headers['Authorization'] = 'Bearer $newAccess';

        final retryDio = Dio();
        final retryResponse = await retryDio.fetch<dynamic>(retryOptions);
        return handler.resolve(retryResponse);
      } catch (_) {
        // Refresh de başarısız → oturumu temizle
        await _storage.clearAll();
        return handler.next(err);
      }
    }

    handler.next(err);
  }
}

/// Temel Dio HTTP istemcisi Riverpod provider'ı.
final dioClientProvider = Provider<Dio>((ref) {
  final storage = ref.watch(localStorageServiceProvider);

  final dio = Dio(
    BaseOptions(
      baseUrl: AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: AppConfig.apiTimeoutSeconds),
      receiveTimeout: const Duration(seconds: AppConfig.apiTimeoutSeconds),
      headers: const {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ),
  );

  dio.interceptors.add(_AuthInterceptor(storage, AppConfig.apiBaseUrl));

  return dio;
});
