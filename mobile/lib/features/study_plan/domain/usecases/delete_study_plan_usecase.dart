import '../repositories/study_plan_repository.dart';

/// Bir çalışma planını (soft delete) siler.
class DeleteStudyPlanUsecase {
  const DeleteStudyPlanUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<void> call(String id) => _repository.deletePlan(id);
}
