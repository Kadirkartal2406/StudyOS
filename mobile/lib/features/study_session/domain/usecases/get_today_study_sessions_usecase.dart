import '../entities/study_session_entity.dart';
import '../repositories/study_session_repository.dart';

class GetTodayStudySessionsUsecase {
  const GetTodayStudySessionsUsecase(this._repository);

  final StudySessionRepository _repository;

  Future<List<StudySessionEntity>> call() => _repository.getToday();
}
