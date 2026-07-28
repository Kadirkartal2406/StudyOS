import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/subject_hub_entity.dart';

class SubjectHubRemoteDatasource {
  const SubjectHubRemoteDatasource(this._dio);

  final Dio _dio;

  Future<SubjectHubEntity> getHub(String subjectCode) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.subjectHub(subjectCode),
      );
      final data = response.data;
      if (data is! Map<String, dynamic> || data['data'] is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Geçersiz Subject Hub yanıtı');
      }
      return _parse(data['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  SubjectHubEntity _parse(Map<String, dynamic> json) {
    final subject = json['subject'] as Map<String, dynamic>? ?? {};
    final progress = json['progress'] as Map<String, dynamic>? ?? {};
    final today = json['today'] as Map<String, dynamic>? ?? {};
    final revision = json['revision'] as Map<String, dynamic>? ?? {};
    final plans = json['plans'] as Map<String, dynamic>? ?? {};
    final exam = json['exam_summary'] as Map<String, dynamic>? ?? {};
    final resources = json['resources'] as Map<String, dynamic>? ?? {};
    final flashcards = json['flashcards'] as Map<String, dynamic>? ?? {};
    final topics = json['topics'] as Map<String, dynamic>? ?? {};
    final ai = json['ai'] as Map<String, dynamic>? ?? {};

    final topicItems = (topics['items'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => TopicCatalogItem(
            topicCode: m['code'] as String? ?? '',
            topicName: m['name'] as String? ?? '',
            subjectCode: m['subject_code'] as String? ?? '',
            sortOrder: m['sort_order'] as int? ?? 0,
            difficulty: m['difficulty'] as int?,
            isActive: m['is_active'] as bool? ?? true,
          ),
        )
        .toList();

    return SubjectHubEntity(
      subject: SubjectHubIdentity(
        subjectCode: subject['subject_code'] as String? ?? '',
        subjectName: subject['subject_name'] as String? ?? '',
        section: subject['section'] as String?,
        examTypes: (subject['exam_types'] as List<dynamic>? ?? [])
            .map((e) => e.toString())
            .toList(),
        isActive: subject['is_active'] as bool? ?? true,
        source: subject['source'] as String? ?? 'onboarding',
      ),
      progress: SubjectHubProgress(
        progressPct: (progress['progress_pct'] as num?)?.toDouble() ?? 0,
        accuracy: (progress['accuracy'] as num?)?.toDouble() ?? 0,
        totalQuestions: progress['total_questions'] as int? ?? 0,
        studyMinutes: progress['study_minutes'] as int? ?? 0,
        lastStudiedAt: _dt(progress['last_studied_at']),
        lastRevisionAt: _dt(progress['last_revision_at']),
      ),
      today: SubjectHubToday(
        studyMinutes: today['study_minutes'] as int? ?? 0,
        questionsSolved: today['questions_solved'] as int? ?? 0,
        planCount: today['plan_count'] as int? ?? 0,
        completedPlanCount: today['completed_plan_count'] as int? ?? 0,
      ),
      revision: SubjectHubRevision(
        dueToday: revision['due_today'] as int? ?? 0,
        overdue: revision['overdue'] as int? ?? 0,
        dueThisWeek: revision['due_this_week'] as int? ?? 0,
        nextTitle: revision['next_title'] as String?,
        overviewReason: revision['overview_reason'] as String?,
        available: revision['available'] as bool? ?? true,
      ),
      plans: SubjectHubPlans(
        todayCount: plans['today_count'] as int? ?? 0,
        completedCount: plans['completed_count'] as int? ?? 0,
        nextTitle: plans['next_title'] as String?,
        overviewReason: plans['overview_reason'] as String?,
        available: plans['available'] as bool? ?? true,
      ),
      examSummary: SubjectHubExamSummary(
        averageNet: (exam['average_net'] as num?)?.toDouble(),
        examCount: exam['exam_count'] as int? ?? 0,
        lastNet: (exam['last_net'] as num?)?.toDouble(),
        available: exam['available'] as bool? ?? false,
        placeholder: exam['placeholder'] as bool? ?? true,
      ),
      resources: SubjectHubResources(
        count: resources['count'] as int? ?? 0,
        recentTitles: (resources['recent_titles'] as List<dynamic>? ?? [])
            .map((e) => e.toString())
            .toList(),
        available: resources['available'] as bool? ?? false,
        placeholder: resources['placeholder'] as bool? ?? true,
      ),
      flashcards: SubjectHubFlashcards(
        enabled: flashcards['enabled'] as bool? ?? false,
        placeholder: flashcards['placeholder'] as bool? ?? true,
        message: flashcards['message'] as String? ?? 'Flashcards yakında',
      ),
      topics: SubjectHubTopics(
        items: topicItems,
        count: topics['count'] as int? ?? topicItems.length,
        available: topics['available'] as bool? ?? true,
      ),
      ai: SubjectHubAi(
        recommendation: ai['recommendation'] as String?,
        reason: ai['reason'] as String?,
        code: ai['code'] as String?,
        explainAvailable: ai['explain_available'] as bool? ?? false,
        explainPlaceholder: ai['explain_placeholder'] as String? ??
            'Explain yakında (Sprint-3.1.D)',
      ),
      activeExamType: json['active_exam_type'] as String?,
      primaryExamType: json['primary_exam_type'] as String?,
    );
  }

  DateTime? _dt(Object? value) {
    if (value == null) return null;
    return DateTime.tryParse(value.toString());
  }
}
