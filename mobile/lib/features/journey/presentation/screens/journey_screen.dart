import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../../shared/widgets/ds.dart';
import '../../../assessment/presentation/screens/assessment_overview_screen.dart';
import '../../../dashboard/presentation/widgets/active_exam_switcher.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../statistics/domain/entities/statistics_entities.dart';
import '../../../statistics/presentation/providers/statistics_provider.dart';
import '../../../statistics/presentation/providers/statistics_state.dart';
import '../providers/coach_journey_provider.dart';
import '../providers/journey_trends_provider.dart';

/// Sprint 16 — Journey Surface (kişisel gelişim polish).
class JourneyScreen extends ConsumerWidget {
  const JourneyScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statsState = ref.watch(statisticsProvider);
    final profileAsync = ref.watch(learningProfileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Yolculuğum'),
        actions: const [ActiveExamSwitcher()],
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 4),
      body: switch (statsState) {
        StatisticsInitial() || StatisticsLoading() => ListView(
            padding: AppSpacing.pageWide,
            children: const [
              SkeletonCard(height: 160),
              SizedBox(height: AppSpacing.md),
              SkeletonCard(height: 72),
              SizedBox(height: AppSpacing.sm),
              SkeletonCard(height: 72),
            ],
          ),
        StatisticsError(:final message) => _ErrorView(
            message: message,
            onRetry: () => ref.read(statisticsProvider.notifier).load(),
          ),
        StatisticsLoaded() => _JourneyBody(
            stats: statsState,
            profileAsync: profileAsync,
          ),
      },
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton(
              onPressed: onRetry,
              child: const Text('Tekrar Dene'),
            ),
          ],
        ),
      ),
    );
  }
}

class _JourneyBody extends ConsumerWidget {
  const _JourneyBody({required this.stats, required this.profileAsync});

  final StatisticsLoaded stats;
  final AsyncValue<dynamic> profileAsync;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final overview = stats.overview;
    final subjectItems = stats.subjects.items;

    final strong = subjectItems
        .where((s) => s.sessionCount > 0)
        .toList()
      ..sort((a, b) => b.studyMinutes.compareTo(a.studyMinutes));

    final weak = subjectItems
        .where((s) => s.sessionCount == 0)
        .toList()
      ..sort((a, b) => a.name.compareTo(b.name));

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(statisticsProvider);
        ref.invalidate(journeyTrendsProvider);
        ref.invalidate(assessmentOverviewProvider);
        ref.invalidate(coachWeeklyProvider);
        ref.invalidate(coachTimelineProvider);
      },
      child: ListView(
        padding: AppSpacing.pageWide,
        children: [
          _OverallProgressCard(overview: overview),
          const SizedBox(height: AppSpacing.xl),
          const _AssessmentProgressSection(),
          const SizedBox(height: AppSpacing.xl),
          const _WeeklyReflectionSection(),
          const SizedBox(height: AppSpacing.xl),
          const _CoachTimelineSection(),
          const SizedBox(height: AppSpacing.xl),
          const _ConfidenceTrendsSection(),
          const SizedBox(height: AppSpacing.xl),
          const SectionHeader(
            icon: Icons.star_rounded,
            title: 'Güçlü konular',
            subtitle: 'En çok çalıştığın alanlar',
          ),
          const SizedBox(height: AppSpacing.sm),
          if (strong.isEmpty)
            EmptyState(
              icon: Icons.star_outline,
              title: 'Henüz güçlü konu yok',
              message: 'Birkaç oturum sonrası burası dolacak.',
              ctaLabel: 'Derslere git',
              onCta: () => context.push('/subjects'),
            )
          else
            _SubjectList(
              items: strong,
              showMinutes: true,
              profile: profileAsync.valueOrNull,
            ),
          const SizedBox(height: AppSpacing.xl),
          const SectionHeader(
            icon: Icons.trending_up_rounded,
            title: 'Geliştirme gereken',
            subtitle: 'Henüz oturum açılmamış dersler',
          ),
          const SizedBox(height: AppSpacing.sm),
          if (weak.isEmpty)
            const EmptyState(
              icon: Icons.check_circle_outline,
              title: 'Harika denge',
              message: 'Tüm konularda oturum verisi var.',
            )
          else
            _SubjectList(
              items: weak,
              showMinutes: false,
              profile: profileAsync.valueOrNull,
            ),
          const SizedBox(height: AppSpacing.xl),
        ],
      ),
    );
  }
}

