import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/notification_settings_model.dart';

class NotificationSettingsRemoteDatasource {
  const NotificationSettingsRemoteDatasource(this._dio);

  final Dio _dio;

  Future<NotificationSettingsModel> getSettings() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.notificationSettings,
      );
      return NotificationSettingsModel.fromJson(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<NotificationSettingsModel> updateSettings(
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _dio.put<Map<String, dynamic>>(
        ApiEndpoints.notificationSettings,
        data: body,
      );
      return NotificationSettingsModel.fromJson(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<NotificationSettingsModel> updateFcmToken(String token) async {
    try {
      final response = await _dio.put<Map<String, dynamic>>(
        ApiEndpoints.notificationSettingsFcmToken,
        data: {'fcm_token': token},
      );
      return NotificationSettingsModel.fromJson(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Map<String, dynamic> _extract(Map<String, dynamic>? body) {
    if (body == null || body['success'] != true) {
      throw const ServerException(message: 'Beklenmeyen API yanıtı');
    }
    return body['data'] as Map<String, dynamic>;
  }
}
