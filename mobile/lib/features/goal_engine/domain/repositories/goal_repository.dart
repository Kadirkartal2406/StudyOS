import '../entities/goal_entity.dart';
import '../entities/goal_explain_entity.dart';
import '../entities/goal_progress_entity.dart';

abstract class GoalRepository {
  Future<List<GoalEntity>> listAll();

  Future<List<GoalEntity>> listActive();

  Future<List<GoalEntity>> listCompleted();

  Future<List<GoalEntity>> listWeekly();

  Future<List<GoalEntity>> listMonthly();

  Future<GoalProgressEntity> getProgress();

  Future<GoalEntity> getById(String id);

  Future<GoalEntity> create(Map<String, dynamic> body);

  Future<GoalEntity> update(String id, Map<String, dynamic> body);

  Future<void> delete(String id);

  Future<GoalExplainEntity> explain(String id);
}
