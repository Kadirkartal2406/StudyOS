import '../entities/study_plan_entity.dart';
import '../entities/study_time.dart';
import '../repositories/study_plan_repository.dart';

/// Mevcut bir çalışma planını günceller.
class UpdateStudyPlanUsecase {
  const UpdateStudyPlanUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<StudyPlanEntity> call({
    required String id,
    required String title,
    required String subject,
    String? topic,
    required int targetQuestionCount,
    required int estimatedMinutes,
    required DateTime studyDate,
    StudyTime? plannedStartTime,
    StudyTime? plannedEndTime,
    int? orderIndex,
  }) {
    return _repository.updatePlan(
      id: id,
      title: title,
      subject: subject,
      topic: topic,
      targetQuestionCount: targetQuestionCount,
      estimatedMinutes: estimatedMinutes,
      studyDate: studyDate,
      plannedStartTime: plannedStartTime,
      plannedEndTime: plannedEndTime,
      orderIndex: orderIndex,
    );
  }
}
