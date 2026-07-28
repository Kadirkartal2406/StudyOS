import '../entities/study_plan_entity.dart';
import '../repositories/study_plan_repository.dart';

/// Bir planı "completed" durumuna geçirir; gerçekleşen ilerlemeyi kaydeder.
class CompleteStudyPlanUsecase {
  const CompleteStudyPlanUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<StudyPlanEntity> call(
    String id, {
    int? completedQuestionCount,
    int? completedMinutes,
  }) {
    return _repository.completePlan(
      id,
      completedQuestionCount: completedQuestionCount,
      completedMinutes: completedMinutes,
    );
  }
}
