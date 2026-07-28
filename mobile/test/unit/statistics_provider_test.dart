import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/features/statistics/domain/entities/statistics_entities.dart';
import 'package:studyos_mobile/features/statistics/domain/repositories/statistics_repository.dart';
import 'package:studyos_mobile/features/statistics/presentation/providers/statistics_provider.dart';
import 'package:studyos_mobile/features/statistics/presentation/providers/statistics_state.dart';

class _FakeRepo implements StatisticsRepository {
  @override
  Future<StatisticsOverviewEntity> getOverview() async {
    return const StatisticsOverviewEntity(
      totalStudyMinutes: 100,
      todayStudyMinutes: 25,
      todayQuestions: 5,
      weekStudyMinutes: 50,
      monthStudyMinutes: 100,
      totalSessions: 3,
      totalPomodoros: 3,
      completedPlans: 1,
      totalQuestions: 20,
      averageSessionMinutes: 33.3,
      longestSessionMinutes: 50,
      streakDays: 2,
      mostStudiedSubject: 'Matematik',
    );
  }

  @override
  Future<StatisticsDailyEntity> getDaily({DateTime? date}) async {
    return const StatisticsDailyEntity(
      studyMinutes: 25,
      sessionCount: 1,
      questionCount: 5,
      completedPlans: 0,
      buckets: [],
    );
  }

  @override
  Future<StatisticsPeriodEntity> getWeekly({DateTime? anchor}) async {
    return const StatisticsPeriodEntity(
      studyMinutes: 50,
      sessionCount: 2,
      questionCount: 10,
      completedPlans: 1,
      buckets: [
        TimeBucketEntity(
          label: '2026-07-14',
          studyMinutes: 20,
          sessionCount: 1,
          questionCount: 4,
        ),
        TimeBucketEntity(
          label: '2026-07-15',
          studyMinutes: 30,
          sessionCount: 1,
          questionCount: 6,
        ),
      ],
    );
  }

  @override
  Future<StatisticsPeriodEntity> getMonthly({DateTime? anchor}) async {
    return const StatisticsPeriodEntity(
      studyMinutes: 100,
      sessionCount: 3,
      questionCount: 20,
      completedPlans: 1,
      buckets: [],
    );
  }

  @override
  Future<StatisticsDistributionEntity> getSubjects() async {
    return const StatisticsDistributionEntity(
      totalMinutes: 100,
      items: [
        DistributionItemEntity(
          name: 'Matematik',
          studyMinutes: 100,
          sessionCount: 3,
          questionCount: 20,
          percentage: 100,
        ),
      ],
    );
  }

  @override
  Future<StatisticsDistributionEntity> getTopics() async {
    return const StatisticsDistributionEntity(totalMinutes: 0, items: []);
  }

  @override
  Future<StatisticsHeatmapEntity> getHeatmap() async {
    return StatisticsHeatmapEntity(
      days: [
        HeatmapDayEntity(
          date: DateTime(2026, 7, 16),
          studyMinutes: 25,
          sessionCount: 1,
        ),
      ],
    );
  }
}

void main() {
  late ProviderContainer container;

  setUp(() {
    container = ProviderContainer(
      overrides: [
        statisticsRepositoryProvider.overrideWithValue(_FakeRepo()),
      ],
    );
  });

  tearDown(() => container.dispose());

  test('load populates StatisticsLoaded', () async {
    container.listen(statisticsProvider, (_, __) {});
    StatisticsState? state;
    for (var i = 0; i < 50; i++) {
      await Future<void>.delayed(const Duration(milliseconds: 10));
      state = container.read(statisticsProvider);
      if (state is StatisticsLoaded) break;
    }

    expect(state, isA<StatisticsLoaded>());
    final loaded = state! as StatisticsLoaded;
    expect(loaded.overview.streakDays, 2);
    expect(loaded.subjects.items.first.name, 'Matematik');
    expect(loaded.heatmap.days, hasLength(1));
  });
}
