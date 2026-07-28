import '../entities/study_session_entity.dart';
import '../repositories/study_session_repository.dart';

class FinishStudySessionUsecase {
  const FinishStudySessionUsecase(this._repository);

  final StudySessionRepository _repository;

  Future<StudySessionEntity> call({
    int? completedQuestions,
    int? completedTopics,
  }) {
    return _repository.finish(
      completedQuestions: completedQuestions,
      completedTopics: completedTopics,
    );
  }
}
