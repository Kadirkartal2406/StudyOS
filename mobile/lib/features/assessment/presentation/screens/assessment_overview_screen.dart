import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/ds.dart';
import '../../data/assessment_remote_datasource.dart';

final assessmentOverviewProvider =
    FutureProvider.autoDispose<AssessmentOverviewEntity>((ref) async {
  return ref.watch(assessmentDatasourceProvider).overview();
});

/// Sprint 18 — Seviye testi / Assessment Progress.
class AssessmentOverviewScreen extends ConsumerWidget {
  const AssessmentOverviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(assessmentOverviewProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Seviye testi')),
      body: async.when(
        loading: () => ListView(
          padding: AppSpacing.pageWide,
          children: const [
            SkeletonCard(height: 120),
            SizedBox(height: AppSpacing.md),
            SkeletonCard(height: 72),
            SkeletonCard(height: 72),
          ],
        ),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  e is AppException ? e.message : 'Yüklenemedi',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                FilledButton(
                  onPressed: () => ref.invalidate(assessmentOverviewProvider),
                  child: const Text('Tekrar dene'),
                ),
              ],
            ),
          ),
        ),
        data: (overview) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(assessmentOverviewProvider),
          child: ListView(
            padding: AppSpacing.pageWide,
            children: [
              StudyCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      overview.examType.toUpperCase(),
                      style: Theme.of(context).textTheme.labelLarge,
                    ),
                    const SizedBox(height: AppSpacing.sm),
                    Text(
                      overview.message,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: AppSpacing.md),
                    LinearProgressIndicator(
                      value: (overview.progressPct.clamp(0, 100)) / 100,
                    ),
                    const SizedBox(height: AppSpacing.xs),
                    Text(
                      '${overview.completedSubjects}/${overview.totalSubjects} ders · %${overview.progressPct.toStringAsFixed(0)}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              if (overview.coachSummary != null &&
                  overview.coachSummary!.isNotEmpty) ...[
                const SizedBox(height: AppSpacing.lg),
                StudyCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Koç özeti',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                      const SizedBox(height: AppSpacing.xs),
                      if (overview.coachRankLabel != null)
                        Text(overview.coachRankLabel!),
                      Text(overview.coachSummary!),
                      if (overview.coachCriticalSubject != null) ...[
                        const SizedBox(height: AppSpacing.xs),
                        Text('Hedefe uzak: ${overview.coachCriticalSubject}'),
                      ],
                      if (overview.coachNextTarget != null) ...[
                        const SizedBox(height: AppSpacing.xs),
                        Text('Hedef: ${overview.coachNextTarget}'),
                      ],
                    ],
                  ),
                ),
              ],
              const SizedBox(height: AppSpacing.lg),
              SecondaryButton(
                label: 'Günün Denemesi — Kitapçık',
                icon: Icons.today_outlined,
                expand: true,
                onPressed: () => context.push('/assessment/daily'),
              ),
              const SizedBox(height: AppSpacing.xl),
              const SectionHeader(
                title: 'Ders ders seviye testi',
                subtitle: 'İstediğin dersten başla — zorunlu değil',
                icon: Icons.tune,
              ),
              const SizedBox(height: AppSpacing.sm),
              if (overview.subjects.isEmpty)
                const EmptyState(
                  icon: Icons.school_outlined,
                  title: 'Henüz ders yok',
                  message: 'Önce aktif sınav derslerini seç.',
                )
              else
                ...overview.subjects.map(
                  (s) => MetricTile(
                    title: s.subjectName,
                    subtitle: s.completed
                        ? (s.accuracy != null
                            ? 'Tamamlandı · %${(s.accuracy! * 100).toStringAsFixed(0)}'
                            : 'Tamamlandı')
                        : 'Bekliyor',
                    leading: Icon(
                      s.completed
                          ? Icons.check_circle
                          : Icons.play_circle_outline,
                      color: s.completed
                          ? Theme.of(context).colorScheme.primary
                          : null,
                    ),
                    onTap: s.completed
                        ? null
                        : () => context.push(
                              '/assessment/branch/start?subject_code=${s.subjectCode}&kind=calibration',
                            ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
