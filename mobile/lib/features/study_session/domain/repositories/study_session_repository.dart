import '../entities/study_session_entity.dart';

/// StudySession repository sözleşmesi (domain).
abstract class StudySessionRepository {
  Future<StudySessionEntity> start({
    int? plannedDurationMinutes,
    required int breakDurationMinutes,
    String mode = 'pomodoro',
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
  });

  Future<StudySessionEntity> pause();

  Future<StudySessionEntity> resume();

  Future<StudySessionEntity> startBreak();

  Future<StudySessionEntity> endBreak();

  Future<StudySessionEntity> finish({
    int? completedQuestions,
    int? completedTopics,
  });

  /// M25 — aktif oturum; yoksa null.
  Future<StudySessionEntity?> getActive();

  Future<List<StudySessionEntity>> getToday();

  Future<StudySessionHistoryResult> getHistory({
    int page = 1,
    int pageSize = 20,
    DateTime? dateFrom,
    DateTime? dateTo,
    String? studyPlanId,
    String? status,
    String? q,
  });

  Future<StudySessionEntity> getById(String id);
}
