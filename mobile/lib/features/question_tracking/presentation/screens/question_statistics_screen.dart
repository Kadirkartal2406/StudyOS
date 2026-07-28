import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/entities/question_record_entity.dart';
import '../providers/question_tracking_provider.dart';
import '../providers/question_tracking_state.dart';

class QuestionStatisticsScreen extends ConsumerWidget {
  const QuestionStatisticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(questionStatsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Soru İstatistikleri')),
      body: switch (state) {
        QuestionStatsInitial() || QuestionStatsLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
        QuestionStatsError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                FilledButton(
                  onPressed: () =>
                      ref.read(questionStatsProvider.notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        QuestionStatsLoaded(
          :final overview,
          :final daily,
          :final subjects,
          :final topics,
          :final exams,
        ) =>
          ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _OverviewGrid(overview: overview),
              const SizedBox(height: 24),
              Text(
                'Günlük soru',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 180,
                child: daily.isEmpty
                    ? const Center(child: Text('Veri yok'))
                    : BarChart(
                        BarChartData(
                          titlesData: FlTitlesData(
                            topTitles: const AxisTitles(),
                            rightTitles: const AxisTitles(),
                            bottomTitles: AxisTitles(
                              sideTitles: SideTitles(
                                showTitles: true,
                                getTitlesWidget: (v, _) {
                                  final i = v.toInt();
                                  if (i < 0 || i >= daily.length) {
                                    return const SizedBox.shrink();
                                  }
                                  final d = daily[i].date;
                                  return Text(
                                    d.length >= 10 ? d.substring(5) : d,
                                    style: const TextStyle(fontSize: 10),
                                  );
                                },
                              ),
                            ),
                          ),
                          barGroups: [
                            for (var i = 0; i < daily.length; i++)
                              BarChartGroupData(
                                x: i,
                                barRods: [
                                  BarChartRodData(
                                    toY: daily[i].questionCount.toDouble(),
                                    width: 12,
                                  ),
                                ],
                              ),
                          ],
                        ),
                      ),
              ),
              const SizedBox(height: 24),
              _DistributionSection(title: 'Ders dağılımı', items: subjects),
              _DistributionSection(title: 'Konu dağılımı', items: topics),
              _DistributionSection(title: 'Sınav dağılımı', items: exams),
            ],
          ),
      },
    );
  }
}

class _OverviewGrid extends StatelessWidget {
  const _OverviewGrid({required this.overview});

  final QuestionStatisticsOverviewEntity overview;

  @override
  Widget build(BuildContext context) {
    final cards = [
      ('Toplam', '${overview.totalQuestions}'),
      ('Bugün', '${overview.todayQuestions}'),
      ('Hafta', '${overview.weekQuestions}'),
      ('Ay', '${overview.monthQuestions}'),
      ('Doğru %', overview.correctRate.toStringAsFixed(1)),
      ('Yanlış %', overview.wrongRate.toStringAsFixed(1)),
      ('Net', overview.totalNet.toStringAsFixed(1)),
      ('Süre', '${overview.totalDurationMinutes} dk'),
    ];
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 2.2,
      mainAxisSpacing: 8,
      crossAxisSpacing: 8,
      children: [
        for (final (label, value) in cards)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label, style: Theme.of(context).textTheme.bodySmall),
                  Text(
                    value,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _DistributionSection extends StatelessWidget {
  const _DistributionSection({required this.title, required this.items});

  final String title;
  final List<QuestionDistributionItemEntity> items;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 16),
        Text(title, style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        if (items.isEmpty)
          const Text('Veri yok')
        else
          ...items.map(
            (i) => ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(i.name),
              subtitle: Text(
                '${i.questionCount} soru · net ${i.netScore.toStringAsFixed(1)} · '
                '%${i.correctRate.toStringAsFixed(0)} doğru',
              ),
            ),
          ),
      ],
    );
  }
}
