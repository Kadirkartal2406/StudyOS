import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../subjects/presentation/widgets/subject_code_chip.dart';
import '../providers/exam_provider.dart';
import '../providers/exam_state.dart';
import '../widgets/exam_charts_card.dart';

class ExamListScreen extends ConsumerWidget {
  const ExamListScreen({super.key, this.subjectCode});

  /// Sprint-3.1.C — Subject Hub deep-link entry.
  final String? subjectCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(examProvider);
    final code = subjectCode;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Denemeler'),
        actions: [
          if (code != null && code.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: SubjectCodeChip(subjectCode: code),
            ),
          IconButton(
            tooltip: 'İstatistik',
            onPressed: () => context.push('/exams/statistics'),
            icon: const Icon(Icons.bar_chart_outlined),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/exams/add'),
        icon: const Icon(Icons.add),
        label: const Text('Deneme Ekle'),
      ),
      body: switch (state) {
        ExamInitial() || ExamLoading() => const Center(
            child: CircularProgressIndicator(),
          ),
        ExamError(:final message) => Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(message),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => ref.read(examProvider.notifier).load(),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        ExamLoaded(:final items, :final statistics, :final trends, :final errorMessage) =>
          RefreshIndicator(
            onRefresh: () => ref.read(examProvider.notifier).load(),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 96),
              children: [
                if (errorMessage != null)
                  Text(
                    errorMessage,
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                  ),
                if (statistics != null)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Text(
                        'Toplam ${statistics.totalExams} · '
                        'Ort. net ${statistics.averageNet.toStringAsFixed(1)} · '
                        'En yüksek ${statistics.highestNet.toStringAsFixed(1)}',
                      ),
                    ),
                  ),
                if (trends != null) ...[
                  const SizedBox(height: 8),
                  ExamChartsCard(trends: trends),
                ],
                const SizedBox(height: 8),
                if (items.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 48),
                    child: Center(child: Text('Henüz deneme yok.')),
                  )
                else
                  ...items.map((exam) {
                    final dateLabel =
                        DateFormat('dd.MM.yyyy').format(exam.examDate);
                    return Card(
                      child: ListTile(
                        title: Text(exam.title),
                        subtitle: Text(
                          '${exam.examType.toUpperCase()} · $dateLabel · '
                          'Net ${exam.totalNet.toStringAsFixed(1)}',
                        ),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: () => context.push('/exams/${exam.id}'),
                      ),
                    );
                  }),
              ],
            ),
          ),
      },
    );
  }
}
