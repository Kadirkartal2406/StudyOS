import 'package:intl/intl.dart';

import '../../domain/entities/study_plan_entity.dart';
import '../../domain/entities/study_time.dart';
import '../../domain/repositories/study_plan_repository.dart';
import '../datasources/study_plan_remote_datasource.dart';

/// StudyPlanRepository interface'inin gerçek implementasyonu.
/// Datasource'u çağırır ve domain entity'lerine dönüştürür.
class StudyPlanRepositoryImpl implements StudyPlanRepository {
  const StudyPlanRepositoryImpl(this._datasource);

  final StudyPlanRemoteDatasource _datasource;

  static final DateFormat _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  Future<List<StudyPlanEntity>> getPlans(DateTime studyDate) async {
    final models = await _datasource.getPlans(studyDate);
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<StudyPlanEntity> getPlan(String id) async {
    final model = await _datasource.getPlan(id);
    return model.toEntity();
  }

  @override
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
  }) async {
    final model = await _datasource.createPlan(
      _buildBody(
        title: title,
        subject: subject,
        topic: topic,
        targetQuestionCount: targetQuestionCount,
        estimatedMinutes: estimatedMinutes,
        studyDate: studyDate,
        plannedStartTime: plannedStartTime,
        plannedEndTime: plannedEndTime,
        orderIndex: orderIndex,
      ),
    );
    return model.toEntity();
  }

  @override
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
  }) async {
    final model = await _datasource.updatePlan(
      id,
      _buildBody(
        title: title,
        subject: subject,
        topic: topic,
        targetQuestionCount: targetQuestionCount,
        estimatedMinutes: estimatedMinutes,
        studyDate: studyDate,
        plannedStartTime: plannedStartTime,
        plannedEndTime: plannedEndTime,
        orderIndex: orderIndex,
      ),
    );
    return model.toEntity();
  }

  @override
  Future<void> deletePlan(String id) => _datasource.deletePlan(id);

  @override
  Future<StudyPlanEntity> startPlan(String id) async {
    final model = await _datasource.startPlan(id);
    return model.toEntity();
  }

  @override
  Future<StudyPlanEntity> completePlan(
    String id, {
    int? completedQuestionCount,
    int? completedMinutes,
  }) async {
    final model = await _datasource.completePlan(
      id,
      completedQuestionCount: completedQuestionCount,
      completedMinutes: completedMinutes,
    );
    return model.toEntity();
  }

  @override
  Future<StudyPlanEntity> skipPlan(String id) async {
    final model = await _datasource.skipPlan(id);
    return model.toEntity();
  }

  Map<String, dynamic> _buildBody({
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
    return {
      'title': title,
      'subject': subject,
      if (topic != null) 'topic': topic,
      'target_question_count': targetQuestionCount,
      'estimated_minutes': estimatedMinutes,
      'study_date': _dateFormat.format(studyDate),
      if (plannedStartTime != null)
        'planned_start_time': plannedStartTime.toApi(),
      if (plannedEndTime != null) 'planned_end_time': plannedEndTime.toApi(),
      if (orderIndex != null) 'order_index': orderIndex,
    };
  }
}
