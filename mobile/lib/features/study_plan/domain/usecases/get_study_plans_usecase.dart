import '../entities/study_plan_entity.dart';
import '../repositories/study_plan_repository.dart';

/// Belirli bir güne ait çalışma planlarını getirir.
class GetStudyPlansUsecase {
  const GetStudyPlansUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<List<StudyPlanEntity>> call(DateTime studyDate) {
    return _repository.getPlans(studyDate);
  }
}
