import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/constants/api_endpoints.dart';
import '../../../core/errors/app_exception.dart';
import '../../../core/errors/dio_exception_mapper.dart';
import '../../../core/network/dio_client.dart';

class AssessmentQuestionItem {
  const AssessmentQuestionItem({
    required this.id,
    required this.ordIndex,
    required this.stem,
    required this.choices,
    this.subjectCode,
    this.topicCode,
    this.subjectName,
    this.eaeInteraction,
  });

  final String id;
  final int ordIndex;
  final String stem;
  final Map<String, String> choices;
  final String? subjectCode;
  final String? topicCode;
  final String? subjectName;
  final Map<String, dynamic>? eaeInteraction;

  bool get isMathSubject {
    final c = (subjectCode ?? '').toLowerCase();
    return c.contains('matematik') || c.contains('geometri');
  }

  factory AssessmentQuestionItem.fromJson(Map<String, dynamic> json) {
    final raw = json['choices'];
    final choices = <String, String>{};
    if (raw is Map) {
      for (final e in raw.entries) {
        choices['${e.key}'] = '${e.value}';
      }
    }
    return AssessmentQuestionItem(
      id: json['id'] as String,
      ordIndex: json['ord_index'] as int? ?? 0,
      stem: json['stem'] as String? ?? '',
      choices: choices,
      subjectCode: json['subject_code'] as String?,
      topicCode: json['topic_code'] as String?,
      subjectName: json['subject_name'] as String?,
      eaeInteraction: json['eae_interaction'] as Map<String, dynamic>?,
    );
  }
}

class AssessmentSessionEntity {
  const AssessmentSessionEntity({
    required this.id,
    required this.kind,
    required this.status,
    required this.questions,
    this.subjectCode,
    this.topicCode,
    this.subjectName,
    this.topicName,
    this.commentary,
    this.accuracy,
    this.correctCount,
    this.wrongCount,
    this.blankCount,
    this.isBooklet = false,
    this.requestedCount,
    this.generationProgress = 0,
    this.sectionPlan,
  });

  final String id;
  final String kind;
  final String status;
  final String? subjectCode;
  final String? topicCode;
  final String? subjectName;
  final String? topicName;
  final String? commentary;
  final double? accuracy;
  final int? correctCount;
  final int? wrongCount;
  final int? blankCount;
  final bool isBooklet;
  final int? requestedCount;
  final int generationProgress;
  final Map<String, dynamic>? sectionPlan;
  final List<AssessmentQuestionItem> questions;

  factory AssessmentSessionEntity.fromJson(Map<String, dynamic> json) {
    final questions = (json['questions'] as List<dynamic>? ?? [])
        .whereType<Map<String, dynamic>>()
        .map(AssessmentQuestionItem.fromJson)
        .toList()
      ..sort((a, b) => a.ordIndex.compareTo(b.ordIndex));
    final planRaw = json['section_plan'];
    return AssessmentSessionEntity(
      id: json['id'] as String,
      kind: json['kind'] as String? ?? '',
      status: json['status'] as String? ?? '',
      subjectCode: json['subject_code'] as String?,
      topicCode: json['topic_code'] as String?,
      subjectName: json['subject_name'] as String?,
      topicName: json['topic_name'] as String?,
      commentary: json['commentary'] as String?,
      accuracy: (json['accuracy'] as num?)?.toDouble(),
      correctCount: json['correct_count'] as int?,
      wrongCount: json['wrong_count'] as int?,
      blankCount: json['blank_count'] as int?,
      isBooklet: json['is_booklet'] as bool? ?? false,
      requestedCount: json['requested_count'] as int?,
      generationProgress: json['generation_progress'] as int? ?? 0,
      sectionPlan: planRaw is Map<String, dynamic>
          ? planRaw
          : (planRaw is Map
              ? planRaw.map((k, v) => MapEntry(k.toString(), v))
              : null),
      questions: questions,
    );
  }
}

class AssessmentReviewItem {
  const AssessmentReviewItem({
    required this.id,
    required this.ordIndex,
    required this.stem,
    required this.choices,
    required this.correctKey,
    this.explanation,
    this.selectedKey,
    this.isCorrect,
    this.eaeInteraction,
  });

