import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/revision_entity.dart';

class RevisionRemoteDatasource {
  const RevisionRemoteDatasource(this._dio);

  final Dio _dio;

  Future<List<RevisionItemEntity>> listToday() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.revisionsToday,
      );
      return _listFrom(response.data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<RevisionItemEntity>> listOverdue() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.revisionsOverdue,
      );
      return _listFrom(response.data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<RevisionItemEntity>> listAll() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.revisions,
      );
      return _listFrom(response.data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<RevisionItemEntity> create(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.revisions,
        data: body,
      );
      return _itemFromJson(_extractData(response.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<RevisionItemEntity> review(String id, String grade) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.revisionReview(id),
        data: {'grade': grade},
      );
      return _itemFromJson(_extractData(response.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<RevisionItemEntity> skip(String id, {int days = 1}) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.revisionSkip(id),
        data: {'days': days},
      );
      return _itemFromJson(_extractData(response.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<RevisionItemEntity> postpone(String id, {int days = 1}) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.revisionPostpone(id),
        data: {'days': days},
      );
      return _itemFromJson(_extractData(response.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<RevisionExplainEntity> explain(String id) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.revisionExplain(id),
      );
      final json = _extractData(response.data) as Map<String, dynamic>;
      return RevisionExplainEntity(
        revisionId: json['revision_id'] as String,
        explanation: json['explanation'] as String? ?? '',
        provider: json['provider'] as String? ?? 'null',
        reason: json['reason'] as String? ?? '',
        difficulty: json['difficulty'] as int? ?? 3,
        usedFallback: json['used_fallback'] as bool? ?? false,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<RevisionGenerateResult> generate() async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.revisionsGenerate,
        data: {
          'include_questions': true,
          'include_exams': true,
          'max_items': 8,
        },
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      final created = (data['created'] as List<dynamic>? ?? [])
          .map((e) => _itemFromJson(e as Map<String, dynamic>))
          .toList();
      return RevisionGenerateResult(
        created: created,
        skippedExisting: data['skipped_existing'] as int? ?? 0,
        message: data['message'] as String? ?? '',
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<RevisionStatisticsEntity> statistics() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.revisionsStatistics,
      );
      final json = _extractData(response.data) as Map<String, dynamic>;
      return RevisionStatisticsEntity(
        totalActive: json['total_active'] as int? ?? 0,
        totalMastered: json['total_mastered'] as int? ?? 0,
        dueToday: json['due_today'] as int? ?? 0,
        overdue: json['overdue'] as int? ?? 0,
        dueThisWeek: json['due_this_week'] as int? ?? 0,
        reviewedToday: json['reviewed_today'] as int? ?? 0,
        reviewedThisWeek: json['reviewed_this_week'] as int? ?? 0,
        averageDifficulty:
            (json['average_difficulty'] as num?)?.toDouble() ?? 0,
        averageEase: (json['average_ease'] as num?)?.toDouble() ?? 0,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  List<RevisionItemEntity> _listFrom(Map<String, dynamic>? body) {
    final data = _extractData(body) as List<dynamic>? ?? [];
    return data
        .map((e) => _itemFromJson(e as Map<String, dynamic>))
        .toList();
  }

  RevisionItemEntity _itemFromJson(Map<String, dynamic> json) {
    final scheduleJson = json['schedule'] as Map<String, dynamic>?;
    return RevisionItemEntity(
      id: json['id'] as String,
      title: json['title'] as String? ?? '',
      subject: json['subject'] as String? ?? '',
      topic: json['topic'] as String?,
      note: json['note'] as String?,
      sourceType: json['source_type'] as String? ?? 'manual',
      sourceId: json['source_id'] as String?,
      difficulty: json['difficulty'] as int? ?? 3,
      reason: json['reason'] as String? ?? '',
      status: json['status'] as String? ?? 'active',
      schedule: scheduleJson == null
          ? null
          : RevisionScheduleEntity(
              dueAt: DateTime.parse(scheduleJson['due_at'] as String),
              intervalDays: scheduleJson['interval_days'] as int? ?? 1,
              easeFactor:
                  (scheduleJson['ease_factor'] as num?)?.toDouble() ?? 2.5,
              repetitionCount: scheduleJson['repetition_count'] as int? ?? 0,
              lapseCount: scheduleJson['lapse_count'] as int? ?? 0,
              lastReviewedAt: scheduleJson['last_reviewed_at'] == null
                  ? null
                  : DateTime.parse(
                      scheduleJson['last_reviewed_at'] as String,
                    ),
            ),
    );
  }

  dynamic _extractData(Map<String, dynamic>? body) {
    if (body == null) return null;
    return body['data'];
  }
}

class RevisionGenerateResult {
  const RevisionGenerateResult({
    required this.created,
    required this.skippedExisting,
    required this.message,
  });

  final List<RevisionItemEntity> created;
  final int skippedExisting;
  final String message;
}
