import '../../domain/entities/study_session_entity.dart';
import '../../domain/repositories/study_session_repository.dart';
import '../datasources/study_session_remote_datasource.dart';

class StudySessionRepositoryImpl implements StudySessionRepository {
  const StudySessionRepositoryImpl(this._remote);

  final StudySessionRemoteDatasource _remote;

  @override
  Future<StudySessionEntity> start({
    int? plannedDurationMinutes,
    required int breakDurationMinutes,
    String mode = 'pomodoro',
    String? studyPlanId,
    String? subjectCode,
    String? topicCode,
  }) async {
    final body = <String, dynamic>{
      'mode': mode,
      'break_duration_minutes': breakDurationMinutes,
      if (plannedDurationMinutes != null)
        'planned_duration_minutes': plannedDurationMinutes,
      if (studyPlanId != null) 'study_plan_id': studyPlanId,
      if (subjectCode != null) 'subject_code': subjectCode,
      if (topicCode != null) 'topic_code': topicCode,
    };
    final model = await _remote.start(body);
    return model.toEntity();
  }

  @override
  Future<StudySessionEntity> pause() async {
    final model = await _remote.pause();
    return model.toEntity();
  }

  @override
  Future<StudySessionEntity> resume() async {
    final model = await _remote.resume();
    return model.toEntity();
  }

  @override
  Future<StudySessionEntity> startBreak() async {
    final model = await _remote.startBreak();
    return model.toEntity();
  }

  @override
  Future<StudySessionEntity> endBreak() async {
    final model = await _remote.endBreak();
    return model.toEntity();
  }

  @override
  Future<StudySessionEntity> finish({
    int? completedQuestions,
    int? completedTopics,
  }) async {
    final body = <String, dynamic>{
      if (completedQuestions != null) 'completed_questions': completedQuestions,
      if (completedTopics != null) 'completed_topics': completedTopics,
    };
    final model = await _remote.finish(body);
    return model.toEntity();
  }

  @override
  Future<StudySessionEntity?> getActive() async {
    final model = await _remote.getActive();
    return model?.toEntity();
  }

  @override
  Future<List<StudySessionEntity>> getToday() async {
    final models = await _remote.getToday();
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<StudySessionHistoryResult> getHistory({
    int page = 1,
    int pageSize = 20,
    DateTime? dateFrom,
    DateTime? dateTo,
    String? studyPlanId,
    String? status,
    String? q,
  }) async {
    final pageData = await _remote.getHistory(
      page: page,
      pageSize: pageSize,
      dateFrom: dateFrom,
      dateTo: dateTo,
      studyPlanId: studyPlanId,
      status: status,
      q: q,
    );
    return StudySessionHistoryResult(
      items: pageData.items.map((m) => m.toEntity()).toList(),
      page: pageData.page,
      pageSize: pageData.pageSize,
      totalItems: pageData.totalItems,
      totalPages: pageData.totalPages,
    );
  }

  @override
  Future<StudySessionEntity> getById(String id) async {
    final model = await _remote.getById(id);
    return model.toEntity();
  }
}
