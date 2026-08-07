import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/errors/app_exception.dart';
import '../../../../shared/widgets/app_bottom_nav_bar.dart';
import '../../../study_session/presentation/providers/study_session_provider.dart';
import '../../../subjects/presentation/widgets/subject_code_chip.dart';
import '../../domain/entities/study_plan_entity.dart';
import '../providers/study_plan_provider.dart';
import '../providers/study_plan_state.dart';
import '../widgets/daily_progress.dart';
import '../widgets/date_selector.dart';
import '../widgets/study_card.dart';
import '../widgets/study_plan_empty_state.dart';
import '../widgets/study_plan_timeline.dart';

/// Alignment Sprint-4 — Living Plan yansıması (günlük bloklar).
/// Kullanıcı plan yönetmez; blokları görür ve uygular (Complete/Skip).
/// Create/Edit/Delete/Reorder primary değildir (Override).
class StudyPlanScreen extends ConsumerWidget {
  const StudyPlanScreen({super.key, this.subjectCode});

  final String? subjectCode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(studyPlanProvider);
    final code = subjectCode;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bugünkü bloklar'),
        actions: [
          if (code != null && code.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: SubjectCodeChip(subjectCode: code),
            ),
          // Override — primary Create değil; düşük keşif
          PopupMenuButton<String>(
            tooltip: 'Gelişmiş',
            onSelected: (value) {
              if (value == 'suggest_plan') {
                context.push('/planner');
              } else if (value == 'override_add') {
                context.push('/study-plan/add');
              }
            },
            itemBuilder: (context) => const [
              PopupMenuItem(
                value: 'suggest_plan',
                child: Text('Önerilen plan oluştur'),
              ),
              PopupMenuItem(
                value: 'override_add',
                child: Text('Geçici blok ekle (Gelişmiş)'),
              ),
            ],
          ),
        ],
      ),
      body: SafeArea(
        child: switch (state) {
          StudyPlanInitial() || StudyPlanLoading() => const _LoadingView(),
          StudyPlanLoaded() => _LoadedView(state: state),
          StudyPlanError(:final message) => _ErrorView(message: message),
        },
      ),
      bottomNavigationBar: const AppBottomNavBar(currentIndex: 3),
    );
  }
}

class _LoadingView extends StatelessWidget {
  const _LoadingView();

  @override
  Widget build(BuildContext context) {
    return const Center(child: CircularProgressIndicator());
  }
}

class _ErrorView extends ConsumerWidget {
  const _ErrorView({required this.message});

  final String message;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colorScheme = Theme.of(context).colorScheme;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.wifi_off_rounded, size: 48, color: colorScheme.error),
            const SizedBox(height: 16),
            Text(
              'Bloklar yüklenemedi',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 8),
            Text(
              message,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: colorScheme.onSurfaceVariant,
                  ),
            ),
            const SizedBox(height: 20),
            FilledButton.icon(
              onPressed: () => ref.read(studyPlanProvider.notifier).retry(),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Tekrar Dene'),
            ),
          ],
        ),
      ),
    );
  }
}

class _LoadedView extends ConsumerWidget {
  const _LoadedView({required this.state});

  final StudyPlanLoaded state;

  void _showError(BuildContext context, Object error) {
    final message =
        error is AppException ? error.message : 'Beklenmeyen bir hata oluştu';
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _confirmDelete(
    BuildContext context,
    WidgetRef ref,
    StudyPlanEntity plan,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Bloğu kaldır'),
        content: Text(
          '"${plan.displayLabel}" bloğunu kaldırmak istediğine emin misin?\n'
          'Bu bir Gelişmiş (Override) işlemdir.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Vazgeç'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            child: const Text('Kaldır'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;
    try {
      await ref.read(studyPlanProvider.notifier).deletePlan(plan.id);
    } catch (e) {
      if (context.mounted) _showError(context, e);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifier = ref.read(studyPlanProvider.notifier);

    return RefreshIndicator(
      onRefresh: () => notifier.load(state.selectedDate),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
                child: DateSelector(
                  selectedDate: state.selectedDate,
                  onDateSelected: notifier.changeDate,
                  onTodayPressed: notifier.goToToday,
                ),
              ),
              Expanded(
                child: state.plans.isEmpty
                    ? StudyPlanEmptyState(
                        onGoToToday: () => context.go('/dashboard'),
                        onSuggestPlan: () => context.push('/planner'),
                      )
                    : ListView(
                        padding: const EdgeInsets.fromLTRB(20, 16, 20, 96),
                        children: [
                          DailyProgress(
                            completedCount: state.completedCount,
                            totalCount: state.plans.length,
                            totalMinutes: state.totalMinutes,
                            totalQuestions: state.totalQuestions,
                            progressPercentage: state.progressPercentage,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Sözleşmenin bugünkü yansıması · sıralama sistemde',
                            style: Theme.of(context)
                                .textTheme
                                .labelMedium
                                ?.copyWith(
                                  color: Theme.of(context)
                                      .colorScheme
                                      .onSurfaceVariant,
                                ),
                          ),
                          const SizedBox(height: 16),
                          StudyPlanTimeline(plans: state.plans),
                          if (state.plans.any((p) => p.hasTimeRange))
                            const SizedBox(height: 16),
                          // Reorder kaldırıldı — sıra tasarımı kullanıcıda değil
                          ...state.plans.map(
                            (plan) => Padding(
                              padding: const EdgeInsets.only(bottom: 12),
                              child: StudyCard(
                                plan: plan,
                                isMutating: state.mutatingPlanId == plan.id,
                                onStart: () async {
                                  try {
                                    await notifier.startPlan(plan.id);
                                  } catch (e) {
                                    if (context.mounted) {
                                      _showError(context, e);
                                    }
                                  }
                                },
                                onStartStudy: () {
                                  ref
                                      .read(studySessionProvider.notifier)
                                      .setContext(
                                        subject: plan.subject,
                                        topic: plan.topic,
                                        studyPlanId: plan.id,
                                      );
                                  context.go('/pomodoro');
                                },
                                onComplete: () async {
                                  try {
                                    await notifier.completePlan(plan.id);
                                  } catch (e) {
                                    if (context.mounted) {
                                      _showError(context, e);
                                    }
                                  }
                                },
                                onSkip: () async {
                                  try {
                                    await notifier.skipPlan(plan.id);
                                  } catch (e) {
                                    if (context.mounted) {
                                      _showError(context, e);
                                    }
                                  }
                                },
                                onEdit: () => context
                                    .push('/study-plan/edit/${plan.id}'),
                                onDelete: () =>
                                    _confirmDelete(context, ref, plan),
                                onOpenDetail: () =>
                                    context.push('/study-plan/${plan.id}'),
                              ),
                            ),
                          ),
                        ],
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
