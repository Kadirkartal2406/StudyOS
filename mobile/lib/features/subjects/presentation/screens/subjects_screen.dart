import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_spacing.dart';
import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../../shared/widgets/ds.dart';
import '../../../dashboard/presentation/widgets/active_exam_switcher.dart';
import '../../../onboarding/domain/entities/learning_profile_entity.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../domain/subject_display_title.dart';

/// Active Exam scoped list → Subject Learning Container (subject_code).
class SubjectsScreen extends ConsumerWidget {
  const SubjectsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(learningProfileProvider);

    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        title: const Text('Derslerim'),
        actions: [
          const ActiveExamSwitcher(),
          IconButton(
            tooltip: 'Yenile',
            onPressed: () => invalidateLearningProfile(ref),
            icon: const Icon(StudyIcons.refresh),
          ),
        ],
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 1),
      body: StudyGlassAtmosphere(
        child: async.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(
            child: Padding(
              padding: AppSpacing.pageWide,
              child: EmptyState(
                icon: Icons.wifi_off_rounded,
                title: 'Dersler yüklenemedi',
                message: '$e',
                ctaLabel: 'Tekrar Dene',
                onCta: () => invalidateLearningProfile(ref),
              ),
            ),
          ),
          data: (profile) => _SubjectsBody(profile: profile),
        ),
      ),
    );
  }
}

class _SubjectsBody extends StatelessWidget {
  const _SubjectsBody({required this.profile});

  final LearningProfileEntity profile;

  static const _accents = [
    AppColors.primary,
    AppColors.info,
    AppColors.warning,
    AppColors.success,
    Color(0xFF8B5CF6),
  ];

  @override
  Widget build(BuildContext context) {
    final primary = profile.primaryExamType;
    final subjects = profile.activeSubjects;
    final width = MediaQuery.sizeOf(context).width;
    final hPad = EditorialPage.horizontalPadding(width);
    final text = Theme.of(context).textTheme;

    if (subjects.isEmpty) {
      return Center(
        child: Padding(
          padding: AppSpacing.pageWide,
          child: EmptyState(
            icon: StudyIcons.subjects,
            title: primary == null
                ? 'Önce bir sınav seç'
                : 'Bu sınav için henüz ders yok',
            message: primary == null
                ? 'Kurulumdan sınavını belirle.'
                : 'Active sınav için ders listesi boş.',
          ),
        ),
      );
    }

    final grouped = <String?, List<UserSubjectEntity>>{};
    for (final s in subjects) {
      grouped.putIfAbsent(s.section, () => []).add(s);
    }
    final keys = grouped.keys.toList()
      ..sort((a, b) {
        if (a == null) return 1;
        if (b == null) return -1;
        return a.compareTo(b);
      });

    var accentIndex = 0;

    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: BoxConstraints(
          maxWidth: EditorialPage.maxContentWidth(width),
        ),
        child: ListView(
          padding: EdgeInsets.only(
            left: hPad.left,
            right: hPad.right,
            top: AppSpacing.lg,
            bottom: AppSpacing.xxl,
          ),
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Derslerim',
                    style: text.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      letterSpacing: -0.4,
                    ),
                  ),
                ),
                if (primary != null)
                  Text(
                    primary.toUpperCase(),
                    style: text.labelLarge?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: AppSpacing.xs),
            Text(
              '${subjects.length} ders',
              style: text.bodyMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            for (final key in keys) ...[
              if (key != null) ...[
                Padding(
                  padding: const EdgeInsets.only(
                    top: AppSpacing.md,
                    bottom: AppSpacing.xs,
                    left: AppSpacing.xxs,
                  ),
                  child: Text(
                    key.toUpperCase(),
                    style: text.labelLarge?.copyWith(
                      color: Theme.of(context).colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.4,
                    ),
                  ),
                ),
              ],
              StudyFloatingCard(
                padding: const EdgeInsets.symmetric(vertical: AppSpacing.xs),
                child: Column(
                  children: [
                    for (final s in grouped[key]!)
                      _SubjectListRow(
                        subject: s,
                        accent: _accents[accentIndex++ % _accents.length],
                      ),
                  ],
                ),
              ),
              const SizedBox(height: AppSpacing.md),
            ],
          ],
        ),
      ),
    );
  }
}

class _SubjectListRow extends StatelessWidget {
  const _SubjectListRow({
    required this.subject,
    required this.accent,
  });

  final UserSubjectEntity subject;
  final Color accent;

  @override
  Widget build(BuildContext context) {
    final pct = subject.progressPct.clamp(0, 100);
    final title = subjectDisplayTitle(
      subjectCode: subject.subjectCode,
      subjectName: subject.subjectName,
      section: subject.section,
    );

    return StudyRow(
      title: title,
      subtitle: subject.section?.isNotEmpty == true
          ? subject.section
          : subject.subjectCode,
      leading: StudyIcons.subjects,
      leadingColor: accent,
      trailing: Text(
        '%${pct.toStringAsFixed(0)}',
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
              color: accent,
            ),
      ),
      onTap: () => context.push('/subjects/${subject.subjectCode}'),
    );
  }
}
