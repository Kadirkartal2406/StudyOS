import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/planner_entity.dart';

class PlannerRemoteDatasource {
  const PlannerRemoteDatasource(this._dio);

  final Dio _dio;

  Future<PlannerDraftEntity> generate(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.plannerGenerate,
        data: body,
      );
      return _draftFromJson(_extractData(response.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<PlannerDraftEntity> getDraft(String id) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.plannerDraft(id),
      );
      return _draftFromJson(_extractData(response.data) as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<PlannerDraftEntity> accept(String id, {bool force = false}) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.plannerAccept(id),
        data: {'force': force},
      );
      final data = _extractData(response.data) as Map<String, dynamic>;
      return _draftFromJson(data['draft'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<PlannerExplainEntity> explain(String id) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.plannerExplain(id),
      );
      final json = _extractData(response.data) as Map<String, dynamic>;
      return PlannerExplainEntity(
        draftId: json['draft_id'] as String,
        explanation: json['explanation'] as String? ?? '',
        provider: json['provider'] as String? ?? 'null',
        usedFallback: json['used_fallback'] as bool? ?? false,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  PlannerDraftEntity _draftFromJson(Map<String, dynamic> json) {
    final itemsJson = json['items'] as List<dynamic>? ?? [];
    final rationale = json['rationale'] as Map<String, dynamic>? ?? {};
    return PlannerDraftEntity(
      id: json['id'] as String,
      status: json['status'] as String? ?? 'draft',
      targetExam: json['target_exam'] as String? ?? 'tyt',
      targetNet: (json['target_net'] as num?)?.toDouble() ?? 0,
      availableDays: (json['available_days'] as List<dynamic>? ?? [])
          .map((e) => e as int)
          .toList(),
      availableHours: (json['available_hours'] as num?)?.toDouble() ?? 0,
      items: itemsJson.map((e) {
        final m = e as Map<String, dynamic>;
        return PlannerItemEntity(
          studyDate: DateTime.parse(m['study_date'] as String),
          title: m['title'] as String? ?? '',
          subject: m['subject'] as String? ?? '',
          topic: m['topic'] as String?,
          targetQuestionCount: m['target_question_count'] as int? ?? 0,
          estimatedMinutes: m['estimated_minutes'] as int? ?? 0,
          startTime: m['start_time'] as String?,
          endTime: m['end_time'] as String?,
          resourceIds: (m['resource_ids'] as List<dynamic>? ?? [])
              .map((x) => x.toString())
              .toList(),
          resourceTitles: (m['resource_titles'] as List<dynamic>? ?? [])
              .map((x) => x.toString())
              .toList(),
          reason: m['reason'] as String? ?? '',
        );
      }).toList(),
      summary: Map<String, dynamic>.from(json['summary'] as Map? ?? {}),
      rationale: Map<String, dynamic>.from(rationale),
      overviewReason: rationale['overview'] as String?,
    );
  }

  dynamic _extractData(Map<String, dynamic>? body) {
    if (body == null) return null;
    return body['data'];
  }
}
