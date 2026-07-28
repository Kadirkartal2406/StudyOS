import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../../domain/entities/statistics_entities.dart';

class StatisticsSummaryGrid extends StatelessWidget {
  const StatisticsSummaryGrid({super.key, required this.overview});

  final StatisticsOverviewEntity overview;

  @override
  Widget build(BuildContext context) {
    final items = [
      ('Toplam süre', '${overview.totalStudyMinutes} dk', Icons.timer_outlined),
      ('Bugün', '${overview.todayStudyMinutes} dk', Icons.today_outlined),
      ('Seri', '${overview.streakDays} gün', Icons.local_fire_department_outlined),
      ('Soru', '${overview.totalQuestions}', Icons.quiz_outlined),
      ('Pomodoro', '${overview.totalPomodoros}', Icons.timelapse_outlined),
      (
        'Ort. oturum',
        '${overview.averageSessionMinutes.toStringAsFixed(1)} dk',
        Icons.av_timer_outlined,
      ),
      (
        'En çok ders',
        overview.mostStudiedSubject ?? '—',
        Icons.menu_book_outlined,
      ),
      ('Haftalık', '${overview.weekStudyMinutes} dk', Icons.date_range_outlined),
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: items.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        mainAxisSpacing: 10,
        crossAxisSpacing: 10,
        childAspectRatio: 1.7,
      ),
      itemBuilder: (context, index) {
        final item = items[index];
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(item.$3, size: 18),
                const Spacer(),
                Text(
                  item.$2,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  item.$1,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class MinutesBarChart extends StatelessWidget {
  const MinutesBarChart({
    super.key,
    required this.buckets,
    this.maxBars = 14,
  });

  final List<TimeBucketEntity> buckets;
  final int maxBars;

  @override
  Widget build(BuildContext context) {
    final color = Theme.of(context).colorScheme.primary;
    final data = buckets.length > maxBars
        ? buckets.sublist(buckets.length - maxBars)
        : buckets;
    if (data.every((b) => b.studyMinutes == 0)) {
      return const SizedBox(
        height: 180,
        child: Center(child: Text('Henüz veri yok')),
      );
    }
    final maxY = data
        .map((b) => b.studyMinutes)
        .fold<int>(0, (a, b) => a > b ? a : b)
        .toDouble();

    return SizedBox(
      height: 220,
      child: BarChart(
        BarChartData(
          maxY: maxY == 0 ? 1 : maxY * 1.2,
          barGroups: [
            for (var i = 0; i < data.length; i++)
              BarChartGroupData(
                x: i,
                barRods: [
                  BarChartRodData(
                    toY: data[i].studyMinutes.toDouble(),
                    color: color,
                    width: 10,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ],
              ),
          ],
          titlesData: FlTitlesData(
            topTitles: const AxisTitles(),
            rightTitles: const AxisTitles(),
            leftTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: true, reservedSize: 28),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: 1,
                getTitlesWidget: (value, meta) {
                  final i = value.toInt();
                  if (i < 0 || i >= data.length) {
                    return const SizedBox.shrink();
                  }
                  final label = data[i].label;
                  final short = label.length > 5
                      ? label.substring(label.length - 5)
                      : label;
                  return Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(short, style: const TextStyle(fontSize: 9)),
                  );
                },
              ),
            ),
          ),
          gridData: const FlGridData(show: false),
          borderData: FlBorderData(show: false),
        ),
      ),
    );
  }
}

class SubjectsPieChart extends StatelessWidget {
  const SubjectsPieChart({super.key, required this.items});

  final List<DistributionItemEntity> items;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty || items.every((i) => i.studyMinutes == 0)) {
      return const SizedBox(
        height: 180,
        child: Center(child: Text('Henüz ders dağılımı yok')),
      );
    }
    final colors = [
      Theme.of(context).colorScheme.primary,
      Theme.of(context).colorScheme.secondary,
      Theme.of(context).colorScheme.tertiary,
      Colors.orange,
      Colors.teal,
    ];

    return Column(
      children: [
        SizedBox(
          height: 200,
          child: PieChart(
            PieChartData(
              sectionsSpace: 2,
              centerSpaceRadius: 36,
              sections: [
                for (var i = 0; i < items.length; i++)
                  PieChartSectionData(
                    value: items[i].studyMinutes.toDouble(),
                    title: '${items[i].percentage.toStringAsFixed(0)}%',
                    color: colors[i % colors.length],
                    radius: 50,
                    titleStyle: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Colors.white,
                    ),
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 4,
          children: [
            for (var i = 0; i < items.length; i++)
              Chip(
                avatar: CircleAvatar(
                  backgroundColor: colors[i % colors.length],
                  radius: 6,
                ),
                label: Text(
                  '${items[i].name} (${items[i].studyMinutes} dk)',
                ),
              ),
          ],
        ),
      ],
    );
  }
}

class StudyHeatmapGrid extends StatelessWidget {
  const StudyHeatmapGrid({super.key, required this.days});

  final List<HeatmapDayEntity> days;

  @override
  Widget build(BuildContext context) {
    final base = Theme.of(context).colorScheme.primary;
    return Wrap(
      spacing: 4,
      runSpacing: 4,
      children: [
        for (final day in days)
          Tooltip(
            message: '${day.date.toIso8601String().substring(0, 10)}'
                ' — ${day.studyMinutes} dk',
            child: Container(
              width: 14,
              height: 14,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(3),
                color: day.studyMinutes == 0
                    ? Theme.of(context).colorScheme.surfaceContainerHighest
                    : base.withValues(
                        alpha: (day.studyMinutes / 120).clamp(0.2, 1.0),
                      ),
              ),
            ),
          ),
      ],
    );
  }
}
