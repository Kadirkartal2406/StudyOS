import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/soft_progress.dart';
import '../../../../shared/widgets/study_surface.dart';
import '../../data/datasources/study_session_remote_datasource.dart';

final studySessionTodaySummaryProvider =
    FutureProvider.autoDispose<Map<String, dynamic>>((ref) async {
  final ds = StudySessionRemoteDatasource(ref.watch(dioClientProvider));
  return ds.todaySummary();
});

/// Günlük uyum paneli — sakin progress + tonal surface.
class TodaySummaryCard extends ConsumerWidget {
  const TodaySummaryCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(studySessionTodaySummaryProvider);
    final theme = Theme.of(context);
    final scheme = theme.colorScheme;

    return async.when(
      loading: () => const StudySurface(
        child: SizedBox(
          height: 72,
          child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
        ),
      ),
      error: (e, _) => StudySurface(
        child: Text(
          e is AppException ? e.message : 'Bugünkü özet yüklenemedi',
          style: TextStyle(color: scheme.error),
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
        final progress = (adherence / 100).clamp(0.0, 1.0);

        return StudySurface(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Bugünkü hedef',
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: AppSpacing.md),
              Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '%${adherence.toStringAsFixed(0)}',
                    style: theme.textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.w700,
                      letterSpacing: -0.4,
                    ),
                  ),
                  const SizedBox(width: AppSpacing.xs),
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Text(
                      'plan uyumu',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: scheme.onSurfaceVariant,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.sm),
              SoftProgress(value: progress),
              const SizedBox(height: AppSpacing.md),
              Wrap(
                spacing: AppSpacing.lg,
                runSpacing: AppSpacing.sm,
                children: [
                  _metric(context, 'Odak', '$focus dk'),
                  _metric(
                    context,
                    gap > 0 ? 'Hedefe' : 'Hedef',
                    gap > 0 ? '$gap dk kaldı' : 'tamam',
                  ),
                  _metric(context, 'Mola', '$breaks dk'),
                  if (planned > 0) _metric(context, 'Planlanan', '$planned dk'),
                ],
              ),
              if (bySubject.isNotEmpty) ...[
                const SizedBox(height: AppSpacing.lg),
                Text(
                  'Dersler',
                  style: theme.textTheme.labelLarge?.copyWith(
                    color: scheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: AppSpacing.xs),
                for (final s in bySubject.take(5))
                  Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.xs),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            s['subject_label']?.toString() ??
                                s['subject_code']?.toString() ??
                                '',
                            style: theme.textTheme.bodyLarge,
                          ),
                        ),
                        Text(
                          '${s['focus_minutes'] ?? 0} dk'
                          '${(s['planned_minutes'] as num? ?? 0) > 0 ? ' / ${s['planned_minutes']} plan' : ''}',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: scheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _metric(BuildContext context, String label, String value) {
    final theme = Theme.of(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: theme.textTheme.labelMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}
