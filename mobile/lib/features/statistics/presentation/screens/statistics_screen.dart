import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../domain/entities/statistics_entities.dart';
import '../providers/statistics_provider.dart';
import '../providers/statistics_state.dart';
import '../widgets/statistics_charts.dart';

class StatisticsScreen extends ConsumerWidget {
  const StatisticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(statisticsProvider);

    return DefaultTabController(
      length: 5,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('İstatistikler'),
          actions: [
            TextButton(
              onPressed: () => context.push('/journey'),
              child: const Text('Yolculuk'),
            ),
            TextButton(
              onPressed: () => context.push('/questions/statistics'),
              child: const Text('Soru'),
            ),
          ],
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'Özet'),
              Tab(text: 'Günlük'),
              Tab(text: 'Haftalık'),
              Tab(text: 'Aylık'),
              Tab(text: 'Dersler'),
            ],
          ),
        ),
        body: switch (state) {
          StatisticsInitial() || StatisticsLoading() => const Center(
              child: CircularProgressIndicator(),
            ),
          StatisticsError(:final message) => Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(message, textAlign: TextAlign.center),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: () =>
                          ref.read(statisticsProvider.notifier).load(),
                      child: const Text('Tekrar Dene'),
                    ),
                  ],
                ),
              ),
            ),
          StatisticsLoaded() => TabBarView(
              children: [
                _OverviewTab(state: state),
                _PeriodTab(
                  title: 'Günlük çalışma',
                  minutes: state.daily.studyMinutes,
                  sessions: state.daily.sessionCount,
                  buckets: state.daily.buckets,
                ),
                _PeriodTab(
                  title: 'Haftalık çalışma',
                  minutes: state.weekly.studyMinutes,
                  sessions: state.weekly.sessionCount,
                  buckets: state.weekly.buckets,
                ),
                _PeriodTab(
                  title: 'Aylık çalışma',
                  minutes: state.monthly.studyMinutes,
                  sessions: state.monthly.sessionCount,
                  buckets: state.monthly.buckets,
                  maxBars: 31,
                ),
                _SubjectsTab(state: state),
              ],
            ),
        },
      ),
    );
  }
}

class _OverviewTab extends StatelessWidget {
  const _OverviewTab({required this.state});

  final StatisticsLoaded state;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        StatisticsSummaryGrid(overview: state.overview),
        const SizedBox(height: 20),
        Text(
          'Son 30 gün',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        StudyHeatmapGrid(days: state.heatmap.days),
        const SizedBox(height: 20),
        Text(
          'Haftalık grafik',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 12),
        MinutesBarChart(buckets: state.weekly.buckets),
      ],
    );
  }
}

class _PeriodTab extends StatelessWidget {
  const _PeriodTab({
    required this.title,
    required this.minutes,
    required this.sessions,
    required this.buckets,
    this.maxBars = 14,
  });

  final String title;
  final int minutes;
  final int sessions;
  final List<TimeBucketEntity> buckets;
  final int maxBars;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(title, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 8),
        Text('$minutes dk · $sessions oturum'),
        const SizedBox(height: 16),
        MinutesBarChart(
          buckets: buckets,
          maxBars: maxBars,
        ),
      ],
    );
  }
}

class _SubjectsTab extends StatelessWidget {
  const _SubjectsTab({required this.state});

  final StatisticsLoaded state;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Ders dağılımı',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 16),
        SubjectsPieChart(items: state.subjects.items),
        const SizedBox(height: 24),
        Text(
          'Pomodoro / oturum özeti',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Text(
          'Toplam Pomodoro: ${state.overview.totalPomodoros}\n'
          'Ort. oturum: ${state.overview.averageSessionMinutes.toStringAsFixed(1)} dk\n'
          'En uzun: ${state.overview.longestSessionMinutes} dk',
        ),
      ],
    );
  }
}
