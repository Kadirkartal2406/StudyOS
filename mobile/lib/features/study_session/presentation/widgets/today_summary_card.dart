import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../data/datasources/study_session_remote_datasource.dart';

final studySessionTodaySummaryProvider =
    FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final ds = StudySessionRemoteDatasource(ref.watch(dioClientProvider));
  return ds.todaySummary();
});

/// Günlük uyum paneli — ders dakikası / plan % / hedef gap / mola.
class TodaySummaryCard extends ConsumerWidget {
  const TodaySummaryCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(studySessionTodaySummaryProvider);
    final theme = Theme.of(context);

    return async.when(
      loading: () => const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
        ),
      ),
      error: (e, _) => Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Text(
            e is AppException ? e.message : 'Bugünkü özet yüklenemedi',
            style: TextStyle(color: theme.colorScheme.error),
          ),
        ),
      ),
      data: (data) {
        final focus = (data['focus_minutes'] as num?)?.toInt() ?? 0;
        final breaks = (data['break_minutes'] as num?)?.toInt() ?? 0;
        final planned = (data['planned_minutes'] as num?)?.toInt() ?? 0;
        final adherence =
            (data['plan_adherence_pct'] as num?)?.toDouble() ?? 0;
        final gap = (data['goal_gap_minutes'] as num?)?.toInt() ?? 0;
        final bySubject = (data['by_subject'] as List<dynamic>? ?? [])
            .whereType<Map>()
            .toList();

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Bugünkü özet',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  children: [
                    _statChip(context, 'Odak', '$focus dk'),
                    _statChip(
                      context,
                      'Plan uyumu',
                      '%${adherence.toStringAsFixed(0)}',
                    ),
                    _statChip(
                      context,
                      gap > 0 ? 'Hedefe' : 'Hedef',
                      gap > 0 ? '$gap dk kaldı' : 'tamam',
                    ),
                    _statChip(context, 'Mola', '$breaks dk'),
                    if (planned > 0)
                      _statChip(context, 'Planlanan', '$planned dk'),
                  ],
                ),
                if (bySubject.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(
                    'Dersler',
                    style: theme.textTheme.labelLarge,
                  ),
                  const SizedBox(height: 6),
                  for (final s in bySubject.take(5))
                    Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              s['subject_label']?.toString() ??
                                  s['subject_code']?.toString() ??
                                  '',
                            ),
                          ),
                          Text(
                            '${s['focus_minutes'] ?? 0} dk'
                            '${(s['planned_minutes'] as num? ?? 0) > 0 ? ' / ${s['planned_minutes']} plan' : ''}',
                            style: theme.textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _statChip(BuildContext context, String label, String value) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: cs.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: Theme.of(context).textTheme.labelSmall),
          Text(
            value,
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
          ),
        ],
      ),
    );
  }
}
