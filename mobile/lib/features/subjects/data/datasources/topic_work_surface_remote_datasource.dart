import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/topic_work_surface_entity.dart';

class TopicWorkSurfaceRemoteDatasource {
  const TopicWorkSurfaceRemoteDatasource(this._dio);

  final Dio _dio;

  Future<TopicWorkSurfaceEntity> getWorkSurface({
    required String subjectCode,
    required String topicCode,
  }) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.topicWorkSurface(subjectCode, topicCode),
      );
      final data = response.data;
      if (data is! Map<String, dynamic> ||
          data['data'] is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Geçersiz Work Surface yanıtı');
      }
      return _parse(data['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  TopicWorkSurfaceEntity _parse(Map<String, dynamic> json) {
    final state = json['learning_state'] as Map<String, dynamic>? ?? {};
    final action = json['primary_action'] as Map<String, dynamic>? ?? {};
    final tools = (json['secondary_tools'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => TopicSecondaryToolEntity(
            id: m['id'] as String? ?? '',
            label: m['label'] as String? ?? '',
            deepLinkHint: m['deep_link_hint'] as String? ?? '',
          ),
        )
        .toList();

    final intelJson = json['intelligence'] as Map<String, dynamic>?;
    TopicIntelligenceEntity? intelligence;
    if (intelJson != null) {
      intelligence = TopicIntelligenceEntity(
        topicName: intelJson['topic_name'] as String? ?? '',
        headline: intelJson['headline'] as String? ?? '',
        stars: intelJson['stars'] as int? ?? 0,
        lastStudiedLabel: intelJson['last_studied_label'] as String?,
        lastQuizLabel: intelJson['last_quiz_label'] as String?,
        confidenceLabel: intelJson['confidence_label'] as String? ?? 'Bilinmiyor',
        confidenceLevel: intelJson['confidence_level'] as String? ?? 'unknown',
        weakSpot: intelJson['weak_spot'] as String?,
        suggestion: intelJson['suggestion'] as String?,
      );
    }

    final timeline = (json['timeline'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => TimelineEventEntity(
            id: m['id'] as String? ?? '',
            kind: m['kind'] as String? ?? 'activity',
            title: m['title'] as String? ?? '',
            subtitle: m['subtitle'] as String?,
            relativeLabel: m['relative_label'] as String? ?? '',
            deepLinkHint: m['deep_link_hint'] as String?,
          ),
        )
        .toList();

    final insights = (json['insights'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => InsightCardEntity(
            id: m['id'] as String? ?? '',
            code: m['code'] as String? ?? '',
            message: m['message'] as String? ?? '',
            tone: m['tone'] as String? ?? 'neutral',
            subjectCode: m['subject_code'] as String?,
            topicCode: m['topic_code'] as String?,
            topicName: m['topic_name'] as String?,
            deepLinkHint: m['deep_link_hint'] as String?,
          ),
        )
        .toList();

    final quizHistory = (json['quiz_history'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => QuizHistoryItemEntity(
            id: m['id'] as String? ?? '',
            questionCount: m['question_count'] as int? ?? 0,
            accuracyPct: (m['accuracy_pct'] as num?)?.toDouble(),
            correctCount: m['correct_count'] as int?,
            status: m['status'] as String? ?? '',
            relativeLabel: m['relative_label'] as String? ?? '',
            difficulty: m['difficulty'] as String? ?? 'medium',
          ),
        )
        .toList();

    final resources = (json['resources'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(
          (m) => ResourceIntelligenceEntity(
            id: m['id'] as String? ?? '',
            title: m['title'] as String? ?? '',
            intelligenceLabel: m['intelligence_label'] as String? ?? '',
            resourceType: m['resource_type'] as String? ?? 'other',
            status: m['status'] as String? ?? 'not_started',
            url: m['url'] as String?,
            knowledgeHealth: m['knowledge_health'] as String?,
            chunkCount: m['chunk_count'] as int? ?? 0,
            citationCount: m['citation_count'] as int? ?? 0,
            quizGeneratedCount: m['quiz_generated_count'] as int? ?? 0,
            usedByAi: m['used_by_ai'] as bool? ?? false,
          ),
        )
        .toList();

    return TopicWorkSurfaceEntity(
      learningState: TopicLearningStateEntity(
        subjectCode: state['subject_code'] as String? ?? '',
        topicCode: state['topic_code'] as String? ?? '',
        topicName: state['topic_name'] as String? ?? '',
        subjectName: state['subject_name'] as String?,
        summaryLine: state['summary_line'] as String?,
        revisionDue: state['revision_due'] as bool? ?? false,
        studyMinutes: state['study_minutes'] as int? ?? 0,
        sessionCount: state['session_count'] as int? ?? 0,
        correctCount: state['correct_count'] as int? ?? 0,
        wrongCount: state['wrong_count'] as int? ?? 0,
        blankCount: state['blank_count'] as int? ?? 0,
        questionCount: state['question_count'] as int? ?? 0,
        accuracyPct: (state['accuracy_pct'] as num?)?.toDouble() ?? 0,
      ),
      primaryAction: TopicPrimaryActionEntity(
        title: action['title'] as String? ?? '',
        subtitle: action['subtitle'] as String?,
        reason: action['reason'] as String? ?? '',
        actionType: action['action_type'] as String? ?? 'focus',
        deepLinkHint: action['deep_link_hint'] as String? ?? '',
        ctaLabel: action['cta_label'] as String? ?? 'Başla',
        confidenceTone: action['confidence_tone'] as String? ?? 'high',
        subjectCode: action['subject_code'] as String?,
        topicCode: action['topic_code'] as String?,
        purpose: action['purpose'] as String?,
        toolHint: action['tool_hint'] as String?,
      ),
      secondaryTools: tools,
      intelligence: intelligence,
      timeline: timeline,
      insights: insights,
      quizHistory: quizHistory,
      resources: resources,
      coachHeadline: json['coach_headline'] as String?,
      coachBody: json['coach_body'] as String?,
      coachCtaLabel: json['coach_cta_label'] as String?,
      coachDeepLinkHint: json['coach_deep_link_hint'] as String?,
    );
  }
}
