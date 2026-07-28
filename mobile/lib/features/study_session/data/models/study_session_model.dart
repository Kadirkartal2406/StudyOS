import '../../domain/entities/study_session_entity.dart';
import '../../domain/entities/study_session_status.dart';

/// API JSON → domain entity dönüşümü.
class StudySessionModel {
  const StudySessionModel({
    required this.id,
    required this.userId,
    required this.startedAt,
    required this.plannedDurationMinutes,
    required this.actualDurationMinutes,
    required this.breakDurationMinutes,
    required this.completedQuestions,
    required this.completedTopics,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.studyPlanId,
    this.endedAt,
    this.planTitle,
    this.planSubject,
    this.mode = 'pomodoro',
    this.phase = 'focus',
    this.actualBreakMinutes = 0,
    this.subjectCode,
    this.topicCode,
    this.engineState,
    this.breakStartedAt,
    this.pausedAt,
    this.pausedSeconds = 0,
  });

  final String id;
  final String userId;
  final String? studyPlanId;
  final DateTime startedAt;
  final DateTime? endedAt;
  final int plannedDurationMinutes;
  final int actualDurationMinutes;
  final int breakDurationMinutes;
  final int completedQuestions;
  final int completedTopics;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? planTitle;
  final String? planSubject;
  final String mode;
  final String phase;
  final int actualBreakMinutes;
  final String? subjectCode;
  final String? topicCode;
  final String? engineState;
  final DateTime? breakStartedAt;
  final DateTime? pausedAt;
  final int pausedSeconds;

  factory StudySessionModel.fromJson(Map<String, dynamic> json) {
    return StudySessionModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      studyPlanId: json['study_plan_id'] as String?,
      startedAt: DateTime.parse(json['started_at'] as String),
      endedAt: json['ended_at'] != null
          ? DateTime.parse(json['ended_at'] as String)
          : null,
      plannedDurationMinutes: json['planned_duration_minutes'] as int? ?? 0,
      actualDurationMinutes: json['actual_duration_minutes'] as int? ?? 0,
      breakDurationMinutes: json['break_duration_minutes'] as int? ?? 0,
      completedQuestions: json['completed_questions'] as int? ?? 0,
      completedTopics: json['completed_topics'] as int? ?? 0,
      status: json['status'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      planTitle: json['plan_title'] as String?,
      planSubject: json['plan_subject'] as String?,
      mode: json['mode'] as String? ?? 'pomodoro',
      phase: json['phase'] as String? ?? 'focus',
      actualBreakMinutes: json['actual_break_minutes'] as int? ?? 0,
      subjectCode: json['subject_code'] as String?,
      topicCode: json['topic_code'] as String?,
      engineState: json['engine_state'] as String?,
      breakStartedAt: json['break_started_at'] != null
          ? DateTime.parse(json['break_started_at'] as String)
          : null,
      pausedAt: json['paused_at'] != null
          ? DateTime.parse(json['paused_at'] as String)
          : null,
      pausedSeconds: json['paused_seconds'] as int? ?? 0,
    );
  }

  StudySessionEntity toEntity() {
    final statusEnum = StudySessionStatus.fromApi(status);
    final resolvedEngine = engineState != null
        ? StudyEngineStateX.fromApi(engineState)
        : StudyEngineStateX.fromStatusAndPhase(
            status: statusEnum,
            phase: phase,
          );
    return StudySessionEntity(
      id: id,
      userId: userId,
      studyPlanId: studyPlanId,
      startedAt: startedAt,
      endedAt: endedAt,
      plannedDurationMinutes: plannedDurationMinutes,
      actualDurationMinutes: actualDurationMinutes,
      breakDurationMinutes: breakDurationMinutes,
      completedQuestions: completedQuestions,
      completedTopics: completedTopics,
      status: statusEnum,
      createdAt: createdAt,
      updatedAt: updatedAt,
      planTitle: planTitle,
      planSubject: planSubject,
      mode: mode,
      phase: phase,
      actualBreakMinutes: actualBreakMinutes,
      subjectCode: subjectCode,
      topicCode: topicCode,
      engineState: resolvedEngine,
      breakStartedAt: breakStartedAt,
      pausedAt: pausedAt,
      pausedSeconds: pausedSeconds,
    );
  }
}

class StudySessionHistoryPage {
  const StudySessionHistoryPage({
    required this.items,
    required this.page,
    required this.pageSize,
    required this.totalItems,
    required this.totalPages,
  });

  final List<StudySessionModel> items;
  final int page;
  final int pageSize;
  final int totalItems;
  final int totalPages;

  bool get hasMore => page < totalPages;
}
