import '../entities/study_plan_entity.dart';
import '../repositories/study_plan_repository.dart';

/// Bir planı "skipped" durumuna geçirir.
class SkipStudyPlanUsecase {
  const SkipStudyPlanUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<StudyPlanEntity> call(String id) => _repository.skipPlan(id);
}
