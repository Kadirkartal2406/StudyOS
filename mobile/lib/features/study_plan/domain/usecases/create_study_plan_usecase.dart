import '../entities/study_plan_entity.dart';
import '../entities/study_time.dart';
import '../repositories/study_plan_repository.dart';

/// Yeni bir çalışma planı kalemi oluşturur.
class CreateStudyPlanUsecase {
  const CreateStudyPlanUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<StudyPlanEntity> call({
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
    return _repository.createPlan(
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
