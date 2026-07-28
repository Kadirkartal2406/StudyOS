import '../entities/study_session_entity.dart';
import '../repositories/study_session_repository.dart';

class PauseStudySessionUsecase {
  const PauseStudySessionUsecase(this._repository);

  final StudySessionRepository _repository;

  Future<StudySessionEntity> call() => _repository.pause();
}
