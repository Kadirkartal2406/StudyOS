import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/auth_response_model.dart';

/// Backend auth endpoint'lerine doğrudan erişen datasource.
/// Yalnızca ham API çağrıları içerir — iş mantığı yok.
class RemoteAuthDatasource {
  const RemoteAuthDatasource(this._dio);

  final Dio _dio;

  /// POST /auth/login
  Future<AuthResponseModel> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.login,
        data: {'email': email, 'password': password},
      );
      final data = _extractData(response.data);
      return AuthResponseModel.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// POST /auth/register
  Future<AuthResponseModel> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    String role = 'student',
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.register,
        data: {
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
          'role': role,
        },
      );
      final data = _extractData(response.data);
      return AuthResponseModel.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// POST /auth/refresh
  Future<TokenRefreshModel> refreshToken(String refreshToken) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.refresh,
        data: {'refresh_token': refreshToken},
        options: Options(extra: {'skipAuthInterceptor': true}),
      );
      final data = _extractData(response.data);
      return TokenRefreshModel.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// POST /auth/logout
  Future<void> logout(String refreshToken) async {
    try {
      await _dio.post<void>(
        ApiEndpoints.logout,
        data: {'refresh_token': refreshToken},
        options: Options(extra: {'skipAuthInterceptor': true}),
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// POST /auth/forgot-password
  Future<void> forgotPassword(String email) async {
    try {
      await _dio.post<void>(
        ApiEndpoints.forgotPassword,
        data: {'email': email},
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// API yanıtındaki `data` alanını çıkarır; hata durumunda exception fırlatır.
  Map<String, dynamic> _extractData(Map<String, dynamic>? responseData) {
    if (responseData == null) {
      throw const NetworkException(message: 'Boş yanıt alındı');
    }
    final success = responseData['success'] as bool? ?? false;
    if (!success) {
      final error = responseData['error'] as Map<String, dynamic>?;
      final message = error?['message'] as String? ?? 'Bilinmeyen hata';
      throw UnknownException(message: message);
    }
    return responseData['data'] as Map<String, dynamic>;
  }
}
