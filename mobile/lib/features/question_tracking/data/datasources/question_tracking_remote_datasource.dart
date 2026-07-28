import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/question_record_entity.dart';
import '../models/question_record_model.dart';

class QuestionTrackingRemoteDatasource {
  const QuestionTrackingRemoteDatasource(this._dio);

  final Dio _dio;

  Future<(List<QuestionRecordModel>, Map<String, dynamic>)> list({
    int page = 1,
    int pageSize = 20,
    String? subject,
    String? topic,
    String? examType,
    String? source,
  }) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.questions,
        queryParameters: {
          'page': page,
          'page_size': pageSize,
          if (subject != null) 'subject': subject,
          if (topic != null) 'topic': topic,
          if (examType != null) 'exam_type': examType,
          if (source != null) 'source': source,
        },
      );
      final body = response.data;
      if (body == null || body['success'] != true) {
        throw const ServerException(message: 'Beklenmeyen API yanıtı');
      }
      final list = (body['data'] as List<dynamic>)
          .map((e) => QuestionRecordModel.fromJson(e as Map<String, dynamic>))
          .toList();
      final pagination = body['pagination'] as Map<String, dynamic>? ?? {};
      return (list, pagination);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<QuestionRecordModel> getById(String id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.question(id),
      );
      return QuestionRecordModel.fromJson(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<QuestionRecordModel> create(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.questions,
        data: body,
      );
      return QuestionRecordModel.fromJson(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<QuestionRecordModel> update(
    String id,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _dio.put<Map<String, dynamic>>(
        ApiEndpoints.question(id),
        data: body,
      );
      return QuestionRecordModel.fromJson(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<void> delete(String id) async {
    try {
      await _dio.delete<void>(ApiEndpoints.question(id));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<QuestionStatisticsOverviewModel> getStatistics() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.questionsStatistics,
      );
      return QuestionStatisticsOverviewModel.fromJson(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<QuestionDailyBucketEntity>> getDaily({int days = 14}) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.questionsDaily,
        queryParameters: {'days': days},
      );
      final data = _extract(response.data);
      final buckets = (data['buckets'] as List<dynamic>? ?? [])
          .map((e) {
            final m = e as Map<String, dynamic>;
            return QuestionDailyBucketEntity(
              date: m['date'] as String,
              questionCount: m['question_count'] as int? ?? 0,
              correctCount: m['correct_count'] as int? ?? 0,
              wrongCount: m['wrong_count'] as int? ?? 0,
              blankCount: m['blank_count'] as int? ?? 0,
              netScore: parseNetScore(m['net_score']),
              durationMinutes: m['duration_minutes'] as int? ?? 0,
            );
          })
          .toList();
      return buckets;
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<QuestionDistributionItemEntity>> getDistribution(
    String path,
  ) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(path);
      final data = _extract(response.data);
      return (data['items'] as List<dynamic>? ?? []).map((e) {
        final m = e as Map<String, dynamic>;
        return QuestionDistributionItemEntity(
          name: m['name'] as String,
          questionCount: m['question_count'] as int? ?? 0,
          correctCount: m['correct_count'] as int? ?? 0,
          wrongCount: m['wrong_count'] as int? ?? 0,
          blankCount: m['blank_count'] as int? ?? 0,
          netScore: parseNetScore(m['net_score']),
          durationMinutes: m['duration_minutes'] as int? ?? 0,
          correctRate: (m['correct_rate'] as num?)?.toDouble() ?? 0,
        );
      }).toList();
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
