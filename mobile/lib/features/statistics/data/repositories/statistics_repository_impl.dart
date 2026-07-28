import '../../domain/entities/statistics_entities.dart';
import '../../domain/repositories/statistics_repository.dart';
import '../datasources/statistics_remote_datasource.dart';

class StatisticsRepositoryImpl implements StatisticsRepository {
  const StatisticsRepositoryImpl(this._remote);

  final StatisticsRemoteDatasource _remote;

  @override
  Future<StatisticsOverviewEntity> getOverview() async {
    final model = await _remote.getOverview();
    return model.toEntity();
  }

  @override
  Future<StatisticsDailyEntity> getDaily({DateTime? date}) async {
    final model = await _remote.getDaily(date: date);
    return model.toEntity();
  }

  @override
  Future<StatisticsPeriodEntity> getWeekly({DateTime? anchor}) async {
    final model = await _remote.getWeekly(anchor: anchor);
    return model.toEntity();
  }

  @override
  Future<StatisticsPeriodEntity> getMonthly({DateTime? anchor}) async {
    final model = await _remote.getMonthly(anchor: anchor);
    return model.toEntity();
  }

  @override
  Future<StatisticsDistributionEntity> getSubjects() async {
    final model = await _remote.getSubjects();
    return model.toEntity();
  }

  @override
  Future<StatisticsDistributionEntity> getTopics() async {
    final model = await _remote.getTopics();
    return model.toEntity();
  }

  @override
  Future<StatisticsHeatmapEntity> getHeatmap() async {
    final model = await _remote.getHeatmap();
    return model.toEntity();
  }
}