  final String id;
  final int ordIndex;
  final String stem;
  final Map<String, String> choices;
  final String correctKey;
  final String? explanation;
  final String? selectedKey;
  final bool? isCorrect;
  final Map<String, dynamic>? eaeInteraction;

  factory AssessmentReviewItem.fromJson(Map<String, dynamic> json) {
    final raw = json['choices'];
    final choices = <String, String>{};
    if (raw is Map) {
      for (final e in raw.entries) {
        choices['${e.key}'] = '${e.value}';
      }
    }
    return AssessmentReviewItem(
      id: json['id'] as String,
      ordIndex: json['ord_index'] as int? ?? 0,
      stem: json['stem'] as String? ?? '',
      choices: choices,
      correctKey: json['correct_key'] as String? ?? '',
      explanation: json['explanation'] as String?,
      selectedKey: json['selected_key'] as String?,
      isCorrect: json['is_correct'] as bool?,
      eaeInteraction: json['eae_interaction'] as Map<String, dynamic>?,
    );
  }
}

class AssessmentWrongExplainEntity {
  const AssessmentWrongExplainEntity({
    required this.questionId,
    required this.explanation,
    this.whyWrong,
    this.whyCorrect,
    this.cached = false,
    this.provider = 'ai',
  });

  final String questionId;
  final String explanation;
  final String? whyWrong;
  final String? whyCorrect;
  final bool cached;
  final String provider;

  factory AssessmentWrongExplainEntity.fromJson(Map<String, dynamic> json) {
    return AssessmentWrongExplainEntity(
      questionId: json['question_id'] as String? ?? '',
      explanation: json['explanation'] as String? ?? '',
      whyWrong: json['why_wrong'] as String?,
      whyCorrect: json['why_correct'] as String?,
      cached: json['cached'] as bool? ?? false,
      provider: json['provider'] as String? ?? 'ai',
    );
  }
}

class AssessmentSubjectBreakdownEntity {
  const AssessmentSubjectBreakdownEntity({
    required this.subjectCode,
    required this.subjectName,
    required this.correct,
    required this.wrong,
    required this.blank,
    required this.net,
    required this.total,
  });

  final String subjectCode;
  final String subjectName;
  final int correct;
  final int wrong;
  final int blank;
  final double net;
  final int total;

  factory AssessmentSubjectBreakdownEntity.fromJson(Map<String, dynamic> json) {
    return AssessmentSubjectBreakdownEntity(
      subjectCode: json['subject_code'] as String? ?? '',
      subjectName: json['subject_name'] as String? ?? '',
      correct: (json['correct'] as num?)?.toInt() ?? 0,
      wrong: (json['wrong'] as num?)?.toInt() ?? 0,
      blank: (json['blank'] as num?)?.toInt() ?? 0,
      net: (json['net'] as num?)?.toDouble() ?? 0,
      total: (json['total'] as num?)?.toInt() ?? 0,
    );
  }
}

class AssessmentTopicBreakdownEntity {
  const AssessmentTopicBreakdownEntity({
    required this.topicCode,
    required this.topicName,
    required this.correct,
    required this.wrong,
    required this.blank,
    required this.total,
    this.subjectCode,
  });

  final String topicCode;
  final String topicName;
  final String? subjectCode;
  final int correct;
  final int wrong;
  final int blank;
  final int total;

  factory AssessmentTopicBreakdownEntity.fromJson(Map<String, dynamic> json) {
    return AssessmentTopicBreakdownEntity(
      topicCode: json['topic_code'] as String? ?? '',
      topicName: json['topic_name'] as String? ?? '',
      subjectCode: json['subject_code'] as String?,
      correct: (json['correct'] as num?)?.toInt() ?? 0,
      wrong: (json['wrong'] as num?)?.toInt() ?? 0,
      blank: (json['blank'] as num?)?.toInt() ?? 0,
      total: (json['total'] as num?)?.toInt() ?? 0,
    );
  }
}

