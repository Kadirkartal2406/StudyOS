import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/ai_settings_model.dart';

class AiSettingsRemoteDatasource {
  const AiSettingsRemoteDatasource(this._dio);

  final Dio _dio;

  Future<AiSettingsModel> getSettings() async {
    try {
      final response =
          await _dio.get<Map<String, dynamic>>(ApiEndpoints.aiSettings);
      return AiSettingsModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AiSettingsModel> updateSettings({
    String? preferredProvider,
    String? preferredModel,
  }) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.aiSettings,
        data: {
          if (preferredProvider != null) 'preferred_provider': preferredProvider,
          if (preferredModel != null) 'preferred_model': preferredModel,
        },
      );
      return AiSettingsModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  dynamic _extractData(Map<String, dynamic>? responseData) {
    if (responseData == null) {
      throw const NetworkException(message: 'Boş yanıt alındı');
    }
    final success = responseData['success'] as bool? ?? false;
    if (!success) {
      final error = responseData['error'] as Map<String, dynamic>?;
      final message = error?['message'] as String? ?? 'Bilinmeyen hata';
      throw UnknownException(message: message);
    }
    return responseData['data'];
  }
}