class _OverallProgressCard extends StatelessWidget {
  const _OverallProgressCard({required this.overview});

  final StatisticsOverviewEntity overview;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final hours = overview.totalStudyMinutes ~/ 60;
    final mins = overview.totalStudyMinutes % 60;

    return StudyCard(
      padding: AppSpacing.cardComfortable,
      color: colorScheme.primaryContainer.withValues(alpha: 0.35),
      borderColor: colorScheme.primary.withValues(alpha: 0.2),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Genel ilerleme',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: colorScheme.primary,
                ),
          ),
          const SizedBox(height: AppSpacing.md),
          _StatRow(
            icon: Icons.timer_outlined,
            label: 'Toplam çalışma',
            value: hours > 0 ? '$hours sa $mins dk' : '$mins dk',
          ),
          const SizedBox(height: AppSpacing.xs),
          _StatRow(
            icon: Icons.play_circle_outline_rounded,
            label: 'Oturum sayısı',
            value: '${overview.totalSessions}',
          ),
          const SizedBox(height: AppSpacing.xs),
          _StatRow(
            icon: Icons.local_fire_department_rounded,
            label: 'Seri (gün)',
            value: '${overview.streakDays}',
          ),
          if (overview.mostStudiedSubject != null) ...[
            const SizedBox(height: AppSpacing.xs),
            _StatRow(
              icon: Icons.star_outline_rounded,
              label: 'En çok çalışılan',
              value: overview.mostStudiedSubject!,
            ),
          ],
        ],
      ),
    );
  }
}

/// Sprint 20 — Weekly Reflection.
class _WeeklyReflectionSection extends ConsumerWidget {
  const _WeeklyReflectionSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(coachWeeklyProvider);
    return async.when(
      loading: () => const SkeletonCard(height: 120),
      error: (_, __) => const SizedBox.shrink(),
      data: (w) => StudyCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Haftalık yansıma',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              '${w.questionsSolved} soru · ${w.studyMinutes} dk',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            if (w.confidenceDeltaLabel != null) ...[
              const SizedBox(height: AppSpacing.xs),
              Text(w.confidenceDeltaLabel!),
            ],
            const SizedBox(height: AppSpacing.sm),
            Text(w.body),
            const SizedBox(height: AppSpacing.sm),
            Text(
              w.weeklySuggestion,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Sprint 20 — Coach Timeline.
class _CoachTimelineSection extends ConsumerWidget {
  const _CoachTimelineSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(coachTimelineProvider);
    return async.when(
      loading: () => const SkeletonCard(height: 100),
      error: (_, __) => const SizedBox.shrink(),
      data: (tl) {
        if (tl.items.isEmpty) return const SizedBox.shrink();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SectionHeader(
              title: 'Koç zaman çizelgesi',
              icon: Icons.timeline,
              subtitle: 'Geçen ay → bugün → sonraki hedef',
            ),
            const SizedBox(height: AppSpacing.sm),
            ...tl.items.map(
              (item) => MetricTile(
                title: item.title,
                subtitle: item.body,
              ),
            ),
            if (tl.nextGoal != null)
              Padding(
                padding: const EdgeInsets.only(top: AppSpacing.sm),
                child: Text(
                  'Hedef: ${tl.nextGoal}',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
          ],
        );
      },
    );
  }
}

/// Sprint 18 — Assessment Progress (LOS §11 Sense).
class _AssessmentProgressSection extends ConsumerWidget {
  const _AssessmentProgressSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(assessmentOverviewProvider);
    return async.when(
      loading: () => const SkeletonCard(height: 100),
      error: (_, __) => const SizedBox.shrink(),
      data: (overview) {
        final done = overview.progressPct >= 100;
        return StudyCard(
          onTap: () => context.push('/assessment'),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.science_outlined,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  Expanded(
                    child: Text(
                      'Assessment Progress',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                  Text(
                    '%${overview.progressPct.toStringAsFixed(0)}',
                    style: Theme.of(context).textTheme.labelLarge,
                  ),
                ],
              ),
              const SizedBox(height: AppSpacing.sm),
              LinearProgressIndicator(
                value: (overview.progressPct.clamp(0, 100)) / 100,
              ),
              const SizedBox(height: AppSpacing.sm),
              Text(
                done
                    ? 'Sistem seni tanımaya başladı.'
                    : overview.message,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: AppSpacing.xs),
              Text(
                '${overview.completedSubjects}/${overview.totalSubjects} ders kalibre edildi',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
        );
      },
    );
  }
}

class _StatRow extends StatelessWidget {
  const _StatRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Row(
      children: [
        Icon(icon, size: 18, color: colorScheme.onSurfaceVariant),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: colorScheme.onSurfaceVariant,
                ),
          ),
        ),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
        ),
      ],
    );
  }
}

