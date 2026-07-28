import '../entities/study_plan_entity.dart';
import '../repositories/study_plan_repository.dart';

/// Drag & Drop sıralaması sonrası bir planın `order_index`'ini günceller.
///
/// Backend'de ayrı bir "reorder" endpoint'i tanımlı değildir (bkz.
/// docs/architecture/api-design.md §2.6); mevcut `PUT /study-plans/{id}`
/// güncelleme endpoint'i `order_index` alanını da kabul ettiği için
/// bu usecase onun üzerinden çalışır.
class ReorderStudyPlanUsecase {
  const ReorderStudyPlanUsecase(this._repository);

  final StudyPlanRepository _repository;

  Future<StudyPlanEntity> call(StudyPlanEntity plan, int newOrderIndex) {
    return _repository.updatePlan(
      id: plan.id,
      title: plan.title,
      subject: plan.subject,
      topic: plan.topic,
      targetQuestionCount: plan.targetQuestionCount,
      estimatedMinutes: plan.estimatedMinutes,
      studyDate: plan.studyDate,
      plannedStartTime: plan.plannedStartTime,
      plannedEndTime: plan.plannedEndTime,
      orderIndex: newOrderIndex,
    );
  }
}
