import '../entities/study_session_entity.dart';
import '../repositories/study_session_repository.dart';

class StartStudySessionUsecase {
  const StartStudySessionUsecase(this._repository);

  final StudySessionRepository _repository;

  Future<StudySessionEntity> call({
    int? plannedDurationMinutes,
    required int breakDurationMinutes,
    String mode = 'pomodoro',
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
  }) {
    return _repository.start(
      plannedDurationMinutes: plannedDurationMinutes,
      breakDurationMinutes: breakDurationMinutes,
      mode: mode,
      studyPlanId: studyPlanId,
      subjectCode: subjectCode,
      topicCode: topicCode,
    );
  }
}
