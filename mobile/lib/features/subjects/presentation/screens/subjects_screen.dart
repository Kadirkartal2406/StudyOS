import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../onboarding/domain/entities/learning_profile_entity.dart';
import '../../../onboarding/presentation/providers/learning_profile_provider.dart';
import '../../../dashboard/presentation/widgets/active_exam_switcher.dart';
import '../../domain/subject_display_title.dart';
import '../../../../shared/widgets/app_bottom_nav_bar.dart';

/// Active Exam scoped list → Subject Learning Container (subject_code).
/// Alignment Sprint-2: Subject work center değil; Topic seçimine giriş.
class SubjectsScreen extends ConsumerWidget {
  const SubjectsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(learningProfileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Derslerim'),
        actions: [
          const ActiveExamSwitcher(),
          IconButton(
            tooltip: 'Yenile',
            onPressed: () => invalidateLearningProfile(ref),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 1),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('Dersler yüklenemedi: $e'),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => invalidateLearningProfile(ref),
                  child: const Text('Tekrar Dene'),
                ),
              ],
            ),
          ),
        ),
        data: (profile) => _SubjectsBody(profile: profile),
      ),
    );
  }
}

class _SubjectsBody extends StatelessWidget {
  const _SubjectsBody({required this.profile});

  final LearningProfileEntity profile;

  @override
  Widget build(BuildContext context) {
    final primary = profile.primaryExamType;
    final subjects = profile.activeSubjects;

    if (subjects.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.menu_book_outlined,
                size: 48,
                color: Theme.of(context).colorScheme.outline,
              ),
              const SizedBox(height: 16),
              Text(
                primary == null
                    ? 'Önce bir sınav seç (Kurulum)'
                    : 'Bu sınav için henüz ders yok',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleMedium,
              ),
            ],
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

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (primary != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(
              'Sınav: ${primary.toUpperCase()} · ${subjects.length} ders',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
          ),
        for (final key in keys) ...[
          if (key != null)
            Padding(
              padding: const EdgeInsets.only(top: 8, bottom: 4),
              child: Text(
                key.toUpperCase(),
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: Theme.of(context).colorScheme.primary,
                      fontWeight: FontWeight.w700,
                    ),
              ),
            ),
          for (final s in grouped[key]!) _SubjectMetricCard(subject: s),
        ],
      ],
    );
  }
}

class _SubjectMetricCard extends StatelessWidget {
  const _SubjectMetricCard({required this.subject});

  final UserSubjectEntity subject;

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat('dd.MM.yyyy');
    final progress = (subject.progressPct / 100).clamp(0.0, 1.0);

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: InkWell(
        onTap: () => context.push('/subjects/${subject.subjectCode}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.book_outlined, size: 22),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      subjectDisplayTitle(
                        subjectCode: subject.subjectCode,
                        subjectName: subject.subjectName,
                        section: subject.section,
                      ),
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                  ),
                  Text(
                    'Güven: ${subject.progressPct.toStringAsFixed(0)}%',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  const SizedBox(width: 4),
                  const Icon(Icons.chevron_right, size: 20),
                ],
              ),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: progress,
                  minHeight: 6,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
