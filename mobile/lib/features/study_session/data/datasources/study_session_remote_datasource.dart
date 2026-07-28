import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../models/study_session_model.dart';

/// Backend `/study-sessions` endpoint'lerine erişen datasource.
class StudySessionRemoteDatasource {
  const StudySessionRemoteDatasource(this._dio);

  final Dio _dio;

  Future<StudySessionModel> start(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studySessionsStart,
        data: body,
      );
      final data = _extractData(response.data);
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudySessionModel> pause() async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studySessionsPause,
      );
      final data = _extractData(response.data);
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudySessionModel> resume() async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studySessionsResume,
      );
      final data = _extractData(response.data);
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudySessionModel> finish(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studySessionsFinish,
        data: body,
      );
      final data = _extractData(response.data);
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudySessionModel> startBreak() async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studySessionsBreakStart,
      );
      final data = _extractData(response.data);
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudySessionModel> endBreak() async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.studySessionsBreakEnd,
      );
      final data = _extractData(response.data);
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<Map<String, dynamic>> todaySummary() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studySessionsTodaySummary,
      );
      final data = _extractData(response.data);
      if (data is Map<String, dynamic>) return data;
      return {};
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// M25 — aktif oturum; yoksa null.
  Future<StudySessionModel?> getActive() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studySessionsActive,
      );
      final data = _extractData(response.data);
      if (data == null) return null;
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<StudySessionModel>> getToday() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studySessionsToday,
      );
      final data = _extractData(response.data);
      return (data as List<dynamic>)
          .map(
            (json) =>
                StudySessionModel.fromJson(json as Map<String, dynamic>),
          )
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudySessionHistoryPage> getHistory({
    int page = 1,
    int pageSize = 20,
    DateTime? dateFrom,
    DateTime? dateTo,
    String? studyPlanId,
    String? status,
    String? q,
  }) async {
    try {
      final query = <String, dynamic>{
        'page': page,
        'page_size': pageSize,
        if (dateFrom != null)
          'date_from':
              '${dateFrom.year.toString().padLeft(4, '0')}-${dateFrom.month.toString().padLeft(2, '0')}-${dateFrom.day.toString().padLeft(2, '0')}',
        if (dateTo != null)
          'date_to':
              '${dateTo.year.toString().padLeft(4, '0')}-${dateTo.month.toString().padLeft(2, '0')}-${dateTo.day.toString().padLeft(2, '0')}',
        if (studyPlanId != null) 'study_plan_id': studyPlanId,
        if (status != null) 'status': status,
        if (q != null && q.isNotEmpty) 'q': q,
      };
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studySessionsHistory,
        queryParameters: query,
      );
      final body = response.data;
      if (body == null || body['success'] != true) {
        throw const ServerException(message: 'Beklenmeyen API yanıtı');
      }
      final data = body['data'] as List<dynamic>;
      final pagination = body['pagination'] as Map<String, dynamic>? ?? {};
      return StudySessionHistoryPage(
        items: data
            .map(
              (json) =>
                  StudySessionModel.fromJson(json as Map<String, dynamic>),
            )
            .toList(),
        page: pagination['page'] as int? ?? page,
        pageSize: pagination['page_size'] as int? ?? pageSize,
        totalItems: pagination['total_items'] as int? ?? data.length,
        totalPages: pagination['total_pages'] as int? ?? 1,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<StudySessionModel> getById(String id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.studySession(id),
      );
      final data = _extractData(response.data);
      return StudySessionModel.fromJson(data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  dynamic _extractData(Map<String, dynamic>? body) {
    if (body == null || body['success'] != true) {
      throw const ServerException(message: 'Beklenmeyen API yanıtı');
    }
    return body['data'];
  }
}
