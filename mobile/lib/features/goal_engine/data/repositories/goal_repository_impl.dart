import '../../domain/entities/goal_entity.dart';
import '../../domain/entities/goal_explain_entity.dart';
import '../../domain/entities/goal_progress_entity.dart';
import '../../domain/repositories/goal_repository.dart';
import '../datasources/goal_remote_datasource.dart';

class GoalRepositoryImpl implements GoalRepository {
  const GoalRepositoryImpl(this._remote);

  final GoalRemoteDatasource _remote;

  @override
  Future<List<GoalEntity>> listAll() async {
    final models = await _remote.listAll();
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<List<GoalEntity>> listActive() async {
    final models = await _remote.listActive();
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<List<GoalEntity>> listCompleted() async {
    final models = await _remote.listCompleted();
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<List<GoalEntity>> listWeekly() async {
    final models = await _remote.listWeekly();
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<List<GoalEntity>> listMonthly() async {
    final models = await _remote.listMonthly();
    return models.map((m) => m.toEntity()).toList();
  }

  @override
  Future<GoalProgressEntity> getProgress() async {
    final model = await _remote.getProgress();
    return model.toEntity();
  }

  @override
  Future<GoalEntity> getById(String id) async {
    final model = await _remote.getById(id);
    return model.toEntity();
  }

  @override
  Future<GoalEntity> create(Map<String, dynamic> body) async {
    final model = await _remote.create(body);
    return model.toEntity();
  }

  @override
  Future<GoalEntity> update(String id, Map<String, dynamic> body) async {
    final model = await _remote.update(id, body);
    return model.toEntity();
  }

  @override
  Future<void> delete(String id) => _remote.delete(id);

  @override
  Future<GoalExplainEntity> explain(String id) async {
    final model = await _remote.explain(id);
    return GoalExplainEntity(
      goalId: model.goalId,
      explanation: model.explanation,
      whyProgressed: model.whyProgressed,
      whyStalled: model.whyStalled,
      howToComplete: model.howToComplete,
      title: model.title,
      progress: model.progress,
      provider: model.provider,
      usedFallback: model.usedFallback,
    );
  }
}