class _SubjectList extends StatelessWidget {
  const _SubjectList({
    required this.items,
    required this.showMinutes,
    this.profile,
  });

  final List<DistributionItemEntity> items;
  final bool showMinutes;
  final dynamic profile;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        for (final item in items)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              dense: true,
              tileColor: colorScheme.surfaceContainerHighest
                  .withValues(alpha: 0.4),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              leading: CircleAvatar(
                radius: 16,
                backgroundColor: colorScheme.primary.withValues(alpha: 0.15),
                child: Text(
                  item.name.isNotEmpty ? item.name[0].toUpperCase() : '?',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w700,
                    color: colorScheme.primary,
                  ),
                ),
              ),
              title: Row(
                children: [
                  Expanded(
                    child: Text(
                      item.name,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ),
                  if (profile != null) ...[
                    Builder(
                      builder: (context) {
                        final subjects = (profile.subjects as List).cast<dynamic>();
                        final pSub = subjects.where((s) => s.subjectName.toLowerCase() == item.name.toLowerCase()).firstOrNull;
                        final conf = pSub?.progressPct ?? 0.0;
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: colorScheme.primary.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            'Güven: %${conf.toStringAsFixed(0)}',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: colorScheme.primary,
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ],
              ),
              subtitle: showMinutes
                  ? Text(
                      '${item.studyMinutes} dk · '
                      '${item.sessionCount} oturum',
                      style: TextStyle(
                        fontSize: 12,
                        color: colorScheme.onSurfaceVariant,
                      ),
                    )
                  : Text(
                      'Henüz çalışma yok',
                      style: TextStyle(
                        fontSize: 12,
                        color: colorScheme.onSurfaceVariant,
                      ),
                    ),
              trailing: showMinutes
                  ? Text(
                      '${item.percentage.toStringAsFixed(0)}%',
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        color: colorScheme.primary,
                      ),
                    )
                  : null,
            ),
          ),
      ],
    );
  }
}

class _ConfidenceTrendsSection extends ConsumerWidget {
  const _ConfidenceTrendsSection();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(journeyTrendsProvider);
    return async.when(
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
      data: (trends) {
        if (trends.rising.isEmpty && trends.falling.isEmpty) {
          return const SizedBox.shrink();
        }
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SectionHeader(
              title: 'Confidence trendleri',
              subtitle: 'Yükselen ve düşen konular',
              icon: Icons.insights_outlined,
            ),
            const SizedBox(height: AppSpacing.sm),
            ...trends.rising.take(3).map(
                  (t) => MetricTile(
                    title: t.topicName,
                    subtitle: t.trendLabel,
                    leading: const Text('↑', style: TextStyle(fontSize: 18, color: Colors.green)),
                  ),
                ),
            ...trends.falling.take(3).map(
                  (t) => MetricTile(
                    title: t.topicName,
                    subtitle: t.trendLabel,
                    leading: const Text('↓', style: TextStyle(fontSize: 18, color: Colors.redAccent)),
                  ),
                ),
          ],
        );
      },
    );
  }
}
