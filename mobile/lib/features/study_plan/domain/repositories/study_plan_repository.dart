import '../entities/study_plan_entity.dart';
import '../entities/study_time.dart';

/// StudyPlan repository contract (interface).
/// Data katmanı bu interface'i implemente eder.
abstract interface class StudyPlanRepository {
  /// Belirtilen güne ait planları order_index'e göre sıralı döner.
  Future<List<StudyPlanEntity>> getPlans(DateTime studyDate);

  Future<StudyPlanEntity> getPlan(String id);

  Future<StudyPlanEntity> createPlan({
    required String title,
    required String subject,
    String? topic,
    required int targetQuestionCount,
    required int estimatedMinutes,
    required DateTime studyDate,
    StudyTime? plannedStartTime,
    StudyTime? plannedEndTime,
    int? orderIndex,
  });

  Future<StudyPlanEntity> updatePlan({
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
  });

  Future<void> deletePlan(String id);

  Future<StudyPlanEntity> startPlan(String id);

  Future<StudyPlanEntity> completePlan(
    String id, {
    int? completedQuestionCount,
    int? completedMinutes,
  });

  Future<StudyPlanEntity> skipPlan(String id);
}
