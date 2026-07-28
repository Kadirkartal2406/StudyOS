import 'study_session_status.dart';

/// M25 — Study Session Engine state machine projection.
enum StudyEngineState {
  idle,
  studying,
  breakTime,
  paused,
  completed,
}

extension StudyEngineStateX on StudyEngineState {
  String get apiValue => switch (this) {
        StudyEngineState.idle => 'IDLE',
        StudyEngineState.studying => 'STUDYING',
        StudyEngineState.breakTime => 'BREAK',
        StudyEngineState.paused => 'PAUSED',
        StudyEngineState.completed => 'COMPLETED',
      };

  static StudyEngineState fromApi(String? raw) {
    switch ((raw ?? '').toUpperCase()) {
      case 'STUDYING':
        return StudyEngineState.studying;
      case 'BREAK':
        return StudyEngineState.breakTime;
      case 'PAUSED':
        return StudyEngineState.paused;
      case 'COMPLETED':
        return StudyEngineState.completed;
      default:
        return StudyEngineState.idle;
    }
  }

  /// status + phase → engine state (client-side fallback).
  static StudyEngineState fromStatusAndPhase({
    required StudySessionStatus status,
    required String phase,
  }) {
    if (status == StudySessionStatus.completed) {
      return StudyEngineState.completed;
    }
    if (status == StudySessionStatus.paused) {
      return StudyEngineState.paused;
    }
    if (status == StudySessionStatus.running) {
      if (phase == 'break') return StudyEngineState.breakTime;
      return StudyEngineState.studying;
    }
    return StudyEngineState.idle;
  }
}

/// Pomodoro çalışma oturumu — domain katmanında saf Dart nesnesi.
class StudySessionEntity {
  const StudySessionEntity({
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
    this.engineState = StudyEngineState.idle,
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
  final StudySessionStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? planTitle;
  final String? planSubject;
  final String mode;
  final String phase;
  final int actualBreakMinutes;
  final String? subjectCode;
  final String? topicCode;
  final StudyEngineState engineState;
  final DateTime? breakStartedAt;
  final DateTime? pausedAt;
  final int pausedSeconds;

  bool get isActive => status.isActive;
  bool get isCompleted => status == StudySessionStatus.completed;
  bool get isBreak =>
      engineState == StudyEngineState.breakTime || phase == 'break';

  StudySessionEntity copyWith({
    StudySessionStatus? status,
    DateTime? endedAt,
    int? actualDurationMinutes,
    int? completedQuestions,
    int? completedTopics,
    String? phase,
    int? actualBreakMinutes,
    StudyEngineState? engineState,
  }) {
    return StudySessionEntity(
      id: id,
      userId: userId,
      studyPlanId: studyPlanId,
      startedAt: startedAt,
      endedAt: endedAt ?? this.endedAt,
      plannedDurationMinutes: plannedDurationMinutes,
      actualDurationMinutes:
          actualDurationMinutes ?? this.actualDurationMinutes,
      breakDurationMinutes: breakDurationMinutes,
      completedQuestions: completedQuestions ?? this.completedQuestions,
      completedTopics: completedTopics ?? this.completedTopics,
      status: status ?? this.status,
      createdAt: createdAt,
      updatedAt: updatedAt,
      planTitle: planTitle,
      planSubject: planSubject,
      mode: mode,
      phase: phase ?? this.phase,
      actualBreakMinutes: actualBreakMinutes ?? this.actualBreakMinutes,
      subjectCode: subjectCode,
      topicCode: topicCode,
      engineState: engineState ?? this.engineState,
      breakStartedAt: breakStartedAt,
      pausedAt: pausedAt,
      pausedSeconds: pausedSeconds,
    );
  }
}

class StudySessionHistoryResult {
  const StudySessionHistoryResult({
    required this.items,
    required this.page,
    required this.pageSize,
    required this.totalItems,
    required this.totalPages,
  });

  final List<StudySessionEntity> items;
  final int page;
  final int pageSize;
  final int totalItems;
  final int totalPages;

  bool get hasMore => page < totalPages;
}
