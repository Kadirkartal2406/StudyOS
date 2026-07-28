import 'package:dio/dio.dart';
import 'package:intl/intl.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/study_plan_model.dart';

/// Backend `/study-plans` endpoint'lerine doğrudan erişen datasource.
/// Yalnızca ham API çağrıları içerir — iş mantığı yok.
class StudyPlanRemoteDatasource {
  const StudyPlanRemoteDatasource(this._dio);

  final Dio _dio;

  static final DateFormat _dateFormat = DateFormat('yyyy-MM-dd');

  /// GET /study-plans?study_date=YYYY-MM-DD
  Future<List<StudyPlanModel>> getPlans(DateTime studyDate) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studyPlans,
        queryParameters: {'study_date': _dateFormat.format(studyDate)},
      );
      final data = _extractData(response.data);
      return (data as List<dynamic>)
          .map((json) => StudyPlanModel.fromJson(json as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// GET /study-plans/{id}
  Future<StudyPlanModel> getPlan(String id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studyPlan(id),
      );
      final data = _extractData(response.data);
      return StudyPlanModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// POST /study-plans
  Future<StudyPlanModel> createPlan(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studyPlans,
        data: body,
      );
      final data = _extractData(response.data);
      return StudyPlanModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// PUT /study-plans/{id}
  Future<StudyPlanModel> updatePlan(
    String id,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _dio.put<Map<String, dynamic>>(
        ApiEndpoints.studyPlan(id),
        data: body,
      );
      final data = _extractData(response.data);
      return StudyPlanModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// DELETE /study-plans/{id}
  Future<void> deletePlan(String id) async {
    try {
      await _dio.delete<void>(ApiEndpoints.studyPlan(id));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// PATCH /study-plans/{id}/start
  Future<StudyPlanModel> startPlan(String id) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.studyPlanStart(id),
      );
      final data = _extractData(response.data);
      return StudyPlanModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// PATCH /study-plans/{id}/complete
  Future<StudyPlanModel> completePlan(
    String id, {
    int? completedQuestionCount,
    int? completedMinutes,
  }) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.studyPlanComplete(id),
        data: {
          if (completedQuestionCount != null)
            'completed_question_count': completedQuestionCount,
          if (completedMinutes != null) 'completed_minutes': completedMinutes,
        },
      );
      final data = _extractData(response.data);
      return StudyPlanModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// PATCH /study-plans/{id}/skip
  Future<StudyPlanModel> skipPlan(String id) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.studyPlanSkip(id),
      );
      final data = _extractData(response.data);
      return StudyPlanModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// API yanıtındaki `data` alanını çıkarır; hata durumunda exception fırlatır.
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
