import 'package:dio/dio.dart';

import '../../../../core/constants/api_endpoints.dart';
import '../../../../core/errors/app_exception.dart';
import '../../../../core/errors/dio_exception_mapper.dart';
import '../../domain/entities/learning_profile_entity.dart';

class LearningProfileRemoteDatasource {
  const LearningProfileRemoteDatasource(this._dio);

  final Dio _dio;

  Future<OnboardingStatusEntity> status() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.onboardingStatus,
      );
      final json = _extract(response.data);
      return OnboardingStatusEntity(
        onboardingRequired: json['onboarding_required'] as bool? ?? true,
        onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
        onboardingSkipped: json['onboarding_skipped'] as bool? ?? false,
        journeyStage: json['journey_stage'] as String? ?? 'new_user',
        canSkip: json['can_skip'] as bool? ?? false,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<LearningProfileEntity> getProfile() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.learningProfile,
      );
      return _profile(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<LearningProfileEntity> complete(Map<String, dynamic> body) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.onboardingComplete,
        data: body,
      );
      return _profile(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<String> welcomeTone({
    required String step,
    required String firstName,
    String? examHint,
    String? lastAnswer,
  }) async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.onboardingWelcomeTone,
        data: {
          'step': step,
          'first_name': firstName,
          if (examHint != null) 'exam_hint': examHint,
          if (lastAnswer != null) 'last_answer': lastAnswer,
        },
        options: Options(
          sendTimeout: const Duration(seconds: 20),
          receiveTimeout: const Duration(seconds: 25),
        ),
      );
      final data = _extract(response.data);
      return data['text'] as String? ?? '';
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<LearningProfileEntity> skip() async {
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.onboardingSkip,
      );
      return _profile(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<LearningProfileEntity> setActiveExam(String examType) async {
    try {
      final response = await _dio.patch<Map<String, dynamic>>(
        ApiEndpoints.activeExam,
        data: {'exam_type': examType},
      );
      return _profile(_extract(response.data));
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  /// Yeni sınav hedefi ekle — dashboard'dan sonradan ekleme (Duolingo tarzı).
  Future<void> addExamTarget(Map<String, dynamic> body) async {
    try {
      await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.examTargets,
        data: body,
      );
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Future<List<UserSubjectEntity>> mySubjects() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(
        ApiEndpoints.mySubjects,
      );
      final data = response.data;
      final list = data is Map<String, dynamic> && data['data'] is List
          ? data['data'] as List<dynamic>
          : const <dynamic>[];
      return list
          .map((e) => e as Map<String, dynamic>)
          .map(
            (m) => UserSubjectEntity(
              id: m['id'] as String?,
              subjectCode: m['subject_code'] as String,
              subjectName: m['subject_name'] as String,
              isActive: m['is_active'] as bool? ?? true,
              section: m['section'] as String?,
              totalQuestions: m['total_questions'] as int? ?? 0,
              studyMinutes: m['study_minutes'] as int? ?? 0,
              accuracy: (m['accuracy'] as num?)?.toDouble() ?? 0,
              lastStudiedAt: m['last_studied_at'] == null
                  ? null
                  : DateTime.tryParse(m['last_studied_at'] as String),
              lastRevisionAt: m['last_revision_at'] == null
                  ? null
                  : DateTime.tryParse(m['last_revision_at'] as String),
              progressPct: (m['progress_pct'] as num?)?.toDouble() ?? 0,
            ),
          )
          .toList();
    } on DioException catch (e) {
      throw dioExceptionToAppException(e);
    }
  }

  Map<String, dynamic> _extract(dynamic data) {
    if (data is Map<String, dynamic> && data['data'] is Map<String, dynamic>) {
      return data['data'] as Map<String, dynamic>;
    }
    throw const UnknownException(message: 'Geçersiz yanıt');
  }

  LearningProfileEntity _profile(Map<String, dynamic> json) {
    final targets = (json['exam_targets'] as List<dynamic>? ?? [])
        .map((e) => e as Map<String, dynamic>)
        .map(
          (m) => ExamTargetEntity(
            id: m['id'] as String,
            examType: m['exam_type'] as String,
            isPrimary: m['is_primary'] as bool? ?? false,
            targetNet: (m['target_net'] as num?)?.toDouble(),
            targetScore: (m['target_score'] as num?)?.toDouble(),
            targetRank: m['target_rank'] as int?,
            targetUniversity: m['target_university'] as String?,
            targetDepartment: m['target_department'] as String?,
            branch: m['branch'] as String?,
            examDate: m['exam_date'] == null
                ? null
                : DateTime.tryParse(m['exam_date'] as String),
          ),
        )
        .toList();
    final subjects = (json['subjects'] as List<dynamic>? ?? [])
        .map((e) => e as Map<String, dynamic>)
        .map(
          (m) => UserSubjectEntity(
            id: m['id'] as String?,
            subjectCode: m['subject_code'] as String,
            subjectName: m['subject_name'] as String,
            isActive: m['is_active'] as bool? ?? true,
            section: m['section'] as String?,
            totalQuestions: m['total_questions'] as int? ?? 0,
            studyMinutes: m['study_minutes'] as int? ?? 0,
            accuracy: (m['accuracy'] as num?)?.toDouble() ?? 0,
            lastStudiedAt: m['last_studied_at'] == null
                ? null
                : DateTime.tryParse(m['last_studied_at'] as String),
            lastRevisionAt: m['last_revision_at'] == null
                ? null
                : DateTime.tryParse(m['last_revision_at'] as String),
            progressPct: (m['progress_pct'] as num?)?.toDouble() ?? 0,
          ),
        )
        .toList();
    String? primary = json['primary_exam_type'] as String?;
    if (primary == null || primary.isEmpty) {
      for (final t in targets) {
        if (t.isPrimary) {
          primary = t.examType;
          break;
        }
      }
      primary ??= targets.isEmpty ? null : targets.first.examType;
    }
    final active = (json['active_exam_type'] as String?) ?? primary;

    return LearningProfileEntity(
      userId: json['user_id'] as String,
      journeyStage: json['journey_stage'] as String? ?? 'new_user',
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
      onboardingSkipped: json['onboarding_skipped'] as bool? ?? false,
      onboardingRequired: json['onboarding_required'] as bool? ?? true,
      dailyStudyMinutes: json['daily_study_minutes'] as int? ?? 120,
      availableDays: (json['available_days'] as List<dynamic>? ?? [])
          .map((e) => e as int)
          .toList(),
      availableHours: (json['available_hours'] as num?)?.toDouble() ?? 2,
      baselineLevel: json['baseline_level'] as String? ?? 'unknown',
      baselineReason: json['baseline_reason'] as String?,
      examTargets: targets,
      subjects: subjects,
      primaryExamType: primary,
      activeExamType: active,
    );
  }
}
