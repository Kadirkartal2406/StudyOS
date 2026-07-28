import '../../domain/entities/achievement_entity.dart';
import '../datasources/achievement_remote_datasource.dart';

class AchievementRepository {
  AchievementRepository(this._remote);

  final AchievementRemoteDatasource _remote;

  Future<List<AchievementEntity>> listCatalog() => _remote.listCatalog();

  Future<List<AchievementEntity>> listUnlocked() => _remote.listUnlocked();

  Future<List<AchievementEntity>> listProgress() => _remote.listProgress();

  Future<List<AchievementEntity>> check({String? event}) =>
      _remote.check(event: event);

  Future<AchievementExplainEntity> explain(String id) => _remote.explain(id);
}
