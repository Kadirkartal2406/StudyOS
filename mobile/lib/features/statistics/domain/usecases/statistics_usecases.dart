import '../entities/statistics_entities.dart';
import '../repositories/statistics_repository.dart';

class GetStatisticsOverviewUsecase {
  const GetStatisticsOverviewUsecase(this._repository);
  final StatisticsRepository _repository;
  Future<StatisticsOverviewEntity> call() => _repository.getOverview();
}

class GetStatisticsDailyUsecase {
  const GetStatisticsDailyUsecase(this._repository);
  final StatisticsRepository _repository;
  Future<StatisticsDailyEntity> call({DateTime? date}) =>
      _repository.getDaily(date: date);
}

class GetStatisticsWeeklyUsecase {
  const GetStatisticsWeeklyUsecase(this._repository);
  final StatisticsRepository _repository;
  Future<StatisticsPeriodEntity> call({DateTime? anchor}) =>
      _repository.getWeekly(anchor: anchor);
}

class GetStatisticsMonthlyUsecase {
  const GetStatisticsMonthlyUsecase(this._repository);
  final StatisticsRepository _repository;
  Future<StatisticsPeriodEntity> call({DateTime? anchor}) =>
      _repository.getMonthly(anchor: anchor);
}

class GetStatisticsSubjectsUsecase {
  const GetStatisticsSubjectsUsecase(this._repository);
  final StatisticsRepository _repository;
  Future<StatisticsDistributionEntity> call() => _repository.getSubjects();
}
