import '../entities/study_plan_entity.dart';
import '../repositories/study_plan_repository.dart';

/// Bir planı "in_progress" durumuna geçirir.
class StartStudyPlanUsecase {
  const StartStudyPlanUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<StudyPlanEntity> call(String id) => _repository.startPlan(id);
}
