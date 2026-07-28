import '../entities/statistics_entities.dart';

abstract class StatisticsRepository {
  Future<StatisticsOverviewEntity> getOverview();
  Future<StatisticsDailyEntity> getDaily({DateTime? date});
  Future<StatisticsPeriodEntity> getWeekly({DateTime? anchor});
  Future<StatisticsPeriodEntity> getMonthly({DateTime? anchor});
  Future<StatisticsDistributionEntity> getSubjects();
  Future<StatisticsDistributionEntity> getTopics();
  Future<StatisticsHeatmapEntity> getHeatmap();
}
