import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/ai_coach_models.dart';

class AiCoachRemoteDatasource {
  const AiCoachRemoteDatasource(this._dio);

  final Dio _dio;

  Future<AiOverviewModel> getOverview() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.aiOverview,
      );
      return AiOverviewModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<AiRecommendationModel>> getRecommendations() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.aiRecommendations,
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final items = data['items'] as List<dynamic>? ?? [];
      return items
          .map(
            (e) => AiRecommendationModel.fromJson(e as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AiTrendsModel> getTrends() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.aiTrends,
      );
      return AiTrendsModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AiPerformanceModel> getPerformance() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.aiPerformance,
      );
      return AiPerformanceModel.fromJson(
        _extractData(response.data) as Map<String, dynamic>,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AiProductivityModel> getProductivity() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.aiProductivity,
      );
      return AiProductivityModel.fromJson(
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
