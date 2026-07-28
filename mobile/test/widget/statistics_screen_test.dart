import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:studyos_mobile/features/statistics/domain/entities/statistics_entities.dart';
import 'package:studyos_mobile/features/statistics/domain/repositories/statistics_repository.dart';
import 'package:studyos_mobile/features/statistics/presentation/providers/statistics_provider.dart';
import 'package:studyos_mobile/features/statistics/presentation/screens/statistics_screen.dart';

class _FakeRepo implements StatisticsRepository {
  @override
  Future<StatisticsOverviewEntity> getOverview() async {
    return const StatisticsOverviewEntity(
      totalStudyMinutes: 90,
      todayStudyMinutes: 30,
      todayQuestions: 5,
      weekStudyMinutes: 60,
      monthStudyMinutes: 90,
      totalSessions: 2,
      totalPomodoros: 2,
      completedPlans: 1,
      totalQuestions: 15,
      averageSessionMinutes: 45,
      longestSessionMinutes: 50,
      streakDays: 1,
      mostStudiedSubject: 'Fizik',
    );
  }

  @override
  Future<StatisticsDailyEntity> getDaily({DateTime? date}) async {
    return const StatisticsDailyEntity(
      studyMinutes: 30,
      sessionCount: 1,
      questionCount: 5,
      completedPlans: 0,
      buckets: [
        TimeBucketEntity(
          label: '10:00',
          studyMinutes: 30,
          sessionCount: 1,
          questionCount: 5,
        ),
      ],
    );
  }

  @override
  Future<StatisticsPeriodEntity> getWeekly({DateTime? anchor}) async {
    return const StatisticsPeriodEntity(
      studyMinutes: 60,
      sessionCount: 2,
      questionCount: 10,
      completedPlans: 1,
      buckets: [
        TimeBucketEntity(
          label: '2026-07-15',
          studyMinutes: 30,
          sessionCount: 1,
          questionCount: 5,
        ),
        TimeBucketEntity(
          label: '2026-07-16',
          studyMinutes: 30,
          sessionCount: 1,
          questionCount: 5,
        ),
      ],
    );
  }

  @override
  Future<StatisticsPeriodEntity> getMonthly({DateTime? anchor}) async {
    return const StatisticsPeriodEntity(
      studyMinutes: 90,
      sessionCount: 2,
      questionCount: 15,
      completedPlans: 1,
      buckets: [],
    );
  }

  @override
  Future<StatisticsDistributionEntity> getSubjects() async {
    return const StatisticsDistributionEntity(
      totalMinutes: 90,
      items: [
        DistributionItemEntity(
          name: 'Fizik',
          studyMinutes: 90,
          sessionCount: 2,
          questionCount: 15,
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
    return const StatisticsHeatmapEntity(days: []);
  }
}

void main() {
  testWidgets('shows tabs and overview cards', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          statisticsRepositoryProvider.overrideWithValue(_FakeRepo()),
        ],
        child: const MaterialApp(home: StatisticsScreen()),
      ),
    );

    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));

    expect(find.text('İstatistikler'), findsWidgets);
    expect(find.text('Özet'), findsOneWidget);
    expect(find.text('Günlük'), findsOneWidget);
    expect(find.text('Dersler'), findsOneWidget);
    expect(find.text('Pomodoro'), findsWidgets);
    expect(find.textContaining('Seri'), findsOneWidget);
  });
}
