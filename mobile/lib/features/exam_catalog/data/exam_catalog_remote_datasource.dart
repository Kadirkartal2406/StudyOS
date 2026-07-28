import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../../../core/network/dio_client.dart';

/// Sprint X — Exam Intelligence Catalog client (read-only).
/// Onboarding / Subject Hub bu API'den beslenecek; Decision Engine dokunulmaz.
class ExamCatalogApi {
  const ExamCatalogApi(this._dio);

  final Dio _dio;

  Future<List<Map<String, dynamic>>> listExams() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examCatalog,
      );
      return _asMapList(response.data?['data']);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<Map<String, dynamic>> getExamTree(String exam) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examCatalogExam(exam),
      );
      final data = response.data?['data'];
      if (data is Map<String, dynamic>) return data;
      if (data is Map) {
        return data.map((k, v) => MapEntry(k.toString(), v));
      }
      return {};
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<Map<String, dynamic>>> listPacks(String exam) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examCatalogPacks(exam),
      );
      return _asMapList(response.data?['data']);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<Map<String, dynamic>> getPack(String exam, String pack) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examCatalogPack(exam, pack),
      );
      final data = response.data?['data'];
      if (data is Map<String, dynamic>) return data;
      if (data is Map) {
        return data.map((k, v) => MapEntry(k.toString(), v));
      }
      return {};
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<Map<String, dynamic>>> listSubjects(
    String exam, {
    String? pack,
    String? branch,
  }) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examCatalogSubjects(exam),
        queryParameters: {
          if (pack != null) 'pack': pack,
          if (branch != null) 'branch': branch,
        },
      );
      return _asMapList(response.data?['data']);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<Map<String, dynamic>>> listTopics(
    String exam,
    String subject, {
    String? pack,
  }) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examCatalogSubjectTopics(exam, subject),
        queryParameters: {if (pack != null) 'pack': pack},
      );
      return _asMapList(response.data?['data']);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<Map<String, dynamic>> getTopic(String topicCode) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.examCatalogTopic(topicCode),
      );
      final data = response.data?['data'];
      if (data is Map<String, dynamic>) return data;
      if (data is Map) {
        return data.map((k, v) => MapEntry(k.toString(), v));
      }
      return {};
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  List<Map<String, dynamic>> _asMapList(Object? data) {
    if (data is! List) return const [];
    return data
        .whereType<Map>()
        .map((e) => e.map((k, v) => MapEntry(k.toString(), v)))
        .toList();
  }
}

final examCatalogApiProvider = Provider<ExamCatalogApi>((ref) {
  return ExamCatalogApi(ref.watch(dioClientProvider));
});
