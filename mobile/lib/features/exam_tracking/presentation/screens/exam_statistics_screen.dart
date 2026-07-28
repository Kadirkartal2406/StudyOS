import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/exam_provider.dart';
import '../providers/exam_state.dart';
import '../widgets/exam_charts_card.dart';

class ExamStatisticsScreen extends ConsumerWidget {
  const ExamStatisticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(examProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Deneme İstatistikleri')),
      body: switch (state) {
        ExamLoaded(:final statistics, :final trends) => ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (statistics != null) ...[
                Text('Toplam deneme: ${statistics.totalExams}'),
                Text('Son deneme: ${statistics.lastExamTitle ?? '-'}'),
                Text('Son net: ${statistics.lastExamNet.toStringAsFixed(1)}'),
                Text('En yüksek: ${statistics.highestNet.toStringAsFixed(1)}'),
                Text('En düşük: ${statistics.lowestNet.toStringAsFixed(1)}'),
                Text('Ortalama: ${statistics.averageNet.toStringAsFixed(1)}'),
                Text('Bu hafta: ${statistics.weekExams}'),
                Text('Bu ay: ${statistics.monthExams}'),
                const SizedBox(height: 16),
              ],
              if (trends != null) ExamChartsCard(trends: trends),
            ],
          ),
        ExamLoading() || ExamInitial() => const Center(
            child: CircularProgressIndicator(),
          ),
        ExamError(:final message) => Center(child: Text(message)),
      },
    );
  }
}
