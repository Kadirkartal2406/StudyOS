import '../../domain/entities/planner_entity.dart';
import '../datasources/planner_remote_datasource.dart';

class PlannerRepository {
  PlannerRepository(this._remote);

  final PlannerRemoteDatasource _remote;

  Future<PlannerDraftEntity> generate({
    required String targetExam,
    required double targetNet,
    required List<int> availableDays,
    required double availableHours,
  }) {
    return _remote.generate({
      'target_exam': targetExam,
      'target_net': targetNet,
      'available_days': availableDays,
      'available_hours': availableHours,
    });
  }

  Future<PlannerDraftEntity> getDraft(String id) => _remote.getDraft(id);

  Future<PlannerDraftEntity> accept(String id, {bool force = false}) =>
      _remote.accept(id, force: force);

  Future<PlannerExplainEntity> explain(String id) => _remote.explain(id);
}
