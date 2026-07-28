import '../../domain/entities/statistics_entities.dart';

sealed class StatisticsState {
  const StatisticsState();
}

final class StatisticsInitial extends StatisticsState {
  const StatisticsInitial();
}

final class StatisticsLoading extends StatisticsState {
  const StatisticsLoading();
}

final class StatisticsLoaded extends StatisticsState {
  const StatisticsLoaded({
    required this.overview,
    required this.daily,
    required this.weekly,
    required this.monthly,
    required this.subjects,
    required this.heatmap,
  });

  final StatisticsOverviewEntity overview;
  final StatisticsDailyEntity daily;
  final StatisticsPeriodEntity weekly;
  final StatisticsPeriodEntity monthly;
  final StatisticsDistributionEntity subjects;
  final StatisticsHeatmapEntity heatmap;
}

final class StatisticsError extends StatisticsState {
  const StatisticsError(this.message);

  final String message;
}
