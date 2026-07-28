import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../../domain/entities/exam_entity.dart';

class ExamChartsCard extends StatelessWidget {
  const ExamChartsCard({super.key, required this.trends});

  final ExamTrendsEntity trends;

  @override
  Widget build(BuildContext context) {
    if (trends.netOverTime.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('Grafik için henüz yeterli deneme yok.'),
        ),
      );
    }

    final spots = <FlSpot>[];
    for (var i = 0; i < trends.netOverTime.length; i++) {
      spots.add(FlSpot(i.toDouble(), trends.netOverTime[i].net));
    }

    final cwb = trends.correctWrongBlank;
    final correct = (cwb['correct'] ?? 0).toDouble();
    final wrong = (cwb['wrong'] ?? 0).toDouble();
    final blank = (cwb['blank'] ?? 0).toDouble();
    final total = correct + wrong + blank;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Net zaman grafiği', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            SizedBox(
              height: 160,
              child: LineChart(
                LineChartData(
                  gridData: const FlGridData(show: false),
                  titlesData: const FlTitlesData(show: false),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      color: Theme.of(context).colorScheme.primary,
                      barWidth: 3,
                      dotData: const FlDotData(show: true),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text('Ders bazlı ortalama net', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            for (final s in trends.bySubject.take(6))
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text('${s.subject}: ${s.averageNet.toStringAsFixed(1)}'),
              ),
            if (total > 0) ...[
              const SizedBox(height: 12),
              Text('Doğru / Yanlış / Boş', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              Text(
                'D ${correct.toInt()} · Y ${wrong.toInt()} · B ${blank.toInt()}',
              ),
            ],
          ],
        ),
      ),
    );
  }
}