class AssessmentSubmitResultEntity {
  const AssessmentSubmitResultEntity({
    required this.session,
    required this.reviewItems,
    required this.commentary,
    this.estimatedSuccessPct,
    this.net,
    this.scoreFormula,
    this.bySubject = const [],
    this.byTopic = const [],
  });

  final AssessmentSessionEntity session;
  final List<AssessmentReviewItem> reviewItems;
  final String commentary;
  final double? estimatedSuccessPct;
  final double? net;
  final String? scoreFormula;
  final List<AssessmentSubjectBreakdownEntity> bySubject;
  final List<AssessmentTopicBreakdownEntity> byTopic;

  factory AssessmentSubmitResultEntity.fromJson(Map<String, dynamic> json) {
    final sessionRaw = json['session'];
    return AssessmentSubmitResultEntity(
      session: AssessmentSessionEntity.fromJson(
        sessionRaw is Map<String, dynamic> ? sessionRaw : {},
      ),
      reviewItems: (json['review_items'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(AssessmentReviewItem.fromJson)
          .toList()
        ..sort((a, b) => a.ordIndex.compareTo(b.ordIndex)),
      commentary: json['commentary'] as String? ?? '',
      estimatedSuccessPct: (json['estimated_success_pct'] as num?)?.toDouble(),
      net: (json['net'] as num?)?.toDouble(),
      scoreFormula: json['score_formula'] as String?,
      bySubject: (json['by_subject'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(AssessmentSubjectBreakdownEntity.fromJson)
          .toList(),
      byTopic: (json['by_topic'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(AssessmentTopicBreakdownEntity.fromJson)
          .toList(),
    );
  }
}

class AssessmentProgressItemEntity {
  const AssessmentProgressItemEntity({
    required this.subjectCode,
    required this.subjectName,
    required this.completed,
    this.accuracy,
    this.sessionId,
  });

  final String subjectCode;
  final String subjectName;
  final bool completed;
  final double? accuracy;
  final String? sessionId;

  factory AssessmentProgressItemEntity.fromJson(Map<String, dynamic> json) {
    return AssessmentProgressItemEntity(
      subjectCode: json['subject_code'] as String? ?? '',
      subjectName: json['subject_name'] as String? ?? '',
      completed: json['completed'] as bool? ?? false,
      accuracy: (json['accuracy'] as num?)?.toDouble(),
      sessionId: json['session_id'] as String?,
    );
  }
}

class AssessmentOverviewEntity {
  const AssessmentOverviewEntity({
    required this.examType,
    required this.progressPct,
    required this.completedSubjects,
    required this.totalSubjects,
    required this.message,
    required this.subjects,
    this.coachSummary,
    this.coachCriticalSubject,
    this.coachNextTarget,
    this.coachRankLabel,
  });

  final String examType;
  final double progressPct;
  final int completedSubjects;
  final int totalSubjects;
  final String message;
  final List<AssessmentProgressItemEntity> subjects;
  final String? coachSummary;
  final String? coachCriticalSubject;
  final String? coachNextTarget;
  final String? coachRankLabel;

  factory AssessmentOverviewEntity.fromJson(Map<String, dynamic> json) {
    return AssessmentOverviewEntity(
      examType: json['exam_type'] as String? ?? '',
      progressPct: (json['progress_pct'] as num?)?.toDouble() ?? 0,
      completedSubjects: json['completed_subjects'] as int? ?? 0,
      totalSubjects: json['total_subjects'] as int? ?? 0,
      message: json['message'] as String? ?? '',
      subjects: (json['subjects'] as List<dynamic>? ?? [])
          .whereType<Map<String, dynamic>>()
          .map(AssessmentProgressItemEntity.fromJson)
          .toList(),
      coachSummary: json['coach_summary'] as String?,
      coachCriticalSubject: json['coach_critical_subject'] as String?,
      coachNextTarget: json['coach_next_target'] as String?,
      coachRankLabel: json['coach_rank_label'] as String?,
    );
  }
}

class AssessmentRemoteDatasource {
  const AssessmentRemoteDatasource(this._dio);

  final Dio _dio;

  Future<AssessmentOverviewEntity> overview() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.assessment,
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Geçersiz assessment yanıtı');
      }
      return AssessmentOverviewEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AssessmentSessionEntity> start({
    required String kind,
    String? subjectCode,
    String? topicCode,
    int? count,
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.assessmentStart,
        data: {
          'kind': kind,
          if (subjectCode != null) 'subject_code': subjectCode,
          if (topicCode != null) 'topic_code': topicCode,
          if (count != null) 'count': count,
        },
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Assessment başlatılamadı');
      }
      return AssessmentSessionEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AssessmentSessionEntity> startDaily({String? subjectCode}) async {
    try {
      // Ortak günlük pack klonu — kısa timeout yeterli
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.dailyChallengeStart,
        data: const {
          'kind': 'daily_challenge',
        },
        options: Options(
          sendTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 60),
        ),
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Günün denemesi başlatılamadı');
      }
      return AssessmentSessionEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<Map<String, dynamic>> dailyBundle() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.dailyChallenge,
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

  Future<List<Map<String, dynamic>>> dailyHistory() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        '${ApiEndpoints.dailyChallenge}/history',
      );
      final data = response.data?['data'];
      if (data is List) {
        return data.map((e) => Map<String, dynamic>.from(e as Map)).toList();
      }
      return [];
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<Map<String, dynamic>> dailySubjects() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.dailyChallengeSubjects,
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

  Future<List<int>> downloadSessionPdf(String sessionId) async {
    try {
      final response = await _dio.get<List<int>>(
        ApiEndpoints.assessmentSessionPdf(sessionId),
        options: Options(
          responseType: ResponseType.bytes,
          // JSON Accept PDF'i bozmasın / CORS preflight
          headers: const {'Accept': 'application/pdf,*/*'},
          sendTimeout: const Duration(seconds: 60),
          receiveTimeout: const Duration(seconds: 180),
        ),
      );
      final data = response.data;
      if (data == null || data.isEmpty) {
        throw const UnknownException(message: 'PDF indirilemedi');
      }
      return data;
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<int>> downloadSessionReportPdf(String sessionId) async {
    try {
      final response = await _dio.get<List<int>>(
        ApiEndpoints.assessmentSessionReportPdf(sessionId),
        options: Options(
          responseType: ResponseType.bytes,
          headers: const {'Accept': 'application/pdf,*/*'},
          sendTimeout: const Duration(seconds: 60),
          receiveTimeout: const Duration(seconds: 120),
        ),
      );
      final data = response.data;
      if (data == null || data.isEmpty) {
        throw const UnknownException(message: 'Rapor PDF indirilemedi');
      }
      return data;
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AssessmentWrongExplainEntity> explainWrong({
    required String sessionId,
    required String questionId,
    String? selectedKey,
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.assessmentQuestionExplain(sessionId, questionId),
        data: {
          if (selectedKey != null) 'selected_key': selectedKey,
        },
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Açıklama alınamadı');
      }
      return AssessmentWrongExplainEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<Map<String, dynamic>> dailyLeaderboard({String? subjectCode}) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.dailyChallengeLeaderboard,
        queryParameters: {
          if (subjectCode != null && subjectCode.isNotEmpty)
            'subject_code': subjectCode,
        },
      );
      final data = response.data?['data'];
      if (data is Map<String, dynamic>) return data;
      return {};
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AssessmentSessionEntity> getSession(String sessionId) async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.assessmentSession(sessionId),
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Assessment yüklenemedi');
      }
      return AssessmentSessionEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<AssessmentSubmitResultEntity> submit({
    required String sessionId,
    required Map<String, String?> answers,
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.assessmentSubmit(sessionId),
        data: {
          'answers': answers.entries
              .map(
                (e) => {
                  'question_id': e.key,
                  'selected_key': e.value,
                },
              )
              .toList(),
        },
      );
      final data = response.data?['data'];
      if (data is! Map<String, dynamic>) {
        throw const UnknownException(message: 'Assessment gönderilemedi');
      }
      return AssessmentSubmitResultEntity.fromJson(data);
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }
}

final assessmentDatasourceProvider = Provider<AssessmentRemoteDatasource>((ref) {
  return AssessmentRemoteDatasource(ref.watch(dioClientProvider));
});
